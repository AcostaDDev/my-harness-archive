"""Lectura explícita local. No ejecuta históricos ni sigue enlaces simbólicos."""
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import re
import stat

from harness_local.core.legacy import LegacyArtifact, LegacyInventory, LegacyRun


EXECUTOR = re.compile(r"claude-(\d+)\.")
EVIDENCE = re.compile(r"(?:review|validation|stop|resume|policy|scope|format|preflight)-(\d+)(?:\.|/)")


def artifact_kind(path: str) -> str:
    name = Path(path).name
    if name == "task.json":
        return "task"
    if name.endswith(".result.request.json"):
        return "request"
    if name.endswith(".result.usage.json"):
        return "usage"
    if name.endswith(".result.json"):
        return "result"
    if name.endswith(".events.jsonl"):
        return "events"
    if name == "phase-review.meta.json":
        return "phase_metadata"
    if name == "phase-review.json":
        return "phase_review"
    if name == "reconcile.json":
        return "reconcile"
    match = re.match(r"(review|validation|stop|resume|policy|scope|format|preflight)-\d+\.json$", name)
    if match:
        return match[1]
    return "document" if path.startswith("docs/") else "evidence"


def artifact_format(path: str) -> str:
    return "json" if path.endswith(".json") else "jsonl" if path.endswith(".jsonl") else "text"


def reject_constant(value):
    raise ValueError(f"Constante JSON no válida: {value}")


class ChangingEvidence(ValueError):
    pass


def read_raw(root: Path, path: str) -> bytes:
    """Bounded regular-file read, without following any path component."""
    descriptors = []
    try:
        fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
        descriptors.append(fd)
        parts = (root / path).parts[1:]
        for part in parts[:-1]:
            fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            descriptors.append(fd)
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        descriptors.append(fd)
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("La evidencia no es un archivo regular.")
        maximum = 64 * 1024 * 1024
        if before.st_size > maximum:
            raise ValueError("Lectura limitada a 64 MiB por evidencia.")
        raw = bytearray()
        while chunk := os.read(fd, 65536):
            raw.extend(chunk)
            if len(raw) > maximum:
                raise ValueError("Archivo creció sobre el límite de lectura de 64 MiB.")
        after = os.fstat(fd)
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ChangingEvidence("Archivo cambió durante la lectura; pendiente de relectura.")
        return bytes(raw)
    finally:
        for fd in reversed(descriptors):
            os.close(fd)


def read_artifact(root: Path, path: str, run_path: str | None) -> LegacyArtifact:
    artifact = LegacyArtifact(path, run_path, artifact_kind(path), artifact_format(path), "available")
    try:
        # También rechaza enlaces en directorios ante cambios durante el inventario.
        file = root / path
        if any(parent.is_symlink() for parent in (file, *file.parents) if parent != root):
            raise ValueError("Enlace simbólico no leído.")
        raw = read_raw(root, path)
        artifact = replace(artifact, sha256=hashlib.sha256(raw).hexdigest(), size_bytes=len(raw))
        if artifact.format == "text":
            return artifact
        decoded = raw.decode("utf-8")
        if artifact.format == "json":
            payload = json.loads(decoded, parse_constant=reject_constant)
            if not isinstance(payload, dict):
                raise ValueError("Se esperaba un objeto JSON legacy.")
            return replace(artifact, payload=payload)
        payload = []
        for number, line in enumerate(decoded.splitlines(), 1):
            if not line.strip():
                continue
            try:
                event = json.loads(line, parse_constant=reject_constant)
                if not isinstance(event, dict):
                    raise ValueError("Se esperaba un objeto de evento.")
                payload.append(event)
            except (ValueError, RecursionError) as error:
                return replace(artifact, status="pending", payload=payload,
                               diagnostic=f"JSONL pendiente de relectura, línea {number}: {error}")
        return replace(artifact, payload=payload)
    except (json.JSONDecodeError, UnicodeDecodeError, RecursionError, ChangingEvidence) as error:
        return replace(artifact, status="pending", diagnostic=f"Pendiente de relectura: {error}")
    except (OSError, ValueError) as error:
        return replace(artifact, status="error", diagnostic=str(error))


class LocalLegacyReader:
    def __init__(self, incremental: bool = False):
        self.incremental = incremental
        self.cache = {}

    def clear(self):
        self.cache.clear()

    def read(self, root: str) -> LegacyInventory:
        checkout = Path(root).expanduser().resolve(strict=True)
        if not checkout.is_dir():
            raise ValueError("La raíz de origen debe ser un directorio.")
        if any(parent.is_symlink() for parent in (Path(root), *Path(root).parents)):
            raise ValueError("Raíz o componente del origen convertido en enlace; lectura detenida.")
        artifacts: dict[str, LegacyArtifact] = {}
        runs: dict[str, LegacyRun] = {}

        def record(path: Path, run_path: str | None):
            relative = path.relative_to(checkout).as_posix()
            key = (str(checkout), relative)
            signature = None
            try:
                info = path.lstat()
                signature = (info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
            except OSError:
                pass
            cached = self.cache.get(key)
            if self.incremental and cached and signature is not None and cached[0] == signature and cached[1].status == "available":
                artifacts[relative] = cached[1]
            else:
                artifacts[relative] = read_artifact(checkout, relative, run_path)
                if self.incremental:
                    self.cache[key] = (signature, artifacts[relative])

        def walk(directory: Path, run_path: str | None):
            if directory.is_symlink():
                record(directory, run_path)
                return

            def onerror(error):
                path = Path(error.filename).relative_to(checkout).as_posix()
                artifacts[path] = LegacyArtifact(path, run_path, "evidence", "text", "error",
                                                 diagnostic=str(error))

            for current, directories, files in os.walk(directory, onerror=onerror, followlinks=False):
                for name in list(directories):
                    child = Path(current) / name
                    if child.is_symlink():
                        record(child, run_path)
                        directories.remove(name)
                for name in files:
                    record(Path(current) / name, run_path)

        run_root = checkout / ".harness/runs"
        # No seguir un enlace en .harness o runs, tampoco fuera del checkout.
        if (checkout / ".harness").is_symlink() or run_root.is_symlink():
            record(checkout / ".harness" if (checkout / ".harness").is_symlink() else run_root, None)
        elif run_root.exists():
            try:
                for directory in sorted(run_root.iterdir()):
                    if directory.is_symlink():
                        record(directory, None)
                    elif directory.is_dir():
                        path = directory.relative_to(checkout).as_posix()
                        # Identidad observada del nombre, no un número de invocación.
                        runs[path] = LegacyRun(path, directory.name.partition("_")[2] or directory.name)
                        walk(directory, path)
            except OSError as error:
                artifacts[".harness/runs"] = LegacyArtifact(
                    ".harness/runs", None, "evidence", "text", "error", diagnostic=str(error))

        docs = checkout / "docs"
        if docs.is_symlink():
            record(docs, None)
        else:
            for name in ("STATE.md", "NEXT_STEPS.md", "ROADMAP.md"):
                if (docs / name).exists() or (docs / name).is_symlink():
                    record(docs / name, None)
            if (docs / "archive").exists() or (docs / "archive").is_symlink():
                walk(docs / "archive", None)

        # Ausencias de compañeros de evidencia; nunca prueban un fallo/invocación.
        expected: dict[str, str] = {}
        for path, run in runs.items():
            names = [a.path[len(path) + 1:] for a in artifacts.values() if a.run_path == path]
            if re.fullmatch(r"P\d+-T\d+", run.identity):
                expected[f"{path}/task.json"] = path
            for name in names:
                executor = EXECUTOR.match(name)
                evidence = EVIDENCE.match(name)
                if executor:
                    index = executor[1]
                    for suffix in ("prompt.md", "stderr.log", "result.request.json", "result.events.jsonl",
                                   "result.json", "result.usage.json"):
                        expected[f"{path}/claude-{index}.{suffix}"] = path
                if executor or evidence:
                    index = (executor or evidence)[1]
                    for kind in ("review", "validation", "stop"):
                        expected[f"{path}/{kind}-{index}.json"] = path
            if run.identity.endswith("-CLOSE"):
                for name in ("phase-review.json", "phase-review.meta.json"):
                    expected[f"{path}/{name}"] = path
            if run.identity.endswith("-RECONCILE"):
                expected[f"{path}/reconcile.json"] = path
        for path, run_path in expected.items():
            if path not in artifacts:
                artifacts[path] = LegacyArtifact(path, run_path, artifact_kind(path), artifact_format(path),
                                                 "missing", diagnostic="Archivo no observado; no acredita fallo.")
        if self.incremental:
            self.cache = {key: value for key, value in self.cache.items()
                          if key[0] == str(checkout) and key[1] in artifacts}
        return LegacyInventory(str(checkout), tuple(runs[key] for key in sorted(runs)),
                               tuple(artifacts[key] for key in sorted(artifacts)))

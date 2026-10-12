"""Sistema de archivos H2.5: sonda de modo, copia consistente, marcador y exportación.

Solo escribe en el directorio de migraciones de la aplicación y, en el checkout,
el marcador `.harness/managed-mode.json` (creación exclusiva; se retira solo si
sus bytes son exactamente los registrados). No sigue enlaces ni lanza procesos.
"""

import os
from pathlib import Path
import shutil
import stat

from harness_local.adapters.legacy import read_raw
from harness_local.core.legacy import LegacyInventory
from harness_local.core.migration import (
    LEGACY_RUNS, MARKER_PATH, CheckoutFacts, MigrationError, classify_drift, digest,
)


def _repository(root: Path) -> tuple[str | None, str | None]:
    """Common dir Git y checkout principal leyendo `.git`, sin ejecutar Git."""
    for directory in (root, *root.parents):
        dot = directory / ".git"
        if not os.path.lexists(dot):
            continue
        try:
            if dot.is_dir() and not dot.is_symlink():
                common = dot.resolve()
            elif dot.is_file() and not dot.is_symlink():
                text = dot.read_text(encoding="utf-8").strip()
                if not text.startswith("gitdir:"):
                    return None, None
                gitdir = (directory / text.partition(":")[2].strip()).resolve()
                pointer = gitdir / "commondir"
                common = (gitdir / pointer.read_text(encoding="utf-8").strip()).resolve() if pointer.is_file() else gitdir
            else:
                return None, None
        except (OSError, UnicodeDecodeError):
            return None, None
        main = str(common.parent) if common.name == ".git" else None
        return str(common), main
    return None, None


def probe(root) -> CheckoutFacts:
    checkout = Path(root).expanduser().resolve(strict=True)
    if not checkout.is_dir():
        raise ValueError("La raíz del checkout debe ser un directorio.")
    key, main = _repository(checkout)
    marker, error = None, None
    if os.path.lexists(checkout / MARKER_PATH):
        try:
            marker = read_raw(checkout, MARKER_PATH)
        except (OSError, ValueError) as exc:
            error = f"ilegible: {exc}"
    main_legacy = bool(main and Path(main) != checkout and os.path.lexists(Path(main) / LEGACY_RUNS))
    return CheckoutFacts(str(checkout), key, main, os.path.lexists(checkout / LEGACY_RUNS), main_legacy,
                         marker, error)


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write_new(path: Path, data: bytes, mode: int) -> None:
    with open(path, "xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.chmod(path, mode)


def copy_snapshot(origin: str, inventory: LegacyInventory, staging: Path, *, hook=None) -> None:
    """Copia byte a byte lo inventariado con hash; cada archivo se verifica al copiarlo."""
    staging.mkdir(parents=False)
    for artifact in inventory.artifacts:
        if artifact.sha256 is None:
            continue
        destination = (staging / artifact.path)
        if not destination.resolve().is_relative_to(staging.resolve()):
            raise MigrationError(f"Ruta fuera de la copia: {artifact.path}")
        try:
            raw = read_raw(Path(origin), artifact.path)
        except (OSError, ValueError) as exc:
            raise MigrationError(f"{artifact.path} cambió o desapareció durante la copia: {exc}") from exc
        if digest(raw) != artifact.sha256 or len(raw) != artifact.size_bytes:
            raise MigrationError(f"{artifact.path} cambió durante la copia; hash distinto del inventario.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        partial = destination.with_name(f".{destination.name}.partial")
        _write_new(partial, raw, 0o444)
        os.replace(partial, destination)
        if hook:
            hook("copied", path=artifact.path)
    _fsync_directory(staging)


def publish(staging: Path, final: Path) -> bool:
    """Rename atómico; si otra ejecución ya publicó, la copia propia se descarta."""
    try:
        os.rename(staging, final)
    except OSError:
        if not final.is_dir():
            raise
        shutil.rmtree(staging)
        return False
    _fsync_directory(final.parent)
    return True


def origin_mtimes(origin: str, inventory: LegacyInventory) -> dict[str, int]:
    return {a.path: os.lstat(Path(origin) / a.path).st_mtime_ns for a in inventory.artifacts if a.sha256}


def write_marker(root: str, content: bytes) -> bool:
    """Creación exclusiva; los mismos bytes ya presentes (reanudación) no se reescriben."""
    path = Path(root) / MARKER_PATH
    if (Path(root) / ".harness").is_symlink():
        raise MigrationError(".harness es un enlace; no se escribe el marcador.")
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    except FileExistsError:
        try:
            existing = read_raw(Path(root), MARKER_PATH)
        except (OSError, ValueError) as exc:
            raise MigrationError(f"Marcador existente ilegible: {exc}") from exc
        if existing != content:
            raise MigrationError("Ya existe un marcador de modo gestionado distinto; no se sobrescribe.")
        return False
    try:
        os.write(fd, content)
        os.fsync(fd)
    finally:
        os.close(fd)
    _fsync_directory(path.parent)
    return True


def remove_marker(root: str, expected: bytes) -> bool:
    """Retira solo el marcador registrado; ausente es idempotente, distinto se conserva."""
    path = Path(root) / MARKER_PATH
    if not os.path.lexists(path):
        return False
    try:
        existing = read_raw(Path(root), MARKER_PATH)
    except (OSError, ValueError) as exc:
        raise MigrationError(f"Marcador ilegible; no se retira: {exc}") from exc
    if existing != expected:
        raise MigrationError("El marcador no coincide con la activación registrada; no se retira.")
    os.unlink(path)
    _fsync_directory(path.parent)
    return True


def scan_legacy_scope(root: str) -> dict[str, tuple[str, int, int]]:
    """Estado actual de `.harness/runs` por lstat: (tipo, tamaño, mtime_ns)."""
    checkout = Path(root)
    runs = checkout / LEGACY_RUNS
    if not os.path.lexists(runs):
        return {}
    if runs.is_symlink() or not runs.is_dir() or (checkout / ".harness").is_symlink():
        return {LEGACY_RUNS: ("other", 0, 0)}
    found = {}
    for current, directories, files in os.walk(runs, followlinks=False):
        for name in [*directories, *files]:
            path = Path(current) / name
            info = path.lstat()
            kind = "dir" if stat.S_ISDIR(info.st_mode) else "file" if stat.S_ISREG(info.st_mode) else "other"
            found[path.relative_to(checkout).as_posix()] = (kind, info.st_size, info.st_mtime_ns)
    return found


def legacy_drift(root: str, manifest: dict) -> dict[str, list[str]]:
    def hash_of(path):
        try:
            return digest(read_raw(Path(root), path))
        except (OSError, ValueError):
            return None
    return classify_drift(manifest, scan_legacy_scope(root), hash_of)


def current_documents(root: str, inventory: LegacyInventory) -> dict[str, str | None]:
    return {a.path: a.sha256 for a in inventory.artifacts
            if a.run_path is None and a.path.startswith("docs/") and a.sha256 is not None}


def write_export(directory: Path, name: str, data: bytes) -> str:
    """Escritura temporal + rename y relectura; devuelve el hash comprobado."""
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / name
    partial = directory / f".{name}.{os.getpid()}.partial"
    if os.path.lexists(partial):
        os.unlink(partial)
    _write_new(partial, data, 0o444)
    os.replace(partial, target)
    _fsync_directory(directory)
    if target.read_bytes() != data:
        raise MigrationError("La exportación releída no coincide con el estado serializado.")
    return digest(data)

"""H2.5: reglas puras de migración legacy → gestionado. Biblioteca estándar.

Ningún run legacy se convierte en intento gestionado. La vista previa y el
manifiesto describen evidencia observada (ruta, estado y hash); la decisión de
modo es una función de hechos ya leídos, sin acceso a disco ni a SQLite.
"""

from dataclasses import dataclass
import hashlib
import re
from typing import Any, Callable

from harness_local.core.engine.contracts import freeze
from harness_local.core.legacy import LegacyInventory

PREVIEW_FORMAT = "harness-local/migration-preview/1"
INVENTORY_FORMAT = "harness-local/migration-inventory/1"
MANIFEST_FORMAT = "harness-local/migration-manifest/1"
MARKER_FORMAT = "harness-local/managed-mode/1"
EXPORT_FORMAT = "harness-local/managed-export/1"
MARKER_PATH = ".harness/managed-mode.json"
LEGACY_RUNS = ".harness/runs"
LIVE_STATUSES = ("PREPARING", "ACTIVE", "REVERTING")

# Reglas persistidas con cada activación; la documentación las explica (D027).
AUTHORITY = {
    "operational_state": "sqlite",  # runs, intentos, jobs, eventos, locks, commits y modo
    "legacy_history": "snapshot",  # copia inmutable con hashes; solo lectura, sin intentos inferidos
    "legacy_runs_in_checkout": "none",  # tras activar, escribir ahí es un escritor legacy
    "documents": "repository",  # requisitos/decisiones en Git; cambios = propuestas por hash
    "marker": "projection_of_activation",  # discrepancia con SQLite: modo no disponible
}
RULES = {
    "marker_path": MARKER_PATH,
    "legacy_scope": LEGACY_RUNS,
    "exclusive_per": ["canonical_root", "repository_common_dir"],
    "managed_requires": "ACTIVE activation, marker identical to the recorded one, no legacy drift",
    "legacy_drift": "new or modified entries under the legacy scope refuse managed work",
    "legacy_engine": "cannot read the marker; exclusion is cooperative and detected, not prevented",
    "authority": AUTHORITY,
}


class MigrationError(ValueError):
    """La activación/reversión se detiene con diagnóstico; nada nuevo queda activo."""


def digest(data: str | bytes) -> str:
    return hashlib.sha256(data.encode("utf-8") if isinstance(data, str) else data).hexdigest()


@dataclass(frozen=True)
class CheckoutFacts:
    """Hechos del sistema de archivos leídos sin seguir enlaces ni escribir."""

    root: str
    repository_key: str | None  # common dir Git canónico; None fuera de Git o ilegible
    main_checkout: str | None
    legacy_state: bool  # existe .harness/runs (de cualquier tipo) en root
    main_legacy_state: bool  # idem en el checkout principal, si es otro
    marker: bytes | None
    marker_error: str | None = None


@dataclass(frozen=True)
class ActivationView:
    id: str
    root: str
    repository_key: str | None
    status: str
    marker_sha256: str
    manifest: dict | None
    version: int


def inventory_fingerprint(inventory: LegacyInventory) -> str:
    """Independiente de la raíz: la copia reproduce la huella del origen."""
    return digest(freeze({
        "format": INVENTORY_FORMAT,
        "runs": [[run.path, run.identity] for run in inventory.runs],
        "artifacts": [[a.path, a.run_path, a.kind, a.format, a.status, a.sha256, a.size_bytes]
                      for a in inventory.artifacts],
    }))


def inventory_blockers(inventory: LegacyInventory) -> list[dict[str, Any]]:
    """Lo que no puede copiarse íntegro bloquea; una ausencia es solo observación."""
    blockers = []
    for artifact in inventory.artifacts:
        if artifact.status == "error":
            blockers.append({"code": "uncopyable_evidence", "path": artifact.path,
                             "diagnostic": artifact.diagnostic})
        elif artifact.status == "pending" and artifact.sha256 is None:
            blockers.append({"code": "changing_evidence", "path": artifact.path,
                             "diagnostic": artifact.diagnostic})
    return blockers


def observed_identities(inventory: LegacyInventory) -> dict[str, list[dict[str, Any]]]:
    """Identidades con su procedencia; discrepancias se conservan, no se resuelven."""
    found: dict[str, dict[str, list]] = {"tasks": {}, "phases": {}}

    def add(kind, value, path, field):
        if isinstance(value, str) and value.strip():
            found[kind].setdefault(value, []).append({"path": path, "field": field})

    for run in inventory.runs:
        if re.fullmatch(r"P\d+-T\d+", run.identity):
            add("tasks", run.identity, run.path, "run_directory")
        if match := re.fullmatch(r"(P\d+)-(?:CLOSE|RECONCILE)", run.identity):
            add("phases", match[1], run.path, "run_directory")
    for artifact in inventory.artifacts:
        payload = artifact.payload if isinstance(artifact.payload, dict) else {}
        if artifact.kind == "task":
            add("tasks", payload.get("task_id"), artifact.path, "task_id")
            add("phases", payload.get("phase_id"), artifact.path, "phase_id")
        elif artifact.kind in ("phase_review", "phase_metadata", "reconcile"):
            add("phases", payload.get("phase_id"), artifact.path, "phase_id")
            add("phases", payload.get("next_phase_id"), artifact.path, "next_phase_id")
    return {kind: [{"identity": key, "sources": sources} for key, sources in sorted(values.items())]
            for kind, values in found.items()}


def _documents(inventory: LegacyInventory) -> list[dict[str, Any]]:
    return [{"path": a.path, "status": a.status, "sha256": a.sha256}
            for a in inventory.artifacts if a.run_path is None and a.path.startswith("docs/")]


def build_preview(inventory: LegacyInventory, facts: CheckoutFacts,
                  blockers: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {state: sum(a.status == state for a in inventory.artifacts)
              for state in ("available", "pending", "error", "missing")}
    history = []
    for run in inventory.runs:
        owned = [a for a in inventory.artifacts if a.run_path == run.path]
        history.append({"path": run.path, "identity": run.identity, "artifacts": len(owned),
                        "statuses": {state: sum(a.status == state for a in owned)
                                     for state in ("available", "pending", "error", "missing")}})
    every = [*blockers, *inventory_blockers(inventory)]
    return {
        "format": PREVIEW_FORMAT, "root": facts.root, "repository_key": facts.repository_key,
        "inventory_sha256": inventory_fingerprint(inventory), "counts": counts,
        "read_only_history": history, "identities": observed_identities(inventory),
        "documents": _documents(inventory),
        "uncertainties": [{"path": a.path, "status": a.status, "diagnostic": a.diagnostic}
                          for a in inventory.artifacts if a.status != "available"],
        "activation": {"mode": "managed", "managed_runs_created": 0, "attempts_inferred": 0,
                       "marker_path": MARKER_PATH, "rules": RULES},
        "blockers": every, "ready": not every,
    }


def marker_bytes(activation_id: str, root: str, prepared_at: str) -> bytes:
    """Contenido determinista: reanudar reescribe exactamente los mismos bytes."""
    return (freeze({
        "format": MARKER_FORMAT, "activation_id": activation_id, "root": root, "prepared_at": prepared_at,
        "notice": "Checkout gestionado por Harness Local. No ejecutar aquí el motor legacy; "
                  "revertir desde Harness Local devuelve el checkout al modo legacy.",
    }) + "\n").encode("utf-8")


def build_manifest(activation_id: str, facts: CheckoutFacts, snapshot_root: str,
                   inventory: LegacyInventory, origin_mtimes: dict[str, int]) -> str:
    """Procedencia única de cada dato importado: ruta de origen, hash y copia."""
    return freeze({
        "format": MANIFEST_FORMAT, "activation_id": activation_id, "origin_root": facts.root,
        "repository_key": facts.repository_key, "snapshot_root": snapshot_root,
        "inventory_sha256": inventory_fingerprint(inventory),
        "runs": [{"path": run.path, "identity": run.identity} for run in inventory.runs],
        "artifacts": [{"path": a.path, "run_path": a.run_path, "kind": a.kind, "format": a.format,
                       "status": a.status, "sha256": a.sha256, "size_bytes": a.size_bytes,
                       "diagnostic": a.diagnostic, "copied": a.sha256 is not None,
                       "origin_mtime_ns": origin_mtimes.get(a.path)} for a in inventory.artifacts],
        "identities": observed_identities(inventory), "documents": _documents(inventory),
        "rules": RULES,
    })


def classify_drift(manifest: dict, observed: dict[str, tuple[str, int, int]],
                   hash_of: Callable[[str], str | None]) -> dict[str, list[str]]:
    """Compara el ámbito legacy actual con lo copiado. Borrar no es escribir.

    `observed`: ruta → (tipo `file`/`dir`/`other`, tamaño, mtime_ns). Un directorio
    nuevo (p. ej. un run recién creado y aún vacío) también es actividad legacy.
    """
    recorded = {entry["path"]: entry for entry in manifest["artifacts"]
                if entry["copied"] and entry["path"].startswith(LEGACY_RUNS + "/")}
    directories = {run["path"] for run in manifest["runs"]}
    for path in recorded:
        parts = path.split("/")
        directories.update("/".join(parts[:end]) for end in range(3, len(parts)))
    added, modified = [], []
    for path, (kind, size, mtime_ns) in sorted(observed.items()):
        entry = recorded.get(path)
        if kind == "dir":
            if path not in directories:
                added.append(path)
        elif entry is None or kind != "file":
            added.append(path)
        elif (size, mtime_ns) != (entry["size_bytes"], entry["origin_mtime_ns"]) and hash_of(path) != entry["sha256"]:
            modified.append(path)
    removed = sorted(path for path in recorded if path not in observed)
    return {"added": added, "modified": modified, "removed": removed}


def document_changes(manifest: dict, current: dict[str, str | None]) -> list[dict[str, Any]]:
    """Propuestas de importación por hash; nunca se mezclan en SQLite."""
    baseline = {entry["path"]: entry["sha256"] for entry in manifest["documents"]}
    proposals = []
    for path in sorted(set(baseline) | set(current)):
        before, after = baseline.get(path), current.get(path)
        if before != after:
            state = "added" if before is None else "removed" if after is None else "changed"
            proposals.append({"path": path, "state": state, "activation_sha256": before, "current_sha256": after})
    return proposals


def mode_refusal(facts: CheckoutFacts, live: ActivationView | None, source: CheckoutFacts | None,
                 drift: dict[str, list[str]] | None) -> str | None:
    """None si el motor gestionado puede operar en `facts.root`; si no, el diagnóstico."""
    if live is None:
        if facts.marker is not None or facts.marker_error:
            return ("Marcador de modo gestionado sin activación viva en esta base; "
                    "no se opera (otra base o activación incompleta).")
        if facts.legacy_state:
            return ("Checkout con estado legacy (.harness/runs) no activado; "
                    "generar la vista previa y activar el modo gestionado antes de operar.")
        if facts.main_legacy_state:
            return (f"El checkout principal {facts.main_checkout} tiene estado legacy no activado; "
                    "sus worktrees no se gestionan hasta activarlo.")
        return None
    if live.status != "ACTIVE":
        return f"Activación {live.id} en estado {live.status}; modo gestionado no disponible."
    if live.root != facts.root and facts.legacy_state:
        return (f"El repositorio está activado desde {live.root}; este checkout tiene estado legacy propio "
                "y no puede gestionarse.")
    if source is None or source.marker_error or source.marker is None:
        detail = source.marker_error if source and source.marker_error else "ausente"
        return f"Marcador de modo gestionado en {live.root} {detail}; modo gestionado no disponible."
    if digest(source.marker) != live.marker_sha256:
        return f"Marcador de modo gestionado en {live.root} modificado; no coincide con la activación {live.id}."
    if drift and (drift["added"] or drift["modified"]):
        changed = [*drift["added"], *drift["modified"]]
        return (f"Escritor legacy detectado tras la activación {live.id}: {len(changed)} rutas nuevas o "
                f"modificadas bajo {LEGACY_RUNS} (p. ej. {changed[0]}).")
    return None

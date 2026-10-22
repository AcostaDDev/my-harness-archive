"""Read-only compatibility rules for managed activations recorded by older releases."""
from dataclasses import dataclass
import hashlib
from typing import Callable

MARKER_PATH = ".harness/managed-mode.json"
LEGACY_RUNS = ".harness/runs"
LIVE_STATUSES = ("PREPARING", "ACTIVE", "REVERTING")

class MigrationError(ValueError):
    """An existing activation cannot authorize managed work."""

def digest(data: str | bytes) -> str:
    return hashlib.sha256(data.encode("utf-8") if isinstance(data, str) else data).hexdigest()


@dataclass(frozen=True)
class CheckoutFacts:
    """Filesystem facts read without following links or writing."""

    root: str
    repository_key: str | None  # canonical Git common dir; None outside Git or unreadable
    main_checkout: str | None
    legacy_state: bool  # .harness/runs exists (of any type) in root
    main_legacy_state: bool  # likewise in the main checkout, if different
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


def classify_drift(manifest: dict, observed: dict[str, tuple[str, int, int]],
                   hash_of: Callable[[str], str | None]) -> dict[str, list[str]]:
    """Compares the current legacy scope with what was copied. Deleting is not writing.

    `observed`: path → (type `file`/`dir`/`other`, size, mtime_ns). A new directory
    (e.g. a freshly created, still empty run) is also legacy activity.
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


def mode_refusal(facts: CheckoutFacts, live: ActivationView | None, source: CheckoutFacts | None,
                 drift: dict[str, list[str]] | None) -> str | None:
    """None if the managed engine may operate in `facts.root`; otherwise, the diagnosis."""
    if live is None:
        if facts.marker is not None or facts.marker_error:
            return ("Marcador de modo gestionado sin activación viva en esta base; "
                    "no se opera (otra base o activación incompleta).")
        if facts.legacy_state:
            return ("Checkout con estado legacy (.harness/runs) no activado; "
                    "legacy/A support has been removed; this checkout cannot be activated.")
        if facts.main_legacy_state:
            return (f"El checkout principal {facts.main_checkout} tiene estado legacy no activado; "
                    "legacy/A support has been removed; its worktrees cannot be activated.")
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

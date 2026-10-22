"""Facts read from a Git tree; no filesystem or provider access."""
from dataclasses import dataclass

class ImportInventoryError(ValueError):
    """The local Git tree cannot be inspected safely."""


@dataclass(frozen=True)
class TreeEntry:
    """Entrada del árbol de HEAD dentro del ámbito documental. `data` es None si no se leyó."""

    path: str
    mode: str
    size: int | None
    data: bytes | None = None
    diagnostic: str | None = None

"""Índice de observación: evidencias legacy, nunca intentos inferidos."""
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class LegacyRun:
    path: str
    identity: str


@dataclass(frozen=True)
class LegacyArtifact:
    path: str
    run_path: str | None
    kind: str
    format: str
    status: str
    sha256: str | None = None
    size_bytes: int | None = None
    payload: Any = None
    diagnostic: str | None = None


@dataclass(frozen=True)
class LegacyInventory:
    root: str
    runs: tuple[LegacyRun, ...]
    artifacts: tuple[LegacyArtifact, ...]


def field_observation(payload: Any, field: str) -> dict[str, Any]:
    """La etiqueta no registrado conserva la diferencia entre ausencia y null."""
    if not isinstance(payload, dict) or field not in payload:
        return {"state": "absent", "label": "no registrado"}
    if payload[field] is None:
        return {"state": "null", "label": "no registrado", "value": None}
    return {"state": "recorded", "value": payload[field]}


TELEMETRY_FIELDS = {
    "result": ("usage", "modelUsage", "num_turns", "duration_ms", "total_cost_usd"),
    "usage": ("usage", "model_usage", "actual_models", "num_turns", "duration_ms",
              "api_equivalent_cost_usd", "requested"),
    "request": ("model", "effort", "reason", "max_turns"),
}


def artifact_summary(artifact: LegacyArtifact) -> dict[str, Any]:
    result = {
        "path": artifact.path, "run_path": artifact.run_path,
        "kind": artifact.kind, "format": artifact.format, "status": artifact.status,
        "sha256": artifact.sha256, "size_bytes": artifact.size_bytes,
        "diagnostic": artifact.diagnostic,
    }
    if artifact.kind in TELEMETRY_FIELDS:
        result["fields"] = {name: field_observation(artifact.payload, name)
                            for name in TELEMETRY_FIELDS[artifact.kind]}
    if artifact.kind == "validation":
        commands = artifact.payload.get("commands", []) if isinstance(artifact.payload, dict) else []
        result["commands"] = [
            {"command": field_observation(command, "command"),
             "duration_seconds": field_observation(command, "duration_seconds")}
            for command in commands
        ] if isinstance(commands, list) else []
    # Los campos desconocidos son evidencia conservada, no defaults del producto.
    if artifact.format in ("json", "jsonl"):
        result["payload"] = artifact.payload
    return result


class LegacyReader(Protocol):
    def read(self, root: str) -> LegacyInventory: ...


class LegacyRepository(Protocol):
    def replace(self, inventory: LegacyInventory) -> None: ...
    def get(self, root: str) -> LegacyInventory | None: ...


class LegacyImportService:
    def __init__(self, repository: LegacyRepository, reader: LegacyReader):
        self.repository = repository
        self.reader = reader

    def import_checkout(self, root: str) -> LegacyInventory:
        inventory = self.reader.read(root)
        self.repository.replace(inventory)
        return inventory

    def summary(self, root: str) -> dict[str, Any] | None:
        inventory = self.repository.get(root)
        if inventory is None:
            return None
        counts = {state: sum(a.status == state for a in inventory.artifacts)
                  for state in ("available", "pending", "error", "missing")}
        return {
            "mode": "observation", "authority": "source_files", "root": inventory.root,
            "runs": [{"path": r.path, "identity": r.identity} for r in inventory.runs],
            "counts": counts,
            "artifacts": [artifact_summary(a) for a in inventory.artifacts],
        }

from datetime import datetime
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class SimulationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=120)


class SimulationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    created_at: datetime
    events: tuple[str, ...]
    kind: Literal["simulation"] = "simulation"
    status: Literal["completed"] = "completed"


class HealthRead(BaseModel):
    status: Literal["ok"] = "ok"
    mode: Literal["simulation"] = "simulation"


Item = TypeVar("Item")


class Page(BaseModel, Generic[Item]):
    items: list[Item]
    offset: int
    next_offset: int | None


class LegacyProjectRead(BaseModel):
    id: str
    name: str
    root: str
    observed_at: str
    mode: Literal["observation"]
    authority: Literal["source_files"]


class ProvenanceRead(BaseModel):
    path: str
    origin: str


class LegacyPhaseRead(BaseModel):
    identity: str
    provenance: list[ProvenanceRead]
    more_provenance: bool


class LegacyTaskRead(BaseModel):
    identity: str
    origin: Literal["run_directory"]


class LegacyRunRead(LegacyTaskRead):
    id: str
    path: str


class LegacyArtifactRead(BaseModel):
    id: str
    path: str
    run_id: str | None
    kind: str
    format: str
    status: Literal["available", "pending", "missing", "error"]
    sha256: str | None
    size_bytes: int | None
    diagnostic: str | None


class FieldRead(BaseModel):
    state: Literal["absent", "null", "recorded"]
    label: str | None = None
    value: Any = None
    truncated: bool = False


class EvidenceEntryRead(BaseModel):
    kind: str
    pointer: str
    fields: dict[str, FieldRead] = Field(default_factory=dict)
    value: Any = None
    truncated: bool = False


class EvidenceEntriesRead(Page[EvidenceEntryRead]):
    path: str
    sha256: str | None
    status: Literal["available", "pending", "missing", "error"]
    diagnostic: str | None
    origin: Literal["indexed_payload"]


class EvidenceContentRead(BaseModel):
    path: str
    indexed_sha256: str | None
    observed_sha256: str | None
    status: Literal["verified", "changed", "missing", "unindexed", "unsafe", "unreadable", "too_large", "invalid_utf8"]
    offset: int
    next_offset: int | None
    text: str | None
    diagnostic: str | None


class ObservationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    enabled: bool


class ObservationRead(BaseModel):
    enabled: bool
    diagnostic: str | None


class LegacyEventRead(BaseModel):
    id: int
    project_id: str
    root: str
    kind: Literal["index_updated", "watch_changed", "observation_error"]
    observed_at: str
    payload: dict[str, Any]


class LegacyUpdatesRead(BaseModel):
    items: list[LegacyEventRead]
    cursor: int
    has_more: bool

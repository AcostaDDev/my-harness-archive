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


# --- Modo gestionado (salida H2, parte 1) ---------------------------------------------


class ProblemRead(BaseModel):
    code: str
    diagnostic: str


class ProblemResponse(BaseModel):
    detail: ProblemRead


class SupervisorRead(BaseModel):
    enabled: bool
    alive: bool
    last_error: str | None
    ports_configured: bool
    commit_writer_configured: bool


class ManagedProjectRead(BaseModel):
    id: str
    root: str
    profile: str
    versions: dict[str, str | None]


ActivationStatus = Literal["PREPARING", "ACTIVE", "FAILED", "REVERTING", "REVERTED"]


class ActivationRead(BaseModel):
    id: str
    root: str
    repository_key: str | None
    status: ActivationStatus
    preview_sha256: str
    marker_sha256: str
    snapshot_root: str
    manifest_sha256: str | None
    version: int
    diagnostic: str | None
    export_path: str | None
    export_sha256: str | None


class ModeRead(BaseModel):
    project_id: str
    root: str
    refusal: str | None
    activation: ActivationRead | None
    drift: dict[str, list[str]] | None
    documents: list[dict[str, Any]] | None
    activations: list[ActivationRead]


class MigrationPreviewRead(BaseModel):
    format: str
    root: str
    repository_key: str | None
    inventory_sha256: str
    counts: dict[str, int]
    read_only_history: list[dict[str, Any]]
    identities: dict[str, list[dict[str, Any]]]
    documents: list[dict[str, Any]]
    uncertainties: list[dict[str, Any]]
    activation: dict[str, Any]
    blockers: list[dict[str, Any]]
    ready: bool


class ActivationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    preview_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    legacy_stopped: str = Field(min_length=1, max_length=2000)


class ActivationTransition(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    expected_version: int = Field(ge=1)
    reason: str = Field(min_length=1, max_length=2000)


class RunCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    task_id: str = Field(min_length=1, max_length=120)
    phase_id: str = Field(min_length=1, max_length=120)
    text: str = Field(min_length=1, max_length=200_000)


class RunActionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    action: Literal["revalidate", "retry_executor", "commit"]
    expected_version: int = Field(ge=0)


class ConfirmStoppedCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    owner_token: str = Field(min_length=1, max_length=64)
    expected_version: int = Field(ge=0)
    reason: str = Field(min_length=1, max_length=2000)


class ManagedJobRead(BaseModel):
    id: int
    run_id: str
    action: str
    status: str
    idempotency_key: str
    owner_token: str | None
    lease_until: str | None
    created_at: str
    finished_at: str | None
    diagnostic: str | None
    activation_id: str | None
    owner_closed: bool


class ManagedRunSummaryRead(BaseModel):
    id: str
    project_id: str | None
    root: str
    task_id: str
    phase_id: str
    status: str
    stage: str
    version: int
    revisions: int
    revision_limit: int
    created_at: str
    updated_at: str


class StopRead(BaseModel):
    stage: str
    reason: str


class CycleRead(BaseModel):
    diff: str
    provenance: dict[str, Any] | None
    validation: dict[str, Any]
    review: dict[str, Any] | None
    number: int
    verdict: str | None
    fingerprint: str
    changed_paths: list[str]


class AcceptanceRead(BaseModel):
    eligible: bool
    reasons: list[str]
    base_revision: str
    fingerprint: str
    changed_paths: list[str]


class ManagedHistoryRead(BaseModel):
    status: str
    task: dict[str, Any] | None
    stop: StopRead | None
    stops: list[StopRead]
    attempts: int
    cycles: list[CycleRead]
    acceptance: AcceptanceRead | None


class ManagedCommitRead(BaseModel):
    operation_id: str
    job_id: int
    status: Literal["INTENT", "COMMITTED", "INVALIDATED"]
    base_revision: str
    reviewed_fingerprint: str
    expected_tree: str
    expected_commit: str
    commit: str | None
    result: dict[str, Any] | None
    created_at: str
    finished_at: str | None


class ManagedRunRead(ManagedRunSummaryRead):
    versions: dict[str, str | None]
    history: ManagedHistoryRead
    commit: ManagedCommitRead | None
    locked_by_job: int | None


class ManagedAttemptRead(BaseModel):
    id: str
    number: int
    role: str
    selection: dict[str, Any]
    fresh_session: bool
    status: str
    versions: dict[str, str | None]
    result: dict[str, Any] | None
    started_at: str
    finished_at: str | None


class ManagedEventRead(BaseModel):
    id: int
    sequence: int
    kind: str
    recorded_at: str
    payload: dict[str, Any]


class ManagedEventsRead(BaseModel):
    items: list[ManagedEventRead]
    cursor: int
    has_more: bool

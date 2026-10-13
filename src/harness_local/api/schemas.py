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


class ReviewerAgentRead(BaseModel):
    """D052: el revisor planifica, revisa, evalúa fases, conversa y propone el bootstrap (solo lectura)."""
    provider: str | None  # null fuera de una composición CLI local-config-2 (demo o adaptador inyectado)
    model: str
    effort: str


class SelectionRead(BaseModel):
    model: str
    effort: str


class ExecutorAgentRead(BaseModel):
    """Único escritor; el revisor fija su modelo y esfuerzo en cada tarea y revisión."""
    provider: str | None
    selection_mode: Literal["catalog", "open"]
    models: list[str]
    efforts: list[str]
    effort_vocabulary: list[str]


class ProjectAgentsRead(BaseModel):
    planning_mode: Literal["auto", "agent", "deterministic"]
    reviewer: ReviewerAgentRead
    planner: SelectionRead
    executor: ExecutorAgentRead


class ManagedProjectRead(BaseModel):
    id: str
    root: str
    profile: str
    versions: dict[str, str | None]
    tag_kind: Literal["lightweight", "annotated"]
    agents: ProjectAgentsRead


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
    purpose: Literal['task', 'phase_check', 'phase_close', 'chat', 'document_export', 'bootstrap', 'bootstrap_discovery']


class StopRead(BaseModel):
    stage: str
    reason: str


class JUnitCaseRead(BaseModel):
    id: str
    reported_id: str | None
    name: str | None
    classname: str | None
    suite: list[str | None]
    result: Literal['passed', 'failed', 'error', 'skipped', 'unknown']
    duration_seconds: float | None
    message: str | None
    error_type: str | None
    error: str | None


class JUnitReportRead(BaseModel):
    path: str
    coverage: str
    status: Literal['complete', 'partial', 'invalid', 'missing', 'unreadable', 'limit', 'stale']
    diagnostics: list[str]
    sha256: str | None
    size_bytes: int | None
    freshness: Literal['unknown', 'created', 'changed', 'unchanged']
    case_count: int
    original_available: bool


class ValidationEntryRead(BaseModel):
    command: dict[str, Any] | None
    requested: str
    result: dict[str, Any]
    command_id: str | None
    reports: list[JUnitReportRead]


class ValidationRead(BaseModel):
    evidence: dict[str, Any]
    entries: list[ValidationEntryRead]
    run_id: str | None
    source_attempt_id: str | None


class JUnitCasesRead(BaseModel):
    report: JUnitReportRead
    run_id: str | None
    source_attempt_id: str | None
    command_id: str | None
    evidence: dict[str, Any]
    items: list[JUnitCaseRead]
    offset: int
    next_offset: int | None


class CycleRead(BaseModel):
    diff: str
    provenance: dict[str, Any] | None
    validation: ValidationRead
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
    actions: list[Literal['revalidate', 'retry_executor', 'commit', 'permissions']]
    versions: dict[str, str | None]
    history: ManagedHistoryRead
    commit: ManagedCommitRead | None
    locked_by_job: int | None


class ManagedAttemptRead(BaseModel):
    prompt: str
    permission_snapshot: dict[str, Any] | None = None
    prompt_snapshot: dict[str, Any] | None
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


class ManagedLogRead(BaseModel):
    stream: str
    source: str
    sha256: str
    size_bytes: int
    state: Literal['retained', 'purged', 'pending', 'missing', 'unverified']
    diagnostic: str | None
    authorization: dict[str, Any] | None


class ManagedEventsRead(BaseModel):
    items: list[ManagedEventRead]
    cursor: int
    has_more: bool


PromptScope = Literal['core', 'profile', 'project']


class PromptVersionRead(BaseModel):
    name: str
    id: str
    scope: str
    owner: str
    template: str
    sha256: str
    source: str


class PromptActivationRead(BaseModel):
    previous_id: str | None
    version_id: str
    reason: str
    generation: int
    created_at: str


class PromptDetailRead(BaseModel):
    name: str
    scope: PromptScope
    owner: str
    generation: int
    active_id: str | None
    effective: PromptVersionRead
    variables: list[str]
    versions: list[PromptVersionRead]
    activations: list[PromptActivationRead]


class PromptDraftCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    expected_version: int = Field(ge=0)
    template: str | None = Field(default=None, max_length=100000)
    from_version: str | None = Field(default=None, max_length=200)


class PromptActivateCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    expected_version: int = Field(ge=0)
    version_id: str = Field(min_length=1, max_length=200)
    reason: str = Field(min_length=1, max_length=2000)
    confirmed: Literal[True]


class PromptValidateCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    template: str = Field(max_length=100000)


class PromptValidationRead(BaseModel):
    variables: list[str]


class PromptDiffRead(BaseModel):
    diff: str


PermissionKind = Literal['files', 'tools', 'network', 'product', 'acceptance']


class PermissionCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    expected_version: int = Field(ge=0)
    kind: PermissionKind
    target: str = Field(min_length=1, max_length=2000)
    operation: str = Field(min_length=1, max_length=120)
    arguments: list[str] = Field(max_length=100)
    requested_by: str = Field(min_length=1, max_length=120)
    source_attempt_id: str = Field(min_length=1, max_length=36)
    reason: str = Field(min_length=1, max_length=2000)
    ttl_seconds: int = Field(ge=1, le=86400)
    supersedes: str | None = None


class PermissionDecisionCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    expected_version: int = Field(ge=0)
    expected_request_version: int = Field(ge=1)
    fingerprint: str = Field(pattern=r'^[a-f0-9]{64}$')
    decision: Literal['grant', 'deny']
    scope: Literal['once', 'task']
    reason: str = Field(min_length=1, max_length=2000)
    confirmed: Literal[True]


class PermissionRequestRead(BaseModel):
    id: str
    run_id: str
    version: int
    status: str
    effective_status: str
    request: dict[str, Any]
    fingerprint: str
    expires_at: str
    decision: dict[str, Any] | None
    consumed_by: str | None
    supersedes: str | None


PhaseStatus = Literal['ACTIVE', 'CHECKING', 'READY_TO_CLOSE', 'NEEDS_RECONCILIATION', 'BLOCKED', 'CLOSING', 'CLOSED',
                      'ABANDONED']
PhaseAction = Literal['check', 'reconcile', 'reconcile_task', 'close', 'question', 'authorize_batch', 'batch_next',
                      'amend', 'abandon']


class PhaseCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    code: str = Field(min_length=1, max_length=120)
    objective: str = Field(min_length=1, max_length=4000)
    exit_criteria: list[str] = Field(min_length=1, max_length=100)
    tasks: list[str] = Field(max_length=200)
    documents: list[str] | None = Field(default=None, max_length=50,
                                        description='Rutas del checkout; por defecto STATE y NEXT_STEPS del proyecto.')
    tag: str | None = Field(default=None, max_length=100)


class PhaseSummaryRead(BaseModel):
    id: str
    code: str
    objective: str
    status: PhaseStatus
    version: int
    created_at: str
    updated_at: str


class PhaseDocumentsRead(BaseModel):
    baseline: dict[str, str | None]
    current: dict[str, str | None] | None
    drift: list[str] | None
    current_sha256: str | None


class PhaseQuestionRead(BaseModel):
    id: str
    text: str
    source: dict[str, Any]
    status: Literal['OPEN', 'ANSWERED']
    answer: dict[str, Any] | None
    version: int
    created_at: str


class PhaseOperationRead(BaseModel):
    id: str
    kind: Literal['check', 'close', 'reconcile', 'reconcile_task', 'amend', 'abandon', 'document_export']
    run_id: str | None
    status: str
    previous_status: str
    request: dict[str, Any]
    result: dict[str, Any] | None
    created_at: str
    finished_at: str | None


class PhaseAuthorizationRead(BaseModel):
    id: str
    kind: Literal['batch', 'close']
    status: str
    effective_status: str
    scope: dict[str, Any]
    fingerprint: str
    actor: dict[str, Any]
    reason: str
    expires_at: str
    created_at: str
    closed: dict[str, Any] | None
    version: int


class PhaseReadyRead(BaseModel):
    operation_id: str
    binding: dict[str, Any]
    binding_sha256: str
    stale_reasons: list[str]


class PhaseDefinitionRead(BaseModel):
    number: int
    definition: dict[str, Any]
    definition_sha256: str
    documents: dict[str, str | None]
    origin: Literal['created', 'amended', 'migrated']
    reason: str | None
    actor: dict[str, Any] | None
    created_at: str


class PhaseRead(BaseModel):
    id: str
    project_id: str | None
    root: str
    code: str
    definition: dict[str, Any]
    definition_sha256: str
    definition_number: int
    definitions: list[PhaseDefinitionRead]
    tag_kind: Literal['lightweight', 'annotated'] | None = Field(
        description='Tipo de tag que fijará el cierre según el proyecto registrado; null si no está registrado.')
    status: PhaseStatus
    version: int
    created_at: str
    updated_at: str
    documents: PhaseDocumentsRead
    tasks: dict[str, dict[str, str] | None]
    questions: list[PhaseQuestionRead]
    operations: list[PhaseOperationRead]
    authorizations: list[PhaseAuthorizationRead]
    ready: PhaseReadyRead | None
    actions: list[PhaseAction]


class PhaseVersioned(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    expected_version: int = Field(ge=0)


class PhaseCheckCreate(PhaseVersioned):
    action: Literal['check']


class PhaseCloseCreate(PhaseVersioned):
    action: Literal['close']
    binding_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    reason: str = Field(min_length=1, max_length=2000)
    ttl_seconds: int = Field(default=3600, ge=1, le=86400)
    confirmed: Literal[True]


class PhaseReconcileCreate(PhaseVersioned):
    documents_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    reason: str = Field(min_length=1, max_length=2000)
    confirmed: Literal[True]


class PhaseQuestionCreate(PhaseVersioned):
    text: str = Field(min_length=1, max_length=4000)


class PhaseAnswerCreate(PhaseVersioned):
    expected_question_version: int = Field(ge=1)
    answer: str = Field(min_length=1, max_length=4000)
    confirmed: Literal[True]


class PhaseBatchCreate(PhaseVersioned):
    tasks: list[str] = Field(min_length=1, max_length=200)
    ttl_seconds: int = Field(ge=1, le=86400)
    reason: str = Field(min_length=1, max_length=2000)
    confirmed: Literal[True]
    chain_commits: bool = Field(default=False, description=(
        'Alcance explícito «encadenar tareas y confirmar commits»: el supervisor encola cada tarea, el commit de '
        'cada aceptación elegible y la siguiente tarea; se detiene en el primer bloqueo. Nunca comprueba ni cierra.'))
    text: str | None = Field(default=None, min_length=1, max_length=200_000,
                             description='Texto del plan congelado; obligatorio solo con chain_commits.')


class PhaseAmendCreate(PhaseVersioned):
    objective: str = Field(min_length=1, max_length=4000)
    exit_criteria: list[str] = Field(min_length=1, max_length=100)
    tasks: list[str] = Field(max_length=200)
    documents: list[str] = Field(min_length=1, max_length=50)
    tag: str | None = Field(default=None, max_length=100)
    reason: str = Field(min_length=1, max_length=2000)
    confirmed: Literal[True]


class PhaseAbandonCreate(PhaseVersioned):
    reason: str = Field(min_length=1, max_length=2000)
    confirmed: Literal[True]


class PhaseReconcileTaskCreate(PhaseVersioned):
    pass


class DocumentExportPreviewRead(BaseModel):
    expected_version: int
    resume_operation_id: str | None
    preview_sha256: str
    snapshot: dict[str, Any]
    baseline: dict[str, str | None]
    head: str
    fingerprint: str
    tree: str
    index_tree: str
    documents: list[dict[str, Any]]
    mechanical: list[dict[str, str]]
    diff: str


class DocumentExportCreate(PhaseVersioned):
    preview_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    resume_operation_id: str | None = Field(default=None, max_length=36)
    reason: str = Field(min_length=1, max_length=2000)
    confirmed: Literal[True]


class PhaseRevokeCreate(PhaseVersioned):
    reason: str = Field(min_length=1, max_length=2000)


class PhaseBatchNextCreate(PhaseVersioned):
    authorization_id: str = Field(min_length=1, max_length=36)
    text: str = Field(min_length=1, max_length=200_000)


# --- H4.1: chat contextual -------------------------------------------------------------------

ChatTurnStatus = Literal['QUEUED', 'ANSWERED', 'FAILED', 'UNKNOWN', 'REFUSED']


class ChatConversationCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    title: str = Field(min_length=1, max_length=200)
    phase_id: str | None = Field(default=None, max_length=36,
                                 description='Fase gestionada de este proyecto cuyo contexto se ofrece por defecto.')


class ChatConversationSummaryRead(BaseModel):
    id: str
    title: str
    phase_id: str | None
    phase_code: str | None
    turns: int
    version: int
    created_at: str
    updated_at: str


class ChatDocumentRead(BaseModel):
    path: str
    sha256: str | None = Field(description='null: el documento no existía al congelar el turno.')
    size: int | None
    truncated: bool


class ChatTurnRead(BaseModel):
    id: str
    number: int
    status: ChatTurnStatus
    run_id: str
    run_status: str
    message: str
    documents: list[ChatDocumentRead]
    run_ids: list[str]
    phase_code: str | None
    previous_turns: int
    context_sha256: str
    request_sha256: str
    result: dict[str, Any] | None
    actor: dict[str, Any]
    created_at: str
    finished_at: str | None


class ChatProposalRunRead(BaseModel):
    task_id: str
    phase_id: str
    status: str
    commit: str | None


class ChatProposalRead(BaseModel):
    id: str
    number: int
    turn_id: str
    turn_number: int
    status: Literal['PROPOSED', 'ACCEPTED', 'DISMISSED']
    proposal: dict[str, Any]
    proposal_sha256: str
    run_id: str | None
    run: ChatProposalRunRead | None
    decision: dict[str, Any] | None
    version: int
    created_at: str
    actions: list[Literal['accept', 'dismiss']]


class ChatPhaseRead(BaseModel):
    id: str
    code: str
    status: str


class ChatConversationRead(BaseModel):
    id: str
    project_id: str | None
    root: str
    title: str
    phase: ChatPhaseRead | None
    actor: dict[str, Any]
    version: int
    created_at: str
    updated_at: str
    turns: list[ChatTurnRead]
    proposals: list[ChatProposalRead]
    actions: list[Literal['message']]


class ChatMessageCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    expected_version: int = Field(ge=0)
    text: str = Field(min_length=1, max_length=20_000)
    documents: list[str] | None = Field(default=None, max_length=8, description=(
        'Documentos del checkout que se congelan como contexto; null: los de la fase o STATE y NEXT_STEPS.'))
    run_ids: list[str] = Field(default_factory=list, max_length=10,
                               description='Runs de este checkout cuya evidencia se congela como contexto.')


class ChatProposalAcceptCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    expected_version: int = Field(ge=0)
    proposal_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    task_id: str = Field(min_length=1, max_length=120)
    phase_id: str = Field(min_length=1, max_length=120)
    confirmed: Literal[True]


class ChatProposalDismissCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    expected_version: int = Field(ge=0)
    reason: str = Field(min_length=1, max_length=2000)


# --- H4.2: bootstrap guiado ------------------------------------------------------------------
class BootstrapBrief(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    problem: str = Field(min_length=1, max_length=4000)
    users: str = Field(min_length=1, max_length=4000)
    minimum_features: str = Field(min_length=1, max_length=4000)
    constraints: str = Field(min_length=1, max_length=4000)
    delivery_goal: str = Field(min_length=1, max_length=4000)


class BootstrapDecisions(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    scope: str = Field(min_length=1, max_length=4000)
    architecture: str = Field(min_length=1, max_length=4000)
    out_of_scope: str = Field(min_length=1, max_length=4000)


class BootstrapInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    brief: BootstrapBrief
    decisions: BootstrapDecisions


class BootstrapDocumentRead(BaseModel):
    path: str
    content: str
    sha256: str


class BootstrapPreviewRead(BaseModel):
    template: dict[str, str]
    input: BootstrapInput
    context_sha256: str
    documents: list[BootstrapDocumentRead]
    phase: dict[str, Any]
    first_task: dict[str, Any]
    task_text: str
    preparation: list[dict[str, Any]]
    validations: list[dict[str, Any]]
    policy: dict[str, Any]
    profile: str
    versions: dict[str, str | None]
    target: dict[str, Any]
    author: dict[str, str]
    git: dict[str, str]
    ready: bool
    preview_sha256: str
    resume_operation_id: str | None = None
    expected_version: int | None = None


class BootstrapCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    input: BootstrapInput
    preview_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    confirmed: Literal[True]
    reason: str = Field(min_length=1, max_length=2000)
    resume_operation_id: str | None = Field(default=None, max_length=36)
    expected_version: int | None = Field(default=None, ge=0)


class BootstrapOperationRead(BaseModel):
    id: str
    root: str
    run_id: str
    phase_id: str | None
    status: Literal['QUEUED', 'COMPLETED', 'INTERRUPTED']
    preview: BootstrapPreviewRead
    intent: dict[str, Any]
    decision: dict[str, Any]
    result: dict[str, Any] | None
    created_at: str
    finished_at: str | None
    expected_version: int
    run_status: str
    first_task_run: dict[str, str] | None


class BootstrapDiscoveryCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    brief: BootstrapBrief
    confirmed: Literal[True]


class BootstrapDiscoveryResultRead(BaseModel):
    summary: str
    requirements: list[str]
    alternatives: list[str]
    pending_decisions: list[str]


class BootstrapDiscoveryOutcomeRead(BaseModel):
    status: Literal['PROPOSED', 'FAILED', 'UNKNOWN']
    result: BootstrapDiscoveryResultRead | None
    reason: str | None


class BootstrapDiscoveryRead(BaseModel):
    run_id: str
    run_status: str
    brief: BootstrapBrief
    outcome: BootstrapDiscoveryOutcomeRead | None


class BootstrapStatusRead(BaseModel):
    enabled: bool
    import_required: bool
    diagnostic: str | None
    operation: BootstrapOperationRead | None
    discovery: BootstrapDiscoveryRead | None
    discovery_available: bool
    discovery_selection: dict[str, str]

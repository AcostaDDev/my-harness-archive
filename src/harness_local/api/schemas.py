from datetime import datetime
from typing import Annotated, Any, Generic, Literal, TypeVar

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
    documents: Literal["v2"] | None = Field(default=None, description="Contrato documental unificado D088; null solo en lecturas de proyectos anteriores.")
    source: Literal["operator", "registry"] = Field(
        default="operator", description="D076: declarado en el TOML del operador o registrado desde la UI.")
    registry_version: int | None = Field(default=None, description="Versión del registro congelada en sus jobs.")
    bootstrap_enabled: bool = False


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
    purpose: Literal['task', 'phase_check', 'phase_close', 'chat', 'document_export', 'bootstrap', 'bootstrap_discovery',
                     'definition', 'phase_planning', 'project_import', 'onboarding', 'import_commit',
                     'document_edit', 'phase_transition']



class PhaseTaskRead(BaseModel):
    """Resumen de una tarea de la fase para su URL `PNNN-TNNN` (D076); sin runs, `latest` es null."""
    task_id: str
    planned: bool = Field(description='La tarea figura en la definición vigente de la fase.')
    runs: int = Field(description='Runs de propósito task registrados para esta tarea.')
    latest: ManagedRunSummaryRead | None


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
    diff_sha256: str = Field(description='SHA-256 del diff revisado del ciclo (texto UTF-8 almacenado); su contenido se lee '
                                         'paginado en `/runs/{id}/cycles/{n}/diff`.')
    diff_bytes: int = Field(description='Tamaño en bytes UTF-8 del diff revisado del ciclo.')
    provenance: dict[str, Any] | None
    validation: ValidationRead
    review: dict[str, Any] | None
    formatting: dict[str, Any] | None = Field(default=None, description='Formateo del perfil tras el intento del '
                                              'ejecutor (comando, rutas, resultado); null si no hubo (D133).')
    number: int
    verdict: str | None
    fingerprint: str
    changed_paths: list[str]


class CycleDiffRead(BaseModel):
    run_id: str
    cycle: int
    sha256: str
    size_bytes: int
    offset: int
    next_offset: int | None = Field(description='Offset de la página siguiente; null en la última. Las páginas acaban en '
                                                'fin de línea salvo una línea mayor que el límite, cortada en un límite UTF-8.')
    text: str


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
    active_job: int | None = Field(description='Job del run en cola, en curso o pendiente de recuperación; null si el run '
                                               'no avanza sin una acción nueva.')


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
    kind: Literal['check', 'close', 'reconcile', 'reconcile_task', 'amend', 'abandon', 'document_export',
                  'transition', 'document_edit']
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
    successor: str | None = Field(description='Código de la fase posterior del checkout; null si esta es la última. Solo la '
                                              'última exporta su estado y decide sobre sus documentos.')


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


# --- D072/H6.3: contrato documental por fase -----------------------------------------------------


DocumentKind = Literal['phase', 'product', 'instructions', 'diagram', 'flow', 'phase_work', 'archive', 'other']


class DocumentStateRead(BaseModel):
    path: str
    kind: DocumentKind
    exists: bool
    sha256: str | None
    adopted_sha256: str | None
    drift: bool
    blocks: list[str]
    error: str | None


class DocumentFolderRead(BaseModel):
    path: str
    exists: bool


class DocumentChangeRead(BaseModel):
    path: str
    editable: bool


class DecisionEntryRead(BaseModel):
    id: str
    title: str
    status: str | None


class ArchivedPhaseRead(BaseModel):
    path: str
    files: list[str]


class DocumentsStatusRead(BaseModel):
    layout: Literal['v2']
    phase: dict[str, Any] | None
    documents: list[DocumentStateRead]
    folders: list[DocumentFolderRead]
    uncommitted: list[DocumentChangeRead] | None = Field(
        description='Cambios locales del checkout; null si no hay escritor Git configurado.')
    warnings: list[str]
    decisions: list[DecisionEntryRead]
    archive: list[ArchivedPhaseRead]
    unresolved_intent: bool
    git_error: str | None


class DocumentRead(BaseModel):
    path: str
    content: str
    sha256: str
    editable: bool
    archived: bool
    blocks: list[str]


class DocumentChange(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    path: str = Field(min_length=1, max_length=500)
    content: str = Field(max_length=512 * 1024)
    base_sha256: Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')] | None = Field(default=None, description=(
        'Hash con el que se abrió el documento en el editor (CAS); null: no debe existir. Sin el campo, no se compara.'))


class DocumentEditInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    source: Literal['content', 'worktree'] = Field(
        description='content: documentos enviados sobre un checkout limpio; worktree: cambios locales del editor.')
    changes: list[DocumentChange] | None = Field(default=None, max_length=50)
    regenerate_blocks: bool = Field(default=False, description=(
        'Solo worktree: sustituye los bloques gestionados editados en local por los de la base (H6.2 E3).'))


class DocumentPreviewEntry(BaseModel):
    path: str
    before_sha256: str | None
    after_sha256: str
    content: str
    disk_sha256: str | None = Field(default=None, description='Bytes locales que se sustituyen (bloques regenerados).')


class RegeneratedDocumentRead(BaseModel):
    path: str
    local_sha256: str
    diff: str = Field(description='Lo que se descarta de los bytes locales al regenerar los bloques.')


class DocumentTreeEntryRead(BaseModel):
    path: str
    kind: DocumentKind
    editable: bool
    archived: bool
    bytes: int


class DocumentTreeRead(BaseModel):
    docs: str
    files: list[DocumentTreeEntryRead]
    truncated: bool
    skipped: list[str] = Field(description='Enlaces simbólicos u objetos no regulares que no se listan.')


class DocumentOperationPreview(BaseModel):
    resume_operation_id: str | None
    preview_sha256: str
    operation: Literal['document_edit']
    head: str
    fingerprint: str
    tree: str
    index_tree: str
    documents: list[DocumentPreviewEntry]
    mechanical: list[dict[str, str]]
    diff: str


class DocumentEditPreviewRead(DocumentOperationPreview):
    source: Literal['content', 'worktree']
    regenerated: list[RegeneratedDocumentRead] = []


class DocumentEditCreate(DocumentEditInput):
    preview_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    resume_operation_id: str | None = Field(default=None, max_length=36)
    reason: str = Field(min_length=1, max_length=2000)
    confirmed: Literal[True]


class PhasePlanInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    next_steps: str | None = Field(default=None, max_length=512 * 1024)
    plan_proposal: 'PlanProposalRef | None' = None


class PhasePlanCreate(PhasePlanInput):
    preview_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    resume_operation_id: str | None = Field(default=None, max_length=36)
    reason: str = Field(min_length=1, max_length=2000)
    confirmed: Literal[True]


class PhasePlanPreviewRead(DocumentEditPreviewRead):
    phase_plan: dict[str, Any]


class PhaseRevokeCreate(PhaseVersioned):
    reason: str = Field(min_length=1, max_length=2000)


class PhaseBatchNextCreate(PhaseVersioned):
    authorization_id: str = Field(min_length=1, max_length=36)
    text: str = Field(min_length=1, max_length=200_000)


# --- H4.1: chat contextual -------------------------------------------------------------------

ChatTurnStatus = Literal['QUEUED', 'ANSWERED', 'FAILED', 'UNKNOWN', 'REFUSED']


class ChatConversationCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    task_run_id: str | None = Field(default=None, max_length=36)
    title: str = Field(min_length=1, max_length=200)
    phase_id: str | None = Field(default=None, max_length=36,
                                 description='Fase gestionada de este proyecto cuyo contexto se ofrece por defecto.')


class ChatConversationSummaryRead(BaseModel):
    id: str
    title: str
    phase_id: str | None
    phase_code: str | None
    task_run_id: str | None
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
    head: str | None
    command: dict[str, str] | None
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
    task_run_id: str | None
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


class ChatCommandCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    expected_version: int = Field(ge=0)
    text: str = Field(min_length=1, max_length=20_000)


class ChatCommandRead(BaseModel):
    name: Literal['estado', 'tests', 'siguiente', 'lote', 'check', 'cerrar', 'exportar', 'abrir-fase', 'tarea']
    argument: str
    conversation_version: int
    phase_code: str | None
    phase_version: int | None
    run_id: str | None
    run_version: int | None
    preview_sha256: str


# --- H6.5: creación y planificación conversacionales -----------------------------------------------

PlanningKind = Literal['definition', 'phase_planning', 'project_import', 'onboarding']
SHA256 = r'^[0-9a-f]{64}$'


class DefinitionDocumentRead(BaseModel):
    path: str
    content: str
    sha256: str
    before_sha256: str | None = Field(description='Hash del borrador en disco que se sustituye; null si no existía.')
    origin: Literal['draft', 'draft+blocks', 'template', 'archive']


class DefinitionPreviewRead(BaseModel):
    """Aceptación de la definición v2: bloqueos o los archivos íntegros del commit raíz (bootstrap D037)."""
    template: dict[str, str]
    input: dict[str, str]
    definition: dict[str, Any]
    context_sha256: str
    documents: list[DefinitionDocumentRead]
    phase: dict[str, Any] | None
    first_task: dict[str, Any] | None
    task_text: str | None
    blockers: list[str]
    warnings: list[str]
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


class DefinitionOperationRead(BaseModel):
    id: str
    root: str
    run_id: str
    phase_id: str | None
    status: Literal['QUEUED', 'COMPLETED', 'INTERRUPTED']
    preview: DefinitionPreviewRead
    intent: dict[str, Any]
    decision: dict[str, Any]
    result: dict[str, Any] | None
    created_at: str
    finished_at: str | None
    expected_version: int
    run_status: str
    first_task_run: dict[str, str] | None


class DefinitionAcceptCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    preview_sha256: str = Field(pattern=SHA256)
    confirmed: Literal[True]
    reason: str = Field(min_length=1, max_length=2000)
    resume_operation_id: str | None = Field(default=None, max_length=36)
    expected_version: int | None = Field(default=None, ge=0)


class PlanningConversationCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    kind: PlanningKind
    title: str = Field(min_length=1, max_length=200)
    brief: str | None = Field(default=None, min_length=1, max_length=256 * 1024, description=(
        'Brief Markdown (UTF-8, máximo 256 KiB) de una definición; null en la planificación y la importación.'))
    phase_id: str | None = Field(default=None, max_length=36,
                                 description='Fase ACTIVE sin tareas que se planifica; se conservan las conversaciones históricas anteriores.')


class PlanningConversationSummaryRead(BaseModel):
    id: str
    kind: PlanningKind
    title: str
    phase_id: str | None
    phase_code: str | None
    turns: int
    version: int
    created_at: str
    updated_at: str


class PlanningTurnRead(BaseModel):
    id: str
    number: int
    status: ChatTurnStatus
    run_id: str
    run_status: str
    message: str
    context_sha256: str
    request_sha256: str
    drafts: list[dict[str, Any]] = Field(description='Borradores congelados (ruta, hash, tamaño); definición e importación.')
    user_edits: list[dict[str, Any]] = Field(description='Ediciones del usuario detectadas por hash al congelar.')
    documents: list[dict[str, Any]] = Field(description='Documentos congelados; solo planificación de fase.')
    result: dict[str, Any] | None
    actor: dict[str, Any]
    created_at: str
    finished_at: str | None


class PlanningProposalRead(BaseModel):
    id: str
    number: int
    turn_id: str
    turn_number: int
    kind: Literal['draft', 'plan']
    path: str | None
    content: str
    reason: str
    content_sha256: str
    base_sha256: str | None = Field(description='CAS: hash del borrador que leyó el turno; null si no existía.')
    proposal_sha256: str
    status: Literal['PROPOSED', 'APPLIED', 'ACCEPTED', 'DISMISSED', 'SUPERSEDED']
    decision: dict[str, Any] | None
    version: int
    created_at: str
    actions: list[Literal['apply', 'dismiss']]


class PlanningQuestionRead(BaseModel):
    id: str
    text: str
    blocking: bool
    deferred: dict[str, Any] | None


class PlanningConversationRead(BaseModel):
    id: str
    project_id: str | None
    root: str
    kind: PlanningKind
    title: str
    phase: ChatPhaseRead | None
    brief: dict[str, Any] | None
    source: dict[str, Any] | None = Field(default=None, description=(
        'Importación (P008-T011): origen, HEAD, carpeta de documentos, huellas del inventario y del mapa congelados '
        'y fase activa detectada. Onboarding: HEAD, árbol y huella del inventario; null en las demás.'))
    known: dict[str, str | None]
    log: list[dict[str, Any]]
    questions: list[PlanningQuestionRead]
    pending: list[str]
    actor: dict[str, Any]
    version: int
    created_at: str
    updated_at: str
    created: bool = Field(description='Definición o importación ya confirmada; sus borradores quedan cerrados.')
    turns: list[PlanningTurnRead]
    proposals: list[PlanningProposalRead]
    actions: list[Literal['message', 'edit_draft', 'defer_question', 'accept']]
    operation: DefinitionOperationRead | None = None


class ImportStatusRead(BaseModel):
    """P008-T011: si la importación puede pasar a la vista previa; se recalcula releyendo checkout y borradores."""
    ready: bool
    blockers: list[str]
    warnings: list[str]
    source: dict[str, Any]
    drafts: dict[str, str] = Field(description='Hash de cada borrador del área privada de la importación.')
    conversation_version: int


class PlanningMessageCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    expected_version: int = Field(ge=0)
    text: str = Field(min_length=1, max_length=20_000)


class PlanningApplyCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    expected_version: int = Field(ge=0)
    proposal_sha256: str = Field(pattern=SHA256)
    confirmed: Literal[True]


class PlanningDismissCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    expected_version: int = Field(ge=0)
    reason: str = Field(min_length=1, max_length=2000)


class PlanningDeferCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    expected_version: int = Field(ge=0)
    question_id: str = Field(pattern=SHA256)
    reason: str = Field(min_length=1, max_length=2000)


class PlanningDraftEdit(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    expected_version: int = Field(ge=0)
    path: str = Field(min_length=1, max_length=500)
    content: str | None = Field(max_length=512 * 1024, description='Contenido completo; null borra el borrador.')
    base_sha256: str | None = Field(pattern=SHA256, description='CAS: hash actual en disco; null si no existe.')


class PlanningDraftStateRead(BaseModel):
    path: str
    sha256: str | None
    known_sha256: str | None
    user_edited: bool


class PlanningDraftsRead(BaseModel):
    created: bool
    allowed: dict[str, list[str]]
    drafts: list[PlanningDraftStateRead]
    foreign: list[str]
    foreign_truncated: bool
    invalid: list[str]
    import_required: bool


class PlanningDraftContentRead(BaseModel):
    path: str
    content: str
    sha256: str = Field(description='Hash en disco: la base de la CAS para editarlo.')
    known_sha256: str | None = Field(description='Hash que conoce el harness (último turno respondido o propuesta aplicada).')


class PlanningBriefRead(BaseModel):
    content: str
    sha256: str
    size: int


class PlanProposalRef(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    conversation_id: str = Field(min_length=1, max_length=36)
    proposal_id: str = Field(min_length=1, max_length=36)
    proposal_sha256: str = Field(pattern=SHA256)


class BootstrapStatusRead(BaseModel):
    enabled: bool
    import_required: bool
    diagnostic: str | None
    definition_operation: DefinitionOperationRead | None = Field(default=None, description=(
        'Creación confirmada desde la conversación de definición, con el commit raíz y P001.'))


# --- H6.4: métricas por intento y agregados (D072 §9) -------------------------------------------------

class MetricSumRead(BaseModel):
    sum: int | None = Field(description='Suma de los intentos que aportan el campo; null si ninguno lo aporta (no es cero).')
    attempts: int = Field(description='Intentos que aportan un valor al campo.')


class MetricAmountRead(BaseModel):
    sum: float | None
    attempts: int
    basis: Literal['api_equivalent_reported'] = Field(
        description='Coste equivalente API reportado por el proveedor; no es factura ni cuota.')


class MetricAccountingRead(BaseModel):
    terminal: int = Field(description='Intentos con el total acumulado del terminal (reportado).')
    messages: int = Field(description='Intentos sin terminal con uso por mensaje deduplicado (derivado, parcial).')
    absent: int


class ConsumptionRead(BaseModel):
    attempts: int
    accounting: MetricAccountingRead
    tokens: dict[str, MetricSumRead] = Field(description='uncached_input/cache_read/cache_write/output/reasoning '
                                                         '(⊆ output)/total, cada uno sumado por separado. La entrada '
                                                         'cruda no se agrega: su semántica depende del proveedor.')
    cost_usd: MetricAmountRead
    turns_reported: MetricSumRead = Field(description='num_turns de Claude.')
    turns_derived: MetricSumRead = Field(description='Elementos completados del stream de Codex.')
    tool_calls: MetricSumRead
    permission_denials: MetricSumRead
    attempt_wall_ms: MetricSumRead = Field(description='Suma de duraciones por intento: tiempo de agente, no transcurrido.')
    reported_duration_ms: MetricSumRead
    api_duration_ms: MetricSumRead


class ModelUsageRead(BaseModel):
    model: str
    input_tokens: int | None
    cache_read_tokens: int | None
    cache_write_tokens: int | None
    output_tokens: int | None
    reasoning_tokens: int | None
    cost_usd: float | None


class AttemptMetricRead(BaseModel):
    attempt_id: str
    run_id: str
    number: int
    root: str
    phase_code: str
    task_id: str
    purpose: str
    role: str
    provider: str | None
    adapter_version: str | None
    cli_version: str | None
    requested_model: str | None
    requested_effort: str | None
    reported_models: list[str] | None
    reported_effort: str | None
    status: str
    error: str | None
    verdict: str | None
    executor_round: int
    accounting: Literal['terminal', 'messages'] | None
    input_semantics: Literal['excludes_cache', 'includes_cache_read'] | None
    input_tokens: int | None
    cache_read_tokens: int | None
    cache_write_tokens: int | None
    output_tokens: int | None
    reasoning_tokens: int | None
    uncached_input_tokens: int | None
    total_tokens: int | None
    turns: int | None
    tool_calls: int | None
    tools: dict[str, int] | None
    permission_denials: int | None
    wall_ms: int | None
    duration_ms: int | None
    api_duration_ms: int | None
    cost_usd: float | None
    started_at: str
    finished_at: str | None
    day: str
    source: Literal['capture', 'backfill']
    normalization: str | None
    catalog: str
    provenance: dict[str, str] = Field(description='requested | reported | derived | measured | absent, por campo.')
    diagnostics: list[str]
    recorded_at: str
    models: list[ModelUsageRead]


MetricDimension = Literal['role', 'provider', 'requested_model', 'requested_effort', 'day', 'phase', 'task', 'status',
                          'purpose', 'root']
MetricOrder = Literal['attempts', 'tokens', 'key']


class MetricGroupRead(ConsumptionRead):
    key: str | None


class MetricGroupsRead(BaseModel):
    dimension: MetricDimension
    order: MetricOrder
    role: str | None
    items: list[MetricGroupRead]
    offset: int
    next_offset: int | None


class ModelMetricGroupRead(BaseModel):
    key: str
    attempts: int
    tokens: dict[str, MetricSumRead]
    cost_usd: MetricAmountRead


class ModelMetricGroupsRead(BaseModel):
    dimension: Literal['reported_model']
    order: MetricOrder
    role: str | None
    items: list[ModelMetricGroupRead]
    offset: int
    next_offset: int | None


class TaskAgentRead(BaseModel):
    role: str
    provider: str | None
    requested_model: str | None
    requested_effort: str | None
    attempts: int


class ValidationCountsRead(BaseModel):
    commands_passed: int
    commands_failed: int
    cases: dict[str, int] | None = Field(description='JUnit: passed, failed, error, skipped; null sin reportes legibles.')


class StopRead(BaseModel):
    stage: str
    reason: str


class TaskMetricsRead(BaseModel):
    root: str
    phase_code: str
    task_id: str
    runs: int
    status: str | None
    agents: list[TaskAgentRead]
    attempts_by_role: dict[str, int]
    executions: int
    corrections: int | None
    first_verdict: str | None
    accepted_first_time: bool | None
    started_at: str | None
    accepted_at: str | None
    committed_at: str | None
    seconds_to_accept: float | None
    seconds_to_commit: float | None
    tests: ValidationCountsRead | None = Field(description='Última validación de la tarea.')
    stops: list[StopRead]
    consumption: ConsumptionRead


class MetricsScopeRead(BaseModel):
    root: str | None
    phase: str | None
    task: str | None


class CountSumRead(BaseModel):
    sum: int
    tasks: int


class DurationSumRead(BaseModel):
    sum: float
    tasks: int
    max: float


class TaskQualityRead(BaseModel):
    count: int
    reviewed: int
    accepted_first_time: int
    committed: int
    corrections: CountSumRead | None
    seconds_to_commit: DurationSumRead | None


class ValidationTotalsRead(BaseModel):
    tasks_with_validation: int
    commands_passed: int
    commands_failed: int
    cases: dict[str, int] | None


class StopCountRead(BaseModel):
    purpose: str
    stage: str
    reason: str
    count: int


class StopsRead(BaseModel):
    distinct: int
    items: list[StopCountRead]


ValidationDimension = Literal['phase', 'task', 'root']


class ValidationGroupRead(BaseModel):
    key: str = Field(description='Fase, tarea o raíz. Los ciclos no guardan su hora: no hay agrupación por día.')
    validations: int = Field(description='Ciclos de validación de tareas, incluidas las revalidaciones.')
    passed: int = Field(description='Validaciones con todos los comandos correctos y sin fallos nuevos en JUnit.')
    failed: int
    commands_passed: int
    commands_failed: int
    cases: dict[str, int] | None = Field(description='JUnit: passed, failed, error, skipped; null sin reportes legibles.')
    validations_with_cases: int


class ValidationGroupsRead(BaseModel):
    dimension: ValidationDimension
    items: list[ValidationGroupRead]
    offset: int
    next_offset: int | None


class MetricsSummaryRead(BaseModel):
    scope: MetricsScopeRead
    catalog: str
    consumption: ConsumptionRead
    attempts_without_metrics: int = Field(description='Intentos resueltos sin fila: relleno explícito pendiente.')
    tasks: TaskQualityRead
    tests: ValidationTotalsRead
    stops: StopsRead


# --- H6.2 E2: registro de proyectos (D054/D076) ------------------------------------------

PermissionLayer = Literal['global', 'project', 'contract', 'provider']
PermissionKind = Literal['files', 'tools', 'network', 'product', 'acceptance']
ShortText = Annotated[str, Field(min_length=1, max_length=200)]


class RegistryPolicyInput(BaseModel):
    """Política D052 del proyecto: selecciones, nunca ejecutables ni entornos."""
    model_config = ConfigDict(extra='forbid', strict=True)
    planning_mode: Literal['agent', 'deterministic']
    executor_mode: Literal['catalog', 'open']
    executor_models: list[ShortText] = Field(min_length=1, max_length=20)
    executor_efforts: list[ShortText] = Field(min_length=1, max_length=10)
    max_revision_cycles: int | None = Field(default=None, ge=0, le=20)


class ReviewerSelectionInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    preset_id: str = Field(min_length=1, max_length=64)
    model: ShortText
    effort: ShortText


class ExecutorSelectionInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    preset_id: str = Field(min_length=1, max_length=64)


class AgentSelectionInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    reviewer: ReviewerSelectionInput
    executor: ExecutorSelectionInput


class AgentPresetRead(BaseModel):
    id: str
    provider: Literal['codex', 'claude']
    roles: list[Literal['reviewer', 'executor']]
    models: list[str]
    efforts: list[str]
    allow_open_executor: bool


class RegistryChangeInput(BaseModel):
    """Alta (`register`), cambio (`update`) o baja lógica (`retire`); la composición se nombra, no se define."""
    model_config = ConfigDict(extra='forbid', strict=True)
    action: Literal['register', 'update', 'retire']
    project_id: str = Field(min_length=1, max_length=64)
    expected_version: int = Field(ge=0, le=2**31, description='0 en el alta; la versión leída en un cambio o baja.')
    root: str | None = Field(default=None, max_length=4096, description='Solo en el alta; la raíz no cambia después.')
    composition: str | None = Field(default=None, max_length=64)
    policy: RegistryPolicyInput | None = None
    agent_selection: AgentSelectionInput | None = None
    tag_kind: Literal['lightweight', 'annotated'] = 'lightweight'
    documents: Literal['v2'] | None = 'v2'
    bootstrap_enabled: bool = False
    permission_authority: dict[PermissionLayer, dict[PermissionKind, list[ShortText]]] | None = Field(
        default=None, description='Techo de permisos por capa; null: sin techo explícito.')


class RegistryApplyCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    change: RegistryChangeInput
    preview_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    trust_root: str | None = Field(default=None, max_length=4096,
                                   description='Confirmación aparte de la confianza: la raíz canónica exacta.')
    reason: str | None = Field(default=None, max_length=2000)


class RegistryCompositionRead(BaseModel):
    name: str
    profile: str
    executables: list[str] = Field(description='Solo los nombres; las rutas quedan en el TOML.')
    environment_keys: list[str] = Field(description='Solo las claves; los valores nunca salen del TOML.')
    authorize_profile_commands: bool
    extra_commands: list[list[str]]


class RegisteredProjectSummaryRead(BaseModel):
    id: str
    creation_id: str | None = None
    version: int
    status: Literal['ACTIVE', 'RETIRED']
    root: str
    composition: str
    profile: str
    row_sha256: str
    created_at: str
    updated_at: str
    available: bool
    diagnostic: str | None = Field(description='Por qué una fila activa no se compone con el TOML actual.')


class RegistryRead(BaseModel):
    available: bool
    creation_available: bool = False
    format: str | None
    roots: list[str]
    bootstrap_enabled: bool
    compositions: list[RegistryCompositionRead]
    executor_provider: str | None
    reviewer_provider: str | None
    executor_effort_vocabulary: list[str]
    agent_presets: list[AgentPresetRead] = Field(default_factory=list)
    reserved_ids: list[str]
    operator_projects: list[str]
    projects: list[RegisteredProjectSummaryRead]
    trust_statement: str


class RegistryEventRead(BaseModel):
    version: int
    action: Literal['register', 'update', 'retire']
    row: dict[str, Any]
    row_sha256: str
    previous_sha256: str | None
    preview_sha256: str
    actor: dict[str, Any]
    reason: str | None
    recorded_at: str


class RegisteredProjectRead(RegisteredProjectSummaryRead):
    row: dict[str, Any]
    trust: dict[str, Any]
    unfinished_jobs: list[int]
    configuration_blockers: list[str] = Field(default_factory=list)
    history: list[RegistryEventRead]


class RegistryFieldChangeRead(BaseModel):
    field: str
    before: Any
    after: Any


class RegistryPreviewRead(BaseModel):
    action: Literal['register', 'update', 'retire']
    project_id: str
    expected_version: int
    version: int
    status: Literal['ACTIVE', 'RETIRED']
    row: dict[str, Any]
    row_sha256: str
    changes: list[RegistryFieldChangeRead]
    versions: dict[str, str | None] | None = Field(description='Versiones que congelarán sus jobs; null en la baja.')
    profile: str
    trust_required: bool
    trust_statement: str | None
    unfinished_jobs: list[int] = Field(description='Trabajos sin terminar del checkout: bloquean la confirmación.')
    configuration_blockers: list[str] = Field(default_factory=list)
    preview_sha256: str


class RegistryApplyRead(BaseModel):
    project: RegisteredProjectSummaryRead
    replayed: bool = Field(description='La misma confirmación ya estaba aplicada; no hay otra versión.')


class ImportPreviewRead(BaseModel):
    preview_sha256: str
    operation: Literal['import_commit']
    proposed_tree: str
    head: str
    fingerprint: str
    tree: str
    index_tree: str
    documents: list[dict[str, Any]]
    mechanical: list[dict[str, Any]]
    diff: str
    phase: dict[str, Any]
    baseline: dict[str, str]
    origin: dict[str, Any]
    source: dict[str, Any]
    moves: list[dict[str, Any]]
    preserved: list[dict[str, Any]]
    foreign: list[dict[str, Any]]
    result_tree: list[dict[str, Any]]
    warnings: list[str]
    author: dict[str, str]
    message: str
    versions: dict[str, Any]
    context: str
    resume_operation_id: str | None = None
    expected_version: int | None = None
    already_imported: bool = False
    flow: Literal['onboarding'] | None = None
    profile: dict[str, Any] | None = None
    profile_sha256: str | None = None
    profile_proposal: dict[str, Any] | None = None


class OnboardingConfirmCreate(DefinitionAcceptCreate):
    profile_sha256: str = Field(pattern=SHA256)


class ImportOperationRead(BaseModel):
    id: str
    root: str
    conversation_id: str
    run_id: str
    phase_id: str | None
    status: Literal['QUEUED', 'COMPLETED', 'INTERRUPTED']
    preview: ImportPreviewRead
    decision: dict[str, Any]
    result: dict[str, Any] | None
    expected_version: int
    run_status: str
    created_at: str
    finished_at: str | None


class ImportEntryRead(BaseModel):
    activation_required: bool
    refusal: str | None
    activation_preview: MigrationPreviewRead | None
    operation: ImportOperationRead | None


class CreationRootChangeInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    action: Literal['select', 'retire']
    expected_version: int = Field(ge=0)
    path: str | None = Field(default=None, max_length=4096)


class CreationRootApplyInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    change: CreationRootChangeInput
    preview_sha256: str = Field(pattern=SHA256)
    confirm_path: str | None = Field(default=None, max_length=4096)
    reason: str | None = Field(default=None, max_length=2000)


class CreationInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    project_id: str = Field(min_length=1, max_length=64)
    directory_name: str = Field(min_length=1, max_length=64)
    root_version: int = Field(ge=1)
    composition: str = Field(min_length=1, max_length=64)
    policy: RegistryPolicyInput
    agent_selection: AgentSelectionInput | None = None
    tag_kind: Literal['lightweight', 'annotated'] = 'lightweight'
    documents: Literal['v2'] = 'v2'
    permission_authority: dict[PermissionLayer, dict[PermissionKind, list[ShortText]]] | None = None


class CreationConfirmInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    change: CreationInput
    preview_sha256: str = Field(pattern=SHA256)
    trust_root: str = Field(min_length=1, max_length=4096)
    reason: str | None = Field(default=None, max_length=2000)


class CreationRootSnapshotRead(BaseModel):
    version: int
    status: Literal['ABSENT', 'ACTIVE', 'REVOKED']
    path: str | None
    identity: dict[str, int] | None
    row_sha256: str | None = None
    updated_at: str | None = None


class CreationOperationRead(BaseModel):
    id: str
    version: int
    project_id: str
    directory_name: str
    target: str
    reserved: bool
    authority: dict[str, Any]
    intent: dict[str, Any]
    intent_sha256: str
    status: Literal['INTENDED', 'DIRECTORY_CREATED', 'REGISTERED', 'BLOCKED', 'RECOVERY_REQUIRED', 'CANCELLED']
    child_identity: dict[str, int] | None
    result: dict[str, Any] | None
    diagnostic: str | None
    created_at: str
    updated_at: str
    history: list[dict[str, Any]] = Field(default_factory=list)


class CreationRootRead(CreationRootSnapshotRead):
    available: bool
    diagnostic: str | None
    bootstrap_enabled: bool
    permission_statement: str
    history: list[dict[str, Any]]
    operations: list[CreationOperationRead]


class CreationRootPreviewRead(BaseModel):
    action: Literal['select', 'retire']
    expected_version: int
    root: CreationRootSnapshotRead
    permission_statement: str
    preview_sha256: str
    replayed: bool = False


class CreationPreviewRead(BaseModel):
    contract: str
    authority: dict[str, Any]
    row: dict[str, Any]
    target: str
    directory_name: str
    versions: dict[str, str | None]
    profile: str
    profile_details: dict[str, Any]
    agents: ProjectAgentsRead
    composition: RegistryCompositionRead
    trust_statement: str
    permission_statement: str
    preview_sha256: str


class CreationResumeInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    expected_version: int = Field(ge=1)
    root_version: int = Field(ge=1)


class CreationResumePreviewRead(BaseModel):
    operation_id: str
    expected_version: int
    authority: dict[str, Any]
    intent_sha256: str
    target: str
    preview_sha256: str


class CreationResumeConfirmInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    change: CreationResumeInput
    preview_sha256: str = Field(pattern=SHA256)
    reason: str | None = Field(default=None, max_length=2000)


class CreationCancelInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    expected_version: int = Field(ge=1)
    intent_sha256: str = Field(pattern=SHA256)
    reason: str | None = Field(default=None, max_length=2000)


class PreparationChangeInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    expected_version: int = Field(ge=1)
    mode: Literal['offline', 'network']
    previous_id: str | None = Field(default=None, min_length=1, max_length=36)
    retry_step: int | None = Field(default=None, ge=0, le=100)


class PreparationConfirmInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    change: PreparationChangeInput
    preview_sha256: str = Field(pattern=SHA256)
    reason: str | None = Field(default=None, max_length=2000)


class PreparationControlInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    expected_version: int = Field(ge=1)
    plan_sha256: str = Field(pattern=SHA256)
    reason: str | None = Field(default=None, max_length=2000)


class PreparationPlanRead(BaseModel):
    model_config = ConfigDict(extra='allow')
    contract: str
    recipe: str
    project_id: str
    root: str
    preview_sha256: str
    files: list[dict[str, Any]]
    steps: list[dict[str, Any]]
    mode: Literal['offline', 'network']


class PreparationOperationRead(BaseModel):
    id: str
    project_id: str
    version: int
    status: Literal['QUEUED', 'ACTIVE', 'FAILED', 'RECOVERY_REQUIRED', 'CANCELLED', 'COMPLETED']
    plan: dict[str, Any]
    plan_sha256: str
    previous_id: str | None
    receipt: dict[str, Any] | None
    diagnostic: str | None
    cancel_requested: bool
    owner_closed: bool
    created_at: str
    updated_at: str
    steps: list[dict[str, Any]]
    events: list[dict[str, Any]]


class PreparationRead(BaseModel):
    available: bool
    prepared: bool
    diagnostic: str | None
    recipe: str | None
    project_version: int
    operation: PreparationOperationRead | None

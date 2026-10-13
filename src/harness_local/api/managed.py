"""API gestionada local: delega en la autoridad H2.2–H2.5 sin lógica nueva de motor.

Toda ruta exige Host de loopback; toda mutación exige además Origin de loopback
(si el navegador lo envía) y la cabecera `X-Harness-Local: 1`, que una página
ajena no puede añadir sin preflight CORS (el servicio no habilita CORS). Las
mutaciones que crean jobs exigen `Idempotency-Key`; las que cambian un recurso
existente, `expected_version`. Conflictos y rechazos de modo devuelven 409 con
diagnóstico; la biblioteca garantiza que no quedan efectos parciales.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query
from pydantic import Field

from harness_local.api.schemas import (
    PromptScope, PromptDetailRead, PromptVersionRead, PromptDraftCreate, PromptActivateCreate,
    PromptValidateCreate, PromptValidationRead, PromptDiffRead,
    ActivationCreate, ActivationRead, ActivationTransition, ConfirmStoppedCreate, ManagedAttemptRead,
    ManagedEventsRead, ManagedJobRead, ManagedProjectRead, ManagedRunRead, ManagedRunSummaryRead,
    MigrationPreviewRead, ModeRead, Page, ProblemResponse, RunActionCreate, RunCreate, SupervisorRead,
)
from harness_local.api.security import local_request, problem
from harness_local.core.migration import MigrationError
from harness_local.services.managed_runtime import ManagedRuntime
from harness_local.storage.managed import Conflict, OwnershipLost
from harness_local.storage.migration import ModeConflict

Offset = Annotated[int, Query(ge=0, le=2**53 - 1)]
Limit = Annotated[int, Query(ge=1, le=100)]
IdempotencyKey = Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=200,
                                       description="Misma clave y misma acción devuelven el mismo job.")]
ERRORS = {status: {"model": ProblemResponse} for status in (403, 404, 409, 422)}


def call(operation, /, *args, **kwargs):
    """Traduce los errores de la autoridad a HTTP. El orden importa: todos derivan de ValueError."""
    try:
        return operation(*args, **kwargs)
    except LookupError as error:
        raise problem(404, "not_found", str(error)) from error
    except Conflict as error:
        code = "mode_refused" if isinstance(error.__cause__, ModeConflict) else "conflict"
        raise problem(409, code, str(error)) from error
    except ModeConflict as error:
        raise problem(409, "migration_conflict", str(error)) from error
    except MigrationError as error:
        raise problem(409, "migration_refused", str(error)) from error
    except OwnershipLost as error:
        raise problem(409, "ownership_lost", str(error)) from error
    except ValueError as error:
        raise problem(422, "invalid_request", str(error)) from error
    except OSError as error:
        raise problem(409, "checkout_unreadable", f"{type(error).__name__}: {error}") from error


def _activation(record) -> dict:
    return {name: getattr(record, name) for name in (
        "id", "root", "repository_key", "status", "preview_sha256", "marker_sha256", "snapshot_root",
        "manifest_sha256", "version", "diagnostic", "export_path", "export_sha256")}


def managed_router(runtime: ManagedRuntime):
    router = APIRouter(prefix="/api/managed", dependencies=[Depends(local_request)], responses=ERRORS)

    def project_read(project):
        return {"id": project.id, "root": str(project.context.root), "profile": project.context.profile.name,
                "versions": dict(project.versions), "tag_kind": project.tag_kind}

    def project(project_id: str):
        return call(runtime.project, project_id)

    def configured_actions(detail):
        if runtime.project_id(detail['root']) is None:
            return {**detail, 'actions': []}
        if runtime.config.commit_factory is None:
            return {**detail, 'actions': [a for a in detail['actions'] if a != 'commit']}
        return detail

    def registered_run(run_id: str):
        """Las acciones solo operan sobre checkouts registrados en este servicio."""
        run = call(runtime.views.run, run_id)
        project_id = runtime.project_id(run["root"])
        if project_id is None:
            raise problem(404, "not_found", "El run pertenece a un checkout no registrado en este servicio.")
        return configured_actions({**run, "project_id": project_id})

    def registered_activation(activation_id: str):
        runtime.ready()
        record = call(runtime.migration.repository.get, activation_id)
        if runtime.project_id(record.root) is None:
            raise problem(404, "not_found", "La activación pertenece a un checkout no registrado.")
        return record

    def queued(job):
        runtime.notify()
        return call(runtime.views.job, job.id)

    @router.get("/supervisor", response_model=SupervisorRead, operation_id="managed_supervisor")
    def supervisor():
        return call(runtime.supervisor_status)

    @router.get("/projects", response_model=list[ManagedProjectRead], operation_id="managed_projects")
    def projects():
        runtime.ready()
        return [project_read(item) for item in runtime.projects.values()]

    @router.get("/projects/{project_id}", response_model=ManagedProjectRead, operation_id="managed_project")
    def project_detail(project_id: str):
        return project_read(project(project_id))

    # --- migración H2.5 ---------------------------------------------------------------

    @router.get("/projects/{project_id}/mode", response_model=ModeRead, operation_id="managed_mode")
    def mode(project_id: str):
        root = str(project(project_id).context.root)
        status = call(runtime.migration.status, root)
        live = status["activation"]
        return {"project_id": project_id, "root": root, "refusal": status["refusal"],
                "activation": _activation(call(runtime.migration.repository.get, live["id"])) if live else None,
                "drift": status["drift"], "documents": status["documents"],
                "activations": [_activation(item) for item in runtime.migration.repository.history(root)]}

    @router.get("/projects/{project_id}/migration/preview", response_model=MigrationPreviewRead,
                operation_id="managed_migration_preview")
    def preview(project_id: str):
        return call(runtime.migration.preview, project(project_id).context.root)

    @router.post("/projects/{project_id}/migration/activations", response_model=ActivationRead,
                 operation_id="managed_activate")
    def activate(project_id: str, body: ActivationCreate):
        """Idempotente por hash de vista previa: repetir devuelve la activación ACTIVE ya completada."""
        record = call(runtime.migration.activate, project(project_id).context.root,
                      preview_sha256=body.preview_sha256, legacy_stopped=body.legacy_stopped)
        return _activation(record)

    @router.get("/activations/{activation_id}", response_model=ActivationRead, operation_id="managed_activation")
    def activation(activation_id: str):
        return _activation(registered_activation(activation_id))

    @router.post("/activations/{activation_id}/resume", response_model=ActivationRead,
                 operation_id="managed_resume_activation")
    def resume_activation(activation_id: str, body: ActivationTransition):
        registered_activation(activation_id)
        return _activation(call(runtime.migration.resume_activation, activation_id, reason=body.reason,
                                expected_version=body.expected_version))

    @router.post("/activations/{activation_id}/abandon", response_model=ActivationRead,
                 operation_id="managed_abandon_activation")
    def abandon_activation(activation_id: str, body: ActivationTransition):
        registered_activation(activation_id)
        call(runtime.migration.abandon_activation, activation_id, reason=body.reason,
             expected_version=body.expected_version)
        return _activation(registered_activation(activation_id))

    @router.post("/activations/{activation_id}/revert", response_model=ActivationRead,
                 operation_id="managed_revert")
    def revert(activation_id: str, body: ActivationTransition):
        registered_activation(activation_id)
        return _activation(call(runtime.migration.revert, activation_id, reason=body.reason,
                                expected_version=body.expected_version))

    @router.post("/activations/{activation_id}/resume-revert", response_model=ActivationRead,
                 operation_id="managed_resume_revert")
    def resume_revert(activation_id: str, body: ActivationTransition):
        registered_activation(activation_id)
        return _activation(call(runtime.migration.resume_revert, activation_id, reason=body.reason,
                                expected_version=body.expected_version))

    # --- runs, jobs, intentos y eventos ---------------------------------------------

    @router.get("/projects/{project_id}/runs", response_model=Page[ManagedRunSummaryRead],
                operation_id="managed_runs")
    def runs(project_id: str, offset: Offset = 0, limit: Limit = 30):
        page = runtime.views.runs(str(project(project_id).context.root), offset, limit)
        return {**page, "items": [{**item, "project_id": project_id} for item in page["items"]]}

    def frozen_versions(item):
        from harness_local.core.engine.contracts import freeze
        versions = dict(item.versions)
        if item.permission_authority is not None:
            versions['permission_authority'] = freeze(item.permission_authority)
        return versions

    @router.post("/projects/{project_id}/runs", response_model=ManagedJobRead, status_code=202,
                 operation_id="managed_submit_run")
    def submit_run(project_id: str, body: RunCreate, idempotency_key: IdempotencyKey):
        item = project(project_id)
        job = call(runtime.repository.submit, item.context, body.task_id, body.phase_id, body.text,
                   frozen_versions(item), key=idempotency_key)
        return queued(job)

    @router.get("/runs/{run_id}", response_model=ManagedRunRead, operation_id="managed_run")
    def run(run_id: str):
        runtime.ready()
        detail = call(runtime.views.run, run_id)
        return configured_actions({**detail, "project_id": runtime.project_id(detail["root"])})

    @router.get("/runs/{run_id}/jobs", response_model=list[ManagedJobRead], operation_id="managed_run_jobs")
    def run_jobs(run_id: str):
        runtime.ready()
        return call(runtime.views.jobs, run_id)

    @router.get("/runs/{run_id}/attempts", response_model=Page[ManagedAttemptRead],
                operation_id="managed_run_attempts")
    def attempts(run_id: str, offset: Offset = 0, limit: Limit = 30):
        runtime.ready()
        return call(runtime.views.attempts, run_id, offset, limit)

    @router.get("/runs/{run_id}/events", response_model=ManagedEventsRead, operation_id="managed_run_events")
    def events(run_id: str, after: Offset = 0, limit: Limit = 100):
        """Solo eventos confirmados, por secuencia del run; `cursor` es el `after` de la página siguiente."""
        runtime.ready()
        return call(runtime.views.events, run_id, after, limit)

    @router.post("/runs/{run_id}/actions", response_model=ManagedJobRead, status_code=202,
                 operation_id="managed_run_action")
    def run_action(run_id: str, body: RunActionCreate, idempotency_key: IdempotencyKey):
        runtime.ready()
        registered_run(run_id)
        if body.action == "commit":
            if runtime.config.commit_factory is None:
                raise problem(409, "commit_writer_unavailable",
                              "Este servicio no tiene escritor Git configurado; el commit no se encola.")
            # Sin actualizaciones mecánicas por HTTP: el commit contiene exactamente lo revisado.
            job = call(runtime.repository.submit_commit, run_id, key=idempotency_key,
                       expected_version=body.expected_version)
        else:
            job = call(runtime.repository.resume, run_id, key=idempotency_key,
                       expected_version=body.expected_version, retry_executor=body.action == "retry_executor")
        return queued(job)

    @router.get("/jobs/{job_id}", response_model=ManagedJobRead, operation_id="managed_job")
    def job(job_id: int):
        runtime.ready()
        return call(runtime.views.job, job_id)

    @router.post("/jobs/{job_id}/confirm-stopped", response_model=ManagedRunRead,
                 operation_id="managed_confirm_stopped")
    def confirm_stopped(job_id: int, body: ConfirmStoppedCreate):
        """Afirmación del usuario tras descartar al escritor anterior; la autoridad comprueba procesos."""
        runtime.ready()
        detail = call(runtime.views.job, job_id)
        registered_run(detail["run_id"])
        call(runtime.repository.confirm_stopped, job_id, owner_token=body.owner_token,
             expected_version=body.expected_version, reason=body.reason)
        runtime.notify()
        return registered_run(detail["run_id"])

    @router.get("/projects/{project_id}/prompts", response_model=list[PromptDetailRead])
    def prompts(project_id: str, scope: PromptScope = "project"):
        from harness_local.core.engine.prompts import VARIABLES
        context = project(project_id).context
        return [call(runtime.prompts.detail, context, scope, name) for name in VARIABLES]

    @router.get("/projects/{project_id}/prompts/{name}", response_model=PromptDetailRead)
    def prompt_detail(project_id: str, name: str, scope: PromptScope = "project"):
        return call(runtime.prompts.detail, project(project_id).context, scope, name)

    @router.post("/projects/{project_id}/prompts/{name}/validate", response_model=PromptValidationRead)
    def validate_prompt(project_id: str, name: str, body: PromptValidateCreate):
        from harness_local.core.engine.prompts import validate
        project(project_id)
        return {"variables": call(validate, name, body.template)}

    @router.post("/projects/{project_id}/prompts/{name}/versions", response_model=PromptVersionRead, status_code=201)
    def draft_prompt(project_id: str, name: str, body: PromptDraftCreate, scope: PromptScope = "project"):
        return call(runtime.prompts.draft, project(project_id).context, scope, name, body.expected_version,
                    text=body.template, from_version=body.from_version)

    @router.post("/projects/{project_id}/prompts/{name}/activate", response_model=PromptDetailRead)
    def activate_prompt(project_id: str, name: str, body: PromptActivateCreate, scope: PromptScope = "project"):
        context = project(project_id).context
        call(runtime.prompts.activate, context, scope, name, body.expected_version, body.version_id, body.reason)
        return call(runtime.prompts.detail, context, scope, name)

    @router.get("/projects/{project_id}/prompts/{name}/diff", response_model=PromptDiffRead)
    def prompt_diff(project_id: str, name: str, before: str, after: str):
        return {"diff": call(runtime.prompts.diff, project(project_id).context, name, before, after)}

    from harness_local.api.schemas import PermissionCreate, PermissionDecisionCreate, PermissionRequestRead

    @router.get('/runs/{run_id}/permissions', response_model=list[PermissionRequestRead])
    def permissions(run_id: str):
        registered_run(run_id)
        return call(runtime.permissions.list, run_id)

    @router.post('/runs/{run_id}/permissions', response_model=PermissionRequestRead, status_code=201)
    def request_permission(run_id: str, body: PermissionCreate):
        registered_run(run_id)
        values = body.model_dump()
        expected = values.pop('expected_version')
        return call(runtime.permissions.create, run_id, expected, **values)

    @router.post('/runs/{run_id}/permissions/{permission_id}/decision', response_model=PermissionRequestRead)
    def decide_permission(run_id: str, permission_id: str, body: PermissionDecisionCreate):
        registered_run(run_id)
        values = body.model_dump(exclude={'confirmed'})
        expected = values.pop('expected_version')
        return call(runtime.permissions.decide, run_id, permission_id, expected, **values)

    # --- H3.3: fases ----------------------------------------------------------------

    from harness_local.api.schemas import (
        PhaseAbandonCreate, PhaseAmendCreate, PhaseAnswerCreate, PhaseBatchCreate, PhaseBatchNextCreate,
        PhaseCheckCreate, PhaseCloseCreate, PhaseCreate, PhaseQuestionCreate, PhaseRead, PhaseReconcileCreate,
        PhaseReconcileTaskCreate, PhaseRevokeCreate, PhaseSummaryRead,
    )
    from harness_local.core.engine.phases import document_hashes

    def phase_read(phase_id: str):
        """Lectura con documentos actuales (disco) y acciones calculadas por el servidor."""
        runtime.ready()
        root, definition = call(runtime.phases.definition, phase_id)
        project_id = runtime.project_id(root)
        current = None
        if project_id is not None:
            try:
                current = document_hashes(runtime.projects[project_id].context, definition["documents"])
            except (OSError, ValueError):
                current = None
        detail = call(runtime.phases.get, phase_id, current)
        actions = detail["actions"] if project_id is not None else []
        if current is None:
            actions = [a for a in actions if a != "reconcile"]
        if runtime.config.commit_factory is None:
            actions = [a for a in actions if a not in ("check", "close", "reconcile_task")]
        tag_kind = runtime.projects[project_id].tag_kind if project_id is not None else None
        return {**detail, "project_id": project_id, "actions": actions, "tag_kind": tag_kind}

    def registered_phase(phase_id: str):
        detail = phase_read(phase_id)
        if detail["project_id"] is None:
            raise problem(404, "not_found", "La fase pertenece a un checkout no registrado en este servicio.")
        return runtime.projects[detail["project_id"]], detail

    @router.get("/projects/{project_id}/phases", response_model=list[PhaseSummaryRead], operation_id="managed_phases")
    def phases(project_id: str):
        return call(runtime.phases.list, str(project(project_id).context.root))

    @router.post("/projects/{project_id}/phases", response_model=PhaseRead, status_code=201,
                 operation_id="managed_create_phase")
    def create_phase(project_id: str, body: PhaseCreate):
        context = project(project_id).context
        data = body.model_dump()
        if data["documents"] is None:
            data["documents"] = [context.state_file, context.next_steps_file]
        return phase_read(call(runtime.phases.create, context, data))

    @router.get("/phases/{phase_id}", response_model=PhaseRead, operation_id="managed_phase")
    def phase(phase_id: str):
        return phase_read(phase_id)

    @router.get("/phases/{phase_id}/events", response_model=ManagedEventsRead, operation_id="managed_phase_events")
    def phase_events(phase_id: str, after: Offset = 0, limit: Limit = 100):
        runtime.ready()
        return call(runtime.phases.events, phase_id, after, limit)

    @router.post("/phases/{phase_id}/actions", response_model=ManagedJobRead, status_code=202,
                 operation_id="managed_phase_action")
    def phase_action(phase_id: str, body: Annotated[PhaseCheckCreate | PhaseCloseCreate, Field(discriminator="action")],
                     idempotency_key: IdempotencyKey):
        """check y close son jobs bajo el lock del checkout; el cierre exige su propia autorización."""
        item, _ = registered_phase(phase_id)
        if runtime.config.commit_factory is None:
            raise problem(409, "commit_writer_unavailable",
                          "Este servicio no tiene escritor Git configurado; las operaciones de fase no se encolan.")
        if body.action == "check":
            job = call(runtime.phases.submit_check, item.context, phase_id, body.expected_version,
                       key=idempotency_key, versions=frozen_versions(item))
        else:
            job = call(runtime.phases.submit_close, item.context, phase_id, body.expected_version,
                       key=idempotency_key, versions=frozen_versions(item), binding_sha256=body.binding_sha256,
                       reason=body.reason, ttl_seconds=body.ttl_seconds, tag_kind=item.tag_kind)
        return queued(job)

    @router.post("/phases/{phase_id}/reconcile", response_model=PhaseRead, operation_id="managed_phase_reconcile")
    def reconcile_phase(phase_id: str, body: PhaseReconcileCreate):
        item, _ = registered_phase(phase_id)
        call(runtime.phases.reconcile, item.context, phase_id, body.expected_version,
             documents_sha256=body.documents_sha256, reason=body.reason)
        return phase_read(phase_id)

    @router.post("/phases/{phase_id}/questions", response_model=PhaseRead, status_code=201,
                 operation_id="managed_phase_question")
    def raise_question(phase_id: str, body: PhaseQuestionCreate):
        registered_phase(phase_id)
        call(runtime.phases.raise_question, phase_id, body.expected_version, text=body.text)
        return phase_read(phase_id)

    @router.post("/phases/{phase_id}/questions/{question_id}/answer", response_model=PhaseRead,
                 operation_id="managed_phase_answer")
    def answer_question(phase_id: str, question_id: str, body: PhaseAnswerCreate):
        registered_phase(phase_id)
        call(runtime.phases.answer, phase_id, question_id, body.expected_version,
             expected_question_version=body.expected_question_version, answer=body.answer)
        return phase_read(phase_id)

    @router.post("/phases/{phase_id}/authorizations", response_model=PhaseRead, status_code=201,
                 operation_id="managed_phase_authorize_batch")
    def authorize_batch(phase_id: str, body: PhaseBatchCreate):
        """Solo lote: nunca autoriza check ni cierre. Con `chain_commits`, el supervisor encadena tareas y commits."""
        item, _ = registered_phase(phase_id)
        if body.chain_commits and runtime.config.commit_factory is None:
            raise problem(409, "commit_writer_unavailable",
                          "Este servicio no tiene escritor Git configurado; un lote con commits no se autoriza.")
        call(runtime.phases.authorize_batch, phase_id, body.expected_version, tasks=body.tasks,
             ttl_seconds=body.ttl_seconds, reason=body.reason, chain_commits=body.chain_commits, text=body.text,
             context=item.context, versions=frozen_versions(item))
        runtime.notify()
        return phase_read(phase_id)

    @router.post("/phases/{phase_id}/authorizations/{authorization_id}/revoke", response_model=PhaseRead,
                 operation_id="managed_phase_revoke")
    def revoke_batch(phase_id: str, authorization_id: str, body: PhaseRevokeCreate):
        registered_phase(phase_id)
        call(runtime.phases.revoke, phase_id, authorization_id, body.expected_version, reason=body.reason)
        return phase_read(phase_id)

    @router.post("/phases/{phase_id}/batch/next", response_model=ManagedJobRead, status_code=202,
                 operation_id="managed_phase_batch_next")
    def batch_next(phase_id: str, body: PhaseBatchNextCreate, idempotency_key: IdempotencyKey):
        item, _ = registered_phase(phase_id)
        job = call(runtime.phases.batch_next, item.context, phase_id, body.expected_version, key=idempotency_key,
                   versions=frozen_versions(item), authorization_id=body.authorization_id, text=body.text)
        return queued(job)

    # --- H3.4: enmienda, abandono y reconciliación con agente ---------------------------

    @router.post("/phases/{phase_id}/amend", response_model=PhaseRead, operation_id="managed_phase_amend")
    def amend_phase(phase_id: str, body: PhaseAmendCreate):
        """Nueva versión de la definición (la anterior se conserva); invalida READY y lotes vigentes."""
        item, _ = registered_phase(phase_id)
        data = body.model_dump(exclude={"expected_version", "reason", "confirmed"})
        call(runtime.phases.amend, item.context, phase_id, body.expected_version, data=data, reason=body.reason)
        return phase_read(phase_id)

    @router.post("/phases/{phase_id}/abandon", response_model=PhaseRead, operation_id="managed_phase_abandon")
    def abandon_phase(phase_id: str, body: PhaseAbandonCreate):
        item, _ = registered_phase(phase_id)
        call(runtime.phases.abandon, phase_id, body.expected_version, reason=body.reason, context=item.context)
        return phase_read(phase_id)

    @router.post("/phases/{phase_id}/reconcile-task", response_model=ManagedJobRead, status_code=202,
                 operation_id="managed_phase_reconcile_task")
    def reconcile_task(phase_id: str, body: PhaseReconcileTaskCreate, idempotency_key: IdempotencyKey):
        """Tarea normal con contrato determinista limitado a los documentos; sin adopción automática."""
        item, _ = registered_phase(phase_id)
        if runtime.config.commit_factory is None:
            raise problem(409, "commit_writer_unavailable",
                          "Este servicio no tiene escritor Git configurado; la reconciliación con agente no podría "
                          "confirmarse y no se encola.")
        job = call(runtime.phases.submit_reconcile_task, item.context, phase_id, body.expected_version,
                   key=idempotency_key, versions=frozen_versions(item))
        return queued(job)

    # --- Exportación mecánica confirmada de documentos -----------------------------------------
    from harness_local.api.schemas import DocumentExportCreate, DocumentExportPreviewRead
    from harness_local.storage.document_export import DocumentExportRepository

    def export_writer(item):
        if runtime.config.commit_factory is None:
            raise problem(409, 'commit_writer_unavailable', 'La exportación requiere un escritor Git configurado.')
        return runtime.config.commit_factory(item.context, frozen_versions(item))

    @router.get('/phases/{phase_id}/export', response_model=DocumentExportPreviewRead,
                operation_id='managed_document_export_preview')
    def export_preview(phase_id: str):
        item, _ = registered_phase(phase_id)
        return call(DocumentExportRepository(runtime.repository).preview, item.context, phase_id, export_writer(item))

    @router.post('/phases/{phase_id}/export', response_model=ManagedJobRead, status_code=202,
                 operation_id='managed_document_export')
    def export_documents(phase_id: str, body: DocumentExportCreate, idempotency_key: IdempotencyKey):
        item, _ = registered_phase(phase_id)
        job = call(DocumentExportRepository(runtime.repository).submit, item.context, phase_id, body.expected_version,
                   key=idempotency_key, versions=frozen_versions(item), git=export_writer(item),
                   **body.model_dump(exclude={'expected_version'}))
        return queued(job)

    # --- H4.1: chat contextual -----------------------------------------------------------------

    from harness_local.api.schemas import (
        ChatConversationCreate, ChatConversationRead, ChatConversationSummaryRead, ChatMessageCreate,
        ChatProposalAcceptCreate, ChatProposalDismissCreate,
    )

    def conversation_read(conversation_id: str):
        runtime.ready()
        detail = call(runtime.chat.get, conversation_id)
        project_id = runtime.project_id(detail["root"])
        actions = detail["actions"] if project_id is not None else []
        proposals = [{**item, "actions": item["actions"] if project_id is not None else []}
                     for item in detail["proposals"]]
        return {**detail, "project_id": project_id, "actions": actions, "proposals": proposals}

    def registered_conversation(conversation_id: str):
        runtime.ready()
        project_id = runtime.project_id(call(runtime.chat.root, conversation_id))
        if project_id is None:
            raise problem(404, "not_found", "La conversación pertenece a un checkout no registrado en este servicio.")
        return runtime.projects[project_id]

    @router.get("/projects/{project_id}/conversations", response_model=list[ChatConversationSummaryRead],
                operation_id="managed_conversations")
    def conversations(project_id: str):
        return call(runtime.chat.list, str(project(project_id).context.root))

    @router.post("/projects/{project_id}/conversations", response_model=ChatConversationRead, status_code=201,
                 operation_id="managed_create_conversation")
    def create_conversation(project_id: str, body: ChatConversationCreate):
        """Conversación separada del flujo de ejecución; no encola nada."""
        context = project(project_id).context
        return conversation_read(call(runtime.chat.create, context, title=body.title, phase_id=body.phase_id))

    @router.get("/conversations/{conversation_id}", response_model=ChatConversationRead,
                operation_id="managed_conversation")
    def conversation(conversation_id: str):
        return conversation_read(conversation_id)

    @router.post("/conversations/{conversation_id}/messages", response_model=ManagedJobRead, status_code=202,
                 operation_id="managed_chat_message")
    def chat_message(conversation_id: str, body: ChatMessageCreate, idempotency_key: IdempotencyKey):
        """Turno nuevo de solo lectura: mensaje y contexto se congelan al encolar; sin sesión del proveedor."""
        item = registered_conversation(conversation_id)
        job = call(runtime.chat.submit_message, item.context, conversation_id, body.expected_version,
                   key=idempotency_key, versions=frozen_versions(item), text=body.text, documents=body.documents,
                   run_ids=body.run_ids)
        return queued(job)

    @router.post("/conversations/{conversation_id}/proposals/{proposal_id}/accept", response_model=ManagedJobRead,
                 status_code=202, operation_id="managed_chat_accept")
    def accept_proposal(conversation_id: str, proposal_id: str, body: ChatProposalAcceptCreate,
                        idempotency_key: IdempotencyKey):
        """Confirmación explícita del hash mostrado → tarea normal vinculada (planificar, ejecutar, revisar)."""
        item = registered_conversation(conversation_id)
        job = call(runtime.chat.accept, item.context, conversation_id, proposal_id, body.expected_version,
                   key=idempotency_key, versions=frozen_versions(item), proposal_sha256=body.proposal_sha256,
                   task_id=body.task_id, phase_id=body.phase_id, confirmed=body.confirmed)
        return queued(job)

    @router.post("/conversations/{conversation_id}/proposals/{proposal_id}/dismiss",
                 response_model=ChatConversationRead, operation_id="managed_chat_dismiss")
    def dismiss_proposal(conversation_id: str, proposal_id: str, body: ChatProposalDismissCreate):
        registered_conversation(conversation_id)
        call(runtime.chat.dismiss, conversation_id, proposal_id, body.expected_version, reason=body.reason)
        return conversation_read(conversation_id)

    return router

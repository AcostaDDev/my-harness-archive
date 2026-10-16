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
from fastapi.responses import Response
from pydantic import Field

from harness_local.api.schemas import (
    CycleDiffRead, JUnitCasesRead, ManagedLogRead,
    PromptScope, PromptDetailRead, PromptVersionRead, PromptDraftCreate, PromptActivateCreate,
    PromptValidateCreate, PromptValidationRead, PromptDiffRead,
    ActivationCreate, ActivationRead, ActivationTransition, ConfirmStoppedCreate, ManagedAttemptRead,
    ManagedEventsRead, ManagedJobRead, ManagedProjectRead, ManagedRunRead, ManagedRunSummaryRead,
    MigrationPreviewRead, ModeRead, Page, PhaseTaskRead, ProblemResponse, RunActionCreate, RunCreate, SupervisorRead,
)
from harness_local.api.security import local_request, problem
from harness_local.core.engine.document_ops import BaseChanged
from harness_local.core.migration import MigrationError
from harness_local.services.managed_runtime import ManagedRuntime, agents_view
from harness_local.storage.documents import IMAGE_TYPES
from harness_local.storage.managed import Conflict, OwnershipLost
from harness_local.storage.migration import ModeConflict

Offset = Annotated[int, Query(ge=0, le=2**53 - 1)]
Limit = Annotated[int, Query(ge=1, le=100)]
DiffLimit = Annotated[int, Query(ge=4096, le=512 * 1024)]
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
        code = ("mode_refused" if isinstance(error.__cause__, ModeConflict)
                else "document_changed" if isinstance(error.__cause__, BaseChanged) else "conflict")
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
                "versions": dict(project.versions), "tag_kind": project.tag_kind, "agents": agents_view(project),
                "documents": project.context.documents, "bootstrap_enabled": project.bootstrap_enabled,
                "source": "registry" if "project_registry" in project.versions else "operator",
                "registry_version": int(project.versions["project_registry"])
                if "project_registry" in project.versions else None}

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

    # --- registro de proyectos H6.2 E2 (D054/D076) -------------------------------------
    from harness_local.api.schemas import (
        RegisteredProjectRead, RegistryApplyCreate, RegistryApplyRead, RegistryChangeInput, RegistryPreviewRead,
        RegistryRead,
    )
    from harness_local.services.project_registry import RegistryError

    def registry(operation, /, *args, **kwargs):
        def guarded():
            try:
                return operation(*args, **kwargs)
            except RegistryError as error:  # antes que ValueError en `call`: códigos propios del registro
                raise problem(error.status, error.code, str(error)) from error
        return call(guarded)

    def change(body: RegistryChangeInput) -> dict:
        data = body.model_dump()
        if body.policy is not None:
            data['policy'] = body.policy.model_dump(exclude_none=True)
        return data

    @router.get("/registry", response_model=RegistryRead, operation_id="managed_registry")
    def registry_options():
        runtime.ready()
        return runtime.registry.options()

    @router.get("/registry/projects/{project_id}", response_model=RegisteredProjectRead,
                operation_id="managed_registered_project")
    def registered_project(project_id: str):
        runtime.ready()
        return registry(runtime.registry.read, project_id)

    @router.post("/registry/preview", response_model=RegistryPreviewRead, operation_id="managed_registry_preview")
    def registry_preview(body: RegistryChangeInput):
        """Sin efectos: fila resultante, cambios, versiones congeladas y hash que liga la confirmación."""
        runtime.ready()
        return registry(runtime.registry.preview, change(body))

    @router.post("/registry/apply", response_model=RegistryApplyRead, operation_id="managed_registry_apply")
    def registry_apply(body: RegistryApplyCreate):
        """Repetir la misma confirmación devuelve el resultado ya aplicado, sin otra versión."""
        runtime.ready()
        return registry(runtime.registry.apply, change(body.change), preview_sha256=body.preview_sha256,
                        trust_root=body.trust_root, reason=body.reason)

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

    # --- estado de la creación conversacional (D088) ---------------------------------
    from harness_local.api.schemas import BootstrapStatusRead
    from harness_local.storage.bootstrap import BootstrapRepository

    def bootstrap_writer(item):
        if not item.bootstrap_enabled:
            raise problem(409, 'bootstrap_disabled', 'Este destino no autoriza crear el proyecto en el servidor.')
        return call(runtime.config.commit_factory, item.context, frozen_versions(item))

    @router.get('/projects/{project_id}/bootstrap', response_model=BootstrapStatusRead,
                operation_id='managed_bootstrap_status')
    def bootstrap_status(project_id: str):
        """Estado de la definición y su commit raíz; la creación v1 ya no se expone."""
        item = project(project_id)
        operation = call(BootstrapRepository(runtime.repository).get, item.context.root)
        target = (call(bootstrap_writer(item).inspect_definition, item.context)
                  if item.bootstrap_enabled and not operation else None)
        return {'enabled': item.bootstrap_enabled, 'import_required': bool(target and target['import_required']),
                'diagnostic': target.get('diagnostic') if target else None,
                'definition_operation': operation if item.context.documents is not None else None}

    # --- runs, jobs, intentos y eventos ---------------------------------------------

    @router.get("/projects/{project_id}/runs", response_model=Page[ManagedRunSummaryRead],
                operation_id="managed_runs")
    def runs(project_id: str, offset: Offset = 0, limit: Limit = 30,
             phase: Annotated[str | None, Query(min_length=1, max_length=120)] = None,
             task: Annotated[str | None, Query(min_length=1, max_length=120)] = None):
        page = runtime.views.runs(str(project(project_id).context.root), offset, limit, phase, task)
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

    @router.get("/runs/{run_id}/jobs", response_model=Page[ManagedJobRead], operation_id="managed_run_jobs")
    def run_jobs(run_id: str, offset: Offset = 0, limit: Limit = 30):
        """Del más reciente al más antiguo."""
        runtime.ready()
        return call(runtime.views.jobs, run_id, offset, limit)

    @router.get("/runs/{run_id}/cycles/{cycle}/diff", response_model=CycleDiffRead, operation_id="managed_cycle_diff")
    def cycle_diff(run_id: str, cycle: int, offset: Offset = 0, limit: DiffLimit = 64 * 1024,
                   sha256: Annotated[str | None, Query(pattern=r'^[0-9a-f]{64}$')] = None):
        """Diff revisado de un ciclo por páginas de bytes UTF-8 que acaban en fin de línea; `offset` es 0 o un
        `next_offset` anterior. Con `sha256`, un diff distinto del pedido responde 409."""
        runtime.ready()
        return call(runtime.views.cycle_diff, run_id, cycle, offset, limit, sha256)

    @router.get('/runs/{run_id}/cycles/{cycle}/validations/{entry}/reports/{report}',
                response_model=JUnitCasesRead, operation_id='managed_junit_cases')
    def junit_cases(run_id: str, cycle: int, entry: int, report: int, offset: Offset = 0, limit: Limit = 50):
        runtime.ready()
        return call(runtime.views.test_cases, run_id, cycle, entry, report, offset, limit)

    @router.get('/runs/{run_id}/cycles/{cycle}/validations/{entry}/reports/{report}/original',
                response_class=Response, operation_id='managed_junit_original',
                responses={200: {'content': {'application/octet-stream': {'schema': {'type': 'string', 'format': 'binary'}}}}})
    def junit_original(run_id: str, cycle: int, entry: int, report: int):
        runtime.ready()
        data, sha256 = call(runtime.views.test_original, run_id, cycle, entry, report)
        return Response(data, media_type='application/octet-stream', headers={
            'Content-Disposition': 'attachment; filename="junit.xml"', 'ETag': f'"{sha256}"',
            'X-Content-Type-Options': 'nosniff'})

    @router.get("/runs/{run_id}/attempts", response_model=Page[ManagedAttemptRead],
                operation_id="managed_run_attempts")
    def attempts(run_id: str, offset: Offset = 0, limit: Limit = 30):
        runtime.ready()
        return call(runtime.views.attempts, run_id, offset, limit)

    @router.get('/runs/{run_id}/attempts/{attempt_id}/logs', response_model=list[ManagedLogRead],
                operation_id='managed_attempt_logs')
    def attempt_logs(run_id: str, attempt_id: str):
        runtime.ready()
        from sqlalchemy import text
        from harness_local.storage.retention import inspect_logs
        with runtime.repository.engine.connect() as db:
            owner = db.scalar(text('SELECT run_id FROM managed_attempts WHERE id=:id'), {'id': attempt_id})
        if owner != run_id:
            raise problem(404, 'not_found', 'Intento desconocido para este run.')
        return call(inspect_logs, runtime.repository.engine.url.database, attempt_id)

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
            actions = [a for a in actions if a not in ("check", "close", "reconcile_task", "abandon")]
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

    @router.get("/projects/{project_id}/phases/{code}", response_model=PhaseRead, operation_id="managed_phase_by_code")
    def phase_by_code(project_id: str, code: str):
        """Lectura por el código de la URL (`P001`), único por checkout (D076)."""
        return phase_read(call(runtime.phases.by_code, str(project(project_id).context.root), code))

    @router.get("/projects/{project_id}/phases/{code}/tasks", response_model=Page[PhaseTaskRead],
                operation_id="managed_phase_tasks")
    def phase_tasks(project_id: str, code: str, offset: Offset = 0, limit: Limit = 30):
        """Sin fase definida (runs v1 o anteriores a la definición), solo las tareas con runs."""
        root = str(project(project_id).context.root)
        try:
            planned = list(runtime.phases.definition(runtime.phases.by_code(root, code))[1].get("tasks") or [])
        except LookupError:
            planned = []
        page = runtime.views.tasks(root, code, planned, offset, limit)
        return {**page, "items": [{**item, "latest": item["latest"] and {**item["latest"], "project_id": project_id}}
                                  for item in page["items"]]}

    @router.post("/projects/{project_id}/phases", response_model=PhaseRead, status_code=201,
                 operation_id="managed_create_phase")
    def create_phase(project_id: str, body: PhaseCreate):
        context = project(project_id).context
        data = body.model_dump()
        if data["documents"] is None:
            from harness_local.core.engine.documents import layout
            target = layout(context)
            data["documents"] = (list(target.phase_documents) if target is not None
                                 else [context.state_file, context.next_steps_file])
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
                       reason=body.reason, ttl_seconds=body.ttl_seconds, tag_kind=item.tag_kind,
                       git=document_writer(item))
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
    def abandon_phase(phase_id: str, body: PhaseAbandonCreate, idempotency_key: IdempotencyKey):
        item, _ = registered_phase(phase_id)
        job = call(runtime.phases.abandon, phase_id, body.expected_version, reason=body.reason, context=item.context,
                   git=document_writer(item), key=idempotency_key, versions=frozen_versions(item))
        queued(job)
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

    # --- D088: documentos del proyecto y plan de la fase activa ---------------------------------------
    from harness_local.api.schemas import (
        DocumentEditCreate, DocumentEditInput, DocumentEditPreviewRead, DocumentRead, DocumentsStatusRead,
        DocumentTreeRead,
    )
    from harness_local.storage.documents import DocumentsRepository
    from harness_local.api.documents import document_status, document_tree as project_document_tree

    def documents_project(project_id: str):
        item = project(project_id)
        if item.context.documents is None:
            raise problem(409, 'documents_layout', 'Este proyecto requiere importar su documentación al contrato unificado D088.')
        return item

    def document_writer(item):
        if runtime.config.commit_factory is None:
            raise problem(409, 'commit_writer_unavailable', 'Las operaciones documentales requieren un escritor Git.')
        return runtime.config.commit_factory(item.context, frozen_versions(item))

    @router.get('/projects/{project_id}/documents', response_model=DocumentsStatusRead,
                operation_id='managed_documents')
    def documents_status(project_id: str):
        """Documentos, deriva frente a la base adoptada, cambios locales, avisos, decisiones y archivo."""
        item = documents_project(project_id)
        git = runtime.config.commit_factory(item.context, frozen_versions(item)) if runtime.config.commit_factory else None
        return call(document_status, DocumentsRepository(runtime.repository), item.context, git)

    @router.get('/projects/{project_id}/documents/content', response_model=DocumentRead,
                operation_id='managed_document')
    def document_content(project_id: str, path: Annotated[str, Query(min_length=1, max_length=500)]):
        return call(DocumentsRepository(runtime.repository).read, documents_project(project_id).context, path)

    @router.get('/projects/{project_id}/documents/tree', response_model=DocumentTreeRead,
                operation_id='managed_document_tree')
    def document_tree(project_id: str):
        """Instrucciones y Markdown del contrato; sin enlaces simbólicos, ocultos ni contenido."""
        return call(project_document_tree, DocumentsRepository(runtime.repository), documents_project(project_id).context)

    @router.get('/projects/{project_id}/documents/image', response_class=Response,
                operation_id='managed_document_image',
                responses={200: {'content': {kind: {} for kind in sorted(set(IMAGE_TYPES.values()))},
                                 'description': 'Bytes de la imagen del checkout'}})
    def document_image(project_id: str, path: Annotated[str, Query(min_length=1, max_length=500)]):
        """Imagen del checkout para el visor (H6.2 E3). Sin scripts ni recursos externos aunque se abra sola."""
        data, kind = call(DocumentsRepository(runtime.repository).image, documents_project(project_id).context, path)
        return Response(data, media_type=kind, headers={
            'Content-Security-Policy': "default-src 'none'; style-src 'unsafe-inline'; sandbox",
            'X-Content-Type-Options': 'nosniff', 'Cache-Control': 'private, no-cache'})

    @router.post('/projects/{project_id}/documents/edit/preview', response_model=DocumentEditPreviewRead,
                 operation_id='managed_document_edit_preview')
    def document_edit_preview(project_id: str, body: DocumentEditInput):
        """Diff exacto sin efectos; los bloques gestionados y el archivo de fases no se editan."""
        item = documents_project(project_id)
        return call(DocumentsRepository(runtime.repository).preview, item.context, document_writer(item),
                    source=body.source, changes=_changes(body), regenerate_blocks=body.regenerate_blocks)

    @router.post('/projects/{project_id}/documents/edit', response_model=ManagedJobRead, status_code=202,
                 operation_id='managed_document_edit')
    def document_edit(project_id: str, body: DocumentEditCreate, idempotency_key: IdempotencyKey):
        item = documents_project(project_id)
        job = call(DocumentsRepository(runtime.repository).submit, item.context, key=idempotency_key,
                   versions=frozen_versions(item), preview_sha256=body.preview_sha256, reason=body.reason,
                   confirmed=body.confirmed, git=document_writer(item), source=body.source, changes=_changes(body),
                   resume_operation_id=body.resume_operation_id, regenerate_blocks=body.regenerate_blocks)
        return queued(job)

    def _changes(body):
        # Sin `base_sha256` no hay CAS; con null, el documento no debe existir.
        return None if body.changes is None else [change.model_dump(exclude_unset=True) for change in body.changes]

    def _plan(body):
        return None if body.plan_proposal is None else body.plan_proposal.model_dump()

    from harness_local.api.schemas import PhasePlanCreate, PhasePlanInput, PhasePlanPreviewRead
    from harness_local.storage.phase_plan import PhasePlanRepository

    @router.post('/phases/{phase_id}/plan/preview', response_model=PhasePlanPreviewRead,
                 operation_id='managed_phase_plan_preview')
    def phase_plan_preview(phase_id: str, body: PhasePlanInput):
        item, _ = registered_phase(phase_id)
        plans = PhasePlanRepository(runtime.repository, phase_id, body.next_steps, _plan(body))
        return call(plans.preview, item.context, document_writer(item))

    @router.post('/phases/{phase_id}/plan', response_model=ManagedJobRead, status_code=202,
                 operation_id='managed_phase_plan')
    def phase_plan(phase_id: str, body: PhasePlanCreate, idempotency_key: IdempotencyKey):
        item, _ = registered_phase(phase_id)
        plans = PhasePlanRepository(runtime.repository, phase_id, body.next_steps, _plan(body))
        return queued(call(plans.submit, item.context, key=idempotency_key, versions=frozen_versions(item),
                           preview_sha256=body.preview_sha256, reason=body.reason, confirmed=body.confirmed,
                           git=document_writer(item), source='content', changes=None,
                           resume_operation_id=body.resume_operation_id))

    # --- H6.4: métricas por intento y agregados (solo lectura) ----------------------------------------
    from harness_local.api.schemas import (
        AttemptMetricRead, MetricDimension, MetricGroupsRead, MetricOrder, MetricsSummaryRead, ModelMetricGroupsRead,
        TaskMetricsRead, ValidationDimension, ValidationGroupsRead,
    )
    from harness_local.storage.metrics import MetricsViews

    Scoped = Annotated[str | None, Query(min_length=1, max_length=200)]

    def metrics_scope(project_id, phase, task):
        """Sin proyecto: global, todos los proyectos de esta SQLite. Fase y tarea exigen proyecto."""
        runtime.ready()
        if project_id is None:
            if phase is not None or task is not None:
                raise problem(422, 'invalid_request', 'Fase y tarea requieren project_id.')
            return {'root': None, 'phase': None, 'task': None}
        return {'root': str(project(project_id).context.root), 'phase': phase, 'task': task}

    def metrics():
        return MetricsViews(runtime.repository.engine)

    @router.get('/metrics/summary', response_model=MetricsSummaryRead, operation_id='managed_metrics_summary')
    def metrics_summary(project_id: Scoped = None, phase: Scoped = None, task: Scoped = None):
        """Consumo, calidad de las tareas, tests OK/KO de su última validación y paradas por motivo."""
        return call(metrics().summary, metrics_scope(project_id, phase, task))

    @router.get('/metrics/attempts', response_model=Page[AttemptMetricRead], operation_id='managed_metrics_attempts')
    def metrics_attempts(project_id: Scoped = None, phase: Scoped = None, task: Scoped = None, run_id: Scoped = None,
                         offset: Offset = 0, limit: Limit = 30):
        """Filas materializadas por intento, con procedencia por campo; null es ausencia, no cero."""
        return call(metrics().attempts, metrics_scope(project_id, phase, task), offset, limit, run_id=run_id)

    @router.get('/metrics/groups', response_model=MetricGroupsRead, operation_id='managed_metrics_groups')
    def metrics_groups(dimension: MetricDimension, project_id: Scoped = None, phase: Scoped = None,
                       task: Scoped = None, role: Scoped = None, order: MetricOrder = 'attempts',
                       offset: Offset = 0, limit: Limit = 30):
        """Consumo agrupado; con `role` y `order` da los modelos y esfuerzos favoritos por frecuencia o tokens."""
        return call(metrics().groups, metrics_scope(project_id, phase, task), dimension, offset, limit,
                    role=role, order=order)

    @router.get('/metrics/models', response_model=ModelMetricGroupsRead, operation_id='managed_metrics_models')
    def metrics_models(project_id: Scoped = None, phase: Scoped = None, task: Scoped = None, role: Scoped = None,
                       order: MetricOrder = 'attempts', offset: Offset = 0, limit: Limit = 30):
        """Consumo por modelo reportado (Claude `modelUsage`); Codex no informa modelo."""
        return call(metrics().groups, metrics_scope(project_id, phase, task), 'reported_model', offset, limit,
                    role=role, order=order)

    @router.get('/metrics/tasks', response_model=Page[TaskMetricsRead], operation_id='managed_metrics_tasks')
    def metrics_tasks(project_id: Scoped = None, phase: Scoped = None, task: Scoped = None,
                      offset: Offset = 0, limit: Limit = 30):
        """Por tarea: agentes, intentos por rol, correcciones, aceptación a la primera, tiempos, tests y consumo."""
        return call(metrics().tasks, metrics_scope(project_id, phase, task), offset, limit)

    @router.get('/metrics/validations', response_model=ValidationGroupsRead, operation_id='managed_metrics_validations')
    def metrics_validations(dimension: ValidationDimension = 'phase', project_id: Scoped = None, phase: Scoped = None,
                            task: Scoped = None, offset: Offset = 0, limit: Limit = 30):
        """H6.2 E6: evolución de los tests. Cada ciclo de validación de las tareas, OK/KO, por clave descendente."""
        return call(metrics().validations, metrics_scope(project_id, phase, task), dimension, offset, limit)

    # --- H4.1: chat contextual -----------------------------------------------------------------

    from harness_local.api.schemas import (
        ChatConversationCreate, ChatConversationRead, ChatConversationSummaryRead, ChatMessageCreate,
        ChatProposalAcceptCreate, ChatProposalDismissCreate, ChatCommandCreate, ChatCommandRead,
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
    def create_conversation(project_id: str, body: ChatConversationCreate, idempotency_key: IdempotencyKey):
        """Conversación separada del flujo de ejecución; no encola nada. Misma clave y misma petición devuelven la
        misma conversación."""
        context = project(project_id).context
        return conversation_read(call(runtime.chat.create, context, title=body.title, phase_id=body.phase_id,
                                      task_run_id=body.task_run_id, key=idempotency_key))

    @router.get("/conversations/{conversation_id}", response_model=ChatConversationRead,
                operation_id="managed_conversation")
    def conversation(conversation_id: str):
        return conversation_read(conversation_id)

    @router.post("/conversations/{conversation_id}/messages", response_model=ManagedJobRead, status_code=202,
                 operation_id="managed_chat_message")
    def chat_message(conversation_id: str, body: ChatMessageCreate, idempotency_key: IdempotencyKey):
        """Turno nuevo de solo lectura: mensaje y contexto se congelan al encolar; sin sesión del proveedor."""
        item = registered_conversation(conversation_id)
        from harness_local.adapters.chat_snapshot import HeadSnapshot
        writer = call(runtime.config.commit_factory, item.context, frozen_versions(item)) if runtime.config.commit_factory else None
        reader = HeadSnapshot(item.context.root, executable=getattr(writer, 'executable', 'git'))
        job = call(runtime.chat.submit_message, item.context, conversation_id, body.expected_version,
                   key=idempotency_key, versions=frozen_versions(item), text=body.text, documents=body.documents,
                   run_ids=body.run_ids, reader=reader)
        return queued(job)

    @router.post("/conversations/{conversation_id}/commands/preview", response_model=ChatCommandRead,
                 operation_id="managed_chat_command_preview")
    def chat_command_preview(conversation_id: str, body: ChatCommandCreate):
        item = registered_conversation(conversation_id)
        return call(runtime.chat.command_preview, item.context, conversation_id, body.expected_version, body.text)

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

    # --- H6.5: creación y planificación conversacionales -----------------------------------------
    from harness_local.api.schemas import (
        DefinitionAcceptCreate, DefinitionPreviewRead, ImportStatusRead, ImportPreviewRead, ImportEntryRead, PlanningApplyCreate, PlanningBriefRead,
        PlanningConversationCreate, PlanningConversationRead, PlanningConversationSummaryRead, PlanningDeferCreate,
        PlanningDismissCreate, PlanningDraftContentRead, PlanningDraftEdit, PlanningDraftsRead, PlanningMessageCreate,
    )
    from harness_local.storage.planning import PlanningRepository

    def planning_repository():
        return PlanningRepository(runtime.repository)

    def planning_project(project_id: str):
        item = project(project_id)
        if item.context.documents is None:
            raise problem(409, 'documents_layout', 'Las conversaciones de definición y planificación requieren '
                                                  'el contrato documental unificado D088.')
        return item

    def conversation_of(item, conversation_id: str):
        root = call(planning_repository().root, conversation_id)
        if root != str(item.context.root):
            raise problem(404, 'not_found', 'La conversación pertenece a otro proyecto.')
        return conversation_id

    def definition_writer(item):
        """Lectura y escritura de borradores: solo destinos con bootstrap autorizado por el servidor."""
        return bootstrap_writer(item)

    def import_reader(item):
        """P008-T011: Git de solo lectura del escritor configurado para leer el árbol de HEAD del proyecto."""
        if runtime.config.commit_factory is None:
            raise problem(409, 'git_unconfigured', 'No hay lector Git configurado para importar el proyecto.')
        return call(runtime.config.commit_factory, item.context, frozen_versions(item))

    def conversation_port(item, kind):
        """Puerto de cada tipo: destino del bootstrap (definición) o lector Git (importación; sus borradores viven
        en el área privada junto a SQLite)."""
        port = {'definition': definition_writer, 'project_import': import_reader, 'onboarding': import_reader}
        return port.get(kind, lambda _: None)(item)

    def drafts_port(item, conversation_id):
        """Los borradores de una importación están en el área privada: no necesitan Git ni bootstrap."""
        kind = call(planning_repository().get, conversation_id)['kind']
        return definition_writer(item) if kind == 'definition' else None

    def planning_read(item, conversation_id):
        detail = call(planning_repository().get, conversation_id)
        operation = None
        if detail['kind'] == 'definition':
            operation = call(BootstrapRepository(runtime.repository).get, item.context.root)
        return {**detail, 'project_id': item.id, 'operation': operation}

    @router.get('/projects/{project_id}/planning', response_model=list[PlanningConversationSummaryRead],
                operation_id='managed_planning_conversations')
    def planning_list(project_id: str):
        return call(planning_repository().list, planning_project(project_id).context.root)

    @router.post('/projects/{project_id}/planning', response_model=PlanningConversationRead, status_code=201,
                 operation_id='managed_planning_create')
    def planning_create(project_id: str, body: PlanningConversationCreate, idempotency_key: IdempotencyKey):
        """Definición (brief Markdown, destino vacío o con borradores), planificación de la fase activa sin tareas o
        importación de un proyecto aún no gestionado (inventario y mapa de HEAD congelados). Misma clave y misma
        petición devuelven la misma conversación."""
        item = planning_project(project_id)
        writer = conversation_port(item, body.kind)
        conversation_id = call(planning_repository().create, item.context, kind=body.kind, title=body.title, brief=body.brief,
                               phase_id=body.phase_id, writer=writer, key=idempotency_key)
        return planning_read(item, conversation_id)

    @router.get('/projects/{project_id}/planning/{conversation_id}', response_model=PlanningConversationRead,
                operation_id='managed_planning_conversation')
    def planning_detail(project_id: str, conversation_id: str):
        item = planning_project(project_id)
        return planning_read(item, conversation_of(item, conversation_id))

    @router.get('/projects/{project_id}/planning/{conversation_id}/brief', response_model=PlanningBriefRead,
                operation_id='managed_planning_brief')
    def planning_brief(project_id: str, conversation_id: str):
        item = planning_project(project_id)
        return call(planning_repository().brief, conversation_of(item, conversation_id))

    @router.post('/projects/{project_id}/planning/{conversation_id}/messages', response_model=ManagedJobRead,
                 status_code=202, operation_id='managed_planning_message')
    def planning_message(project_id: str, conversation_id: str, body: PlanningMessageCreate,
                         idempotency_key: IdempotencyKey):
        """Turno nuevo de solo lectura del revisor con el contexto congelado al encolarlo."""
        item = planning_project(project_id)
        conversation_of(item, conversation_id)
        if runtime.config.ports_factory is None:
            raise problem(409, 'ports_unconfigured', 'No hay puertos de agente configurados para la conversación.')
        kind = call(planning_repository().get, conversation_id)['kind']
        job = call(planning_repository().submit_message, item.context, conversation_id, body.expected_version,
                   key=idempotency_key, versions=frozen_versions(item), text=body.text,
                   writer=conversation_port(item, kind))
        return queued(job)

    @router.get('/projects/{project_id}/planning/{conversation_id}/drafts', response_model=PlanningDraftsRead,
                operation_id='managed_planning_drafts')
    def planning_drafts(project_id: str, conversation_id: str):
        """Borradores en disco frente a lo que conoce el harness; archivos ajenos e inválidos."""
        item = planning_project(project_id)
        return call(planning_repository().drafts, item.context, conversation_of(item, conversation_id),
                    drafts_port(item, conversation_id))

    @router.get('/projects/{project_id}/planning/{conversation_id}/drafts/content', response_model=PlanningDraftContentRead,
                operation_id='managed_planning_draft')
    def planning_draft(project_id: str, conversation_id: str, path: Annotated[str, Query(min_length=1, max_length=500)]):
        """H6.2 E4: un borrador admitido con su hash en disco, base de la CAS del editor."""
        item = planning_project(project_id)
        return call(planning_repository().draft, item.context, conversation_of(item, conversation_id), path,
                    drafts_port(item, conversation_id))

    @router.put('/projects/{project_id}/planning/{conversation_id}/drafts', response_model=PlanningConversationRead,
                operation_id='managed_planning_draft_edit')
    def planning_draft_edit(project_id: str, conversation_id: str, body: PlanningDraftEdit):
        """Edición del usuario con CAS sobre el hash en disco; nunca sobrescribe otro cambio."""
        item = planning_project(project_id)
        call(planning_repository().edit_draft, item.context, conversation_of(item, conversation_id), body.expected_version,
             path=body.path, content=body.content, base_sha256=body.base_sha256,
             writer=drafts_port(item, conversation_id))
        return planning_read(item, conversation_id)

    @router.post('/projects/{project_id}/planning/{conversation_id}/proposals/{proposal_id}/apply',
                 response_model=PlanningConversationRead, operation_id='managed_planning_apply')
    def planning_apply(project_id: str, conversation_id: str, proposal_id: str, body: PlanningApplyCreate):
        """El harness escribe el borrador confirmado si sigue siendo el que leyó el turno (CAS)."""
        item = planning_project(project_id)
        call(planning_repository().apply, item.context, conversation_of(item, conversation_id), proposal_id,
             body.expected_version, proposal_sha256=body.proposal_sha256, confirmed=body.confirmed,
             writer=drafts_port(item, conversation_id))
        return planning_read(item, conversation_id)

    @router.post('/projects/{project_id}/planning/{conversation_id}/proposals/{proposal_id}/dismiss',
                 response_model=PlanningConversationRead, operation_id='managed_planning_dismiss')
    def planning_dismiss(project_id: str, conversation_id: str, proposal_id: str, body: PlanningDismissCreate):
        item = planning_project(project_id)
        call(planning_repository().dismiss, conversation_of(item, conversation_id), proposal_id, body.expected_version,
             reason=body.reason)
        return planning_read(item, conversation_id)

    @router.post('/projects/{project_id}/planning/{conversation_id}/questions/defer',
                 response_model=PlanningConversationRead, operation_id='managed_planning_defer')
    def planning_defer(project_id: str, conversation_id: str, body: PlanningDeferCreate):
        """Aplazamiento explícito de una pregunta bloqueante, con motivo; no la responde."""
        item = planning_project(project_id)
        call(planning_repository().defer, conversation_of(item, conversation_id), body.expected_version,
             question_id=body.question_id, reason=body.reason)
        return planning_read(item, conversation_id)

    from harness_local.storage.project_import import ImportRepository
    from harness_local.storage.onboarding_commit import OnboardingRepository
    from harness_local.api.schemas import OnboardingConfirmCreate

    @router.get('/projects/{project_id}/onboarding', response_model=ImportEntryRead,
                operation_id='managed_onboarding_entry')
    def onboarding_entry(project_id: str):
        item = planning_project(project_id)
        return {'activation_required': False, 'refusal': None, 'activation_preview': None,
                'operation': call(OnboardingRepository(runtime.repository).get, item.context.root)}

    @router.post('/projects/{project_id}/planning/{conversation_id}/onboarding/preview',
                 response_model=ImportPreviewRead, operation_id='managed_onboarding_preview')
    def onboarding_preview(project_id: str, conversation_id: str):
        item = planning_project(project_id)
        return call(OnboardingRepository(runtime.repository).preview, item.context,
                    conversation_of(item, conversation_id), frozen_versions(item), import_reader(item))

    @router.post('/projects/{project_id}/planning/{conversation_id}/onboarding/confirm',
                 response_model=ManagedJobRead, status_code=202, operation_id='managed_onboarding_confirm')
    def onboarding_confirm(project_id: str, conversation_id: str, body: OnboardingConfirmCreate,
                           idempotency_key: IdempotencyKey):
        item = planning_project(project_id)
        job = call(OnboardingRepository(runtime.repository).submit, item.context,
                   conversation_of(item, conversation_id), frozen_versions(item), import_reader(item),
                   key=idempotency_key, **body.model_dump())
        return queued(job)

    @router.get('/projects/{project_id}/import', response_model=ImportEntryRead,
                operation_id='managed_import_entry')
    def import_entry(project_id: str):
        item = planning_project(project_id)
        assessment = runtime.repository.guard.assess(item.context.root)
        required = bool(assessment.facts and assessment.facts.legacy_state and assessment.activation is None)
        return {'activation_required': required, 'refusal': assessment.refusal,
                'activation_preview': call(runtime.migration.preview, item.context.root) if required else None,
                'operation': call(ImportRepository(runtime.repository).get, item.context.root)}

    @router.post('/projects/{project_id}/planning/{conversation_id}/import/preview',
                 response_model=ImportPreviewRead, operation_id='managed_import_preview')
    def import_preview(project_id: str, conversation_id: str):
        item = planning_project(project_id)
        return call(ImportRepository(runtime.repository).preview, item.context,
                    conversation_of(item, conversation_id), frozen_versions(item), import_reader(item))

    @router.post('/projects/{project_id}/planning/{conversation_id}/import/confirm', response_model=ManagedJobRead,
                 status_code=202, operation_id='managed_import_confirm')
    def import_confirm(project_id: str, conversation_id: str, body: DefinitionAcceptCreate,
                       idempotency_key: IdempotencyKey):
        item = planning_project(project_id)
        job = call(ImportRepository(runtime.repository).submit, item.context,
                   conversation_of(item, conversation_id), frozen_versions(item), import_reader(item),
                   key=idempotency_key, **body.model_dump())
        return queued(job)

    @router.get('/projects/{project_id}/planning/{conversation_id}/import', response_model=ImportStatusRead,
                operation_id='managed_import_status')
    def import_status(project_id: str, conversation_id: str):
        """P008-T011: bloqueos para pasar a la vista previa de la importación (preguntas bloqueantes sin responder ni
        aplazar, checkout distinto del inventariado, borradores inválidos, documentos o límites de D088)."""
        item = planning_project(project_id)
        return call(planning_repository().import_status, item.context, conversation_of(item, conversation_id),
                    import_reader(item))

    @router.post('/projects/{project_id}/planning/{conversation_id}/accept/preview',
                 response_model=DefinitionPreviewRead, operation_id='managed_definition_accept_preview')
    def definition_accept_preview(project_id: str, conversation_id: str):
        """Archivos íntegros del commit raíz, archivo phase-000, bloques, P001, perfil y comandos; o bloqueos."""
        item = planning_project(project_id)
        return call(BootstrapRepository(runtime.repository).preview, item.context,
                    {'conversation_id': conversation_of(item, conversation_id)}, frozen_versions(item),
                    definition_writer(item))

    @router.post('/projects/{project_id}/planning/{conversation_id}/accept', response_model=ManagedJobRead,
                 status_code=202, operation_id='managed_definition_accept')
    def definition_accept(project_id: str, conversation_id: str, body: DefinitionAcceptCreate,
                          idempotency_key: IdempotencyKey):
        """Confirma la vista previa exacta: bootstrap D037 con la plantilla v2 y P001 ACTIVE adoptada."""
        item = planning_project(project_id)
        job = call(BootstrapRepository(runtime.repository).submit, item.context,
                   {'conversation_id': conversation_of(item, conversation_id)}, frozen_versions(item),
                   definition_writer(item), key=idempotency_key, **body.model_dump())
        return queued(job)

    return router

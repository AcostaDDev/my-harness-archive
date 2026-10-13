"""API gestionada local: delega en la autoridad H2.2–H2.5 sin lógica nueva de motor.

Toda ruta exige Host de loopback; toda mutación exige además Origin de loopback
(si el navegador lo envía) y la cabecera `X-Harness-Local: 1`, que una página
ajena no puede añadir sin preflight CORS (el servicio no habilita CORS). Las
mutaciones que crean jobs exigen `Idempotency-Key`; las que cambian un recurso
existente, `expected_version`. Conflictos y rechazos de modo devuelven 409 con
diagnóstico; la biblioteca garantiza que no quedan efectos parciales.
"""

from typing import Annotated
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request

from harness_local.api.schemas import (
    PromptScope, PromptDetailRead, PromptVersionRead, PromptDraftCreate, PromptActivateCreate,
    PromptValidateCreate, PromptValidationRead, PromptDiffRead,
    ActivationCreate, ActivationRead, ActivationTransition, ConfirmStoppedCreate, ManagedAttemptRead,
    ManagedEventsRead, ManagedJobRead, ManagedProjectRead, ManagedRunRead, ManagedRunSummaryRead,
    MigrationPreviewRead, ModeRead, Page, ProblemResponse, RunActionCreate, RunCreate, SupervisorRead,
)
from harness_local.core.migration import MigrationError
from harness_local.services.managed_runtime import ManagedRuntime
from harness_local.storage.managed import Conflict, OwnershipLost
from harness_local.storage.migration import ModeConflict

LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})

Offset = Annotated[int, Query(ge=0, le=2**53 - 1)]
Limit = Annotated[int, Query(ge=1, le=100)]
IdempotencyKey = Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=200,
                                       description="Misma clave y misma acción devuelven el mismo job.")]
ERRORS = {status: {"model": ProblemResponse} for status in (403, 404, 409, 422)}


def problem(status: int, code: str, diagnostic: str) -> HTTPException:
    return HTTPException(status, {"code": code, "diagnostic": diagnostic})


def _hostname(value: str | None) -> str | None:
    try:
        return urlsplit(f"//{value}").hostname if value else None
    except ValueError:
        return None


def local_request(request: Request, x_harness_local: Annotated[str | None, Header(
        description="Obligatoria con valor 1 en mutaciones (protección CSRF).")] = None) -> None:
    """Rechaza DNS rebinding (Host), peticiones cruzadas (Origin) y formularios ajenos (cabecera propia)."""
    if _hostname(request.headers.get("host")) not in LOOPBACK_HOSTS:
        raise problem(403, "host_rejected", "El servicio gestionado solo atiende nombres de loopback.")
    if request.method in SAFE_METHODS:
        return
    origin = request.headers.get("origin")
    if origin is not None:
        parsed = urlsplit(origin)
        if parsed.scheme not in {"http", "https"} or _hostname(parsed.netloc) not in LOOPBACK_HOSTS:
            raise problem(403, "origin_rejected", "Origen no local para una mutación gestionada.")
    if x_harness_local != "1":
        raise problem(403, "csrf_header_required", "Las mutaciones exigen la cabecera X-Harness-Local: 1.")


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
                "versions": dict(project.versions)}

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

    @router.post("/projects/{project_id}/runs", response_model=ManagedJobRead, status_code=202,
                 operation_id="managed_submit_run")
    def submit_run(project_id: str, body: RunCreate, idempotency_key: IdempotencyKey):
        item = project(project_id)
        from harness_local.core.engine.contracts import freeze
        versions = dict(item.versions)
        if item.permission_authority is not None:
            versions['permission_authority'] = freeze(item.permission_authority)
        job = call(runtime.repository.submit, item.context, body.task_id, body.phase_id, body.text,
                   versions, key=idempotency_key)
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

    return router

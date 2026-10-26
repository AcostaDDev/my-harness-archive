"""Authenticated initial configuration editor; never a provider-inference endpoint."""
from datetime import datetime
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, ConfigDict, Field

from harness_local.api.security import local_request, problem
from harness_local.api.schemas import ProblemResponse
from harness_local.i18n import tr
from harness_local.storage.configuration import ConfigurationConflict

Key = Annotated[str, Header(alias='Idempotency-Key', min_length=1, max_length=200)]
Hash = Annotated[str, Field(pattern=r'^[a-f0-9]{64}$')]


class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class ConfigurationCandidate(Input):
    text: str | None = Field(default=None, max_length=65536)
    form: dict[str, Any] | None = None
    validated: bool = True


class ConfigurationChange(ConfigurationCandidate):
    expected_version: int = Field(ge=0)
    base_sha256: Hash | None
    active_sha256: Hash | None
    import_external: bool = False
    reason: str = Field(min_length=1, max_length=1000)


class ConfigurationSave(ConfigurationChange):
    preview_sha256: Hash


class ConfigurationReference(Input):
    scope: Literal['global'] = 'global'
    revision: int = Field(ge=1)
    sha256: Hash
    expected_version: int = Field(ge=0)


class ConfigurationActivation(Input):
    references: list[ConfigurationReference] = Field(min_length=1, max_length=1)
    reason: str = Field(min_length=1, max_length=1000)


class ConfigurationActivate(ConfigurationActivation):
    preview_sha256: Hash


class ConfigurationCancel(Input):
    activation_id: str = Field(min_length=1, max_length=100)
    expected_version: int = Field(ge=0)
    reason: str = Field(min_length=1, max_length=1000)


class ConfigurationRecovery(Input):
    preview_sha256: Hash
    writers_stopped: bool = False


class ConfigurationRecoveryRead(BaseModel):
    operation_id: str
    updated_at: datetime
    observed: list[dict[str, str | None]]
    sha256: str


class ConfigurationDetection(Input):
    path: str = Field(min_length=1, max_length=8192)


class ConfigurationRevisionRead(BaseModel):
    scope: str
    revision: int
    sha256: str
    status: Literal['DRAFT', 'VALIDATED']


class ConfigurationRead(BaseModel):
    mode: Literal['UNCONFIGURED', 'INVALID', 'READY', 'RESTART_REQUIRED', 'RECOVERY_REQUIRED', 'READ_ONLY_ARCHIVE']
    status: str
    version: int
    legacy: bool
    saved: ConfigurationRevisionRead | None
    active: ConfigurationRevisionRead | None
    pending: ConfigurationRevisionRead | None
    working_sha256: str | None = None
    actual_sha256: str | None = None
    blockers: list[str]
    pending_activation_id: str | None
    recovery_operations: list[str]
    text: str | None = None


class ConfigurationPreviewRead(BaseModel):
    format: str
    kind: str
    sha256: str
    reason: str
    impact: list[str]
    changes: list[dict[str, Any]] | None = None
    references: list[dict[str, Any]] | None = None
    restart_required: bool | None = None
    roots: list[str] | None = None
    evidence: dict[str, Any] | None = None
    directory: str | None = None
    state_dir: str | None = None


class ConfigurationOperationRead(BaseModel):
    id: str
    format: str
    kind: str
    status: str
    result: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime


class ConfigurationDetectionRead(BaseModel):
    candidates: dict[str, str | None]
    user: str
    state_dir: str
    configuration_dir: str
    providers: dict[str, list[str]]


class ConfigurationClientsRead(BaseModel):
    reports: dict[str, dict[str, Any]]
    inference_performed: Literal[False] = False
    internal_effects_verified: Literal[False] = False


def configuration_router(runtime):
    router = APIRouter(prefix='/api/managed/configuration', dependencies=[Depends(local_request)],
                       responses={status: {'model': ProblemResponse} for status in (403, 404, 409, 422)})

    def call(operation):
        try:
            if runtime.setup is None:
                raise ConfigurationConflict('configuration_setup_unavailable')
            return operation(runtime.setup)
        except ConfigurationConflict as error:
            raise problem(409, error.code, tr('setup.conflict')) from None
        except LookupError:
            raise problem(404, 'configuration_not_found', tr('setup.not_found')) from None
        except (ValueError, OSError):
            raise problem(422, 'configuration_invalid', tr('setup.invalid')) from None

    def change(setup, body):
        values = body.model_dump(exclude={'reason', 'preview_sha256', 'text', 'form'})
        text = setup.candidate(text=body.text, form=body.form, validated=body.validated)
        return [{'scope': 'global', 'text': text, **values}]

    @router.get('', response_model=ConfigurationRead, operation_id='configuration_read')
    def read():
        def view(setup):
            state = setup.state()
            # Complete content is confined to this authenticated editor, never general listings.
            if state['mode'] not in ('READ_ONLY_ARCHIVE', 'INVALID') and state['saved']:
                state['text'] = setup.repository.document('global', state['saved']['revision'])
            return state
        return call(view)

    @router.post('/detect', response_model=ConfigurationDetectionRead, operation_id='configuration_detect')
    def detect(body: ConfigurationDetection):
        return call(lambda setup: setup.detect(body.path))

    @router.post('/check-clients', response_model=ConfigurationClientsRead, operation_id='configuration_check_clients')
    def check_clients(body: ConfigurationCandidate):
        return {'reports': call(lambda setup: setup.check_clients(**body.model_dump()))}

    @router.post('/preview', response_model=ConfigurationPreviewRead, operation_id='configuration_preview')
    def preview(body: ConfigurationChange):
        return call(lambda setup: setup.repository.preview(change(setup, body), reason=body.reason))

    @router.post('/save', response_model=ConfigurationOperationRead, operation_id='configuration_save')
    def save(body: ConfigurationSave, idempotency_key: Key):
        return call(lambda setup: setup.repository.save(change(setup, body), reason=body.reason,
                    preview_sha256=body.preview_sha256, key=idempotency_key))

    @router.post('/activation/preview', response_model=ConfigurationPreviewRead, operation_id='configuration_activation_preview')
    def activation_preview(body: ConfigurationActivation):
        def apply(setup):
            setup.editable()
            return setup.repository.activation_preview([ref.model_dump() for ref in body.references], reason=body.reason)
        return call(apply)

    @router.post('/activate', response_model=ConfigurationOperationRead, operation_id='configuration_activate')
    def activate(body: ConfigurationActivate, idempotency_key: Key):
        def apply(setup):
            setup.editable()
            return setup.repository.activate([ref.model_dump() for ref in body.references], reason=body.reason,
                                              preview_sha256=body.preview_sha256, key=idempotency_key)
        return call(apply)

    @router.post('/cancel', response_model=ConfigurationOperationRead, operation_id='configuration_cancel')
    def cancel(body: ConfigurationCancel, idempotency_key: Key):
        def apply(setup):
            setup.editable()
            return setup.repository.cancel_pending(activation_id=body.activation_id,
                expected_versions={'global': body.expected_version}, reason=body.reason, key=idempotency_key)
        return call(apply)

    @router.get('/operations/{operation_id}', response_model=ConfigurationOperationRead, operation_id='configuration_operation')
    def operation(operation_id: str):
        return call(lambda setup: setup.repository.operation(operation_id))

    @router.post('/operations/{operation_id}/recovery/preview', response_model=ConfigurationRecoveryRead,
                 operation_id='configuration_recovery_preview')
    def recovery_preview(operation_id: str):
        return call(lambda setup: setup.repository.recovery_preview(operation_id))

    @router.post('/operations/{operation_id}/recovery/confirm', response_model=ConfigurationOperationRead,
                 operation_id='configuration_recovery_confirm')
    def recovery_confirm(operation_id: str, body: ConfigurationRecovery):
        return call(lambda setup: setup.repository.recover(operation_id, **body.model_dump()))

    return router

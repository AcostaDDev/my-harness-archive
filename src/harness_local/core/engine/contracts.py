"""Valores congelados y puertos; no hay estado operativo persistido."""

from dataclasses import asdict, dataclass, replace
import json
import re
import shlex
from typing import Protocol, TYPE_CHECKING
from uuid import uuid4

from harness_local.core.engine.context import ProjectContext, policy_payload, relative_path

if TYPE_CHECKING:
    from harness_local.core.engine.journal import EngineJournal
    from harness_local.core.engine.acceptance import AcceptanceDecision
    from harness_local.core.engine.review import ReviewCycle


def freeze(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


MODEL_FORM = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:@\[\]-]{0,127}")


class ContractError(ValueError):
    pass


class IncompleteContract(ContractError):
    """Único motivo que permite pasar de planificación documental a agente."""


@dataclass(frozen=True)
class Selection:
    model: str
    effort: str
    reason: str


def executor_selection(context: ProjectContext, data: object) -> Selection:
    if not isinstance(data, dict) or set(data) != {"model", "effort", "reason"}:
        raise ContractError("Executor selection requires model, effort and reason")
    policy = context.policy
    if policy.executor_mode == "open":
        # Modo libre (D052): solo forma del modelo y vocabulario del proveedor ejecutor.
        allowed = (isinstance(data["model"], str) and MODEL_FORM.fullmatch(data["model"]) is not None
                   and data["effort"] in policy.executor_effort_vocabulary)
    else:
        allowed = data["model"] in policy.executor_models and data["effort"] in policy.executor_efforts
    if not allowed or not isinstance(data["reason"], str) or not data["reason"].strip():
        raise ContractError("Executor selection outside explicit policy")
    return Selection(**data)


def command_text(item: object) -> object:
    """D056: an argv array becomes the equivalent shell-free string; validation splits it back unchanged."""
    if isinstance(item, list) and item and all(isinstance(arg, str) and arg for arg in item):
        return shlex.join(item)
    return item


def task_contract(context: ProjectContext, data: object, task_id: str, phase_id: str) -> str:
    if not isinstance(data, dict) or data.get("task_id") != task_id or data.get("phase_id") != phase_id:
        raise ContractError("Task/phase identity mismatch")
    if isinstance(data.get("validation_commands"), list):
        # The frozen contract keeps strings; the agent's original output stays in its attempt.
        data = {**data, "validation_commands": [command_text(item) for item in data["validation_commands"]]}
    for field in ("title", "objective", "executor_prompt"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ContractError(f"Missing task {field}")
    for field in ("allowed_paths", "forbidden_paths", "acceptance_criteria", "validation_commands"):
        items = data.get(field)
        if not isinstance(items, list) or not all(isinstance(item, str) and item.strip() for item in items):
            raise ContractError(f"Invalid task {field}")
    if not data["acceptance_criteria"]:
        raise ContractError("Task requires acceptance criteria")
    for path in data["allowed_paths"] + data["forbidden_paths"]:
        try:
            relative_path(path)
        except ValueError as exc:
            raise ContractError("Task file scope must stay inside checkout") from exc
    executor_selection(context, data.get("executor_selection"))
    return freeze(data)


@dataclass(frozen=True)
class AgentRequest:
    id: str
    role: str
    selection: Selection
    prompt: str
    task_json: str | None
    context_json: str
    # No conversation/session handle: cada petición exige una sesión nueva.
    fresh_session: bool = True
    prompt_snapshot_json: str | None = None
    permission_snapshot_json: str | None = None


@dataclass(frozen=True)
class AgentResult:
    payload_json: str | None
    terminal_observed: bool = False
    exit_code: int | None = None
    raw_output: str = ""
    error: str | None = None
    status: str | None = None  # None preserves historical/fake adapter semantics.
    metadata_json: str | None = None


class AgentAdapter(Protocol):
    def invoke(self, context: ProjectContext, request: AgentRequest) -> AgentResult: ...


@dataclass(frozen=True)
class Attempt:
    request: AgentRequest
    result: AgentResult


@dataclass(frozen=True)
class OperationalStop:
    stage: str
    reason: str
    # No review verdict: una parada operativa no es juicio de agente.


@dataclass(frozen=True)
class RunHistory:
    id: str
    context_json: str
    task_json: str | None = None
    attempts: tuple[Attempt, ...] = ()
    cycles: tuple["ReviewCycle", ...] = ()
    preparation_json: tuple[str, ...] = ()
    status: str = "planned"
    stop: OperationalStop | None = None
    stops: tuple[OperationalStop, ...] = ()
    acceptance: "AcceptanceDecision | None" = None
    prompt_catalog_json: str | None = None

    @property
    def revisions(self) -> int:
        return max(0, sum(item.request.role == "executor" for item in self.attempts) - 1)


def context_snapshot(context: ProjectContext) -> str:
    profile = asdict(context.profile)
    if not profile['junit_reports']:
        profile.pop('junit_reports')  # Preserva snapshots anteriores sin reportes.
    return freeze({"root": str(context.root), "profile": profile,
                   "policy": policy_payload(context.policy), "next_steps_file": context.next_steps_file,
                   "state_file": context.state_file})


def stop_history(history: RunHistory, stage: str, reason: str) -> RunHistory:
    stop = OperationalStop(stage, reason)
    return replace(history, status="stopped", stop=stop, stops=history.stops + (stop,))


def invoke_agent(context: ProjectContext, history: RunHistory, adapter: AgentAdapter,
                 role: str, selection: Selection, prompt: str,
                 journal: "EngineJournal | None" = None, *, prompt_snapshot_json: str | None = None) -> tuple[RunHistory, dict | None]:
    request = AgentRequest(str(uuid4()), role, selection, prompt, history.task_json, history.context_json,
                           prompt_snapshot_json=prompt_snapshot_json)
    if journal:
        request = journal.agent_started(history, request) or request
    try:
        from harness_local.core.engine.permissions import snapshot_payload
        if snapshot_payload(request).get('denials'):
            raise ContractError('An explicit permission denial blocks this executor attempt; replace the request or wait for expiry')
        result = adapter.invoke(context, request)
    except Exception as exc:
        from harness_local.core.engine.journal import JournalError
        if isinstance(exc, JournalError):
            raise
        result = AgentResult(None, False, None, error=f"{type(exc).__name__}: {exc}")
    history = replace(history, attempts=history.attempts + (Attempt(request, result),))
    if journal:
        journal.checkpoint(history, role)
    try:
        if (result.error or result.terminal_observed is not True
                or type(result.exit_code) is not int or result.exit_code != 0):
            raise ContractError(result.error or "Agent stream failed or lacks terminal/zero exit")
        data = json.loads(result.payload_json or "")
        if not isinstance(data, dict) or data.get("is_error"):
            raise ContractError("Agent result is invalid or reports an error")
        freeze(data)  # JSON no finito tampoco es un resultado estructurado válido.
    except (ValueError, TypeError) as exc:
        return stop_history(history, role, str(exc)), None
    return history, data

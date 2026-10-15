"""Motor con puertos explícitos y journal opcional; no publica ejecución real."""

from dataclasses import asdict, replace
import json
from uuid import uuid4

from harness_local.core.engine.acceptance import assess_acceptance, documentation_parity
from harness_local.core.engine.context import ProjectContext
from harness_local.core.engine.contracts import (
    AgentAdapter, ContractError, IncompleteContract, RunHistory,
    Selection, context_snapshot, executor_selection, freeze, invoke_agent, task_contract,
    stop_history as stopped,
)
from harness_local.core.engine.evidence import (
    ContentEvidence, EvidenceCapture, check_paths, strip_empty_provenance,
)
from harness_local.core.engine.journal import EngineJournal, JournalError
from harness_local.core.engine.prompts import builtin_catalog, dump_catalog, load_catalog, render_attempt
from harness_local.core.engine.planning import SHARED_HEADING, deterministic_task, section
from harness_local.core.engine.review import ReviewCycle, decision_proposals, review_contract, stalled_review_signature
from harness_local.core.engine.validation import CommandRunner, command_result_payload, run_command, run_validations, validation_payload


def _executor_output(payload: dict) -> str | None:
    """Motivo de parada si la salida del ejecutor trae denegaciones o propuestas de ADR mal formadas."""
    if not isinstance(payload.get("permission_denials", []), list):
        return "Malformed permission denials"
    try:
        decision_proposals(payload.get("decision_proposals", []))
    except ContractError as exc:
        return f"Malformed decision proposals: {exc}"
    return None


def _latest_executor_proposals(history: RunHistory) -> list:
    """Propuestas de ADR válidas de la última salida del ejecutor (P008-T003). Una salida que se detuvo por
    propuestas mal formadas no las aporta al revalidar."""
    for attempt in reversed(history.attempts):
        if attempt.request.role == "executor":
            try:
                payload = json.loads(attempt.result.payload_json or "")
                return decision_proposals(payload.get("decision_proposals", []))
            except (ValueError, AttributeError):  # ContractError es un ValueError
                return []
    return []


class OfflineEngine:
    """Puertos inyectados; ninguna CLI se activa desde el núcleo."""

    def __init__(self, agents: AgentAdapter, commands: CommandRunner, evidence: EvidenceCapture,
                 journal: EngineJournal | None = None, prompts=None):
        self.agents = agents
        self.commands = commands
        self.evidence = evidence
        self.journal = journal
        self.prompts = prompts or (lambda context: builtin_catalog())
        self.resuming = False

    def _checkpoint(self, history: RunHistory, stage: str) -> None:
        if self.journal:
            self.journal.checkpoint(history, stage)

    def _catalog(self, context, history):
        if self.resuming and history.prompt_catalog_json is not None:
            return load_catalog(history.prompt_catalog_json)
        return self.prompts(context)

    def _invoke(self, context, history, role, selection, name, values):
        try:
            catalog = self._catalog(context, history)
            history = replace(history, prompt_catalog_json=dump_catalog(catalog))
            prompt, snapshot = render_attempt(catalog, name, values, context)
        except (ValueError, KeyError, TypeError) as exc:
            return stopped(history, "prompts", str(exc)), None
        return invoke_agent(context, history, self.agents, role, selection, prompt, self.journal,
                            prompt_snapshot_json=snapshot)

    def _prepare(self, context: ProjectContext, history: RunHistory) -> RunHistory:
        try:
            history = replace(history, prompt_catalog_json=dump_catalog(self._catalog(context, history)))
        except (ValueError, KeyError, TypeError) as exc:
            return stopped(history, "prompts", str(exc))
        self._checkpoint(history, "preparation")
        for command in context.profile.preparation:
            result = run_command(context, self.commands, command, self.journal)
            entry = freeze({"command": asdict(command), "result": command_result_payload(result)})
            history = replace(history, preparation_json=history.preparation_json + (entry,))
            self._checkpoint(history, "preparation")
            if not result.passed:
                return stopped(history, "preparation", result.error or "Environment preparation failed")
        return history

    def start(self, context: ProjectContext, task_id: str, phase_id: str, text: str,
              *, history: RunHistory | None = None, contract: str | None = None) -> RunHistory:
        """`contract`: contrato determinista ya congelado por el servidor (H3.4); no se llama al planificador."""
        self.resuming = False
        history = history or RunHistory(str(uuid4()), context_snapshot(context))
        if (history.context_json != context_snapshot(context) or history.task_json is not None
                or history.attempts or history.cycles or history.stops or history.preparation_json
                or history.status != "planned"):
            raise ContractError("Start requires a fresh history with the frozen context")
        if context.documents is not None:
            # D072: unos cambios locales previos se mezclarían con el diff del ejecutor.
            try:
                current = self.evidence.capture(context)
            except Exception as exc:
                return stopped(history, "evidence", str(exc))
            if current.changed_paths:
                return stopped(history, "start", "Uncommitted changes in the checkout ("
                               + ", ".join(current.changed_paths[:20]) + "); confirm them as a document edit "
                               "or remove them before starting a task")
        history = self._prepare(context, history)
        if history.stop:
            return history
        self._checkpoint(history, "planner")
        try:
            if contract is not None:
                if task_contract(context, json.loads(contract), task_id, phase_id) != contract:
                    raise ContractError("Server contract must be frozen canonical JSON")
                history = replace(history, task_json=contract)
            elif context.policy.planning_mode != "agent":
                try:
                    contract = deterministic_task(context, task_id, phase_id, text)
                except IncompleteContract:
                    if context.policy.planning_mode == "deterministic":
                        raise
                else:
                    history = replace(history, task_json=contract)
            if history.task_json is None:
                prompt = freeze({
                    "task_id": task_id, "phase_id": phase_id,
                    "task_section": section(text, rf"^##\s+{task_id}\s+[—-].*$"),
                    "shared_constraints": section(text, SHARED_HEADING),
                })
                selection = Selection(context.policy.planner_model, context.policy.planner_effort, "Explicit planner policy")
                history, data = self._invoke(context, history, "planner", selection, "plan-task", {"INPUT_JSON": prompt})
                if data is None:
                    return history
                history = replace(history, task_json=task_contract(context, data, task_id, phase_id))
        except ContractError as exc:
            return stopped(history, "planner", str(exc))
        task = json.loads(history.task_json)
        return self._execute(context, history, executor_selection(context, task["executor_selection"]),
                             task["executor_prompt"])

    def resume(self, context: ProjectContext, history: RunHistory, *, retry_executor: bool = False) -> RunHistory:
        """Revalidar conserva trabajo; reintento explícito consume el presupuesto previo."""
        self.resuming = True
        if context_snapshot(context) != history.context_json:
            raise ContractError("Resume requires the original frozen context/policy")
        if history.status not in {"stopped", "blocked", "revision_limit"} or history.task_json is None:
            raise ContractError("Only a stopped task with a contract can be resumed")
        task = json.loads(history.task_json)
        try:
            current = self.evidence.capture(context)
        except Exception as exc:
            return stopped(history, "evidence", str(exc))
        if check_paths(context, task, current).hard_failure:
            return stopped(history, "resume", "Out-of-scope changes must be resolved without discarding edits")
        if retry_executor and not task["allowed_paths"]:
            raise ContractError("Read-only tasks cannot retry implementation")
        has_execution = any(item.request.role == "executor" for item in history.attempts)
        if retry_executor and has_execution and history.revisions >= context.policy.max_revision_cycles:
            return replace(history, status="revision_limit", stop=None)
        history = replace(history, status="planned", stop=None, acceptance=None)
        history = self._prepare(context, history)
        if history.stop:
            return history
        if retry_executor:
            selection = executor_selection(context, task["executor_selection"])
            # Conservar la última selección explícita de corrección si la hubo.
            executions = [item for item in history.attempts if item.request.role == "executor"]
            if executions:
                selection = executions[-1].request.selection
            prompt = task["executor_prompt"] + "\nExplicit retry: preserve existing implementation and resolve outstanding findings."
            latest_review = history.cycles[-1].review_json if history.cycles else None
            prompt += "\nHistorical review (does not change scope):\n" + (latest_review or "No review recorded")
            return self._execute(context, history, selection, prompt)
        return self._review_loop(context, history, None, [], allow_revision=False)

    def _execute(self, context: ProjectContext, history: RunHistory, selection: Selection, prompt: str) -> RunHistory:
        self._checkpoint(history, "executor")
        try:
            before = self.evidence.capture(context)
        except Exception as exc:
            return stopped(history, "evidence", str(exc))
        # No path/tool/network grant is inferred from prompt text.
        history, payload = self._invoke(context, history, "executor", selection, "execute-task", {
            "INSTRUCTIONS": prompt, "TASK_JSON": history.task_json,
            "PROFILE_INSTRUCTIONS": context.profile.executor_instructions})
        if payload is None:
            return history
        malformed = _executor_output(payload)
        if malformed:
            return stopped(history, "executor", malformed)
        return self._review_loop(context, history, before, payload.get("permission_denials", []))

    def _review_loop(self, context: ProjectContext, history: RunHistory,
                     before: ContentEvidence | None, denials: list, *, allow_revision: bool = True) -> RunHistory:
        task = json.loads(history.task_json)
        while True:
            self._checkpoint(history, "validation")
            try:
                evidence = self.evidence.capture(context)
                policy = check_paths(context, task, evidence)
                source = next((a.request.id for a in reversed(history.attempts) if a.request.role == 'executor'), None)
                validation = run_validations(context, task, evidence, self.commands, self.journal,
                                             run_id=history.id, source_attempt_id=source)
                cycle = ReviewCycle(len(history.cycles), evidence, policy, validation, None, before, freeze(denials))
                history = replace(history, cycles=history.cycles + (cycle,))
                if self.evidence.capture(context) != evidence:
                    return stopped(history, "validation", "Content changed during validation; revalidate")
            except JournalError:
                raise
            except Exception as exc:
                return stopped(history, "evidence", str(exc))
            self._checkpoint(history, "reviewer")
            review_input = {
                "task": task, "evidence": strip_empty_provenance(asdict(evidence)), "policy": asdict(policy),
                "validation": strip_empty_provenance(validation_payload(validation)),
            }
            # P008-T003: claves solo con el layout v2 o con propuestas, para conservar la entrada anterior.
            parity = documentation_parity(context, evidence.changed_paths)
            if parity is not None:
                review_input["documentation"] = parity
            proposals = _latest_executor_proposals(history)
            if proposals:
                review_input["executor_decision_proposals"] = proposals
            prompt = freeze(review_input)
            selection = Selection(context.policy.reviewer_model, context.policy.reviewer_effort, "Explicit independent review policy")
            history, data = self._invoke(context, history, "reviewer", selection, "review-task", {"INPUT_JSON": prompt})
            if data is None:
                return history
            # Incluso una review inválida queda conservada para diagnóstico.
            cycle = replace(cycle, review_json=freeze(data))
            history = replace(history, cycles=history.cycles[:-1] + (cycle,))
            self._checkpoint(history, "reviewer")
            try:
                review_contract(context, task, data)
            except ContractError as exc:
                return stopped(history, "reviewer", str(exc))
            verdict = data["verdict"]
            if verdict == "ACCEPT":
                try:
                    decision = assess_acceptance(cycle, self.evidence.capture(context), context)
                except Exception as exc:
                    return stopped(history, "evidence", str(exc))
                history = replace(history, acceptance=decision)
                if not decision.eligible:
                    return stopped(history, "acceptance", "; ".join(decision.reasons))
                return replace(history, status="acceptance_ready", stop=None)
            if verdict == "BLOCKED":
                return replace(history, status="blocked", stop=None)
            if data.get("blocking_questions") or data.get("scope_grants"):
                return stopped(history, "permissions", "Human decision required; task scope is frozen")
            no_changes = before is not None and before == evidence
            previous = next((item for item in reversed(history.cycles[:-1]) if item.verdict == "REVISE"), None)
            signature = stalled_review_signature(data, validation)
            if no_changes and previous and signature == stalled_review_signature(json.loads(previous.review_json), previous.validation):
                return stopped(history, "revision", "Revision made no changes and the same findings/validation remain")
            if denials and no_changes:
                return stopped(history, "permissions", "Required operations denied; no automatic retry")
            if history.revisions >= context.policy.max_revision_cycles:
                return replace(history, status="revision_limit", stop=None)
            if not allow_revision:
                return stopped(history, 'revision', 'Review requests changes; retry executor explicitly')
            selection = executor_selection(context, data["executor_selection"])
            prompt = data["next_prompt"]
            try:
                before = self.evidence.capture(context)
            except Exception as exc:
                return stopped(history, "evidence", str(exc))
            history, payload = self._invoke(context, history, "executor", selection, "revise-task", {
                "INSTRUCTIONS": prompt, "TASK_JSON": history.task_json, "REVIEW_JSON": cycle.review_json,
                "PROFILE_INSTRUCTIONS": context.profile.executor_instructions})
            if payload is None:
                return history
            malformed = _executor_output(payload)
            if malformed:
                return stopped(history, "executor", malformed)
            denials = payload.get("permission_denials", [])

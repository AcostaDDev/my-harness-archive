"""Motor con puertos explícitos y journal opcional; no publica ejecución real."""

from dataclasses import asdict, replace
import json
from uuid import uuid4

from harness_local.core.engine.acceptance import assess_acceptance
from harness_local.core.engine.context import ProjectContext
from harness_local.core.engine.contracts import (
    AgentAdapter, ContractError, IncompleteContract, RunHistory,
    Selection, context_snapshot, executor_selection, freeze, invoke_agent, task_contract,
    stop_history as stopped,
)
from harness_local.core.engine.evidence import ContentEvidence, EvidenceCapture, check_paths
from harness_local.core.engine.journal import EngineJournal, JournalError
from harness_local.core.engine.planning import deterministic_task, section
from harness_local.core.engine.review import ReviewCycle, review_contract, stalled_review_signature
from harness_local.core.engine.validation import CommandRunner, run_command, run_validations


class OfflineEngine:
    """Puertos inyectados; H2.1/H2.2 proporcionan solo adaptadores falsos."""

    def __init__(self, agents: AgentAdapter, commands: CommandRunner, evidence: EvidenceCapture,
                 journal: EngineJournal | None = None):
        self.agents = agents
        self.commands = commands
        self.evidence = evidence
        self.journal = journal

    def _checkpoint(self, history: RunHistory, stage: str) -> None:
        if self.journal:
            self.journal.checkpoint(history, stage)

    def _prepare(self, context: ProjectContext, history: RunHistory) -> RunHistory:
        self._checkpoint(history, "preparation")
        for command in context.profile.preparation:
            result = run_command(context, self.commands, command, self.journal)
            entry = freeze({"command": asdict(command), "result": asdict(result)})
            history = replace(history, preparation_json=history.preparation_json + (entry,))
            self._checkpoint(history, "preparation")
            if not result.passed:
                return stopped(history, "preparation", result.error or "Environment preparation failed")
        return history

    def start(self, context: ProjectContext, task_id: str, phase_id: str, text: str,
              *, history: RunHistory | None = None) -> RunHistory:
        history = history or RunHistory(str(uuid4()), context_snapshot(context))
        if (history.context_json != context_snapshot(context) or history.task_json is not None
                or history.attempts or history.cycles or history.stops or history.preparation_json
                or history.status != "planned"):
            raise ContractError("Start requires a fresh history with the frozen context")
        history = self._prepare(context, history)
        if history.stop:
            return history
        self._checkpoint(history, "planner")
        try:
            if context.policy.planning_mode != "agent":
                try:
                    contract = deterministic_task(context, task_id, phase_id, text)
                except IncompleteContract:
                    if context.policy.planning_mode == "deterministic":
                        raise
                else:
                    history = replace(history, task_json=contract)
            if history.task_json is None:
                prompt = "Plan exactly the requested task with an explicit executor selection.\n" + freeze({
                    "task_id": task_id, "phase_id": phase_id,
                    "task_section": section(text, rf"^##\s+{task_id}\s+[—-].*$"),
                    "shared_constraints": section(text, r"^##\s+Shared\b.*$"),
                })
                selection = Selection(context.policy.planner_model, context.policy.planner_effort, "Explicit planner policy")
                history, data = invoke_agent(context, history, self.agents, "planner", selection, prompt, self.journal)
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
        return self._review_loop(context, history, None, [])

    def _execute(self, context: ProjectContext, history: RunHistory, selection: Selection, prompt: str) -> RunHistory:
        self._checkpoint(history, "executor")
        try:
            before = self.evidence.capture(context)
        except Exception as exc:
            return stopped(history, "evidence", str(exc))
        # No path/tool/network grant is inferred from prompt text.
        prompt += "\n\nFrozen task contract:\n" + history.task_json
        prompt += "\n\nProfile instructions:\n" + context.profile.executor_instructions
        history, payload = invoke_agent(context, history, self.agents, "executor", selection, prompt, self.journal)
        if payload is None:
            return history
        denials = payload.get("permission_denials", [])
        if not isinstance(denials, list):
            return stopped(history, "executor", "Malformed permission denials")
        return self._review_loop(context, history, before, denials)

    def _review_loop(self, context: ProjectContext, history: RunHistory,
                     before: ContentEvidence | None, denials: list) -> RunHistory:
        task = json.loads(history.task_json)
        while True:
            self._checkpoint(history, "validation")
            try:
                evidence = self.evidence.capture(context)
                policy = check_paths(context, task, evidence)
                validation = run_validations(context, task, evidence, self.commands, self.journal)
                cycle = ReviewCycle(len(history.cycles), evidence, policy, validation, None, before, freeze(denials))
                history = replace(history, cycles=history.cycles + (cycle,))
                if self.evidence.capture(context) != evidence:
                    return stopped(history, "validation", "Content changed during validation; revalidate")
            except JournalError:
                raise
            except Exception as exc:
                return stopped(history, "evidence", str(exc))
            self._checkpoint(history, "reviewer")
            prompt = "Review independently the frozen task and supplied evidence; ACCEPT, REVISE or BLOCKED.\n" + freeze({
                "task": task, "evidence": asdict(evidence), "policy": asdict(policy),
                "validation": asdict(validation),
            })
            selection = Selection(context.policy.reviewer_model, context.policy.reviewer_effort, "Explicit independent review policy")
            history, data = invoke_agent(context, history, self.agents, "reviewer", selection, prompt, self.journal)
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
                    decision = assess_acceptance(cycle, self.evidence.capture(context))
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
            selection = executor_selection(context, data["executor_selection"])
            prompt = data["next_prompt"]
            try:
                before = self.evidence.capture(context)
            except Exception as exc:
                return stopped(history, "evidence", str(exc))
            prompt += "\n\nFrozen task contract:\n" + history.task_json
            prompt += "\n\nIndependent review to address:\n" + cycle.review_json
            prompt += "\n\nProfile instructions:\n" + context.profile.executor_instructions
            history, payload = invoke_agent(context, history, self.agents, "executor", selection, prompt, self.journal)
            if payload is None:
                return history
            denials = payload.get("permission_denials", [])
            if not isinstance(denials, list):
                return stopped(history, "executor", "Malformed permission denials")

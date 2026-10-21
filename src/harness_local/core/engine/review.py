"""Validación de reviews y caracterización del ciclo sin progreso legacy."""

from dataclasses import dataclass
import json

from harness_local.core.engine.context import ProjectContext
from harness_local.core.engine.contracts import ContractError, executor_selection, freeze
from harness_local.core.engine.evidence import ContentEvidence, PathPolicyResult
from harness_local.core.engine.validation import ValidationReport


# D088 punto 2 (P008-T003): el ejecutor no edita DECISIONS; propone ADR en su salida y el revisor devuelve las que
# respalda. Acotadas y sin efecto sobre el veredicto ni la aceptación; se consolidan en la reconciliación o por
# edición confirmada.
MAX_DECISION_PROPOSALS = 5
DECISION_FIELDS = {'title': 200, 'decision': 4000, 'rationale': 4000}


def decision_proposals(value: object) -> list[dict]:
    if not isinstance(value, list) or len(value) > MAX_DECISION_PROPOSALS:
        raise ContractError(f"decision_proposals must be a list of at most {MAX_DECISION_PROPOSALS} items")
    for item in value:
        if (not isinstance(item, dict) or set(item) != set(DECISION_FIELDS)
                or not all(isinstance(item[key], str) and item[key].strip() and len(item[key]) <= limit
                           for key, limit in DECISION_FIELDS.items())):
            raise ContractError("Each decision proposal needs non-empty title (≤200), decision and rationale (≤4000)")
    return value


def review_contract(context: ProjectContext, task: dict, review: dict) -> str:
    if review.get("task_id") != task["task_id"] or review.get("verdict") not in ("ACCEPT", "REVISE", "BLOCKED"):
        raise ContractError("Review task/verdict mismatch")
    for field in ("findings", "blocking_questions", "scope_grants"):
        if field in review and not isinstance(review[field], list):
            raise ContractError(f"Invalid review {field}")
    for finding in review.get("findings", []):
        if not isinstance(finding, dict) or not all(isinstance(finding.get(key, ""), str)
                for key in ("severity", "category", "file", "problem")):
            raise ContractError("Invalid review finding")
    if "decision_proposals" in review:
        decision_proposals(review["decision_proposals"])
    if review["verdict"] == "REVISE":
        executor_selection(context, review.get("executor_selection"))
        if not isinstance(review.get("next_prompt"), str) or not review["next_prompt"].strip():
            raise ContractError("REVISE requires a fresh selection and next_prompt")
    return freeze(review)


def stalled_review_signature(review: dict, validation: ValidationReport) -> str:
    findings = sorted((item.get("category", ""), item.get("file", ""), item.get("problem", ""))
                      for item in review.get("findings", []) if item.get("severity") != "info")
    commands = [(entry.requested, entry.result.passed, entry.result.exit_code) for entry in validation.entries]
    return freeze([findings, commands])


@dataclass(frozen=True)
class ReviewCycle:
    number: int
    evidence: ContentEvidence
    policy: PathPolicyResult
    validation: ValidationReport
    review_json: str | None
    before_execution: ContentEvidence | None
    permission_denials_json: str = "[]"
    # P009-T019 (D133): formateo del perfil tras el intento del ejecutor (comando, rutas y resultado); None si no hubo.
    formatting_json: str | None = None

    @property
    def verdict(self) -> str | None:
        value = json.loads(self.review_json).get("verdict") if self.review_json else None
        return value if isinstance(value, str) else None

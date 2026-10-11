"""Decisión pura: ACCEPT, validación y política no equivalen a commit."""

from dataclasses import dataclass
import json

from harness_local.core.engine.evidence import ContentEvidence
from harness_local.core.engine.review import ReviewCycle


@dataclass(frozen=True)
class AcceptanceDecision:
    eligible: bool
    reasons: tuple[str, ...]
    evidence: ContentEvidence


def assess_acceptance(cycle: ReviewCycle, current: ContentEvidence) -> AcceptanceDecision:
    review = json.loads(cycle.review_json) if cycle.review_json else {}
    reasons = []
    if review.get("verdict") != "ACCEPT":
        reasons.append("Independent review did not ACCEPT")
    if review.get("blocking_questions") or review.get("scope_grants"):
        reasons.append("Unresolved questions or scope grants")
    if cycle.policy.hard_failure:
        reasons.append("File policy failure")
    if not cycle.validation.all_passed:
        reasons.append("Deterministic validation failed")
    if cycle.validation.evidence != cycle.evidence or current != cycle.evidence:
        reasons.append("Content changed since evidence capture")
    return AcceptanceDecision(not reasons, tuple(reasons), cycle.evidence)

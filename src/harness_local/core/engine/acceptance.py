"""Decisión pura: ACCEPT, validación y política no equivalen a commit."""

from dataclasses import dataclass
import json

from harness_local.core.engine.context import ProjectContext
from harness_local.core.engine.evidence import ContentEvidence, matches
from harness_local.core.engine.review import ReviewCycle


@dataclass(frozen=True)
class AcceptanceDecision:
    eligible: bool
    reasons: tuple[str, ...]
    evidence: ContentEvidence


def documentation_parity(context: ProjectContext, changed_paths) -> dict | None:
    """D088 punto 6 (P008-T003): qué tocó el diff de modelos de datos, diagrama y flujos. None fuera del layout v2."""
    from harness_local.core.engine.documents import layout
    target = layout(context)
    if target is None:
        return None
    models = [path for path in changed_paths
              if path != target.ddbb_diagram and matches(path, context.profile.data_model_paths)]
    return {'data_model_paths': list(context.profile.data_model_paths), 'data_model_changes': models,
            'ddbb_diagram': target.ddbb_diagram, 'ddbb_diagram_changed': target.ddbb_diagram in changed_paths,
            'flows_dir': target.flows_dir,
            'flows_changed': [path for path in changed_paths if path.startswith(target.flows_dir + '/')]}


def parity_reasons(context: ProjectContext, changed_paths) -> list[str]:
    """Motivo determinista: un cambio de modelos de datos sin el diagrama de datos no se acepta. La paridad de
    flujos de negocio la juzga el revisor (`review-task`)."""
    parity = documentation_parity(context, changed_paths)
    if parity is None or not parity['data_model_changes'] or parity['ddbb_diagram_changed']:
        return []
    return [f"Data model changed without {parity['ddbb_diagram']} (D088): "
            + ", ".join(parity['data_model_changes'][:20])]


def assess_acceptance(cycle: ReviewCycle, current: ContentEvidence, context: ProjectContext) -> AcceptanceDecision:
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
    reasons += parity_reasons(context, cycle.evidence.changed_paths)
    if cycle.validation.evidence != cycle.evidence or current != cycle.evidence:
        reasons.append("Content changed since evidence capture")
    return AcceptanceDecision(not reasons, tuple(reasons), cycle.evidence)

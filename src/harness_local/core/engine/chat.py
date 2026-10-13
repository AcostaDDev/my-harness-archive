"""H4.1: turno de chat contextual. Biblioteca estándar; la autoridad vive en SQLite.

Cada turno es una invocación nueva, de solo lectura, del rol `chat` (agente revisor, Codex o Claude) con el contexto
explícito congelado al encolarlo: proyecto, fase, documentos y evidencias seleccionadas, más los
turnos anteriores. No hay sesión del proveedor que reanudar. La salida tiene un esquema fijo; una
salida inválida detiene el turno sin fallback ni reintento. El turno no escribe: la evidencia del
checkout se captura antes y después, y cualquier cambio invalida el turno y sus propuestas.
Una propuesta no ejecuta nada; solo una confirmación explícita la convierte en una tarea normal.
"""

from dataclasses import replace
import hashlib
import re

from harness_local.core.engine.contracts import ContractError, RunHistory, Selection, freeze, invoke_agent, stop_history
from harness_local.core.engine.prompts import dump_catalog, render_attempt

TASK_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,119}")
PROPOSAL_FIELDS = ("title", "objective", "scope", "acceptance_criteria", "validation", "rationale")
MAX_PROPOSALS = 5


def digest(value) -> str:
    return hashlib.sha256(freeze(value).encode("utf-8")).hexdigest()


def _text(value, name, *, empty=False, limit=20_000) -> str:
    if not isinstance(value, str) or (not empty and not value.strip()) or len(value) > limit:
        raise ContractError(f"Chat {name} must be a {'' if empty else 'non-empty '}text of at most {limit} characters")
    return value.strip()


def _texts(value, name, *, empty=True, limit=50) -> list[str]:
    if (not isinstance(value, list) or len(value) > limit or (not empty and not value)
            or not all(isinstance(item, str) and item.strip() and len(item) <= 4000 for item in value)):
        raise ContractError(f"Chat {name} must be a list of at most {limit} non-empty texts")
    return [item.strip() for item in value]


def validate_chat_result(data: dict) -> dict:
    """Esquema fijo: respuesta, referencias y propuestas estructuradas; nada más."""
    if not isinstance(data, dict) or set(data) != {"answer", "references", "proposals"}:
        raise ContractError("Chat result must contain exactly answer, references and proposals")
    proposals = data["proposals"]
    if not isinstance(proposals, list) or len(proposals) > MAX_PROPOSALS:
        raise ContractError(f"Chat proposals must be a list of at most {MAX_PROPOSALS} items")
    result = []
    for item in proposals:
        if not isinstance(item, dict) or set(item) != set(PROPOSAL_FIELDS):
            raise ContractError("Each proposal must contain exactly " + ", ".join(PROPOSAL_FIELDS))
        result.append({"title": _text(item["title"], "proposal title", limit=200),
                       "objective": _text(item["objective"], "proposal objective", limit=4000),
                       "scope": _text(item["scope"], "proposal scope", empty=True, limit=4000),
                       "acceptance_criteria": _texts(item["acceptance_criteria"], "acceptance criteria", empty=False),
                       "validation": _texts(item["validation"], "validation"),
                       "rationale": _text(item["rationale"], "proposal rationale", empty=True, limit=4000)})
    return {"answer": _text(data["answer"], "answer"), "references": _texts(data["references"], "references"),
            "proposals": result}


def task_text(proposal: dict, task_id: str, origin: dict) -> str:
    """Sección de plan para el flujo normal. Sin rutas permitidas ni ejecutor legibles por máquina:
    el contrato lo fija el planificador bajo la política del proyecto, nunca el chat."""
    if not TASK_ID.fullmatch(task_id):
        raise ValueError("Task id must be 1–120 letters, digits, '.', '_' or '-'")
    lines = [f"## {task_id} — {proposal['title']}", f"**Objective:** {proposal['objective']}"]
    if proposal["scope"]:
        lines.append(f"**Scope:** {proposal['scope']}")
    lines += ["**Acceptance criteria:**", *[f"- {item}" for item in proposal["acceptance_criteria"]]]
    if proposal["validation"]:
        lines += ["**Validation:**", *[f"- {item}" for item in proposal["validation"]]]
    if proposal["rationale"]:
        lines.append(f"**Business context:** {proposal['rationale']}")
    lines.append(f"**References:** chat conversation {origin['conversation_id']}, turn {origin['turn_number']}, "
                 f"proposal {origin['proposal_id']} (sha256 {origin['proposal_sha256']})")
    return "\n".join(lines) + "\n"


def chat_turn(context, history: RunHistory, snapshot: dict, agents, evidence, journal,
              catalog) -> tuple[RunHistory, dict]:
    """Una sola invocación con la petición congelada; la evidencia del checkout no puede cambiar."""

    def done(history, status, reasons, *, result=None, checkout=None):
        return replace(history, status="completed", stop=None) if status == "ANSWERED" else history, {
            "status": status, "reasons": list(reasons), "result": result, "checkout": checkout}

    if digest(snapshot["context"]) != snapshot["context_sha256"]:
        raise ContractError("Frozen chat context changed after it was queued")
    journal.checkpoint(history, "chat")
    try:
        before = evidence.capture(context)
    except Exception as exc:
        reason = f"Checkout evidence could not be captured before the turn: {type(exc).__name__}: {exc}"
        return done(stop_history(history, "evidence", reason), "FAILED", [reason])
    observed = {"base_revision": before.base_revision, "fingerprint": before.fingerprint}
    try:
        catalog_json = dump_catalog(catalog)
        prompt, prompt_snapshot = render_attempt(catalog, "chat-turn", {
            "CONTEXT_JSON": freeze(snapshot["context"]), "MESSAGE": snapshot["message"]}, context)
    except (ValueError, KeyError, TypeError) as exc:
        return done(stop_history(history, "prompts", str(exc)), "FAILED", [str(exc)], checkout={"before": observed})
    history = replace(history, prompt_catalog_json=catalog_json)
    selection = Selection(context.policy.planner_model, context.policy.planner_effort,
                          "Explicit planner policy for read-only chat proposals")
    history, data = invoke_agent(context, history, agents, "chat", selection, prompt, journal,
                                 prompt_snapshot_json=prompt_snapshot)
    try:
        after = evidence.capture(context)
    except Exception as exc:
        reason = f"Checkout evidence could not be re-captured after the turn: {type(exc).__name__}: {exc}"
        return done(stop_history(history, "evidence", reason) if history.stop is None else history, "FAILED",
                    [reason], result=data, checkout={"before": observed, "after": None})
    checkout = {"before": observed, "after": {"base_revision": after.base_revision, "fingerprint": after.fingerprint},
                "unchanged": after == before}
    if after != before:
        reason = "The checkout changed during a read-only chat turn; the answer and its proposals are discarded"
        return done(stop_history(history, "chat", reason) if history.stop is None else history, "FAILED", [reason],
                    result=data, checkout=checkout)
    if data is None:
        return done(history, "FAILED", [history.stop.reason], checkout=checkout)
    try:
        result = validate_chat_result(data)
    except ContractError as exc:
        return done(stop_history(history, "chat", str(exc)), "FAILED", [str(exc)], result=data, checkout=checkout)
    return done(history, "ANSWERED", [], result=result, checkout=checkout)

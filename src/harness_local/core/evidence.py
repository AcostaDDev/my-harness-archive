"""Proyecciones de evidencia observada, sin reconstruir estados del motor."""
from typing import Any, Iterator

from harness_local.core.legacy import TELEMETRY_FIELDS, field_observation


def evidence_entries(kind: str, payload: Any) -> Iterator[dict[str, Any]]:
    """Cada entrada conserva su JSON pointer y campos no registrados."""
    if not isinstance(payload, dict):
        return
    fields = TELEMETRY_FIELDS.get(kind, ())
    if kind == "task":
        fields = ("task_id", "phase_id", "title", "objective", "executor_selection")
    elif kind in ("review", "phase_review", "stop", "resume", "reconcile", "phase_metadata"):
        fields = ("verdict", "summary", "reason", "stage", "task_id", "phase_id", "head")
    elif kind == "validation":
        fields = ("iteration", "all_passed", "note", "policy")
    for name in fields:
        yield {"kind": "field", "pointer": f"/{name}", "fields": {name: field_observation(payload, name)}}
    for name, entry_kind in (("findings", "finding"), ("blocking_questions", "blocking_question"),
                             ("acceptance_criteria_results", "criterion"),
                             ("exit_criteria_results", "criterion"), ("required_actions", "action"),
                             ("problems", "problem"), ("commands", "command")):
        values = payload.get(name)
        if not isinstance(values, list):
            continue
        for index, value in enumerate(values):
            entry = {"kind": entry_kind, "pointer": f"/{name}/{index}", "value": value}
            if entry_kind == "command":
                entry["fields"] = {field: field_observation(value, field) for field in (
                    "command", "argv", "passed", "exit_code", "duration_seconds", "error",
                    "stdout_file", "stderr_file")}
            yield entry

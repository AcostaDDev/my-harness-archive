"""H3.3: puertas de fase con puertos explícitos. Biblioteca estándar; la autoridad vive en SQLite.

READY se vincula a contenido exacto: definición, HEAD/fingerprint Git limpio, documentos
adoptados, commits de tareas aceptadas y preguntas. El cierre vuelve a observar ese
contenido antes de cualquier efecto Git. D088: cierre y archivo en un solo flujo,
con tag opcional sobre el HEAD evaluado y un commit documental conciliable.
Los snapshots anteriores conservan el protocolo de cierre que congelaron.
"""

from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import re
from typing import Protocol

from harness_local.core.engine.commit import CommitError, git_provenance
from harness_local.core.engine.context import ProjectContext, relative_path
from harness_local.core.engine.contracts import (
    ContractError, RunHistory, Selection, freeze, invoke_agent, stop_history,
)
from harness_local.core.engine.evidence import ContentEvidence, PathPolicyResult, strip_empty_provenance
from harness_local.core.engine.prompts import dump_catalog, render_attempt
from harness_local.core.engine.validation import run_validations, validation_payload
from harness_local.core.engine.review import ReviewCycle

PHASE_CODE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,119}")
TAG_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*(?:\.[A-Za-z0-9_-]+)*")
VERDICTS = ("READY", "REVISE", "BLOCKED")
TAG_KINDS = ("lightweight", "annotated")
# Resultado de check → estado de fase. FAILED vuelve al estado anterior al check.
CHECK_STATUS = {"READY": "READY_TO_CLOSE", "REVISE": "NEEDS_RECONCILIATION", "BLOCKED": "BLOCKED",
                "NEEDS_RECONCILIATION": "NEEDS_RECONCILIATION", "NOT_READY": "ACTIVE"}


def digest(value) -> str:
    return hashlib.sha256(freeze(value).encode("utf-8")).hexdigest()


def _texts(value, name, *, empty=False) -> list[str]:
    if (not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value)
            or (not empty and not value) or len(set(value)) != len(value)):
        raise ContractError(f"Phase {name} must be a list of distinct, non-empty texts")
    return [item.strip() for item in value]


def phase_definition(context: ProjectContext, data: dict) -> dict:
    """Definición congelada por quien crea la fase; nunca la amplía un agente."""
    if not isinstance(data, dict) or set(data) != {"code", "objective", "exit_criteria", "tasks", "documents", "tag"}:
        raise ContractError("Phase requires code, objective, exit_criteria, tasks, documents and tag")
    code, objective, tag = data["code"], data["objective"], data["tag"]
    if not isinstance(code, str) or not PHASE_CODE.fullmatch(code):
        raise ContractError("Phase code must be 1–120 letters, digits, '.', '_' or '-'")
    if not isinstance(objective, str) or not objective.strip():
        raise ContractError("Phase objective required")
    documents = _texts(data["documents"], "documents")
    for path in documents:
        relative_path(path)
        context.path(path)
    if tag is not None and (not isinstance(tag, str) or len(tag) > 100 or not TAG_NAME.fullmatch(tag)
                            or tag.endswith(".lock")):
        raise ContractError("Tag must be null or a simple tag name (letters, digits, '.', '_', '-')")
    return {"code": code, "objective": objective.strip(), "exit_criteria": _texts(data["exit_criteria"], "exit criteria"),
            "tasks": _texts(data["tasks"], "tasks", empty=True), "documents": documents, "tag": tag}


def document_hashes(context: ProjectContext, paths) -> dict[str, str | None]:
    """SHA-256 de archivos regulares sin enlaces; None si no existen (ausencia explícita)."""
    result = {}
    for path in paths:
        item = context.path(path)
        if item.is_symlink() or (item.exists() and not item.is_file()):
            raise ValueError(f"Phase document {path} must be a regular file")
        result[path] = hashlib.sha256(item.read_bytes()).hexdigest() if item.exists() else None
    return result


class PhaseGit(Protocol):
    def capture(self, context: ProjectContext) -> ContentEvidence: ...
    def contains(self, context: ProjectContext, commit: str) -> bool: ...
    def seal_tag(self, context: ProjectContext, intent: dict) -> str: ...
    def tag(self, context: ProjectContext, intent: dict) -> dict: ...


def tag_message(definition: dict, binding_sha256: str) -> str:
    """Sin identificador de operación: un cierre posterior que concilia produce el mismo objeto."""
    return (f"Phase {definition['code']} closed\n\nHarness-Phase: {definition['code']}\n"
            f"Harness-Ready-Binding: {binding_sha256}\n")


def tag_intent(snapshot: dict, git: PhaseGit, context: ProjectContext, now=None) -> dict:
    """Intención completa antes del efecto. Un tag anotado fija mensaje, identidad y fecha, y con
    ellos su id; si un cierre anterior dejó una intención incierta para el mismo READY, se reutiliza."""
    ready, name = snapshot["ready"], snapshot["definition"]["tag"]
    kind = snapshot.get("tag_kind", "lightweight")
    if kind not in TAG_KINDS:
        raise ValueError("Unknown tag kind")
    intent = {"operation_id": snapshot["operation_id"], "ref": f"refs/tags/{name}", "kind": kind,
              "target": ready["binding"]["head"], "binding_sha256": ready["binding_sha256"]}
    if kind == "annotated":
        previous = snapshot.get("previous_tag_intent") or {}
        if all(previous.get(key) == intent[key] for key in ("ref", "kind", "target", "binding_sha256")):
            fixed = {key: previous[key] for key in ("message", "tagger_name", "tagger_email", "tagged_at")}
        else:
            instant = (now or (lambda: datetime.now(timezone.utc)))()
            if instant.tzinfo is None:
                raise ValueError("Clock must return an aware time")
            fixed = {"message": tag_message(snapshot["definition"], ready["binding_sha256"]),
                     "tagger_name": git.identity.name, "tagger_email": git.identity.email,
                     "tagged_at": int(instant.timestamp())}
        intent.update(fixed)
        intent["object"] = git.seal_tag(context, intent)
    return intent


def binding(snapshot: dict, evidence: ContentEvidence, documents: dict) -> dict:
    return {"definition_sha256": snapshot["definition_sha256"], "head": evidence.base_revision,
            "fingerprint": evidence.fingerprint, "documents": documents,
            "tasks": {task: (None if item is None else {"run_id": item["run_id"], "commit": item["commit"]})
                      for task, item in snapshot["tasks"].items()},
            "questions_sha256": snapshot["questions_sha256"]}


def observe(context: ProjectContext, snapshot: dict, git: PhaseGit):
    """Contenido actual y motivos por los que no puede estar listo; solo lecturas."""
    definition = snapshot["definition"]
    documents = document_hashes(context, definition["documents"])
    drift = sorted(path for path, value in documents.items() if snapshot["documents"].get(path) != value)
    evidence = git.capture(context)
    reasons = []
    try:
        git_provenance(evidence)
    except CommitError as exc:
        reasons.append(f"Phase gates require Git evidence: {exc}")
    if evidence.changed_paths:
        reasons.append("Uncommitted changes in the checkout: " + ", ".join(evidence.changed_paths[:20]))
    for task in (() if snapshot.get('terminal') == 'ABANDONED' else definition["tasks"]):
        item = snapshot["tasks"].get(task)
        if item is None:
            reasons.append(f"Task {task} has no committed acceptance")
        elif not git.contains(context, item["commit"]):
            reasons.append(f"Task {task} commit {item['commit']} is not reachable from HEAD")
    return evidence, documents, drift, reasons


def validate_phase_result(definition: dict, data: dict) -> dict:
    if data.get("phase_id") != definition["code"] or data.get("verdict") not in VERDICTS:
        raise ContractError("Phase review must name this phase and READY, REVISE or BLOCKED")
    if not isinstance(data.get("summary"), str):
        raise ContractError("Phase review summary required")
    for key in ("required_actions", "blocking_questions"):
        value = data.get(key)
        if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
            raise ContractError(f"Phase review {key} must be a list of texts")
    results = data.get("exit_criteria_results")
    if (not isinstance(results, list) or not all(
            isinstance(item, dict) and isinstance(item.get("criterion"), str) and type(item.get("passed")) is bool
            and isinstance(item.get("evidence"), str) for item in results)
            or sorted(item["criterion"] for item in results) != sorted(definition["exit_criteria"])):
        raise ContractError("Phase review must evaluate each frozen exit criterion exactly once")
    if data["verdict"] == "READY" and (not all(item["passed"] for item in results)
                                       or data["required_actions"] or data["blocking_questions"]):
        raise ContractError("READY requires every exit criterion passed, no actions and no questions")
    if data["verdict"] == "REVISE" and not data["required_actions"]:
        raise ContractError("REVISE requires concrete required actions")
    return data


def check_phase(context: ProjectContext, history: RunHistory, snapshot: dict, agents, commands, git: PhaseGit,
                journal, catalog) -> tuple[RunHistory, dict]:
    """Puertas deterministas antes de gastar una llamada; el agente solo evalúa."""
    definition = snapshot["definition"]

    def outcome(verdict, reasons, *, bound=None, result=None, validation=None, questions=()):
        return {"verdict": verdict, "reasons": list(reasons), "binding": bound,
                "binding_sha256": digest(bound) if bound else None, "result": result,
                "validation": validation, "questions": list(questions)}

    def done(history, value):
        return replace(history, status="completed", stop=None), value

    if snapshot["open_questions"]:
        return done(history, outcome("BLOCKED", ["Pending blocking questions must be answered first"]))
    journal.checkpoint(history, "phase")
    try:
        evidence, documents, drift, reasons = observe(context, snapshot, git)
    except Exception as exc:
        return done(stop_history(history, "evidence", f"{type(exc).__name__}: {exc}"),
                    outcome("FAILED", [f"Evidence could not be captured: {exc}"]))
    if drift:
        return done(history, outcome("NEEDS_RECONCILIATION",
                                     ["Documents changed since the adopted baseline: " + ", ".join(drift)]))
    from harness_local.core.engine.documents import BUDGETS, base_section
    try:
        state = context.path(context.state_file).read_bytes()
        base = base_section(state.decode('utf-8')) or ''
    except (ValueError, OSError, UnicodeError) as exc:
        return done(history, outcome('FAILED', [f'STATE could not be read: {exc}']))
    if len(state) > BUDGETS['state'] or len(base.encode('utf-8')) > BUDGETS['base']:
        return done(history, outcome("NEEDS_RECONCILIATION", [
            "Compact STATE (24 KiB) and its accumulated baseline (12 KiB) before checking the phase"]))
    if reasons:
        return done(history, outcome("NOT_READY", reasons))
    bound = binding(snapshot, evidence, documents)
    journal.checkpoint(history, "validation")
    report = run_validations(context, {"validation_commands": []}, evidence, commands, journal, run_id=history.id)
    if any(entry.reports for entry in report.entries):
        history = replace(history, cycles=history.cycles + (
            ReviewCycle(len(history.cycles), evidence, PathPolicyResult(()), report, None, None),))
        journal.checkpoint(history, 'validation')
    validation = strip_empty_provenance(validation_payload(report, include_cases=False))
    if not report.all_passed:
        return done(history, outcome("NOT_READY", ["Baseline validation failed"], validation=validation))
    try:
        catalog_json = dump_catalog(catalog)
        payload = {"phase": definition, "head": evidence.base_revision, "fingerprint": evidence.fingerprint,
                   "documents": documents, "tasks": snapshot["task_evidence"], "validation": validation,
                   "answered_questions": snapshot["answered_questions"]}
        prompt, prompt_snapshot = render_attempt(catalog, "close-phase", {
            "PHASE_ID": definition["code"], "EVIDENCE_JSON": freeze(payload)}, context)
    except (ValueError, KeyError, TypeError) as exc:
        return done(stop_history(history, "prompts", str(exc)), outcome("FAILED", [str(exc)], validation=validation))
    history = replace(history, prompt_catalog_json=catalog_json)
    selection = Selection(context.policy.reviewer_model, context.policy.reviewer_effort,
                          "Explicit independent phase review policy")
    history, data = invoke_agent(context, history, agents, "phase", selection, prompt, journal,
                                 prompt_snapshot_json=prompt_snapshot)
    if data is None:
        return done(history, outcome("FAILED", [history.stop.reason], validation=validation))
    try:
        validate_phase_result(definition, data)
    except ContractError as exc:
        return done(stop_history(history, "phase", str(exc)),
                    outcome("FAILED", [str(exc)], result=data, validation=validation))
    try:
        after = observe(context, snapshot, git)
    except Exception as exc:
        return done(stop_history(history, "evidence", f"{type(exc).__name__}: {exc}"),
                    outcome("FAILED", [f"Evidence could not be re-captured: {exc}"], result=data))
    if after[0] != evidence or after[1] != documents:
        return done(history, outcome("NOT_READY", ["Content changed during the phase check; check again"],
                                     result=data, validation=validation))
    verdict = data["verdict"]
    reasons = [] if verdict == "READY" else (data["required_actions"] or [data["summary"]])
    return done(history, outcome(verdict, reasons, bound=bound if verdict == "READY" else None, result=data,
                                 validation=validation, questions=data["blocking_questions"]))


def close_phase(context: ProjectContext, history: RunHistory, snapshot: dict, git: PhaseGit,
                journal, now=None) -> tuple[RunHistory, dict]:
    """Reobserva READY; sella, etiqueta y archiva. Una intención existente solo se concilia."""
    ready = snapshot["ready"]
    done = replace(history, status="completed", stop=None)
    closure = snapshot.get('closure')
    continuing = closure and closure.get('commit_intent')
    if not continuing and not snapshot["authorization"]["usable"]:
        return done, {"status": "EXPIRED", "reasons": ["Close authorization expired before the job ran"]}
    journal.checkpoint(history, "phase")
    if not continuing:
        evidence, documents, drift, reasons = observe(context, snapshot, git)
        current = binding(snapshot, evidence, documents)
        if drift:
            reasons.append("Documents changed since READY: " + ", ".join(drift))
        changed = sorted(key for key in current if current[key] != ready["binding"].get(key))
        if changed:
            reasons.append("READY evidence is stale: " + ", ".join(changed) + " changed")
        if reasons:
            return done, {"status": "STALE", "reasons": reasons, "observed_sha256": digest(current)}
    if closure:
        from harness_local.core.engine.document_ops import seal_operation, BaseChanged
        try:
            sealed = seal_operation(context, history, closure, git, journal, now,
                                    label=f"archive {snapshot['definition']['code']}")
        except BaseChanged as exc:
            return done, {'status': 'STALE', 'reasons': [str(exc)]}
    tag = None
    if snapshot["definition"]["tag"] is not None and snapshot.get('terminal', 'CLOSED') == 'CLOSED':
        intent = snapshot.get('tag_intent') or tag_intent(snapshot, git, context, now)
        if not snapshot.get('tag_intent'):
            journal.tag_intent(intent)
        tag = git.tag(context, intent)
        if tag["status"] == "conflict":
            return done, {"status": "FAILED", "reasons": [tag["diagnostic"]], "tag": tag}
    result = {'status': snapshot.get('terminal', 'CLOSED'), 'reasons': [], 'tag': tag,
              'binding_sha256': ready['binding_sha256']}
    if closure:
        outcome = git.execute_documents(context, sealed, closure['preview']['documents'])
        if outcome.status == 'invalidated':
            return done, {'status': 'STALE', 'reasons': [outcome.diagnostic], 'tag': tag}
        result.update(commit=outcome.commit, tree=outcome.tree, archive=closure['preview']['archive'],
                      reconciled=outcome.status == 'reconciled')
        from harness_local.core.engine.documents import require_layout
        work = context.path(require_layout(context).phase_dir)
        if work.exists():
            for folder in sorted(work.rglob('*'), key=lambda item: len(item.parts), reverse=True):
                if folder.is_dir() and not folder.is_symlink():
                    folder.rmdir()
    return done, result

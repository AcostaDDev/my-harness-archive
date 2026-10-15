"""Contrato H2.4 del commit aceptado: intención, resultado y orquestación.

Biblioteca estándar y puertos. Los subprocesos Git y SQLite viven en adaptadores.
El commit se crea desde el árbol revisado (y solo actualizaciones mecánicas
declaradas) y su identidad es determinista: tras una caída se comprueba antes
de repetir. ACCEPT/acceptance_ready no equivalen a un commit existente.
"""

from dataclasses import asdict, dataclass
import base64
from datetime import datetime, timezone
import json
import re
from typing import Callable, Protocol
from uuid import uuid4

from harness_local.core.engine.acceptance import assess_acceptance
from harness_local.core.engine.context import ProjectContext, relative_path
from harness_local.core.engine.contracts import RunHistory, freeze, stop_history
from harness_local.core.engine.evidence import ContentEvidence, matches

GIT_FORMAT = "git-v1"
_OBJECT_ID = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?")


class CommitError(RuntimeError):
    """Precondición o contrato de commit inválido; no se crea ningún efecto."""


class CommitUncertain(CommitError):
    """No puede determinarse qué ocurrió; exige recuperación manual con evidencia."""


@dataclass(frozen=True)
class GitIdentity:
    name: str
    email: str

    def __post_init__(self):
        for value in (self.name, self.email):
            if (not isinstance(value, str) or not value.strip() or value != value.strip()
                    or any(char in value for char in "<>\n\r\0")):
                raise ValueError("Explicit commit identity required without markup or newlines")


@dataclass(frozen=True)
class MechanicalUpdate:
    """Contenido escrito por el harness; UTF-8 por defecto, bytes base64 o borrado para el archivo D088."""

    path: str
    content: str | None
    reason: str
    encoding: str = 'utf-8'

    def __post_init__(self):
        relative_path(self.path)
        if self.path.startswith(".git/") or self.path == ".git":
            raise ValueError("Mechanical updates cannot target Git metadata")
        if self.encoding not in ('utf-8', 'base64'):
            raise ValueError('Unknown mechanical content encoding')
        if self.content is not None and (not isinstance(self.content, str) or "\0" in self.content):
            raise ValueError("Mechanical content must be NUL-free UTF-8 text")
        self.bytes()  # valida también el base64 antes de sellar la intención
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("Mechanical updates require an explicit reason")

    def bytes(self) -> bytes | None:
        """None elimina el archivo; base64 conserva artefactos de fase binarios por bytes."""
        if self.content is None:
            return None
        return (base64.b64decode(self.content, validate=True) if self.encoding == 'base64'
                else self.content.encode('utf-8'))


@dataclass(frozen=True)
class GitProvenance:
    base_revision: str
    base_tree: str
    worktree_tree: str
    index_tree: str


def git_provenance(evidence: ContentEvidence) -> GitProvenance:
    if evidence.provenance_json is None:
        raise CommitError("Evidence has no Git provenance and cannot support a commit")
    try:
        data = json.loads(evidence.provenance_json)
        if not isinstance(data, dict) or data.get("format") != GIT_FORMAT:
            raise ValueError
        values = [evidence.base_revision] + [data[key] for key in ("base_tree", "worktree_tree", "index_tree")]
        if not all(isinstance(item, str) and _OBJECT_ID.fullmatch(item) for item in values):
            raise ValueError
    except (ValueError, KeyError) as exc:
        raise CommitError("Evidence provenance is not valid Git provenance") from exc
    return GitProvenance(evidence.base_revision, data["base_tree"], data["worktree_tree"], data["index_tree"])


@dataclass(frozen=True)
class CommitPlan:
    """Datos fijados antes de que el adaptador calcule árbol/commit esperados."""

    base_revision: str
    reviewed_tree: str
    mechanical: tuple[MechanicalUpdate, ...]
    message: str
    author_name: str
    author_email: str
    committed_at: int


@dataclass(frozen=True)
class CommitIntent:
    operation_id: str
    run_id: str
    task_id: str
    base_revision: str
    reviewed_fingerprint: str
    reviewed_tree: str
    reviewed_index_tree: str
    reviewed_paths: tuple[str, ...]
    mechanical: tuple[MechanicalUpdate, ...]
    expected_tree: str
    expected_commit: str
    message: str
    author_name: str
    author_email: str
    committed_at: int

    def to_json(self) -> str:
        return freeze(asdict(self))

    @staticmethod
    def from_json(text: str) -> "CommitIntent":
        data = json.loads(text)
        data["reviewed_paths"] = tuple(data["reviewed_paths"])
        data["mechanical"] = tuple(MechanicalUpdate(**item) for item in data["mechanical"])
        return CommitIntent(**data)


@dataclass(frozen=True)
class CommitOutcome:
    # committed: esta ejecución movió la referencia. reconciled: ya existía.
    # invalidated: sin efecto; el contenido/base revisados ya no son vigentes.
    status: str
    operation_id: str | None
    commit: str | None = None
    tree: str | None = None
    head: str | None = None
    diagnostic: str | None = None
    observed_fingerprint: str | None = None
    index: str | None = None  # refreshed | already_current | left_untouched

    def __post_init__(self):
        if self.status not in {"committed", "reconciled", "invalidated"}:
            raise ValueError("Unknown commit outcome status")

    def to_json(self) -> str:
        return freeze(asdict(self))

    @staticmethod
    def from_json(text: str) -> "CommitOutcome":
        return CommitOutcome(**json.loads(text))


class CommitWriter(Protocol):
    identity: GitIdentity

    def capture(self, context: ProjectContext) -> ContentEvidence: ...
    def seal(self, context: ProjectContext, plan: CommitPlan) -> tuple[str, str]: ...
    def execute(self, context: ProjectContext, intent: CommitIntent) -> CommitOutcome: ...


class CommitJournal(Protocol):
    def pending_commit(self) -> CommitIntent | None: ...
    def commit_intent(self, intent: CommitIntent) -> None: ...
    def commit_result(self, outcome: CommitOutcome) -> None: ...
    def commit_invalidated(self, outcome: CommitOutcome) -> None: ...


def validate_mechanical_updates(context: ProjectContext, reviewed_paths: tuple[str, ...],
                                updates: tuple[MechanicalUpdate, ...], block_paths: frozenset[str] = frozenset()) -> None:
    """Rutas propias del harness: nunca sensibles ni solapadas con lo revisado.

    D072: `block_paths` son documentos revisados cuyo único cambio mecánico es regenerar un bloque
    gestionado sobre el contenido revisado (reconciliación de fase); la prosa revisada se conserva."""
    seen: set[str] = set()
    for update in updates:
        if not isinstance(update, MechanicalUpdate):
            raise CommitError("Mechanical updates must be explicit MechanicalUpdate values")
        if update.path in seen:
            raise CommitError("Duplicate mechanical update path")
        seen.add(update.path)
        if update.path in reviewed_paths and update.path not in block_paths:
            raise CommitError("Mechanical update overlaps reviewed content; revalidate instead")
        profile = context.profile
        if matches(update.path, profile.sensitive_paths) and not matches(update.path, profile.sensitive_allowlist):
            raise CommitError("Mechanical update targets a sensitive path")
        try:
            context.path(update.path)
        except ValueError as exc:
            raise CommitError(f"Mechanical update path is unsafe: {exc}") from exc


def commit_message(prefix: str, task: dict, run_id: str, operation_id: str, fingerprint: str,
                   reviewed_tree: str, updates: tuple[MechanicalUpdate, ...]) -> str:
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,40}", prefix):
        raise CommitError("Invalid commit message prefix")
    title = " ".join(str(task["title"]).split())
    lines = [f"{prefix}: accept {task['task_id']} - {title}", "",
             f"Harness-Operation: {operation_id}", f"Harness-Run: {run_id}",
             f"Harness-Reviewed-Fingerprint: {fingerprint}", f"Harness-Reviewed-Tree: {reviewed_tree}"]
    lines += [f"Harness-Mechanical: {update.path}" for update in sorted(updates, key=lambda item: item.path)]
    return "\n".join(lines) + "\n"


def _invalidated(reason: str, observed: ContentEvidence, expected_fingerprint: str) -> CommitOutcome:
    return CommitOutcome(
        "invalidated", None, head=observed.base_revision, observed_fingerprint=observed.fingerprint,
        diagnostic=f"{reason}; reviewed fingerprint {expected_fingerprint}, observed {observed.fingerprint}")


def prepare_commit(context: ProjectContext, history: RunHistory, writer: CommitWriter, *,
                   mechanical: tuple[MechanicalUpdate, ...] = (), message_prefix: str = "harness",
                   now: Callable[[], datetime] | None = None,
                   operation_id: str | None = None,
                   block_paths: frozenset[str] = frozenset()) -> CommitIntent | CommitOutcome:
    """Comprueba aceptación vigente y fija la intención; sin efectos sobre refs ni archivos."""
    if (history.status != "acceptance_ready" or history.acceptance is None or not history.acceptance.eligible
            or not history.cycles or history.task_json is None):
        raise CommitError("Only an eligible acceptance_ready run can be committed")
    cycle = history.cycles[-1]
    reviewed = history.acceptance.evidence
    if cycle.evidence != reviewed:
        raise CommitError("Acceptance evidence does not match the last reviewed cycle")
    provenance = git_provenance(reviewed)
    current = writer.capture(context)
    decision = assess_acceptance(cycle, current, context)
    if not decision.eligible:
        return _invalidated("; ".join(decision.reasons), current, reviewed.fingerprint)
    task = json.loads(history.task_json)
    validate_mechanical_updates(context, reviewed.changed_paths, tuple(mechanical), block_paths)
    operation = operation_id or str(uuid4())
    message = commit_message(message_prefix, task, history.id, operation, reviewed.fingerprint,
                             provenance.worktree_tree, tuple(mechanical))
    instant = (now or (lambda: datetime.now(timezone.utc)))()
    if instant.tzinfo is None:
        raise ValueError("Clock must return an aware time")
    plan = CommitPlan(provenance.base_revision, provenance.worktree_tree, tuple(mechanical), message,
                      writer.identity.name, writer.identity.email, int(instant.timestamp()))
    expected_tree, expected_commit = writer.seal(context, plan)
    return CommitIntent(
        operation_id=operation, run_id=history.id, task_id=task["task_id"],
        base_revision=provenance.base_revision, reviewed_fingerprint=reviewed.fingerprint,
        reviewed_tree=provenance.worktree_tree, reviewed_index_tree=provenance.index_tree,
        reviewed_paths=tuple(reviewed.changed_paths), mechanical=tuple(mechanical),
        expected_tree=expected_tree, expected_commit=expected_commit, message=message,
        author_name=plan.author_name, author_email=plan.author_email, committed_at=plan.committed_at)


def commit_accepted(context: ProjectContext, history: RunHistory, writer: CommitWriter,
                    journal: CommitJournal, *, mechanical: tuple[MechanicalUpdate, ...] = (),
                    message_prefix: str = "harness", now: Callable[[], datetime] | None = None,
                    operation_id: str | None = None,
                    block_paths: frozenset[str] = frozenset()) -> tuple[RunHistory, CommitOutcome]:
    """Intención persistida antes del efecto, resultado después, reconciliando al reanudar."""
    intent = journal.pending_commit()
    if intent is not None:
        if intent.run_id != history.id:
            raise CommitError("Pending commit intent belongs to a different run")
    else:
        prepared = prepare_commit(context, history, writer, mechanical=mechanical,
                                  message_prefix=message_prefix, now=now, operation_id=operation_id,
                                  block_paths=block_paths)
        if isinstance(prepared, CommitOutcome):
            # Sin intención ni efecto: se conserva el hecho y se exige revalidar.
            journal.commit_invalidated(prepared)
            return stop_history(history, "commit", prepared.diagnostic or "Acceptance invalidated"), prepared
        intent = prepared
        journal.commit_intent(intent)
    outcome = writer.execute(context, intent)
    journal.commit_result(outcome)
    if outcome.status == "invalidated":
        history = stop_history(history, "commit", outcome.diagnostic or "Acceptance invalidated")
    return history, outcome

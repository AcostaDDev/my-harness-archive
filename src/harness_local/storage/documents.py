"""D072/H6.3: autoridad SQLite del contrato documental.

Proyecciones de SQLite para los bloques gestionados, regeneración mecánica en cada commit de
tarea, adopción de los hashes que escribe el propio harness y edición documental confirmada
como operación de fase con intención conciliable. Las lecturas de disco se hacen fuera de las
transacciones y se comparan por hash; ningún byte ajeno se sobrescribe.
"""

import hashlib
import json
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness_local.core.engine.commit import CommitIntent, MechanicalUpdate
from harness_local.core.engine.contracts import context_snapshot, freeze
from harness_local.core.engine.document_ops import preview_edit, read_decisions, read_text, text_hash
from harness_local.core.engine.documents import (
    BLOCK_REASON, blocks, budget_warnings, decision_index, layout, managed_bodies, replace_block, require_layout,
    validation_counts,
)
from harness_local.core.engine.phases import document_hashes
from harness_local.core.engine.serialization import load_history, restore_context
from harness_local.storage.managed import Conflict, _job
from harness_local.storage.models import (
    ManagedCommitRow as Commit, ManagedJobRow as Job, ManagedRunRow as Run, PhaseAuthorizationRow as Authorization,
    PhaseDefinitionRow as Definition, PhaseOperationRow as Operation, PhaseRow as Phase,
)
from harness_local.storage.permissions import actor
from harness_local.storage.phases import PhaseRepository, _event, _latest, _open, _operation, _questions

DOCUMENT_KINDS = ('document_export', 'transition', 'document_edit')


# --- proyecciones de SQLite --------------------------------------------------------------------


def _latest_run(session, root, code, task):
    return session.scalar(select(Run).where(Run.root == root, Run.phase_id == code, Run.task_id == task,
                                            Run.purpose == 'task').order_by(Run.created_at.desc(), Run.id).limit(1))


def _commit_of(session, root, code, task):
    return session.scalar(select(Commit.commit_sha).join(Run, Run.id == Commit.run_id).where(
        Run.root == root, Run.phase_id == code, Run.task_id == task, Run.purpose == 'task',
        Commit.status == 'COMMITTED').order_by(Commit.finished_at.desc(), Commit.operation_id).limit(1))


def _task_view(session, phase, task, *, planned, committing_run_id=None):
    run = _latest_run(session, phase.root, phase.code, task)
    history = load_history(run.history_json) if run is not None else None
    summary = verdict = tests = None
    attempts = {}
    if history is not None:
        for attempt in history.attempts:
            attempts[attempt.request.role] = attempts.get(attempt.request.role, 0) + 1
        executed = [a for a in history.attempts if a.request.role == 'executor' and a.result.payload_json]
        if executed:
            try:
                payload = json.loads(executed[-1].result.payload_json)
            except ValueError:
                payload = None
            if isinstance(payload, dict) and isinstance(payload.get('result'), str):
                summary = payload['result']
        if history.cycles:
            verdict = history.cycles[-1].verdict
            tests = validation_counts(history.cycles[-1].validation)
    committing = run is not None and run.id == committing_run_id
    return {'task_id': task, 'planned': planned, 'status': 'COMMITTED' if committing else (run.status if run else None),
            'verdict': verdict, 'commit': _commit_of(session, phase.root, phase.code, task), 'committing': committing,
            'summary': summary, 'tests': tests, 'attempts': attempts,
            'revisions': run.revisions if run is not None else None}


def state_snapshot(session, phase, committing_run_id=None) -> dict:
    """Bloques de STATE/NEXT_STEPS: fase, tareas del plan y añadidas, preguntas y último check."""
    tasks = [_task_view(session, phase, task, planned=True, committing_run_id=committing_run_id)
             for task in phase.definition['tasks']]
    extra = session.execute(select(Run.task_id).where(
        Run.root == phase.root, Run.phase_id == phase.code, Run.purpose == 'task',
        Run.task_id.notin_(phase.definition['tasks'] or [''])).group_by(Run.task_id)
        .order_by(Run.task_id)).scalars().all()
    tasks += [_task_view(session, phase, task, planned=False, committing_run_id=committing_run_id) for task in extra]
    check = _latest(session, phase.id, 'check')
    return {'phase': {'code': phase.code, 'status': phase.status, 'objective': phase.definition['objective']},
            'tasks': tasks, 'open_questions': [q.text for q in _open(_questions(session, phase.id))],
            'latest_check': None if check is None else {'status': check.status,
                                                         'reasons': (check.result or {}).get('reasons') or []}}


def phases_snapshot(session, root) -> dict:
    rows = session.scalars(select(Phase).where(Phase.root == root).order_by(Phase.created_at, Phase.id)).all()
    return {row.code: {'status': row.status, 'tag': row.definition.get('tag')} for row in rows}


def summary_snapshot(session, phase) -> dict:
    state = state_snapshot(session, phase)
    questions = [{'text': q.text, 'status': q.status, 'answer': q.answer['text'] if q.answer else None}
                 for q in _questions(session, phase.id)]
    definitions = session.scalars(select(Definition).where(Definition.phase_id == phase.id)
                                  .order_by(Definition.number)).all()
    definition = phase.definition
    return {'phase': {'code': phase.code, 'status': phase.status, 'objective': definition['objective'],
                      'exit_criteria': definition['exit_criteria'], 'tag': definition.get('tag'),
                      'definition_number': phase.definition_number},
            'tasks': [task for task in state['tasks'] if task['planned']],
            'extra_tasks': [task for task in state['tasks'] if not task['planned']],
            'questions': questions,
            'definitions': [{'number': row.number, 'origin': row.origin, 'reason': row.reason} for row in definitions]}


def latest_phase(session, root):
    return session.scalar(select(Phase).where(Phase.root == root)
                          .order_by(Phase.created_at.desc(), Phase.id.desc()).limit(1))


# --- intenciones documentales pendientes ------------------------------------------------------


def unresolved(session, root, kinds=DOCUMENT_KINDS) -> bool:
    """Una intención incierta conserva su autoridad hasta conciliación; ninguna mutación la oculta."""
    rows = session.scalars(select(Operation).join(Phase, Phase.id == Operation.phase_id).where(
        Phase.root == root, Operation.kind.in_(kinds), Operation.status.in_(('QUEUED', 'INTENT', 'INTERRUPTED')))).all()
    return any(op.request.get('commit_intent') for op in rows)


def pending(session, phase, kind):
    rows = session.scalars(select(Operation).where(Operation.phase_id == phase.id, Operation.kind == kind,
                          Operation.status == 'INTERRUPTED', Operation.finished_at.is_not(None))
                          .order_by(Operation.created_at.desc(), Operation.id)).all()
    return next((op for op in rows if op.request.get('commit_intent')), None)


def record_operation_intent(managed, session, run, intent, kind, matches):
    op, phase = _operation(session, run)
    if (op.kind != kind or op.status != 'QUEUED' or intent.operation_id != op.id or intent.run_id != run.id
            or not matches(session, phase)):
        raise Conflict('Intent must match its exact reviewed preview and SQLite authority')
    op.request = {**op.request, 'commit_intent': intent.to_json()}
    op.status = 'INTENT'
    _event(managed, session, phase, f'{kind}_intent', {
        'operation_id': op.id, 'expected_commit': intent.expected_commit, 'expected_tree': intent.expected_tree})


def verify_committed(op, outcome):
    intent = CommitIntent.from_json(op.request['commit_intent'])
    if outcome['commit'] != intent.expected_commit or outcome['tree'] != intent.expected_tree:
        raise Conflict('Result differs from its sealed intent')


def observed_documents(run, shown):
    context = restore_context(run.context_json)
    expected = {doc['path']: doc['after_sha256'] for doc in shown['documents']}
    if document_hashes(context, list(expected)) != expected:
        raise Conflict('Documents changed after the commit; recover with the recorded intent before adoption')
    return context


def abort_operation(managed, session, run, status, reason, kind):
    op, phase = _operation(session, run)
    if op.status not in ('QUEUED', 'INTENT'):
        return
    op.status, op.result, op.finished_at = status, {'reason': reason}, managed._now()
    _event(managed, session, phase, f'{kind}_aborted', {'operation_id': op.id, 'status': status, 'reason': reason})


# --- commits de tarea: bloques regenerados y adopción ------------------------------------------


def task_commit_updates(managed, context, run_id, history):
    """Bloques regenerados sobre el contenido revisado; los revisados solo admiten el bloque (reconciliación)."""
    target = require_layout(context)
    with Session(managed.engine) as session:
        run = session.get(Run, run_id)
        phase = session.scalar(select(Phase).where(Phase.root == run.root, Phase.code == run.phase_id))
        if phase is None:
            return (), frozenset()
        snap = state_snapshot(session, phase, committing_run_id=run_id)
        phases = phases_snapshot(session, run.root)
    texts = {path: read_text(context, path) for path in target.phase_documents}
    bodies = managed_bodies(target, snap, phases, texts, read_decisions(context, target))
    updates = []
    for path, (name, body) in bodies.items():
        if texts.get(path) is None:
            continue
        new = replace_block(texts[path], body, name)
        blocks(new)
        if new != texts[path]:
            updates.append(MechanicalUpdate(path, new, BLOCK_REASON))
    reviewed = set(history.acceptance.evidence.changed_paths) if history.acceptance is not None else set()
    return tuple(updates), frozenset(update.path for update in updates if update.path in reviewed)


def block_adoption(context, intent, writer) -> dict:
    """Solo bloques sobre documentos no revisados: su prosa es la de la base, ya adoptada o no."""
    adopt = {}
    for update in intent.mechanical:
        if update.reason != BLOCK_REASON or update.path in intent.reviewed_paths:
            continue
        blob = writer.read_blob(context, intent.base_revision, update.path)
        adopt[update.path] = [None if blob is None else hashlib.sha256(blob).hexdigest(), text_hash(update.content)]
    return adopt


def adopt_blocks(managed, session, run, adopt, commit):
    """En la transacción del resultado COMMITTED: la base adoptada avanza solo desde su hash anterior."""
    if not adopt:
        return
    phase = session.scalar(select(Phase).where(Phase.root == run.root, Phase.code == run.phase_id))
    if phase is None:
        return
    documents, changed = dict(phase.documents), {}
    for path, (before, after) in sorted(adopt.items()):
        if before is not None and documents.get(path) == before:
            documents[path] = changed[path] = after
    if changed:
        phase.documents = documents
        _event(managed, session, phase, 'managed_blocks_adopted', {'run_id': run.id, 'commit': commit,
                                                                  'documents': changed})


# --- edición documental confirmada ----------------------------------------------------------------


def _edit_phase(session, context, *, resume=False):
    root = str(context.root)
    phase = latest_phase(session, root)
    if phase is None:
        raise Conflict('Create or bootstrap a phase before editing documents through the harness')
    if PhaseRepository._root_pending(session, root) or phase.status in ('CHECKING', 'CLOSING'):
        raise Conflict('Checkout has unfinished work; edit documents at a stopped boundary')
    if not resume and unresolved(session, root):
        raise Conflict('A document intent awaits reconciliation; recover it first')
    from harness_local.storage.bootstrap import unresolved as bootstrap_unresolved
    if bootstrap_unresolved(session, root):
        raise Conflict('Bootstrap awaits completion or explicit recovery')
    if session.scalar(select(Authorization.id).where(Authorization.phase_id == phase.id,
                      Authorization.kind == 'batch', Authorization.status == 'ACTIVE')):
        raise Conflict('Revoke the active batch before editing documents')
    return phase


class DocumentsRepository:
    def __init__(self, managed):
        self.managed = managed

    def status(self, context, git=None) -> dict:
        target = require_layout(context)
        root = str(context.root)
        with Session(self.managed.engine) as session:
            phase = latest_phase(session, root)
            baseline = dict(phase.documents) if phase is not None else {}
            phase_view = None if phase is None else {'id': phase.id, 'code': phase.code, 'status': phase.status}
            open_intent = unresolved(session, root)
        paths = [*target.product_documents, *target.phase_documents]
        documents, texts = [], {}
        for path in paths:
            item = {'path': path, 'kind': 'phase' if path in target.phase_documents else 'product',
                    'exists': False, 'sha256': None, 'adopted_sha256': baseline.get(path),
                    'drift': False, 'blocks': [], 'error': None}
            try:
                text = read_text(context, path)
                if text is not None:
                    texts[path] = text
                    item.update(exists=True, sha256=text_hash(text), blocks=sorted(blocks(text)))
            except (ValueError, OSError, UnicodeError) as exc:
                item['error'] = str(exc)
            item['drift'] = path in baseline and baseline[path] != item['sha256']
            documents.append(item)
        uncommitted, git_error = None, None
        if git is not None:
            try:
                evidence = git.capture(context)
                uncommitted = [{'path': path, 'editable': target.editable(path)} for path in evidence.changed_paths]
            except (RuntimeError, ValueError, OSError) as exc:
                git_error = f'{type(exc).__name__}: {exc}'
        archive = []
        folder = context.path(target.archive_dir)
        if folder.is_dir() and not folder.is_symlink():
            for phase_dir in sorted(item for item in folder.iterdir() if item.is_dir() and not item.is_symlink()):
                archive.append({'path': f'{target.archive_dir}/{phase_dir.name}',
                                'files': sorted(item.name for item in phase_dir.iterdir() if item.is_file())})
        try:
            decisions = decision_index(read_decisions(context, target))
        except (ValueError, OSError, UnicodeError):
            decisions = []
        return {'layout': context.documents, 'phase': phase_view, 'documents': documents,
                'folders': [{'path': path, 'exists': context.path(path).is_dir()} for path in target.folders],
                'uncommitted': uncommitted, 'warnings': budget_warnings(target, texts), 'decisions': decisions,
                'archive': archive, 'unresolved_intent': open_intent, 'git_error': git_error}

    def read(self, context, path) -> dict:
        target = require_layout(context)
        archived = target.archived(path) and path.endswith('.md')
        if not (target.editable(path) or archived):
            raise LookupError('Unknown project document')
        text = read_text(context, path)
        if text is None:
            raise LookupError('Document does not exist in the checkout')
        return {'path': path, 'content': text, 'sha256': text_hash(text), 'editable': target.editable(path),
                'archived': archived, 'blocks': sorted(blocks(text))}

    def preview(self, context, git, *, source, changes):
        with Session(self.managed.engine) as session:
            phase = _edit_phase(session, context, resume=True)
            stored = pending(session, phase, 'document_edit')
            if stored is not None:
                return {**stored.request['preview'], 'resume_operation_id': stored.id}
        try:
            shown = preview_edit(context, git, source=source, changes=changes)
        except (ValueError, OSError, UnicodeError, RuntimeError) as exc:  # RuntimeError: captura/sellado Git
            raise Conflict(str(exc)) from exc
        return {**shown, 'resume_operation_id': None}

    def submit(self, context, *, key, versions, preview_sha256, reason, confirmed, git, source, changes,
               resume_operation_id=None):
        if confirmed is not True or not isinstance(reason, str) or not reason.strip():
            raise ValueError('Explicit confirmation of the exact diff and reason required')
        marker = freeze({'action': 'document_edit', 'root': str(context.root), 'preview_sha256': preview_sha256,
                         'reason': reason, 'confirmed': confirmed, 'resume_operation_id': resume_operation_id})
        with Session(self.managed.engine) as session:
            existing = self.managed._existing(session, key, marker)
            if existing:
                return _job(existing)
        try:
            shown = self.preview(context, git, source=source, changes=changes)
        except Conflict:
            with Session(self.managed.engine) as session:
                existing = self.managed._existing(session, key, marker)
                if existing:
                    return _job(existing)
            raise
        if shown['preview_sha256'] != preview_sha256 or shown['resume_operation_id'] != resume_operation_id:
            raise Conflict('Preview changed; review the exact diff again')
        assessment = self.managed.guard.assess(context.root)
        with self.managed._write() as session:
            existing = self.managed._existing(session, key, marker)
            if existing:
                return _job(existing)
            phase = _edit_phase(session, context, resume=resume_operation_id is not None)
            if resume_operation_id is not None:
                op = pending(session, phase, 'document_edit')
                if op is None or op.id != resume_operation_id:
                    raise Conflict('Only the exact interrupted edit intent can resume')
                job = _resume_job(self.managed, session, op, context, versions, key, marker, assessment, 'document_edit')
            else:
                job = self.managed._queue_new_run(session, assessment, context, versions, f'{phase.code}-DOCS',
                                                  phase.code, key, marker, purpose='document_edit')
                saved = {k: v for k, v in shown.items() if k != 'resume_operation_id'}
                op = Operation(id=str(uuid4()), phase_id=phase.id, kind='document_edit', run_id=job.run_id,
                               status='QUEUED', previous_status=phase.status, created_at=self.managed._now(),
                               request={'preview': saved, 'actor': actor(), 'reason': reason})
                session.add(op)
            _event(self.managed, session, phase, 'document_edit_queued', {
                'operation_id': op.id, 'run_id': job.run_id, 'job_id': job.id, 'preview_sha256': preview_sha256,
                'paths': [doc['path'] for doc in shown['documents']], 'actor': actor(), 'reason': reason})
            return job

    def request(self, run_id):
        with Session(self.managed.engine) as session:
            run = session.get(Run, run_id)
            op, _ = _operation(session, run)
            if op.kind != 'document_edit' or op.status != 'QUEUED':
                raise Conflict('Document edit requires its queued operation')
            return {**op.request, 'operation_id': op.id}


def _resume_job(managed, session, op, context, versions, key, marker, assessment, stage):
    run = session.get(Run, op.run_id)
    if run.context_json != context_snapshot(context) or run.versions_json != freeze(versions):
        raise Conflict('Frozen context/versions changed; restore the configured writer first')
    job = Job(idempotency_key=key, run_id=run.id, request_json=marker, status='QUEUED',
              created_at=managed._now(), activation_id=managed._admit(session, assessment))
    session.add(job)
    session.flush()
    run.status, run.stage = 'QUEUED', stage
    managed._event(session, run, 'job_queued', {'job_id': job.id, 'action': stage})
    op.status, op.finished_at = 'QUEUED', None
    return _job(job)


def record_intent(managed, session, run, intent):
    record_operation_intent(managed, session, run, intent, 'document_edit', lambda session, phase: True)


def settle(managed, session, run, outcome):
    op, phase = _operation(session, run)
    if op.status not in ('QUEUED', 'INTENT'):
        raise Conflict('Document edit already settled')
    if outcome['status'] == 'COMMITTED':
        verify_committed(op, outcome)
        shown = op.request['preview']
        observed_documents(run, shown)
        documents, adopted = dict(phase.documents), {}
        for doc in shown['documents']:
            if doc['path'] in documents and documents[doc['path']] == doc['before_sha256']:
                documents[doc['path']] = adopted[doc['path']] = doc['after_sha256']
        if adopted:
            phase.documents = documents
        outcome = {**outcome, 'adopted': adopted}
        run.status, run.stage = 'COMMITTED', 'committed'
    op.status, op.result, op.finished_at = outcome['status'], outcome, managed._now()
    _event(managed, session, phase, 'documents_edited' if outcome['status'] == 'COMMITTED' else 'document_edit_invalidated',
           {'operation_id': op.id, **outcome})


def abort(managed, session, run, status, reason):
    abort_operation(managed, session, run, status, reason, 'document_edit')

"""H3.3: autoridad SQLite de fases, serializada con la cola gestionada.

Las lecturas de disco (documentos) se hacen fuera de transacción y se comparan por
hash; checks y cierres son jobs bajo el lock del checkout. Las autorizaciones de lote
y de cierre son filas distintas, explícitas y auditadas: ninguna implica la otra, y
las concesiones de permisos H3.2 no intervienen. Ningún histórico se reescribe.
"""

from datetime import datetime, timedelta
import json
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness_local.core.engine.contracts import context_snapshot, freeze
from harness_local.core.engine.phases import CHECK_STATUS, digest, document_hashes, phase_definition
from harness_local.core.engine.serialization import load_history
from harness_local.storage.managed import Conflict, _job
from harness_local.storage.models import (
    ManagedCommitRow as Commit, ManagedJobRow as Job, ManagedRunRow as Run, PhaseAuthorizationRow as Authorization,
    PhaseEventRow as PhaseEvent, PhaseOperationRow as Operation, PhaseQuestionRow as Question, PhaseRow as Phase,
)
from harness_local.storage.permissions import actor

PENDING = ('QUEUED', 'ACTIVE', 'RECOVERY_REQUIRED')
CHECKABLE = ('ACTIVE', 'NEEDS_RECONCILIATION', 'READY_TO_CLOSE', 'BLOCKED')
RECONCILABLE = CHECKABLE


def _event(managed, session, phase, kind, payload):
    phase.version += 1
    phase.updated_at = managed._now()
    session.add(PhaseEvent(phase_id=phase.id, sequence=phase.version, kind=kind, recorded_at=phase.updated_at,
                           payload={**payload, 'status': phase.status}))


def _questions(session, phase_id):
    return session.scalars(select(Question).where(Question.phase_id == phase_id)
                           .order_by(Question.created_at, Question.id)).all()


def _open(rows):
    return [row for row in rows if row.status == 'OPEN']


def committed_tasks(session, phase):
    """Última aceptación COMMITTED de cada tarea declarada, solo runs de tarea de este checkout y fase."""
    result = {}
    for task in phase.definition['tasks']:
        row = session.execute(select(Commit.run_id, Commit.commit_sha).join(Run, Run.id == Commit.run_id).where(
            Run.root == phase.root, Run.phase_id == phase.code, Run.task_id == task, Run.purpose == 'task',
            Commit.status == 'COMMITTED').order_by(Commit.finished_at.desc(), Commit.operation_id).limit(1)).first()
        result[task] = None if row is None else {'run_id': row.run_id, 'commit': row.commit_sha}
    return result


def authority(session, phase):
    """Partes del vínculo READY que viven en SQLite."""
    rows = _questions(session, phase.id)
    sha = digest([[q.id, q.status, q.text, q.answer['text'] if q.answer else None] for q in rows])
    return {'definition_sha256': phase.definition_sha256, 'tasks': committed_tasks(session, phase),
            'questions_sha256': sha}, rows


def stale_reasons(parts, bound):
    return [f'{key} changed since READY' for key in sorted(parts) if parts[key] != bound.get(key)]


def _latest(session, phase_id, kind):
    return session.scalar(select(Operation).where(Operation.phase_id == phase_id, Operation.kind == kind)
                          .order_by(Operation.created_at.desc(), Operation.id.desc()).limit(1))


def _ready(session, phase):
    """READY vigente: el último check, mientras la fase siga en READY_TO_CLOSE/CLOSING."""
    if phase.status not in ('READY_TO_CLOSE', 'CLOSING'):
        return None
    check = _latest(session, phase.id, 'check')
    return check if check is not None and check.status == 'READY' else None


def question_view(row):
    return {key: getattr(row, key) for key in ('id', 'text', 'source', 'status', 'answer', 'version', 'created_at')}


def operation_view(row):
    return {key: getattr(row, key) for key in ('id', 'kind', 'run_id', 'status', 'previous_status', 'request',
                                                 'result', 'created_at', 'finished_at')}


def authorization_view(row, now, tasks=None):
    data = {key: getattr(row, key) for key in ('id', 'kind', 'status', 'scope', 'fingerprint', 'actor', 'reason',
                                                 'expires_at', 'created_at', 'closed', 'version')}
    effective = row.status
    if row.status == 'ACTIVE' and row.expires_at <= now:
        effective = 'EXPIRED'
    elif row.status == 'ACTIVE' and row.kind == 'batch' and tasks is not None and all(
            tasks.get(task) is not None for task in row.scope['tasks']):
        effective = 'COMPLETE'
    return {**data, 'effective_status': effective}


def _operation(session, run):
    op = session.scalar(select(Operation).where(Operation.run_id == run.id))
    if op is None:
        raise Conflict('Phase run without its phase operation')
    return op, session.get(Phase, op.phase_id)


def _invalidate(managed, session, phase, op, status, reason):
    auth = session.get(Authorization, op.request['authorization_id'])
    if auth.status == 'ACTIVE':
        auth.status, auth.version = status, auth.version + 1
        auth.closed = {'at': managed._now(), 'operation_id': op.id, 'reason': reason}


def settle(managed, session, run, outcome):
    """Resultado de check/cierre, atómico con el fin del job (llamado desde `finish`)."""
    op, phase = _operation(session, run)
    if op.status not in ('QUEUED', 'INTENT'):
        raise Conflict('Phase operation already settled')
    now = managed._now()
    parts, rows = authority(session, phase)
    if op.kind == 'check':
        outcome = dict(outcome)
        if outcome['verdict'] == 'READY' and stale_reasons(parts, outcome['binding']):
            outcome.update(verdict='NOT_READY', binding=None, binding_sha256=None,
                           reasons=['Phase authority changed during the check: '
                                    + ', '.join(stale_reasons(parts, outcome['binding']))])
        attempt = load_history(run.history_json).attempts
        for text in outcome['questions']:
            session.add(Question(id=str(uuid4()), phase_id=phase.id, text=text.strip(), status='OPEN', answer=None,
                                 version=1, created_at=now, source={
                                     'kind': 'phase_check', 'operation_id': op.id, 'run_id': run.id,
                                     'attempt_id': attempt[-1].request.id if attempt else None}))
        session.flush()
        op.status, op.result, op.finished_at = outcome['verdict'], outcome, now
        phase.status = CHECK_STATUS.get(outcome['verdict'], op.previous_status)
        if _open(_questions(session, phase.id)):
            phase.status = 'BLOCKED'
        _event(managed, session, phase, 'phase_checked', {'operation_id': op.id, 'run_id': run.id,
               'verdict': outcome['verdict'], 'reasons': outcome['reasons'],
               'binding_sha256': outcome['binding_sha256'], 'questions': outcome['questions']})
        return
    op.result, op.finished_at = outcome, now
    if outcome['status'] == 'CLOSED':
        # Preguntas y commits están excluidos durante CLOSING; un cambio aquí exige recuperación manual.
        changed = stale_reasons(parts, op.request['binding'])
        if changed or _open(rows):
            raise Conflict('Phase authority changed during close; recover manually with the recorded evidence')
        auth = session.get(Authorization, op.request['authorization_id'])
        auth.status, auth.version = 'CONSUMED', auth.version + 1
        auth.closed = {'at': now, 'operation_id': op.id, 'reason': 'Phase closed'}
        op.status, phase.status = 'CLOSED', 'CLOSED'
        _event(managed, session, phase, 'phase_closed', {'operation_id': op.id, 'run_id': run.id,
               'tag': outcome['tag'], 'binding_sha256': outcome['binding_sha256']})
    elif outcome['status'] == 'STALE':
        _invalidate(managed, session, phase, op, 'INVALIDATED', 'READY evidence is stale')
        op.status, phase.status = 'STALE', 'NEEDS_RECONCILIATION'
        _event(managed, session, phase, 'ready_invalidated', {'operation_id': op.id, 'reasons': outcome['reasons']})
    else:
        _invalidate(managed, session, phase, op, 'INVALIDATED', '; '.join(outcome['reasons']))
        op.status, phase.status = outcome['status'], op.previous_status
        _event(managed, session, phase, 'phase_close_failed', {'operation_id': op.id, 'status': outcome['status'],
               'reasons': outcome['reasons']})


def abort(managed, session, run, status, reason):
    """Job rechazado o escritor confirmado detenido: sin repetir efectos; el tag queda por conciliar."""
    op, phase = _operation(session, run)
    if op.status not in ('QUEUED', 'INTENT'):
        return
    intent = op.request.get('tag_intent')
    op.result = {'reason': reason, **({'tag_effect': 'uncertain', 'tag_intent': intent} if intent else {})}
    op.status, op.finished_at = status, managed._now()
    if op.kind == 'close':
        _invalidate(managed, session, phase, op, 'INVALIDATED', f'Close {status.lower()}: {reason}')
    phase.status = 'BLOCKED' if _open(_questions(session, phase.id)) else op.previous_status
    _event(managed, session, phase, 'phase_operation_aborted', {
        'operation_id': op.id, 'kind': op.kind, 'status': status, 'reason': reason, 'tag_intent': intent})


def record_tag_intent(managed, session, run, intent):
    op, phase = _operation(session, run)
    if op.kind != 'close' or op.status != 'QUEUED' or intent['operation_id'] != op.id:
        raise Conflict('Tag intent requires its queued close operation')
    op.request = {**op.request, 'tag_intent': intent}
    op.status = 'INTENT'
    _event(managed, session, phase, 'phase_tag_intent', {'operation_id': op.id, **intent})


class PhaseRepository:
    def __init__(self, managed):
        self.managed = managed

    def _phase(self, session, phase_id, expected, context=None):
        phase = session.get(Phase, phase_id)
        if phase is None:
            raise LookupError('Unknown managed phase')
        if context is not None and str(context.root) != phase.root:
            raise LookupError('Phase belongs to another checkout')
        if type(expected) is not int or phase.version != expected:
            raise Conflict('Phase changed; reload before acting')
        return phase

    @staticmethod
    def _root_pending(session, root):
        return session.scalar(select(Job.id).join(Run, Run.id == Job.run_id).where(
            Run.root == root, Job.status.in_(PENDING))) is not None

    # --- lecturas ---------------------------------------------------------------------

    def list(self, root):
        with Session(self.managed.engine) as session:
            rows = session.scalars(select(Phase).where(Phase.root == root).order_by(Phase.created_at, Phase.id)).all()
            return [{key: getattr(row, key) for key in ('id', 'code', 'status', 'version', 'created_at', 'updated_at')}
                    | {'objective': row.definition['objective']} for row in rows]

    def definition(self, phase_id):
        with Session(self.managed.engine) as session:
            phase = session.get(Phase, phase_id)
            if phase is None:
                raise LookupError('Unknown managed phase')
            return phase.root, phase.definition

    def get(self, phase_id, current_documents=None):
        """Proyección con acciones calculadas por el servidor; `current_documents` es una lectura de disco."""
        now = self.managed._now()
        with Session(self.managed.engine) as session:
            phase = session.get(Phase, phase_id)
            if phase is None:
                raise LookupError('Unknown managed phase')
            parts, rows = authority(session, phase)
            open_questions = _open(rows)
            auths = session.scalars(select(Authorization).where(Authorization.phase_id == phase.id)
                                    .order_by(Authorization.created_at, Authorization.id)).all()
            auth_views = [authorization_view(row, now, parts['tasks']) for row in auths]
            ops = session.scalars(select(Operation).where(Operation.phase_id == phase.id)
                                  .order_by(Operation.created_at, Operation.id)).all()
            ready = _ready(session, phase)
            ready_view = None if ready is None else {
                'operation_id': ready.id, 'binding': ready.result['binding'],
                'binding_sha256': ready.result['binding_sha256'],
                'stale_reasons': stale_reasons(parts, ready.result['binding'])}
            drift = None
            if current_documents is not None:
                drift = sorted(path for path, value in current_documents.items() if phase.documents.get(path) != value)
                if ready_view is not None and current_documents != ready.result['binding']['documents']:
                    ready_view['stale_reasons'].append('documents changed since READY')
            pending = self._root_pending(session, phase.root)
            active_batch = [a for a in auth_views if a['kind'] == 'batch' and a['effective_status'] == 'ACTIVE']
            actions = []
            if not open_questions and phase.status in CHECKABLE:
                actions.append('check')
            if phase.status in RECONCILABLE and not pending:
                actions.append('reconcile')
            if (phase.status == 'READY_TO_CLOSE' and ready_view and not ready_view['stale_reasons']
                    and not open_questions):
                actions.append('close')
            if phase.status not in ('CLOSED', 'CLOSING'):
                actions.append('question')
            if phase.status == 'ACTIVE' and not open_questions:
                actions.append('batch_next' if active_batch else 'authorize_batch')
            return {
                'id': phase.id, 'root': phase.root, 'code': phase.code, 'definition': phase.definition,
                'definition_sha256': phase.definition_sha256, 'status': phase.status, 'version': phase.version,
                'created_at': phase.created_at, 'updated_at': phase.updated_at,
                'documents': {'baseline': phase.documents, 'current': current_documents, 'drift': drift,
                              'current_sha256': digest(current_documents) if current_documents is not None else None},
                'tasks': parts['tasks'], 'questions': [question_view(q) for q in rows],
                'operations': [operation_view(op) for op in ops], 'authorizations': auth_views,
                'ready': ready_view, 'actions': actions}

    def events(self, phase_id, after=0, limit=100):
        if type(after) is not int or after < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError('Invalid phase event page')
        with Session(self.managed.engine) as session:
            if session.get(Phase, phase_id) is None:
                raise LookupError('Unknown managed phase')
            rows = session.scalars(select(PhaseEvent).where(PhaseEvent.phase_id == phase_id, PhaseEvent.sequence > after)
                                   .order_by(PhaseEvent.sequence).limit(limit + 1)).all()
            items = [{'id': r.id, 'sequence': r.sequence, 'kind': r.kind, 'recorded_at': r.recorded_at,
                      'payload': r.payload} for r in rows[:limit]]
            return {'items': items, 'cursor': items[-1]['sequence'] if items else after, 'has_more': len(rows) > limit}

    def snapshot(self, run_id):
        """Lectura para el job de fase; `settle` vuelve a comprobar la autoridad en su transacción."""
        with Session(self.managed.engine) as session:
            run = session.get(Run, run_id)
            op, phase = _operation(session, run)
            parts, rows = authority(session, phase)
            evidence = {}
            for task, item in parts['tasks'].items():
                review = None
                if item is not None:
                    cycles = load_history(session.get(Run, item['run_id']).history_json).cycles
                    review = cycles[-1].review_json if cycles else None
                evidence[task] = None if item is None else {**item, 'review_json': review}
            result = {'operation_id': op.id, 'kind': op.kind, 'definition': phase.definition,
                      'definition_sha256': phase.definition_sha256, 'documents': phase.documents,
                      'tasks': parts['tasks'], 'questions_sha256': parts['questions_sha256'],
                      'open_questions': [q.text for q in rows if q.status == 'OPEN'],
                      'answered_questions': [{'question': q.text, 'answer': q.answer['text']}
                                             for q in rows if q.status == 'ANSWERED'],
                      'task_evidence': evidence}
            if op.kind == 'close':
                auth = session.get(Authorization, op.request['authorization_id'])
                result['ready'] = {'binding': op.request['binding'], 'binding_sha256': op.request['binding_sha256']}
                result['authorization'] = {'id': auth.id, 'status': auth.status, 'expires_at': auth.expires_at,
                                           'usable': auth.status == 'ACTIVE' and auth.expires_at > self.managed._now()}
            return result

    # --- definición y documentos ---------------------------------------------------------

    def create(self, context, data):
        definition = phase_definition(context, data)
        documents = document_hashes(context, definition['documents'])
        with self.managed._write() as session:
            root = str(context.root)
            if session.scalar(select(Phase.id).where(Phase.root == root, Phase.code == definition['code'])):
                raise Conflict('Phase code already exists in this checkout')
            if session.scalar(select(Phase.id).where(Phase.root == root, Phase.status != 'CLOSED')):
                raise Conflict('Close the open phase of this checkout before creating another')
            now = self.managed._now()
            phase = Phase(id=str(uuid4()), root=root, code=definition['code'], definition=definition,
                          definition_sha256=digest(definition), documents=documents, status='ACTIVE', version=0,
                          created_at=now, updated_at=now)
            session.add(phase)
            session.flush()
            _event(self.managed, session, phase, 'phase_created', {
                'definition_sha256': phase.definition_sha256, 'documents': documents, 'actor': actor()})
            return phase.id

    def reconcile(self, context, phase_id, expected, *, documents_sha256, reason):
        """Adopción explícita de documentos cambiados (propuesta por hash), nunca mezcla silenciosa."""
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('Explicit reconciliation reason required')
        root, definition = self.definition(phase_id)
        if root != str(context.root):
            raise LookupError('Phase belongs to another checkout')
        current = document_hashes(context, definition['documents'])
        if digest(current) != documents_sha256:
            raise Conflict('Documents changed since they were reviewed; reload before reconciling')
        with self.managed._write() as session:
            phase = self._phase(session, phase_id, expected, context)
            if phase.status not in RECONCILABLE:
                raise Conflict('Reconciliation requires a phase without operations in progress')
            if self._root_pending(session, phase.root):
                raise Conflict('Checkout has unfinished jobs; reconcile at a stopped boundary')
            before = phase.documents
            now = self.managed._now()
            op = Operation(id=str(uuid4()), phase_id=phase.id, kind='reconcile', run_id=None, status='RECORDED',
                           previous_status=phase.status, created_at=now, finished_at=now,
                           request={'actor': actor(), 'reason': reason, 'documents_sha256': documents_sha256},
                           result={'before': before, 'after': current,
                                   'changed': sorted(p for p in current if before.get(p) != current[p])})
            session.add(op)
            phase.documents = current
            if phase.status in ('NEEDS_RECONCILIATION', 'READY_TO_CLOSE'):
                phase.status = 'ACTIVE'
            _event(self.managed, session, phase, 'documents_reconciled', {
                'operation_id': op.id, 'changed': op.result['changed'], 'reason': reason, 'actor': op.request['actor']})

    # --- preguntas bloqueantes ---------------------------------------------------------

    def raise_question(self, phase_id, expected, *, text):
        if not isinstance(text, str) or not text.strip():
            raise ValueError('Explicit question text required')
        with self.managed._write() as session:
            phase = self._phase(session, phase_id, expected)
            if phase.status in ('CLOSED', 'CLOSING'):
                raise Conflict('A closed or closing phase does not accept new questions')
            row = Question(id=str(uuid4()), phase_id=phase.id, text=text.strip(), status='OPEN', answer=None,
                           version=1, created_at=self.managed._now(), source={'kind': 'human', 'actor': actor()})
            session.add(row)
            if phase.status in ('ACTIVE', 'NEEDS_RECONCILIATION', 'READY_TO_CLOSE'):
                phase.status = 'BLOCKED'
            _event(self.managed, session, phase, 'question_raised', question_view(row))

    def answer(self, phase_id, question_id, expected, *, expected_question_version, answer):
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError('Explicit answer required')
        with self.managed._write() as session:
            phase = self._phase(session, phase_id, expected)
            row = session.get(Question, question_id)
            if row is None or row.phase_id != phase.id:
                raise LookupError('Unknown phase question')
            if phase.status in ('CLOSED', 'CLOSING'):
                raise Conflict('A closed or closing phase does not change its questions')
            if row.status != 'OPEN' or row.version != expected_question_version:
                raise Conflict('Question changed or was already answered')
            row.status, row.version = 'ANSWERED', row.version + 1
            row.answer = {'text': answer.strip(), 'actor': actor(), 'answered_at': self.managed._now()}
            session.flush()
            if phase.status == 'BLOCKED' and not _open(_questions(session, phase.id)):
                phase.status = 'ACTIVE'
            _event(self.managed, session, phase, 'question_answered', question_view(row))

    # --- operaciones por job -----------------------------------------------------------

    def submit_check(self, context, phase_id, expected, *, key, versions):
        request = freeze({'action': 'phase_check', 'phase_id': phase_id, 'expected_version': expected})
        assessment = self.managed.guard.assess(context.root)
        with self.managed._write() as session:
            existing = self.managed._existing(session, key, request)
            if existing:
                return _job(existing)
            phase = self._phase(session, phase_id, expected, context)
            if phase.status not in CHECKABLE:
                raise Conflict('Phase check requires a phase without operations in progress')
            if _open(_questions(session, phase.id)):
                raise Conflict('Pending blocking questions must be answered before checking the phase')
            job = self.managed._queue_new_run(session, assessment, context, versions, f'{phase.code}-CHECK',
                                              phase.code, key, request, purpose='phase_check')
            op = Operation(id=str(uuid4()), phase_id=phase.id, kind='check', run_id=job.run_id, status='QUEUED',
                           previous_status=phase.status, request={'job_id': job.id, 'actor': actor()},
                           created_at=self.managed._now())
            session.add(op)
            phase.status = 'CHECKING'
            _event(self.managed, session, phase, 'phase_check_queued',
                   {'operation_id': op.id, 'run_id': job.run_id, 'job_id': job.id})
            return job

    def submit_close(self, context, phase_id, expected, *, key, versions, binding_sha256, reason, ttl_seconds):
        """Autorización de cierre ligada al READY mostrado + job de cierre, en una transacción."""
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('Explicit close reason required')
        if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= 86400:
            raise ValueError('Validity must be between 1 second and 24 hours')
        request = freeze({'action': 'phase_close', 'phase_id': phase_id, 'expected_version': expected,
                          'binding_sha256': binding_sha256, 'reason': reason, 'ttl_seconds': ttl_seconds})
        assessment = self.managed.guard.assess(context.root)
        with self.managed._write() as session:
            existing = self.managed._existing(session, key, request)
            if existing:
                return _job(existing)
            phase = self._phase(session, phase_id, expected, context)
            ready = _ready(session, phase)
            if phase.status != 'READY_TO_CLOSE' or ready is None:
                raise Conflict('Only a READY_TO_CLOSE phase with a current READY check can be closed')
            if ready.result['binding_sha256'] != binding_sha256:
                raise Conflict('Close authorization must name the current READY evidence')
            parts, rows = authority(session, phase)
            if _open(rows):
                raise Conflict('Pending blocking questions prevent closing the phase')
            if session.scalar(select(Commit.operation_id).join(Run, Run.id == Commit.run_id).where(
                    Run.root == phase.root, Commit.status == 'INTENT')) is not None:
                raise Conflict('A commit operation of this checkout awaits reconciliation; reconcile it first')
            stale = stale_reasons(parts, ready.result['binding'])
            if stale:
                raise Conflict('READY review is stale: ' + ', '.join(stale) + '; check the phase again')
            now = self.managed._now()
            expires = (datetime.fromisoformat(now) + timedelta(seconds=ttl_seconds)).isoformat(timespec='microseconds')
            scope = {'check_operation_id': ready.id, 'binding_sha256': binding_sha256, 'tag': phase.definition['tag']}
            auth = Authorization(id=str(uuid4()), phase_id=phase.id, kind='close', status='ACTIVE', scope=scope,
                                 fingerprint=digest({'phase_id': phase.id, 'scope': scope, 'expires_at': expires}),
                                 actor=actor(), reason=reason.strip(), expires_at=expires, created_at=now,
                                 closed=None, version=1)
            session.add(auth)
            job = self.managed._queue_new_run(session, assessment, context, versions, f'{phase.code}-CLOSE',
                                              phase.code, key, request, purpose='phase_close')
            op = Operation(id=str(uuid4()), phase_id=phase.id, kind='close', run_id=job.run_id, status='QUEUED',
                           previous_status=phase.status, created_at=now, request={
                               'job_id': job.id, 'authorization_id': auth.id, 'check_operation_id': ready.id,
                               'binding': ready.result['binding'], 'binding_sha256': binding_sha256})
            session.add(op)
            phase.status = 'CLOSING'
            _event(self.managed, session, phase, 'close_authorized', authorization_view(auth, now))
            _event(self.managed, session, phase, 'phase_close_queued',
                   {'operation_id': op.id, 'run_id': job.run_id, 'job_id': job.id})
            return job

    # --- lote ----------------------------------------------------------------------

    def authorize_batch(self, phase_id, expected, *, tasks, ttl_seconds, reason):
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('Explicit batch reason required')
        if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= 86400:
            raise ValueError('Validity must be between 1 second and 24 hours')
        if (not isinstance(tasks, list) or not tasks or len(set(tasks)) != len(tasks)
                or not all(isinstance(t, str) for t in tasks)):
            raise ValueError('Explicit, distinct batch tasks required')
        with self.managed._write() as session:
            phase = self._phase(session, phase_id, expected)
            if not set(tasks) <= set(phase.definition['tasks']):
                raise ValueError('Batch tasks must belong to the frozen phase definition')
            if phase.status != 'ACTIVE' or _open(_questions(session, phase.id)):
                raise Conflict('Batch authorization requires an ACTIVE phase without pending questions')
            now = self.managed._now()
            live = session.scalars(select(Authorization).where(Authorization.phase_id == phase.id,
                                   Authorization.kind == 'batch', Authorization.status == 'ACTIVE')).all()
            if any(row.expires_at > now for row in live):
                raise Conflict('Revoke the active batch authorization before replacing it')
            expires = (datetime.fromisoformat(now) + timedelta(seconds=ttl_seconds)).isoformat(timespec='microseconds')
            scope = {'tasks': tasks}
            row = Authorization(id=str(uuid4()), phase_id=phase.id, kind='batch', status='ACTIVE', scope=scope,
                                fingerprint=digest({'phase_id': phase.id, 'scope': scope, 'expires_at': expires}),
                                actor=actor(), reason=reason.strip(), expires_at=expires, created_at=now,
                                closed=None, version=1)
            session.add(row)
            _event(self.managed, session, phase, 'batch_authorized', authorization_view(row, now))
            return row.id

    def revoke(self, phase_id, authorization_id, expected, *, reason):
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('Explicit revocation reason required')
        with self.managed._write() as session:
            phase = self._phase(session, phase_id, expected)
            row = session.get(Authorization, authorization_id)
            if row is None or row.phase_id != phase.id:
                raise LookupError('Unknown phase authorization')
            if row.kind != 'batch' or row.status != 'ACTIVE':
                raise Conflict('Only an active batch authorization can be revoked; close runs as its own job')
            row.status, row.version = 'REVOKED', row.version + 1
            row.closed = {'at': self.managed._now(), 'actor': actor(), 'reason': reason.strip()}
            _event(self.managed, session, phase, 'batch_revoked', authorization_view(row, self.managed._now()))

    def batch_next(self, context, phase_id, expected, *, key, versions, authorization_id, text):
        """Encola la siguiente tarea autorizada; no comprueba ni cierra la fase y no confirma commits."""
        if not isinstance(text, str) or not text.strip():
            raise ValueError('Explicit plan text required')
        assessment = self.managed.guard.assess(context.root)
        with self.managed._write() as session:
            prior = session.scalar(select(Job).where(Job.idempotency_key == key))
            phase = session.get(Phase, phase_id)
            if prior is not None:
                run = session.get(Run, prior.run_id)
                stored = json.loads(prior.request_json)
                if (phase is None or run.root != phase.root or run.phase_id != phase.code
                        or stored.get('text') != text or stored.get('versions_json') != freeze(versions)):
                    raise Conflict('Idempotency key already names a different action')
                return _job(prior)
            phase = self._phase(session, phase_id, expected, context)
            auth = session.get(Authorization, authorization_id)
            now = self.managed._now()
            if (auth is None or auth.phase_id != phase.id or auth.kind != 'batch' or auth.status != 'ACTIVE'
                    or auth.expires_at <= now):
                raise Conflict('A current batch authorization of this phase is required')
            if phase.status != 'ACTIVE' or _open(_questions(session, phase.id)):
                raise Conflict('The batch only advances an ACTIVE phase without pending questions')
            if self._root_pending(session, phase.root):
                raise Conflict('Checkout has unfinished jobs; the batch advances one task at a time')
            done = committed_tasks(session, phase)
            task = None
            for candidate in auth.scope['tasks']:
                if done[candidate] is not None:
                    continue
                if session.scalar(select(Run.id).where(Run.root == phase.root, Run.phase_id == phase.code,
                                                       Run.task_id == candidate, Run.purpose == 'task')):
                    raise Conflict(f'Task {candidate} has a run without committed acceptance; resolve it explicitly')
                task = candidate
                break
            if task is None:
                raise Conflict('Every authorized task already has a committed acceptance')
            request = freeze({'action': 'start', 'context_json': context_snapshot(context),
                              'versions_json': freeze(versions), 'task_id': task, 'phase_id': phase.code, 'text': text})
            job = self.managed._queue_new_run(session, assessment, context, versions, task, phase.code, key, request)
            _event(self.managed, session, phase, 'batch_task_queued', {
                'authorization_id': auth.id, 'task_id': task, 'run_id': job.run_id, 'job_id': job.id})
            return job

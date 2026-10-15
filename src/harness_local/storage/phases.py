"""H3.3/H3.4: autoridad SQLite de fases, serializada con la cola gestionada.

Las lecturas de disco (documentos) se hacen fuera de transacción y se comparan por
hash; checks y cierres son jobs bajo el lock del checkout. Las autorizaciones de lote
y de cierre son filas distintas, explícitas y auditadas: ninguna implica la otra, y
las concesiones de permisos H3.2 no intervienen. Ningún histórico se reescribe.

H3.4 (D033): un lote puede autorizar, de forma explícita, encadenar tareas y confirmar
el commit de cada aceptación elegible; lo conduce el supervisor paso a paso con claves
deterministas y se detiene en el primer bloqueo. Las definiciones se enmiendan como
versiones nuevas, la fase puede abandonarse y la reconciliación con agente es una
tarea normal con contrato determinista limitado a los documentos de la fase.
"""

from datetime import datetime, timedelta
import json
from uuid import uuid4

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from harness_local.core.engine.contracts import context_snapshot, freeze
from harness_local.core.engine.phases import CHECK_STATUS, TAG_KINDS, digest, document_hashes, phase_definition
from harness_local.core.engine.serialization import load_history, restore_context
from harness_local.storage.managed import Conflict, _job
from harness_local.storage.models import (
    ManagedCommitRow as Commit, ManagedJobRow as Job, ManagedRunRow as Run, PhaseAuthorizationRow as Authorization,
    PhaseDefinitionRow as Definition, PhaseEventRow as PhaseEvent, PhaseOperationRow as Operation,
    PhaseQuestionRow as Question, PhaseRow as Phase,
)
from harness_local.storage.permissions import actor

PENDING = ('QUEUED', 'ACTIVE', 'RECOVERY_REQUIRED')
CHECKABLE = ('ACTIVE', 'NEEDS_RECONCILIATION', 'READY_TO_CLOSE', 'BLOCKED')
RECONCILABLE = CHECKABLE
# Enmendar o abandonar: nunca con un check/cierre en curso ni sobre una fase terminal.
AMENDABLE = CHECKABLE
TERMINAL = ('CLOSED', 'ABANDONED')
# Run de tarea que terminó sin aceptación confirmable: no bloquea otra tarea de reconciliación.
FAILED_RUN = ('STOPPED', 'BLOCKED', 'REVISION_LIMIT', 'INTERRUPTED', 'REFUSED')
# Partes del alcance de un lote desatendido que no se proyectan (contenido grande o interno).
HIDDEN_SCOPE = ('text', 'context_json', 'versions_json')


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
    data['scope'] = {key: value for key, value in row.scope.items() if key not in HIDDEN_SCOPE}
    effective = row.status
    if row.status == 'ACTIVE' and row.expires_at <= now:
        effective = 'EXPIRED'
    elif row.status == 'ACTIVE' and row.kind == 'batch' and tasks is not None and all(
            tasks.get(task) is not None for task in row.scope['tasks']):
        effective = 'COMPLETE'
    return {**data, 'effective_status': effective}


def definition_view(row):
    return {key: getattr(row, key) for key in ('number', 'definition', 'definition_sha256', 'documents', 'origin',
                                                 'reason', 'actor', 'created_at')}


def _invalidate_batches(managed, session, phase, reason):
    """Una enmienda o un abandono invalida los lotes vigentes; los ya terminados se conservan."""
    rows = session.scalars(select(Authorization).where(Authorization.phase_id == phase.id,
                           Authorization.kind == 'batch', Authorization.status == 'ACTIVE')).all()
    for row in rows:
        row.status, row.version = 'INVALIDATED', row.version + 1
        row.closed = {'at': managed._now(), 'actor': actor(), 'reason': reason}
    return [row.id for row in rows]


def _open_reconcile_task(session, phase):
    """Tarea de reconciliación en curso, pendiente de commit o de adopción (una a la vez)."""
    op = _latest(session, phase.id, 'reconcile_task')
    if op is None or op.status != 'QUEUED':
        return None
    return None if session.get(Run, op.run_id).status in FAILED_RUN else op


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


def insert_phase(managed, session, root, definition, documents, source=None):
    """Inserción compartida: creación normal y adopción bootstrap en la transacción del job."""
    now = managed._now()
    phase = Phase(id=str(uuid4()), root=root, code=definition['code'], definition=definition,
                  definition_sha256=digest(definition), documents=documents, status='ACTIVE', version=0,
                  created_at=now, updated_at=now, definition_number=1)
    session.add(phase)
    session.flush()
    session.add(Definition(id=str(uuid4()), phase_id=phase.id, number=1, definition=definition,
                           definition_sha256=phase.definition_sha256, documents=documents, origin='created',
                           reason=None, actor=actor(), created_at=now))
    _event(managed, session, phase, 'phase_created', {
        'definition_sha256': phase.definition_sha256, 'documents': documents, 'actor': actor(),
        **({'source': source} if source else {})})
    return phase.id


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
        from harness_local.storage.documents import unresolved
        if unresolved(session, phase.root):
            raise Conflict('A document intent awaits reconciliation; recover it first')
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

    def by_code(self, root, code):
        """Id de la fase con ese código en el checkout; el código es único por raíz."""
        with Session(self.managed.engine) as session:
            phase_id = session.scalar(select(Phase.id).where(Phase.root == root, Phase.code == code))
        if phase_id is None:
            raise LookupError('Unknown managed phase')
        return phase_id

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
            op_views = []
            for op in ops:
                view = operation_view(op)
                if op.kind == 'reconcile_task' and op.status == 'QUEUED':
                    view['status'] = session.get(Run, op.run_id).status  # estado vivo del run normal
                op_views.append(view)
            definitions = session.scalars(select(Definition).where(Definition.phase_id == phase.id)
                                          .order_by(Definition.number)).all()
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
            reconcile_task = _open_reconcile_task(session, phase)
            actions = []
            if not open_questions and phase.status in CHECKABLE:
                actions.append('check')
            if phase.status in RECONCILABLE and not pending:
                actions.append('reconcile')
                if reconcile_task is None:
                    actions.append('reconcile_task')
            if (phase.status == 'READY_TO_CLOSE' and ready_view and not ready_view['stale_reasons']
                    and not open_questions):
                actions.append('close')
            if phase.status not in ('CLOSED', 'CLOSING', 'ABANDONED'):
                actions.append('question')
            if phase.status == 'ACTIVE' and not open_questions:
                if not active_batch:
                    actions.append('authorize_batch')
                elif not active_batch[0]['scope'].get('chain_commits'):
                    actions.append('batch_next')  # lote manual H3.3; el desatendido lo conduce el supervisor
            if phase.status in AMENDABLE and not pending:
                actions += ['amend', 'abandon']
            from harness_local.storage.documents import unresolved
            if unresolved(session, phase.root):
                actions = []
            # Mismo orden que `latest_phase`: creación y después id.
            successor = session.scalar(select(Phase.code).where(Phase.root == phase.root, or_(
                Phase.created_at > phase.created_at, and_(Phase.created_at == phase.created_at, Phase.id > phase.id)))
                .order_by(Phase.created_at, Phase.id).limit(1))
            return {
                'id': phase.id, 'root': phase.root, 'code': phase.code, 'definition': phase.definition,
                'definition_sha256': phase.definition_sha256, 'definition_number': phase.definition_number,
                'definitions': [definition_view(row) for row in definitions],
                'status': phase.status, 'version': phase.version,
                'created_at': phase.created_at, 'updated_at': phase.updated_at,
                'documents': {'baseline': phase.documents, 'current': current_documents, 'drift': drift,
                              'current_sha256': digest(current_documents) if current_documents is not None else None},
                'tasks': parts['tasks'], 'questions': [question_view(q) for q in rows],
                'operations': op_views, 'authorizations': auth_views,
                'ready': ready_view, 'actions': actions, 'successor': successor}

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
                result['tag_kind'] = op.request.get('tag_kind', 'lightweight')
                previous = session.scalars(select(Operation).where(
                    Operation.phase_id == phase.id, Operation.kind == 'close', Operation.id != op.id)
                    .order_by(Operation.created_at.desc(), Operation.id.desc())).all()
                result['previous_tag_intent'] = next((row.result['tag_intent'] for row in previous if row.result
                                                      and row.result.get('tag_effect') == 'uncertain'), None)
                result['authorization'] = {'id': auth.id, 'status': auth.status, 'expires_at': auth.expires_at,
                                           'usable': auth.status == 'ACTIVE' and auth.expires_at > self.managed._now()}
            return result

    # --- definición y documentos ---------------------------------------------------------

    def create(self, context, data):
        definition = phase_definition(context, data)
        documents = document_hashes(context, definition['documents'])
        with self.managed._write() as session:
            root = str(context.root)
            from harness_local.storage.documents import unresolved
            from harness_local.storage.bootstrap import unresolved as bootstrap_unresolved
            if self._root_pending(session, root) or unresolved(session, root) or bootstrap_unresolved(session, root):
                raise Conflict('Checkout has unfinished work; finish or reconcile it before creating a phase')
            if session.scalar(select(Phase.id).where(Phase.root == root, Phase.code == definition['code'])):
                raise Conflict('Phase code already exists in this checkout')
            if session.scalar(select(Phase.id).where(Phase.root == root, Phase.status.notin_(TERMINAL))):
                raise Conflict('Close or abandon the open phase of this checkout before creating another')
            return insert_phase(self.managed, session, root, definition, documents)

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
            source = None
            task_op = _open_reconcile_task(session, phase)
            if task_op is not None:
                # H3.4: la base se adopta después del commit de contenido exacto de la tarea de reconciliación.
                commit = session.scalar(select(Commit).where(Commit.run_id == task_op.run_id,
                                                             Commit.status == 'COMMITTED'))
                if commit is None:
                    raise Conflict('The reconciliation task must be reviewed and committed before adopting documents')
                source = {'operation_id': task_op.id, 'run_id': task_op.run_id, 'commit': commit.commit_sha}
            op = Operation(id=str(uuid4()), phase_id=phase.id, kind='reconcile', run_id=None, status='RECORDED',
                           previous_status=phase.status, created_at=now, finished_at=now,
                           request={'actor': actor(), 'reason': reason, 'documents_sha256': documents_sha256},
                           result={'before': before, 'after': current, 'source': source,
                                   'changed': sorted(p for p in current if before.get(p) != current[p])})
            session.add(op)
            if task_op is not None:
                task_op.status, task_op.finished_at = 'ADOPTED', now
                task_op.result = {'adopted_by': op.id, 'commit': source['commit'], 'documents_sha256': documents_sha256}
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
            if phase.status in ('CLOSED', 'CLOSING', 'ABANDONED'):
                raise Conflict('A closed, closing or abandoned phase does not accept new questions')
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
            if phase.status in ('CLOSED', 'CLOSING', 'ABANDONED'):
                raise Conflict('A closed, closing or abandoned phase does not change its questions')
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

    def submit_close(self, context, phase_id, expected, *, key, versions, binding_sha256, reason, ttl_seconds,
                     tag_kind='lightweight'):
        """Autorización de cierre ligada al READY mostrado + job de cierre, en una transacción.

        `tag_kind` lo fija el proyecto en el servidor (H3.4) y queda congelado en la autorización."""
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('Explicit close reason required')
        if tag_kind not in TAG_KINDS:
            raise ValueError('Unknown tag kind')
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
            scope = {'check_operation_id': ready.id, 'binding_sha256': binding_sha256, 'tag': phase.definition['tag'],
                     'tag_kind': tag_kind}
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
                               'binding': ready.result['binding'], 'binding_sha256': binding_sha256,
                               'tag_kind': tag_kind})
            session.add(op)
            phase.status = 'CLOSING'
            _event(self.managed, session, phase, 'close_authorized', authorization_view(auth, now))
            _event(self.managed, session, phase, 'phase_close_queued',
                   {'operation_id': op.id, 'run_id': job.run_id, 'job_id': job.id})
            return job

    # --- lote ----------------------------------------------------------------------

    def authorize_batch(self, phase_id, expected, *, tasks, ttl_seconds, reason, chain_commits=False, text=None,
                        context=None, versions=None):
        """`chain_commits` (H3.4, D033): alcance explícito «encadenar tareas y confirmar commits», con texto del
        plan, contexto y versiones congelados; sin él, lote manual H3.3 que solo encola por `batch_next`."""
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('Explicit batch reason required')
        if type(chain_commits) is not bool:
            raise ValueError('Explicit boolean chain_commits required')
        if chain_commits and (not isinstance(text, str) or not text.strip() or context is None
                              or not isinstance(versions, dict)):
            raise ValueError('An unattended batch freezes its plan text, context and versions')
        if not chain_commits and text is not None:
            raise ValueError('Only an unattended batch freezes a plan text')
        if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= 86400:
            raise ValueError('Validity must be between 1 second and 24 hours')
        if (not isinstance(tasks, list) or not tasks or len(set(tasks)) != len(tasks)
                or not all(isinstance(t, str) for t in tasks)):
            raise ValueError('Explicit, distinct batch tasks required')
        with self.managed._write() as session:
            phase = self._phase(session, phase_id, expected, context)
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
            if chain_commits:
                scope = {'tasks': tasks, 'chain_commits': True, 'plan_sha256': digest(text), 'text': text,
                         'definition_sha256': phase.definition_sha256, 'context_json': context_snapshot(context),
                         'versions_json': freeze(versions)}
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
            if auth.scope.get('chain_commits'):
                raise Conflict('An unattended batch is advanced by the supervisor, not by hand')
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

    # --- H3.4: enmienda, abandono y reconciliación con agente -----------------------------

    def amend(self, context, phase_id, expected, *, data, reason):
        """Nueva versión de la definición; la anterior se conserva. Invalida READY y lotes vigentes.

        El código no cambia (identifica los runs). Documentos nuevos se adoptan con su hash actual,
        registrado en la auditoría de la enmienda; los existentes conservan su base adoptada."""
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('Explicit amendment reason required')
        root, current = self.definition(phase_id)
        if root != str(context.root):
            raise LookupError('Phase belongs to another checkout')
        if not isinstance(data, dict) or 'code' in data:
            raise ValueError('An amendment keeps the phase code; send the other definition fields')
        definition = phase_definition(context, {**data, 'code': current['code']})
        observed = document_hashes(context, definition['documents'])
        sha = digest(definition)
        with self.managed._write() as session:
            phase = self._phase(session, phase_id, expected, context)
            if phase.status not in AMENDABLE:
                raise Conflict('Amendment requires a phase without operations in progress that is not closed')
            if self._root_pending(session, phase.root):
                raise Conflict('Checkout has unfinished jobs; amend at a stopped boundary')
            if sha == phase.definition_sha256:
                raise Conflict('The amendment does not change the definition')
            now = self.managed._now()
            added = [path for path in definition['documents'] if path not in phase.documents]
            documents = {path: phase.documents[path] if path in phase.documents else observed[path]
                         for path in definition['documents']}
            number = phase.definition_number + 1
            session.add(Definition(id=str(uuid4()), phase_id=phase.id, number=number, definition=definition,
                                   definition_sha256=sha, documents=documents, origin='amended',
                                   reason=reason.strip(), actor=actor(), created_at=now))
            invalidated = _invalidate_batches(self.managed, session, phase, f'Phase definition amended to version {number}')
            op = Operation(id=str(uuid4()), phase_id=phase.id, kind='amend', run_id=None, status='RECORDED',
                           previous_status=phase.status, created_at=now, finished_at=now,
                           request={'actor': actor(), 'reason': reason.strip(), 'definition_sha256': sha,
                                    'previous_sha256': phase.definition_sha256},
                           result={'previous_number': phase.definition_number, 'number': number,
                                   'added_documents': added,
                                   'removed_documents': [p for p in phase.documents if p not in documents],
                                   'invalidated_authorizations': invalidated,
                                   'ready_invalidated': phase.status == 'READY_TO_CLOSE'})
            session.add(op)
            phase.definition, phase.definition_sha256, phase.definition_number = definition, sha, number
            phase.documents = documents
            if phase.status == 'READY_TO_CLOSE':
                phase.status = 'ACTIVE'  # READY nunca sobrevive a otra definición
            _event(self.managed, session, phase, 'definition_amended', {
                'operation_id': op.id, 'number': number, 'definition_sha256': sha, 'reason': reason.strip(),
                'invalidated_authorizations': invalidated, 'actor': op.request['actor']})

    def abandon(self, phase_id, expected, *, reason, context=None):
        """Estado terminal explícito y auditado; no edita documentos ni toca Git."""
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('Explicit abandonment reason required')
        with self.managed._write() as session:
            phase = self._phase(session, phase_id, expected, context)
            if phase.status not in AMENDABLE:
                raise Conflict('Only a phase without operations in progress that is not closed can be abandoned')
            if self._root_pending(session, phase.root):
                raise Conflict('Checkout has unfinished jobs; abandon at a stopped boundary')
            now = self.managed._now()
            invalidated = _invalidate_batches(self.managed, session, phase, 'Phase abandoned')
            op = Operation(id=str(uuid4()), phase_id=phase.id, kind='abandon', run_id=None, status='RECORDED',
                           previous_status=phase.status, created_at=now, finished_at=now,
                           request={'actor': actor(), 'reason': reason.strip()},
                           result={'invalidated_authorizations': invalidated,
                                   'open_questions': [q.id for q in _open(_questions(session, phase.id))]})
            session.add(op)
            phase.status = 'ABANDONED'
            _event(self.managed, session, phase, 'phase_abandoned', {
                'operation_id': op.id, 'reason': reason.strip(), 'invalidated_authorizations': invalidated,
                'actor': op.request['actor']})

    def submit_reconcile_task(self, context, phase_id, expected, *, key, versions):
        """Tarea normal con contrato determinista (plantilla `reconcile-phase`) limitado a los documentos.

        Se ejecuta, revisa y confirma por el flujo de tareas; después se adopta la base por hash."""
        from harness_local.core.engine.contracts import task_contract
        from harness_local.core.engine.evidence import matches
        from harness_local.core.engine.prompts import digest as text_digest, render
        from harness_local.storage.prompts import PromptRepository
        template = PromptRepository(self.managed.engine).catalog(context)['reconcile-phase']
        marker = {'kind': 'reconcile_task', 'phase_id': phase_id, 'expected_version': expected}
        assessment = self.managed.guard.assess(context.root)
        with self.managed._write() as session:
            prior = session.scalar(select(Job).where(Job.idempotency_key == key))
            if prior is not None:
                if json.loads(prior.request_json).get('phase_operation') != marker:
                    raise Conflict('Idempotency key already names a different action')
                return _job(prior)
            phase = self._phase(session, phase_id, expected, context)
            if phase.status not in RECONCILABLE:
                raise Conflict('Reconciliation requires a phase without operations in progress')
            if self._root_pending(session, phase.root):
                raise Conflict('Checkout has unfinished jobs; reconcile at a stopped boundary')
            if _open_reconcile_task(session, phase) is not None:
                raise Conflict('A reconciliation task of this phase is in progress or awaits commit/adoption')
            documents = phase.definition['documents']
            protected = context.profile.protected_paths
            if any(matches(path, protected) for path in documents):
                raise Conflict('A phase document is protected by the profile; reconcile it by hand')
            number = 1 + len(session.scalars(select(Operation.id).where(
                Operation.phase_id == phase.id, Operation.kind == 'reconcile_task')).all())
            task_id = f'{phase.code}-RECONCILE-{number}'
            check = _latest(session, phase.id, 'check')
            evidence = {'phase': phase.definition, 'definition_sha256': phase.definition_sha256,
                        'baseline_documents': phase.documents, 'tasks': committed_tasks(session, phase),
                        'latest_check': None if check is None else {
                            'operation_id': check.id, 'status': check.status,
                            'reasons': (check.result or {}).get('reasons'), 'review': (check.result or {}).get('result')}}
            instructions = render(template, {'PHASE_ID': phase.code, 'REVIEW_JSON': freeze(evidence)})
            required = (check.result or {}).get('reasons', []) if check is not None and check.status == 'REVISE' else []
            policy = context.policy
            from harness_local.core.engine.documents import BUDGETS, layout
            target = layout(context)
            allowed, constraints = list(documents), ['Documentation only: no code, tests, plans state, commits or tags.']
            if target is not None:
                # D072: la reconciliación compacta STATE y pone al día los documentos de producto y decisiones;
                # los bloques gestionados (también el índice de DECISIONS, D088) y el archivo siguen siendo del harness.
                allowed = list(dict.fromkeys(list(documents) + list(target.product_documents)
                                             + [f'{folder}/**' for folder in target.folders]))
                constraints += [
                    'Never edit inside harness-local managed blocks; Harness Local regenerates them at commit.',
                    f'Rewrite the "## Base acumulada" section of {target.state} as a compact description of what '
                    f'exists and works, by area, within {BUDGETS["base"]} bytes, linking archived summaries.',
                    f'Summarize the phase in the "## Fase activa" section of {target.state} and note what the next '
                    'session must know.',
                    f'Record durable decisions as new "## DNNN — title" sections of {target.decisions}, each with '
                    'a first "Estado:" line and the next free number; supersede, never delete or renumber.']
            contract = task_contract(context, {
                'task_id': task_id, 'phase_id': phase.code, 'title': f'Reconcile phase {phase.code} documents',
                'objective': f'Make the phase {phase.code} documents describe accepted reality.',
                'business_context': '', 'allowed_paths': allowed,
                'forbidden_paths': list(dict.fromkeys(protected)),
                'acceptance_criteria': [f'Only these {"phase " if target is None else ""}documents change: {", ".join(allowed)}.',
                                        *[f'Required by the phase review: {item}' for item in required],
                                        'Unresolved product decisions are recorded as questions, not invented.'],
                'implementation_constraints': constraints,
                'validation_commands': [], 'documentation_refs': list(documents), 'deliverables': list(documents),
                'risk_notes': [], 'executor_prompt': instructions,
                'executor_selection': {'model': policy.executor_models[0], 'effort': policy.executor_efforts[0],
                                       'reason': 'First explicit executor selection of the policy (deterministic contract)'},
                'contract_source': f'reconcile-phase template {template.id} (deterministic, no agent planner)',
                'prompt_template': {'name': template.name, 'id': template.id, 'sha256': template.sha256,
                                    'rendered_sha256': text_digest(instructions)},
            }, task_id, phase.code)
            request = freeze({'action': 'start', 'context_json': context_snapshot(context),
                              'versions_json': freeze(versions), 'task_id': task_id, 'phase_id': phase.code,
                              'text': f'Deterministic reconcile-phase contract for {phase.code}',
                              'contract_json': contract, 'phase_operation': marker})
            job = self.managed._queue_new_run(session, assessment, context, versions, task_id, phase.code, key, request)
            op = Operation(id=str(uuid4()), phase_id=phase.id, kind='reconcile_task', run_id=job.run_id,
                           status='QUEUED', previous_status=phase.status, created_at=self.managed._now(),
                           request={'job_id': job.id, 'actor': actor(), 'task_id': task_id,
                                    'contract_sha256': text_digest(contract), 'allowed_paths': allowed,
                                    'template': {'id': template.id, 'sha256': template.sha256}})
            session.add(op)
            _event(self.managed, session, phase, 'reconcile_task_queued', {
                'operation_id': op.id, 'run_id': job.run_id, 'job_id': job.id, 'task_id': task_id})
            return job


# --- H3.4: conductor del lote desatendido ----------------------------------------------------


def _batch_stop(managed, session, phase, auth, status, reason):
    auth.status, auth.version = status, auth.version + 1
    auth.closed = {'at': managed._now(), 'reason': reason, 'by': 'batch_driver'}
    _event(managed, session, phase, 'batch_stopped', {'authorization_id': auth.id, 'status': status, 'reason': reason})


def _batch_step(managed, session, auth_id, context, assessment):
    """Un paso derivado del estado: encola una tarea o un commit, espera, termina o se detiene."""
    auth = session.get(Authorization, auth_id)
    if auth is None or auth.status != 'ACTIVE':
        return
    phase, scope = session.get(Phase, auth.phase_id), auth.scope

    def stop(status, reason):
        _batch_stop(managed, session, phase, auth, status, reason)
    if auth.expires_at <= managed._now():
        return stop('EXPIRED', 'Batch authorization expired; nothing further is queued')
    if phase.definition_sha256 != scope['definition_sha256']:
        return stop('INVALIDATED', 'Phase definition changed since the batch was authorized')
    if _open(_questions(session, phase.id)):
        return stop('STOPPED', 'Pending blocking questions')
    if phase.status != 'ACTIVE':
        return stop('STOPPED', f'Phase is {phase.status}; the batch never checks or closes it')
    states = session.scalars(select(Job.status).join(Run, Run.id == Job.run_id).where(
        Run.root == phase.root, Job.status.in_(PENDING))).all()
    if 'RECOVERY_REQUIRED' in states:
        return stop('STOPPED', 'A job of this checkout requires explicit recovery; uncertain effects are not repeated')
    if states:
        return  # una acción escritora cada vez: espera a que termine
    done = committed_tasks(session, phase)
    for task in scope['tasks']:
        if done.get(task) is not None:
            continue
        start_key = f'batch:{auth.id}:start:{task}'
        start = session.scalar(select(Job).where(Job.idempotency_key == start_key))
        if start is None:
            if session.scalar(select(Run.id).where(Run.root == phase.root, Run.phase_id == phase.code,
                                                   Run.task_id == task, Run.purpose == 'task')):
                return stop('STOPPED', f'Task {task} has a run outside this batch without committed acceptance')
            request = freeze({'action': 'start', 'context_json': scope['context_json'],
                              'versions_json': scope['versions_json'], 'task_id': task, 'phase_id': phase.code,
                              'text': scope['text']})
            job = managed._queue_new_run(session, assessment, context, json.loads(scope['versions_json']), task,
                                         phase.code, start_key, request)
            _event(managed, session, phase, 'batch_task_queued', {
                'authorization_id': auth.id, 'task_id': task, 'run_id': job.run_id, 'job_id': job.id,
                'unattended': True})
            return
        run = session.get(Run, start.run_id)
        commit_key = f'batch:{auth.id}:commit:{run.id}'
        if session.scalar(select(Job.id).where(Job.idempotency_key == commit_key)) is None:
            history = load_history(run.history_json)
            if history.status == 'acceptance_ready' and history.acceptance is not None and history.acceptance.eligible:
                request = freeze({'action': 'commit', 'run_id': run.id, 'expected_version': run.version,
                                  'mechanical': []})
                job = managed._queue_commit(session, run, commit_key, request, (), assessment)
                _event(managed, session, phase, 'batch_commit_queued', {
                    'authorization_id': auth.id, 'task_id': task, 'run_id': run.id, 'job_id': job.id})
                return
            detail = history.stop.reason if history.stop else history.status
            return stop('STOPPED', f'Task {task} stopped without an eligible acceptance ({run.status}): {detail}')
        return stop('STOPPED', f'The commit of task {task} did not complete ({run.status}); '
                               'evidence invalidated or uncertain, reconcile it explicitly')
    auth.status, auth.version = 'COMPLETED', auth.version + 1
    auth.closed = {'at': managed._now(), 'reason': 'Every authorized task has a committed acceptance',
                   'by': 'batch_driver'}
    _event(managed, session, phase, 'batch_completed', {'authorization_id': auth.id})


def advance_batches(managed):
    """Llamado por el supervisor antes de reclamar. Idempotente: claves deterministas por lote y paso."""
    with Session(managed.engine) as session:
        live = [row.id for row in session.scalars(select(Authorization).where(
            Authorization.kind == 'batch', Authorization.status == 'ACTIVE')
            .order_by(Authorization.created_at, Authorization.id)) if row.scope.get('chain_commits')]
        contexts = {auth_id: session.get(Authorization, auth_id).scope['context_json'] for auth_id in live}
    for auth_id in live:
        try:
            context = restore_context(contexts[auth_id])
            assessment = managed.guard.assess(context.root)  # lectura de disco fuera de la transacción
            with managed._write() as session:
                _batch_step(managed, session, auth_id, context, assessment)
        except (ValueError, LookupError, OSError) as exc:  # Conflict deriva de ValueError
            with managed._write() as session:
                auth = session.get(Authorization, auth_id)
                if auth.status == 'ACTIVE':
                    _batch_stop(managed, session, session.get(Phase, auth.phase_id), auth, 'STOPPED',
                                f'{type(exc).__name__}: {exc}')

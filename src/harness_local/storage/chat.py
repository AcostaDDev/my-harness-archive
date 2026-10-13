"""H4.1: autoridad SQLite del chat contextual, serializada con la cola gestionada.

La conversación vive separada del flujo de ejecución. Cada mensaje congela, en la transacción que
encola su turno, el mensaje y el contexto explícito: proyecto, fase, documentos (contenido acotado
con hash) y evidencias de runs seleccionadas, más los turnos anteriores. El turno es un run
`chat` con job bajo el lock del checkout: reutiliza supervisor, guardia de modo, cuarentena y
persistencia de intentos. Una caída deja el turno con resultado desconocido y nunca se reintenta.

Las propuestas no ejecutan nada. Aceptar una exige confirmación explícita, la versión observada y
el hash exacto mostrado, y encola una tarea normal (planificador, ejecutor, revisión y commit)
vinculada a la propuesta. El chat no concede permisos ni fija contratos.
"""

import hashlib
import json
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from harness_local.core.engine.chat import TASK_ID, digest, task_text
from harness_local.core.engine.contracts import context_snapshot, freeze
from harness_local.core.engine.serialization import load_history
from harness_local.storage.managed import Conflict, _job
from harness_local.storage.models import (
    ChatConversationRow as Conversation, ChatProposalRow as Proposal, ChatTurnRow as Turn,
    ManagedCommitRow as Commit, ManagedJobRow as Job, ManagedRunRow as Run, PhaseRow as Phase,
)
from harness_local.storage.permissions import actor

MAX_DOCUMENTS = 8
MAX_DOCUMENT_BYTES = 64 * 1024
MAX_RUNS = 10
MAX_PREVIOUS_TURNS = 10
MAX_MESSAGE = 20_000


def read_documents(context, paths) -> list[dict]:
    """Lectura de disco fuera de transacción: contenido acotado, con hash y tamaño del archivo completo."""
    result = []
    for path in paths:
        item = context.path(path)
        if item.is_symlink() or (item.exists() and not item.is_file()):
            raise ValueError(f'Chat document {path} must be a regular file')
        if not item.exists():
            result.append({'path': path, 'sha256': None, 'size': None, 'content': None, 'truncated': False})
            continue
        data = item.read_bytes()
        result.append({'path': path, 'sha256': hashlib.sha256(data).hexdigest(), 'size': len(data),
                       'content': data[:MAX_DOCUMENT_BYTES].decode('utf-8', errors='replace'),
                       'truncated': len(data) > MAX_DOCUMENT_BYTES})
    return result


def _distinct(values, name, limit):
    if (not isinstance(values, list) or len(values) > limit or len(set(values)) != len(values)
            or not all(isinstance(v, str) and v.strip() for v in values)):
        raise ValueError(f'Chat {name} must be a list of at most {limit} distinct, non-empty texts')
    return values


def _run_evidence(session, root, run_id):
    run = session.get(Run, run_id)
    if run is None or run.root != root:
        raise LookupError('A selected run does not belong to this checkout')
    history = load_history(run.history_json)
    task = json.loads(history.task_json) if history.task_json else None
    review = history.cycles[-1].review_json if history.cycles else None
    commit = session.scalar(select(Commit.commit_sha).where(Commit.run_id == run.id, Commit.status == 'COMMITTED'))
    return {'run_id': run.id, 'purpose': run.purpose, 'task_id': run.task_id, 'phase_id': run.phase_id,
            'status': run.status, 'contract': None if task is None else {
                key: task.get(key) for key in ('title', 'objective', 'allowed_paths', 'acceptance_criteria',
                                               'validation_commands')},
            'stop': None if history.stop is None else {'stage': history.stop.stage, 'reason': history.stop.reason},
            'review': None if review is None else json.loads(review),
            'acceptance': None if history.acceptance is None else {
                'eligible': history.acceptance.eligible, 'changed_paths': list(history.acceptance.evidence.changed_paths)},
            'commit': commit}


def _phase_context(session, phase):
    from harness_local.storage.phases import _open, _questions, committed_tasks
    return {'id': phase.id, 'code': phase.code, 'status': phase.status, 'definition': phase.definition,
            'definition_number': phase.definition_number, 'baseline_documents': phase.documents,
            'tasks': committed_tasks(session, phase),
            'open_questions': [q.text for q in _open(_questions(session, phase.id))]}


def _touch(managed, conversation):
    conversation.version += 1
    conversation.updated_at = managed._now()


def _turn(session, run):
    turn = session.scalar(select(Turn).where(Turn.run_id == run.id))
    if turn is None:
        raise Conflict('Chat run without its turn')
    return turn, session.get(Conversation, turn.conversation_id)


def settle(managed, session, run, outcome):
    """Resultado del turno, atómico con el fin del job (llamado desde `finish`)."""
    turn, conversation = _turn(session, run)
    if turn.status != 'QUEUED':
        raise Conflict('Chat turn already settled')
    attempts = load_history(run.history_json).attempts
    turn.status, turn.finished_at = outcome['status'], managed._now()
    turn.result = {**outcome, 'attempt_id': attempts[-1].request.id if attempts else None}
    if outcome['status'] == 'ANSWERED':
        number = session.scalar(select(func.max(Proposal.number)).where(
            Proposal.conversation_id == conversation.id)) or 0
        for item in outcome['result']['proposals']:
            number += 1
            session.add(Proposal(id=str(uuid4()), conversation_id=conversation.id, turn_id=turn.id, number=number,
                                 status='PROPOSED', proposal=item, proposal_sha256=digest(item), run_id=None,
                                 decision=None, version=1, created_at=turn.finished_at))
    _touch(managed, conversation)


def abort(managed, session, run, status, reason):
    """Escritor confirmado detenido (resultado desconocido) o job rechazado: nunca se reintenta solo."""
    turn, conversation = _turn(session, run)
    if turn.status != 'QUEUED':
        return
    turn.status = 'UNKNOWN' if status == 'INTERRUPTED' else 'REFUSED'
    turn.finished_at = managed._now()
    turn.result = {'status': turn.status, 'reasons': [reason], 'result': None, 'checkout': None}
    _touch(managed, conversation)


class ChatRepository:
    def __init__(self, managed):
        self.managed = managed

    def _conversation(self, session, conversation_id, expected=None, context=None):
        row = session.get(Conversation, conversation_id)
        if row is None:
            raise LookupError('Unknown chat conversation')
        if context is not None and row.root != str(context.root):
            raise LookupError('Conversation belongs to another checkout')
        if expected is not None and (type(expected) is not int or row.version != expected):
            raise Conflict('Conversation changed; reload before acting')
        return row

    # --- lecturas ---------------------------------------------------------------------

    def root(self, conversation_id):
        with Session(self.managed.engine) as session:
            return self._conversation(session, conversation_id).root

    def list(self, root):
        with Session(self.managed.engine) as session:
            rows = session.scalars(select(Conversation).where(Conversation.root == root)
                                   .order_by(Conversation.created_at, Conversation.id)).all()
            result = []
            for row in rows:
                phase = session.get(Phase, row.phase_id) if row.phase_id else None
                turns = session.scalar(select(func.count()).select_from(Turn).where(Turn.conversation_id == row.id))
                result.append({'id': row.id, 'title': row.title, 'phase_id': row.phase_id,
                               'phase_code': phase.code if phase else None, 'turns': turns, 'version': row.version,
                               'created_at': row.created_at, 'updated_at': row.updated_at})
            return result

    def get(self, conversation_id):
        """Proyección con estado vivo de los runs vinculados y acciones calculadas por el servidor."""
        with Session(self.managed.engine) as session:
            row = self._conversation(session, conversation_id)
            phase = session.get(Phase, row.phase_id) if row.phase_id else None
            turns = session.scalars(select(Turn).where(Turn.conversation_id == row.id).order_by(Turn.number)).all()
            proposals = session.scalars(select(Proposal).where(Proposal.conversation_id == row.id)
                                        .order_by(Proposal.number)).all()
            numbers = {turn.id: turn.number for turn in turns}
            turn_views = []
            for turn in turns:
                context = turn.request['context']
                turn_views.append({
                    'id': turn.id, 'number': turn.number, 'status': turn.status, 'run_id': turn.run_id,
                    'run_status': session.get(Run, turn.run_id).status, 'message': turn.message,
                    'documents': [{key: item[key] for key in ('path', 'sha256', 'size', 'truncated')}
                                  for item in context['documents']],
                    'run_ids': [item['run_id'] for item in context['runs']],
                    'phase_code': context['phase']['code'] if context['phase'] else None,
                    'previous_turns': len(context['previous_turns']),
                    'context_sha256': turn.request['context_sha256'], 'request_sha256': turn.request_sha256,
                    'result': turn.result, 'actor': turn.actor, 'created_at': turn.created_at,
                    'finished_at': turn.finished_at})
            proposal_views = []
            for item in proposals:
                run = session.get(Run, item.run_id) if item.run_id else None
                commit = None if run is None else session.scalar(select(Commit.commit_sha).where(
                    Commit.run_id == run.id, Commit.status == 'COMMITTED'))
                proposal_views.append({
                    'id': item.id, 'number': item.number, 'turn_id': item.turn_id, 'turn_number': numbers[item.turn_id],
                    'status': item.status, 'proposal': item.proposal, 'proposal_sha256': item.proposal_sha256,
                    'run_id': item.run_id, 'run': None if run is None else {
                        'task_id': run.task_id, 'phase_id': run.phase_id, 'status': run.status, 'commit': commit},
                    'decision': item.decision, 'version': item.version, 'created_at': item.created_at,
                    'actions': ['accept', 'dismiss'] if item.status == 'PROPOSED' else []})
            pending = any(turn.status == 'QUEUED' for turn in turns)
            return {'id': row.id, 'root': row.root, 'title': row.title,
                    'phase': None if phase is None else {'id': phase.id, 'code': phase.code, 'status': phase.status},
                    'actor': row.actor, 'version': row.version, 'created_at': row.created_at,
                    'updated_at': row.updated_at, 'turns': turn_views, 'proposals': proposal_views,
                    'actions': [] if pending else ['message']}

    def snapshot(self, run_id):
        """Petición congelada para el job del turno."""
        with Session(self.managed.engine) as session:
            run = session.get(Run, run_id)
            if run is None:
                raise LookupError('Unknown managed run')
            turn, _ = _turn(session, run)
            return {'turn_id': turn.id, 'message': turn.message, 'context': turn.request['context'],
                    'context_sha256': turn.request['context_sha256']}

    # --- conversación y turnos ---------------------------------------------------------

    def create(self, context, *, title, phase_id=None):
        if not isinstance(title, str) or not title.strip() or len(title) > 200:
            raise ValueError('Conversation title must contain 1–200 characters')
        with self.managed._write() as session:
            if phase_id is not None:
                phase = session.get(Phase, phase_id)
                if phase is None or phase.root != str(context.root):
                    raise LookupError('Unknown phase of this checkout')
            now = self.managed._now()
            row = Conversation(id=str(uuid4()), root=str(context.root), title=title.strip(), phase_id=phase_id,
                               actor=actor(), version=0, created_at=now, updated_at=now)
            session.add(row)
            return row.id

    def submit_message(self, context, conversation_id, expected, *, key, versions, text, documents=None, run_ids=None):
        """Congela mensaje y contexto explícito en la transacción que encola el turno."""
        if not isinstance(text, str) or not text.strip() or len(text) > MAX_MESSAGE:
            raise ValueError(f'Chat message must contain 1–{MAX_MESSAGE} characters')
        run_ids = _distinct([] if run_ids is None else run_ids, 'runs', MAX_RUNS)
        request = freeze({'action': 'chat_turn', 'conversation_id': conversation_id, 'expected_version': expected,
                          'text': text, 'documents': documents, 'run_ids': run_ids})
        with Session(self.managed.engine) as session:
            row = self._conversation(session, conversation_id, context=context)
            phase = session.get(Phase, row.phase_id) if row.phase_id else None
            selected = documents if documents is not None else (
                list(phase.definition['documents']) if phase else [context.state_file, context.next_steps_file])
        observed = read_documents(context, _distinct(selected, 'documents', MAX_DOCUMENTS))
        assessment = self.managed.guard.assess(context.root)
        with self.managed._write() as session:
            existing = self.managed._existing(session, key, request)
            if existing:
                return _job(existing)
            conversation = self._conversation(session, conversation_id, expected, context)
            if session.scalar(select(Turn.id).where(Turn.conversation_id == conversation.id, Turn.status == 'QUEUED')):
                raise Conflict('The previous turn of this conversation is still pending')
            phase = session.get(Phase, conversation.phase_id) if conversation.phase_id else None
            previous = session.scalars(select(Turn).where(Turn.conversation_id == conversation.id)
                                       .order_by(Turn.number.desc()).limit(MAX_PREVIOUS_TURNS)).all()
            history = []
            for turn in reversed(previous):
                answered = turn.status == 'ANSWERED'
                history.append({'number': turn.number, 'status': turn.status, 'message': turn.message,
                                'answer': turn.result['result']['answer'] if answered else None,
                                'proposals': [{'number': p.number, 'title': p.proposal['title'], 'status': p.status}
                                              for p in session.scalars(select(Proposal).where(Proposal.turn_id == turn.id)
                                                                       .order_by(Proposal.number))]})
            number = 1 + (session.scalar(select(func.max(Turn.number)).where(
                Turn.conversation_id == conversation.id)) or 0)
            frozen = {'project': {'root': str(context.root), 'profile': context.profile.name,
                                  'state_file': context.state_file, 'next_steps_file': context.next_steps_file},
                      'conversation': {'id': conversation.id, 'title': conversation.title, 'turn': number},
                      'phase': None if phase is None else _phase_context(session, phase),
                      'documents': observed, 'runs': [_run_evidence(session, conversation.root, r) for r in run_ids],
                      'previous_turns': history}
            job = self.managed._queue_new_run(session, assessment, context, versions,
                                              f'CHAT-{conversation.id[:8]}-{number}', phase.code if phase else 'CHAT',
                                              key, request, purpose='chat')
            context_sha256 = digest(frozen)
            session.add(Turn(id=str(uuid4()), conversation_id=conversation.id, number=number, run_id=job.run_id,
                             status='QUEUED', message=text, request={'context': frozen, 'context_sha256': context_sha256},
                             request_sha256=digest({'message': text, 'context_sha256': context_sha256}),
                             result=None, actor=actor(), created_at=self.managed._now()))
            _touch(self.managed, conversation)
            return job

    # --- propuestas ------------------------------------------------------------------

    def accept(self, context, conversation_id, proposal_id, expected, *, key, versions, proposal_sha256, task_id,
               phase_id, confirmed):
        """Confirmación explícita → tarea normal vinculada; sin confirmación no se encola nada."""
        if confirmed is not True:
            raise ValueError('Accepting a proposal requires explicit confirmation; nothing was queued')
        if not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id):
            raise ValueError("Task id must be 1–120 letters, digits, '.', '_' or '-'")
        if not isinstance(phase_id, str) or not TASK_ID.fullmatch(phase_id):
            raise ValueError("Phase id must be 1–120 letters, digits, '.', '_' or '-'")
        marker = {'kind': 'chat_proposal', 'conversation_id': conversation_id, 'proposal_id': proposal_id,
                  'proposal_sha256': proposal_sha256, 'expected_version': expected, 'task_id': task_id,
                  'phase_id': phase_id}
        assessment = self.managed.guard.assess(context.root)
        with self.managed._write() as session:
            prior = session.scalar(select(Job).where(Job.idempotency_key == key))
            if prior is not None:
                if json.loads(prior.request_json).get('chat_proposal') != marker:
                    raise Conflict('Idempotency key already names a different action')
                return _job(prior)
            conversation = self._conversation(session, conversation_id, expected, context)
            proposal = session.get(Proposal, proposal_id)
            if proposal is None or proposal.conversation_id != conversation.id:
                raise LookupError('Unknown proposal of this conversation')
            if proposal.status != 'PROPOSED':
                raise Conflict(f'The proposal is already {proposal.status.lower()}')
            if proposal.proposal_sha256 != proposal_sha256:
                raise Conflict('Accept the exact proposal that was shown; reload it')
            turn = session.get(Turn, proposal.turn_id)
            text = task_text(proposal.proposal, task_id, {
                'conversation_id': conversation.id, 'turn_number': turn.number, 'proposal_id': proposal.id,
                'proposal_sha256': proposal.proposal_sha256})
            request = freeze({'action': 'start', 'context_json': context_snapshot(context),
                              'versions_json': freeze(versions), 'task_id': task_id, 'phase_id': phase_id,
                              'text': text, 'chat_proposal': marker})
            job = self.managed._queue_new_run(session, assessment, context, versions, task_id, phase_id, key, request)
            proposal.status, proposal.run_id, proposal.version = 'ACCEPTED', job.run_id, proposal.version + 1
            proposal.decision = {'decision': 'accept', 'actor': actor(), 'at': self.managed._now(), 'task_id': task_id,
                                 'phase_id': phase_id, 'job_id': job.id, 'text_sha256': digest(text)}
            _touch(self.managed, conversation)
            return job

    def dismiss(self, conversation_id, proposal_id, expected, *, reason):
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('Explicit dismissal reason required')
        with self.managed._write() as session:
            conversation = self._conversation(session, conversation_id, expected)
            proposal = session.get(Proposal, proposal_id)
            if proposal is None or proposal.conversation_id != conversation.id:
                raise LookupError('Unknown proposal of this conversation')
            if proposal.status != 'PROPOSED':
                raise Conflict(f'The proposal is already {proposal.status.lower()}')
            proposal.status, proposal.version = 'DISMISSED', proposal.version + 1
            proposal.decision = {'decision': 'dismiss', 'actor': actor(), 'at': self.managed._now(),
                                 'reason': reason.strip()}
            _touch(self.managed, conversation)

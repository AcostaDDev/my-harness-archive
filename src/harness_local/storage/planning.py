"""H6.5: autoridad SQLite de las conversaciones de definición y de planificación de fase.

Reutiliza la infraestructura del chat (D035): cada mensaje congela, en la transacción que encola su
turno, el mensaje y el contexto explícito; el turno es un run (`definition` o `phase_planning`) con job
bajo el lock del checkout, con supervisor, guardia de modo, cuarentena y persistencia de intentos.
Una caída deja el turno con resultado desconocido y nunca se reintenta.

Definición: el brief y los borradores de la carpeta destino (con su hash) forman el contexto. El agente
nunca escribe. Aplicar una propuesta confirmada escribe el borrador con CAS sobre el hash que leyó el
turno; una edición del usuario entre medias es un conflicto y no se sobrescribe. Las ediciones del
usuario (en disco o por API) se detectan por hash en el turno siguiente. La aceptación es la vista
previa del bootstrap D037 con la plantilla v2 (`storage/bootstrap.py`).

Planificación: propone NEXT_STEPS para la fase activa sin tareas (o la siguiente en conversaciones anteriores).
La confirmación del plan escribe los documentos y versiona la definición; el agente nunca produce efectos.
"""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from uuid import uuid4

from harness_local.core.engine.chat import digest
from harness_local.core.engine.contracts import freeze
from harness_local.core.engine.definition import (
    MAX_CONTEXT_DRAFT_BYTES, acceptance, allowed_draft, allowed_drafts_view, brief as brief_payload,
    default_documents, definition_layout, text_hash,
)
from harness_local.core.engine.document_ops import read_text
from harness_local.core.engine.documents import base_section, parse_roadmap, require_layout, skeleton
from harness_local.core.engine.serialization import load_history
from harness_local.storage.chat import MAX_MESSAGE, MAX_PREVIOUS_TURNS, read_documents
from harness_local.storage.managed import Conflict, _job, existing_creation
from harness_local.storage.models import (
    ManagedRunRow as Run, PhaseRow as Phase, PlanningConversationRow as Conversation,
    PlanningProposalRow as Proposal, PlanningTurnRow as Turn, ProjectBootstrapRow as Bootstrap,
)
from harness_local.storage.permissions import actor

KINDS = ('definition', 'phase_planning')


def _touch(managed, conversation):
    conversation.version += 1
    conversation.updated_at = managed._now()


def _turn(session, run):
    turn = session.scalar(select(Turn).where(Turn.run_id == run.id))
    if turn is None:
        raise Conflict('Planning run without its turn')
    return turn, session.get(Conversation, turn.conversation_id)


def current_questions(session, conversation) -> tuple[list[dict], list[str]]:
    """Preguntas y pendientes del último turno respondido, con los aplazamientos explícitos."""
    turn = session.scalar(select(Turn).where(Turn.conversation_id == conversation.id, Turn.status == 'ANSWERED')
                          .order_by(Turn.number.desc()).limit(1))
    if turn is None:
        return [], []
    result = turn.result['result']
    return ([{**q, 'deferred': conversation.deferred.get(q['id'])} for q in result['questions']],
            list(result['pending']))


def _bootstrapped(session, root) -> bool:
    return session.scalar(select(Bootstrap.id).where(Bootstrap.root == root)) is not None


def settle(managed, session, run, outcome):
    """Resultado del turno, atómico con el fin del job; las propuestas nuevas sustituyen a las pendientes."""
    turn, conversation = _turn(session, run)
    if turn.status != 'QUEUED':
        raise Conflict('Planning turn already settled')
    attempts = load_history(run.history_json).attempts
    turn.status, turn.finished_at = outcome['status'], managed._now()
    result = outcome['result']
    stored = result
    if outcome['status'] == 'ANSWERED' and conversation.kind == 'definition':
        # El contenido íntegro vive en cada propuesta; el turno conserva ruta, motivo y hash.
        stored = {**result, 'drafts': [{'path': d['path'], 'reason': d['reason'], 'content_sha256': text_hash(d['content'])}
                                       for d in result['drafts']]}
    elif outcome['status'] == 'ANSWERED' and result['plan'] is not None:
        stored = {**result, 'plan': {'reason': result['plan']['reason'],
                                     'content_sha256': text_hash(result['plan']['content'])}}
    turn.result = {**outcome, 'result': stored, 'attempt_id': attempts[-1].request.id if attempts else None}
    if outcome['status'] == 'ANSWERED':
        if conversation.kind == 'definition':
            bases = {item['path']: item['sha256'] for item in turn.request['context']['drafts']}
            # Solo un turno respondido «ve» los borradores: uno fallido vuelve a mostrar las ediciones al siguiente.
            conversation.known = dict(bases)
            items = [('draft', d['path'], d['content'], d['reason'], bases.get(d['path'])) for d in result['drafts']]
        else:
            plan = result['plan']
            items = [] if plan is None else [('plan', None, plan['content'], plan['reason'], None)]
        number = session.scalar(select(func.max(Proposal.number)).where(
            Proposal.conversation_id == conversation.id)) or 0
        for kind, path, content, reason, base in items:
            older = select(Proposal).where(Proposal.conversation_id == conversation.id, Proposal.kind == kind,
                                           Proposal.status == 'PROPOSED')
            older = older.where(Proposal.path == path) if path is not None else older.where(Proposal.path.is_(None))
            for row in session.scalars(older):
                row.status, row.version = 'SUPERSEDED', row.version + 1
                row.decision = {'decision': 'superseded', 'by_turn': turn.number, 'at': turn.finished_at}
            number += 1
            content_sha256 = text_hash(content)
            session.add(Proposal(
                id=str(uuid4()), conversation_id=conversation.id, turn_id=turn.id, number=number, kind=kind, path=path,
                content=content, reason=reason, content_sha256=content_sha256, base_sha256=base,
                proposal_sha256=digest({'kind': kind, 'path': path, 'content_sha256': content_sha256,
                                        'base_sha256': base, 'reason': reason, 'turn_id': turn.id}),
                status='PROPOSED', decision=None, version=1, created_at=turn.finished_at))
    _touch(managed, conversation)


def abort(managed, session, run, status, reason):
    """Escritor confirmado detenido (resultado desconocido) o job rechazado: nunca se reintenta solo."""
    turn, conversation = _turn(session, run)
    if turn.status != 'QUEUED':
        return
    turn.status = 'UNKNOWN' if status == 'INTERRUPTED' else 'REFUSED'
    turn.finished_at = managed._now()
    turn.result = {'status': turn.status, 'reasons': [reason], 'result': None, 'observed': None}
    _touch(managed, conversation)


def lock_for_bootstrap(session, shown):
    """En la transacción que encola el bootstrap v2: la conversación sigue siendo la revisada."""
    definition = shown['definition']
    conversation = session.get(Conversation, definition['conversation_id'])
    if conversation is None or conversation.version != definition['conversation_version']:
        raise Conflict('The definition conversation changed since the preview; review it again')
    if session.scalar(select(Turn.id).where(Turn.conversation_id == conversation.id, Turn.status == 'QUEUED')):
        raise Conflict('A definition turn is pending; accept after it settles')


def definition_acceptance(managed, context, data, writer) -> dict:
    """Vista previa de la aceptación v2: snapshot SQLite + borradores del destino, sin efectos."""
    if not isinstance(data, dict) or set(data) != {'conversation_id'}:
        raise ValueError('Projects with documents = "v2" are created through the definition conversation (H6.5)')
    inspection = writer.inspect_definition(context, texts=True)
    texts = inspection.pop('texts')
    with Session(managed.engine) as session:
        conversation = session.get(Conversation, data['conversation_id'])
        if conversation is None or conversation.root != str(context.root) or conversation.kind != 'definition':
            raise LookupError('Unknown definition conversation of this project')
        if session.scalar(select(Turn.id).where(Turn.conversation_id == conversation.id, Turn.status == 'QUEUED')):
            raise Conflict('A definition turn is pending; accept after it settles')
        snapshot = PlanningRepository._record(session, conversation)
    shown = acceptance(context, snapshot, inspection, texts)
    return {**shown, 'target': inspection, 'ready': not shown['blockers']}


class PlanningRepository:
    def __init__(self, managed):
        self.managed = managed

    def _conversation(self, session, conversation_id, expected=None, context=None):
        row = session.get(Conversation, conversation_id)
        if row is None:
            raise LookupError('Unknown planning conversation')
        if context is not None and row.root != str(context.root):
            raise LookupError('Conversation belongs to another checkout')
        if expected is not None and (type(expected) is not int or row.version != expected):
            raise Conflict('Conversation changed; reload before acting')
        return row

    @staticmethod
    def _record(session, conversation) -> dict:
        """Lo que la aceptación resume en DEFINITION.md: datos de SQLite, deterministas."""
        turns = session.scalars(select(Turn).where(Turn.conversation_id == conversation.id).order_by(Turn.number)).all()
        questions, pending = current_questions(session, conversation)
        return {'id': conversation.id, 'title': conversation.title, 'version': conversation.version,
                'brief': conversation.brief, 'log': list(conversation.log), 'questions': questions, 'pending': pending,
                'turns': [{'number': t.number, 'status': t.status, 'message': t.message,
                           'answer': (t.result or {}).get('result', {}).get('answer') if t.status == 'ANSWERED' else None,
                           'drafts': (t.result['result']['drafts'] if t.status == 'ANSWERED' else [])}
                          for t in turns]}

    # --- lecturas ---------------------------------------------------------------------

    def root(self, conversation_id):
        with Session(self.managed.engine) as session:
            return self._conversation(session, conversation_id).root

    def list(self, root):
        with Session(self.managed.engine) as session:
            rows = session.scalars(select(Conversation).where(Conversation.root == str(root))
                                   .order_by(Conversation.created_at, Conversation.id)).all()
            result = []
            for row in rows:
                phase = session.get(Phase, row.phase_id) if row.phase_id else None
                turns = session.scalar(select(func.count()).select_from(Turn).where(Turn.conversation_id == row.id))
                result.append({'id': row.id, 'kind': row.kind, 'title': row.title, 'phase_id': row.phase_id,
                               'phase_code': phase.code if phase else None, 'turns': turns, 'version': row.version,
                               'created_at': row.created_at, 'updated_at': row.updated_at})
            return result

    def get(self, conversation_id):
        """Proyección con estado vivo de los runs y acciones calculadas por el servidor."""
        with Session(self.managed.engine) as session:
            row = self._conversation(session, conversation_id)
            phase = session.get(Phase, row.phase_id) if row.phase_id else None
            turns = session.scalars(select(Turn).where(Turn.conversation_id == row.id).order_by(Turn.number)).all()
            proposals = session.scalars(select(Proposal).where(Proposal.conversation_id == row.id)
                                        .order_by(Proposal.number)).all()
            numbers = {turn.id: turn.number for turn in turns}
            pending = any(turn.status == 'QUEUED' for turn in turns)
            created = row.kind == 'definition' and _bootstrapped(session, row.root)
            open_ = not pending and not created
            questions, items = current_questions(session, row)
            turn_views = [{
                'id': turn.id, 'number': turn.number, 'status': turn.status, 'run_id': turn.run_id,
                'run_status': session.get(Run, turn.run_id).status, 'message': turn.message,
                'context_sha256': turn.request['context_sha256'], 'request_sha256': turn.request_sha256,
                'drafts': [{key: item[key] for key in ('path', 'sha256', 'size')}
                           for item in turn.request['context'].get('drafts', [])],
                'user_edits': turn.request['context'].get('user_edits', []),
                'documents': [{key: item[key] for key in ('path', 'sha256', 'size', 'truncated')}
                              for item in turn.request['context'].get('documents', [])],
                'result': turn.result, 'actor': turn.actor, 'created_at': turn.created_at,
                'finished_at': turn.finished_at} for turn in turns]
            proposal_views = []
            for item in proposals:
                actions = []
                if item.status == 'PROPOSED' and open_:
                    actions = ['apply', 'dismiss'] if item.kind == 'draft' else ['dismiss']
                proposal_views.append({
                    'id': item.id, 'number': item.number, 'turn_id': item.turn_id, 'turn_number': numbers[item.turn_id],
                    'kind': item.kind, 'path': item.path, 'content': item.content, 'reason': item.reason,
                    'content_sha256': item.content_sha256, 'base_sha256': item.base_sha256,
                    'proposal_sha256': item.proposal_sha256, 'status': item.status, 'decision': item.decision,
                    'version': item.version, 'created_at': item.created_at, 'actions': actions})
            actions = []
            if open_:
                actions = ['message'] + (['edit_draft', 'defer_question', 'accept'] if row.kind == 'definition' else [])
            return {'id': row.id, 'root': row.root, 'kind': row.kind, 'title': row.title,
                    'phase': None if phase is None else {'id': phase.id, 'code': phase.code, 'status': phase.status},
                    'brief': None if row.brief is None else {k: row.brief[k] for k in ('sha256', 'size')},
                    'known': row.known, 'log': row.log, 'questions': questions, 'pending': items,
                    'actor': row.actor, 'version': row.version, 'created_at': row.created_at,
                    'updated_at': row.updated_at, 'created': created, 'turns': turn_views,
                    'proposals': proposal_views, 'actions': actions}

    def brief(self, conversation_id):
        with Session(self.managed.engine) as session:
            row = self._conversation(session, conversation_id)
            if row.brief is None:
                raise LookupError('This conversation has no brief')
            return dict(row.brief)

    def drafts(self, context, conversation_id, writer):
        """Borradores del destino frente a lo que conoce el harness: las diferencias son del usuario."""
        target = definition_layout(context)
        with Session(self.managed.engine) as session:
            row = self._conversation(session, conversation_id, context=context)
            if row.kind != 'definition':
                raise Conflict('Only a definition conversation has drafts on disk')
            known = dict(row.known)
            if _bootstrapped(session, row.root):
                return {'created': True, 'allowed': allowed_drafts_view(target), 'drafts': [], 'foreign': [],
                        'foreign_truncated': False, 'invalid': [], 'import_required': False}
        inspection = writer.inspect_definition(context)
        drafts = [{'path': path, 'sha256': inspection['drafts'].get(path), 'known_sha256': known.get(path),
                   'user_edited': inspection['drafts'].get(path) != known.get(path)}
                  for path in sorted(set(inspection['drafts']) | {p for p, v in known.items() if v is not None})]
        return {'created': False, 'allowed': allowed_drafts_view(target), 'drafts': drafts,
                'foreign': inspection['foreign'], 'foreign_truncated': inspection['foreign_truncated'],
                'invalid': inspection['invalid'], 'import_required': inspection['import_required']}

    def draft(self, context, conversation_id, path, writer):
        """H6.2 E4: contenido de un borrador por la misma inspección que usan el turno y la CAS."""
        target = definition_layout(context)
        if not allowed_draft(target, path):
            raise LookupError(f'{path} is not an allowed definition draft')
        with Session(self.managed.engine) as session:
            row = self._conversation(session, conversation_id, context=context)
            if row.kind != 'definition':
                raise Conflict('Only a definition conversation has drafts on disk')
            if _bootstrapped(session, row.root):
                raise Conflict('The project was already created; read its documents instead')
            known = row.known.get(path)
        inspection = writer.inspect_definition(context, texts=True)
        if path in inspection['invalid']:
            raise Conflict(f'{path} is not a valid draft (UTF-8 without NUL, not executable, at most 512 KiB)')
        if path not in inspection['texts']:
            raise LookupError(f'{path} does not exist in the target folder')
        return {'path': path, 'content': inspection['texts'][path], 'sha256': inspection['drafts'][path],
                'known_sha256': known}

    def snapshot(self, run_id):
        """Petición congelada para el job del turno."""
        with Session(self.managed.engine) as session:
            run = session.get(Run, run_id)
            if run is None:
                raise LookupError('Unknown managed run')
            turn, conversation = _turn(session, run)
            return {'kind': conversation.kind, 'turn_id': turn.id, 'message': turn.message,
                    'context': turn.request['context'], 'context_sha256': turn.request['context_sha256'],
                    'observed': turn.request.get('observed')}

    # --- conversación ------------------------------------------------------------------

    def create(self, context, *, kind, title, brief=None, phase_id=None, writer=None, key=None):
        """`key` (API): un reintento con la misma petición devuelve la misma conversación antes de reevaluar el
        destino, que el alta original puede haber cambiado (proyecto ya creado, fase ya transicionada)."""
        request = digest({'action': 'planning_conversation', 'root': str(context.root), 'kind': kind, 'title': title,
                          'brief': brief, 'phase_id': phase_id})
        if key is not None:
            with Session(self.managed.engine) as session:
                if found := existing_creation(session, Conversation, key, request):
                    return found
        if kind not in KINDS:
            raise ValueError('Conversation kind must be definition or phase_planning')
        if not isinstance(title, str) or not title.strip() or len(title) > 200:
            raise ValueError('Conversation title must contain 1–200 characters')
        if kind == 'definition':
            definition_layout(context)
            frozen = brief_payload(brief)
            if phase_id is not None:
                raise ValueError('A definition conversation has no phase')
            if writer.inspect_definition(context)['import_required']:
                raise Conflict('The target belongs to a Git repository or contains .git: use the import flow')
        else:
            require_layout(context)
            if brief is not None:
                raise ValueError('A phase planning conversation has no brief')
            frozen = None
        try:
            with self.managed._write() as session:
                if key is not None and (found := existing_creation(session, Conversation, key, request)):
                    return found
                if kind == 'definition':
                    from harness_local.storage.bootstrap import BootstrapRepository
                    if _bootstrapped(session, str(context.root)):
                        raise Conflict('The project was already created; plan its phases instead')
                    BootstrapRepository._empty_authority(session, str(context.root))
                else:
                    phase = session.get(Phase, phase_id) if isinstance(phase_id, str) else None
                    if phase is None or phase.root != str(context.root):
                        raise LookupError('Unknown phase of this checkout')
                    from harness_local.storage.documents import latest_phase
                    if latest_phase(session, phase.root).id != phase.id:
                        raise Conflict('Plan from the latest phase of the checkout')
                now = self.managed._now()
                row = Conversation(id=str(uuid4()), root=str(context.root), kind=kind, phase_id=phase_id,
                                   title=title.strip(), brief=frozen, known={}, deferred={}, log=[], actor=actor(),
                                   version=0, created_at=now, updated_at=now, idempotency_key=key,
                                   request_sha256=request if key is not None else None)
                session.add(row)
                session.flush()
                return row.id
        except IntegrityError as exc:
            raise Conflict('This project already has a definition conversation') from exc

    # --- turnos ------------------------------------------------------------------------

    def submit_message(self, context, conversation_id, expected, *, key, versions, text, writer=None):
        """Congela mensaje y contexto en la transacción que encola el turno."""
        if not isinstance(text, str) or not text.strip() or len(text) > MAX_MESSAGE:
            raise ValueError(f'Planning message must contain 1–{MAX_MESSAGE} characters')
        request = freeze({'action': 'planning_turn', 'conversation_id': conversation_id, 'expected_version': expected,
                          'text': text})
        with Session(self.managed.engine) as session:
            existing = self.managed._existing(session, key, request)
            if existing:
                return _job(existing)
            conversation = self._conversation(session, conversation_id, context=context)
            kind = conversation.kind
            if kind == 'definition' and _bootstrapped(session, conversation.root):
                raise Conflict('The project was already created from this definition')
        observed, prepared = None, {}
        if kind == 'definition':
            target = definition_layout(context)
            inspection = writer.inspect_definition(context, texts=True)
            texts = inspection.pop('texts')
            if inspection['import_required']:
                raise Conflict('The target belongs to a Git repository or contains .git: use the import flow')
            if sum(len(value.encode('utf-8')) for value in texts.values()) > MAX_CONTEXT_DRAFT_BYTES:
                raise ValueError('Drafts exceed the 2 MiB a turn can freeze; shorten or remove some drafts')
            observed = inspection
            prepared = {'drafts': [{'path': path, 'sha256': inspection['drafts'][path],
                                    'size': len(texts[path].encode('utf-8')), 'content': texts[path]}
                                   for path in sorted(texts)],
                        'foreign': inspection['foreign'], 'invalid': inspection['invalid'],
                        'allowed': allowed_drafts_view(target)}
        else:
            target = require_layout(context)
            roadmap, state = read_text(context, target.roadmap), read_text(context, target.state)
            prepared = {'documents': read_documents(context, [target.roadmap, target.state, target.specification,
                                                              target.architecture, target.decisions, target.next_steps,
                                                              target.ddbb_diagram, *target.instructions]),
                        'entries': parse_roadmap(roadmap) if roadmap is not None else [],
                        'base': base_section(state) if state is not None else None}
        assessment = self.managed.guard.assess(context.root)
        with self.managed._write() as session:
            existing = self.managed._existing(session, key, request)
            if existing:
                return _job(existing)
            conversation = self._conversation(session, conversation_id, expected, context)
            if session.scalar(select(Turn.id).where(Turn.conversation_id == conversation.id, Turn.status == 'QUEUED')):
                raise Conflict('The previous turn of this conversation is still pending')
            previous = session.scalars(select(Turn).where(Turn.conversation_id == conversation.id)
                                       .order_by(Turn.number.desc()).limit(MAX_PREVIOUS_TURNS)).all()
            history = []
            for turn in reversed(previous):
                answered = turn.status == 'ANSWERED'
                history.append({'number': turn.number, 'status': turn.status, 'message': turn.message,
                                'answer': turn.result['result']['answer'] if answered else None,
                                'proposals': [{'number': p.number, 'kind': p.kind, 'path': p.path, 'status': p.status}
                                              for p in session.scalars(select(Proposal).where(Proposal.turn_id == turn.id)
                                                                       .order_by(Proposal.number))]})
            number = 1 + (session.scalar(select(func.max(Turn.number)).where(
                Turn.conversation_id == conversation.id)) or 0)
            questions, pending = current_questions(session, conversation)
            frozen = {'kind': conversation.kind,
                      'project': {'root': str(context.root), 'profile': context.profile.name,
                                  'layout': {'docs': target.docs, 'state': target.state,
                                             'next_steps': target.next_steps, 'decisions': target.decisions,
                                             'ddbb_diagram': target.ddbb_diagram, 'flows': target.flows_dir,
                                             'phase': target.phase_dir}},
                      'conversation': {'id': conversation.id, 'title': conversation.title, 'turn': number},
                      'questions': questions, 'pending': pending, 'previous_turns': history}
            if conversation.kind == 'definition':
                if _bootstrapped(session, conversation.root):
                    raise Conflict('The project was already created from this definition')
                known, drafts = conversation.known, observed['drafts']
                defaults = skeleton(target, conversation.title,
                                    preparation=[command.argv for command in context.profile.preparation],
                                    validations=[command.argv for command in context.profile.validations])
                frozen.update(prepared, brief=conversation.brief, user_edits=[
                    {'path': path, 'before_sha256': known.get(path), 'after_sha256': drafts.get(path)}
                    for path in sorted(set(known) | set(drafts)) if known.get(path) != drafts.get(path)],
                    template_defaults={path: defaults[path] for path in default_documents(target)})
                task_id, phase_code = f'DEF-{conversation.id[:8]}-{number}', 'P000'
            else:
                from harness_local.storage.documents import latest_phase, summary_snapshot
                phase = session.get(Phase, conversation.phase_id)
                if latest_phase(session, phase.root).id != phase.id:
                    raise Conflict('A newer phase exists; plan from the latest phase')
                codes = [entry['code'] for entry in prepared['entries']]
                following = (prepared['entries'][codes.index(phase.code) + 1]
                             if phase.code in codes and codes.index(phase.code) + 1 < len(codes) else None)
                if phase.status == 'ACTIVE' and not phase.definition['tasks']:
                    following = next((entry for entry in prepared['entries'] if entry['code'] == phase.code), None)
                frozen.update(documents=prepared['documents'], base=prepared['base'], next=following,
                              phase={'id': phase.id, 'code': phase.code, 'status': phase.status,
                                     'summary': summary_snapshot(session, phase)})
                task_id, phase_code = f'PLAN-{conversation.id[:8]}-{number}', phase.code
            job = self.managed._queue_new_run(session, assessment, context, versions, task_id, phase_code, key, request,
                                              purpose=conversation.kind)
            context_sha256 = digest(frozen)
            session.add(Turn(id=str(uuid4()), conversation_id=conversation.id, number=number, run_id=job.run_id,
                             status='QUEUED', message=text,
                             request={'context': frozen, 'context_sha256': context_sha256, 'observed': observed},
                             request_sha256=digest({'message': text, 'context_sha256': context_sha256}),
                             result=None, actor=actor(), created_at=self.managed._now()))
            _touch(self.managed, conversation)
            return job

    # --- borradores ----------------------------------------------------------------------

    def _definition_open(self, session, conversation):
        if conversation.kind != 'definition':
            raise Conflict('Only a definition conversation has drafts on disk')
        if _bootstrapped(session, conversation.root):
            raise Conflict('The project was already created; edit its documents with a confirmed edit')
        if session.scalar(select(Turn.id).where(Turn.conversation_id == conversation.id, Turn.status == 'QUEUED')):
            raise Conflict('A definition turn is pending; act after it settles')

    def apply(self, context, conversation_id, proposal_id, expected, *, proposal_sha256, confirmed, writer):
        """Confirmación explícita → el harness escribe el borrador si sigue siendo el que leyó el turno."""
        from harness_local.adapters.bootstrap import DraftConflict
        if confirmed is not True:
            raise ValueError('Applying a draft requires explicit confirmation; nothing was written')
        with self.managed._write() as session:
            conversation = self._conversation(session, conversation_id, expected, context)
            self._definition_open(session, conversation)
            proposal = session.get(Proposal, proposal_id)
            if proposal is None or proposal.conversation_id != conversation.id or proposal.kind != 'draft':
                raise LookupError('Unknown draft proposal of this conversation')
            if proposal.status != 'PROPOSED':
                raise Conflict(f'The proposal is already {proposal.status.lower()}')
            if proposal.proposal_sha256 != proposal_sha256:
                raise Conflict('Apply the exact proposal that was shown; reload it')
            try:
                written = writer.write_draft(context, proposal.path, proposal.content, proposal.base_sha256)
            except DraftConflict as exc:
                raise Conflict(f'{exc}. The user edit is preserved; ask a new turn or edit the draft yourself') from exc
            turn = session.get(Turn, proposal.turn_id)
            now = self.managed._now()
            proposal.status, proposal.version = 'APPLIED', proposal.version + 1
            proposal.decision = {'decision': 'apply', 'actor': actor(), 'at': now, 'before': written['before'],
                                 'after': written['after'], 'written': written['written']}
            conversation.known = {**conversation.known, proposal.path: proposal.content_sha256}
            conversation.log = [*conversation.log, {
                'source': 'proposal', 'path': proposal.path, 'proposal_id': proposal.id,
                'proposal_number': proposal.number, 'turn_number': turn.number, 'before': written['before'],
                'after': written['after'], 'at': now}]
            _touch(self.managed, conversation)

    def edit_draft(self, context, conversation_id, expected, *, path, content, base_sha256, writer):
        """Edición del usuario por API con CAS; el turno siguiente la ve como edición del usuario."""
        from harness_local.adapters.bootstrap import DraftConflict
        target = definition_layout(context)
        if not allowed_draft(target, path):
            raise ValueError(f'{path} is not an allowed definition draft')
        if content is not None and (not isinstance(content, str) or '\0' in content
                                    or len(content.encode('utf-8')) > 512 * 1024):
            raise ValueError('Draft content must be NUL-free text of at most 512 KiB')
        with self.managed._write() as session:
            conversation = self._conversation(session, conversation_id, expected, context)
            self._definition_open(session, conversation)
            try:
                written = writer.write_draft(context, path, content, base_sha256)
            except DraftConflict as exc:
                raise Conflict(f'{exc}; nothing was overwritten') from exc
            conversation.log = [*conversation.log, {'source': 'api', 'path': path, 'before': written['before'],
                                                    'after': written['after'], 'actor': actor(),
                                                    'at': self.managed._now()}]
            _touch(self.managed, conversation)
            return written

    def defer(self, conversation_id, expected, *, question_id, reason):
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('Explicit deferral reason required')
        with self.managed._write() as session:
            conversation = self._conversation(session, conversation_id, expected)
            self._definition_open(session, conversation)
            questions, _ = current_questions(session, conversation)
            question = next((q for q in questions if q['id'] == question_id), None)
            if question is None:
                raise LookupError('Unknown open question of the latest turn')
            if not question['blocking'] or question['deferred']:
                raise Conflict('Only an open blocking question can be deferred')
            conversation.deferred = {**conversation.deferred, question_id: {
                'text': question['text'], 'reason': reason.strip(), 'actor': actor(), 'at': self.managed._now()}}
            _touch(self.managed, conversation)

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

    # --- plan de la fase siguiente ---------------------------------------------------------

    def plan(self, session, context, phase_id, reference) -> tuple[str, dict]:
        """Plan propuesto y confirmado para una transición: contenido exacto y su origen."""
        if not isinstance(reference, dict) or set(reference) != {'conversation_id', 'proposal_id', 'proposal_sha256'}:
            raise ValueError('A plan proposal reference needs conversation_id, proposal_id and proposal_sha256')
        conversation = self._conversation(session, reference['conversation_id'], context=context)
        proposal = session.get(Proposal, reference['proposal_id'])
        if (conversation.kind != 'phase_planning' or conversation.phase_id != phase_id or proposal is None
                or proposal.conversation_id != conversation.id or proposal.kind != 'plan'):
            raise LookupError('Unknown plan proposal for this phase')
        if proposal.status != 'PROPOSED':
            raise Conflict(f'The plan proposal is already {proposal.status.lower()}')
        if proposal.proposal_sha256 != reference['proposal_sha256']:
            raise Conflict('Use the exact plan proposal that was shown; reload it')
        turn = session.get(Turn, proposal.turn_id)
        return proposal.content, {**reference, 'turn_number': turn.number, 'content_sha256': proposal.content_sha256}

    def mark_plan(self, session, origin, run_id, job_id, *, decision='transition'):
        proposal = session.get(Proposal, origin['proposal_id'])
        if proposal.status != 'PROPOSED' or proposal.proposal_sha256 != origin['proposal_sha256']:
            raise Conflict('The plan proposal changed since the preview; review it again')
        proposal.status, proposal.version = 'ACCEPTED', proposal.version + 1
        proposal.decision = {'decision': decision, 'actor': actor(), 'at': self.managed._now(),
                             'run_id': run_id, 'job_id': job_id}
        _touch(self.managed, session.get(Conversation, proposal.conversation_id))

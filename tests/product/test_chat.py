"""H4.1 (D033 punto 2): chat contextual por turnos nuevos de solo lectura y propuestas confirmadas.

Git/SQLite temporales y agentes falsos; sin proveedores, red ni sesiones reanudadas."""
import json
import os

from alembic import command
import pytest
from sqlalchemy import func, inspect, select
from sqlalchemy.orm import Session

from harness_local.adapters.cli_agents import CLIConfig, argv_for
from harness_local.core.engine.chat import validate_chat_result
from harness_local.core.engine.contracts import AgentRequest, AgentResult, ContractError, Selection, freeze
from harness_local.core.engine.journal import JournalError
from harness_local.core.engine.prompts import builtin_catalog, dump_catalog, load_catalog, output_schema
from harness_local.storage.chat import ChatRepository
from harness_local.storage.managed import Conflict
from harness_local.storage.models import ChatTurnRow, ManagedAttemptRow, ManagedJobRow, PermissionRequestRow
from test_managed import repository  # noqa: F401  (fixture)
from test_managed_api import PLAN, VERSIONS, Ports, client, git, make_context, review, settle
from test_phases import checkout, world  # noqa: F401  (fixtures)

PROPOSAL = {'title': 'Adjust wording', 'objective': 'Adjust the synthetic wording', 'scope': 'Only app/main.txt',
            'acceptance_criteria': ['The wording is adjusted'], 'validation': ['test-runner check'],
            'rationale': 'The user asked to adjust it'}


def answer(*proposals, text='Synthetic answer from the frozen context'):
    return {'answer': text, 'references': ['docs/STATE.md'], 'proposals': list(proposals)}


def planned(task='CHAT-T001', phase='P001'):
    return {'task_id': task, 'phase_id': phase, 'title': 'Adjust wording', 'objective': 'Adjust synthetic wording',
            'executor_prompt': 'Adjust app/main.txt', 'allowed_paths': ['app/**'], 'forbidden_paths': [],
            'acceptance_criteria': ['The wording is adjusted'], 'validation_commands': [],
            'executor_selection': {'model': 'synthetic-executor', 'effort': 'medium', 'reason': 'Explicit policy'}}


class Chat:
    def __init__(self, world):
        self.world = world
        self.repo = ChatRepository(world.repository)

    def create(self, phase_id=None):
        return self.repo.create(self.world.context, title='Synthetic conversation', phase_id=phase_id)

    def get(self, cid):
        return self.repo.get(cid)

    def say(self, cid, text='¿Qué falta en la fase?', key=None, **kwargs):
        return self.repo.submit_message(self.world.context, cid, self.get(cid)['version'], key=key or self.world.key(),
                                        versions=VERSIONS, text=text, **kwargs)

    def accept(self, cid, proposal, key=None, task='CHAT-T001', phase='P001', confirmed=True, **overrides):
        values = {'proposal_sha256': proposal['proposal_sha256'], 'task_id': task, 'phase_id': phase,
                  'confirmed': confirmed, **overrides}
        return self.repo.accept(self.world.context, cid, proposal['id'], self.get(cid)['version'],
                                key=key or self.world.key(), versions=VERSIONS, **values)


@pytest.fixture
def chat(world):  # noqa: F811
    return Chat(world)


def jobs(world):
    with Session(world.repository.engine) as session:
        return session.scalar(select(func.count()).select_from(ManagedJobRow))


def tree_status(world):
    return git(world.context.root, 'status', '--porcelain')


# --- turno nuevo, contexto congelado y solo lectura -------------------------------------------------


def test_turn_freezes_explicit_context_before_a_fresh_read_only_invocation(world, chat):
    run_id = world.accept_task()
    pid = world.create()
    cid = chat.create(pid)
    job = chat.say(cid, run_ids=[run_id])
    detail = chat.get(cid)
    turn = detail['turns'][0]
    assert turn['status'] == 'QUEUED' and detail['actions'] == []  # un turno pendiente cada vez
    assert [d['path'] for d in turn['documents']] == ['docs/STATE.md', 'docs/NEXT_STEPS.md']  # los de la fase
    assert turn['run_ids'] == [run_id] and turn['phase_code'] == 'P001'
    # Un cambio posterior al encolado no altera la petición congelada.
    world.context.path('docs/STATE.md').write_text('# Changed after queueing\n', encoding='utf-8')
    world.script(answer(PROPOSAL))
    world.run()
    request = world.ports.agents.requests[-1]
    assert request.role == 'chat' and request.fresh_session and request.task_json is None
    assert '# State' in request.prompt and 'Changed after queueing' not in request.prompt
    assert '¿Qué falta en la fase?' in request.prompt and run_id in request.prompt
    snapshot = json.loads(request.prompt_snapshot_json)
    assert snapshot['parts'][0]['version']['name'] == 'chat-turn'
    assert set(snapshot['output_schema']['required']) == {'answer', 'references', 'proposals'}
    with Session(world.repository.engine) as session:
        attempt = session.scalar(select(ManagedAttemptRow).where(ManagedAttemptRow.run_id == job.run_id))
        assert json.loads(attempt.request_json)['prompt'] == request.prompt  # persistida antes del efecto
        stored = session.scalar(select(ChatTurnRow).where(ChatTurnRow.run_id == job.run_id))
        frozen = stored.request['context']
    assert frozen['documents'][0]['content'] == '# State\n' and frozen['runs'][0]['commit'] is not None
    assert frozen['phase']['code'] == 'P001' and frozen['previous_turns'] == []
    detail = chat.get(cid)
    turn = detail['turns'][0]
    assert turn['status'] == 'ANSWERED' and turn['run_status'] == 'COMPLETED'
    assert turn['result']['checkout']['unchanged'] is True and turn['result']['attempt_id'] == request.id
    assert [p['status'] for p in detail['proposals']] == ['PROPOSED'] and detail['actions'] == ['message']
    run = world.repository.get_run(job.run_id)
    assert run.history.task_json is None and run.history.status == 'completed'
    assert world.ports.roles() == ['executor', 'reviewer', 'chat']
    assert jobs(world) == 3  # tarea, commit y turno: la propuesta no encoló nada


def test_each_turn_is_a_new_invocation_with_previous_turns_as_explicit_context(world, chat):
    cid = chat.create()
    world.script(answer(text='First answer'), answer(text='Second answer'))
    chat.say(cid, text='First question')
    world.run()
    chat.say(cid, text='Second question', documents=['app/main.txt', 'docs/missing.md'])
    world.run()
    first, second = world.ports.agents.requests
    assert first.id != second.id and second.fresh_session
    assert 'First question' in second.prompt and 'First answer' in second.prompt  # contexto explícito, sin sesión
    detail = chat.get(cid)
    assert detail['turns'][1]['previous_turns'] == 1
    assert detail['turns'][1]['documents'] == [
        {'path': 'app/main.txt', 'sha256': detail['turns'][1]['documents'][0]['sha256'], 'size': 9, 'truncated': False},
        {'path': 'docs/missing.md', 'sha256': None, 'size': None, 'truncated': False}]  # ausencia explícita
    assert [t['status'] for t in detail['turns']] == ['ANSWERED', 'ANSWERED']


def test_message_selection_is_validated_inside_this_checkout(world, chat, tmp_path):
    cid = chat.create()
    with pytest.raises(ValueError):
        chat.say(cid, documents=['../outside.md'])
    os.symlink(world.context.path('docs/STATE.md'), world.context.root / 'docs/link.md')
    git(world.context.root, 'add', 'docs/link.md')
    git(world.context.root, 'commit', '-qm', 'synthetic link')
    with pytest.raises(ValueError):
        chat.say(cid, documents=['docs/link.md'])
    git(world.context.root, 'reset', '--hard', 'HEAD~1')
    (tmp_path / 'other-checkout').mkdir()
    other = make_context(tmp_path / 'other-checkout')
    foreign = world.repository.submit(other, 'P001-T001', 'P001', PLAN, VERSIONS, key='foreign')
    with pytest.raises(LookupError):
        chat.say(cid, run_ids=[foreign.run_id])
    with pytest.raises(ValueError):
        chat.say(cid, text='   ')
    assert chat.get(cid)['turns'] == []


@pytest.mark.parametrize('bad', [
    {**answer(), 'extra': True},
    answer({**PROPOSAL, 'allowed_paths': ['**']}),  # una propuesta no fija contratos
    answer({**PROPOSAL, 'acceptance_criteria': []}),
    answer(*[PROPOSAL] * 6),
    {'answer': '', 'references': [], 'proposals': []},
    AgentResult(None, terminal_observed=False, exit_code=1, error='CLI failed'),
])
def test_invalid_output_stops_the_turn_without_fallback_or_retry(world, chat, bad):
    cid = chat.create()
    world.script(bad)
    job = chat.say(cid)
    world.run()
    detail = chat.get(cid)
    assert detail['turns'][0]['status'] == 'FAILED' and detail['proposals'] == []
    assert world.repository.get_run(job.run_id).status == 'STOPPED'
    assert world.ports.roles() == ['chat'] and world.worker.run_once() is None  # nada se reintenta
    assert detail['actions'] == ['message']  # un turno nuevo es una acción explícita


def test_turn_that_writes_to_the_checkout_is_discarded(world, chat):
    cid = chat.create()

    def writes(context, request):
        context.path('app/main.txt').chmod(0o644)  # malicious agent bypasses cooperative mode
        context.path('app/main.txt').write_text('side effect\n', encoding='utf-8')
        return answer(PROPOSAL)
    world.script(writes)
    chat.say(cid)
    world.run()
    turn = chat.get(cid)['turns'][0]
    assert turn['status'] == 'FAILED' and 'checkout changed' in turn['result']['reasons'][0]
    assert turn['result']['checkout']['unchanged'] is False and chat.get(cid)['proposals'] == []


def test_validate_chat_result_has_a_fixed_schema():
    assert validate_chat_result(answer(PROPOSAL))['proposals'][0]['title'] == 'Adjust wording'
    for bad in ({'answer': 'a', 'references': []}, {**answer(), 'references': 'docs'},
                answer({key: value for key, value in PROPOSAL.items() if key != 'rationale'})):
        with pytest.raises(ContractError):
            validate_chat_result(bad)


# --- propuestas y tareas vinculadas ----------------------------------------------------------------


def test_proposal_without_confirmation_or_with_stale_evidence_queues_nothing(world, chat):
    cid = chat.create()
    world.script(answer(PROPOSAL, {**PROPOSAL, 'title': 'Second idea'}))
    chat.say(cid)
    world.run()
    first, second = chat.get(cid)['proposals']
    before = jobs(world)
    with pytest.raises(ValueError, match='confirmation'):
        chat.accept(cid, first, confirmed=False)
    with pytest.raises(Conflict, match='exact proposal'):
        chat.accept(cid, first, proposal_sha256='0' * 64)
    with pytest.raises(Conflict, match='reload'):
        chat.repo.accept(world.context, cid, first['id'], chat.get(cid)['version'] - 1, key='stale', versions=VERSIONS,
                         proposal_sha256=first['proposal_sha256'], task_id='CHAT-T001', phase_id='P001', confirmed=True)
    with pytest.raises(ValueError):
        chat.accept(cid, first, task='bad id with spaces')
    chat.repo.dismiss(cid, second['id'], chat.get(cid)['version'], reason='Not now')
    with pytest.raises(Conflict, match='dismissed'):
        chat.accept(cid, chat.get(cid)['proposals'][1])
    assert jobs(world) == before
    assert world.worker.run_once() is None


def test_confirmed_proposal_becomes_a_linked_task_planned_executed_reviewed_and_committed(world, chat):
    pid = world.create(tasks=())
    cid = chat.create(pid)
    world.script(answer(PROPOSAL))
    chat.say(cid, text='Ajusta el texto de app/main.txt')
    world.run()
    proposal = chat.get(cid)['proposals'][0]
    version = chat.get(cid)['version']

    def decide(task='CHAT-T001'):
        return chat.repo.accept(world.context, cid, proposal['id'], version, key='accept', versions=VERSIONS,
                                proposal_sha256=proposal['proposal_sha256'], task_id=task, phase_id='P001',
                                confirmed=True)
    job = decide()
    assert decide() == job  # idempotente: misma clave y misma decisión, aunque la conversación avanzó
    with pytest.raises(Conflict, match='different action'):
        decide('CHAT-T002')

    def edit(context, request):
        context.path('app/main.txt').write_text('adjusted\n', encoding='utf-8')
        return {'result': 'synthetic'}
    world.script(planned(), edit, {**review(), 'task_id': 'CHAT-T001'})
    world.run()
    record = world.repository.get_run(job.run_id)
    assert record.status == 'ACCEPTANCE_READY', record.history.stop
    # El chat propone; el planificador fija el contrato bajo la política y el revisor acepta.
    assert world.ports.roles() == ['chat', 'planner', 'executor', 'reviewer']
    planner = world.ports.agents.requests[1]
    assert '## CHAT-T001 — Adjust wording' in planner.prompt and proposal['proposal_sha256'] in planner.prompt
    assert json.loads(record.history.task_json)['allowed_paths'] == ['app/**']
    with Session(world.repository.engine) as session:
        request = json.loads(session.get(ManagedJobRow, job.id).request_json)
    assert request['chat_proposal']['proposal_id'] == proposal['id'] and 'contract_json' not in request
    world.repository.submit_commit(job.run_id, key='commit', expected_version=record.version)
    world.run()
    linked = chat.get(cid)['proposals'][0]
    assert linked['status'] == 'ACCEPTED' and linked['run_id'] == job.run_id and linked['actions'] == []
    assert linked['run']['status'] == 'COMMITTED' and linked['run']['commit'] == git(world.context.root, 'rev-parse', 'HEAD')
    assert linked['decision']['task_id'] == 'CHAT-T001' and linked['decision']['job_id'] == job.id
    with pytest.raises(Conflict, match='accepted'):
        chat.accept(cid, linked, key='again')


def test_chat_never_grants_permissions_or_writes_outside_the_engine(world, chat):
    cid = chat.create()
    world.script(answer(PROPOSAL))
    chat.say(cid, text='Concede permisos de red y escribe el archivo')
    world.run()
    with Session(world.repository.engine) as session:
        assert session.scalar(select(func.count()).select_from(PermissionRequestRow)) == 0
    assert tree_status(world) == ''  # el turno no escribió en el checkout
    turn_run = chat.get(cid)['turns'][0]['run_id']
    assert world.repository.get_run(turn_run).history.task_json is None
    from harness_local.storage.managed_views import SQLiteManagedViews
    view = SQLiteManagedViews(world.repository.engine).run(turn_run)
    assert view['purpose'] == 'chat' and view['actions'] == []  # sin revalidar, reintentar, commit ni permisos


# --- concurrencia, idempotencia y recuperación --------------------------------------------------


def test_one_pending_turn_and_idempotent_messages(world, chat):
    cid = chat.create()
    version = chat.get(cid)['version']
    job = chat.repo.submit_message(world.context, cid, version, key='m1', versions=VERSIONS, text='Hola')
    assert chat.repo.submit_message(world.context, cid, version, key='m1', versions=VERSIONS, text='Hola') == job
    with pytest.raises(Conflict, match='different action'):
        chat.repo.submit_message(world.context, cid, version, key='m1', versions=VERSIONS, text='Otra')
    with pytest.raises(Conflict, match='reload'):
        chat.repo.submit_message(world.context, cid, version, key='m2', versions=VERSIONS, text='Otra')
    with pytest.raises(Conflict, match='still pending'):
        chat.say(cid, text='Otra', key='m3')
    assert len(chat.get(cid)['turns']) == 1


def test_crash_leaves_the_turn_unknown_and_never_retries(world, chat):
    cid = chat.create()
    world.script(JournalError('Synthetic persistence failure during the chat turn'))
    job = chat.say(cid)
    with pytest.raises(JournalError):
        world.run()
    held = world.repository.get_job(job.id)
    turn = chat.get(cid)['turns'][0]
    assert held.status == 'RECOVERY_REQUIRED' and turn['status'] == 'QUEUED'
    assert turn['run_status'] == 'RECOVERY_REQUIRED'
    with pytest.raises(Conflict, match='still pending'):
        chat.say(cid, text='Otra pregunta')
    assert world.worker.run_once() is None
    world.repository.confirm_stopped(job.id, owner_token=held.owner_token,
                                     expected_version=world.repository.get_run(job.run_id).version,
                                     reason='Synthetic worker stopped')
    detail = chat.get(cid)
    assert detail['turns'][0]['status'] == 'UNKNOWN' and detail['proposals'] == []
    assert world.repository.get_run(job.run_id).history.attempts[-1].result.error.startswith('Interrupted')
    assert world.ports.roles() == ['chat'] and world.worker.run_once() is None
    world.script(answer())
    chat.say(cid, text='Otra pregunta')
    world.run()
    assert [t['status'] for t in chat.get(cid)['turns']] == ['UNKNOWN', 'ANSWERED']


def test_fifo_without_a_live_writer_still_preserves_queue_order(world, chat):
    task = world.repository.submit(world.context, 'P001-T001', 'P001', PLAN, VERSIONS, key='task')
    cid = chat.create()
    chat.say(cid)
    world.script(lambda context, request: {'result': 'synthetic'}, {**review(), 'verdict': 'BLOCKED',
                                                                       'blocking_questions': ['?']}, answer())
    world.run()
    assert world.repository.get_run(task.run_id).status == 'BLOCKED'
    world.run()
    assert world.ports.roles() == ['executor', 'reviewer', 'chat']  # FIFO bajo el lock del checkout


# --- compatibilidad, adaptador y migración -------------------------------------------------------


def test_catalogs_frozen_before_the_chat_template_remain_loadable():
    catalog = builtin_catalog()
    assert 'chat-turn' in catalog
    old = {name: item for name, item in catalog.items() if name != 'chat-turn'}
    assert load_catalog(dump_catalog(old)) == old
    with pytest.raises(ContractError):
        dump_catalog({name: item for name, item in old.items() if name != 'close-phase'})


def test_cli_reviewer_handles_chat_role_read_only_with_either_provider(tmp_path):
    context = make_context(tmp_path)
    request = AgentRequest('00000000-0000-4000-8000-000000000002', 'chat', Selection('m', 'low', 'r'), 'p', None, '{}')
    argv = argv_for(CLIConfig('codex', ('/synthetic/codex',), '0.162.1', (), 1), context, request)
    assert argv[argv.index('--sandbox') + 1] == 'read-only' and '--ephemeral' in argv
    # D052: a Claude reviewer chats with the fixed read-only inventory and a JSON schema.
    argv = argv_for(CLIConfig('claude', ('/synthetic/claude',), '2.1.295', (), 1), context, request)
    assert argv[argv.index('--tools') + 1] == 'Read,Glob,Grep' and '--restricted' in argv
    # D058 (cli-6): the typed engine schema, not only the required fields.
    assert json.loads(argv[argv.index('--json-schema') + 1]) == output_schema('chat')


def test_migration_roundtrip_and_downgrade_refused_with_chat_runs(migrated_database, world, chat):
    command.check(migrated_database[1])
    command.downgrade(migrated_database[1], '0011_phase_amendments')
    assert 'chat_turns' not in inspect(world.repository.engine).get_table_names()
    command.upgrade(migrated_database[1], 'head')
    command.check(migrated_database[1])
    cid = chat.create()
    world.script(answer())
    chat.say(cid)
    world.run()
    with pytest.raises(RuntimeError, match='0012'):
        command.downgrade(migrated_database[1], '0011_phase_amendments')
    assert chat.get(cid)['turns'][0]['status'] == 'ANSWERED'


# --- HTTP ----------------------------------------------------------------------------------


def test_http_chat_flow_with_guard_confirmation_and_linked_task(tmp_path, migrated_database, checkout, monkeypatch):  # noqa: F811
    from harness_local.services.managed_runtime import CONFIG_ENV
    from test_managed_api import config
    monkeypatch.delenv(CONFIG_ENV, raising=False)

    def edit(context, request):
        context.path('app/main.txt').write_text('adjusted\n', encoding='utf-8')
        return {'result': 'synthetic'}
    ports = Ports([answer(PROPOSAL, {**PROPOSAL, 'title': 'Second idea'}), planned(), edit,
                   {**review(), 'task_id': 'CHAT-T001'}])
    with client(migrated_database[0], tmp_path, config(checkout, ports)) as http:
        denied = http.post('/api/managed/projects/synthetic/conversations', json={'title': 'Chat'},
                           headers={'X-Harness-Local': '0'})
        assert denied.status_code == 403
        created = http.post('/api/managed/projects/synthetic/conversations', json={'title': 'Chat'})
        assert created.status_code == 201, created.text
        conversation = created.json()
        cid = conversation['id']
        assert conversation['project_id'] == 'synthetic' and conversation['actions'] == ['message']
        assert http.get('/api/managed/projects/synthetic/conversations').json()[0]['turns'] == 0
        body = {'expected_version': conversation['version'], 'text': 'Ajusta el texto'}
        assert http.post(f'/api/managed/conversations/{cid}/messages', json=body).status_code == 422  # sin clave
        message = http.post(f'/api/managed/conversations/{cid}/messages', json=body, headers={'Idempotency-Key': 'm'})
        assert message.status_code == 202, message.text
        turn_run = settle(http, message.json()['run_id'])
        assert turn_run['purpose'] == 'chat' and turn_run['actions'] == []
        detail = http.get(f'/api/managed/conversations/{cid}').json()
        assert detail['turns'][0]['status'] == 'ANSWERED' and len(detail['proposals']) == 2
        first, second = detail['proposals']
        accept = {'expected_version': detail['version'], 'proposal_sha256': first['proposal_sha256'],
                  'task_id': 'CHAT-T001', 'phase_id': 'P001'}
        path = f"/api/managed/conversations/{cid}/proposals/{first['id']}/accept"
        assert http.post(path, json=accept, headers={'Idempotency-Key': 'a'}).status_code == 422  # sin confirmación
        stale = http.post(path, json={**accept, 'confirmed': True, 'proposal_sha256': 'f' * 64},
                          headers={'Idempotency-Key': 'stale'})
        assert stale.status_code == 409 and stale.json()['detail']['code'] == 'conflict'
        accepted = http.post(path, json={**accept, 'confirmed': True}, headers={'Idempotency-Key': 'a'})
        assert accepted.status_code == 202, accepted.text
        run = settle(http, accepted.json()['run_id'])
        assert run['purpose'] == 'task' and run['status'] == 'ACCEPTANCE_READY' and 'commit' in run['actions']
        detail = http.get(f'/api/managed/conversations/{cid}').json()
        dismissed = http.post(f"/api/managed/conversations/{cid}/proposals/{second['id']}/dismiss",
                              json={'expected_version': detail['version'], 'reason': 'Later'})
        assert dismissed.status_code == 200
        statuses = [(p['status'], p['run']['status'] if p['run'] else None) for p in dismissed.json()['proposals']]
        assert statuses == [('ACCEPTED', 'ACCEPTANCE_READY'), ('DISMISSED', None)]
        assert http.get('/api/managed/conversations/unknown').status_code == 404
    assert ports.roles() == ['chat', 'planner', 'executor', 'reviewer']
    assert git(checkout.root, 'status', '--porcelain') == 'M app/main.txt'  # solo la tarea normal escribió

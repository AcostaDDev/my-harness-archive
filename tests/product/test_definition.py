"""H6.5: creación y planificación conversacionales con Git/SQLite temporales y agentes falsos; sin proveedores."""
from dataclasses import replace
from hashlib import sha256
import json

from alembic import command
import pytest
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from harness_local.adapters.git import GitWorkspace
from harness_local.core.engine.documents import Layout, blocks, decision_index, markers, parse_roadmap
from harness_local.core.engine.journal import JournalError
from harness_local.services.managed import LocalSupervisor
from harness_local.services.managed_runtime import ManagedConfig, ManagedProject
from harness_local.storage.bootstrap import BootstrapRepository
from harness_local.storage.database import make_engine
from harness_local.storage.managed import Conflict, SQLiteManagedRepository
from harness_local.storage.models import PhaseRow, PlanningProposalRow
from harness_local.storage.phases import PhaseRepository
from harness_local.storage.planning import PlanningRepository
from test_documents import PLAN_P002, transitions, v2, v2checkout  # noqa: F401  (fixtures)
from test_managed import repository  # noqa: F401  (fixture)
from test_managed_api import IDENTITY, VERSIONS, client, git, make_context, Ports, review

LAYOUT = Layout('docs', 'docs/STATE.md', 'docs/NEXT_STEPS.md')
STATE_BEGIN, STATE_END = markers('state')
ROAD_BEGIN, ROAD_END = markers('roadmap')
DEC_BEGIN, DEC_END = markers('decisions')
BRIEF = '# Brief sintético\n\nUn flujo local para operadores sintéticos.\n\n- Sin red ni datos reales.\n'

DRAFTS = {
    'README.md': '# Sintético\n\nHerramienta local sintética.\n',
    'docs/SPECIFICATION.md': '# Especificación — Sintético\n\n## Problema\n\nCoordinar un flujo sintético.\n',
    'docs/ARCHITECTURE.md': '# Arquitectura — Sintético\n\n## Stack\n\nPerfil registrado.\n',
    'docs/architecture/data-model.md': '# Modelo de datos\n\n```mermaid\nerDiagram\n  ITEM ||--o{ STEP : has\n```\n',
    'docs/ROADMAP.md': f"""# Roadmap — Sintético

{ROAD_BEGIN}
{ROAD_END}

## P001 — Fundamentos

**Objetivo:** Entregar el flujo sintético mínimo.
**Criterios de salida:**
- El flujo sintético está aceptado.
**Tag:** `p001`

## P002 — Ampliación

**Objetivo:** Ampliar el comportamiento sintético.
**Criterios de salida:**
- Second behavior is accepted
""",
    'docs/DECISIONS.md': f'# Decisiones — Sintético\n\nRegistro en `decisions/`.\n\n{DEC_BEGIN}\n{DEC_END}\n',
    'docs/decisions/D001-usar-perfil.md': ('# D001 — Usar el perfil registrado\n\n**Estado:** aceptada\n'
                                          '**Fecha:** 2026-10-14\n**Fase:** P000\n**Contexto:** sintético.\n'),
    'docs/STATE.md': (f'# Estado — Sintético\n\n{STATE_BEGIN}\n{STATE_END}\n\n## Base acumulada\n\n'
                      'Todavía no hay trabajo aceptado.\n\n## Fase activa — P001 Fundamentos\n\nSin notas todavía.\n'),
    'docs/NEXT_STEPS.md': f"""# P001 — Fundamentos

Objetivo y criterios en [ROADMAP](ROADMAP.md).

{STATE_BEGIN}
{STATE_END}

## Restricciones compartidas

Solo contenido sintético.

## P001-T001 — Cambio sintético

**Objetivo:** Cambiar el contenido sintético.
**Rutas permitidas:** `app/**`
**Criterios de aceptación:**
- Synthetic behavior is present.
**Comandos de validación:** `test-runner check`
**Ejecutor:** synthetic-executor / medium — Selección explícita de prueba
""",
}
QUESTION = {'text': '¿Hace falta autenticación?', 'blocking': True}


def answer(drafts=None, questions=(), pending=(), text='Borradores propuestos'):
    return {'answer': text, 'questions': list(questions), 'pending': list(pending),
            'drafts': [{'path': path, 'content': content, 'reason': f'Propuesta para {path}'}
                       for path, content in (drafts if drafts is not None else DRAFTS).items()]}


@pytest.fixture
def world(migrated_database, tmp_path):
    root = tmp_path / 'definition-destination'
    root.mkdir()
    context = replace(make_context(root), documents='v2')
    engine = make_engine(migrated_database[0])
    repo = SQLiteManagedRepository(engine)
    writer = GitWorkspace(IDENTITY)
    ports = Ports()
    worker = LocalSupervisor(repo, ports, commit_factory=lambda c, v: writer)
    yield World(context, repo, writer, worker, ports)
    engine.dispose()


class World:
    def __init__(self, context, repo, writer, worker, ports):
        self.context, self.repo, self.writer, self.worker, self.ports = context, repo, writer, worker, ports
        self.planning = PlanningRepository(repo)
        self.bootstrap = BootstrapRepository(repo)
        self.keys = 0

    def key(self):
        self.keys += 1
        return f'definition-{self.keys}'

    def create(self, brief=BRIEF):
        return self.planning.create(self.context, kind='definition', title='Sintético', brief=brief, writer=self.writer)

    def view(self, cid):
        return self.planning.get(cid)

    def message(self, cid, text='Propón los documentos', key=None):
        return self.planning.submit_message(self.context, cid, self.view(cid)['version'], key=key or self.key(),
                                            versions=VERSIONS, text=text, writer=self.writer)

    def turn(self, cid, response, text='Propón los documentos'):
        job = self.message(cid, text)
        self.ports.agents.responses.append(response)
        assert self.worker.run_once().status == 'DONE'
        return job, self.view(cid)['turns'][-1]

    def apply(self, cid, proposal):
        self.planning.apply(self.context, cid, proposal['id'], self.view(cid)['version'],
                            proposal_sha256=proposal['proposal_sha256'], confirmed=True, writer=self.writer)

    def apply_all(self, cid):
        for proposal in self.view(cid)['proposals']:
            if proposal['status'] == 'PROPOSED':
                self.apply(cid, proposal)

    def preview(self, cid):
        return self.bootstrap.preview(self.context, {'conversation_id': cid}, VERSIONS, self.writer)

    def accept(self, cid, shown=None, key=None):
        shown = shown or self.preview(cid)
        return self.bootstrap.submit(self.context, {'conversation_id': cid}, VERSIONS, self.writer, key=key or self.key(),
                                     preview_sha256=shown['preview_sha256'], reason='Definición revisada',
                                     confirmed=True, resume_operation_id=shown['resume_operation_id'],
                                     expected_version=shown['expected_version'])

    def path(self, relative):
        return self.context.root / relative

    def files(self):
        return sorted(p.relative_to(self.context.root).as_posix() for p in self.context.root.rglob('*')
                      if p.is_file() and '.git' not in p.relative_to(self.context.root).parts)


def ready(world):
    """Conversación con todos los borradores aplicados y sin preguntas bloqueantes."""
    cid = world.create()
    world.turn(cid, answer())
    world.apply_all(cid)
    return cid


# --- recorrido completo ------------------------------------------------------------------------


def test_empty_folder_to_root_commit_with_p001_and_phase_000(world):
    cid = world.create()
    assert world.files() == []
    job, turn = world.turn(cid, answer(questions=[QUESTION], pending=['Confirmar autenticación']))
    assert turn['status'] == 'ANSWERED' and world.files() == []  # el agente no escribe
    request = world.repo.get_run(job.run_id).history.attempts[0].request
    assert request.role == 'definition' and request.fresh_session
    assert json.loads(request.prompt_snapshot_json)['parts'][0]['version']['name'] == 'define-project'
    assert sha256(BRIEF.encode()).hexdigest() in request.prompt  # brief congelado en el contexto
    assert world.planning.snapshot(job.run_id)['context']['brief']['content'] == BRIEF
    view = world.view(cid)
    assert [p['status'] for p in view['proposals']] == ['PROPOSED'] * len(DRAFTS)
    assert all(p['base_sha256'] is None for p in view['proposals'])
    assert view['questions'][0]['blocking'] and view['pending'] == ['Confirmar autenticación']
    world.apply_all(cid)
    assert {path: world.path(path).read_text() for path in DRAFTS} == DRAFTS
    # Edición del usuario en su editor y por API entre turnos.
    world.path('docs/SPECIFICATION.md').write_text(DRAFTS['docs/SPECIFICATION.md'] + '\nEditado en disco.\n')
    readme = '# Sintético\n\nEditado por API.\n'
    world.planning.edit_draft(world.context, cid, world.view(cid)['version'], path='README.md', content=readme,
                              base_sha256=sha256(DRAFTS['README.md'].encode()).hexdigest(), writer=world.writer)
    shown = world.preview(cid)
    assert not shown['ready'] and any('Blocking questions' in item for item in shown['blockers'])
    job, turn = world.turn(cid, answer(drafts={}, text='Sin autenticación: decisión del usuario'),
                           text='No hace falta autenticación')
    edits = world.planning.snapshot(job.run_id)['context']['user_edits']
    assert {item['path'] for item in edits} == {'docs/SPECIFICATION.md', 'README.md'}
    assert 'Editado en disco.' in world.repo.get_run(job.run_id).history.attempts[0].request.prompt
    assert world.view(cid)['questions'] == []
    shown = world.preview(cid)
    assert shown == world.preview(cid) and shown['ready'] and shown['blockers'] == [], shown['blockers']
    documents = {doc['path']: doc for doc in shown['documents']}
    assert documents['docs/archive/phase-000/BRIEF.md']['content'] == BRIEF
    record = documents['docs/archive/phase-000/DEFINITION.md']['content']
    assert '| 2 | ANSWERED | No hace falta autenticación |' in record and 'edición del usuario por API' in record
    assert documents['docs/research/README.md']['origin'] == 'template'
    assert documents['docs/SPECIFICATION.md']['origin'] == 'draft'
    assert documents['docs/STATE.md']['origin'] == 'draft+blocks'
    assert '**Fase:** P001 · estado ACTIVE' in blocks(documents['docs/STATE.md']['content'])['state']
    assert '**Siguiente tarea:** P001-T001' in blocks(documents['docs/NEXT_STEPS.md']['content'])['state']
    assert '| P001 | Fundamentos | activa | — |' in blocks(documents['docs/ROADMAP.md']['content'])['roadmap']
    assert '| D001 |' in blocks(documents['docs/DECISIONS.md']['content'])['decisions']
    assert shown['phase']['code'] == 'P001' and shown['phase']['tasks'] == ['P001-T001']
    assert shown['phase']['documents'] == list(LAYOUT.phase_documents) and shown['phase']['tag'] == 'p001'
    assert shown['first_task']['allowed_paths'] == ['app/**']
    before = world.files()
    job = world.accept(cid, shown, key='accept-once')
    assert world.accept(cid, shown, key='accept-once').id == job.id
    assert world.files() == before  # encolar no escribe
    assert world.worker.run_once().status == 'DONE'
    op = world.bootstrap.get(world.context.root)
    assert op['status'] == 'COMPLETED' and op['result']['commit'] == git(world.context.root, 'rev-parse', 'HEAD')
    assert git(world.context.root, 'rev-list', '--count', 'HEAD') == '1'
    assert git(world.context.root, 'status', '--porcelain') == ''
    tracked = git(world.context.root, 'ls-files').splitlines()
    assert tracked == sorted(documents) == world.files()
    assert all(world.path(path).read_text() == doc['content'] for path, doc in documents.items())
    phases = PhaseRepository(world.repo)
    detail = phases.get(op['phase_id'], {p: sha256(world.path(p).read_bytes()).hexdigest() for p in LAYOUT.phase_documents})
    assert detail['status'] == 'ACTIVE' and detail['documents']['drift'] == []
    assert world.view(cid)['created'] and world.view(cid)['actions'] == []
    with pytest.raises(Conflict, match='already created'):
        world.message(cid)
    # La primera tarea sigue por el flujo normal y regenera los bloques en su commit.
    def implement(context, request):
        context.path('app/main.txt').parent.mkdir(exist_ok=True)
        context.path('app/main.txt').write_text('implemented\n')
        return {'result': 'Implementado P001-T001'}
    world.ports.agents.responses.extend([implement, review()])
    task = world.repo.submit(world.context, 'P001-T001', 'P001', shown['task_text'], VERSIONS, key='first-task')
    assert world.worker.run_once().status == 'DONE'
    world.repo.submit_commit(task.run_id, key='first-commit', expected_version=world.repo.get_run(task.run_id).version)
    assert world.worker.run_once().status == 'DONE'
    assert world.repo.get_run(task.run_id).status == 'COMMITTED'
    assert '| P001-T001 | COMMITTED | ACCEPT | este commit |' in blocks(world.path('docs/STATE.md').read_text())['state']
    assert world.ports.roles() == ['definition', 'definition', 'executor', 'reviewer']


def test_agent_writes_are_detected_and_discard_the_turn(world):
    cid = world.create()

    def writes(context, request):
        (context.root / 'README.md').write_text('# escrito por el agente\n')
        return answer()
    _, turn = world.turn(cid, writes)
    assert turn['status'] == 'FAILED' and 'changed during a read-only turn' in turn['result']['reasons'][0]
    assert world.view(cid)['proposals'] == []
    assert world.path('README.md').read_text() == '# escrito por el agente\n'  # conservado, no se revierte
    assert world.ports.roles() == ['definition']


INVALID = {
    'outside': {'drafts': [{'path': 'src/app.py', 'content': 'x', 'reason': 'r'}]},
    'archive': {'drafts': [{'path': 'docs/archive/phase-000/BRIEF.md', 'content': 'x', 'reason': 'r'}]},
    'research': {'drafts': [{'path': 'docs/research/spike.md', 'content': 'x', 'reason': 'r'}]},
    'escape': {'drafts': [{'path': 'docs/decisions/../x.md', 'content': 'x', 'reason': 'r'}]},
    'duplicate': {'drafts': [{'path': 'README.md', 'content': 'x', 'reason': 'r'}] * 2},
    'extra': {'extra': True},
    'blocking': {'questions': [{'text': 'q', 'blocking': 'yes'}]},
    'empty': {'drafts': [{'path': 'README.md', 'content': '', 'reason': 'r'}]},
}


@pytest.mark.parametrize('case', sorted(INVALID))
def test_invalid_definition_output_stops_the_turn_without_retry(world, case):
    cid = world.create()
    _, turn = world.turn(cid, {**answer(drafts={}), **INVALID[case]})
    assert turn['status'] == 'FAILED' and world.view(cid)['proposals'] == []
    assert world.files() == [] and world.worker.run_once() is None and world.ports.roles() == ['definition']


# --- ediciones concurrentes ----------------------------------------------------------------------


def test_concurrent_edits_are_detected_and_never_overwritten(world):
    cid = world.create()
    world.turn(cid, answer())
    proposals = {p['path']: p for p in world.view(cid)['proposals']}
    world.apply(cid, proposals['docs/ROADMAP.md'])
    # El usuario crea README entre el turno y la aplicación: conflicto, nada se sobrescribe.
    world.path('README.md').write_text('# mío\n')
    with pytest.raises(Conflict, match='changed since it was read'):
        world.apply(cid, proposals['README.md'])
    assert world.path('README.md').read_text() == '# mío\n'
    assert world.view(cid)['proposals'][0]['status'] in ('PROPOSED', 'APPLIED')
    # Una edición por API con un hash base obsoleto tampoco sobrescribe.
    with pytest.raises(Conflict, match='nothing was overwritten'):
        world.planning.edit_draft(world.context, cid, world.view(cid)['version'], path='README.md', content='# API\n',
                                  base_sha256=None, writer=world.writer)
    assert world.path('README.md').read_text() == '# mío\n'
    with pytest.raises(ValueError, match='not an allowed definition draft'):
        world.planning.edit_draft(world.context, cid, world.view(cid)['version'], path='notes.txt', content='x',
                                  base_sha256=None, writer=world.writer)
    # Un borrador cambiado después de encolar el mensaje detiene el turno sin invocar al agente.
    world.message(cid)
    world.path('docs/ROADMAP.md').write_text(DRAFTS['docs/ROADMAP.md'] + '\nCambio tardío.\n')
    assert world.worker.run_once().status == 'DONE'
    turn = world.view(cid)['turns'][-1]
    assert turn['status'] == 'FAILED' and 'changed after the message was queued' in turn['result']['reasons'][0]
    assert world.ports.roles() == ['definition']
    # Con un turno pendiente no se aplica ni se edita por API.
    world.message(cid)
    with pytest.raises(Conflict, match='pending'):
        world.apply(cid, proposals['docs/STATE.md'])
    world.ports.agents.responses.append(answer(drafts={'README.md': '# propuesto\n'}))
    assert world.worker.run_once().status == 'DONE'
    snapshot = world.view(cid)['turns'][-1]
    assert {e['path'] for e in snapshot['user_edits']} == {'docs/ROADMAP.md', 'README.md'}
    readme = [p for p in world.view(cid)['proposals'] if p['path'] == 'README.md']
    assert [p['status'] for p in readme] == ['SUPERSEDED', 'PROPOSED']
    assert readme[-1]['base_sha256'] == sha256('# mío\n'.encode()).hexdigest()
    world.apply(cid, readme[-1])  # el turno ya leyó la edición del usuario: la CAS coincide
    assert world.path('README.md').read_text() == '# propuesto\n'


# --- archivos ajenos y bloqueos ------------------------------------------------------------------


@pytest.mark.parametrize('foreign', ['notes.txt', '.DS_Store', 'docs/other.md', 'docs/research/spike.md',
                                     'docs/decisions/sub/D002-x.md', 'app/main.py', 'link'])
def test_foreign_files_block_acceptance_and_are_preserved(world, foreign, tmp_path):
    cid = ready(world)
    target = world.path(foreign)
    target.parent.mkdir(parents=True, exist_ok=True)
    if foreign == 'link':
        target.symlink_to(tmp_path)
    else:
        target.write_bytes(b'foreign')
    shown = world.preview(cid)
    assert not shown['ready'] and any('outside the definition drafts' in item for item in shown['blockers'])
    assert shown['documents'] == []
    with pytest.raises(Conflict, match='import required|Preview changed'):
        world.accept(cid, shown)
    assert world.bootstrap.get(world.context.root) is None and not world.path('.git').exists()
    assert target.is_symlink() if foreign == 'link' else target.read_bytes() == b'foreign'


def test_git_metadata_requires_import(world):
    cid = ready(world)
    git(world.context.root, 'init', '-q', '-b', 'main')
    shown = world.preview(cid)
    assert not shown['ready'] and shown['target']['import_required']
    with pytest.raises(Conflict, match='import'):
        world.message(cid)


BLOCKERS = {
    'missing': ({'docs/ARCHITECTURE.md': None}, 'Required documents are missing: docs/ARCHITECTURE.md'),
    'no_phases': ({'docs/ROADMAP.md': f'# Roadmap\n\n{ROAD_BEGIN}\n{ROAD_END}\n'}, 'at least one phase'),
    'no_criteria': ({'docs/ROADMAP.md': '# Roadmap\n\n## P001 — Fundamentos\n\n**Objetivo:** algo.\n'},
                    'P001 needs an objective and at least one exit criterion'),
    'first_not_p001': ({'docs/ROADMAP.md': '# Roadmap\n\n## P002 — Otra\n\n**Objetivo:** o\n**Criterios de salida:**\n- c\n'},
                       'first ROADMAP phase must be P001'),
    'wrong_task': ({'docs/NEXT_STEPS.md': '# P001\n\n## P002-T001 — Otra\n\n**Objetivo:** o\n'},
                   'must belong to phase P001'),
    'no_task': ({'docs/NEXT_STEPS.md': '# P001\n\nSin tareas.\n'}, 'at least one P001-TNNN task'),
    'no_criteria_task': ({'docs/NEXT_STEPS.md': '# P001\n\n## P001-T001 — Tarea\n\n**Objetivo:** o\n'},
                         'needs an objective and acceptance criteria'),
    'foreign_block': ({'README.md': f'# R\n\n{ROAD_BEGIN}\n{ROAD_END}\n'}, 'managed blocks that belong to another'),
    'partial_marker': ({'docs/STATE.md': f'# Estado\n\n{STATE_BEGIN}\n'}, 'docs/STATE.md:'),
    'invalid_utf8': ({'docs/SPECIFICATION.md': b'\xff\xfe'}, 'Drafts must be UTF-8'),
    'executable': ({'docs/SPECIFICATION.md': 0o755}, 'Drafts must be UTF-8'),
}


@pytest.mark.parametrize('case', sorted(BLOCKERS))
def test_acceptance_blockers_are_explicit_and_fail_closed(world, case):
    cid = ready(world)
    changes, expected = BLOCKERS[case]
    for path, content in changes.items():
        if content is None:
            world.path(path).unlink()
        elif isinstance(content, bytes):
            world.path(path).write_bytes(content)
        elif isinstance(content, int):
            world.path(path).chmod(content)
        else:
            world.path(path).write_text(content)
    shown = world.preview(cid)
    assert not shown['ready'] and any(expected in item for item in shown['blockers']), shown['blockers']
    with pytest.raises(Conflict):
        world.accept(cid, shown)
    assert world.bootstrap.get(world.context.root) is None


def test_deterministic_mode_requires_a_complete_first_task(world):
    world.context = replace(world.context, policy=replace(world.context.policy, planning_mode='deterministic'))
    cid = world.create()
    plan = '# P001\n\n## P001-T001 — Tarea\n\n**Objetivo:** o\n**Criterios de aceptación:**\n- c\n'
    world.turn(cid, answer(drafts={**DRAFTS, 'docs/NEXT_STEPS.md': plan}))
    world.apply_all(cid)
    shown = world.preview(cid)
    assert any('deterministic planning mode' in item for item in shown['blockers'])
    world.context = replace(world.context, policy=replace(world.context.policy, planning_mode='agent'))
    shown = world.preview(cid)
    assert shown['ready'] and shown['first_task'] == {'task_id': 'P001-T001', 'title': 'Tarea', 'planner': 'agent'}


def test_blocking_question_deferred_explicitly_unblocks_acceptance(world):
    cid = world.create()
    world.turn(cid, answer(questions=[QUESTION, {'text': 'Opcional', 'blocking': False}]))
    world.apply_all(cid)
    question = world.view(cid)['questions'][0]
    with pytest.raises(LookupError):
        world.planning.defer(cid, world.view(cid)['version'], question_id='0' * 64, reason='x')
    with pytest.raises(Conflict, match='Only an open blocking'):
        world.planning.defer(cid, world.view(cid)['version'], question_id=world.view(cid)['questions'][1]['id'],
                             reason='x')
    world.planning.defer(cid, world.view(cid)['version'], question_id=question['id'], reason='Se decide en P002')
    shown = world.preview(cid)
    assert shown['ready'] and 'aplazada: Se decide en P002' in next(
        d['content'] for d in shown['documents'] if d['path'].endswith('DEFINITION.md'))


def test_changed_conversation_or_drafts_invalidate_the_reviewed_preview(world):
    cid = ready(world)
    shown = world.preview(cid)
    world.path('docs/SPECIFICATION.md').write_text('# Especificación cambiada\n')
    with pytest.raises(Conflict, match='Preview changed'):
        world.accept(cid, shown)
    shown = world.preview(cid)
    world.message(cid, 'Una pregunta más')
    with pytest.raises(Conflict, match='turn is pending'):
        world.accept(cid, shown)
    world.ports.agents.responses.append(answer(drafts={}))
    assert world.worker.run_once().status == 'DONE'
    with pytest.raises(Conflict, match='Preview changed'):
        world.accept(cid, shown)
    assert world.bootstrap.get(world.context.root) is None


def test_bootstrap_replaces_drafts_only_from_their_reviewed_bytes(world, monkeypatch):
    """Un borrador editado tras encolar se conserva; el job falla cerrado sin `.git`."""
    cid = ready(world)
    job = world.accept(cid)
    world.path('docs/STATE.md').write_text('# editado tras confirmar\n')
    with pytest.raises(ValueError, match='Bootstrap draft changed'):
        world.worker.run_once()
    assert world.path('docs/STATE.md').read_text() == '# editado tras confirmar\n'
    assert not world.path('.git').exists() and world.repo.get_job(job.id).status == 'RECOVERY_REQUIRED'


@pytest.mark.parametrize('point', ['replace', 'commit'])
def test_bootstrap_crash_resumes_the_same_intent(world, monkeypatch, point):
    from harness_local.adapters import bootstrap as filesystem
    cid = ready(world)
    job = world.accept(cid)
    if point == 'replace':
        real = filesystem._replace_file
        calls = []

        def fail(*args):
            real(*args)
            calls.append(args[0])
            raise RuntimeError('synthetic crash after replacing a draft')
        monkeypatch.setattr(filesystem, '_replace_file', fail)
    else:
        real = world.writer.execute_bootstrap

        def fail(*args):
            real(*args)
            raise RuntimeError('synthetic crash after commit')
        monkeypatch.setattr(world.writer, 'execute_bootstrap', fail)
    with pytest.raises(RuntimeError, match='synthetic'):
        world.worker.run_once()
    intent = world.bootstrap.get(world.context.root)['intent']
    world.repo.confirm_stopped(job.id, owner_token=world.repo.get_job(job.id).owner_token,
                               expected_version=world.repo.get_run(job.run_id).version, reason='Synthetic stop')
    monkeypatch.setattr(filesystem, '_replace_file', filesystem._replace_file if point == 'commit' else real)
    if point == 'commit':
        monkeypatch.setattr(world.writer, 'execute_bootstrap', real)
    shown = world.preview(cid)
    assert shown['resume_operation_id'] is not None
    resumed = world.accept(cid, shown)
    assert resumed.run_id == job.run_id and world.worker.run_once().status == 'DONE'
    op = world.bootstrap.get(world.context.root)
    assert op['status'] == 'COMPLETED' and op['intent'] == intent
    assert git(world.context.root, 'rev-parse', 'HEAD') == intent['commit']
    assert git(world.context.root, 'status', '--porcelain') == ''
    with Session(world.repo.engine) as session:
        assert session.scalar(text('SELECT count(*) FROM managed_phases')) == 1


def test_turn_crash_is_unknown_and_never_retried(world):
    cid = world.create()
    job = world.message(cid)

    def crash(context, request):
        raise JournalError('synthetic turn crash')
    world.ports.agents.responses.append(crash)
    with pytest.raises(JournalError):
        world.worker.run_once()
    assert world.worker.run_once() is None
    world.repo.confirm_stopped(job.id, owner_token=world.repo.get_job(job.id).owner_token,
                               expected_version=world.repo.get_run(job.run_id).version, reason='Synthetic stop')
    assert world.view(cid)['turns'][-1]['status'] == 'UNKNOWN' and world.worker.run_once() is None
    assert world.ports.roles() == ['definition'] and world.view(cid)['actions'][0] == 'message'


# --- compatibilidad ------------------------------------------------------------------------------


def test_v1_flows_are_refused_for_v2_and_v2_flows_for_v1(world, tmp_path):
    from test_bootstrap import DATA
    from harness_local.storage.bootstrap_discovery import DiscoveryRepository
    with pytest.raises(ValueError, match='definition conversation'):
        world.bootstrap.preview(world.context, DATA, VERSIONS, world.writer)
    with pytest.raises(ValueError, match='definition conversation'):
        DiscoveryRepository(world.repo).submit(world.context, DATA['brief'], VERSIONS, world.writer, key='d',
                                               confirmed=True)
    v1 = tmp_path / 'v1-destination'
    v1.mkdir()
    with pytest.raises(ValueError, match='documents = "v2"'):
        world.planning.create(make_context(v1), kind='definition', title='x', brief=BRIEF, writer=world.writer)
    shown = world.bootstrap.preview(make_context(v1), DATA, VERSIONS, world.writer)
    assert shown['ready'] and len(shown['documents']) == 6 and 'definition' not in shown
    with pytest.raises(ValueError, match='256 KiB'):
        world.planning.create(world.context, kind='definition', title='x', brief='x' * (256 * 1024 + 1),
                              writer=world.writer)
    world.create()
    with pytest.raises(Conflict, match='already has a definition'):
        world.create()


def test_migration_roundtrip_and_guard(migrated_database, world):
    _, config = migrated_database
    command.check(config)
    command.downgrade(config, '0014_attempt_metrics')
    command.upgrade(config, 'head')
    command.check(config)
    world.create()
    with pytest.raises(RuntimeError, match='0015'):
        command.downgrade(config, '0014_attempt_metrics')


# --- planificación de la fase siguiente ----------------------------------------------------------


def planning_answer(plan=PLAN_P002, text='Plan propuesto'):
    return {'answer': text, 'questions': [], 'pending': [],
            'plan': None if plan is None else {'content': plan, 'reason': 'Tareas de P002 según ROADMAP'}}


def test_phase_planning_proposes_the_plan_used_by_the_transition(v2):  # noqa: F811
    pid = v2.create_v2()
    v2.accept()
    planning = PlanningRepository(v2.repository)
    cid = planning.create(v2.context, kind='phase_planning', title='Plan P002', phase_id=pid)
    v2.ports.agents.responses.append(planning_answer())
    job = planning.submit_message(v2.context, cid, planning.get(cid)['version'], key='plan-1', versions=VERSIONS,
                                  text='Propón el plan de P002')
    v2.run()
    turn = planning.get(cid)['turns'][-1]
    assert turn['status'] == 'ANSWERED', turn['result']
    context = planning.snapshot(job.run_id)['context']
    assert context['next']['code'] == 'P002' and context['base'].startswith('## Base acumulada')
    assert context['phase']['summary']['phase']['code'] == 'P001'
    request = v2.repository.get_run(job.run_id).history.attempts[-1].request
    assert request.role == 'planning'
    assert json.loads(request.prompt_snapshot_json)['parts'][0]['version']['name'] == 'plan-phase'
    proposal = planning.get(cid)['proposals'][0]
    assert proposal['kind'] == 'plan' and proposal['actions'] == ['dismiss']
    v2.close_ready(pid)
    reference = {'conversation_id': cid, 'proposal_id': proposal['id'], 'proposal_sha256': proposal['proposal_sha256']}
    writer = v2.ports.writer(v2.context, VERSIONS)
    with pytest.raises(ValueError, match='either the plan text or a plan proposal'):
        transitions(v2).preview(v2.context, pid, writer, PLAN_P002, reference)
    with pytest.raises(Conflict, match='exact plan proposal'):
        transitions(v2).preview(v2.context, pid, writer, None, {**reference, 'proposal_sha256': '0' * 64})
    view = transitions(v2).preview(v2.context, pid, writer, None, reference)
    plain = transitions(v2).preview(v2.context, pid, writer, PLAN_P002)
    assert view['plan_origin']['proposal_id'] == proposal['id'] and 'plan_origin' not in plain
    assert view['documents'] == plain['documents'] and view['preview_sha256'] != plain['preview_sha256']
    job = transitions(v2).submit(v2.context, pid, view['expected_version'], key='planned-transition', versions=VERSIONS,
                                 preview_sha256=view['preview_sha256'], reason='Plan propuesto y revisado',
                                 confirmed=True, git=writer, plan_proposal=reference)
    assert planning.get(cid)['proposals'][0]['status'] == 'ACCEPTED'
    v2.run()
    assert v2.repository.get_run(job.run_id).status == 'COMMITTED'
    assert v2.context.path('docs/NEXT_STEPS.md').read_text().startswith(PLAN_P002)
    with Session(v2.repository.engine) as session:
        assert session.scalar(select(PhaseRow.status).where(PhaseRow.code == 'P002')) == 'ACTIVE'
        decision = session.scalar(select(PlanningProposalRow.decision))
        assert decision['run_id'] == job.run_id


@pytest.mark.parametrize('plan', ['# P002\n\n## P003-T001 — Otra\n\n**Objetivo:** o\n', '# P002\n\nSin tareas.\n'])
def test_phase_planning_rejects_a_plan_of_another_phase(v2, plan):  # noqa: F811
    pid = v2.create_v2()
    planning = PlanningRepository(v2.repository)
    cid = planning.create(v2.context, kind='phase_planning', title='Plan', phase_id=pid)
    v2.ports.agents.responses.append(planning_answer(plan))
    planning.submit_message(v2.context, cid, 0, key='bad-plan', versions=VERSIONS, text='Plan')
    v2.run()
    turn = planning.get(cid)['turns'][-1]
    assert turn['status'] == 'FAILED' and planning.get(cid)['proposals'] == []


def test_phase_planning_turn_that_changes_the_checkout_is_discarded(v2):  # noqa: F811
    pid = v2.create_v2()
    planning = PlanningRepository(v2.repository)
    cid = planning.create(v2.context, kind='phase_planning', title='Plan', phase_id=pid)

    def writes(context, request):
        context.path('app/main.txt').write_text('changed by planner\n')
        return planning_answer()
    v2.ports.agents.responses.append(writes)
    planning.submit_message(v2.context, cid, 0, key='writing-plan', versions=VERSIONS, text='Plan')
    v2.run()
    assert planning.get(cid)['turns'][-1]['status'] == 'FAILED' and planning.get(cid)['proposals'] == []


# --- HTTP --------------------------------------------------------------------------------------------


def test_http_definition_flow(migrated_database, tmp_path):
    root = tmp_path / 'http-destination'
    root.mkdir()
    context = replace(make_context(root), documents='v2')
    ports = Ports([answer()])
    configuration = ManagedConfig((ManagedProject('fresh', context, VERSIONS, bootstrap_enabled=True),),
                                  ports_factory=ports, commit_factory=ports.writer, supervisor=False)
    url = migrated_database[0]
    with client(url, tmp_path, configuration) as http:
        base = '/api/managed/projects/fresh'
        status = http.get(base + '/bootstrap').json()
        assert status['enabled'] and not status['import_required'] and not status['discovery_available']
        assert http.post(base + '/bootstrap/preview', json={'brief': {}, 'decisions': {}}).status_code == 422
        created = http.post(base + '/planning', json={'kind': 'definition', 'title': 'Sintético', 'brief': BRIEF})
        assert created.status_code == 201, created.text
        cid = created.json()['id']
        assert http.post(base + '/planning', json={'kind': 'definition', 'title': 'Otra', 'brief': BRIEF}).status_code == 409
        assert http.get(base + f'/planning/{cid}/brief').json()['content'] == BRIEF
        message = http.post(base + f'/planning/{cid}/messages', json={'expected_version': 0, 'text': 'Propón'},
                            headers={'Idempotency-Key': 'm1'})
        assert message.status_code == 202, message.text
        engine = make_engine(url)
        worker = LocalSupervisor(SQLiteManagedRepository(engine), ports, commit_factory=ports.writer)
        assert worker.run_once().status == 'DONE'
        detail = http.get(base + f'/planning/{cid}').json()
        assert detail['turns'][0]['status'] == 'ANSWERED' and detail['actions'] == [
            'message', 'edit_draft', 'defer_question', 'accept']
        for proposal in detail['proposals']:
            version = http.get(base + f'/planning/{cid}').json()['version']
            applied = http.post(base + f"/planning/{cid}/proposals/{proposal['id']}/apply", json={
                'expected_version': version, 'proposal_sha256': proposal['proposal_sha256'], 'confirmed': True})
            assert applied.status_code == 200, applied.text
        drafts = http.get(base + f'/planning/{cid}/drafts').json()
        assert not any(d['user_edited'] for d in drafts['drafts']) and drafts['foreign'] == []
        version = http.get(base + f'/planning/{cid}').json()['version']
        edit = http.put(base + f'/planning/{cid}/drafts', json={
            'expected_version': version, 'path': 'README.md', 'content': '# API\n',
            'base_sha256': sha256(DRAFTS['README.md'].encode()).hexdigest()})
        assert edit.status_code == 200, edit.text
        stale = http.put(base + f'/planning/{cid}/drafts', json={
            'expected_version': edit.json()['version'], 'path': 'README.md', 'content': '# otra\n', 'base_sha256': None})
        assert stale.status_code == 409
        drafts = http.get(base + f'/planning/{cid}/drafts').json()
        assert [d['path'] for d in drafts['drafts'] if d['user_edited']] == ['README.md']
        preview = http.post(base + f'/planning/{cid}/accept/preview')
        assert preview.status_code == 200, preview.text
        shown = preview.json()
        assert shown['ready'], shown['blockers']
        body = {'preview_sha256': shown['preview_sha256'], 'confirmed': True, 'reason': 'HTTP',
                'resume_operation_id': None, 'expected_version': None}
        assert http.post(base + f'/planning/{cid}/accept', json=body).status_code == 422  # sin Idempotency-Key
        accepted = http.post(base + f'/planning/{cid}/accept', json=body, headers={'Idempotency-Key': 'accept'})
        assert accepted.status_code == 202, accepted.text
        assert worker.run_once().status == 'DONE'
        status = http.get(base + '/bootstrap').json()
        assert status['operation'] is None and status['definition_operation']['status'] == 'COMPLETED'
        detail = http.get(base + f'/planning/{cid}').json()
        assert detail['created'] and detail['operation']['phase_id'] and detail['actions'] == []
        assert http.get(f"/api/managed/runs/{detail['turns'][0]['run_id']}").json()['purpose'] == 'definition'
        assert [p['code'] for p in http.get(base + '/phases').json()] == ['P001']
        schema = http.app.openapi()['paths']
        assert {'/api/managed/projects/{project_id}/planning',
                '/api/managed/projects/{project_id}/planning/{conversation_id}/accept'} <= set(schema)
        engine.dispose()
    assert git(root, 'rev-list', '--count', 'HEAD') == '1'
    assert decision_index({'D001-usar-perfil.md': DRAFTS['docs/decisions/D001-usar-perfil.md']})[0]['id'] == 'D001'
    assert [entry['code'] for entry in parse_roadmap((root / 'docs/ROADMAP.md').read_text())] == ['P001', 'P002']

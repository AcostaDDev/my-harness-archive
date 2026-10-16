"""P008-T011: conversación `project_import` del Flujo A con Git/SQLite temporales y agentes falsos; sin proveedores.

Los orígenes son los checkouts sintéticos de T009 (tipo ReferenceProject sin runs, v1 y v2). Se comprueba que la
conversación congela inventario, mapa y contenidos, que el revisor solo propone y nunca escribe, que los borradores
viven en el área privada junto a SQLite con CAS, que un turno inválido falla sin fallback y que las preguntas
bloqueantes impiden pasar a la vista previa hasta responderlas o aplazarlas.
"""
from dataclasses import replace
from hashlib import sha256
import json
import os
from pathlib import Path
import stat

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from harness_local.adapters.git import GitWorkspace
from harness_local.core.engine.definition import KINDS
from harness_local.core.engine.import_conversation import MAX_SOURCE_BYTES
from harness_local.services.managed import LocalSupervisor
from harness_local.services.managed_runtime import ManagedConfig, ManagedProject
from harness_local.storage.database import make_engine
from harness_local.storage.import_drafts import AREA, ImportDrafts
from harness_local.storage.managed import Conflict, SQLiteManagedRepository
from harness_local.storage.models import ManagedRunRow, PhaseRow, PlanningConversationRow
from harness_local.storage.planning import PlanningRepository
from test_managed_api import IDENTITY, VERSIONS, Ports, client, make_context
from test_project_import import REFERENCE_PROJECT, V1, V2, checkout, git, write_tree

AGENTS = '# Synthetic gym — agentes\n\n' + ''.join(f'- Regla {n}.\n' for n in range(1, 31))
CLAUDE = '# Claude\n\n@AGENTS.md\n'
DRAFTS = {
    'AGENTS.md': AGENTS,
    'CLAUDE.md': CLAUDE,
    'docs/SPECIFICATION.md': '# Especificación — Synthetic gym\n\nVisión sintética.\n\n- Synthetic requirement.\n',
    'docs/DDBB-DIAGRAM.md': '# Modelo de datos\n\nSin persistencia.\n',
    'docs/flows/members.md': '# Miembros\n\n```mermaid\nflowchart LR\n  list --> detail\n```\n',
}
QUESTION = {'text': '¿La fase activa es P002?', 'blocking': True}


def answer(drafts=None, questions=(), pending=(), text='Fusiones y adelgazamiento propuestos'):
    return {'answer': text, 'questions': list(questions), 'pending': list(pending),
            'drafts': [{'path': path, 'content': content, 'reason': f'Propuesta para {path}'}
                       for path, content in (DRAFTS if drafts is None else drafts).items()]}


class World:
    def __init__(self, root, engine):
        self.context = replace(make_context(root), documents='v2')
        self.repo = SQLiteManagedRepository(engine)
        self.writer = GitWorkspace(IDENTITY)
        self.ports = Ports()
        self.worker = LocalSupervisor(self.repo, self.ports, commit_factory=lambda c, v: self.writer)
        self.planning = PlanningRepository(self.repo)
        self.engine, self.keys = engine, 0

    def key(self):
        self.keys += 1
        return f'import-{self.keys}'

    def create(self, **kwargs):
        return self.planning.create(self.context, kind='project_import', title='Synthetic gym', writer=self.writer,
                                    **kwargs)

    def view(self, cid):
        return self.planning.get(cid)

    def message(self, cid, text='Propón las fusiones'):
        return self.planning.submit_message(self.context, cid, self.view(cid)['version'], key=self.key(),
                                            versions=VERSIONS, text=text, writer=self.writer)

    def turn(self, cid, response, text='Propón las fusiones'):
        job = self.message(cid, text)
        self.ports.agents.responses.append(response)
        assert self.worker.run_once().status == 'DONE'
        return job, self.view(cid)['turns'][-1]

    def apply_all(self, cid):
        for proposal in self.view(cid)['proposals']:
            if proposal['status'] == 'PROPOSED':
                self.planning.apply(self.context, cid, proposal['id'], self.view(cid)['version'],
                                    proposal_sha256=proposal['proposal_sha256'], confirmed=True, writer=None)

    def status(self, cid):
        return self.planning.import_status(self.context, cid, self.writer)

    def area(self, cid) -> Path:
        return Path(self.engine.url.database).resolve().parent / AREA / cid


@pytest.fixture
def world(migrated_database, tmp_path):
    engine = make_engine(migrated_database[0])
    # Sin `.harness/runs`: un checkout con runs legacy sin activar sigue rechazado por la guardia D027.
    root = checkout(tmp_path, 'reference_project', REFERENCE_PROJECT)
    yield World(root, engine)
    engine.dispose()


def tree_state(root: Path) -> dict:
    """Bytes del checkout y de `.git` (salvo nada): ninguna operación de T011 los cambia."""
    return {path.relative_to(root).as_posix(): sha256(path.read_bytes()).hexdigest()
            for path in sorted(root.rglob('*')) if path.is_file()}


# --- recorrido ------------------------------------------------------------------------------------


def test_import_conversation_freezes_source_and_never_writes_the_checkout(world):
    before = tree_state(world.context.root)
    cid = world.create()
    view = world.view(cid)
    assert view['kind'] == 'project_import' and view['actions'] == ['message', 'edit_draft', 'defer_question']
    assert view['source']['origin'] == 'reference_project' and view['source']['active_phase'] == 'P002'
    with Session(world.engine) as session:
        source = session.get(PlanningConversationRow, cid).source
    assert source['inventory']['inventory_sha256'] == view['source']['inventory_sha256']
    assert source['map']['map_sha256'] == view['source']['map_sha256']
    assert {move['source'] for move in source['map']['moves']} == {'docs/DECISSONS.md'}

    job, turn = world.turn(cid, answer(questions=[QUESTION], pending=['Confirmar la fase activa']))
    assert turn['status'] == 'ANSWERED'
    assert tree_state(world.context.root) == before and not world.area(cid).exists()  # el agente no escribe
    request = world.repo.get_run(job.run_id).history.attempts[0].request
    assert request.role == 'definition' and request.fresh_session
    assert json.loads(request.prompt_snapshot_json)['parts'][0]['version']['name'] == 'import-project'
    assert 'project_instructions' not in json.loads(request.prompt_snapshot_json)
    frozen = world.planning.snapshot(job.run_id)['context']
    assert frozen['kind'] == 'project_import' and frozen['source']['map_sha256'] == view['source']['map_sha256']
    sources = {item['path']: item for item in frozen['sources']}
    # Árbol resultante del mapa: DECISSONS ya renombrado; la fuente de SPECIFICATION llega íntegra.
    assert 'docs/DECISIONS.md' in sources and 'docs/DECISSONS.md' not in sources
    assert sources['docs/PROJECT.md']['content'] == REFERENCE_PROJECT['docs/PROJECT.md']
    assert {item['path'] for item in frozen['listed']} >= {'docs/archive/phase-001/REVIEW.md', '.harness/config.yaml'}
    assert 'Synthetic requirement.' in request.prompt and view['source']['map_sha256'] in request.prompt
    with Session(world.engine) as session:
        assert session.get(ManagedRunRow, job.run_id).purpose == 'project_import'

    status = world.status(cid)
    assert not status['ready']
    assert any('Blocking questions' in item for item in status['blockers'])
    assert 'AGENTS.md (imported document) must contain at most 60 lines (D088)' in status['blockers']
    assert 'CLAUDE.md (imported document) must contain at most 15 lines (D088)' in status['blockers']

    world.apply_all(cid)
    assert tree_state(world.context.root) == before
    for path, content in DRAFTS.items():
        assert (world.area(cid) / path).read_text() == content
    assert stat.S_IMODE(world.area(cid).parent.stat().st_mode) == 0o700
    status = world.status(cid)
    assert status['blockers'] == [
        'Blocking questions remain open; answer them in a turn or defer them explicitly: ¿La fase activa es P002?']
    assert status['drafts'] == {path: sha256(content.encode()).hexdigest() for path, content in DRAFTS.items()}
    assert 'Supplied by the template unless drafted: GEMINI.md' in status['warnings']
    assert 'Map entry for the reviewer: docs/PROJECT.md (merge-proposal)' in status['warnings']

    # Preguntas bloqueantes: aplazar con motivo deja pasar a la vista previa; responderlas en un turno, también.
    question = world.view(cid)['questions'][0]
    world.planning.defer(cid, world.view(cid)['version'], question_id=question['id'], reason='Se decide en T012')
    assert world.status(cid)['ready']
    assert tree_state(world.context.root) == before


def test_answering_the_question_in_a_turn_unblocks_and_user_edits_are_frozen(world):
    cid = world.create()
    world.turn(cid, answer(questions=[QUESTION]))
    world.apply_all(cid)
    assert not world.status(cid)['ready']
    edited = AGENTS + '- Regla del usuario.\n'
    world.planning.edit_draft(world.context, cid, world.view(cid)['version'], path='AGENTS.md', content=edited,
                              base_sha256=sha256(AGENTS.encode()).hexdigest(), writer=None)
    (world.area(cid) / 'docs/SPECIFICATION.md').write_text('# Editado a mano\n')
    job, turn = world.turn(cid, answer(drafts={}, text='P002 confirmada'), text='Sí, P002')
    assert turn['status'] == 'ANSWERED' and world.view(cid)['questions'] == []
    edits = world.planning.snapshot(job.run_id)['context']['user_edits']
    assert {item['path'] for item in edits} == {'AGENTS.md', 'docs/SPECIFICATION.md'}
    assert 'Regla del usuario.' in world.repo.get_run(job.run_id).history.attempts[0].request.prompt
    status = world.status(cid)
    assert status['ready'], status['blockers']


@pytest.mark.parametrize('files,origin,drafted,initial', [
    (V1, 'v1', {'AGENTS.md': AGENTS, 'CLAUDE.md': CLAUDE, 'GEMINI.md': '# Gemini\n\n@AGENTS.md\n',
                'docs/SPECIFICATION.md': '# Especificación\n', 'docs/ARCHITECTURE.md': '# Arquitectura\n',
                'docs/ROADMAP.md': '# Roadmap\n\n## P001 — Base\n\n**Objetivo:** Base.\n'},
     ['Required documents are missing from the map and the drafts: docs/SPECIFICATION.md, docs/ARCHITECTURE.md, '
      'docs/ROADMAP.md']),
    # v2: el mapa ya resuelve los documentos; AGENTS y GEMINI saldrían de la plantilla y lo demás son avisos.
    (V2, 'v2', {'AGENTS.md': AGENTS}, []),
])
def test_v1_and_v2_sources_reach_the_preview_gate(migrated_database, tmp_path, files, origin, drafted, initial):
    engine = make_engine(migrated_database[0])
    world = World(checkout(tmp_path, origin, files), engine)
    cid = world.create()
    assert world.view(cid)['source']['origin'] == origin
    status = world.status(cid)
    assert status['blockers'] == initial and status['ready'] == (not initial)
    if origin == 'v2':
        assert 'Supplied by the template unless drafted: AGENTS.md, GEMINI.md' in status['warnings']
        assert 'Map entry for the reviewer: docs/architecture/checkout.md (merge-proposal)' in status['warnings']
    world.turn(cid, answer(drafts=drafted))
    world.apply_all(cid)
    status = world.status(cid)
    assert status['ready'], status['blockers']
    engine.dispose()


# --- turnos inválidos ---------------------------------------------------------------------------


@pytest.mark.parametrize('response,reason', [
    (answer(drafts={'docs/PROJECT.md': '# Fusionado\n'}), 'outside the D088 template'),
    (answer(drafts={'src/app.py': 'print(1)\n'}), 'outside the D088 template'),
    (answer(drafts={'docs/archive/phase-001/SUMMARY.md': '# Otro\n'}), 'outside the D088 template'),
    ({'answer': 'sin borradores'}, 'exactly answer, questions, drafts and pending'),
])
def test_invalid_turn_fails_without_fallback_and_without_writes(world, response, reason):
    before = tree_state(world.context.root)
    cid = world.create()
    _, turn = world.turn(cid, response)
    assert turn['status'] == 'FAILED' and any(reason in item for item in turn['result']['reasons'])
    assert world.view(cid)['proposals'] == [] and len(world.ports.agents.requests) == 1  # sin reintento
    assert tree_state(world.context.root) == before and not world.area(cid).exists()


def test_an_agent_that_writes_during_the_turn_is_discarded(world):
    cid = world.create()

    def write_checkout(context, request):
        context.path('docs/PROJECT.md').write_text('# Cambiado por el agente\n')
        return answer()

    _, turn = world.turn(cid, write_checkout)
    assert turn['status'] == 'FAILED' and 'could not be re-observed' in turn['result']['reasons'][0]
    assert world.view(cid)['proposals'] == []
    git(world.context.root, 'checkout', '--', 'docs/PROJECT.md')

    def write_area(context, request):
        target = world.area(cid) / 'docs'
        target.mkdir(parents=True)
        (target / 'STATE.md').write_text('# Escrito por el agente\n')
        return answer()

    _, turn = world.turn(cid, write_area)
    assert turn['status'] == 'FAILED' and 'changed during a read-only turn' in turn['result']['reasons'][0]
    assert world.view(cid)['proposals'] == []


# --- origen y área --------------------------------------------------------------------------------


def test_checkout_changes_refuse_turns_and_block_the_preview(world):
    cid = world.create()
    root = world.context.root
    (root / 'docs/PROJECT.md').write_text('# Sin confirmar\n')
    with pytest.raises(Conflict, match='uncommitted changes'):
        world.message(cid)
    assert 'The checkout could not be read' in world.status(cid)['blockers'][0]
    git(root, 'commit', '-qam', 'cambio posterior')
    with pytest.raises(Conflict, match='changed since the import conversation started'):
        world.message(cid)
    assert any('changed since the import conversation started' in item for item in world.status(cid)['blockers'])
    assert world.view(cid)['turns'] == []


def test_queued_turn_refuses_when_the_checkout_changes_before_it_runs(world):
    cid = world.create()
    world.message(cid)
    write_tree(world.context.root, {'docs/PROJECT.md': '# Commit nuevo\n'})
    git(world.context.root, 'commit', '-qam', 'cambio tras encolar')
    world.ports.agents.responses.append(answer())
    assert world.worker.run_once().status == 'DONE'
    turn = world.view(cid)['turns'][-1]
    assert turn['status'] == 'FAILED' and 'Drafts changed after the message was queued' in turn['result']['reasons'][0]
    assert world.ports.agents.requests == []  # ni se invoca


def test_create_refusals(world, tmp_path):
    with pytest.raises(ValueError, match='no brief or phase'):
        world.create(brief='# Brief\n')
    (world.context.root / 'docs/notes.md').write_text('sin seguimiento\n')
    with pytest.raises(Conflict, match='cannot be imported: The checkout has uncommitted changes'):
        world.create()
    (world.context.root / 'docs/notes.md').unlink()
    cid = world.create()
    empty = tmp_path / 'not-git'
    empty.mkdir()
    with pytest.raises(Conflict, match='Not a Git checkout'):
        world.planning.create(replace(world.context, root=empty), kind='project_import', title='x',
                              writer=world.writer)
    with Session(world.engine) as session, session.begin():
        session.add(PhaseRow(id='phase-1', root=str(world.context.root), code='P001', status='ACTIVE',
                             definition={'tasks': []}, definition_sha256='0' * 64, documents={}, version=0,
                             created_at='2026-10-16T00:00:00Z', updated_at='2026-10-16T00:00:00Z'))
    with pytest.raises(Conflict, match='already has managed phases'):
        world.create()
    with pytest.raises(Conflict, match='already has managed phases'):
        world.message(cid)


def test_draft_area_cas_and_paths(world):
    cid = world.create()
    with pytest.raises(ValueError, match='not an allowed definition draft'):
        world.planning.edit_draft(world.context, cid, world.view(cid)['version'], path='docs/PROJECT.md',
                                  content='x\n', base_sha256=None, writer=None)
    world.planning.edit_draft(world.context, cid, world.view(cid)['version'], path='docs/STATE.md',
                              content='# Estado\n', base_sha256=None, writer=None)
    with pytest.raises(Conflict, match='nothing was overwritten'):
        world.planning.edit_draft(world.context, cid, world.view(cid)['version'], path='docs/STATE.md',
                                  content='# Otro\n', base_sha256=None, writer=None)
    assert (world.area(cid) / 'docs/STATE.md').read_text() == '# Estado\n'
    assert not (world.context.root / 'docs/STATE.md').read_text().startswith('# Estado\n')
    drafts = world.planning.drafts(world.context, cid, None)
    assert [d['path'] for d in drafts['drafts']] == ['docs/STATE.md'] and drafts['drafts'][0]['user_edited']
    assert world.planning.draft(world.context, cid, 'docs/STATE.md', None)['content'] == '# Estado\n'
    (world.area(cid) / 'notes.txt').write_text('ajeno\n')
    (world.area(cid) / 'docs/flows').mkdir()
    (world.area(cid) / 'docs/flows/run.md').write_text('# x\n')
    os.chmod(world.area(cid) / 'docs/flows/run.md', 0o755)
    drafts = world.planning.drafts(world.context, cid, None)
    assert drafts['foreign'] == ['notes.txt'] and drafts['invalid'] == ['docs/flows/run.md']
    assert any('Drafts must be UTF-8' in item for item in world.status(cid)['blockers'])
    with pytest.raises(ValueError, match='Invalid import conversation id'):
        ImportDrafts.of(world.engine, '../escape')


def test_turn_context_size_is_bounded(world, monkeypatch):
    cid = world.create()
    world.planning.edit_draft(world.context, cid, world.view(cid)['version'], path='docs/ARCHITECTURE.md',
                              content='x' * (512 * 1024 - 1), base_sha256=None, writer=None)
    from harness_local.core.engine import import_conversation
    monkeypatch.setattr(import_conversation, 'MAX_SOURCE_BYTES', 512 * 1024)
    with pytest.raises(ValueError, match='exceed'):
        world.message(cid)
    assert MAX_SOURCE_BYTES == 2 * 1024 * 1024


def test_import_kind_reuses_the_read_only_definition_role():
    assert KINDS['project_import'] == ('import-project', 'definition')


# --- HTTP -------------------------------------------------------------------------------------------


def test_http_import_flow(migrated_database, tmp_path):
    root = checkout(tmp_path, 'reference_project', REFERENCE_PROJECT)
    context = replace(make_context(root), documents='v2')
    ports = Ports([answer(questions=[QUESTION])])
    configuration = ManagedConfig((ManagedProject('gym', context, VERSIONS),), ports_factory=ports,
                                  commit_factory=ports.writer, supervisor=False)
    url = migrated_database[0]
    before = tree_state(root)
    with client(url, tmp_path, configuration) as http:
        base = '/api/managed/projects/gym'
        body = {'kind': 'project_import', 'title': 'Synthetic gym', 'brief': None, 'phase_id': None}
        created = http.post(base + '/planning', json=body, headers={'Idempotency-Key': 'import'})
        assert created.status_code == 201, created.text
        cid = created.json()['id']
        assert created.json()['source']['origin'] == 'reference_project' and created.json()['brief'] is None
        assert http.post(base + '/planning', json=body, headers={'Idempotency-Key': 'import'}).json()['id'] == cid
        assert http.get(base + f'/planning/{cid}/brief').status_code == 404
        message = http.post(base + f'/planning/{cid}/messages', json={'expected_version': 0, 'text': 'Propón'},
                            headers={'Idempotency-Key': 'm1'})
        assert message.status_code == 202, message.text
        engine = make_engine(url)
        worker = LocalSupervisor(SQLiteManagedRepository(engine), ports, commit_factory=ports.writer)
        assert worker.run_once().status == 'DONE'
        detail = http.get(base + f'/planning/{cid}').json()
        assert detail['turns'][0]['status'] == 'ANSWERED'
        assert detail['actions'] == ['message', 'edit_draft', 'defer_question']
        assert http.get(f"/api/managed/runs/{detail['turns'][0]['run_id']}").json()['purpose'] == 'project_import'
        for proposal in detail['proposals']:
            version = http.get(base + f'/planning/{cid}').json()['version']
            applied = http.post(base + f"/planning/{cid}/proposals/{proposal['id']}/apply", json={
                'expected_version': version, 'proposal_sha256': proposal['proposal_sha256'], 'confirmed': True})
            assert applied.status_code == 200, applied.text
        drafts = http.get(base + f'/planning/{cid}/drafts').json()
        assert sorted(d['path'] for d in drafts['drafts']) == sorted(DRAFTS) and not drafts['import_required']
        read = http.get(base + f'/planning/{cid}/drafts/content', params={'path': 'AGENTS.md'}).json()
        assert read['content'] == AGENTS
        edit = http.put(base + f'/planning/{cid}/drafts', json={
            'expected_version': http.get(base + f'/planning/{cid}').json()['version'], 'path': 'GEMINI.md',
            'content': '# Gemini\n\n@AGENTS.md\n', 'base_sha256': None})
        assert edit.status_code == 200, edit.text
        status = http.get(base + f'/planning/{cid}/import').json()
        assert not status['ready'] and status['blockers'][0].startswith('Blocking questions remain open')
        question = http.get(base + f'/planning/{cid}').json()['questions'][0]
        deferred = http.post(base + f'/planning/{cid}/questions/defer', json={
            'expected_version': http.get(base + f'/planning/{cid}').json()['version'],
            'question_id': question['id'], 'reason': 'Se confirma en la vista previa'})
        assert deferred.status_code == 200, deferred.text
        status = http.get(base + f'/planning/{cid}/import').json()
        assert status['ready'], status['blockers']
        assert '/api/managed/projects/{project_id}/planning/{conversation_id}/import' in http.app.openapi()['paths']
        engine.dispose()
    assert tree_state(root) == before


def test_legacy_runs_keep_the_d027_guard_on_turns(migrated_database, tmp_path):
    """Límite registrado: con `.harness/runs` sin activar, la guardia de modo rechaza el turno antes de encolarlo."""
    from test_project_import import reference_project
    engine = make_engine(migrated_database[0])
    world = World(reference_project(tmp_path), engine)
    cid = world.create()
    assert world.view(cid)['source']['origin'] == 'reference_project'
    with pytest.raises(Exception, match='estado legacy'):
        world.message(cid)
    assert world.view(cid)['turns'] == []
    engine.dispose()

"""P008-T012: importación confirmada y recuperación, solo Git/SQLite y datos sintéticos."""
from dataclasses import replace
from hashlib import sha256
import json

from alembic import command
import pytest
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from harness_local.adapters.git import GitWorkspace
from harness_local.core.engine.commit import CommitIntent
from harness_local.core.engine.documents import Layout, blocks
from harness_local.core.engine.definition import required_documents
from harness_local.services.managed import LocalSupervisor
from harness_local.services.managed_runtime import ManagedConfig, ManagedProject
from harness_local.services.migration import MigrationService
from harness_local.storage.database import make_engine
from harness_local.storage.import_drafts import read_source
from harness_local.storage.managed import Conflict, SQLiteManagedRepository
from harness_local.storage.models import PhaseRow, ProjectImportRow
from harness_local.storage.project_import import ImportRepository
from harness_local.storage.phases import PhaseRepository
from test_definition import DRAFTS as DEFINITION
from test_import_conversation import World, DRAFTS, answer, tree_state, world  # noqa: F401
from test_managed_api import VERSIONS, IDENTITY, Ports, client, make_context
from test_project_import import REFERENCE_PROJECT, V1, V2, reference_project, checkout, git


def checkout_state(root):
    # Previews may materialize unreachable Git blobs/trees, as existing document previews do.
    return {path: value for path, value in tree_state(root).items() if not path.startswith('.git/objects/')}


def ready(world, phase='P002'):
    cid = world.create()
    drafts = {**DRAFTS, 'docs/ARCHITECTURE.md': '# Architecture\n\nSynthetic modules.\n', 'docs/ROADMAP.md': (
        f'# Roadmap\n\n## {phase} — Imported work\n\n**Objetivo:** Continue synthetic work.\n'
        '**Criterios de salida:**\n- Synthetic work accepted.\n'),
        'docs/STATE.md': f'# Estado\n\n## Base acumulada\n\nPrevious work.\n\n## Fase activa — {phase} Imported work\n',
        'docs/NEXT_STEPS.md': DEFINITION['docs/NEXT_STEPS.md'].replace('P001', phase)}
    world.turn(cid, answer(drafts=drafts))
    world.apply_all(cid)
    return cid


def preview(world, cid):
    return ImportRepository(world.repo).preview(world.context, cid, VERSIONS, world.writer)


def confirm(world, cid, shown=None, key=None, **kwargs):
    shown = shown or preview(world, cid)
    return ImportRepository(world.repo).submit(world.context, cid, VERSIONS, world.writer,
        key=key or world.key(), preview_sha256=shown['preview_sha256'], reason='Reviewed synthetic tree',
        confirmed=True, resume_operation_id=shown['resume_operation_id'], expected_version=shown['expected_version'],
        **kwargs)


def operation(world):
    return ImportRepository(world.repo).get(world.context.root)


def assert_adopted(world, shown, initial, phase='P002'):
    op = operation(world)
    assert op['status'] == 'COMPLETED' and op['run_status'] == 'COMMITTED'
    root = world.context.root
    assert git(root, 'rev-list', '--count', 'HEAD') == '2'
    assert git(root, 'log', '-1', '--format=%s') == 'docs: normalizar al contrato documental'
    assert all(root.joinpath(path).is_file() for path in required_documents(Layout('docs', 'docs/STATE.md', 'docs/NEXT_STEPS.md')))
    final = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*')
             if p.is_file() and '.git' not in p.relative_to(root).parts}
    # Every original byte sequence survives; code and foreign harness files keep their paths and bytes.
    assert all(data in final.values() for data in initial.values())
    for path, data in initial.items():
        if not (path.lower().endswith('.md') or path.startswith('docs/')):
            assert final[path] == data
    with Session(world.engine) as session:
        rows = session.scalars(select(PhaseRow)).all()
        assert len(rows) == 1 and rows[0].code == phase and rows[0].status == 'ACTIVE'
        assert rows[0].documents == shown['baseline']
        assert rows[0].definition['tasks'] == [phase + '-T001']
    for path in ('docs/STATE.md', 'docs/NEXT_STEPS.md'):
        assert phase in blocks(root.joinpath(path).read_text())['state']


@pytest.mark.parametrize('files,phase', [(REFERENCE_PROJECT, 'P002'), (V1, 'P001'), (V2, 'P002')])
def test_three_origins_confirm_one_commit_preserve_bytes_and_adopt_phase(migrated_database, tmp_path, files, phase):
    engine = make_engine(migrated_database[0])
    world = World(checkout(tmp_path, 'import', files), engine)
    cid = ready(world, phase)
    initial = {p: world.context.root.joinpath(p).read_bytes() for p in files}
    before = checkout_state(world.context.root)
    shown = preview(world, cid)
    assert preview(world, cid) == shown and checkout_state(world.context.root) == before
    assert shown['phase']['code'] == phase and shown['preserved']
    assert 'diff --git' not in shown['diff'] and '--- a/docs/STATE.md' in shown['diff']
    job = confirm(world, cid, shown, key='import-confirm')
    assert not world.view(cid)['actions']
    assert world.worker.run_once().status == 'DONE'
    assert_adopted(world, shown, initial, phase)
    assert confirm(world, cid, shown, key='import-confirm').id == job.id
    again = preview(world, cid)
    assert again['already_imported'] and again['documents'] == []
    assert git(world.context.root, 'status', '--porcelain') == ''
    with pytest.raises(Conflict, match='no changes'):
        confirm(world, cid, again)
    engine.dispose()


@pytest.mark.parametrize('point', ['before', 'delete', 'replace', 'commit', 'register'])
def test_crash_reconciles_exactly_the_sealed_commit(world, monkeypatch, point):
    cid = ready(world)
    shown = preview(world, cid)
    job = confirm(world, cid, shown)
    with Session(world.engine) as session:
        sealed = session.scalar(select(ProjectImportRow)).intent
    intent = CommitIntent.from_json(sealed)
    if point in ('before', 'commit'):
        original = world.writer.execute_documents
        def fail(*args):
            if point == 'commit':
                original(*args)
            raise RuntimeError('synthetic crash')
        monkeypatch.setattr(world.writer, 'execute_documents', fail)
    elif point == 'register':
        original = world.repo.finish
        def fail(*args):
            raise RuntimeError('synthetic crash')
        monkeypatch.setattr(world.repo, 'finish', fail)
    else:
        original = world.writer._write_mechanical
        def fail(context, intent):
            original(context, intent)
            if (intent.mechanical[0].content is None) == (point == 'delete'):
                raise RuntimeError('synthetic crash')
        monkeypatch.setattr(world.writer, '_write_mechanical', fail)
    with pytest.raises(RuntimeError, match='synthetic crash'):
        world.worker.run_once()
    assert world.repo.get_job(job.id).status == 'RECOVERY_REQUIRED'
    with pytest.raises(Conflict, match='already queued'):
        confirm(world, cid, shown)
    world.repo.confirm_stopped(job.id, owner_token=world.repo.get_job(job.id).owner_token,
        expected_version=world.repo.get_run(job.run_id).version, reason='Synthetic writer stopped')
    monkeypatch.undo()
    resumed = confirm(world, cid)
    assert resumed.run_id == job.run_id
    assert world.worker.run_once().status == 'DONE'
    assert operation(world)['status'] == 'COMPLETED'
    assert world.repo.get_run(job.run_id).history.stop is None
    assert git(world.context.root, 'rev-parse', 'HEAD') == intent.expected_commit
    assert git(world.context.root, 'rev-list', '--count', 'HEAD') == '2'
    with Session(world.engine) as session:
        assert session.scalar(select(ProjectImportRow)).intent == sealed
        assert session.scalar(text('SELECT count(*) FROM managed_phases')) == 1


def test_stale_preview_drafts_questions_and_checkout_refuse_before_writes(world):
    cid = ready(world)
    shown = preview(world, cid)
    before = checkout_state(world.context.root)
    world.planning.edit_draft(world.context, cid, world.view(cid)['version'], path='README.md',
                             content='# Updated\n', base_sha256=None, writer=None)
    with pytest.raises(Conflict, match='preview changed'):
        confirm(world, cid, shown)
    assert operation(world) is None and checkout_state(world.context.root) == before
    shown = preview(world, cid)
    world.context.path('docs/notes.md').write_text('# Unexpected\n')
    with pytest.raises(Conflict, match='uncommitted changes'):
        confirm(world, cid, shown)
    assert operation(world) is None


def test_checkout_change_after_confirmation_is_not_adopted(world):
    cid = ready(world)
    shown = preview(world, cid)
    confirm(world, cid, shown)
    world.context.path('docs/PROJECT.md').write_text('# External\n')
    assert world.worker.run_once().status == 'DONE'
    assert operation(world)['status'] == 'INTERRUPTED'
    assert world.context.path('docs/PROJECT.md').read_text() == '# External\n'
    assert git(world.context.root, 'rev-list', '--count', 'HEAD') == '1'
    assert PhaseRepository(world.repo).list(str(world.context.root)) == []
    with pytest.raises(Conflict):
        world.create()
    with pytest.raises(Conflict):
        world.planning.edit_draft(world.context, cid, world.view(cid)['version'], path='README.md',
                                 content='# Changed\n', base_sha256=None, writer=None)


def test_mismatched_phase_and_archive_collision_block(world):
    cid = ready(world)
    area = world.area(cid)
    area.joinpath('docs/STATE.md').write_text('# Estado\n\n## Fase activa — P099 Otra\n')
    with pytest.raises(Conflict, match='agree on one active phase'):
        preview(world, cid)
    area.joinpath('docs/STATE.md').write_text('# Estado\n\n## Fase activa — P002 Imported work\n')
    target = world.context.path('docs/archive/phase-000/import-originals/AGENTS.md')
    target.parent.mkdir(parents=True)
    target.write_text('# Existing archive\n')
    git(world.context.root, 'add', '.')
    git(world.context.root, 'commit', '-qm', 'synthetic occupied archive')
    new = world.create()
    # New conversation sees the occupied destination; do not overwrite it.
    for path in ('AGENTS.md', 'CLAUDE.md', 'docs/SPECIFICATION.md', 'docs/ROADMAP.md', 'docs/STATE.md', 'docs/NEXT_STEPS.md'):
        data = area.joinpath(path).read_text()
        world.planning.edit_draft(world.context, new, world.view(new)['version'], path=path,
                                  content=data, base_sha256=None, writer=None)
    with pytest.raises(Conflict, match='archive destination already occupied'):
        preview(world, new)
    assert target.read_text() == '# Existing archive\n'


def test_legacy_activation_precedes_import_and_only_its_marker_is_tolerated(migrated_database, tmp_path):
    engine = make_engine(migrated_database[0])
    world = World(reference_project(tmp_path), engine)
    with pytest.raises(Conflict, match='Activate D027'):
        world.create()
    migration = MigrationService(engine)
    activation = migration.activate(world.context.root,
        preview_sha256=migration.preview(world.context.root)['inventory_sha256'], legacy_stopped='Synthetic stop')
    marker = world.context.path('.harness/managed-mode.json')
    marker_before = marker.read_bytes()
    cid = ready(world)
    shown = preview(world, cid)
    assert all(doc['path'] not in ('.harness/managed-mode.json', '.gitignore', '.harness/.gitignore')
               for doc in shown['documents'])
    confirm(world, cid, shown)
    assert world.worker.run_once().status == 'DONE'
    assert marker.read_bytes() == marker_before
    assert '.harness/managed-mode.json' not in git(world.context.root, 'ls-files').splitlines()
    assert world.writer.capture(world.context).changed_paths == ()
    assert migration.status(world.context.root)['refusal'] is None
    assert operation(world)['status'] == 'COMPLETED'
    # A different marker cannot use the exclusion, even with ACTIVE in SQLite.
    marker.write_text('{}\n')
    with pytest.raises(Exception, match='uncommitted changes'):
        read_source(world.context, guard=world.repo.guard)
    assert '.harness/managed-mode.json' in world.writer.capture(world.context).changed_paths
    marker.write_bytes(marker_before)
    world.context.path('notes.txt').write_text('external\n')
    with pytest.raises(Exception, match='uncommitted changes'):
        read_source(world.context, guard=world.repo.guard)
    engine.dispose()


def test_http_preview_confirm_idempotency_and_legacy_first_step(migrated_database, tmp_path):
    root = reference_project(tmp_path)
    context = replace(make_context(root), documents='v2')
    ports = Ports()
    config = ManagedConfig((ManagedProject('gym', context, VERSIONS),), ports_factory=ports,
                           commit_factory=ports.writer, supervisor=False)
    with client(migrated_database[0], tmp_path, config) as http:
        base = '/api/managed/projects/gym'
        entry = http.get(base + '/import').json()
        assert entry['activation_required'] and entry['activation_preview']['ready']
        assert http.post(base + '/planning', json={'kind': 'project_import', 'title': 'Import'},
                         headers={'Idempotency-Key': 'not-before-activation'}).status_code == 409
        activated = http.post(base + '/migration/activations', json={
            'preview_sha256': entry['activation_preview']['inventory_sha256'], 'legacy_stopped': 'Synthetic stop'})
        assert activated.status_code == 200, activated.text
        assert not http.get(base + '/import').json()['activation_required']
        engine = make_engine(migrated_database[0])
        world = World(root, engine)
        cid = ready(world)
        shown = http.post(base + f'/planning/{cid}/import/preview', json={})
        assert shown.status_code == 200, shown.text
        shown = shown.json()
        body = {'preview_sha256': shown['preview_sha256'], 'reason': 'Synthetic review', 'confirmed': True}
        endpoint = base + f'/planning/{cid}/import/confirm'
        assert http.post(endpoint, json=body).status_code == 422  # key required
        body['preview_sha256'] = '0' * 64
        assert http.post(endpoint, json=body, headers={'Idempotency-Key': 'confirm'}).status_code == 409
        body['preview_sha256'] = shown['preview_sha256']
        job = http.post(endpoint, json=body, headers={'Idempotency-Key': 'confirm'})
        assert job.status_code == 202, job.text
        run = http.get('/api/managed/runs/' + job.json()['run_id'])
        assert run.status_code == 200 and run.json()['purpose'] == 'import_commit'
        assert world.worker.run_once().status == 'DONE'
        assert http.post(endpoint, json=body, headers={'Idempotency-Key': 'confirm'}).json()['id'] == job.json()['id']
        final = http.get(base + '/import').json()['operation']
        assert final['status'] == 'COMPLETED' and final['preview']['phase']['code'] == 'P002'
        engine.dispose()


def test_import_migration_keeps_history(migrated_database, tmp_path):
    engine = make_engine(migrated_database[0])
    world = World(checkout(tmp_path, 'import', V1), engine)
    cid = ready(world, 'P001')
    confirm(world, cid)
    with pytest.raises(RuntimeError, match='Import history'):
        command.downgrade(migrated_database[1], '0019_import_conversations')
    engine.dispose()


@pytest.mark.parametrize('case_alias', [False, True])
def test_binary_artifacts_and_case_aliases_keep_exact_originals(migrated_database, tmp_path, case_alias):
    files = dict(REFERENCE_PROJECT)
    if case_alias:
        files['docs/decisions.md'] = files.pop('docs/DECISSONS.md')
    root = checkout(tmp_path, 'import-binary', files)
    binary = root / 'docs/research/P002-probe/data.bin'
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b'\x00\xff\xfeSynthetic binary\r\n')
    git(root, 'add', '.')
    git(root, 'commit', '-qm', 'synthetic binary artifact')
    engine = make_engine(migrated_database[0])
    world = World(root, engine)
    cid = ready(world)
    shown = preview(world, cid)
    job = confirm(world, cid, shown)
    assert world.worker.run_once().status == 'DONE'
    assert operation(world)['status'] == 'COMPLETED', operation(world)['result']
    assert root.joinpath('docs/phase/P002-probe/data.bin').read_bytes() == b'\x00\xff\xfeSynthetic binary\r\n'
    assert git(root, 'status', '--porcelain') == ''
    if case_alias:
        assert 'docs/decisions.md' not in git(root, 'ls-files').splitlines()
        assert root.joinpath('docs/archive/phase-000/import-originals/docs/decisions.md').read_text() == files['docs/decisions.md']
    engine.dispose()


def test_confirmation_requires_exact_hash_reason_and_bounded_diff(world):
    cid = ready(world)
    world.writer.max_diff_bytes = 64
    with pytest.raises(Conflict, match='diff exceeds'):
        preview(world, cid)
    assert operation(world) is None
    world.writer.max_diff_bytes = 4 * 1024 * 1024
    shown = preview(world, cid)
    for field, value in [('confirmed', False), ('reason', ' ')]:
        args = dict(key=world.key(), preview_sha256=shown['preview_sha256'], reason='Reviewed', confirmed=True)
        args[field] = value
        with pytest.raises(ValueError, match='Explicit confirmation'):
            ImportRepository(world.repo).submit(world.context, cid, VERSIONS, world.writer, **args)
    assert operation(world) is None


def test_open_blocking_question_prevents_commit_preview(world):
    cid = ready(world)
    world.turn(cid, answer(drafts={}, questions=[{'text': 'Confirm phase?', 'blocking': True}]))
    with pytest.raises(Conflict, match='Blocking questions remain open'):
        preview(world, cid)
    question = world.view(cid)['questions'][0]
    world.planning.defer(cid, world.view(cid)['version'], question_id=question['id'], reason='Synthetic review')
    assert preview(world, cid)['phase']['code'] == 'P002'


def test_first_task_continues_with_legacy_marker_outside_evidence(migrated_database, tmp_path):
    engine = make_engine(migrated_database[0])
    world = World(reference_project(tmp_path), engine)
    migration = MigrationService(engine)
    migration.activate(world.context.root, preview_sha256=migration.preview(world.context.root)['inventory_sha256'],
                       legacy_stopped='Synthetic stop')
    cid = ready(world)
    confirm(world, cid)
    assert world.worker.run_once().status == 'DONE'
    plan = world.context.path('docs/NEXT_STEPS.md').read_text()
    task = world.repo.submit(world.context, 'P002-T001', 'P002', plan, VERSIONS, key='first-imported-task')
    def implement(context, request):
        context.path('app').mkdir()
        context.path('app/main.txt').write_text('implemented\n')
        return {'result': 'synthetic'}
    world.ports.agents.responses.extend([implement, {'task_id': 'P002-T001', 'verdict': 'ACCEPT', 'findings': [],
        'blocking_questions': [], 'scope_grants': []}])
    assert world.worker.run_once().status == 'DONE'
    run = world.repo.get_run(task.run_id)
    assert run.status == 'ACCEPTANCE_READY', run.history.stop
    assert run.history.cycles[-1].evidence.changed_paths == ('app/main.txt',)
    world.repo.submit_commit(task.run_id, key='first-imported-commit', expected_version=run.version)
    assert world.worker.run_once().status == 'DONE'
    assert world.repo.get_run(task.run_id).status == 'COMMITTED'
    assert world.writer.capture(world.context).changed_paths == ()
    assert '.harness/managed-mode.json' not in git(world.context.root, 'ls-files').splitlines()
    engine.dispose()

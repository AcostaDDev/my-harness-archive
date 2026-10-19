"""P008-T019: gitlinks y filtros hijos, sin ejecutar submódulos; solo Git/SQLite sintéticos."""
import os
import shlex
import shutil
import sys

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from harness_local.adapters.git import Git
from harness_local.adapters.local_git import LocalGit
from harness_local.adapters.project_import import read_checkout
from harness_local.adapters.project_onboarding import read_inventory as onboarding_inventory
from harness_local.core.engine.commit import CommitIntent
from harness_local.core.project_import import ImportInventoryError
from harness_local.storage.managed import Conflict
from harness_local.storage.models import PlanningConversationRow, ProjectImportRow
from harness_local.storage.phases import PhaseRepository
from test_import_commit import confirm, operation, preview, ready
from test_import_conversation import answer, tree_state, world  # noqa: F401
from test_import_git_boundary import job_count
from test_onboarding_conversation import world as onboarding_world  # noqa: F401
from test_onboarding_commit import confirm as onboarding_confirm, preview as onboarding_preview, ready as onboarding_ready
from test_project_import import V1, checkout


def submodule(root, location='synthetic-module', kind='clean', included=False, *, committed=True):
    """Un hijo local inicializado con filtro marcador; nunca se ejecuta submodule add ni transporte."""
    child = root / location
    child.parent.mkdir(parents=True, exist_ok=True)
    checkout(child.parent, child.name, {'README.md': '# Synthetic child\n'})
    git = Git(root)
    (root / '.gitmodules').write_text(
        '[submodule "synthetic-module"]\n\tpath = ' + location + '\n\turl = ./synthetic-module\n')
    git.run('add', '.gitmodules')
    git.run('update-index', '--add', '--cacheinfo', '160000,' + Git(child).text('rev-parse', 'HEAD') + ',' + location)
    if committed:
        git.run('-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
                'commit', '-qm', 'Synthetic gitlink')
    marker, script = root.parent / 'child-filter-invoked', root.parent / 'child filter probe.py'
    script.write_text('import pathlib, sys\npathlib.Path(' + repr(str(marker))
                      + ').write_text("invoked")\nsys.stdout.buffer.write(sys.stdin.buffer.read())\n')
    command = shlex.join([sys.executable, str(script)])
    port = Git(child)
    if included:
        config = root.parent / 'child-included.config'
        port.run('config', '--file', str(config), f'filter.synthetic.{kind}', command)
        port.run('config', 'include.path', str(config))
    else:
        port.run('config', f'filter.synthetic.{kind}', command)
    (child / '.git/info/attributes').write_text('*.md filter=synthetic\n')
    stamp = (child / 'README.md').stat().st_mtime_ns - 3_000_000_000
    os.utime(child / 'README.md', ns=(stamp, stamp))
    return child, marker


@pytest.mark.parametrize('location', ['synthetic-module', 'docs/synthetic-module'])
@pytest.mark.parametrize('kind,included', [('clean', False), ('clean', True), ('process', False), ('process', True)])
def test_inventory_rejects_gitlinks_before_status_without_reading_child(tmp_path, monkeypatch, location, kind, included):
    root = checkout(tmp_path, 'parent', V1)
    child, marker = submodule(root, location, kind, included)
    assert LocalGit(root).run('status', '--porcelain=v1', '--ignore-submodules=all') == b''
    assert LocalGit(root).run('config', '--includes', '--get-regexp',
                              r'^filter\..*\.(clean|process)$', ok=(0, 1)) == b''
    before, calls = tree_state(root), []
    original = Git.run

    def recording(self, *args, **kwargs):
        assert self.cwd == root and args[0] == '--no-lazy-fetch'
        calls.append(args[1])
        return original(self, *args, **kwargs)

    with monkeypatch.context() as local:
        local.setattr(Git, 'run', recording)
        with pytest.raises(ImportInventoryError, match='submodule/gitlink.*' + location):
            read_checkout(root)
    assert 'ls-tree' in calls and not {'status', 'add', 'hash-object'} & set(calls)
    assert not marker.exists() and tree_state(root) == before
    # B's static inventory still reads only HEAD; it does not approve its later writer boundary.
    onboarding_inventory(root)
    assert not marker.exists() and tree_state(root) == before and child.is_dir()


@pytest.mark.parametrize('variant', ['staged', 'removed', 'uninitialized', 'gitfile'])
def test_head_and_index_guard_does_not_depend_on_child_config_or_initialization(tmp_path, monkeypatch, variant):
    root = checkout(tmp_path, 'parent', V1)
    child, marker = submodule(root, committed=variant != 'staged')
    git = Git(root)
    if variant == 'removed':
        git.run('update-index', '--force-remove', '--', child.name)
    elif variant == 'uninitialized':
        shutil.rmtree(child)
    elif variant == 'gitfile':
        git.run('submodule', 'absorbgitdirs', '--', child.name)
    before = tree_state(root)
    original = Git.run

    def recording(self, *args, **kwargs):
        assert 'status' not in args and self.cwd == root
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Git, 'run', recording)
    with pytest.raises(ImportInventoryError, match='submodule/gitlink.*in ' + ('index' if variant == 'staged' else 'HEAD')):
        read_checkout(root)
    assert not marker.exists() and tree_state(root) == before


@pytest.mark.parametrize('stage', ['create', 'message', 'status', 'preview', 'confirm'])
@pytest.mark.parametrize('location', ['synthetic-module', 'docs/synthetic-module'])
def test_consumers_block_before_conversation_turn_or_writer(world, monkeypatch, stage, location):
    cid = None if stage == 'create' else ready(world)
    shown = preview(world, cid) if stage == 'confirm' else None
    _, marker = submodule(world.context.root, location, included=True)
    before, jobs = tree_state(world.context.root), job_count(world)
    requests = list(world.ports.agents.requests)
    with Session(world.engine) as session:
        conversations = session.scalar(select(func.count()).select_from(PlanningConversationRow))

    def forbidden(*args, **kwargs):
        pytest.fail('Submodule guard must precede agent/capture/seal/writer')

    for name in ('capture', 'seal', 'execute_documents'):
        monkeypatch.setattr(world.writer, name, forbidden)
    monkeypatch.setattr(world.ports.agents, 'invoke', forbidden)
    if stage == 'status':
        status = world.status(cid)
        assert not status['ready'] and any('submodule/gitlink' in blocker for blocker in status['blockers'])
    else:
        with pytest.raises(Conflict, match='submodule/gitlink'):
            if stage == 'create':
                world.create()
            elif stage == 'message':
                world.message(cid)
            elif stage == 'preview':
                preview(world, cid)
            else:
                confirm(world, cid, shown)
    assert tree_state(world.context.root) == before and not marker.exists()
    assert job_count(world) == jobs and world.ports.agents.requests == requests
    assert operation(world) is None and PhaseRepository(world.repo).list(str(world.context.root)) == []
    with Session(world.engine) as session:
        assert session.scalar(select(func.count()).select_from(PlanningConversationRow)) == conversations


@pytest.mark.parametrize('point', ['before', 'after'])
def test_queued_turn_observations_refuse_gitlinks_without_accepting_proposals(world, monkeypatch, point):
    cid = world.create()
    world.message(cid)
    before = None
    marker = None
    original = world.ports.agents.invoke

    def install():
        nonlocal before, marker
        _, marker = submodule(world.context.root, included=True)
        before = tree_state(world.context.root)

    if point == 'before':
        install()

        def invoke(*args, **kwargs):
            pytest.fail('No agent invocation allowed after the source acquired a gitlink')
    else:
        world.ports.agents.responses.append(answer())

        def invoke(*args, **kwargs):
            response = original(*args, **kwargs)
            install()  # Synthetic concurrent change after the read-only response.
            return response

    monkeypatch.setattr(world.ports.agents, 'invoke', invoke)
    assert world.worker.run_once().status == 'DONE'
    view = world.view(cid)
    assert view['turns'][-1]['status'] == 'FAILED' and view['proposals'] == []
    assert 'submodule/gitlink' in str(view['turns'][-1])
    assert tree_state(world.context.root) == before and not marker.exists()
    assert operation(world) is None and PhaseRepository(world.repo).list(str(world.context.root)) == []


@pytest.mark.parametrize('flow', ['A', 'B'])
def test_job_and_resume_reject_new_index_gitlink_then_recover_same_commit(world, onboarding_world, monkeypatch, flow):
    if flow == 'B':
        world, prepare, show, submit = onboarding_world, onboarding_ready, onboarding_preview, onboarding_confirm
    else:
        prepare, show, submit = ready, preview, confirm
    cid = prepare(world)
    job = submit(world, cid, show(world, cid))
    with Session(world.engine) as session:
        sealed = session.scalar(select(ProjectImportRow)).intent
    child, marker = submodule(world.context.root, kind='process', included=True, committed=False)
    before = tree_state(world.context.root)

    def forbidden(*args, **kwargs):
        pytest.fail('Submodule guard must precede capture/seal/writing, including recovery')

    with monkeypatch.context() as blocked:
        for name in ('capture', 'seal', 'execute_documents'):
            blocked.setattr(world.writer, name, forbidden)
        with pytest.raises(ImportInventoryError, match='submodule/gitlink.*in index'):
            world.worker.run_once()
        assert tree_state(world.context.root) == before and not marker.exists()
        assert world.repo.get_job(job.id).status == 'RECOVERY_REQUIRED'
        world.repo.confirm_stopped(job.id, owner_token=world.repo.get_job(job.id).owner_token,
            expected_version=world.repo.get_run(job.run_id).version, reason='Synthetic writer stopped')
        jobs = job_count(world)
        with pytest.raises(Conflict, match='submodule/gitlink.*in index'):
            submit(world, cid)
        assert job_count(world) == jobs and tree_state(world.context.root) == before and not marker.exists()
    assert PhaseRepository(world.repo).list(str(world.context.root)) == []
    port = Git(world.context.root)
    port.run('update-index', '--force-remove', '--', child.name, '.gitmodules')
    shutil.rmtree(child)
    (world.context.root / '.gitmodules').unlink()
    resumed = submit(world, cid)
    assert resumed.run_id == job.run_id
    assert world.worker.run_once().status == 'DONE'
    assert operation(world)['status'] == 'COMPLETED'
    assert port.text('rev-parse', 'HEAD') == CommitIntent.from_json(sealed).expected_commit
    with Session(world.engine) as session:
        assert session.scalar(select(ProjectImportRow)).intent == sealed


def test_onboarding_preview_rejects_gitlink_before_shared_capture(onboarding_world, monkeypatch):
    world = onboarding_world
    cid = onboarding_ready(world)
    _, marker = submodule(world.context.root, committed=False)
    before, jobs = tree_state(world.context.root), job_count(world)

    def forbidden(*args, **kwargs):
        pytest.fail('Shared A/B guard must precede capture/seal')

    monkeypatch.setattr(world.writer, 'capture', forbidden)
    monkeypatch.setattr(world.writer, 'seal', forbidden)
    with pytest.raises(Conflict, match='submodule/gitlink'):
        onboarding_preview(world, cid)
    assert tree_state(world.context.root) == before and not marker.exists()
    assert job_count(world) == jobs and operation(world) is None

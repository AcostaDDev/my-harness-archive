"""Quinta revisión P008: exigir H1–H3/H5–H7 corregidos, sin reescribir evidencia previa.

Solo Git/SQLite temporales, datos sintéticos, revisores y transportes falsos. No ejecuta
el harness sobre este repositorio. Exit 0 exige ausencia de filtros/transportes y recuperación exacta.
"""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

from alembic import command
from alembic.config import Config

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/product'))
sys.path.insert(0, str(Path(__file__).parent))

from P008_REVISION_SALIDA_2_REPRO import filter_probe, import_probe
from P008_REVISION_SALIDA_3_REPRO import partial_clone_probe
from P008_REVISION_SALIDA_4_REPRO import op_intent, submodule_probe
from harness_local.adapters.git import Git, GitError, GitWorkspace
from harness_local.adapters.local_git import LocalGit
from harness_local.core.engine.commit import CommitIntent
from harness_local.storage.database import make_engine
from harness_local.storage.managed import Conflict
from harness_local.storage.phases import PhaseRepository
from harness_local.storage.project_import import ImportRepository
from test_import_commit import confirm, ready
from test_import_conversation import World, tree_state
from test_import_local_objects import promisor
from test_import_writer_local_objects import unsupported_git
from test_managed_api import IDENTITY
from test_onboarding_commit import confirm as onboarding_confirm, ready as onboarding_ready
from test_onboarding_conversation import World as OnboardingWorld
from test_project_import import REFERENCE_PROJECT, checkout
from test_project_onboarding import DJANGO


def writer_probe(flow, *, resume=False, missing=None):
    """Reconstruir H7 con puerto nuevo y trazar ambas APIs durante sellado/escritura/conciliación."""
    with TemporaryDirectory(prefix='p008-review5-writer-') as scratch:
        base = Path(scratch)
        cfg = Config(str(ROOT / 'alembic.ini'))
        cfg.attributes['database_url'] = 'sqlite:///' + str(base / 'synthetic.sqlite3')
        command.upgrade(cfg, 'head')
        engine = make_engine(cfg.attributes['database_url'])
        try:
            files = {**(REFERENCE_PROJECT if flow == 'A' else DJANGO),
                     'synthetic-payload.bin': '\0Synthetic code payload\u00ff'}
            root = checkout(base, 'repo', files).resolve()
            world = (World if flow == 'A' else OnboardingWorld)(root, engine)
            prepare, submit = (ready, confirm) if flow == 'A' else (onboarding_ready, onboarding_confirm)
            cid = prepare(world)
            _, _, marker = promisor(root)
            local = LocalGit(root)
            objects = local.run('rev-list', '--objects', '--no-object-names', 'HEAD')
            assert b' missing' not in local.run('cat-file', '--batch-check', input=objects)
            config = (root / '.git/config').read_bytes()
            requests = list(world.ports.agents.requests)
            calls, original_run, original_code = [], Git.run, Git.code

            def recording(api, original):
                def invoke(self, *args, **kwargs):
                    assert self.cwd.resolve() == root and args[0] == '--no-lazy-fetch'
                    calls.append((api, args))
                    result = original(self, *args, **kwargs)
                    assert not marker.exists()
                    return result
                return invoke

            with patch.object(Git, 'run', recording('run', original_run)), \
                    patch.object(Git, 'code', recording('code', original_code)):
                job = submit(world, cid)
                frozen = op_intent(engine)
                intent = CommitIntent.from_json(frozen)
                absent = ('cat-file', '-e', intent.expected_commit + '^{commit}')
                assert local.code(*absent) != 0 and not marker.exists()
                world.writer = GitWorkspace(IDENTITY)
                if resume:
                    with patch.object(world.writer, 'execute_documents', side_effect=RuntimeError('Synthetic crash')):
                        try:
                            world.worker.run_once()
                        except RuntimeError as exc:
                            assert str(exc) == 'Synthetic crash'
                        else:
                            raise AssertionError('Expected a synthetic crash before the writer')
                    world.repo.confirm_stopped(job.id, owner_token=world.repo.get_job(job.id).owner_token,
                        expected_version=world.repo.get_run(job.run_id).version, reason='Synthetic writer stopped')
                    assert submit(world, cid).run_id == job.run_id
                    world.writer = GitWorkspace(IDENTITY)
                diagnostic = None
                if missing:
                    revision = {'source-blob': 'HEAD:synthetic-payload.bin', 'source-tree': 'HEAD^{tree}',
                        'sealed-blob': intent.expected_tree + ':GEMINI.md', 'sealed-tree': intent.expected_tree}[missing]
                    obj = local.text('rev-parse', revision)
                    path = root / '.git/objects' / obj[:2] / obj[2:]
                    data = path.read_bytes()
                    path.unlink()
                    before = tree_state(root)
                    try:
                        world.worker.run_once()
                    except GitError as exc:
                        diagnostic = str(exc)
                    else:
                        raise AssertionError('Required missing object must block before writing')
                    assert any(word in diagnostic for word in ('missing', 'local', 'tree')), diagnostic
                    assert tree_state(root) == before and not marker.exists() and not path.exists()
                    assert PhaseRepository(world.repo).list(str(root)) == [] and op_intent(engine) == frozen
                    world.repo.confirm_stopped(job.id, owner_token=world.repo.get_job(job.id).owner_token,
                        expected_version=world.repo.get_run(job.run_id).version, reason='Synthetic writer stopped')
                    try:
                        submit(world, cid)
                    except Conflict:
                        pass
                    else:
                        raise AssertionError('Missing object must also block reconfirmation')
                    assert tree_state(root) == before and not marker.exists() and not path.exists()
                    path.write_bytes(data)  # Solo restituye los bytes sintéticos retirados por el fixture.
                    assert submit(world, cid).run_id == job.run_id
                    world.writer = GitWorkspace(IDENTITY)
                outcome = world.worker.run_once()
                op = ImportRepository(world.repo).get(root)
                assert outcome.status == 'DONE' and op['status'] == 'COMPLETED'
                assert local.text('rev-parse', 'HEAD') == intent.expected_commit
                assert local.text('write-tree') == intent.expected_tree and local.run('status', '--porcelain') == b''
                assert op_intent(engine) == frozen and world.ports.agents.requests == requests
                assert len(PhaseRepository(world.repo).list(str(root))) == 1
                assert ('code', ('--no-lazy-fetch', *absent)) in calls
                assert (root / '.git/config').read_bytes() == config and not marker.exists()
            return {'flow': flow, 'resume_before_writer': resume, 'missing_object': missing,
                'all_source_objects_initially_local': True, 'source_object_count': len(objects.splitlines()),
                'required_object_diagnostic': diagnostic,
                'missing_object_rejected_without_byte_changes': bool(missing),
                'api_command_counts': dict(sorted(Counter(api + ':' + argv[1] for api, argv in calls).items())),
                'all_commands_no_lazy_fetch': all(argv[0] == '--no-lazy-fetch' for _, argv in calls),
                'future_commit_absence_allowed': True, 'upload_pack_invoked': marker.exists(),
                'job_status': outcome.status, 'operation_status': op['status'], 'same_sealed_intent': True,
                'run_id': job.run_id, 'expected_commit': intent.expected_commit,
                'single_phase_adopted': True, 'new_agent_invocations': 0, 'configuration_unchanged': True,
                'final_checkout_clean': True, 'final_index_equals_sealed_tree': True}
        finally:
            engine.dispose()


def unsupported_probe(api):
    with TemporaryDirectory(prefix='p008-review5-oldgit-') as scratch:
        base = Path(scratch)
        executable, calls, fallback = unsupported_git(base / 'repo')
        before = tree_state(base)
        try:
            getattr(LocalGit(base, executable=executable), api)('cat-file', '-e', 'a' * 40 + '^{commit}')
        except GitError as exc:
            diagnostic = str(exc)
        else:
            raise AssertionError('Unsupported Git cannot be interpreted as future commit absence')
        assert 'unknown option: --no-lazy-fetch' in diagnostic and not fallback.exists()
        assert len(calls.read_text().splitlines()) == 1
        after = tree_state(base)
        after.pop(calls.relative_to(base).as_posix())
        assert after == before
        return {'api': api, 'diagnostic': diagnostic, 'invocations': 1,
                'fallback_invoked': False, 'fixture_bytes_unchanged_except_trace': True}


if __name__ == '__main__':
    historical = tuple('P008_REVISION_SALIDA' + suffix + ending
                       for suffix in ('', '_2', '_3', '_4') for ending in ('_REPRO.py', '_EVIDENCE.json'))
    print(json.dumps({
        'reviewed_commit': Git(ROOT).text('rev-parse', 'HEAD'),
        'git_version': Git(ROOT).text('--version'),
        'reproduction_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'historical_files_sha256': {name: sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                                   for name in historical},
        'H1_filter': filter_probe(),
        **{name: import_probe(case) for name, case in (('H2_conversion', 'conversion'), ('H3_ignored', 'ignored'))},
        'H5_partial_clone': partial_clone_probe(),
        'H6_submodule': [submodule_probe(location, kind, included, stage)
                        for location in ('', 'docs') for kind in ('clean', 'process')
                        for included in (False, True) for stage in ('inventory', 'conversation')]
            + [submodule_probe('', 'clean', True, 'inventory', index_only=True),
               submodule_probe('docs', 'process', True, 'conversation', index_only=True)],
        'H7_writer': [writer_probe(flow, resume=resume) for flow in ('A', 'B') for resume in (False, True)],
        'H7_required_objects': [writer_probe(flow, missing=missing) for flow in ('A', 'B')
                                for missing in ('source-blob', 'source-tree', 'sealed-blob', 'sealed-tree')],
        'H7_unsupported_git': [unsupported_probe(api) for api in ('run', 'code')],
    }, ensure_ascii=False, indent=2))

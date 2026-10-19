"""Cuarta revisión P008: guardias H1–H3/H5/H6 y hallazgo H7; fixtures temporales sintéticos.

Exit 0 exige esas guardias y reproduce H7, no acredita su corrección. No ejecuta el harness sobre este repositorio,
ni modifica las reproducciones o evidencias históricas. Sin proveedores ni transportes reales.
"""
from hashlib import sha256
import json
import os
from pathlib import Path
import shlex
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

from alembic import command
from alembic.config import Config
from sqlalchemy import func, select
from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/product'))
sys.path.insert(0, str(Path(__file__).parent))

from P008_REVISION_SALIDA_2_REPRO import filter_probe, import_probe
from P008_REVISION_SALIDA_3_REPRO import partial_clone_probe
from harness_local.adapters.git import Git
from harness_local.adapters.local_git import LocalGit
from harness_local.adapters.project_import import read_checkout
from harness_local.adapters.project_onboarding import read_inventory as onboarding_inventory
from harness_local.core.project_import import ImportInventoryError
from harness_local.storage.database import make_engine
from harness_local.storage.managed import Conflict
from harness_local.storage.models import PlanningConversationRow, ProjectImportRow
from harness_local.storage.phases import PhaseRepository
from harness_local.storage.project_import import ImportRepository
from test_import_conversation import World, tree_state
from test_import_commit import ready, confirm
from test_import_git_boundary import job_count
from test_onboarding_conversation import World as OnboardingWorld
from test_onboarding_commit import ready as onboarding_ready, confirm as onboarding_confirm
from test_project_import import V1, REFERENCE_PROJECT, checkout
from test_project_onboarding import DJANGO


def submodule_probe(location, kind, included, stage, *, index_only=False):
    """Reconstruye H6 sin usar su función histórica, que exige acreditar el fallo antiguo."""
    with TemporaryDirectory(prefix='p008-review4-submodule-') as scratch:
        base = Path(scratch)
        root = checkout(base, 'parent', V1)
        relative = location + '/synthetic-module' if location else 'synthetic-module'
        child = root / relative
        child.parent.mkdir(parents=True, exist_ok=True)
        checkout(child.parent, child.name, {'README.md': '# Synthetic submodule\n'})
        git = Git(root)
        (root / '.gitmodules').write_text(
            '[submodule "synthetic-module"]\n\tpath = ' + relative + '\n\turl = ./synthetic-module\n')
        git.run('add', '.gitmodules')
        git.run('update-index', '--add', '--cacheinfo',
                '160000,' + Git(child).text('rev-parse', 'HEAD') + ',' + relative)
        if not index_only:
            git.run('commit', '-m', 'Synthetic gitlink', env={
                'GIT_AUTHOR_NAME': 'Fixture Author', 'GIT_AUTHOR_EMAIL': 'author@example.invalid',
                'GIT_COMMITTER_NAME': 'Fixture Author', 'GIT_COMMITTER_EMAIL': 'author@example.invalid'})
        marker, script = base / 'filter-invoked', base / 'fake-filter.py'
        script.write_text('import pathlib, sys\npathlib.Path(' + repr(str(marker))
            + ').write_text("invoked")\n'
            + ('raise SystemExit(1)\n' if kind == 'process' else
               'sys.stdout.buffer.write(sys.stdin.buffer.read())\n'))
        argv = shlex.join([sys.executable, str(script)])
        if included:
            config = base / 'child-included.config'
            Git(child).run('config', '--file', str(config), f'filter.synthetic.{kind}', argv)
            Git(child).run('config', 'include.path', str(config))
        else:
            Git(child).run('config', f'filter.synthetic.{kind}', argv)
        (child / '.git/info/attributes').write_text('*.md filter=synthetic\n')
        doc = child / 'README.md'
        stamp = doc.stat().st_mtime_ns - 3_000_000_000
        os.utime(doc, ns=(stamp, stamp))
        assert LocalGit(root).run('config', '--includes', '--get-regexp',
                                  r'^filter\..*\.(clean|process)$', ok=(0, 1)) == b''
        if not index_only:
            assert LocalGit(root).run('status', '--porcelain=v1', '--ignore-submodules=all') == b''
        before, calls, original = tree_state(root), [], Git.run
        engine = None
        if stage == 'conversation':
            cfg = Config(str(ROOT / 'alembic.ini'))
            url = 'sqlite:///' + str(base / 'synthetic.sqlite3')
            cfg.attributes['database_url'] = url
            command.upgrade(cfg, 'head')
            engine = make_engine(url)
            world = World(root, engine)

        def recording(self, *args, **kwargs):
            assert self.cwd.resolve() == root.resolve() and args[0] == '--no-lazy-fetch'
            try:
                return original(self, *args, **kwargs)
            finally:
                calls.append({'argv': list(args), 'filter_invoked': marker.exists()})

        try:
            with patch.object(Git, 'run', recording):
                try:
                    world.create() if stage == 'conversation' else read_checkout(root)
                except (Conflict, ImportInventoryError) as exc:
                    diagnostic = str(exc)
                else:
                    raise AssertionError('H6: gitlink must be rejected before status or conversation creation')
            result = {'path': relative, 'filter': kind, 'filter_via_include': included, 'stage': stage,
                'gitlink_source': 'index' if index_only else 'HEAD', 'diagnostic': diagnostic,
                'rejected': True, 'filter_invoked': marker.exists(), 'calls': calls,
                'all_checkout_and_git_bytes_unchanged': tree_state(root) == before}
            assert relative in diagnostic and 'submodule/gitlink' in diagnostic
            assert ('in index' if index_only else 'in HEAD') in diagnostic
            assert not any(call['argv'][1] in ('status', 'add', 'hash-object') for call in calls)
            assert not marker.exists() and tree_state(root) == before
            if stage == 'conversation':
                with Session(engine) as session:
                    conversations = session.scalar(select(func.count()).select_from(PlanningConversationRow))
                result.update(conversations=conversations, agent_calls=len(world.ports.agents.requests),
                    jobs=job_count(world), import_operation=ImportRepository(world.repo).get(root),
                    phases=len(PhaseRepository(world.repo).list(str(root))))
                assert result['conversations'] == result['agent_calls'] == result['jobs'] == result['phases'] == 0
                assert result['import_operation'] is None
            onboarding_inventory(root)
            result['flow_b_inventory_filter_invoked'] = marker.exists()
            assert not marker.exists() and tree_state(root) == before
            return result
        finally:
            if engine is not None:
                engine.dispose()


def writer_lazy_fetch_probe(flow, resume):
    """H7: el commit esperado aún no existe por diseño; comprobarlo no autoriza un transporte."""
    with TemporaryDirectory(prefix='p008-review4-writer-') as scratch:
        base = Path(scratch)
        cfg = Config(str(ROOT / 'alembic.ini'))
        url = 'sqlite:///' + str(base / 'synthetic.sqlite3')
        cfg.attributes['database_url'] = url
        command.upgrade(cfg, 'head')
        engine = make_engine(url)
        try:
            root = checkout(base, 'repo', REFERENCE_PROJECT if flow == 'A' else DJANGO)
            world = (World if flow == 'A' else OnboardingWorld)(root, engine)
            prepare, submit = (ready, confirm) if flow == 'A' else (onboarding_ready, onboarding_confirm)
            cid = prepare(world)
            marker, script = base / 'upload-pack-invoked', base / 'fake upload-pack.py'
            script.write_text('from pathlib import Path\nwith Path(' + repr(str(marker))
                              + ').open("a") as log:\n    log.write("invoked\\n")\nraise SystemExit(1)\n')
            git = Git(root)
            for key, value in {
                'remote.origin.url': str(root), 'remote.origin.promisor': 'true',
                'remote.origin.partialclonefilter': 'blob:none',
                'remote.origin.uploadpack': shlex.join([sys.executable, str(script)]),
            }.items():
                git.run('config', key, value)
            # No se elimina ningún objeto: incluso todos los objetos alcanzables de HEAD están disponibles.
            local = LocalGit(root)
            objects = local.run('rev-list', '--objects', '--no-object-names', 'HEAD')
            check = local.run('cat-file', '--batch-check', input=objects)
            assert b' missing' not in check
            job = submit(world, cid)
            with Session(engine) as session:
                sealed = session.scalar(select(ProjectImportRow)).intent
            from harness_local.core.engine.commit import CommitIntent
            intent = CommitIntent.from_json(sealed)
            absent_spec = intent.expected_commit + '^{commit}'
            assert local.code('cat-file', '-e', absent_spec) != 0 and not marker.exists()
            if resume:
                with patch.object(world.writer, 'execute_documents', side_effect=RuntimeError('Synthetic crash')):
                    try:
                        world.worker.run_once()
                    except RuntimeError as exc:
                        assert str(exc) == 'Synthetic crash'
                    else:
                        raise AssertionError('Synthetic crash must interrupt the first job')
                world.repo.confirm_stopped(job.id, owner_token=world.repo.get_job(job.id).owner_token,
                    expected_version=world.repo.get_run(job.run_id).version, reason='Synthetic writer stopped')
                resumed = submit(world, cid)
                assert resumed.run_id == job.run_id
            assert not marker.exists()
            before_agents = len(world.ports.agents.requests)
            calls, original = [], Git.code

            def recording(self, *args, **kwargs):
                result = original(self, *args, **kwargs)
                calls.append({'argv': list(args), 'returncode': result, 'upload_pack_invoked': marker.exists()})
                return result

            with patch.object(Git, 'code', recording):
                outcome = world.worker.run_once()
            op = ImportRepository(world.repo).get(world.context.root)
            head = local.text('rev-parse', 'HEAD')
            result = {'flow': flow, 'resume': resume, 'all_source_objects_local': True,
                'source_object_count': len(objects.splitlines()), 'upload_pack_before_writer': False,
                'no_lazy_fetch_control_invoked_transport': False, 'calls': calls,
                'upload_pack_invoked': marker.exists(), 'upload_pack_invocations': len(marker.read_text().splitlines()),
                'job_status': outcome.status, 'operation_status': op['status'],
                'expected_commit': intent.expected_commit, 'head': head,
                'same_sealed_intent': op is not None and sealed == op_intent(engine),
                'new_agent_invocations': len(world.ports.agents.requests) - before_agents,
                'phases': len(PhaseRepository(world.repo).list(str(world.context.root)))}
            assert marker.exists() and calls[0]['argv'] == ['cat-file', '-e', absent_spec]
            assert calls[0]['upload_pack_invoked'] and '--no-lazy-fetch' not in calls[0]['argv']
            assert outcome.status == 'DONE' and op['status'] == 'COMPLETED' and head == intent.expected_commit
            assert result['same_sealed_intent'] and result['new_agent_invocations'] == 0 and result['phases'] == 1
            return result
        finally:
            engine.dispose()


def op_intent(engine):
    with Session(engine) as session:
        return session.scalar(select(ProjectImportRow)).intent


if __name__ == '__main__':
    historical = ('P008_REVISION_SALIDA_REPRO.py', 'P008_REVISION_SALIDA_2_REPRO.py',
                  'P008_REVISION_SALIDA_3_REPRO.py', 'P008_REVISION_SALIDA_EVIDENCE.json',
                  'P008_REVISION_SALIDA_2_EVIDENCE.json', 'P008_REVISION_SALIDA_3_EVIDENCE.json')
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
        'H7_writer_lazy_fetch': [writer_lazy_fetch_probe(flow, resume)
                                for flow in ('A', 'B') for resume in (False, True)],
    }, ensure_ascii=False, indent=2))

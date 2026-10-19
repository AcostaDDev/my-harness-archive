"""Tercera revisión P008: H1–H5 revisados; H6 reproduce filtros en submódulos.

Solo Git/SQLite temporales, datos sintéticos y herramientas falsas. Exit 0 acredita
la reproducción de H6, no su corrección. No modifica las evidencias anteriores.
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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/product'))
sys.path.insert(0, str(Path(__file__).parent))

from P008_REVISION_SALIDA_2_REPRO import filter_probe, import_probe
from harness_local.adapters.git import Git
from harness_local.adapters.local_git import LocalGit
from harness_local.adapters.project_import import read_checkout
from harness_local.adapters.project_onboarding import read_inventory as onboarding_inventory
from harness_local.core.project_import import ImportInventoryError, build_inventory
from harness_local.core.project_onboarding import OnboardingInventoryError
from harness_local.storage.database import make_engine
from harness_local.storage.project_import import ImportRepository
from test_import_conversation import World, tree_state
from test_import_git_boundary import job_count
from test_import_local_objects import promisor
from test_project_import import V1, checkout


def partial_clone_probe():
    with TemporaryDirectory(prefix='p008-review3-promisor-') as scratch:
        root = checkout(Path(scratch), 'repo', {'README.md': '# Synthetic promisor fixture\n'})
        obj, path, marker = promisor(root)
        path.unlink()
        before = tree_state(root)
        results = {}
        original = Git.run
        for flow, reader, error in (('A', read_checkout, ImportInventoryError),
                                    ('B', onboarding_inventory, OnboardingInventoryError)):
            calls = []

            def recording(self, *args, **kwargs):
                assert args[0] == '--no-lazy-fetch'
                try:
                    return original(self, *args, **kwargs)
                finally:
                    calls.append({'argv': list(args), 'upload_pack_invoked': marker.exists()})

            with patch.object(Git, 'run', recording):
                try:
                    reader(root)
                except error as exc:
                    diagnostic = str(exc)
                else:
                    raise AssertionError(flow + ': missing promised blob must be rejected')
            results[flow] = {'diagnostic': diagnostic, 'calls': calls,
                             'upload_pack_invoked': marker.exists(),
                             'object_still_missing': not path.exists(),
                             'all_checkout_and_git_bytes_unchanged': tree_state(root) == before}
            assert obj in diagnostic and 'missing' in diagnostic
            assert not marker.exists() and not path.exists() and tree_state(root) == before
        return results


def submodule_probe(location, included, stage):
    with TemporaryDirectory(prefix='p008-review3-submodule-') as scratch:
        base = Path(scratch)
        root = checkout(base, 'parent', V1)
        relative = location + '/synthetic-module' if location else 'synthetic-module'
        (root / relative).parent.mkdir(parents=True, exist_ok=True)
        child = checkout((root / relative).parent, 'synthetic-module',
                         {'README.md': '# Synthetic submodule\n'})
        git = Git(root)
        (root / '.gitmodules').write_text(
            '[submodule "synthetic-module"]\n\tpath = ' + relative + '\n\turl = ./synthetic-module\n')
        git.run('add', '.gitmodules')
        git.run('update-index', '--add', '--cacheinfo',
                '160000,' + Git(child).text('rev-parse', 'HEAD') + ',' + relative)
        git.run('commit', '-m', 'Synthetic gitlink', env={
            'GIT_AUTHOR_NAME': 'Fixture Author', 'GIT_AUTHOR_EMAIL': 'author@example.invalid',
            'GIT_COMMITTER_NAME': 'Fixture Author', 'GIT_COMMITTER_EMAIL': 'author@example.invalid',
            'GIT_AUTHOR_DATE': '2026-10-01T10:00:00+00:00', 'GIT_COMMITTER_DATE': '2026-10-01T10:00:00+00:00'})
        marker, script = base / 'filter-invoked', base / 'fake-filter.py'
        script.write_text('import pathlib,sys\npathlib.Path(' + repr(str(marker))
                          + ').write_text("invoked")\nsys.stdout.buffer.write(sys.stdin.buffer.read())\n')
        argv = shlex.join([sys.executable, str(script)])
        if included:
            config = base / 'child-included.config'
            Git(child).run('config', '--file', str(config), 'filter.synthetic.clean', argv)
            Git(child).run('config', 'include.path', str(config))
        else:
            Git(child).run('config', 'filter.synthetic.clean', argv)
        (child / '.git/info/attributes').write_text('*.md filter=synthetic\n')
        doc = child / 'README.md'
        stamp = doc.stat().st_mtime_ns - 3_000_000_000
        os.utime(doc, ns=(stamp, stamp))  # Mismos bytes; fuerza la comprobación de clean.
        assert LocalGit(root).run('status', '--porcelain=v1', '--ignore-submodules=all') == b''
        assert LocalGit(root).run('config', '--includes', '--get-regexp',
                                  r'^filter\..*\.(clean|process)$', ok=(0, 1)) == b''
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
            try:
                return original(self, *args, **kwargs)
            finally:
                calls.append({'argv': list(args), 'filter_invoked': marker.exists()})

        try:
            with patch.object(Git, 'run', recording):
                if stage == 'conversation':
                    cid = world.create()
                    assert world.view(cid)['kind'] == 'project_import'
                    accepted, blockers = True, []
                else:
                    inventory = build_inventory(read_checkout(root))
                    accepted, blockers = not inventory['blockers'], inventory['blockers']
            result = {'path': relative, 'filter_via_include': included, 'stage': stage,
                      'accepted': accepted, 'blockers': blockers, 'filter_invoked': marker.exists(),
                      'calls': calls, 'all_checkout_and_git_bytes_unchanged': tree_state(root) == before}
            if stage == 'conversation':
                result.update(agent_calls=len(world.ports.agents.requests), jobs=job_count(world),
                              import_operation=ImportRepository(world.repo).get(root))
                assert result['agent_calls'] == result['jobs'] == 0 and result['import_operation'] is None
            first_effect = next(call for call in calls if call['filter_invoked'])
            assert first_effect['argv'][1] == 'status'
            assert marker.exists() and tree_state(root) == before
            assert accepted == (not location)
            marker.unlink()
            onboarding_inventory(root)
            result['flow_b_inventory_filter_invoked'] = marker.exists()
            assert not marker.exists() and tree_state(root) == before
            return result
        finally:
            if engine is not None:
                engine.dispose()


if __name__ == '__main__':
    print(json.dumps({
        'reviewed_commit': Git(ROOT).text('rev-parse', 'HEAD'),
        'git_version': Git(ROOT).text('--version'),
        'reproduction_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'historical_scripts_sha256': {
            name: sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in ('P008_REVISION_SALIDA_REPRO.py', 'P008_REVISION_SALIDA_2_REPRO.py')},
        'H1_filter': filter_probe(),
        **{name: import_probe(case) for name, case in (('H2_conversion', 'conversion'), ('H3_ignored', 'ignored'))},
        'H5_partial_clone': partial_clone_probe(),
        'H6_submodule': [submodule_probe(location, included, 'inventory')
                         for location in ('', 'docs') for included in (False, True)]
                        + [submodule_probe('', True, 'conversation')],
    }, ensure_ascii=False, indent=2))

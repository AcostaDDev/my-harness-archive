"""Revisión posterior a T016/T017: H1–H3 corregidos; H5, lazy-fetch del Flujo A.

Solo repositorios/SQLite temporales, datos sintéticos y revisores falsos.
No modifica las reproducciones ni la evidencia histórica de D104.
"""
from hashlib import sha256
import json
from pathlib import Path
import shlex
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

from alembic import command
from alembic.config import Config

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/product'))

from harness_local.adapters.git import Git
from harness_local.adapters.project_import import read_checkout
from harness_local.adapters.project_onboarding import read_inventory as onboarding_inventory
from harness_local.core.project_import import ImportInventoryError
from harness_local.storage.database import make_engine
from harness_local.storage.managed import Conflict
from harness_local.storage.phases import PhaseRepository
from harness_local.storage.project_import import ImportRepository
from test_import_commit import checkout_state, ready, preview
from test_import_conversation import World
from test_import_git_boundary import install_filter
from test_project_import import REFERENCE_PROJECT, checkout


def filter_probe():
    with TemporaryDirectory(prefix='p008-review2-filter-') as scratch:
        root = checkout(Path(scratch), 'repo', REFERENCE_PROJECT)
        marker = install_filter(root, 'clean', False)
        before = checkout_state(root)
        try:
            read_checkout(root)
        except ImportInventoryError as exc:
            diagnostic = str(exc)
        else:
            raise AssertionError('H1: inventory must reject executable filters')
        result = {'inventory_rejected': True, 'diagnostic': diagnostic,
                  'filter_executed': marker.exists(), 'unchanged': checkout_state(root) == before}
        assert not result['filter_executed'] and result['unchanged']
        return result


def import_probe(case):
    with TemporaryDirectory(prefix='p008-review2-' + case + '-') as scratch:
        base = Path(scratch)
        cfg = Config(str(ROOT / 'alembic.ini'))
        url = 'sqlite:///' + str(base / 'synthetic.sqlite3')
        cfg.attributes['database_url'] = url
        command.upgrade(cfg, 'head')
        engine = make_engine(url)
        try:
            files = dict(REFERENCE_PROJECT)
            if case == 'ignored':
                files['.gitignore'] += 'GEMINI.md\n'
            else:
                files['.gitattributes'] = 'GEMINI.md text eol=lf\n'
            world = World(checkout(base, 'repo', files), engine)
            cid = ready(world)
            if case == 'conversion':
                world.planning.edit_draft(world.context, cid, world.view(cid)['version'], path='GEMINI.md',
                    content='# Gemini\r\n\r\n@AGENTS.md\r\n', base_sha256=None, writer=None)
            before = checkout_state(world.context.root)
            try:
                preview(world, cid)
            except Conflict as exc:
                diagnostic = str(exc)
            else:
                raise AssertionError(case + ': preview must reject before confirmation')
            result = {'preview_rejected': True, 'diagnostic': diagnostic,
                      'unchanged': checkout_state(world.context.root) == before,
                      'new_file_written': world.context.path('GEMINI.md').exists(),
                      'operation_created': ImportRepository(world.repo).get(world.context.root) is not None,
                      'phase_count': len(PhaseRepository(world.repo).list(str(world.context.root))),
                      'commit_count': int(Git(world.context.root).text('rev-list', '--count', 'HEAD'))}
            assert result['unchanged'] and not result['new_file_written'] and not result['operation_created']
            assert result['phase_count'] == 0 and result['commit_count'] == 1
            return result
        finally:
            engine.dispose()


def partial_clone_probe():
    """Un objeto prometido ausente no debe ejecutar un transporte durante un inventario de lectura."""
    with TemporaryDirectory(prefix='p008-review2-promisor-') as scratch:
        base = Path(scratch)
        root = checkout(base, 'repo', {'README.md': '# Synthetic promisor fixture\n'})
        git = Git(root)
        blob = git.text('rev-parse', 'HEAD:README.md')
        marker, probe = base / 'fetch-invoked', base / 'upload-pack.py'
        probe.write_text('import pathlib\npathlib.Path(' + repr(str(marker))
                         + ').write_text("invoked")\nraise SystemExit(1)\n')
        for key, value in {
            'remote.origin.url': str(root),
            'remote.origin.promisor': 'true',
            'remote.origin.partialclonefilter': 'blob:none',
            'remote.origin.uploadpack': shlex.join([sys.executable, str(probe)]),
        }.items():
            git.run('config', key, value)
        # Simula un blob prometido ausente sin red ni un clone real.
        (root / '.git/objects' / blob[:2] / blob[2:]).unlink()
        before = checkout_state(root)
        calls, original = [], Git.run

        def recording(self, *args, **kwargs):
            try:
                return original(self, *args, **kwargs)
            finally:
                calls.append({'argv': list(args), 'upload_pack_invoked': marker.exists()})

        with patch.object(Git, 'run', recording):
            try:
                read_checkout(root)
            except Exception as exc:
                diagnostic = type(exc).__name__ + ': ' + str(exc)
            else:
                diagnostic = 'Inventory accepted'
        result = {'flow_a_upload_pack_invoked': marker.exists(), 'flow_a_diagnostic': diagnostic,
                  'flow_a_calls': calls, 'unchanged': checkout_state(root) == before}
        marker.unlink(missing_ok=True)
        try:
            onboarding_inventory(root)
        except Exception as exc:
            result['flow_b_diagnostic'] = type(exc).__name__ + ': ' + str(exc)
        else:
            raise AssertionError('Flow B must reject an unavailable promised blob')
        result['flow_b_upload_pack_invoked'] = marker.exists()
        # Describe el hallazgo de esta revisión: exit 0 no significa que H5 esté corregido.
        assert result['flow_a_upload_pack_invoked'] and not result['flow_b_upload_pack_invoked']
        assert result['unchanged'] and checkout_state(root) == before
        return result


if __name__ == '__main__':
    print(json.dumps({
        'reviewed_commit': Git(ROOT).text('rev-parse', 'HEAD'),
        'historical_reproduction_sha256': sha256(
            Path(__file__).with_name('P008_REVISION_SALIDA_REPRO.py').read_bytes()).hexdigest(),
        'filter': filter_probe(),
        **{case: import_probe(case) for case in ('conversion', 'ignored')},
        'partial_clone': partial_clone_probe(),
    }, ensure_ascii=False, indent=2))

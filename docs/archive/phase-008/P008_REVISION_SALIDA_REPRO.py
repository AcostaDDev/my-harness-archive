"""Reproducciones P008: operaciones del harness solo sobre repositorios y SQLite temporales."""
from hashlib import sha256
import json
import os
from pathlib import Path
import shlex
import sys
from tempfile import TemporaryDirectory

from alembic import command
from alembic.config import Config

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/product'))

from harness_local.adapters.git import Git
from harness_local.adapters.project_import import read_checkout
from harness_local.storage.database import make_engine
from harness_local.storage.project_import import ImportRepository
from test_import_conversation import World
from test_import_commit import ready, preview, confirm
from test_project_import import REFERENCE_PROJECT, checkout, git


def filter_probe():
    with TemporaryDirectory(prefix='p008-exit-filter-') as scratch:
        base = Path(scratch)
        root = base / 'repo'
        root.mkdir()
        port = Git(root)
        port.run('init', '-q')
        doc = root / 'README.md'
        doc.write_text('# Synthetic repository\n')
        (root / '.gitattributes').write_text('*.md filter=review-probe\n')
        port.run('add', '.')
        port.run('-c', 'user.name=Synthetic Review', '-c', 'user.email=review@example.invalid',
                 'commit', '-qm', 'synthetic base')
        marker = base / 'filter-invoked'
        script = base / 'filter.py'
        script.write_text('import pathlib, sys\npathlib.Path(' + repr(str(marker))
                          + ').write_text("invoked")\nsys.stdout.buffer.write(sys.stdin.buffer.read())\n')
        port.run('config', 'filter.review-probe.clean', shlex.join([sys.executable, str(script)]))
        stamp = doc.stat().st_mtime_ns
        os.utime(doc, ns=(stamp - 3_000_000_000, stamp - 3_000_000_000))
        result = read_checkout(root)
        return {'inventory_accepted': bool(result.entries), 'local_filter_executed': marker.exists()}


def import_probe(case):
    with TemporaryDirectory(prefix='p008-exit-' + case + '-') as scratch:
        base = Path(scratch)
        cfg = Config(str(ROOT / 'alembic.ini'))
        url = 'sqlite:///' + str(base / 'review.sqlite3')
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
            shown = preview(world, cid)
            confirm(world, cid, shown)
            result = {'preview_accepted': bool(shown['documents'])}
            try:
                result['job_status'] = world.worker.run_once().status
            except Exception as exc:
                result['exception'] = type(exc).__name__ + ': ' + str(exc)
            operation = ImportRepository(world.repo).get(world.context.root)
            result.update(operation_status=operation['status'], result_status=operation['result']['status'],
                          new_file_written=world.context.path('GEMINI.md').exists(),
                          commit_count=int(git(world.context.root, 'rev-list', '--count', 'HEAD')))
            doc = next(d for d in shown['documents'] if d['path'] == 'GEMINI.md')
            result['preview_after_sha256'] = doc['after_sha256']
            if world.context.path('GEMINI.md').exists():
                result['disk_sha256'] = sha256(world.context.path('GEMINI.md').read_bytes()).hexdigest()
            if result['commit_count'] == 2:
                blob = Git(world.context.root).run('cat-file', 'blob', 'HEAD:GEMINI.md')
                result['committed_sha256'] = sha256(blob).hexdigest()
                result['commit_matches_preview'] = result['committed_sha256'] == doc['after_sha256']
            return result
        finally:
            engine.dispose()


print(json.dumps({
    'reviewed_commit': Git(ROOT).text('rev-parse', 'HEAD'),
    'filter': filter_probe(),
    **{case: import_probe(case) for case in ('ignored', 'conversion')},
}, ensure_ascii=False, indent=2))

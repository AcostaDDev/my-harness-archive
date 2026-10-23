"""Verify the wheel installed in a new venv, with no checkout, cwd or Node at runtime."""
import argparse
from contextlib import closing, contextmanager
import hashlib
import json
from http.cookiejar import CookieJar
from pathlib import Path
import re
import socket
import shutil
import sqlite3
import subprocess
import tempfile
import time
import zipfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPCookieProcessor

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    distribution = args.dist.resolve()
    with zipfile.ZipFile(distribution / 'harness_local-0.1.0-py3-none-any.whl') as wheel:
        for source in (ROOT / 'src/harness_local').rglob('*'):
            if source.is_file() and '__pycache__' not in source.parts and source.suffix != '.pyc':
                assert wheel.read(str(source.relative_to(ROOT / 'src'))) == source.read_bytes()
        for asset in (ROOT / 'frontend/dist').rglob('*'):
            if asset.is_file():
                assert wheel.read('harness_local/web/' + str(asset.relative_to(ROOT / 'frontend/dist'))) == asset.read_bytes()
    with tempfile.TemporaryDirectory(prefix='harness-installed-') as temporary:
        work = Path(temporary).resolve()
        venv = work / 'venv'
        subprocess.run(['uv', 'venv', '--offline', '--no-python-downloads', '--python', str(ROOT / '.venv/bin/python'),
                        str(venv)], check=True)
        python = venv / 'bin/python'
        subprocess.run(['uv', 'pip', 'sync', '--offline', '--require-hashes', '--python', str(python),
                        str(distribution / 'requirements.txt')], check=True)
        subprocess.run(['uv', 'pip', 'install', '--offline', '--no-deps', '--python', str(python),
                        str(distribution / 'harness_local-0.1.0-py3-none-any.whl')], check=True)
        cli = venv / 'bin/harness-local'
        # Git is the only extra executable exposed to the managed synthetic journey.
        (venv / 'bin/git').symlink_to(shutil.which('git'))
        # PATH without Node, no PYTHONPATH, no product configuration from the environment. TMPDIR decides where
        # the session key and the service's temporary Git indexes live (ARCHITECTURE §9).
        (work / 'tmp').mkdir(mode=0o700)
        env = {'PATH': str(venv / 'bin'), 'LANG': 'en_US.UTF-8', 'PYTHONNOUSERSITE': '1', 'TMPDIR': str(work / 'tmp')}

        def run(*argv, ok=True, extra=None):
            result = subprocess.run([str(cli), *map(str, argv)], cwd=work, env=env | (extra or {}),
                                    capture_output=True, text=True, timeout=30)
            assert (result.returncode == 0) == ok, result.stderr
            return result

        opener = build_opener(HTTPCookieProcessor(CookieJar()))

        def request(base, path, data=None, headers=None, method=None):
            body = json.dumps(data).encode() if data is not None else None
            req = Request(base + path, body, headers={'Content-Type': 'application/json'} | (headers or {}), method=method)
            try:
                with opener.open(req, timeout=2) as response:
                    return response.status, response.read()
            except HTTPError as error:
                return error.code, error.read()

        @contextmanager
        def server(database, extra=None):
            nonlocal opener
            opener = build_opener(HTTPCookieProcessor(CookieJar()))
            with socket.socket() as bound:
                bound.bind(('127.0.0.1', 0))
                port = bound.getsockname()[1]
            base = f'http://127.0.0.1:{port}'
            with (work / 'server.log').open('w+') as log:
                process = subprocess.Popen([str(cli), 'serve', '--database', str(database), '--port', str(port)],
                                           cwd=work, env=env | (extra or {}), stdout=log, stderr=log)
                try:
                    for _ in range(150):
                        if process.poll() is not None:
                            log.seek(0)
                            raise AssertionError(log.read())
                        try:
                            if request(base, '/api/health')[0] == 401:
                                break
                        except (URLError, TimeoutError):
                            pass
                        time.sleep(.1)
                    else:
                        raise AssertionError('The server did not start within 15 s')
                    assert request(base, '/api/managed/projects')[0] == 401
                    log.flush()
                    log.seek(0)
                    # Matches the service's access-key line (harness_local.api.session).
                    key_path = Path(re.search(r'access key at (.+)', log.read())[1])
                    assert key_path.resolve().is_relative_to(work / 'tmp'), key_path
                    key = key_path.read_text()
                    assert request(base, '/api/session', {'key': key}, {'X-Harness-Local': '1'})[0] == 200
                    assert request(base, '/api/health')[0] == 200
                    yield base
                    assert request(base, '/api/session', headers={'X-Harness-Local': '1'}, method='DELETE')[0] == 204
                    assert request(base, '/api/simulations')[0] == 401
                    log.seek(0)
                    assert key not in log.read()

                finally:
                    if process.poll() is None:
                        process.terminate()
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
                        raise AssertionError('The service did not exit cleanly')

        db = work / 'synthetic.sqlite3'
        run('serve', '--database', db, ok=False)
        assert not db.exists()
        run('init-db', '--database', db)
        run('init-db', '--database', db, ok=False)
        # P010-T012: the installed entry point upgrades an existing database with a verified snapshot.
        snapshots = work / 'premigration'
        run('migrate', '--database', work / 'absent.sqlite3', '--snapshots', snapshots,
            '--writers-stopped', ok=False)
        assert not (work / 'absent.sqlite3').exists() and not snapshots.exists()
        subprocess.run([str(python), '-c',
            'import sys; from alembic import command; from harness_local.storage.migrate import _config; '
            'command.downgrade(_config("sqlite:///" + sys.argv[1]), "0022_project_preparation")', str(db)],
            cwd=work, env=env, check=True)
        run('serve', '--database', db, ok=False)
        run('migrate', '--database', db, '--snapshots', snapshots, ok=False)
        migration = json.loads(run('migrate', '--database', db, '--snapshots', snapshots,
                                   '--writers-stopped').stdout)
        assert migration['action'] == 'migrated' and migration['previous'] == '0022_project_preparation'
        snapshot = Path(migration['snapshot'])
        manifest = json.loads(snapshot.with_suffix('.json').read_text())
        assert manifest['format'] == 'premigration-1'
        assert manifest['sha256'] == hashlib.sha256(snapshot.read_bytes()).hexdigest()
        with closing(sqlite3.connect(snapshot)) as connection:
            assert connection.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
            assert connection.execute('SELECT version_num FROM alembic_version').fetchone()[0] == migration['previous']
        before = db.read_bytes()
        assert json.loads(run('migrate', '--database', db, '--snapshots', snapshots,
                             '--writers-stopped').stdout)['action'] == 'current'
        assert db.read_bytes() == before and len(list(snapshots.glob('*.sqlite3'))) == 1
        # Effective installation, migrations and templates outside the checkout.
        probe = subprocess.check_output([str(python), '-c',
            'import harness_local; print(harness_local.__file__)'], cwd=work, env=env, text=True)
        assert str(venv) in probe and str(ROOT) not in probe
        with server(db) as base:
            status, html = request(base, '/')
            assert status == 200 and b'<div id="root">' in html
            assets = re.findall(rb'(?:src|href)="(/assets/[^" ]+)"', html)
            assert len(assets) >= 2
            for asset in assets:
                assert request(base, asset.decode())[0] == 200
            assert request(base, '/api/nonexistent')[0] == 404
            status, projects = request(base, '/api/managed/projects')
            assert status == 200 and json.loads(projects) == []
            assert request(base, '/api/simulations', {'title': 'synthetic'})[0] == 403
            status, body = request(base, '/api/simulations', {'title': 'synthetic'}, {'X-Harness-Local': '1'})
            assert status == 201
            simulation = json.loads(body)
        with server(db) as base:
            assert request(base, '/api/simulations/' + simulation['id'])[0] == 200
        # H5.7: actual managed bootstrap -> task -> exact-content commit, all via HTTP.
        # Only the standalone synthetic port module is copied; installed code has no
        # development checkout on sys.path, and no provider executable is on PATH.
        shutil.copy2(ROOT / 'tests/fixtures/e2e/installed_config.py', work / 'installed_config.py')
        area = work / 'offline'
        area.mkdir()
        (area / 'project').mkdir()
        (area / 'marker').write_text('offline-installed-v2\n')
        fixture_env = {'PYTHONPATH': str(work), 'HARNESS_E2E_ROOT': str(area),
                       'HARNESS_MANAGED_CONFIG': 'installed_config:build'}
        headers = {'X-Harness-Local': '1'}
        def post(base, path, data, key=None, expected=202):
            status, body = request(base, path, data, headers | ({'Idempotency-Key': key} if key else {}), 'POST')
            assert status == expected, (status, body)
            return json.loads(body)
        def read(base, path):
            status, body = request(base, path)
            assert status == 200, (status, body)
            return json.loads(body)
        def settled(base, run_id):
            for _ in range(200):
                jobs = read(base, f'/api/managed/runs/{run_id}/jobs?limit=100')['items']
                if jobs and all(j['status'] not in ('QUEUED', 'ACTIVE') for j in jobs):
                    return read(base, f'/api/managed/runs/{run_id}')
                time.sleep(.05)
            raise AssertionError('Installed managed job did not settle')
        def roles():
            calls = area / 'calls.jsonl'
            return [json.loads(line)['role'] for line in calls.read_text().splitlines()] if calls.exists() else []
        # D088: the project is created by the definition conversation (v1 bootstrap retired, D089/D093).
        project = '/api/managed/projects/offline'
        with server(db, fixture_env) as base:
            assert request(base, project + '/bootstrap/preview', {}, headers)[0] in (404, 405)
            assert read(base, project + '/bootstrap')['enabled'] is True
            conversation = post(base, project + '/planning', {'kind': 'definition', 'title': 'Installed synthetic',
                                'brief': '# Brief\n\nOne synthetic outcome, offline only.\n'}, 'definition', 201)
            planning = f"{project}/planning/{conversation['id']}"
            turn = post(base, planning + '/messages', {'expected_version': 0, 'text': 'Draft the definition'}, 'turn')
            settled(base, turn['run_id'])
            for proposal in read(base, planning)['proposals']:
                post(base, f"{planning}/proposals/{proposal['id']}/apply",
                     {'expected_version': read(base, planning)['version'],
                      'proposal_sha256': proposal['proposal_sha256'], 'confirmed': True}, expected=200)
            shown = post(base, planning + '/accept/preview', None, expected=200)
            assert shown['ready'], shown['blockers']
            body = {'preview_sha256': shown['preview_sha256'], 'confirmed': True,
                    'reason': 'Reviewed installed preview', 'resume_operation_id': None, 'expected_version': None}
            post(base, planning + '/accept', {**body, 'confirmed': False}, 'create', expected=422)
            assert not (area / 'project/.git').exists()
            created = post(base, planning + '/accept', body, 'create')
            settled(base, created['run_id'])
            assert read(base, project + '/bootstrap')['definition_operation']['status'] == 'COMPLETED'
            assert (area / 'project/AGENTS.md').is_file() and (area / 'project/docs/DDBB-DIAGRAM.md').is_file()
            assert roles() == ['definition']
        with server(db, fixture_env) as base:
            assert post(base, planning + '/accept', body, 'create')['id'] == created['id']
            task_body = {'task_id': 'P001-T001', 'phase_id': 'P001', 'text': shown['task_text']}
            task = post(base, '/api/managed/projects/offline/runs', task_body, 'first-task')
            ready = settled(base, task['run_id'])
            assert ready['status'] == 'ACCEPTANCE_READY', ready['history'].get('stop')
            assert ready['history']['acceptance']['changed_paths'] == ['app/outcome.txt']
            action_path = f"/api/managed/runs/{task['run_id']}/actions"
            action_body = {'action': 'commit', 'expected_version': ready['version']}
            checkpoint = post(base, action_path, action_body, 'checkpoint')
            committed = settled(base, task['run_id'])
            assert committed['status'] == 'COMMITTED'
            assert committed['commit']['commit'] == committed['commit']['expected_commit']
            assert post(base, action_path, action_body, 'checkpoint')['id'] == checkpoint['id']
            historical_attempts = read(base, f"/api/managed/runs/{task['run_id']}/attempts")
            historical_events = read(base, f"/api/managed/runs/{task['run_id']}/events?limit=100")
        calls = (area / 'calls.jsonl').read_bytes()
        assert roles() == ['definition', 'executor', 'reviewer']
        with server(db, fixture_env) as base:
            assert read(base, f"/api/managed/runs/{task['run_id']}") == committed
            assert post(base, '/api/managed/projects/offline/runs', task_body, 'first-task')['id'] == task['id']
            assert post(base, action_path, action_body, 'checkpoint')['id'] == checkpoint['id']
            time.sleep(.1)
            assert (area / 'calls.jsonl').read_bytes() == calls

        # Incompatible configuration: visible failure, nothing corrected or activated. The expected texts are the
        # product's own English diagnostics (catalog keys runtime.config_reference, cli.schema_incompatible).
        result = run('--ui-language', 'en', 'serve', '--database', db, ok=False,
                     extra={'HARNESS_MANAGED_CONFIG': 'invalid'})
        assert 'module:attribute' in result.stderr
        empty = work / 'empty.sqlite3'
        empty.touch()
        result = run('--ui-language', 'en', 'serve', '--database', empty, ok=False)
        assert 'SQLite schema' in result.stderr
        bundle, restored = work / 'backup', work / 'restored'
        run('backup-create', db, bundle, '--writers-stopped')
        run('backup-verify', bundle)
        run('backup-restore', bundle, restored)
        restored_db = restored / 'state.sqlite3'
        # The restored evidence must be readable with its original Git checkout absent.
        (area / 'project').rename(work / 'unavailable-project')
        with server(restored_db, {'HARNESS_MANAGED_CONFIG': 'invalid'}) as base:
            assert request(base, '/')[0] == 200
            assert request(base, '/api/simulations/' + simulation['id'])[0] == 200
            assert request(base, '/api/simulations', {'title': 'forbidden'}, {'X-Harness-Local': '1'})[0] == 409
            archived = read(base, f"/api/managed/runs/{task['run_id']}")
            assert archived['history'] == committed['history']
            assert archived['commit'] == committed['commit']
            assert read(base, f"/api/managed/runs/{task['run_id']}/attempts") == historical_attempts
            assert read(base, f"/api/managed/runs/{task['run_id']}/events?limit=100") == historical_events
            assert read(base, '/api/managed/supervisor')['enabled'] is False
            assert request(base, action_path, action_body, headers | {'Idempotency-Key': 'archive-refused'})[0] == 409
            assert (area / 'calls.jsonl').read_bytes() == calls
        print('Isolated wheel: UI/assets/API, session, D088 definition/task/commit/restart, errors and restored evidence OK.')


if __name__ == '__main__':
    main()

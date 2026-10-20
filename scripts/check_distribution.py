"""Verifica wheel instalado en venv nuevo, sin checkout/cwd/Node en ejecución."""
import argparse
from contextlib import contextmanager
import json
from http.cookiejar import CookieJar
from pathlib import Path
import re
import socket
import shutil
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
        # PATH sin Node, sin PYTHONPATH, sin configuración ambiental de producto. TMPDIR decide dónde quedan
        # la clave de sesión y los índices temporales de Git del servicio (ARCHITECTURE §9).
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
                        raise AssertionError('El servidor no arrancó en 15 s')
                    assert request(base, '/api/managed/projects')[0] == 401
                    log.flush()
                    log.seek(0)
                    key_path = Path(re.search(r'clave de acceso en (.+)', log.read())[1])
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
                        raise AssertionError('El servicio no terminó limpiamente')

        db = work / 'synthetic.sqlite3'
        run('serve', '--database', db, ok=False)
        assert not db.exists()
        run('init-db', '--database', db)
        run('init-db', '--database', db, ok=False)
        # Instalación efectiva, migraciones y plantillas fuera del checkout.
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

        # Configuración incompatible: fallo visible, sin corregir ni activar nada.
        result = run('serve', '--database', db, ok=False, extra={'HARNESS_MANAGED_CONFIG': 'invalid'})
        assert 'módulo:atributo' in result.stderr
        empty = work / 'empty.sqlite3'
        empty.touch()
        result = run('serve', '--database', empty, ok=False)
        assert 'Esquema SQLite' in result.stderr
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
        print('Wheel aislado: UI/assets/API, sesión, definición D088/tarea/commit/reinicio, errores y evidencia restaurada correctos.')


if __name__ == '__main__':
    main()

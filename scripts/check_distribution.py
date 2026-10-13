"""Verifica wheel instalado en venv nuevo, sin checkout/cwd/Node en ejecución."""
import argparse
from contextlib import contextmanager
import json
from http.cookiejar import CookieJar
from pathlib import Path
import re
import socket
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
        # PATH sin Node, sin PYTHONPATH, sin configuración ambiental de producto.
        env = {'PATH': str(venv / 'bin'), 'LANG': 'en_US.UTF-8', 'PYTHONNOUSERSITE': '1'}

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
        with server(restored_db, {'HARNESS_MANAGED_CONFIG': 'invalid'}) as base:
            assert request(base, '/')[0] == 200
            assert request(base, '/api/simulations/' + simulation['id'])[0] == 200
            assert request(base, '/api/simulations', {'title': 'forbidden'}, {'X-Harness-Local': '1'})[0] == 409
        print('Wheel aislado: UI/assets/API, simulación/reinicio, errores, backup/restauración de consulta correctos.')


if __name__ == '__main__':
    main()

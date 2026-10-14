"""Desarrollo local con un solo comando: dependencias al día, base migrada, API :8013 y Vite :5173.

Uso: scripts/dev [--database RUTA] [--config TOML]

`uv run --frozen` (en scripts/dev) sincroniza el entorno Python desde uv.lock. Este
script reinstala el frontend solo si cambió su lock, migra la SQLite de desarrollo
con instantánea previa (storage/migrate.py), arranca la API y Vite en sus propios
grupos de procesos y los detiene juntos con Ctrl+C o si uno de ellos termina.
Sin red: npm y uv trabajan offline con las cachés de .local/.
"""
import argparse
import hashlib
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
from threading import Thread
import time

from toolchain import check_tools

ROOT = Path(__file__).resolve().parents[1]
API_PORT, UI_PORT = 8013, 5173  # fijados por frontend/package.json y vite.config.ts
STAMP = ROOT / '.local/dev/frontend-lock.sha256'


def lock_digest(root=ROOT):
    return hashlib.sha256((root / 'frontend/package-lock.json').read_bytes()).hexdigest()


def frontend_install_needed(root=ROOT, stamp=STAMP):
    if not (root / 'frontend/node_modules').is_dir() or not stamp.is_file():
        return True
    return stamp.read_text().strip() != lock_digest(root)


def ensure_frontend(root=ROOT, stamp=STAMP):
    if not frontend_install_needed(root, stamp):
        return False
    print('frontend: lock cambiado o dependencias ausentes; npm ci offline', flush=True)
    subprocess.run(['npm', 'ci', '--offline', '--ignore-scripts', '--no-audit', '--no-fund',
                    '--cache', str(root / '.local/npm-cache')], cwd=root / 'frontend', check=True)
    stamp.parent.mkdir(parents=True, exist_ok=True)
    stamp.write_text(lock_digest(root) + '\n')
    return True


def port_free(port):
    with socket.socket() as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            probe.bind(('127.0.0.1', port))
        except OSError:
            return False
    return True


def listening(port):
    with socket.socket() as probe:
        probe.settimeout(0.2)
        return probe.connect_ex(('127.0.0.1', port)) == 0


def stop(process, grace=10.0):
    """Terminar el grupo propio del hijo; matar solo si no termina a tiempo."""
    if process.poll() is not None:
        return process.returncode
    for sig, wait in ((signal.SIGTERM, grace), (signal.SIGKILL, 5.0)):
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            break
        try:
            return process.wait(timeout=wait)
        except subprocess.TimeoutExpired:
            continue
    return process.wait()


class Services:
    """Hijos en sesiones propias; el padre reenvía la parada y no deja huérfanos."""

    def __init__(self):
        self.children = []
        self.stopping = False

    def start(self, name, argv, *, env=None, cwd=ROOT, relay=None):
        process = subprocess.Popen(argv, cwd=cwd, env=env, start_new_session=True,
                                   stdout=subprocess.PIPE if relay else None,
                                   stderr=subprocess.STDOUT if relay else None, text=True)
        if relay:
            Thread(target=self._relay, args=(process, relay), daemon=True).start()
        self.children.append((name, process))
        return process

    @staticmethod
    def _relay(process, relay):
        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            relay(line)

    def wait_port(self, port, process, timeout=30.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and not self.stopping:
            if process.poll() is not None:
                return False
            if listening(port):
                return True
            time.sleep(0.2)
        return False

    def request_stop(self, *_):
        self.stopping = True

    def run(self):
        """Hasta Ctrl+C/TERM o hasta que un hijo termine; devuelve el código de salida."""
        code = 0
        while not self.stopping:
            for name, process in self.children:
                if process.poll() is not None:
                    print(f'{name} terminó con código {process.returncode}; deteniendo el resto', flush=True)
                    code = process.returncode or 1
                    self.stopping = True
                    break
            time.sleep(0.2)
        self.close()
        return code

    def close(self):
        for _, process in reversed(self.children):
            stop(process)


def api_command(database, config):
    env = {**os.environ, 'HARNESS_DATABASE_URL': f'sqlite:///{database}', 'PYTHONUNBUFFERED': '1'}
    if config is not None:
        if env.get('HARNESS_MANAGED_CONFIG'):
            raise SystemExit('--config y HARNESS_MANAGED_CONFIG son incompatibles; elegir una sola composición.')
        env.update(HARNESS_MANAGED_CONFIG='harness_local.services.local_config:from_environment',
                   HARNESS_LOCAL_CONFIG=str(config))
    argv = [sys.executable, '-m', 'uvicorn', 'harness_local.api.app:create_app', '--factory',
            '--host', '127.0.0.1', '--port', str(API_PORT), '--workers', '1',
            '--no-proxy-headers', '--no-access-log']
    return argv, env


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--database', type=Path, default=ROOT / '.local/harness.sqlite3',
                        help='SQLite de desarrollo (por defecto .local/harness.sqlite3)')
    parser.add_argument('--config', type=Path, help='TOML local-config-1/2/3 opcional; sin él, la API gestionada solo lee')
    args = parser.parse_args(argv)
    database = args.database.expanduser().absolute()
    config = args.config.expanduser().absolute() if args.config else None

    check_tools()
    busy = [port for port in (API_PORT, UI_PORT) if not port_free(port)]
    if busy:
        raise SystemExit(f'Puertos ocupados en 127.0.0.1: {busy}; detener el servicio anterior.')
    ensure_frontend()
    from harness_local.storage.migrate import MigrationRefused, prepare_database
    try:
        outcome = prepare_database(str(database), ROOT / '.local/backups')
    except (MigrationRefused, ValueError) as exc:
        raise SystemExit(f'Base de datos: {exc}') from None
    print(f'base: {database} ({outcome.action}, revisión {outcome.revision})'
          + (f'; instantánea previa {outcome.snapshot}' if outcome.snapshot else ''), flush=True)
    if config is not None:
        from harness_local.services.local_config import load_local_config
        load_local_config(config)  # validar antes de lanzar nada; no ejecuta procesos

    services = Services()
    signal.signal(signal.SIGINT, services.request_stop)
    signal.signal(signal.SIGTERM, services.request_stop)
    key = []
    api_argv, api_env = api_command(database, config)
    api = services.start('api', api_argv, env=api_env,
                         relay=lambda line: key.append(line.split(' en ', 1)[1].strip())
                         if 'clave de acceso en' in line else None)
    if not services.wait_port(API_PORT, api):
        services.close()
        return 0 if services.stopping else 1
    ui = services.start('ui', ['npm', '--prefix', 'frontend', 'run', 'dev'])
    if not services.wait_port(UI_PORT, ui):
        services.close()
        return 0 if services.stopping else 1
    print(f'\nHarness Local (desarrollo)\n  UI:    http://127.0.0.1:{UI_PORT}\n  API:   http://127.0.0.1:{API_PORT}\n'
          f'  Clave: {key[0] if key else "ver la línea «clave de acceso» de la API"}\n  Ctrl+C detiene ambos.\n', flush=True)
    return services.run()


if __name__ == '__main__':
    sys.exit(main())

"""Migración local con instantánea previa: base nueva, al día o actualizada tras copiar.

Las migraciones solo cambian SQLite; los artefactos externos no se tocan. Por eso
la instantánea es de la base (API de backup de SQLite, integridad y SHA-256) y no
un bundle H5.2, que exige el esquema actual. Nunca restaura ni borra nada: ante un
fallo conserva base e instantánea para inspección.
"""
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

from harness_local.launcher import initialize, local_database
from harness_local.storage.backup import RESTORED_USER_VERSION
from harness_local.storage.database import make_engine
from harness_local.storage.schema import require_schema

MIGRATIONS = Path(__file__).resolve().parents[1] / 'migrations'


class MigrationRefused(ValueError):
    pass


@dataclass(frozen=True)
class MigrationOutcome:
    action: str  # created | current | migrated
    previous: str | None
    revision: str
    snapshot: Path | None = None


def _config(url):
    config = Config()
    config.set_main_option('script_location', str(MIGRATIONS).replace('%', '%%'))
    config.attributes['database_url'] = url
    return config


def _connect(path, mode):
    connection = sqlite3.connect(f'{path.as_uri()}?mode={mode}', uri=True, isolation_level=None, timeout=1)
    connection.execute('PRAGMA trusted_schema=OFF')
    return connection


def _revision(path):
    with closing(_connect(path, 'ro')) as db:
        if db.execute('PRAGMA user_version').fetchone()[0] == RESTORED_USER_VERSION:
            raise MigrationRefused('Base restaurada de consulta (H5.2): no se migra.')
        try:
            rows = [r[0] for r in db.execute('SELECT version_num FROM alembic_version')]
        except sqlite3.OperationalError as exc:
            raise MigrationRefused('Base sin control de versiones Alembic; no se migra.') from exc
        if len(rows) != 1:
            raise MigrationRefused('Base con varias o ninguna revisión Alembic; no se migra.')
        return rows[0]


def _writers_alive(path):
    """Un servicio o escritor vivo sobre la base impide migrarla."""
    from harness_local.adapters.processes import liveness
    with closing(_connect(path, 'ro')) as db:
        try:
            owners = db.execute('SELECT process_owner FROM managed_jobs WHERE process_owner IS NOT NULL '
                                'AND NOT owner_closed').fetchall()
        except sqlite3.OperationalError:
            return False  # esquemas anteriores a los jobs gestionados
        return any(liveness(json.loads(row[0])) == 'alive' for row in owners)


def _snapshot(path, revision, target, directory):
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    destination = directory / f'{path.stem}-{revision}-{stamp}.sqlite3'
    # Exclusivo: nunca sobrescribir una copia anterior.
    with destination.open('xb'):
        pass
    os.chmod(destination, 0o600)
    with closing(_connect(path, 'ro')) as source, closing(_connect(destination, 'rw')) as copy:
        source.backup(copy)
        if copy.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise MigrationRefused(f'Instantánea con integridad inválida; base sin migrar: {destination}')
    raw = destination.read_bytes()
    manifest = {'format': 'premigration-1', 'source': str(path), 'source_revision': revision,
                'target_revision': target, 'snapshot': destination.name,
                'sha256': hashlib.sha256(raw).hexdigest(), 'size_bytes': len(raw),
                'created_at': datetime.now(timezone.utc).isoformat()}
    with destination.with_suffix('.json').open('x') as file:
        json.dump(manifest, file, indent=2, sort_keys=True)
    return destination


def prepare_database(value: str, snapshots: Path) -> MigrationOutcome:
    """Crear si falta; si hay migraciones pendientes, copiar y después `upgrade head`."""
    path, url = local_database(value)
    head = ScriptDirectory.from_config(_config(url)).get_current_head()
    if not path.exists():
        initialize(value)
        return MigrationOutcome('created', None, head)
    if not path.is_file() or path.is_symlink():
        raise MigrationRefused('La base debe ser un archivo regular, sin enlaces.')
    current = _revision(path)
    known = {script.revision for script in ScriptDirectory.from_config(_config(url)).walk_revisions()}
    if current not in known:
        raise MigrationRefused(f'Revisión {current} desconocida para este código (¿base más nueva?); no se migra.')
    if current == head:
        return MigrationOutcome('current', current, head)
    if _writers_alive(path):
        raise MigrationRefused('Hay un servicio o escritor vivo sobre la base; detenerlo antes de migrar.')
    snapshot = _snapshot(path, current, head, Path(snapshots))
    try:
        command.upgrade(_config(url), 'head')
        engine = make_engine(url)
        try:
            require_schema(engine)
        finally:
            engine.dispose()
    except Exception as exc:
        raise MigrationRefused(f'Migración fallida; base e instantánea conservadas ({snapshot}): {exc}') from exc
    return MigrationOutcome('migrated', current, head, snapshot)

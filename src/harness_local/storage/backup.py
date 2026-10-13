"""H5.2: bundles locales verificados; ningún puerto de ejecución ni escritura de checkout."""

import base64
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sqlite3
import stat

from harness_local.core.engine.serialization import load_history
from harness_local.storage.models import Base
from harness_local.storage.schema import SCHEMA_REVISION

FORMAT = 1
RESTORED_USER_VERSION = 0x483532
MAX_FILE_BYTES = 256 * 1024 * 1024
MAX_TOTAL_BYTES = 2 * 1024 * 1024 * 1024
MAX_FILES = 10000
MAX_MANIFEST_BYTES = 4 * 1024 * 1024


class BackupError(ValueError):
    pass


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _absolute(path):
    path = Path(path).expanduser().absolute()
    if '..' in path.parts or path.resolve() != path:
        raise BackupError(f'Ruta no canónica o enlazada: {path}')
    return path


def _relative(path):
    if not isinstance(path, str) or not path or any(p in ('', '.', '..') for p in path.split('/')) or PurePosixPath(path).is_absolute():
        raise BackupError('Ruta relativa insegura en el manifiesto.')
    return path


def _historical_path(path):
    # La referencia es dato congelado: verificar un bundle no consulta sus originales.
    if not isinstance(path, str) or not path.startswith('/') or any(p in ('.', '..', '') for p in path.split('/')[1:]):
        raise BackupError('Referencia absoluta histórica incompatible.')
    return Path(path)


def _read(path, limit=MAX_FILE_BYTES):
    """Cada componente se abre sin seguir enlaces; archivos especiales nunca bloquean."""
    path = _absolute(path)
    descriptors = []
    try:
        fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
        descriptors.append(fd)
        for part in path.parts[1:-1]:
            fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            descriptors.append(fd)
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        descriptors.append(fd)
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise BackupError(f'Archivo no regular o enlazado: {path}')
        if before.st_size > limit:
            raise BackupError(f'Límite de tamaño excedido: {path}')
        chunks, size = [], 0
        while chunk := os.read(fd, 65536):
            size += len(chunk)
            if size > limit:
                raise BackupError(f'Límite de tamaño excedido: {path}')
            chunks.append(chunk)
        after = os.fstat(fd)
        if (before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise BackupError(f'Archivo cambió durante la lectura: {path}')
        return b''.join(chunks)
    finally:
        for fd in reversed(descriptors):
            os.close(fd)


def _write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def _sync(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _connect(path, mode='ro'):
    connection = sqlite3.connect(f'{path.as_uri()}?mode={mode}', uri=True, isolation_level=None, timeout=1)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA trusted_schema=OFF')
    if mode == 'ro':
        connection.execute('PRAGMA query_only=ON')
    return connection


def is_read_only_archive(engine):
    from sqlalchemy import text
    with engine.connect() as connection:
        return connection.scalar(text('PRAGMA user_version')) == RESTORED_USER_VERSION


def _integrity(db, *, restored=False):
    if db.execute('PRAGMA integrity_check').fetchall()[0][0] != 'ok' or db.execute('PRAGMA foreign_key_check').fetchone():
        raise BackupError('Integridad SQLite o referencias FK inválidas.')
    revisions = [r[0] for r in db.execute('SELECT version_num FROM alembic_version')]
    if revisions != [SCHEMA_REVISION]:
        raise BackupError('Versión de esquema SQLite incompatible; no se migra automáticamente.')
    expected_version = RESTORED_USER_VERSION if restored else 0
    if db.execute('PRAGMA user_version').fetchone()[0] != expected_version:
        raise BackupError('Versión de restauración SQLite incompatible.')
    for name, table in Base.metadata.tables.items():
        columns = {r['name'] for r in db.execute(f'PRAGMA table_info("{name}")')}
        if columns != set(table.columns.keys()):
            raise BackupError(f'Esquema SQLite incompleto/incompatible: {name}')
    for row in db.execute('SELECT history_json FROM managed_runs'):
        try:
            history = load_history(row[0])
            for cycle in history.cycles:
                for entry in cycle.validation.entries:
                    for report in entry.reports:
                        if report.original_base64 is not None:
                            raw = base64.b64decode(report.original_base64, validate=True)
                            if _hash(raw) != report.sha256 or len(raw) != report.size_bytes:
                                raise BackupError('Original JUnit corrupto en el historial.')
        except (KeyError, TypeError, ValueError) as exc:
            raise BackupError(f'Historial gestionado incompatible o corrupto: {exc}') from exc


def _references(db):
    """Solo ubicaciones externas conocidas; jamás buscar arbitrariamente campos 'path'."""
    refs = {}

    def add(source, label, sha=None, size=None, *, optional=False, chunks=()):
        path = str(_historical_path(str(source)))
        ref = refs.setdefault(path, {'labels': [], 'expected': [], 'optional': True, 'chunks': []})
        ref['labels'].append(label)
        ref['optional'] &= optional
        if sha is not None:
            ref['expected'].append((sha, size))
        ref['chunks'].extend(chunks)

    for row in db.execute('SELECT * FROM managed_processes ORDER BY attempt_id'):
        spec, capture = json.loads(row['spec']), json.loads(row['capture']) if row['capture'] else None
        directory = _historical_path(spec['artifacts'])
        prompt = _historical_path(spec['prompt_path'])
        if prompt != directory / 'prompt.txt':
            raise BackupError('Referencia de prompt CLI incompatible.')
        add(prompt, f"process:{row['attempt_id']}:prompt", spec['prompt_sha256'])
        for stream in ('stdout', 'stderr'):
            chunks = []
            for event in db.execute("SELECT payload FROM managed_events WHERE kind='stream_bytes' AND run_id=(SELECT run_id FROM managed_attempts WHERE id=?) ORDER BY sequence", (row['attempt_id'],)):
                event = json.loads(event[0])
                if event.get('attempt_id') == row['attempt_id'] and event['stream'] == stream:
                    chunks.append((event['offset'], event['size'], event['sha256']))
            artifact = capture['artifacts'][stream] if capture else None
            path = directory / f'{stream}.bin'
            if artifact and _historical_path(artifact['path']) != path:
                raise BackupError('Referencia de stream CLI incompatible.')
            add(path, f"process:{row['attempt_id']}:{stream}", artifact['sha256'] if artifact else None,
                artifact['size'] if artifact else None, optional=not artifact and not chunks, chunks=chunks)
    snapshots = set()
    for row in db.execute('SELECT * FROM managed_activations ORDER BY id'):
        snapshots.add(row['snapshot_root'])
        if row['manifest_json']:
            if _hash(row['manifest_json'].encode()) != row['manifest_sha256']:
                raise BackupError('Manifiesto de migración corrupto.')
            manifest = json.loads(row['manifest_json'])
            if manifest['snapshot_root'] != row['snapshot_root']:
                raise BackupError('Referencia de snapshot de migración incompatible.')
            for artifact in manifest['artifacts']:
                if artifact['sha256']:
                    add(Path(row['snapshot_root']) / _relative(artifact['path']),
                        f"migration:{row['id']}:snapshot:{artifact['path']}", artifact['sha256'], artifact['size_bytes'])
        if row['export_path']:
            add(row['export_path'], f"migration:{row['id']}:export", row['export_sha256'])
    for row in db.execute('SELECT * FROM legacy_artifacts ORDER BY root,path'):
        if row['root'] in snapshots and row['sha256']:
            add(Path(row['root']) / _relative(row['path']), f"migration-snapshot:{row['root']}:{row['path']}", row['sha256'], row['size_bytes'])
    return refs


def _check_bytes(data, ref):
    for sha, size in ref['expected']:
        if _hash(data) != sha or (size is not None and len(data) != size):
            raise BackupError('Hash/tamaño distinto de la referencia SQLite.')
    previous = 0
    for offset, size, sha in ref['chunks']:
        if type(offset) is not int or type(size) is not int or offset != previous or size <= 0 or _hash(data[offset:offset + size]) != sha:
            raise BackupError('Rango/hash del stream distinto del evento persistido.')
        previous = offset + size


def _new_destination(destination):
    destination = _absolute(destination)
    if not destination.parent.is_dir():
        raise BackupError('El padre del destino debe existir.')
    try:
        destination.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise BackupError('El destino debe ser nuevo; no se sobrescribe ni reutiliza.') from exc
    return destination


def _finish(destination, manifest):
    raw = _json(manifest)
    if len(raw) > MAX_MANIFEST_BYTES:
        raise BackupError('Manifiesto excede el límite.')
    _write(destination / 'manifest.json', raw)
    _write(destination / 'COMPLETE', _hash(raw).encode())
    for directory, _, _ in os.walk(destination, topdown=False):
        _sync(Path(directory))
    _sync(destination.parent)


def _create_backup(database, destination, *, artifact_roots=(), writers_stopped=False, hook=None):
    """Servicio/observadores/escritores detenidos explícitamente; BEGIN IMMEDIATE cierra carreras DB."""
    if writers_stopped is not True:
        raise BackupError('Detener servicio y escritores; se requiere --writers-stopped.')
    database, destination = _absolute(database), _absolute(destination)
    _read(database)  # validar ruta/tipo antes de abrir SQLite
    for suffix in ('-wal', '-shm', '-journal'):
        sidecar = Path(str(database) + suffix)
        if os.path.lexists(sidecar):
            _read(sidecar)  # SQLite también abre estos archivos; no admitir enlaces/especiales.
    roots = tuple(_absolute(root) for root in artifact_roots)
    if any(not r.is_dir() or r == Path('/') for r in roots):
        raise BackupError('Raíces de artefactos deben ser directorios explícitos acotados.')
    if destination == database or any(destination.is_relative_to(r) or r.is_relative_to(destination) for r in roots):
        raise BackupError('Destino solapado con los originales.')
    before = database.stat()
    with closing(_connect(database, 'rw')) as lock:
        lock.execute('BEGIN IMMEDIATE')
        try:
            _integrity(lock)
            from harness_local.adapters.processes import liveness
            for row in lock.execute('SELECT process_owner, owner_closed FROM managed_jobs WHERE process_owner IS NOT NULL'):
                if not row['owner_closed'] and liveness(json.loads(row['process_owner'])) == 'alive':
                    raise BackupError('Propietario del servicio vivo; detenerlo antes de copiar.')
            for row in lock.execute('SELECT identity FROM managed_processes WHERE identity IS NOT NULL'):
                if liveness(json.loads(row['identity']), group=True) == 'alive':
                    raise BackupError('Grupo de procesos vivo; detener escritores antes de copiar.')
            checkouts = {Path(r[0]) for r in lock.execute('SELECT root FROM managed_runs UNION SELECT root FROM managed_activations UNION SELECT root FROM managed_phases')}
            if any(destination.is_relative_to(r) or any(root.is_relative_to(r) or r.is_relative_to(root) for root in roots) for r in checkouts):
                raise BackupError('Backup/artefactos deben estar fuera de los checkouts.')
            # No probar muerte por lease ni modificar jobs/locks. Un estado incierto puede copiarse,
            # siempre bajo la declaración de parada y con todos sus bytes verificables.
            destination = _new_destination(destination)
            db_path = destination / 'state.sqlite3'
            with closing(_connect(database)) as source, closing(_connect(db_path, 'rwc')) as target:
                source.backup(target)
                _integrity(target)
                # También la copia en sí impide abrir accidentalmente otra cola escritora.
                target.execute(f'PRAGMA user_version={RESTORED_USER_VERSION}')
            os.chmod(db_path, 0o600)
            _sync(db_path)
            if hook:
                hook('database_copied')
            refs = _references(lock)
            files, absent, total = [], [], 0
            if len(refs) > MAX_FILES:
                raise BackupError('Demasiadas referencias de artefactos.')
            for index, (source, ref) in enumerate(sorted(refs.items())):
                path = Path(source)
                if not any(path.is_relative_to(root) for root in roots):
                    raise BackupError(f'Referencia fuera de --artifact-root: {source}')
                try:
                    raw = _read(path)
                except FileNotFoundError:
                    if not ref['optional']:
                        raise BackupError(f'Artefacto requerido ausente: {source}')
                    absent.append(source)
                    continue
                _check_bytes(raw, ref)
                total += len(raw)
                if total > MAX_TOTAL_BYTES:
                    raise BackupError('Artefactos exceden el límite total.')
                relative = f'artifacts/{index:06d}.bin'
                _write(destination / relative, raw)
                files.append({'source': source, 'path': relative, 'sha256': _hash(raw), 'size_bytes': len(raw), 'labels': ref['labels']})
                if hook:
                    hook('artifact_copied')
            # Releer el conjunto al terminar detecta cambios entre archivos, también opcionales.
            for item in files:
                raw = _read(item['source'])
                if _hash(raw) != item['sha256'] or len(raw) != item['size_bytes']:
                    raise BackupError('Artefactos cambiaron durante la copia.')
            if any(os.path.lexists(path) for path in absent):
                raise BackupError('Apareció un artefacto durante la copia.')
            after = database.stat()
            if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
                raise BackupError('La SQLite de origen fue reemplazada durante la copia.')
            raw_db = _read(db_path)
            manifest = {'format': FORMAT, 'kind': 'backup', 'schema': SCHEMA_REVISION,
                        'consistency': 'service-and-writers-stopped/sqlite-backup/write-lock',
                        'database': {'path': 'state.sqlite3', 'sha256': _hash(raw_db), 'size_bytes': len(raw_db)},
                        'files': files, 'absent_optional': absent,
                        'external_legacy_sources': [r[0] for r in lock.execute('SELECT root FROM legacy_sources ORDER BY root') if r[0] not in {r[0] for r in lock.execute('SELECT snapshot_root FROM managed_activations')}],
                        'runs': [dict(r) for r in lock.execute('SELECT id,root,status,purpose FROM managed_runs ORDER BY id')],
                        'execution_authorized': False}
            _finish(destination, manifest)
            return manifest
        finally:
            lock.rollback()


def create_backup(database, destination, *, artifact_roots=(), writers_stopped=False, hook=None):
    try:
        return _create_backup(database, destination, artifact_roots=artifact_roots,
                              writers_stopped=writers_stopped, hook=hook)
    except (OSError, sqlite3.Error, KeyError, TypeError, ValueError, RecursionError) as exc:
        if isinstance(exc, BackupError):
            raise
        raise BackupError(f'Copia no publicada; origen inválido o inaccesible: {exc}') from exc


def verify_bundle(bundle):
    """Verifica manifiesto, DB, originales embebidos y correspondencia completa de referencias."""
    bundle = _absolute(bundle)
    try:
        raw = _read(bundle / 'manifest.json', MAX_MANIFEST_BYTES)
        if _read(bundle / 'COMPLETE', 64) != _hash(raw).encode():
            raise BackupError('Bundle incompleto o manifiesto corrupto.')
        manifest = json.loads(raw)
        if (type(manifest['format']) is not int or manifest['format'] != FORMAT or manifest['schema'] != SCHEMA_REVISION or
                manifest['kind'] not in ('backup', 'restored') or manifest['execution_authorized'] is not False):
            raise BackupError('Versión/formato de backup incompatible.')
        database = manifest['database']
        if database['path'] != 'state.sqlite3':
            raise BackupError('Ruta SQLite incompatible.')
        raw_db = _read(bundle / database['path'])
        if _hash(raw_db) != database['sha256'] or len(raw_db) != database['size_bytes']:
            raise BackupError('Hash/tamaño SQLite corrupto.')
        for suffix in ('-wal', '-journal'):
            sidecar = bundle / (database['path'] + suffix)
            if os.path.lexists(sidecar) and _read(sidecar):
                raise BackupError('Bundle con WAL/journal no vacío; la SQLite sellada debe ser autosuficiente.')
        if len(manifest['files']) > MAX_FILES:
            raise BackupError('Demasiados artefactos.')
        with closing(_connect(bundle / 'state.sqlite3')) as db:
            _integrity(db, restored=True)
            refs = _references(db)
            runs = [dict(r) for r in db.execute('SELECT id,root,status,purpose FROM managed_runs ORDER BY id')]
            if manifest['runs'] != runs:
                raise BackupError('Inventario de runs distinto de la autoridad SQLite.')
        sources, paths, total = set(), set(), 0
        for item in manifest['files']:
            relative = _relative(item['path'])
            source = item['source']
            if not relative.startswith('artifacts/') or relative in paths or source in sources or source not in refs:
                raise BackupError('Referencias de artefactos duplicadas/incompatibles.')
            data = _read(bundle / relative)
            total += len(data)
            if total > MAX_TOTAL_BYTES or _hash(data) != item['sha256'] or len(data) != item['size_bytes']:
                raise BackupError('Hash/tamaño de artefacto corrupto o límite excedido.')
            _check_bytes(data, refs[source])
            if item['labels'] != refs[source]['labels']:
                raise BackupError('Procedencia de artefacto incompatible.')
            sources.add(source)
            paths.add(relative)
        absent = manifest['absent_optional']
        if len(set(absent)) != len(absent) or sources & set(absent) or set(refs) != sources | set(absent) or any(not refs[s]['optional'] for s in absent):
            raise BackupError('Referencias ausentes en el backup.')
        return manifest
    except (OSError, sqlite3.Error, KeyError, TypeError, ValueError, RecursionError) as exc:
        if isinstance(exc, BackupError):
            raise
        raise BackupError(f'Bundle inválido/incompatible: {exc}') from exc


def restore_backup(bundle, destination):
    bundle, destination = _absolute(bundle), _absolute(destination)
    if destination.is_relative_to(bundle) or bundle.is_relative_to(destination):
        raise BackupError('Restauración solapada con el backup.')
    manifest = verify_bundle(bundle)  # Nada creado hasta verificar los originales completos.
    with closing(_connect(bundle / 'state.sqlite3')) as db:
        checkouts = [Path(r[0]) for r in db.execute('SELECT root FROM managed_runs UNION SELECT root FROM managed_activations UNION SELECT root FROM managed_phases')]
    if any(destination.is_relative_to(r) or r.is_relative_to(destination) for r in checkouts):
        raise BackupError('Restauración debe estar fuera de los checkouts históricos.')
    destination = _new_destination(destination)
    raw = _read(bundle / 'state.sqlite3')
    if _hash(raw) != manifest['database']['sha256']:
        raise BackupError('SQLite cambió después de verificar el backup.')
    _write(destination / 'state.sqlite3', raw)
    # Marca interna persistente: make_engine activa query_only, incluso al mover el fichero.
    with closing(_connect(destination / 'state.sqlite3', 'rw')) as db:
        db.execute(f'PRAGMA user_version={RESTORED_USER_VERSION}')
    for item in manifest['files']:
        data = _read(bundle / item['path'])
        if _hash(data) != item['sha256']:
            raise BackupError('Artefacto cambió después de verificar el backup.')
        _write(destination / item['path'], data)
    raw = _read(destination / 'state.sqlite3')
    restored = {**manifest, 'kind': 'restored', 'restored_from': manifest['database']['sha256'],
                'database': {**manifest['database'], 'sha256': _hash(raw), 'size_bytes': len(raw)}}
    _finish(destination, restored)
    verify_bundle(destination)
    return restored


def restored_artifact(engine, source):
    """Resolver referencias históricas sin reescribir snapshots ni volver a los originales."""
    if not is_read_only_archive(engine):
        return None
    bundle = Path(engine.url.database).resolve().parent
    raw = _read(bundle / 'manifest.json', MAX_MANIFEST_BYTES)
    if _read(bundle / 'COMPLETE', 64) != _hash(raw).encode():
        raise BackupError('Manifiesto restaurado corrupto.')
    manifest = json.loads(raw)
    return next((bundle / _relative(item['path']) for item in manifest['files'] if item['source'] == str(source)), None)

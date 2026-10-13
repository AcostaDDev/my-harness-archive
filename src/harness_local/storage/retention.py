"""Explicit offline retention of sealed CLI streams; history is never rewritten."""

from contextlib import closing
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import stat
from uuid import uuid4

from harness_local.storage.backup import (
    BackupError, MAX_FILE_BYTES, MAX_FILES, MAX_TOTAL_BYTES, _absolute, _check_bytes, _connect,
    _hash, _integrity, _json, _read, _references,
)

INTENT = 'log_retention_intent'
REMOVED = 'log_retention_removed'
TERMINAL_RUNS = {'STOPPED', 'BLOCKED', 'REVISION_LIMIT', 'ACCEPTANCE_READY', 'COMMITTED', 'COMPLETED'}
TERMINAL_ATTEMPTS = {'COMPLETE', 'COMPLETED', 'FAILED', 'TIMED_OUT', 'CANCELLED', 'INVALID', 'PARTIAL'}


def _time(value):
    if not isinstance(value, str):
        raise ValueError('La fecha debe ser texto ISO-8601 UTC.')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None or result.utcoffset().total_seconds() != 0:
        raise ValueError('La fecha debe incluir zona UTC.')
    return result


def policy(before, min_bytes=1024 * 1024):
    if type(min_bytes) is not int or min_bytes < 1:
        raise ValueError('min_bytes debe ser un entero positivo.')
    return {'format': 1, 'before': _time(before).isoformat(), 'min_bytes': min_bytes,
            'scope': 'sealed-managed-cli-stdout-stderr', 'automatic': False}


def audit(db, refs):
    """Validate tombstones against frozen references, including their authorization."""
    intents, removed = {}, {}
    for row in db.execute('SELECT * FROM managed_events WHERE kind IN (?,?) ORDER BY id', (INTENT, REMOVED)):
        p = json.loads(row['payload'])
        if not isinstance(p, dict) or any(not isinstance(p.get(k), str) for k in (
                'source', 'operation_id', 'attempt_id', 'stream', 'sha256', 'reference_sha256', 'preview_sha256', 'reason')):
            raise BackupError('Auditoría de retención malformada.')
        if (not isinstance(p.get('actor'), dict) or type(p['actor'].get('uid')) is not int or
                not isinstance(p.get('policy'), dict)):
            raise BackupError('Identidad/política de retención malformada.')
        source, operation = p['source'], p['operation_id']
        ref = refs.get(source)
        label = f"process:{p['attempt_id']}:{p['stream']}"
        if (ref is None or p['stream'] not in ('stdout', 'stderr') or ref['labels'] != [label] or
                not ref['expected'] or any(sha != p['sha256'] or size != p['size_bytes'] for sha, size in ref['expected']) or
                type(p['size_bytes']) is not int or p['size_bytes'] < 1 or
                p['reference_sha256'] != _hash(_json(ref))):
            raise BackupError('Auditoría de retención incompatible con la referencia sellada.')
        attempt = db.execute('SELECT run_id FROM managed_attempts WHERE id=?', (p['attempt_id'],)).fetchone()
        if not attempt or attempt[0] != row['run_id']:
            raise BackupError('Procedencia de retención incompatible.')
        key = (source, operation)
        if row['kind'] == INTENT:
            if source in intents or source in removed or not p['reason'].strip() or not p['actor'] or len(p['preview_sha256']) != 64:
                raise BackupError('Autorización de retención inválida o duplicada.')
            if policy(p['policy']['before'], p['policy']['min_bytes']) != p['policy']:
                raise BackupError('Política de retención incompatible.')
            intents[source] = {**p, 'recorded_at': row['recorded_at']}
        else:
            intent = intents.get(source)
            if not intent or (source, intent['operation_id']) != key or source in removed:
                raise BackupError('Purga sin intención autorizada o duplicada.')
            for field in ('attempt_id', 'stream', 'sha256', 'reference_sha256', 'size_bytes', 'preview_sha256', 'reason', 'actor', 'policy'):
                if p[field] != intent[field]:
                    raise BackupError('Resultado de retención distinto de su intención.')
            if (p['observed_removed_bytes'] is not None and
                    (type(p['observed_removed_bytes']) is not int or p['observed_removed_bytes'] != p['size_bytes'])):
                raise BackupError('Contabilidad de retención inválida.')
            removed[source] = {**p, 'recorded_at': row['recorded_at']}
    return intents, removed


def authorized_absences(db, refs):
    intents, removed = audit(db, refs)
    if set(intents) != set(removed):
        raise BackupError('Retención pendiente de conciliación explícita; no publicar backup.')
    return removed


def _eligible(db, row):
    if (row['run_status'] not in TERMINAL_RUNS or row['status'] != 'STOPPED' or
            row['attempt_status'] not in TERMINAL_ATTEMPTS or not row['result_json'] or not row['finished_at'] or
            row['job_status'] != 'DONE'):
        return 'Intento/run/job activo, incierto o sin resultado sellado.'
    if db.execute('SELECT 1 FROM checkout_locks WHERE root=?', (row['root'],)).fetchone():
        return 'Checkout bloqueado.'
    if db.execute("SELECT 1 FROM managed_jobs j JOIN managed_runs r ON r.id=j.run_id WHERE r.root=? AND j.status IN ('QUEUED','ACTIVE','RECOVERY_REQUIRED')", (row['root'],)).fetchone():
        return 'Trabajo pendiente o incierto en el checkout.'
    if db.execute('SELECT 1 FROM managed_attempts WHERE run_id=? AND (result_json IS NULL OR finished_at IS NULL)', (row['run_id'],)).fetchone():
        return 'Run con otro intento incierto.'
    from harness_local.adapters.processes import liveness
    if not row['identity'] or liveness(json.loads(row['identity']), group=True) != 'dead':
        return 'No se ha comprobado la muerte del grupo.'
    return None


def _rows(db):
    return db.execute('''SELECT p.*, a.run_id, a.status AS attempt_status, a.result_json,
        a.finished_at, r.root, r.status AS run_status, j.status AS job_status
        FROM managed_processes p JOIN managed_attempts a ON a.id=p.attempt_id
        JOIN managed_runs r ON r.id=a.run_id JOIN managed_jobs j ON j.id=p.job_id
        ORDER BY a.run_id,a.number''').fetchall()


def _preview(db, roots, selected_policy):
    refs = _references(db)
    if len(refs) > MAX_FILES:
        raise ValueError('Demasiadas referencias de artefactos.')
    intents, removed = audit(db, refs)
    checkouts = [Path(r[0]) for r in db.execute('SELECT root FROM managed_runs UNION SELECT root FROM managed_activations UNION SELECT root FROM managed_phases')]
    if not roots or any(not r.is_dir() or r == Path('/') or any(r.is_relative_to(c) or c.is_relative_to(r) for c in checkouts) for r in roots):
        raise ValueError('Raíces explícitas de artefactos fuera de checkouts requeridas.')
    database = Path(db.execute('PRAGMA database_list').fetchone()['file'])
    if any(database.is_relative_to(c) for c in checkouts):
        raise ValueError('SQLite debe estar fuera de los checkouts.')
    items, total = [], 0
    for row in _rows(db):
        if not row['capture']:
            continue
        capture = json.loads(row['capture'])
        for stream in ('stdout', 'stderr'):
            artifact = capture['artifacts'][stream]
            source = artifact['path']
            item = {'run_id': row['run_id'], 'attempt_id': row['attempt_id'], 'stream': stream,
                    'source': source, 'sha256': artifact['sha256'], 'size_bytes': artifact['size'],
                    'reference_sha256': _hash(_json(refs[source])),
                    'finished_at': row['finished_at'], 'eligible': False, 'diagnostic': None,
                    'authorization': intents.get(source), 'state': 'retained'}
            diagnostic = _eligible(db, row)
            if source in removed:
                item['state'], diagnostic = 'purged', 'Purga autorizada conservada en el historial.'
            elif not any(Path(source).is_relative_to(root) for root in roots):
                diagnostic = 'Fuera de las raíces permitidas.'
            elif refs[source]['labels'] != [f"process:{row['attempt_id']}:{stream}"]:
                diagnostic = 'Referencia compartida con evidencia que debe conservarse.'
            elif diagnostic is None and source not in intents and (
                    _time(row['finished_at']) >= _time(selected_policy['before']) or artifact['size'] < selected_policy['min_bytes']):
                diagnostic = 'Conservado por edad o tamaño de la política.'
            if diagnostic is None:
                try:
                    raw = _read(source)
                    _check_bytes(raw, refs[source])
                    # Capture and events both describe these exact original bytes.
                    if _hash(raw) != item['sha256'] or len(raw) != item['size_bytes']:
                        raise ValueError('Hash/tamaño distintos del original sellado.')
                    item['eligible'] = True
                except FileNotFoundError:
                    item['state'] = 'pending' if source in intents else 'missing'
                    item['eligible'] = source in intents
                    diagnostic = 'Ausente tras intención autorizada; requiere conciliación.' if source in intents else 'Archivo perdido; no hay purga autorizada.'
                except (OSError, ValueError) as exc:
                    item['state'], diagnostic = 'unverified', str(exc)
            if source in intents and source not in removed:
                item['state'] = 'pending'
            item['diagnostic'] = diagnostic
            if item['eligible']:
                total += item['size_bytes']
            items.append(item)
    if len(items) > MAX_FILES or total > MAX_TOTAL_BYTES:
        raise ValueError('Retención excede los límites de archivos/bytes.')
    result = {'format': 1, 'policy': selected_policy, 'artifact_roots': list(map(str, roots)),
              'items': items, 'retire_bytes': total,
              'preserved': ['history', 'contracts', 'prompts', 'snapshots', 'permissions', 'approvals', 'verdicts', 'stream-hashes-and-ranges', 'JUnit', 'migration-artifacts']}
    return {**result, 'preview_sha256': _hash(_json(result))}


def _database(database):
    path = _absolute(database)
    _read(path)
    for suffix in ('-wal', '-shm', '-journal'):
        sidecar = Path(str(path) + suffix)
        if os.path.lexists(sidecar):
            _read(sidecar)
    return path


def preview_retention(database, *, artifact_roots, before, min_bytes=1024 * 1024):
    with closing(_connect(_database(database))) as db:
        db.execute('BEGIN')
        _integrity(db)
        return _preview(db, tuple(_absolute(r) for r in artifact_roots), policy(before, min_bytes))


def _event(db, run_id, kind, payload):
    now = datetime.now(timezone.utc).isoformat()
    db.execute('UPDATE managed_runs SET version=version+1,updated_at=? WHERE id=?', (now, run_id))
    version = db.execute('SELECT version FROM managed_runs WHERE id=?', (run_id,)).fetchone()[0]
    db.execute('INSERT INTO managed_events(run_id,sequence,kind,recorded_at,payload) VALUES(?,?,?,?,?)',
               (run_id, version, kind, now, _json(payload).decode()))


def _stopped(db, writers_stopped):
    if writers_stopped is not True:
        raise ValueError('Detener servicio/escritores; se requiere --writers-stopped.')
    if db.execute('SELECT 1 FROM managed_jobs WHERE process_owner IS NOT NULL AND owner_closed=0').fetchone():
        raise ValueError('Propietario del servicio abierto; detenerlo antes de purgar.')
    from harness_local.adapters.processes import liveness
    for row in db.execute('SELECT identity FROM managed_processes WHERE identity IS NOT NULL'):
        if liveness(json.loads(row[0]), group=True) != 'dead':
            raise ValueError('Grupo vivo o incierto; no purgar.')

    from harness_local.storage.command_processes import persisted_identities
    if any(liveness(value, group=True) != 'dead' for value in persisted_identities(db)):
        raise ValueError('Grupo de validación vivo o incierto; no purgar.')


def _unlink_verified(source, ref):
    """Keep parent descriptors open through verification/unlink; never follow links."""
    source = _absolute(source)
    fds = []
    try:
        fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
        fds.append(fd)
        for part in source.parts[1:-1]:
            fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            fds.append(fd)
        file_fd = os.open(source.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        fds.append(file_fd)
        before = os.fstat(file_fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > MAX_FILE_BYTES:
            raise ValueError('Archivo no regular, enlazado o demasiado grande antes de purgar.')
        chunks, size = [], 0
        while chunk := os.read(file_fd, 65536):
            size += len(chunk)
            if size > MAX_FILE_BYTES:
                raise ValueError('Log excede el límite antes de purgar.')
            chunks.append(chunk)
        data = b''.join(chunks)
        _check_bytes(data, ref)
        after = os.stat(source.name, dir_fd=fd, follow_symlinks=False)
        signature = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_nlink)
        if signature(before) != signature(after) or signature(before) != signature(os.fstat(file_fd)):
            raise ValueError('Archivo sustituido antes de purgar.')
        os.unlink(source.name, dir_fd=fd)
        os.fsync(fd)
        return len(data)
    finally:
        for fd in reversed(fds):
            os.close(fd)


def apply_retention(database, *, artifact_roots, before, min_bytes=1024 * 1024,
                    preview_sha256, reason, confirmed=False, writers_stopped=False, hook=None):
    if confirmed is not True or not isinstance(reason, str) or not reason.strip() or len(reason) > 2000:
        raise ValueError('Confirmación explícita y motivo de 1–2000 caracteres requeridos.')
    roots, selected_policy = tuple(_absolute(r) for r in artifact_roots), policy(before, min_bytes)
    with closing(_connect(_database(database), 'rw')) as db:
        db.execute('BEGIN IMMEDIATE')
        try:
            _integrity(db)
            _stopped(db, writers_stopped)
            preview = _preview(db, roots, selected_policy)
            if preview['preview_sha256'] != preview_sha256:
                raise ValueError('Vista previa obsoleta; revisar y confirmar un hash nuevo.')
            candidates = [i for i in preview['items'] if i['eligible']]
            operation = str(uuid4())
            for item in candidates:
                if not item['authorization']:
                    payload = {k: item[k] for k in ('source', 'attempt_id', 'stream', 'sha256', 'reference_sha256', 'size_bytes')}
                    payload.update(operation_id=operation, preview_sha256=preview_sha256, reason=reason,
                                   actor={'uid': os.getuid()}, policy=selected_policy)
                    _event(db, item['run_id'], INTENT, payload)
                else:
                    _event(db, item['run_id'], 'log_retention_reconfirmed', {
                        'operation_id': item['authorization']['operation_id'], 'source': item['source'],
                        'preview_sha256': preview_sha256, 'reason': reason,
                        'actor': {'uid': os.getuid()}, 'policy': selected_policy})
            db.commit()  # Authorization is durable before any filesystem effect.
            if hook:
                hook('intents_saved')
            db.execute('BEGIN IMMEDIATE')
            _stopped(db, writers_stopped)
            fresh = _preview(db, roots, selected_policy)
            fresh_by_source = {i['source']: i for i in fresh['items']}
            if any(not fresh_by_source[i['source']]['eligible'] for i in candidates):
                raise ValueError('Elegibilidad cambió tras guardar la intención; conciliar explícitamente.')
            refs = _references(db)
            removed = []
            for item in candidates:
                current = fresh_by_source[item['source']]
                try:
                    observed = _unlink_verified(item['source'], refs[item['source']])
                except FileNotFoundError:
                    if not item['authorization']:
                        raise ValueError('Archivo perdido antes del efecto; intención pendiente.')
                    observed = None  # Crash reconciliation cannot invent an observed unlink.
                if hook:
                    hook('bytes_removed')
                payload = {k: v for k, v in current['authorization'].items() if k != 'recorded_at'}
                payload['observed_removed_bytes'] = observed
                _event(db, item['run_id'], REMOVED, payload)
                removed.append(payload)
            db.commit()
            return {'removed': removed, 'retired_bytes': sum(i['size_bytes'] for i in removed),
                    'observed_removed_bytes': sum(i['observed_removed_bytes'] or 0 for i in removed)}
        finally:
            db.rollback()


def inspect_logs(database, attempt_id):
    """Explicit bounded reads, never served as a different version of a sealed log."""
    with closing(_connect(_database(database))) as db:
        db.execute('BEGIN')
        refs = _references(db)
        intents, removed = audit(db, refs)
        row = db.execute('SELECT capture FROM managed_processes WHERE attempt_id=?', (attempt_id,)).fetchone()
        if not row:
            if db.execute('SELECT 1 FROM managed_attempts WHERE id=?', (attempt_id,)).fetchone():
                return []
            raise LookupError('Intento desconocido.')
        if not row['capture']:
            return []
        result = []
        for stream, artifact in json.loads(row['capture'])['artifacts'].items():
            source = artifact['path']
            state, diagnostic = 'retained', None
            if source in removed:
                state, diagnostic = 'purged', 'Original retirado por autorización explícita.'
            elif source in intents:
                state, diagnostic = 'pending', 'Intención de purga pendiente de conciliación.'
            else:
                try:
                    from harness_local.storage.backup import RESTORED_USER_VERSION
                    if db.execute('PRAGMA user_version').fetchone()[0] == RESTORED_USER_VERSION:
                        from harness_local.storage.backup import verify_bundle
                        bundle = Path(database).parent
                        manifest = verify_bundle(bundle)
                        source = next(i['path'] for i in manifest['files'] if i['source'] == source)
                        raw = _read(bundle / source)
                    else:
                        raw = _read(source)
                    _check_bytes(raw, refs[artifact['path']])
                except (FileNotFoundError, StopIteration):
                    state, diagnostic = 'missing', 'Archivo perdido; no hay purga autorizada.'
                except (OSError, ValueError) as exc:
                    state, diagnostic = 'unverified', str(exc)
            result.append({'stream': stream, 'source': artifact['path'], 'sha256': artifact['sha256'],
                           'size_bytes': artifact['size'], 'state': state, 'diagnostic': diagnostic,
                           'authorization': removed.get(artifact['path']) or intents.get(artifact['path'])})
        return result

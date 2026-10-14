"""Git inicial H4.2: sin shell, hooks, configuración global ni sobrescritura de archivos.

La carpeta es una capacidad registrada por el servidor. La exclusión SQLite se
complementa con una marca de propiedad en .git, archivos nuevos exclusivos y
comprobaciones de bytes/índice/HEAD. Escritores externos siguen siendo cooperativos.
"""
from hashlib import sha256
import json
import os
from pathlib import Path
import stat
import tempfile

from harness_local.core.engine.phases import digest

MARKER = 'harness-bootstrap.json'


def target_identity(context):
    root = context.root
    if root.is_symlink() or root.resolve(strict=True) != root or not root.is_dir():
        raise ValueError('Bootstrap target changed or contains a symlink')
    info = root.stat()
    return {'device': info.st_dev, 'inode': info.st_ino}


def inspect_target(context, git):
    identity = target_identity(context)
    entries = sorted(p.name for p in context.root.iterdir())
    # Incluso una carpeta vacía dentro de otro checkout requiere importación.
    nested = git.code('rev-parse', '--is-inside-work-tree') == 0
    return {'identity': identity, 'entries': entries[:100], 'entries_truncated': len(entries) > 100,
            'import_required': bool(entries) or nested,
            'diagnostic': 'La carpeta contiene datos o pertenece a un repositorio: usa el flujo de importación.'
                          if entries or nested else None}


class DraftConflict(ValueError):
    """El borrador en disco ya no tiene el hash esperado: nada se sobrescribe."""


def inspect_drafts(context, git, *, texts=False):
    """H6.5: lectura del destino de una definición v2; solo admite borradores de las rutas permitidas.

    Cualquier otro archivo, carpeta o enlace es ajeno y bloquea la aceptación (flujo de importación).
    Un `.git` propio o un repositorio que contenga la carpeta exigen importación."""
    from harness_local.core.engine.definition import allowed_draft, definition_layout, draft_directories
    from harness_local.core.engine.documents import MAX_DOCUMENT_BYTES
    target = definition_layout(context)
    identity = target_identity(context)
    nested = git.code('rev-parse', '--is-inside-work-tree') == 0
    folders = draft_directories(target)
    drafts, contents, foreign, invalid = {}, {}, [], []

    def visit(folder, prefix):
        for item in sorted(folder.iterdir(), key=lambda entry: entry.name):
            path = prefix + item.name
            mode = item.lstat().st_mode
            if stat.S_ISDIR(mode) and path in folders:
                visit(item, path + '/')
            elif stat.S_ISREG(mode) and allowed_draft(target, path):
                data = item.read_bytes()
                try:
                    # Modo Git 100644: un borrador ejecutable no se puede sellar tal cual.
                    if len(data) > MAX_DOCUMENT_BYTES or b'\0' in data or stat.S_IMODE(mode) & 0o111:
                        raise ValueError(path)
                    text = data.decode('utf-8')
                except (ValueError, UnicodeError):
                    invalid.append(path)
                    continue
                drafts[path] = sha256(data).hexdigest()
                contents[path] = text
            else:
                foreign.append(path + ('/' if stat.S_ISDIR(mode) else ''))

    visit(context.root, '')
    result = {'identity': identity, 'drafts': drafts, 'foreign': foreign[:100],
              'foreign_truncated': len(foreign) > 100, 'invalid': invalid,
              'import_required': nested or (context.root / '.git').exists() or (context.root / '.git').is_symlink()}
    return {**result, 'texts': contents} if texts else result


def _current(path):
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise DraftConflict('The draft must be a regular file')
    return sha256(path.read_bytes()).hexdigest() if path.exists() else None


def write_draft(writer, context, path, content, base_sha256):
    """Escribe (o borra con `content=None`) un borrador si su hash sigue siendo `base_sha256`.

    Exclusión cooperativa como D036: la comprobación se repite justo antes de reemplazar, sin atomicidad
    frente a un editor externo. Devuelve los hashes anterior y nuevo; el mismo contenido no se reescribe."""
    from harness_local.core.engine.definition import allowed_draft, definition_layout, draft_directories
    target = definition_layout(context)
    if not allowed_draft(target, path):
        raise ValueError(f'{path} is not an allowed definition draft')
    if inspect_drafts(context, writer._git(context.root))['import_required']:
        raise ValueError('The target belongs to a Git repository or contains .git: use the import flow')
    folders = draft_directories(target)
    parts = path.split('/')
    for n in range(1, len(parts)):
        folder = context.root.joinpath(*parts[:n])
        if '/'.join(parts[:n]) not in folders or folder.is_symlink() or (folder.exists() and not folder.is_dir()):
            raise ValueError(f'{path} is not inside an allowed draft folder')
    item = context.path(path)
    current = _current(item)
    after = None if content is None else sha256(content.encode('utf-8')).hexdigest()
    if current == after:
        return {'before': current, 'after': after, 'written': False}
    if current != base_sha256:
        raise DraftConflict(f'{path} changed since it was read (expected {base_sha256}, found {current})')
    if content is None:
        item.unlink()
    else:
        item.parent.mkdir(parents=True, exist_ok=True)
        _replace_file(item, content.encode('utf-8'), 'draft', lambda: _current(item) == base_sha256)
    return {'before': current, 'after': after, 'written': True}


def _temporary(path, token):
    return path.with_name(f'.{path.name}.{token}.harness-tmp')


def _replace_file(path, content, token, unchanged):
    """Archivo temporal propio en la misma carpeta y `os.replace`; nunca deja un archivo a medias."""
    temporary = _temporary(path, token)
    if temporary.exists() or temporary.is_symlink():
        temporary.unlink()
    _new_file(temporary, content)
    try:
        if not unchanged():
            raise DraftConflict(f'{path.name} changed while it was being replaced; nothing was overwritten')
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _new_file(path, content):
    with path.open('xb') as stream:
        os.fchmod(stream.fileno(), 0o644)
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _commit(intent):
    return (f"tree {intent['tree']}\n"
            f"author {intent['author_name']} <{intent['author_email']}> {intent['committed_at']} +0000\n"
            f"committer {intent['author_name']} <{intent['author_email']}> {intent['committed_at']} +0000\n"
            f"\n{intent['message']}\n").encode('utf-8')


def _tree(git, documents):
    # Índice temporal separado: no añade staging ni ejecuta filtros del worktree.
    with tempfile.TemporaryDirectory(prefix='harness-bootstrap-index-') as area:
        env = {'GIT_INDEX_FILE': str(Path(area) / 'index')}
        git.run('read-tree', '--empty', env=env)
        for doc in documents:
            blob = git.text('hash-object', '-w', '--stdin', input=doc['content'].encode('utf-8'))
            git.run('update-index', '--add', '--cacheinfo', '100644', blob, doc['path'], env=env)
        return git.text('write-tree', env=env)


def seal(writer, shown, operation_id, committed_at):
    with tempfile.TemporaryDirectory(prefix='harness-bootstrap-seal-') as area:
        git = writer._git(Path(area))
        git.run('init', '-q', '--template=', '--object-format=sha1', '-b', 'main')
        intent = {'operation_id': operation_id, 'preview_sha256': shown['preview_sha256'],
                  'tree': _tree(git, shown['documents']), 'author_name': writer.identity.name,
                  'author_email': writer.identity.email, 'committed_at': committed_at,
                  'message': 'Initialize project from confirmed bootstrap'}
        intent['commit'] = git.text('hash-object', '-t', 'commit', '--stdin', input=_commit(intent))
        return intent


def _directories(documents):
    return {str(parent) for d in documents for parent in Path(d['path']).parents if str(parent) != '.'}


def validate_partial(context, shown, intent):
    if target_identity(context) != shown['target']['identity']:
        raise ValueError('Bootstrap target was replaced since preview')
    documents = {d['path']: d for d in shown['documents']}
    directories = _directories(shown['documents'])
    # H6.5: el temporal propio de un reemplazo interrumpido se descarta antes de escribir.
    temporaries = {_temporary(context.root / path, intent['operation_id']).relative_to(context.root).as_posix()
                   for path, doc in documents.items() if 'before_sha256' in doc}
    for directory, dirs, names in os.walk(context.root, followlinks=False):
        for name in [*dirs, *names]:
            item = Path(directory) / name
            path = item.relative_to(context.root).as_posix()
            mode = item.lstat().st_mode
            if path == '.git':
                if not stat.S_ISDIR(mode):
                    raise ValueError('Bootstrap Git directory must be owned, regular and not linked')
                marker = item / MARKER
                if marker.is_symlink() or not marker.is_file() or marker.read_bytes() != marker_bytes(intent):
                    raise ValueError('Unowned Git directory; import or recover manually without overwriting')
                dirs.remove(name)
                continue
            if stat.S_ISDIR(mode) and path in directories:
                continue
            if path in temporaries and stat.S_ISREG(mode):
                continue
            if path not in documents or not stat.S_ISREG(mode):
                raise ValueError(f'Unexpected bootstrap path: {path}; preserved without overwriting')
            doc = documents[path]
            if 'before_sha256' in doc:
                # H6.5: el borrador revisado o los bytes sellados; sin bit de ejecución (modo Git 100644).
                if (stat.S_IMODE(mode) & 0o111 or sha256(item.read_bytes()).hexdigest()
                        not in (doc['sha256'], doc['before_sha256'])):
                    raise ValueError(f'Bootstrap draft changed: {path}; preserved without overwriting')
                continue
            if (item.stat().st_size != len(doc['content'].encode('utf-8'))
                    or sha256(item.read_bytes()).hexdigest() != doc['sha256']
                    or stat.S_IMODE(mode) != 0o644):
                raise ValueError(f'Bootstrap content changed: {path}; preserved without overwriting')


def marker_bytes(intent):
    return (json.dumps({'format': 'bootstrap-1', 'intent_sha256': digest(intent),
                        'operation_id': intent['operation_id']}, sort_keys=True) + '\n').encode()


def execute(writer, context, shown, intent):
    validate_partial(context, shown, intent)
    gitdir = context.root / '.git'
    drafts = any('before_sha256' in doc for doc in shown['documents'])
    if not gitdir.exists():
        # Empezar exige el mismo directorio vacío (o solo los borradores revisados, H6.5), también al reclamar.
        if not drafts and any(context.root.iterdir()):
            raise ValueError('Target is no longer empty; import required')
        if writer._git(context.root).code('rev-parse', '--is-inside-work-tree') == 0:
            raise ValueError('Target now belongs to another Git checkout; import required')
        gitdir.mkdir()  # exclusivo: jamás reemplaza .git ajeno
        _new_file(gitdir / MARKER, marker_bytes(intent))
    git = writer._git(context.root)
    for name in ('HEAD', 'config', 'index'):
        if (gitdir / name).is_symlink():
            raise ValueError('Bootstrap Git metadata contains a symlink; recover manually')
    if not (gitdir / 'HEAD').exists():
        # Caída entre marca y init: solo la marca propia permite completar el init.
        if sorted(p.name for p in gitdir.iterdir()) != [MARKER]:
            raise ValueError('Incomplete Git initialization has foreign metadata; recover manually')
        git.run('init', '-q', '--template=', '--object-format=sha1', '-b', 'main')
    if git.text('rev-parse', '--show-toplevel') != str(context.root):
        raise ValueError('Bootstrap repository root changed')
    if git.text('symbolic-ref', 'HEAD') != 'refs/heads/main':
        raise ValueError('Bootstrap branch changed')
    head = git.run('rev-parse', '--verify', 'HEAD', ok=(0, 128)).decode().strip()
    if head and head != intent['commit']:
        raise ValueError('Bootstrap HEAD changed; preserved without overwriting')
    refs = git.text('for-each-ref', '--format=%(refname) %(objectname)')
    if refs not in ('', 'refs/heads/main ' + intent['commit']):
        raise ValueError('Bootstrap references changed; recover manually')
    empty = git.text('hash-object', '-t', 'tree', '--stdin', input=b'')
    if (gitdir / 'index').exists():
        index = writer._index_tree(git)
        if index not in (empty, intent['tree']):
            raise ValueError('Bootstrap index changed; preserved without overwriting')
    for doc in shown['documents']:
        validate_partial(context, shown, intent)
        path = context.path(doc['path'])
        path.parent.mkdir(parents=True, exist_ok=True)
        if 'before_sha256' in doc:
            temporary = _temporary(path, intent['operation_id'])
            if temporary.is_file() and not temporary.is_symlink():
                temporary.unlink()
        if not path.exists():
            _new_file(path, doc['content'].encode('utf-8'))
        elif 'before_sha256' in doc and sha256(path.read_bytes()).hexdigest() != doc['sha256']:
            # Borrador revisado → bytes sellados (bloques regenerados); otro contenido ya se rechazó arriba.
            before = doc['before_sha256']
            _replace_file(path, doc['content'].encode('utf-8'), intent['operation_id'],
                          lambda: sha256(path.read_bytes()).hexdigest() == before)
    validate_partial(context, shown, intent)
    if _tree(git, shown['documents']) != intent['tree']:
        raise ValueError('Bootstrap tree differs from sealed intent')
    raw = _commit(intent)
    if git.text('hash-object', '-t', 'commit', '-w', '--stdin', input=raw) != intent['commit']:
        raise ValueError('Bootstrap commit differs from sealed intent')
    validate_partial(context, shown, intent)
    if writer._index_tree(git) not in (empty, intent['tree']):
        raise ValueError('Bootstrap index changed before commit; preserved without overwriting')
    git.run('update-ref', '-m', 'harness: bootstrap ' + intent['operation_id'], 'refs/heads/main',
            intent['commit'], head or '0' * 40)
    if git.text('cat-file', 'commit', intent['commit']) != raw.decode().strip():
        raise ValueError('Bootstrap commit content differs from intent')
    if writer._index_tree(git) not in (empty, intent['tree']):
        raise ValueError('Bootstrap index changed after commit; preserved without overwriting')
    if git.text('rev-parse', 'HEAD') != intent['commit']:
        raise ValueError('Bootstrap HEAD changed after commit; recover manually')
    git.run('read-tree', intent['tree'])
    evidence = writer.capture(context)
    if evidence.changed_paths or evidence.base_revision != intent['commit']:
        raise ValueError('Bootstrap checkout differs from sealed commit; recover manually')
    validate_partial(context, shown, intent)
    return {'commit': intent['commit'], 'tree': intent['tree'], 'documents': {
        d['path']: d['sha256'] for d in shown['documents']}}

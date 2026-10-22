"""Local-object Git boundary shared by onboarding and project preparation."""
from hashlib import sha256

from harness_local.adapters.git import Git
from harness_local.adapters.local_git import object_size
from harness_local.core.tree import ImportInventoryError

READABLE_MODES = ('100644', '100755')

def _tree(git: Git, revision: str = 'HEAD') -> list[tuple[str, str, str, int | None, str]]:
    """(modo, tipo, objeto, tamaño, ruta) de un árbol, sin citar rutas (`-z`)."""
    rows = []
    for record in git.run('ls-tree', '-r', '-z', '-l', '--full-tree', revision).split(b'\0'):
        if not record:
            continue
        header, _, raw_path = record.partition(b'\t')
        mode, kind, obj, size = header.decode('ascii').split()
        path = raw_path.decode('utf-8')
        rows.append((mode, kind, obj, object_size(size, kind, obj, path), path))
    return rows


def _blobs(git: Git, objects: list[str]) -> dict[str, bytes]:
    """Contenido exacto de los blobs con `cat-file --batch`, que no aplica filtros ni textconv."""
    if not objects:
        return {}
    output = git.run('cat-file', '--batch', input=('\n'.join(objects) + '\n').encode('ascii'))
    found, offset = {}, 0
    for obj in objects:
        end = output.find(b'\n', offset)
        if end == -1:
            raise ImportInventoryError(f'Git object {obj} has an incomplete batch response.')
        header = output[offset:end].decode('ascii').split()
        if len(header) != 3 or header[0] != obj or header[1] != 'blob':
            raise ImportInventoryError(f'Git object {obj} is missing or could not be read as a local blob '
                                       '(lazy-fetch is disabled).')
        if not header[2].isascii() or not header[2].isdecimal():
            raise ImportInventoryError(f'Git object {obj} has an unavailable blob size.')
        size = int(header[2])
        if output[end + 1 + size:end + 2 + size] != b'\n':
            raise ImportInventoryError(f'Git object {obj} has incomplete blob content.')
        found[obj] = output[end + 1:end + 1 + size]
        offset = end + 1 + size + 1
    return found


def check_filters(git: Git):
    """Antes de status/add/hash-object: config lee includes, pero nunca ejecuta los filtros."""
    if git.run('config', '--includes', '--get-regexp', r'^filter\..*\.(clean|process)$', ok=(0, 1)).strip():
        raise ImportInventoryError('Import requires no local clean/process Git filters; project code cannot be executed')


def check_submodules(git: Git):
    """Rechaza gitlinks de HEAD o índice antes de status/add, sin consultar el repositorio hijo."""
    for source, args in (
        ('HEAD', ('ls-tree', '-r', '-z', '--full-tree', 'HEAD')),
        ('index', ('ls-files', '--stage', '-z')),
    ):
        for record in git.run(*args).split(b'\0'):
            header, _, path = record.partition(b'\t')
            if header.startswith(b'160000 '):
                raise ImportInventoryError(
                    f'Import does not support submodule/gitlink {path.decode("utf-8", "replace")!r} '
                    f'in {source}; checkout inspection cannot execute submodule code.')


def check_tree(git: Git, tree: str, expected: list[dict], documents: list[dict]):
    """Guardias A/B antes de confirmar o escribir, incluidos archivo, binarios y recuperación parcial."""
    destinations = b''.join(doc['path'].encode() + b'\0' for doc in documents
                            if doc['before_sha256'] is None and doc['after_sha256'] is not None)
    if destinations and git.run('check-ignore', '-z', '--stdin', input=destinations, ok=(0, 1)).strip(b'\0'):
        raise ValueError('Import document destinations are ignored by Git; review the project ignore rules')
    entries = {path: (mode, obj) for mode, _, obj, _, path in _tree(git, tree)}
    if any(item['path'] not in entries or entries[item['path']][0] not in READABLE_MODES for item in expected):
        raise ValueError('The sealed import tree lacks a confirmed regular document')
    blobs = _blobs(git, sorted({entries[item['path']][1] for item in expected}))
    if any(sha256(blobs[entries[item['path']][1]]).hexdigest() != item['sha256'] for item in expected):
        raise ValueError('Git attributes would transform the confirmed document bytes')
    if any(doc['after_sha256'] is None and doc['path'] in entries for doc in documents):
        raise ValueError('The sealed import tree retains a deleted document')

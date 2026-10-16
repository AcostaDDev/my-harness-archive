"""P008-T009: lectura de solo lectura del checkout para el inventario del Flujo A.

Solo Git de lectura con el entorno controlado de `adapters/git.py` (sin hooks, fsmonitor ni configuración global):
`rev-parse`, `status` sin locks opcionales, `ls-tree` y `cat-file --batch` sin filtros. El contenido sale del árbol
de HEAD de un checkout limpio, así que lo ignorado (entornos, secretos locales) nunca se lee y los enlaces
simbólicos son entradas del árbol que no se siguen. De `.harness/runs`, que sigue la migración D027, solo se
observan los nombres por lstat. No escribe en el checkout ni en `.git` y no ejecuta código del proyecto.
"""

import os
from pathlib import Path, PurePosixPath
import stat

from harness_local.adapters.git import Git, GitError
from harness_local.core.engine.context import ProjectContext
from harness_local.core.migration import MARKER_PATH
from harness_local.core.project_import import (
    LEGACY_HARNESS, LEGACY_RUNS, MAX_ENTRIES, MAX_ENTRY_BYTES, MAX_TOTAL_BYTES, CheckoutSnapshot,
    ImportInventoryError, TreeEntry, build_inventory, in_scope,
)

READABLE_MODES = ('100644', '100755')


def _tree(git: Git) -> list[tuple[str, str, str, int | None, str]]:
    """(modo, tipo, objeto, tamaño, ruta) de todo HEAD, sin citar rutas (`-z`)."""
    rows = []
    for record in git.run('ls-tree', '-r', '-z', '-l', '--full-tree', 'HEAD').split(b'\0'):
        if not record:
            continue
        header, _, raw_path = record.partition(b'\t')
        mode, kind, obj, size = header.decode('ascii').split()
        rows.append((mode, kind, obj, None if size == '-' else int(size), raw_path.decode('utf-8')))
    return rows


def _blobs(git: Git, objects: list[str]) -> dict[str, bytes]:
    """Contenido exacto de los blobs con `cat-file --batch`, que no aplica filtros ni textconv."""
    if not objects:
        return {}
    output = git.run('cat-file', '--batch', input=('\n'.join(objects) + '\n').encode('ascii'))
    found, offset = {}, 0
    for obj in objects:
        end = output.index(b'\n', offset)
        header = output[offset:end].decode('ascii').split()
        if len(header) != 3 or header[0] != obj or header[1] != 'blob':
            raise ImportInventoryError(f'Git object {obj} could not be read as a blob.')
        size = int(header[2])
        found[obj] = output[end + 1:end + 1 + size]
        offset = end + 1 + size + 1
    return found


def legacy_runs(root: Path) -> dict:
    """Runs de un harness anterior por lstat: tipo y número de directorios, sin leer su contenido."""
    harness, runs = root / LEGACY_HARNESS, root / LEGACY_RUNS
    observed = {'present': False, 'kind': None, 'directories': 0, 'managed_marker': False}
    if os.path.islink(harness):
        return {**observed, 'present': True, 'kind': 'symlink'}
    observed['managed_marker'] = os.path.lexists(root / MARKER_PATH)
    if not os.path.lexists(runs):
        return observed
    info = os.lstat(runs)
    if not stat.S_ISDIR(info.st_mode):
        return {**observed, 'present': True, 'kind': 'symlink' if stat.S_ISLNK(info.st_mode) else 'other'}
    with os.scandir(runs) as entries:
        count = sum(entry.is_dir(follow_symlinks=False) for entry in entries)
    return {**observed, 'present': True, 'kind': 'dir', 'directories': count}


def read_checkout(root: Path, docs: str = 'docs', *, executable: str = 'git',
                  marker_sha256: str | None = None) -> CheckoutSnapshot:
    root = Path(root)
    git = Git(root, executable=executable)
    try:
        top = Path(git.text('rev-parse', '--show-toplevel')).resolve()
    except GitError as exc:
        raise ImportInventoryError(f'Not a Git checkout: {exc}') from exc
    if top != root.resolve():
        raise ImportInventoryError('The project root must be the top level of its Git checkout.')
    try:
        head = git.text('rev-parse', '--verify', '--quiet', 'HEAD^{commit}')
        tree = git.text('rev-parse', '--verify', f'{head}^{{tree}}')
    except GitError as exc:
        raise ImportInventoryError('The checkout has no commits; import needs a non-empty repository.') from exc
    dirty = [item for item in git.run('status', '--porcelain=v1', '-z', '--untracked-files=all',
                                      '--ignore-submodules=none').split(b'\0') if item]
    if marker_sha256 is not None:
        from hashlib import sha256
        marker = root / MARKER_PATH
        if (not marker.is_symlink() and marker.is_file()
                and sha256(marker.read_bytes()).hexdigest() == marker_sha256):
            dirty = [item for item in dirty if item != b'?? ' + MARKER_PATH.encode()]
    if dirty:
        sample = ', '.join(item[3:].decode('utf-8', 'replace') for item in dirty[:5])
        raise ImportInventoryError(f'The checkout has uncommitted changes ({sample}); commit or discard them first.')
    rows = _tree(git)
    if any(row[4] == MARKER_PATH for row in rows):
        raise ImportInventoryError('The managed marker must remain untracked local state (D099).')
    if not rows:
        raise ImportInventoryError('HEAD has no files; an empty project uses the creation flow.')
    scoped = [row for row in rows if in_scope(row[4], docs)]
    if len(scoped) > MAX_ENTRIES:
        raise ImportInventoryError(f'More than {MAX_ENTRIES} documentation entries; inventory refused.')
    readable = [row for row in scoped if row[0] in READABLE_MODES and row[3] is not None
                and row[3] <= MAX_ENTRY_BYTES]
    if sum(row[3] for row in readable) > MAX_TOTAL_BYTES:
        raise ImportInventoryError(f'Documentation exceeds {MAX_TOTAL_BYTES} bytes; inventory refused.')
    contents = _blobs(git, sorted({row[2] for row in readable}))
    entries = []
    for mode, _, obj, size, path in scoped:
        if '..' in PurePosixPath(path).parts:
            raise ImportInventoryError(f'Unsafe path in HEAD: {path}')
        if mode == '120000':
            diagnostic = 'Symbolic link: not followed or read.'
        elif mode == '160000':
            diagnostic = 'Submodule: outside the documentation contract.'
        elif mode not in READABLE_MODES:
            diagnostic = f'Unsupported Git mode {mode}.'
        elif size is None or size > MAX_ENTRY_BYTES:
            diagnostic = f'Entry over {MAX_ENTRY_BYTES} bytes: not read.'
        else:
            entries.append(TreeEntry(path, mode, size, contents[obj]))
            continue
        entries.append(TreeEntry(path, mode, size, None, diagnostic))
    return CheckoutSnapshot(str(root.resolve()), head, tree, tuple(entries), legacy_runs(root))


def read_inventory(context: ProjectContext, *, executable: str = 'git') -> dict:
    """Inventario de un proyecto registrado; la carpeta de documentación es la de STATE en su contexto."""
    docs = str(PurePosixPath(context.state_file).parent)
    if docs == '.':
        raise ImportInventoryError('Import needs STATE and NEXT_STEPS inside a documentation directory.')
    return build_inventory(read_checkout(context.root, docs, executable=executable), docs)

"""Flujo B: instantánea de HEAD sin ejecutar código, filtros ni consultar el worktree.

Solo rev-parse, ls-tree y cat-file sin filtros. No usa status: este puede lanzar filtros clean del proyecto.
El inventario describe el commit indicado, incluso si el disco tiene cambios; la incorporación confirmada deberá
comprobar de nuevo su base. No lee archivos locales ignorados, enlaces, submódulos ni dependencias instaladas.
"""

from pathlib import Path

from harness_local.adapters.git import GitError
from harness_local.adapters.local_git import LocalGit as _InventoryGit, object_size
from harness_local.adapters.import_git import _blobs
from harness_local.core.tree import ImportInventoryError, TreeEntry
from harness_local.core.project_onboarding import (
    MAX_ENTRIES, MAX_ENTRY_BYTES, MAX_TOTAL_BYTES, OnboardingInventoryError, build_inventory, in_scope,
)


def read_inventory(root: Path, *, executable: str = 'git') -> dict:
    root = Path(root).resolve()
    git = _InventoryGit(root, executable=executable)
    try:
        if Path(git.text('rev-parse', '--show-toplevel')).resolve() != root:
            raise OnboardingInventoryError('The project root must be the top level of its Git checkout.')
        head = git.text('rev-parse', '--verify', '--quiet', 'HEAD^{commit}')
        tree = git.text('rev-parse', '--verify', f'{head}^{{tree}}')
        # Usar el id sellado, no HEAD de nuevo: un movimiento concurrente de la referencia no mezcla commits.
        output = git.run('ls-tree', '-r', '-z', '-l', '--full-tree', tree)
        rows = []
        records = [record for record in output.split(b'\0') if record]
        if not records:
            raise OnboardingInventoryError('HEAD has no files; an empty project uses the creation flow.')
        if len(records) > MAX_ENTRIES:
            raise OnboardingInventoryError(f'More than {MAX_ENTRIES} tree entries; inventory refused.')
        for record in records:
            header, raw_path = record.split(b'\t', 1)
            mode, kind, obj, size = header.decode('ascii').split()
            path = raw_path.decode('utf-8')
            if in_scope(path):
                rows.append((mode, obj, object_size(size, kind, obj, path), path))
        readable = [row for row in rows if row[0] in ('100644', '100755')
                    and row[2] is not None and row[2] <= MAX_ENTRY_BYTES]
        if sum(row[2] for row in readable) > MAX_TOTAL_BYTES:
            raise OnboardingInventoryError(f'Sources exceed {MAX_TOTAL_BYTES} bytes; inventory refused.')
        blobs = _blobs(git, sorted({row[1] for row in readable}))
        entries = []
        for mode, obj, size, path in rows:
            diagnostic = None
            if mode not in ('100644', '100755'):
                diagnostic = 'Symbolic link or submodule: not followed or read.'
            elif size is None or size > MAX_ENTRY_BYTES:
                diagnostic = f'Entry over {MAX_ENTRY_BYTES} bytes: not read.'
            entries.append(TreeEntry(path, mode, size, None if diagnostic else blobs[obj], diagnostic))
        return build_inventory(tuple(entries), head=head, tree=tree)
    except (GitError, ImportInventoryError, UnicodeError) as exc:
        raise OnboardingInventoryError('Cannot read a non-empty Git HEAD from complete local objects '
                                       f'(lazy-fetch is disabled): {exc}') from exc

"""Git with local objects: a missing promised object never authorizes a transport."""

from harness_local.adapters.git import Git, GitError


class LocalGit(Git):
    def run(self, *args, **kwargs):
        # Old Git must fail: an unknown environment variable would be silently ignored.
        return super().run('--no-lazy-fetch', *args, **kwargs)

    def code(self, *args, **kwargs):
        # A boolean question cannot confuse Git without support with a missing future object.
        # run checks the support with the same executable and fails without fallback before the first
        # question of this instance; a failure is not remembered and is checked again.
        if not getattr(self, '_lazy_fetch_checked', False):
            self.run('--version')
            self._lazy_fetch_checked = True
        return super().code('--no-lazy-fetch', *args, **kwargs)

    def require_tree(self, revision: str):
        """Also checks objects outside the documentary scope before capturing or writing."""
        try:
            tree = self.text('rev-parse', '--verify', f'{revision}^{{tree}}')
            entries = self.run('ls-tree', '-r', '-t', '-z', '--full-tree', tree)
        except GitError as exc:
            raise GitError(f'Cannot inspect required local tree {revision}: missing or unavailable '
                           f'(lazy-fetch is disabled): {exc}') from exc
        objects = {tree}
        for entry in entries.split(b'\0'):
            if entry:
                header = entry.split(b'\t', 1)[0].decode('ascii').split()
                if header[1] != 'commit':  # Gitlinks are rejected separately, without reading children.
                    objects.add(header[2])
        objects = sorted(objects)
        rows = self.run('cat-file', '--batch-check', input=('\n'.join(objects) + '\n').encode()).splitlines()
        for index, obj in enumerate(objects):
            row = rows[index].decode('ascii').split() if index < len(rows) else []
            if (len(row) != 3 or row[0] != obj or row[1] not in ('blob', 'tree')
                    or not row[2].isascii() or not row[2].isdecimal()):
                raise GitError(f'Git object {obj} required by tree {tree} is missing or unavailable; '
                               'import requires complete local objects (lazy-fetch is disabled).')


def object_size(size: str, kind: str, obj: str, path: str) -> int | None:
    """ls-tree -l returns BAD for missing blobs and '-' for entries without a size (submodules)."""
    if size == '-' and kind != 'blob':
        return None
    if not size.isascii() or not size.isdecimal():
        raise GitError(f'Git object {obj} at {path!r} is missing or has an unavailable size; '
                       'reading requires complete local objects.')
    return int(size)

"""Lecturas Git de objetos locales: un objeto prometido ausente nunca autoriza un transporte."""

from harness_local.adapters.git import Git, GitError


class LocalGit(Git):
    def run(self, *args, **kwargs):
        # Git antiguo debe fallar: una variable de entorno desconocida se ignoraría silenciosamente.
        return super().run('--no-lazy-fetch', *args, **kwargs)

    def code(self, *args, **kwargs):
        return super().code('--no-lazy-fetch', *args, **kwargs)


def object_size(size: str, kind: str, obj: str, path: str) -> int | None:
    """ls-tree -l devuelve BAD para blobs ausentes y '-' para entradas sin tamaño (submódulos)."""
    if size == '-' and kind != 'blob':
        return None
    if not size.isascii() or not size.isdecimal():
        raise GitError(f'Git object {obj} at {path!r} is missing or has an unavailable size; '
                       'reading requires complete local objects.')
    return int(size)

"""Lectura acotada de bytes exactos del índice; sin seguir enlaces ni ejecutar."""
import errno
import hashlib
import os
from pathlib import PurePosixPath
import stat

from harness_local.core.legacy import LegacyArtifact


MAX_VERIFY_BYTES = 64 * 1024 * 1024


def read_content(root: str, artifact: LegacyArtifact, offset: int, limit: int) -> dict:
    result = {"path": artifact.path, "indexed_sha256": artifact.sha256,
              "observed_sha256": None, "offset": offset, "next_offset": None,
              "text": None, "diagnostic": None}

    def failed(status, message):
        return {**result, "status": status, "diagnostic": message}

    path = PurePosixPath(artifact.path)
    if path.is_absolute() or any(part in ("..", ".", "") for part in artifact.path.split("/")):
        return failed("unsafe", "Ruta relativa no segura.")
    if artifact.sha256 is None:
        return failed("unindexed", artifact.diagnostic or "No hay bytes indexados para verificar.")
    descriptors = []
    try:
        # Abrir cada componente con dir_fd/O_NOFOLLOW elimina el TOCTOU de is_symlink.
        descriptor = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
        descriptors.append(descriptor)
        for part in PurePosixPath(root).parts[1:]:
            descriptor = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            descriptors.append(descriptor)
        for part in path.parts[:-1]:
            descriptor = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            descriptors.append(descriptor)
        descriptor = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=descriptor)
        descriptors.append(descriptor)
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            return failed("unsafe", "La evidencia no es un archivo regular.")
        if before.st_size > MAX_VERIFY_BYTES:
            return failed("too_large", "Verificación limitada a 64 MiB; contenido no servido.")
        digest = hashlib.sha256()
        position = 0
        page = bytearray()
        while chunk := os.read(descriptor, 65536):
            digest.update(chunk)
            # Cuatro bytes extra permiten acabar una secuencia UTF-8 en el límite.
            start, end = max(offset, position), min(offset + limit + 4, position + len(chunk))
            if start < end:
                page.extend(chunk[start - position:end - position])
            position += len(chunk)
            if position > MAX_VERIFY_BYTES:
                return failed("too_large", "Archivo creció sobre el límite de verificación.")
        after = os.fstat(descriptor)
        result["observed_sha256"] = digest.hexdigest()
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            return failed("changed", "El archivo cambió durante la lectura. Reimportar explícitamente.")
        if digest.hexdigest() != artifact.sha256 or position != artifact.size_bytes:
            return failed("changed", "Hash/tamaño distinto del índice. Reimportar explícitamente.")
        # offset válido es cero o next_offset anterior. Se rechaza un corte UTF-8 arbitrario.
        end = min(limit, len(page))
        while end < len(page) and page[end] & 0xC0 == 0x80:
            end += 1
        try:
            decoded = bytes(page[:end]).decode("utf-8")
        except UnicodeDecodeError:
            return failed("invalid_utf8", "Bytes no UTF-8 o cursor en medio de una secuencia; no se sustituyen bytes.")
        return {**result, "status": "verified", "text": decoded,
                "next_offset": offset + end if offset + end < position else None}
    except FileNotFoundError:
        return failed("missing", "Archivo o raíz ausente en el origen.")
    except OSError as error:
        return failed("unsafe" if error.errno in (errno.ENOTDIR, errno.ELOOP) else "unreadable", str(error))
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)

"""Guardia local compartida (§10): Host de loopback, Origin local y cabecera propia en mutaciones.

La cabecera `X-Harness-Local: 1` no es una credencial: una página ajena no puede
añadirla sin preflight CORS y el servicio no habilita CORS. La sesión local frente
a otros usuarios del sistema operativo sigue pendiente (hito 5).
"""

from typing import Annotated
from urllib.parse import urlsplit

from fastapi import Header, HTTPException, Request

LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def problem(status: int, code: str, diagnostic: str) -> HTTPException:
    return HTTPException(status, {"code": code, "diagnostic": diagnostic})


def _hostname(value: str | None) -> str | None:
    try:
        return urlsplit(f"//{value}").hostname if value else None
    except ValueError:
        return None


def local_request(request: Request, x_harness_local: Annotated[str | None, Header(
        description="Obligatoria con valor 1 en mutaciones (protección CSRF).")] = None) -> None:
    """Rechaza DNS rebinding (Host), peticiones cruzadas (Origin) y formularios ajenos (cabecera propia)."""
    if _hostname(request.headers.get("host")) not in LOOPBACK_HOSTS:
        raise problem(403, "host_rejected", "El servicio local solo atiende nombres de loopback.")
    if request.method in SAFE_METHODS:
        return
    origin = request.headers.get("origin")
    if origin is not None:
        parsed = urlsplit(origin)
        if parsed.scheme not in {"http", "https"} or _hostname(parsed.netloc) not in LOOPBACK_HOSTS:
            raise problem(403, "origin_rejected", "Origen no local para una mutación.")
    if x_harness_local != "1":
        raise problem(403, "csrf_header_required", "Las mutaciones exigen la cabecera X-Harness-Local: 1.")

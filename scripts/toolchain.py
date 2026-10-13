"""Toolchain de desarrollo fijada (H0.2): comprobación compartida por los scripts del repositorio."""
import subprocess

EXPECTED = (('node', 'v24.15.0'), ('npm', '11.12.1'), ('uv', 'uv 0.12.19'))


def check_tools():
    for executable, expected in EXPECTED:
        try:
            observed = subprocess.check_output([executable, '--version'], text=True).strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            raise SystemExit(f'{executable}: se requiere {expected}; no disponible ({exc})') from None
        if (observed.split(' (', 1)[0] if executable == 'uv' else observed) != expected:
            raise SystemExit(f'{executable}: se requiere {expected}; observado {observed}')

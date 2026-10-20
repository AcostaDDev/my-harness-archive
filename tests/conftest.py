import atexit
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def _bypass_xcode_git_shim():
    """En macOS, `/usr/bin/git` es un shim de xcrun que duplica el coste de cada llamada a Git.

    Las pruebas lanzan miles de procesos Git: se antepone al PATH de la sesión un prefijo con el
    mismo binario real, su `libexec/git-core` y su `share` (Apple Git resuelve ambos relativos al
    ejecutable). Debe ocurrir al importar este conftest, antes de que los módulos de prueba copien
    `os.environ` en sus entornos de Git.
    """
    if sys.platform != 'darwin' or shutil.which('git') != '/usr/bin/git':
        return
    try:
        real = Path(subprocess.run(['xcrun', '--find', 'git'], capture_output=True, text=True,
                                   check=True).stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        return
    prefix = real.parent.parent
    if not all((prefix / name).is_dir() for name in ('libexec/git-core', 'share')):
        return
    shim = Path(tempfile.mkdtemp(prefix='harness-test-git-'))
    atexit.register(shutil.rmtree, shim, ignore_errors=True)
    (shim / 'bin').mkdir()
    (shim / 'bin' / 'git').symlink_to(real)
    for name in ('libexec', 'share'):
        (shim / name).symlink_to(prefix / name)
    os.environ['PATH'] = f"{shim / 'bin'}{os.pathsep}{os.environ.get('PATH', '')}"


_bypass_xcode_git_shim()

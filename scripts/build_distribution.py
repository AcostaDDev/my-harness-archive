"""Construcción local offline: UI desde lock, sdist/wheel y pins de instalación."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

from toolchain import check_tools

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    output = args.out_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    check_tools()
    subprocess.run(['npm', 'ci', '--offline', '--ignore-scripts', '--cache', str(ROOT / '.local/npm-cache')],
                   cwd=ROOT / 'frontend', check=True)
    subprocess.run(['npm', 'run', 'build'], cwd=ROOT / 'frontend', check=True)
    with tempfile.TemporaryDirectory(prefix='harness-package-') as temporary:
        stage = Path(temporary)
        shutil.copy2(ROOT / 'pyproject.toml', stage)
        shutil.copytree(ROOT / 'src', stage / 'src', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        shutil.copytree(ROOT / 'frontend/dist', stage / 'src/harness_local/web')
        subprocess.run(['uv', 'build', '--offline', '--no-python-downloads', '--out-dir', str(output), str(stage)],
                       cwd=ROOT, check=True)
    subprocess.run(['uv', 'export', '--frozen', '--offline', '--no-dev', '--no-emit-project',
                    '--format', 'requirements-txt', '--output-file', str(output / 'requirements.txt')],
                   cwd=ROOT, check=True, stdout=subprocess.DEVNULL)


if __name__ == '__main__':
    main()

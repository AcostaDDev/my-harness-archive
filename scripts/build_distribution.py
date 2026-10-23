"""Offline local build: UI from the lock, sdist/wheel, installation pins and SHA256SUMS."""
import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile

from toolchain import check_tools

ROOT = Path(__file__).resolve().parents[1]
# Files besides `src/` that enter the sdist; the license files also enter the wheel (`license-files`).
PROJECT_FILES = ('pyproject.toml', 'README.md', 'LICENSE', 'NOTICE.md', 'NOTICE-THIRD-PARTY.md')
# Every packaged source has one of these suffixes; anything else under src/ stops the build.
SOURCE_SUFFIXES = {'.py', '.md', '.json', '.lock', '.mako'}


def package_sources():
    """Relative paths under src/ that the package carries, without caches or unexpected files."""
    sources, unexpected = [], []
    for path in sorted((ROOT / 'src').rglob('*')):
        relative = path.relative_to(ROOT / 'src')
        if '__pycache__' in relative.parts or path.suffix == '.pyc' or path.is_dir():
            continue
        if path.is_symlink() or not path.is_file() or path.suffix not in SOURCE_SUFFIXES or path.name.startswith('.'):
            unexpected.append(str(relative))
        else:
            sources.append(relative)
    if unexpected:
        raise SystemExit('Unexpected files under src/ (remove them before building): ' + ', '.join(unexpected))
    return sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    output = args.out_dir.resolve()
    # Old artifacts are never mixed with a new build.
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f'{output} is not empty; choose a new or empty output directory')
    output.mkdir(parents=True, exist_ok=True)
    check_tools()
    sources = package_sources()
    subprocess.run(['npm', 'ci', '--offline', '--ignore-scripts', '--cache', str(ROOT / '.local/npm-cache')],
                   cwd=ROOT / 'frontend', check=True)
    subprocess.run(['npm', 'run', 'build'], cwd=ROOT / 'frontend', check=True)
    with tempfile.TemporaryDirectory(prefix='harness-package-') as temporary:
        stage = Path(temporary)
        for name in PROJECT_FILES:
            shutil.copy2(ROOT / name, stage)
        for relative in sources:
            (stage / 'src' / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / 'src' / relative, stage / 'src' / relative)
        shutil.copytree(ROOT / 'frontend/dist', stage / 'src/harness_local/web')
        subprocess.run(['uv', 'build', '--offline', '--no-python-downloads', '--out-dir', str(output), str(stage)],
                       cwd=ROOT, check=True)
    # Without the header, which would record the absolute output path.
    subprocess.run(['uv', 'export', '--frozen', '--offline', '--no-dev', '--no-emit-project', '--no-header',
                    '--format', 'requirements-txt', '--output-file', str(output / 'requirements.txt')],
                   cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    sums = [f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n'
            for path in sorted(output.iterdir()) if path.is_file() and not path.name.startswith('.')]
    (output / 'SHA256SUMS').write_text(''.join(sums))


if __name__ == '__main__':
    main()

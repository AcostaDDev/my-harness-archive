"""P011-T015 private evidence: bundled frontend packages versus NOTICE-THIRD-PARTY.md.

Builds the UI once more with source maps into a temporary directory (offline, local node_modules), lists every
npm package whose sources reach the browser bundle and checks that each one has a row with the same version in
NOTICE-THIRD-PARTY.md. Also reports non-JS/CSS assets (fonts, images) and scans the real `frontend/dist`
for private patterns. Prints a JSON summary; exits 1 on a missing notice or a private match.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / 'frontend'
# `docs/phase/` and `docs/archive/` are product paths of managed projects, so only personal patterns are searched.
PRIVATE = re.compile(rb'/Users/|/home/[a-z]|reference_project|acosta', re.IGNORECASE)


def bundled_packages(maps: Path) -> set[tuple[str, str]]:
    """(name, version) of the innermost package of every bundled source, nested copies included."""
    found = set()
    for source_map in maps.rglob('*.map'):
        for source in json.loads(source_map.read_text())['sources']:
            match = re.search(r'(node_modules/(?:.*/node_modules/)?((?:@[^/]+/)?[^/]+))/', source)
            if match:
                manifest = FRONTEND / match[1] / 'package.json'
                found.add((match[2], json.loads(manifest.read_text())['version']))
    return found


def main():
    notices = (ROOT / 'NOTICE-THIRD-PARTY.md').read_text()
    # A package may appear with several versions in the lock: rows are (name, version) pairs.
    rows = set(re.findall(r'^\| (\S+) \| (\S+) \| [^|]+ \| [^|]+\|$', notices, re.MULTILINE))
    lock_hash = hashlib.sha256((FRONTEND / 'package-lock.json').read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='harness-sourcemaps-') as temporary:
        subprocess.run([str(FRONTEND / 'node_modules/.bin/vite'), 'build', '--sourcemap', '--emptyOutDir',
                        '--outDir', temporary, '--logLevel', 'error'], cwd=FRONTEND, check=True)
        packages = bundled_packages(Path(temporary))
        other_assets = sorted(p.name for p in Path(temporary).rglob('*')
                              if p.is_file() and p.suffix not in {'.js', '.css', '.map', '.html'})
    missing = sorted(f'{name}@{version}' for name, version in packages - rows)
    private = sorted(str(p.relative_to(FRONTEND)) for p in (FRONTEND / 'dist').rglob('*')
                     if p.is_file() and PRIVATE.search(p.read_bytes()))
    summary = {'lock_sha256_matches_notice': lock_hash in notices, 'notice_rows': len(rows),
               'bundled_packages': len(packages), 'bundled': sorted(f'{n}@{v}' for n, v in packages),
               'missing_notice': missing, 'non_code_assets': other_assets,
               'dist_files': sum(1 for p in (FRONTEND / 'dist').rglob('*') if p.is_file()),
               'dist_private_matches': private}
    print(json.dumps(summary, indent=2))
    return 1 if missing or private or not summary['lock_sha256_matches_notice'] else 0


if __name__ == '__main__':
    sys.exit(main())

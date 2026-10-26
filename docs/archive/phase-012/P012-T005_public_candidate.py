"""P012-T005 private tool: materialize the updated public snapshot by positive list (contract T001 §8, D176).

Every file Git tracks in this checkout (or, without --revision, also untracked files that are not ignored) is
classified: copied to the same path, mapped from `docs/public/` to the candidate root, or excluded with a reason.
An unclassified path stops the export. The candidate gets no `.git`, history, private docs or evidence.

Writes the tree to --out (which must not exist), a private TSV manifest source → candidate and a publishable
`sha256  path` manifest. Then checks symlinks, hidden files and private patterns in the candidate.

UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python docs/phase/P012-T005_public_candidate.py \
  [--revision HEAD] --out .local/public-candidate
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = 'docs/public/'
ROOT_FILES = {'.gitattributes', '.gitignore', '.python-version', 'alembic.ini', 'pyproject.toml', 'uv.lock',
              'LICENSE', 'NOTICE.md', 'NOTICE-THIRD-PARTY.md', 'README.md', 'README.es.md', 'CONTRIBUTING.md',
              'SECURITY.md', 'CHANGELOG.md'}
COPIED_PREFIXES = ('src/', 'frontend/', 'tests/', 'scripts/', '.github/workflows/')
EXAMPLES = {'examples/local_config.example.toml', 'examples/local_config.minimal.example.toml',
            'examples/django-recipe.example.toml', 'examples/typescript-web-recipe.example.toml',
            'examples/managed_demo.py'}
EXCLUDED = (
    ('tests/fixtures/cli_help/', 'real CLI help originals stay private (D160)'),
    ('examples/first_use/', 'historical script, not current instructions'),
    ('examples/provider_matrix/', 'historical script, not current instructions'),
    ('docs/', 'private documentation, phases, decisions and evidence (D157)'),
)
REPLACED = {'AGENTS.md', 'CLAUDE.md', 'GEMINI.md'}  # private instructions; the public ones come from docs/public/
HIDDEN = {'.gitattributes', '.gitignore', '.python-version', '.github', 'frontend/.npmrc',
          'tests/fixtures/typescript_web/.gitignore'}
# `PNNN-TNNN` codes in code comments are explained by the public DECISIONS preamble (D176); `P001-T001` is also product
# test data. Only personal paths/identities, the private project and links into the private archive/phases are flagged.
# `/private/tmp` (macOS alias of /tmp) and `archive/phase-NNN` links are product behavior in managed projects.
PRIVATE = re.compile(r'/Users/(?!USER\b|you\b)|/home/(?!user\b)[a-z]|acosta@|dacostac|reference_project'
                     r'|\]\([^)]*docs/(archive|phase)/', re.IGNORECASE)


def git(*args: str) -> bytes:
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True).stdout


def sources(revision: str | None) -> dict[str, tuple[str, bytes]]:
    """path → (mode, bytes) from a revision, or from the working tree (tracked + untracked not ignored)."""
    found = {}
    if revision:
        for line in git('ls-tree', '-r', '-z', revision).split(b'\0'):
            if line:
                meta, path = line.decode().split('\t', 1)
                mode, kind, obj = meta.split()
                if kind != 'blob' or mode == '120000':
                    raise SystemExit(f'{path}: {kind} {mode} is not a regular file')
                found[path] = (mode, git('cat-file', 'blob', obj))
        return found
    listed = git('ls-files', '-z', '--cached', '--others', '--exclude-standard').split(b'\0')
    for path in filter(None, (item.decode() for item in listed)):
        file = ROOT / path
        if not file.exists():
            continue  # deleted in the working tree
        if file.is_symlink() or not file.is_file():
            raise SystemExit(f'{path}: not a regular file')
        found[path] = ('100755' if file.stat().st_mode & 0o111 else '100644', file.read_bytes())
    return found


def classify(path: str) -> tuple[str | None, str]:
    if path.startswith(PUBLIC):
        return path.removeprefix(PUBLIC), 'public baseline'
    if path in REPLACED:
        return None, 'replaced by docs/public/' + path
    for prefix, reason in EXCLUDED:
        if path.startswith(prefix):
            return None, reason
    if path in ROOT_FILES or path in EXAMPLES or path.startswith(COPIED_PREFIXES):
        return path, 'copied'
    raise SystemExit(f'{path}: not classified by the positive list')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--revision')
    parser.add_argument('--out', type=Path, default=ROOT / '.local/public-candidate')
    parser.add_argument('--private-manifest', type=Path, default=ROOT / 'docs/phase/P012-T005_MANIFIESTO_PRIVADO.tsv')
    parser.add_argument('--public-manifest', type=Path, default=ROOT / 'docs/phase/P012-T005_MANIFIESTO_PUBLICO.sha256')
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        raise SystemExit(f'{out} exists; remove it first')
    base = git('rev-parse', args.revision or 'HEAD').decode().strip()
    files = sources(args.revision)
    for manifest in (args.private_manifest.resolve(), args.public_manifest.resolve()):  # own outputs, not sources
        if manifest.is_relative_to(ROOT):
            files.pop(str(manifest.relative_to(ROOT)), None)
    rows, tree = [], {}
    for path in sorted(files):
        mode, content = files[path]
        target, reason = classify(path)
        digest = hashlib.sha256(content).hexdigest()
        rows.append((path, target or '-', digest, mode, reason))
        if target:
            if target in tree:
                raise SystemExit(f'{target}: two sources')
            tree[target] = (mode, content)
    for target, (mode, content) in tree.items():
        file = out / target
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(content)
        file.chmod(0o755 if mode == '100755' else 0o644)
    origin = f'revision {base}' if args.revision else f'working tree on {base}'
    args.private_manifest.write_text(f'# Private: {origin}. source\tcandidate\tsha256\tmode\tdisposition\n'
                                     + ''.join('\t'.join(row) + '\n' for row in rows))
    public = ''.join(f'{hashlib.sha256(tree[t][1]).hexdigest()}  {t}\n' for t in sorted(tree))
    args.public_manifest.write_text(public)
    # Checks on the materialized tree, not on the sources.
    on_disk = sorted(str(p.relative_to(out)) for p in out.rglob('*') if p.is_file() or p.is_symlink())
    problems = [f'symlink {p}' for p in on_disk if (out / p).is_symlink()]
    problems += [f'unexpected hidden {p}' for p in on_disk if any(part.startswith('.') for part in Path(p).parts)
                 and Path(p).parts[0] not in HIDDEN and p not in HIDDEN]
    problems += [f'private pattern in {p}: {m[0]!r}' for p in on_disk
                 for m in [PRIVATE.search((out / p).read_bytes().decode('utf-8', 'replace'))] if m]
    if on_disk != sorted(tree):
        problems.append('tree differs from the manifest')
    summary = {'origin': origin, 'sources': len(rows), 'candidate_files': len(tree),
               'excluded': sum(1 for row in rows if row[1] == '-'),
               'public_baseline': sum(1 for row in rows if row[4] == 'public baseline'),
               'candidate_bytes': sum(len(c) for _, c in tree.values()),
               'public_manifest_sha256': hashlib.sha256(public.encode()).hexdigest(), 'problems': problems}
    print(json.dumps(summary, indent=2))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())

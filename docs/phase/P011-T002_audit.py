"""Read-only local audit of the private source; never prints matched values.

Run from the repository root with Python 3.11+:
    python3 docs/phase/P011-T002_audit.py --revision b31b720 > /tmp/p011-audit.json
    python3 docs/phase/P011-T002_audit.py --revision b31b720 \
        --inventory docs/phase/P011-T002_INVENTARIO.tsv > /tmp/p011-audit.json

The inventory is private planning input, not an approved export manifest. No
product imports, network, extraction, builds, subprocess providers or services.
Only local Git read commands are executed. Reflogs, unreachable objects, ignored
working files and dependency caches are outside the secret scan.
"""

import argparse
from collections import Counter, defaultdict
import csv
from email.parser import Parser
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
import tempfile
import tomllib
import zipfile


PATTERNS = {
    'private_key': r'-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----',
    'provider_token': r'\bsk-(?:(?:proj|ant|svcacct)-)?[A-Za-z0-9_-]{24,}',
    'github_token': r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})',
    'aws_access_key': r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'google_api_key': r'\bAIza[A-Za-z0-9_-]{35}\b',
    'slack_token': r'\bxox[baprs]-[A-Za-z0-9-]{20,}',
    'jwt': r'\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}',
    'credential_url': r'[a-zA-Z][a-zA-Z0-9+.-]*://[^\s/:@]+:[^\s/@]+@',
    'credential_literal': r'''(?i)["']?(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|secret|login[_-]?key)["']?\s*[:=]\s*["'][^"'\n]{8,}["']''',
    'home_path': r'/(?:Users|home)/[A-Za-z0-9_.-]+',
    'private_doc_reference': r'(?:docs/)?(?:archive/phase-\d{3}/|phase/P\d{3}[-_])|\bD\d{3}\b',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
}
COMPILED = {name: re.compile(pattern) for name, pattern in PATTERNS.items()}
SENSITIVE_NAME = re.compile(
    r'(^|/)(?:\.env(?:\..+)?|(?:credentials|auth|secrets)\.json|id_(?:rsa|ed25519)(?:\..+)?|'
    r'[^/]+\.(?:pem|key|p12|pfx|sqlite3|db|bundle))$'
)


def git(*args):
    return subprocess.check_output(['git', '--no-lazy-fetch', *args])


def scan(data):
    # Scan every byte stream, including non-UTF-8 blobs, without executing it.
    value = data.decode('utf-8', errors='replace')
    return {name: len(pattern.findall(value)) for name, pattern in COMPILED.items()
            if pattern.search(value)}


def disposition(path):
    if path.startswith(('docs/', 'examples/first_use/', 'examples/provider_matrix/')):
        return 'exclude-private', 'T014/T015', 'New public documentation; preserve private originals'
    if path.startswith('tests/fixtures/cli_help/'):
        return 'replace-before-export', 'T006/T012', 'Real CLI help; replace with synthetic capability fixtures'
    if path.startswith('tests/fixtures/legacy/'):
        return 'remove-before-export', 'T019', 'Exclusive legacy fixture; preserve private history'
    if path.startswith(('README', 'AGENTS.md', 'CLAUDE.md', 'GEMINI.md')):
        return 'replace-before-export', 'T014', 'New self-contained public baseline'
    if path.startswith('examples/'):
        return 'review-before-export', 'T005/T014', 'Synthetic standalone example; no private references'
    if path.startswith(('src/', 'tests/', 'frontend/', 'scripts/')):
        return 'review-before-export', 'T003-T012/T019/T015', 'Recheck after translation and legacy removal'
    return 'review-before-export', 'T015', 'Explicit public file selection and final artifact check'


def audit(revision, inventory):
    revision = git('rev-parse', '--verify', revision + '^{commit}').decode().strip()
    entries = []
    tree_counts = Counter()
    current_counts = Counter()
    current_findings = []
    source_sizes = 0
    for record in git('ls-tree', '-r', '-z', revision).split(b'\0'):
        if not record:
            continue
        metadata, name = record.split(b'\t', 1)
        mode, kind, oid = metadata.decode().split()
        path = name.decode('utf-8')
        tree_counts[mode] += 1
        if kind != 'blob':
            raise RuntimeError('Non-blob tree entry requires manual review')
        body = git('cat-file', 'blob', oid)
        source_sizes += len(body)
        findings = scan(body)
        current_counts.update(findings)
        if findings or SENSITIVE_NAME.search(path):
            current_findings.append({'path': path, 'categories': findings,
                                     'sensitive_name': bool(SENSITIVE_NAME.search(path))})
        state, owner, condition = disposition(path)
        entries.append([path, hashlib.sha256(body).hexdigest(), mode, state, owner,
                        ','.join(sorted(findings)), condition])
    if inventory:
        with inventory.open('w', newline='') as stream:
            writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
            writer.writerow(['path', 'sha256', 'mode', 'disposition', 'owner', 'categories', 'condition'])
            writer.writerows(entries)

    # --all includes heads, remote refs and Codex checkpoint refs. One scan per
    # unique reachable object, not just one tree per branch or recent commits.
    objects = git('rev-list', '--objects', '--all', '--no-object-names').splitlines()
    historical_paths = set(git('log', '--all', '--format=', '--name-only', '-z').decode().split('\0'))
    sensitive_paths = sorted(p for p in historical_paths if SENSITIVE_NAME.search(p)
                             and not p.endswith('.env.example'))
    types = Counter()
    history_counts = Counter()
    object_matches = defaultdict(list)
    identities = set()
    history_bytes = 0
    with tempfile.TemporaryFile() as request:
        request.write(b'\n'.join(objects) + b'\n')
        request.seek(0)
        with subprocess.Popen(['git', '--no-lazy-fetch', 'cat-file', '--batch'],
                              stdin=request, stdout=subprocess.PIPE) as process:
            for _ in objects:
                oid, kind, size = process.stdout.readline().split()
                body = process.stdout.read(int(size))
                if len(body) != int(size) or process.stdout.read(1) != b'\n':
                    raise RuntimeError('Incomplete Git object')
                types[kind.decode()] += 1
                history_bytes += len(body)
                found = scan(body)
                history_counts.update(found)
                for category in found:
                    object_matches[category].append(oid.decode())
                if kind == b'commit':
                    for line in body.split(b'\n\n', 1)[0].splitlines():
                        if line.startswith((b'author ', b'committer ')):
                            identities.add(hashlib.sha256(line.split(b' ', 1)[1].rsplit(b' ', 2)[0]).hexdigest())
            if process.wait() != 0:
                raise RuntimeError('Git object scan failed')

    archives = []
    for path in sorted(Path('dist').glob('*')):
        if path.suffix == '.whl':
            with zipfile.ZipFile(path) as archive:
                archive_names = archive.namelist()
                links = [p.filename for p in archive.infolist() if (p.external_attr >> 16) & 0o170000 == 0o120000]
                members = [(p.filename, archive.read(p)) for p in archive.infolist() if not p.is_dir()]
        elif path.name.endswith('.tar.gz'):
            with tarfile.open(path) as archive:
                archive_names = archive.getnames()
                links = [p.name for p in archive if p.issym() or p.islnk()]
                members = [(p.name, archive.extractfile(p).read()) for p in archive if p.isfile()]
        else:
            continue
        counts = Counter()
        unsafe_names = [name for name in archive_names
                        if PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts]
        for name, body in members:
            counts.update(scan(name.encode() + b'\n' + body))
        archives.append({'name': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'files': len(members), 'categories': dict(counts),
                         'unsafe_names': unsafe_names,
                         'link_entries': links,
                         'names': [name for name, _ in members]})
    return {'revision': revision, 'tree': {'files': len(entries), 'bytes': source_sizes,
                'modes': dict(tree_counts), 'categories': dict(current_counts),
                'dispositions': dict(Counter(row[3] for row in entries)), 'findings': current_findings},
            'history': {'objects': len(objects), 'types': dict(types), 'bytes': history_bytes,
                'distinct_author_committer_identities': len(identities),
                'sensitive_paths': sensitive_paths,
                'categories': dict(history_counts), 'matched_objects': dict(object_matches)},
            'existing_archives': archives}


def dependency_inventory(destination, notices):
    """Inventory lock declarations; retain exact upstream frontend notices."""
    rows = []
    metadata = {}
    for path in Path('.venv/lib').glob('python*/site-packages/*.dist-info/METADATA'):
        record = Parser().parsestr(path.read_text())
        name = record['Name'].lower().replace('_', '-')
        metadata[(name, record['Version'])] = (path, record)
    lock = tomllib.loads(Path('uv.lock').read_text())
    for package in lock['package']:
        name, version = package['name'], package['version']
        if name == 'harness-local':
            continue
        evidence = metadata.get((name, version))
        license_name = 'not-in-local-evidence'
        source, digest = 'uv.lock; external dependency, not vendored', ''
        if evidence:
            path, record = evidence
            license_name = record['License-Expression'] or record['License'] or 'not-in-local-evidence'
            source, digest = 'installed METADATA (matching locked version)', hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(['python', name, version, 'runtime-or-development', license_name, source, digest])
    recipe = json.loads(Path('src/harness_local/recipes/django-packages.json').read_text())
    for name, version in recipe.items():
        rows.append(['django-recipe', name, version, 'child-only', 'not-in-local-evidence',
                     'version/hash recipe manifest; downloaded separately, not vendored', ''])
    backend = tomllib.loads(Path('pyproject.toml').read_text())['build-system']['requires'][0]
    rows.append(['build-backend', *backend.split('=='), 'build-only', 'not-in-local-evidence',
                 'pyproject.toml; not vendored', ''])

    frontend = json.loads(Path('frontend/package-lock.json').read_text())['packages']
    note_texts = {}
    note_packages = []
    for relative, package in frontend.items():
        if not relative:
            continue
        root = Path('frontend') / relative
        name = relative.rsplit('node_modules/', 1)[1]
        declared = package.get('license', 'not-in-lock')
        source = 'frontend/package-lock.json'
        if root.exists():
            installed = json.loads((root / 'package.json').read_text())
            if installed['version'] != package['version']:
                raise RuntimeError('Installed dependency differs from lock: ' + name)
            if declared == 'not-in-lock' and name == 'khroma':
                if 'The MIT License (MIT)' not in (root / 'license').read_text():
                    raise RuntimeError('Unexpected khroma license')
                declared, source = 'MIT', 'installed khroma/license (absent from lock metadata)'
        scope = 'build/development' if package.get('dev') else 'frontend-runtime'
        rows.append(['npm', name, package['version'], scope, declared, source,
                     package.get('integrity', '')])
        if package.get('dev'):
            continue
        if not root.exists():
            raise RuntimeError('Runtime license unavailable locally: ' + name)
        files = sorted(p for p in root.rglob('*') if p.is_file()
                       and 'node_modules' not in p.relative_to(root).parts
                       and any(part in p.name.lower() for part in
                               ('license', 'licence', 'copying', 'notice', 'copyright')))
        if not files and name in ('fastdom', 'strictdom'):
            # These two upstream distributions put the full MIT terms in README.
            text = (root / 'README.md').read_text()
            text = text[text.index('## License'):]
            parts = [('README.md, License section', text)]
        else:
            parts = [(str(p.relative_to(root)), p.read_text()) for p in files]
        if not parts:
            raise RuntimeError('Runtime notice unavailable: ' + name)
        references = []
        for filename, value in parts:
            digest = hashlib.sha256(value.encode()).hexdigest()
            note_texts[digest] = value
            references.append(f'{filename}: [notice {digest[:16]}](#notice-{digest[:16]})')
        note_packages.append(f'| {name} | {package["version"]} | {declared} | {"; ".join(references)} |')
    fixture = json.loads(Path('tests/fixtures/typescript_web/package-lock.json').read_text())['packages']
    for name, record in fixture.items():
        if name:
            rows.append(['typescript-child', name.removeprefix('node_modules/'), record['version'],
                         'child-only', record.get('license', 'not-in-lock'), 'synthetic fixture lock', ''])
    if destination:
        with destination.open('w', newline='') as stream:
            writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
            writer.writerow(['ecosystem', 'package', 'version', 'scope', 'license', 'evidence', 'digest'])
            writer.writerows([[cell or '-' for cell in row] for row in rows])
    if notices:
        lock_digest = hashlib.sha256(Path('frontend/package-lock.json').read_bytes()).hexdigest()
        content = [
            '# Third-party frontend notices', '',
            'Harness Local uses third-party components under their own licenses. The',
            'project MIT license does not replace these terms or copyright notices.', '',
            'This inventory preserves the local upstream notice texts for all 123',
            'runtime entries in the frontend lock, including components a build may omit.',
            'Duplicate texts are shared by hash. It is not a claim about the contents of',
            'a particular wheel or browser bundle. Release packaging must retain the',
            'applicable notices and verify the final assets, including fonts.', '',
            'Python dependencies and child-project recipe dependencies are installed',
            'separately with their upstream license files. Development and build tools',
            'retain their own terms and are not covered by this runtime notice inventory.', '',
            f'Frontend lock SHA-256: `{lock_digest}`.', '',
            '| Package | Version | License | Upstream notice |', '|---|---|---|---|',
            *note_packages, '',
        ]
        for digest, value in sorted(note_texts.items()):
            content.extend([f'## Notice {digest[:16]}', '', '````text', value.rstrip('\n'), '````', ''])
        if len(note_packages) != 123:
            raise RuntimeError('Review runtime inventory count before regenerating notices')
        notices.write_text('\n'.join(content))
    return {'entries': len(rows), 'frontend_runtime': len(note_packages),
            'distinct_notice_texts': len(note_texts),
            'licenses_without_local_evidence': sum(r[4] == 'not-in-local-evidence' for r in rows)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', default='HEAD')
    parser.add_argument('--inventory', type=Path)
    parser.add_argument('--dependencies', type=Path)
    parser.add_argument('--notices', type=Path)
    arguments = parser.parse_args()
    result = audit(arguments.revision, arguments.inventory)
    if arguments.dependencies or arguments.notices:
        result['dependencies'] = dependency_inventory(arguments.dependencies, arguments.notices)
    print(json.dumps(result, indent=2, sort_keys=True))

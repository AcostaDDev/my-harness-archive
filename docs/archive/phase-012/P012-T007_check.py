"""Verify P012's documentary closure with local reads only; no services, builds or network.

Run from the repository root using its installed environment:
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python docs/archive/phase-012/P012-T007_check.py
Original snapshots are checked against their source commit and links in their original paths.
"""
import contextlib
from functools import lru_cache
import hashlib
import io
import json
from pathlib import Path
import posixpath
import re
import subprocess
import sys
import types

from harness_local.core.engine.documents import BUDGETS, base_section, decision_index, parse_roadmap, plan_tasks

ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = ROOT / 'docs/archive/phase-012'
BASE = 'ce4b5d2f8ed1a1ac1af9cec00316b10b1d95a814'
PUBLIC_BASE = '99b1b9954d543259a84956940ea8543035551077'
MANIFEST = 'cf191a40914095aeb3fbbeea0e6485878cc3218754361fa78d314b87dc19362a'


def git(*args):
    return subprocess.run(['git', '--no-lazy-fetch', *args], cwd=ROOT, check=True, capture_output=True).stdout


@lru_cache(None)
def original(path):
    return git('show', f'{BASE}:{path}')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_original(name, filename):
    """Load read-only helpers under their original location without editing archived bytes."""
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / 'docs/phase' / filename)
    exec(compile((ARCHIVE / filename).read_bytes(), module.__file__, 'exec'), module.__dict__)
    return module


def entries(data):
    return dict(line.split('  ', 1)[::-1] for line in data.decode().splitlines())


def anchors(text):
    out, seen, in_code = set(), {}, False
    for line in text.splitlines():
        if line.startswith('```'):
            in_code = not in_code
        if not in_code and (match := re.match(r'#{1,6} (.*)', line)):
            slug = ''.join(c for c in match[1].strip().lower().replace('`', '')
                           if c.isalnum() or c in ' -_').replace(' ', '-')
            count = seen.get(slug, 0)
            seen[slug] = count + 1
            out.add(slug if count == 0 else f'{slug}-{count}')
    return out


def check_links(docs, historical=False):
    count = 0
    for name, data in docs.items():
        text = re.sub(r'```.*?```', '', data.decode(), flags=re.S)
        for target in re.findall(r'\]\(([^)\s]+)\)', text):
            if re.match(r'[a-z]+:', target):
                continue
            count += 1
            file, _, anchor = target.partition('#')
            dest = posixpath.normpath(posixpath.join(posixpath.dirname(name), file)) if file else name
            if historical:
                # The snapshot keeps its source path and source commit, not its archive path.
                content = original(dest)
            else:
                assert (ROOT / dest).exists(), (name, target)
                content = (ROOT / dest).read_bytes() if (ROOT / dest).is_file() else b''
            if anchor and dest.endswith('.md'):
                assert anchor in anchors(content.decode()), (name, target, 'missing anchor')
    return count


def normalize_navigation(text):
    return (text.replace('(archive/phase-012/P012', '(phase/P012')
            .replace('[Tareas](archive/phase-012/NEXT_STEPS.md)', '[Tareas](NEXT_STEPS.md)'))


def bodies(text):
    return {match[1]: match[2].rstrip('\n') for match in
            re.finditer(r'^## (D\d{3}) — ([\s\S]*?)(?=^## D\d{3} — |\Z)', text, re.M)}


def public_tree(exporter, revision):
    tree = {}
    for source, item in exporter.sources(revision).items():
        target, _ = exporter.classify(source)
        if target:
            assert target not in tree
            tree[target] = item
    return tree


def main():
    manifest = json.loads((ARCHIVE / 'MANIFEST.json').read_text())
    assert manifest['source_commit'] == BASE and manifest['phase'] == 'P012'
    expected_sources = {'docs/STATE.md', 'docs/NEXT_STEPS.md'} | set(
        git('ls-tree', '-r', '--name-only', BASE, 'docs/phase/').decode().splitlines())
    rows = manifest['files']
    assert len(rows) == 42 and {row['source'] for row in rows} == expected_sources
    assert len({row['target'] for row in rows}) == len(rows)
    snapshots = {}
    for row in rows:
        data = (ROOT / row['target']).read_bytes()
        assert data == original(row['source']), row['source']
        assert len(data) == row['size_bytes'] and sha(data) == row['sha256']
        if row['source'].endswith('.md'):
            snapshots[row['source']] = data
    assert not list((ROOT / 'docs/phase').rglob('*')), 'docs/phase must be empty'
    previous = git('ls-tree', '-r', '--name-only', BASE, 'docs/archive/').decode().splitlines()
    for name in previous:
        assert (ROOT / name).read_bytes() == original(name), name
    state = (ROOT / 'docs/STATE.md').read_text()
    next_steps = (ROOT / 'docs/NEXT_STEPS.md').read_text()
    roadmap = (ROOT / 'docs/ROADMAP.md').read_text()
    decisions = (ROOT / 'docs/DECISIONS.md').read_text()
    phases = parse_roadmap(roadmap)
    assert phases == parse_roadmap(original('docs/ROADMAP.md').decode()), 'phase contracts changed'
    assert len(phases) == 12 and len(phases[-1]['exit_criteria']) == 7
    assert not plan_tasks(next_steps)
    assert len(plan_tasks((ARCHIVE / 'NEXT_STEPS.md').read_text(), 'P012')) == 13
    parsed = decision_index(decisions)
    assert [item['id'] for item in parsed] == [f'D{n:03d}' for n in range(1, 213)]
    assert all(item['status'] for item in parsed)
    index_ids = re.findall(r'^\| \[(D\d{3})\]\(#', decisions, re.M)
    assert index_ids == [item['id'] for item in parsed]
    old_bodies, current_bodies = bodies(original('docs/DECISIONS.md').decode()), bodies(decisions)
    assert len(old_bodies) == 211
    for key, body in old_bodies.items():
        assert normalize_navigation(current_bodies[key]) == body, key
    sizes = {'state': len(state.encode()), 'base': len(base_section(state).encode()),
             'next_steps': len(next_steps.encode())}
    assert all(size <= BUDGETS[key] for key, size in sizes.items()), sizes
    assert 'Sin fase activa ni sucesora definida' in state
    assert 'harness-local:managed-' not in state + next_steps
    live = [p for p in ROOT.glob('*.md')] + list((ROOT / 'docs').glob('*.md'))
    live += list((ROOT / 'docs/flows').glob('*.md'))
    current_docs = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in live}
    assert not any(re.search(rb'\]\([^)]*phase/P012', data) for data in current_docs.values())
    new_docs = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in ARCHIVE.glob('*.md')
                if p.name in {'SUMMARY.md', 'REVIEW.md', 'P012_CIERRE.md'}}
    live_links = check_links(current_docs | new_docs)
    snapshot_links = check_links(snapshots, historical=True)
    mermaid_count = 0
    for name, data in current_docs.items():
        diagrams = re.findall(rb'```mermaid\n.*?```', data, re.S)
        assert diagrams == re.findall(rb'```mermaid\n.*?```', original(name), re.S), name
        mermaid_count += len(diagrams)
    changes = git('diff', '--name-only', BASE).decode().splitlines()
    untracked = git('ls-files', '--others', '--exclude-standard').decode().splitlines()
    staged = git('diff', '--cached', '--name-only', BASE).decode().splitlines()
    assert all(p.startswith('docs/') and not p.startswith('docs/public/')
               for p in set(changes + untracked + staged)), 'change outside private docs'
    exporter = load_original('p012_exporter', 'P012-T005_public_candidate.py')
    reviewer = load_original('p012_hash_helpers', 'P012-T006_check.py')
    expected_bytes = (ARCHIVE / 'P012-T005_MANIFIESTO_PUBLICO.sha256').read_bytes()
    assert sha(expected_bytes) == MANIFEST
    expected = entries(expected_bytes)
    tree = public_tree(exporter, PUBLIC_BASE)
    assert public_tree(exporter, None) == tree
    assert ''.join(f'{sha(tree[p][1])}  {p}\n' for p in sorted(tree)).encode() == expected_bytes
    modes = {path: item[0] for path, item in tree.items()}
    candidate = reviewer.verify_tree(ROOT.parent / 'my_harness_dist', expected, modes)
    old_bytes = (ROOT / 'docs/archive/phase-011/P011-T017_MANIFIESTO_PUBLICO.sha256').read_bytes()
    assert sha(old_bytes) == '74cc9141da0295a0a658dc10673a454c93eae3fd3cfe86e3df5aa7b9a172ea71'
    old_candidate = reviewer.verify_tree(ROOT.parent / 'my_harness_dist_p011_74cc9141', entries(old_bytes))
    package = ROOT / '.local/p012-t005/package'
    package_manifest = (ARCHIVE / 'P012-T005_PAQUETE.sha256').read_bytes()
    assert (package / 'SHA256SUMS').read_bytes() == package_manifest
    for name, digest in entries(package_manifest).items():
        assert sha((package / name).read_bytes()) == digest, name
    public = load_original('p012_public_checker', 'P012-T005_public_docs_check.py')
    public_output = io.StringIO()
    saved_argv = sys.argv
    try:
        sys.argv = [public.__file__, '--candidate', str(ROOT.parent / 'my_harness_dist')]
        with contextlib.redirect_stdout(public_output):
            assert public.main() == 0, public_output.getvalue()
    finally:
        sys.argv = saved_argv
    print(json.dumps({'base': BASE, 'phase': 'P012', 'originals_preserved': len(rows),
                      'previous_archive_files_preserved': len(previous), 'phase_directory_empty': True,
                      'phase_contracts_preserved': len(phases), 'p012_exit_criteria': 7,
                      'active_tasks': 0, 'archived_tasks': 13, 'decisions': len(parsed),
                      'previous_decision_bodies_preserved_except_navigation': len(old_bodies),
                      'sizes': sizes, 'live_documents': len(current_docs | new_docs),
                      'live_relative_links': live_links, 'snapshot_documents': len(snapshots),
                      'snapshot_links_in_original_context': snapshot_links,
                      'live_mermaid_blocks_preserved': mermaid_count, 'private_docs_only': True,
                      'public_manifest_sha256': MANIFEST, 'public_sources_unchanged': True,
                      'candidate': candidate, 'previous_candidate': old_candidate,
                      'package_sha256': entries(package_manifest),
                      'sha256sums_sha256': sha(package_manifest),
                      'public_documentation_check': public_output.getvalue().strip()}, indent=2))


if __name__ == '__main__':
    main()

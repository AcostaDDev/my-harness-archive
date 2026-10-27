"""Verify P013's documentary closure with local reads only; no services, builds, installs or network.

Run from the repository root using its locked environment:
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python -B docs/archive/phase-013/P013-T015_check.py
Snapshots are checked against their source commit, and their links in their original paths. Archived helpers
are executed under their original docs/phase path without editing their bytes. Prints a JSON report.
"""
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import posixpath
import re
import subprocess
import sys
import types
from urllib.parse import unquote

from harness_local.core.engine.documents import BUDGETS, base_section, decision_index, parse_roadmap, plan_tasks

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = ROOT / 'docs/archive/phase-013'
BASE = 'ff5109df44d65665db1e33a6f3f99f241d3928a0'
SOURCE = '984c287ab9f21ba7976fc7cdb5df86b4f235b118'
MANIFEST = 'ea0f74e9099f1383128ba5e6e2e92ac298447cab54bd7336909d66f0f800c428'
STATUS_DOCS = {'docs/STATE.md', 'docs/NEXT_STEPS.md', 'docs/ROADMAP.md', 'docs/DECISIONS.md',
               'docs/SPECIFICATION.md', 'docs/ARCHITECTURE.md'}


def git(*args):
    return subprocess.run(['git', '--no-lazy-fetch', *args], cwd=ROOT, check=True, capture_output=True).stdout


@lru_cache(None)
def original(path):
    return git('show', f'{BASE}:{path}')


@lru_cache(None)
def original_kind(path):
    result = subprocess.run(['git', 'cat-file', '-t', f'{BASE}:{path}'], cwd=ROOT, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_original(name, filename):
    """Execute an archived helper as if it were still in docs/phase, so path-derived roots stay correct."""
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / 'docs/phase' / filename)
    exec(compile((ARCHIVE / filename).read_bytes(), module.__file__, 'exec'), module.__dict__)
    return module


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
            file, _, anchor = unquote(target).partition('#')
            dest = posixpath.normpath(posixpath.join(posixpath.dirname(name), file)) if file else name
            if historical:
                # The snapshot keeps its source path and source commit, not its archive path.
                kind = original_kind(dest)
                assert kind, (name, target)
                content = original(dest) if kind == 'blob' else b''
            else:
                assert (ROOT / dest).exists(), (name, target)
                content = (ROOT / dest).read_bytes() if (ROOT / dest).is_file() else b''
            if anchor and dest.endswith('.md'):
                assert anchor in anchors(content.decode()), (name, target, 'missing anchor')
    return count


def normalize_navigation(text):
    return (text.replace('](archive/phase-013/NEXT_STEPS.md', '](NEXT_STEPS.md')
            .replace('](../archive/phase-013/NEXT_STEPS.md', '](../NEXT_STEPS.md')
            .replace('](archive/phase-013/', '](phase/').replace('](../archive/phase-013/', '](../phase/'))


def bodies(text):
    return {match[1]: match[2].rstrip('\n') for match in
            re.finditer(r'^## (D\d{3}) — ([\s\S]*?)(?=^## D\d{3} — |\Z)', text, re.M)}


def main():
    manifest = json.loads((ARCHIVE / 'MANIFEST.json').read_text())
    assert manifest['source_commit'] == BASE and manifest['phase'] == 'P013'
    phase_sources = git('ls-tree', '-r', '--name-only', BASE, 'docs/phase/').decode().splitlines()
    rows = manifest['files']
    assert len(rows) == 74 and {row['source'] for row in rows} == {'docs/STATE.md', 'docs/NEXT_STEPS.md', *phase_sources}
    assert len({row['target'] for row in rows}) == len(rows)
    snapshots = {}
    for row in rows:
        data = (ROOT / row['target']).read_bytes()
        assert data == original(row['source']), row['source']
        assert len(data) == row['size_bytes'] and sha(data) == row['sha256']
        if row['source'].endswith('.md'):
            snapshots[row['source']] = data
    assert not [p for p in (ROOT / 'docs/phase').rglob('*') if p.is_file()], 'docs/phase must be empty'
    archived = {p.relative_to(ROOT).as_posix() for p in ARCHIVE.rglob('*') if p.is_file()}
    new_files = {f'docs/archive/phase-013/{name}' for name in
                 ('MANIFEST.json', 'SUMMARY.md', 'REVIEW.md', 'P013_CIERRE.md', 'P013-T015_check.py',
                  'P013-T015_COMPROBACION.json')}
    assert archived == {row['target'] for row in rows} | new_files, archived ^ ({row['target'] for row in rows} | new_files)
    previous = git('ls-tree', '-r', '--name-only', BASE, 'docs/archive/').decode().splitlines()
    for name in previous:
        assert (ROOT / name).read_bytes() == original(name), name

    state = (ROOT / 'docs/STATE.md').read_text()
    next_steps = (ROOT / 'docs/NEXT_STEPS.md').read_text()
    roadmap = (ROOT / 'docs/ROADMAP.md').read_text()
    decisions = (ROOT / 'docs/DECISIONS.md').read_text()
    phases = parse_roadmap(roadmap)
    assert phases == parse_roadmap(original('docs/ROADMAP.md').decode()), 'phase contracts changed'
    assert len(phases) == 13 and len(phases[-1]['exit_criteria']) == 8
    assert '| P013 | Instalación guiada y configuración desde la UI | completada (2026-10-27) |' in roadmap
    assert not plan_tasks(next_steps)
    assert len(plan_tasks((ARCHIVE / 'NEXT_STEPS.md').read_text(), 'P013')) == 15
    parsed = decision_index(decisions)
    assert [item['id'] for item in parsed] == [f'D{n:03d}' for n in range(1, 233)]
    assert all(item['status'] for item in parsed)
    assert re.findall(r'^\| \[(D\d{3})\]\(#', decisions, re.M) == [item['id'] for item in parsed]
    old_bodies, current_bodies = bodies(original('docs/DECISIONS.md').decode()), bodies(decisions)
    assert len(old_bodies) == 231
    for key, body in old_bodies.items():
        assert normalize_navigation(current_bodies[key]) == body, key
    sizes = {'state': len(state.encode()), 'base': len(base_section(state).encode()),
             'next_steps': len(next_steps.encode())}
    assert all(size <= BUDGETS[key] for key, size in sizes.items()), sizes
    assert 'Sin fase activa ni sucesora definida' in state
    assert 'harness-local:managed-' not in state + next_steps

    live = list(ROOT.glob('*.md')) + list((ROOT / 'docs').glob('*.md')) + list((ROOT / 'docs/flows').glob('*.md'))
    current_docs = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in live}
    assert not any(re.search(rb'\]\((\.\./)?phase/', data) for data in current_docs.values())
    unchanged_after_relocation = 0
    for name, data in current_docs.items():
        if name not in STATUS_DOCS:
            assert normalize_navigation(data.decode()).encode() == original(name), name
            unchanged_after_relocation += 1
    new_docs = {f'docs/archive/phase-013/{name}': (ARCHIVE / name).read_bytes()
                for name in ('SUMMARY.md', 'REVIEW.md', 'P013_CIERRE.md')}
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

    reviewer = load_original('p013_t014_check', 'P013-T014_CHECK.py')
    qualifier = load_original('p013_t013_candidate', 'P013-T013_CANDIDATE.py')
    qualifier.load = lambda name, path: load_original(name, Path(path).name)
    exporter = reviewer.load('p012_exporter', ROOT / 'docs/archive/phase-012/P012-T005_public_candidate.py')
    exporter.ROOT = ROOT
    public_manifest = ARCHIVE / 'P013-T013_MANIFIESTO_PUBLICO.sha256'
    assert sha(public_manifest.read_bytes()) == MANIFEST
    tree = {}
    for source, item in exporter.sources(SOURCE).items():
        target, _ = exporter.classify(source)
        if target:
            assert target not in tree
            tree[target] = item
    assert ''.join(f'{sha(tree[p][1])}  {p}\n' for p in sorted(tree)).encode() == public_manifest.read_bytes()
    current = {}
    for source, item in exporter.sources(None).items():
        target, _ = exporter.classify(source)
        if target:
            current[target] = item
    assert current == tree, 'current public sources differ from the qualified candidate'
    candidate_dir = ROOT.parent / 'my_harness_dist_p013'
    candidate = reviewer.verify_tree(candidate_dir, public_manifest, {name: item[0] for name, item in tree.items()})
    public_docs = qualifier.check_public(candidate_dir)
    previous_candidates = {}
    for label, folder, file in (
            ('D214', 'my_harness_dist', ARCHIVE / '2026-10-26_CANDIDATO_MANIFIESTO_PUBLICO.sha256'),
            ('P012', 'my_harness_dist_p012_cf191a40', ROOT / 'docs/archive/phase-012/P012-T005_MANIFIESTO_PUBLICO.sha256'),
            ('P011', 'my_harness_dist_p011_74cc9141', ROOT / 'docs/archive/phase-011/P011-T017_MANIFIESTO_PUBLICO.sha256')):
        previous_candidates[label] = reviewer.verify_tree(ROOT.parent / folder, file)
    conservation = json.loads((ARCHIVE / 'P013-T013_CONSERVACION.json').read_text())
    protected = 0
    for name, expected in conservation.items():
        if name == 'docs/archive':
            continue  # Grows by design; its previous files are compared with BASE above.
        path = ROOT / name if name.startswith('.local/') or name == 'dist' else ROOT.parent / name
        inventory = qualifier.inventory(path)
        assert sha(json.dumps(inventory, sort_keys=True, separators=(',', ':')).encode()) == expected['inventory_sha256'], name
        protected += 1
    package = ROOT.parent / 'my_harness_p013_t013_verification/package'
    assert (package / 'SHA256SUMS').read_bytes() == (ARCHIVE / 'P013-T013_PAQUETE.sha256').read_bytes()
    results = json.loads((ARCHIVE / 'P013-T013_RESULTS.json').read_text())
    package_hashes = {p.relative_to(package).as_posix(): sha(p.read_bytes()) for p in package.rglob('*') if p.is_file()}
    assert package_hashes == results['artifacts']

    print(json.dumps({'base': BASE, 'phase': 'P013', 'originals_preserved': len(rows),
                      'originals_bytes': sum(row['size_bytes'] for row in rows),
                      'previous_archive_files_preserved': len(previous), 'phase_directory_empty': True,
                      'phase_contracts_preserved': len(phases), 'p013_exit_criteria': 8,
                      'active_tasks': 0, 'archived_tasks': 15, 'decisions': len(parsed),
                      'previous_decision_bodies_preserved_except_navigation': len(old_bodies),
                      'sizes': sizes, 'live_documents': len(current_docs | new_docs),
                      'live_documents_identical_except_navigation': unchanged_after_relocation,
                      'live_relative_links': live_links, 'snapshot_documents': len(snapshots),
                      'snapshot_links_in_original_context': snapshot_links,
                      'live_mermaid_blocks_preserved': mermaid_count, 'private_docs_only': True,
                      'public_manifest_sha256': MANIFEST, 'public_sources_unchanged': True,
                      'candidate': candidate, 'candidate_public_documents': public_docs,
                      'previous_candidates': previous_candidates, 'protected_inventories': protected,
                      'package_sha256': package_hashes}, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()

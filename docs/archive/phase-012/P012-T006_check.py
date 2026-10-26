"""P012-T006: read-only documentary/hash review; no services, builds, providers or network.

Run from the repository root with its installed environment:
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python docs/phase/P012-T006_check.py
The baseline is the committed T005 delivery; local package and both external candidates must still exist.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

from harness_local.core.engine.documents import BUDGETS, base_section, decision_index, parse_roadmap, plan_tasks

ROOT = Path(__file__).resolve().parents[2]
BASE = '99b1b9954d543259a84956940ea8543035551077'
MANIFEST = 'cf191a40914095aeb3fbbeea0e6485878cc3218754361fa78d314b87dc19362a'


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True).stdout


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'docs/phase' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def entries(data):
    return dict(line.split('  ', 1)[::-1] for line in data.decode().splitlines())


def verify_tree(root, expected, modes=None):
    paths = list(root.rglob('*'))
    assert not any(p.is_symlink() for p in paths), f'symlink: {root.name}'
    assert not any(p.name == '.git' for p in paths), f'Git: {root.name}'
    actual = {p.relative_to(root).as_posix(): sha(p.read_bytes()) for p in paths if p.is_file()}
    assert actual == expected, f'list/bytes: {root.name}'
    if modes:
        for name, mode in modes.items():
            assert (root / name).stat().st_mode & 0o777 == int(mode[-3:], 8), f'mode: {name}'
    return {'files': len(actual), 'bytes': sum((root / name).stat().st_size for name in actual),
            'hashes': True, 'modes_checked': bool(modes), 'no_git_or_symlinks': True}


def main():
    exporter = load('candidate_t005', 'P012-T005_public_candidate.py')
    public = load('public_check_t005', 'P012-T005_public_docs_check.py')
    manifest_bytes = (ROOT / 'docs/phase/P012-T005_MANIFIESTO_PUBLICO.sha256').read_bytes()
    assert sha(manifest_bytes) == MANIFEST
    expected = entries(manifest_bytes)
    rows = [line.split('\t') for line in
            (ROOT / 'docs/phase/P012-T005_MANIFIESTO_PRIVADO.tsv').read_text().splitlines()[1:]]
    modes = {row[1]: row[3] for row in rows if row[1] != '-'}
    assert set(modes) == set(expected)
    tree = {}
    for source, (mode, content) in exporter.sources(BASE).items():
        target, _ = exporter.classify(source)
        if target:
            assert target not in tree
            tree[target] = (mode, content)
    reproduced = ''.join(f'{sha(tree[p][1])}  {p}\n' for p in sorted(tree)).encode()
    assert reproduced == manifest_bytes, 'T005 committed export differs'
    current_tree = {}
    for source, item in exporter.sources(None).items():
        target, _ = exporter.classify(source)
        if target:
            assert target not in current_tree
            current_tree[target] = item
    assert current_tree == tree, 'current public source list/bytes/modes differ from T005'
    assert {name: item[0] for name, item in tree.items()} == modes
    candidate = verify_tree(ROOT.parent / 'my_harness_dist', expected, modes)
    old_bytes = (ROOT / 'docs/archive/phase-011/P011-T017_MANIFIESTO_PUBLICO.sha256').read_bytes()
    assert sha(old_bytes) == '74cc9141da0295a0a658dc10673a454c93eae3fd3cfe86e3df5aa7b9a172ea71'
    previous = verify_tree(ROOT.parent / 'my_harness_dist_p011_74cc9141', entries(old_bytes))
    package = ROOT / '.local/p012-t005/package'
    package_bytes = (ROOT / 'docs/phase/P012-T005_PAQUETE.sha256').read_bytes()
    assert (package / 'SHA256SUMS').read_bytes() == package_bytes
    package_hashes = entries(package_bytes)
    for name, digest in package_hashes.items():
        assert sha((package / name).read_bytes()) == digest, f'package: {name}'
    docs = {p: ROOT / p for p in ('docs/STATE.md', 'docs/NEXT_STEPS.md', 'docs/ROADMAP.md', 'docs/DECISIONS.md',
                                'docs/phase/P012_REVIEW.md', 'docs/phase/P012_EXPEDIENTE_APERTURA.md')}
    texts = {p: path.read_text() for p, path in docs.items()}
    phases = parse_roadmap(texts['docs/ROADMAP.md'])
    tasks = plan_tasks(texts['docs/NEXT_STEPS.md'], 'P012')
    decisions = decision_index(texts['docs/DECISIONS.md'])
    assert len(phases) == 12 and len(phases[-1]['exit_criteria']) == 7 and len(tasks) == 13
    assert len(decisions) == 211 and all(d['status'] for d in decisions)
    state, next_steps = texts['docs/STATE.md'], texts['docs/NEXT_STEPS.md']
    sizes = {'state': len(state.encode()), 'base': len(base_section(state).encode()),
             'next_steps': len(next_steps.encode())}
    assert all(size <= BUDGETS[key] for key, size in sizes.items()), sizes
    # Reuse the public checker's GitHub-style anchors, but resolve private paths in this checkout.
    public.ROOT = ROOT
    public.MATERIALIZED = True
    links = public.check_links(docs)
    assert not public.errors, public.errors
    original = git('show', f'{BASE}:docs/DECISIONS.md').decode()
    def bodies(text):
        return {m[1]: m[2].rstrip('\n') for m in
                re.finditer(r'^## (D\d{3}) — ([\s\S]*?)(?=^## D\d{3} — |\Z)', text, re.M)}
    old, new = bodies(original), bodies(texts['docs/DECISIONS.md'])
    assert all(new[key] == value for key, value in old.items())
    preserved = {'archive': 0, 'phase_originals': 0}
    for area, prefix in (('archive', 'docs/archive/'), ('phase_originals', 'docs/phase/')):
        for name in git('ls-tree', '-r', '--name-only', BASE, prefix).decode().splitlines():
            assert (ROOT / name).read_bytes() == git('show', f'{BASE}:{name}'), f'changed original: {name}'
            preserved[area] += 1
    print(json.dumps({'base': BASE, 'public_manifest_sha256': MANIFEST,
                      'committed_export_and_current_public_sources_match': True, 'candidate': candidate,
                      'previous_candidate': previous, 'package_sha256': package_hashes,
                      'sha256sums_sha256': sha(package_bytes), 'phases': len(phases),
                      'p012_exit_criteria': 7, 'tasks': len(tasks), 'decisions': len(decisions),
                      'sizes': sizes, 'relative_links': links, 'preserved': preserved,
                      'previous_decision_bodies_preserved': len(old)}, indent=2))


if __name__ == '__main__':
    main()

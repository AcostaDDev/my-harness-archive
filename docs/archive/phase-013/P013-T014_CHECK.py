"""Read-only exit review: exact public sources, local candidates/package and private evidence.

Run with the locked development environment. No build, installation, service,
provider, database or remote Git operation. Prints a JSON report to stdout.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import stat
import subprocess
import sys
from urllib.parse import unquote

from harness_local.core.engine.documents import BUDGETS, base_section, decision_index, parse_roadmap, plan_tasks

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
PHASE = ROOT / 'docs/phase'
BASE = 'a0cab9e51f6440b827825d5491313f0542e4197e'
SOURCE = '984c287ab9f21ba7976fc7cdb5df86b4f235b118'
MANIFEST = 'ea0f74e9099f1383128ba5e6e2e92ac298447cab54bd7336909d66f0f800c428'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def entries(path):
    rows = [line.split('  ', 1) for line in path.read_text().splitlines()]
    assert len(rows) == len({row[1] for row in rows})
    return {name: digest for digest, name in rows}


def verify_tree(root, manifest, modes=None):
    paths = list(root.rglob('*'))
    assert root.is_dir() and not root.is_symlink()
    assert not any(p.is_symlink() or p.name == '.git' for p in paths)
    expected = entries(manifest)
    assert {p.relative_to(root).as_posix(): sha(p.read_bytes()) for p in paths if p.is_file()} == expected
    directories = {parent.as_posix() for name in expected for parent in Path(name).parents if parent != Path('.')}
    assert {p.relative_to(root).as_posix() for p in paths if p.is_dir()} == directories
    assert all(p.is_dir() or p.is_file() for p in paths)
    if modes:
        assert set(modes) == set(expected)
        assert all(stat.S_IMODE((root / name).stat().st_mode) == int(mode[-3:], 8) for name, mode in modes.items())
    return {'files': len(expected), 'bytes': sum((root / name).stat().st_size for name in expected),
            'manifest_sha256': sha(manifest.read_bytes()), 'exact_paths_hashes': True, 'modes': bool(modes)}


def main():
    qualifier = load('qualification', PHASE / 'P013-T013_CANDIDATE.py')
    exporter = load('exporter', ROOT / 'docs/archive/phase-012/P012-T005_public_candidate.py')
    exporter.ROOT = ROOT
    sources = exporter.sources(SOURCE)
    tree, rows = {}, []
    for source, (mode, content) in sorted(sources.items()):
        target, reason = exporter.classify(source)
        rows.append([source, target or '-', sha(content), mode, reason])
        if target:
            assert target not in tree
            tree[target] = (mode, content)
    original_rows = [line.split('\t') for line in (PHASE / 'P013-T013_MANIFIESTO_PRIVADO.tsv').read_text().splitlines()[1:]]
    assert rows == original_rows
    manifest = PHASE / 'P013-T013_MANIFIESTO_PUBLICO.sha256'
    assert sha(manifest.read_bytes()) == MANIFEST
    assert ''.join(f'{sha(tree[name][1])}  {name}\n' for name in sorted(tree)).encode() == manifest.read_bytes()
    current = {}
    for source, value in exporter.sources(None).items():
        target, _ = exporter.classify(source)
        if target:
            assert target not in current
            current[target] = value
    assert current == tree, 'Current public sources differ from the qualified candidate'
    candidate = ROOT.parent / 'my_harness_dist_p013'
    reviewed = verify_tree(candidate, manifest, {name: value[0] for name, value in tree.items()})
    public_docs = qualifier.check_public(candidate)
    previous = {}
    for label, folder, file in (
        ('D214', 'my_harness_dist', PHASE / '2026-10-26_CANDIDATO_MANIFIESTO_PUBLICO.sha256'),
        ('P012', 'my_harness_dist_p012_cf191a40', ROOT / 'docs/archive/phase-012/P012-T005_MANIFIESTO_PUBLICO.sha256'),
        ('P011', 'my_harness_dist_p011_74cc9141', ROOT / 'docs/archive/phase-011/P011-T017_MANIFIESTO_PUBLICO.sha256')):
        previous[label] = verify_tree(ROOT.parent / folder, file)
    conservation = json.loads((PHASE / 'P013-T013_CONSERVACION.json').read_text())
    for name, expected in conservation.items():
        path = ROOT / name if name.startswith(('docs/', '.local/')) or name == 'dist' else ROOT.parent / name
        inventory = qualifier.inventory(path)
        assert sha(json.dumps(inventory, sort_keys=True, separators=(',', ':')).encode()) == expected['inventory_sha256'], name
    package = ROOT.parent / 'my_harness_p013_t013_verification/package'
    assert (package / 'SHA256SUMS').read_bytes() == (PHASE / 'P013-T013_PAQUETE.sha256').read_bytes()
    results = json.loads((PHASE / 'P013-T013_RESULTS.json').read_text())
    actual = {p.relative_to(package).as_posix(): sha(p.read_bytes()) for p in package.rglob('*') if p.is_file()}
    assert actual == results['artifacts']
    artifacts = load('artifacts', ROOT / 'scripts/distribution_artifacts.py')
    assert artifacts.check_artifacts(package)['project']['version'] == '0.1.0'
    frozen = {'archive': 0, 'phase': 0}
    for kind, prefix in (('archive', 'docs/archive/'), ('phase', 'docs/phase/')):
        for name in git('ls-tree', '-r', '--name-only', BASE, prefix).decode().splitlines():
            if name in ('docs/phase/P013_PLAN.md', 'docs/phase/P013_MATRIZ_ACEPTACION.md'):
                continue
            assert (ROOT / name).read_bytes() == git('show', f'{BASE}:{name}'), name
            frozen[kind] += 1
    state = (ROOT / 'docs/STATE.md').read_text()
    steps = (ROOT / 'docs/NEXT_STEPS.md').read_text()
    roadmap = parse_roadmap((ROOT / 'docs/ROADMAP.md').read_text())
    decisions_text = (ROOT / 'docs/DECISIONS.md').read_text()
    decisions = decision_index(decisions_text)
    assert len(roadmap) == 13 and len(roadmap[-1]['exit_criteria']) == 8
    assert len(plan_tasks(steps, 'P013')) == 15 and len(decisions) == 231 and all(d['status'] for d in decisions)
    old = git('show', f'{BASE}:docs/DECISIONS.md').decode()
    assert old[old.index('## D001 —'):].strip() == decisions_text[decisions_text.index('## D001 —'):decisions_text.index('## D231 —')].strip()
    sizes = {'state': len(state.encode()), 'base': len(base_section(state).encode()), 'next_steps': len(steps.encode())}
    assert all(value <= BUDGETS[key] for key, value in sizes.items()), sizes
    changed = set(git('diff', BASE, '--name-only').decode().splitlines())
    changed.update(git('ls-files', '--others', '--exclude-standard').decode().splitlines())
    assert all(name.startswith('docs/') and not name.startswith(('docs/archive/', 'docs/public/')) for name in changed)
    public = load('public', PHASE / 'P013-T012_CHECK_PUBLIC.py')
    links, markdown = 0, 0
    for name in sorted(changed):
        if not name.endswith('.md'):
            continue
        path = ROOT / name
        content = path.read_text()
        assert len(re.findall(r'^```', content, re.M)) % 2 == 0, name
        markdown += 1
        for target in re.findall(r'\]\(([^\s)]+)\)', content):
            if re.match('[a-z]+:', target):
                continue
            file, _, anchor = unquote(target).partition('#')
            destination = (path.parent / file).resolve() if file else path
            assert destination.exists(), (name, target)
            if anchor and destination.suffix == '.md':
                assert anchor in public.anchors(destination), (name, target)
            links += 1
    print(json.dumps({'base_reviewed': BASE, 'source_candidate': SOURCE, 'candidate': reviewed,
                      'committed_and_current_public_sources_match': True, 'private_manifest_rows': len(rows),
                      'public_documents': public_docs, 'previous_candidates': previous, 'protected_inventories': len(conservation),
                      'protected_paths_bytes_modes_unchanged': True,
                      'package_sha256': actual, 'package_members_metadata_hashes': True, 'phases': len(roadmap),
                      'p013_exit_criteria': 8, 'tasks': 15, 'decisions': len(decisions), 'sizes': sizes,
                      'private_markdown_checked': markdown, 'relative_links': links, 'frozen_originals': frozen,
                      'previous_decision_bodies_preserved': 230, 'operational_suites_repeated': False}, indent=2))


if __name__ == '__main__':
    main()

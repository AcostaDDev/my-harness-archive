"""P013-T012: static checks of the public documentation baseline (read-only, no processes or network).

The public candidate is modelled as T013 will assemble it: `docs/public/**` mapped to the candidate root, plus the
root files and folders the candidate takes from this checkout. Checks relative links and GitHub-style anchors, the
D088 parsers and budgets, every DNNN cited by candidate code against the public DECISIONS, and private references.

Usage from the repository root:
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python docs/phase/P013-T012_public_docs_check.py
"""
import posixpath
import re
import subprocess
import sys
from pathlib import Path

from harness_local.core.engine.documents import (
    MAX_AGENTS_LINES, MAX_INSTRUCTIONS_BYTES, MAX_WRAPPER_LINES, BUDGETS, base_section, decision_index,
    parse_roadmap, plan_tasks,
)

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / 'docs/public'
# Root paths the candidate takes from this checkout (T001 §8); everything under docs/ comes from docs/public.
ROOT_SOURCED = ('README.md', 'README.es.md', 'LICENSE', 'NOTICE.md', 'NOTICE-THIRD-PARTY.md', 'CONTRIBUTING.md',
                'SECURITY.md', 'CHANGELOG.md', 'pyproject.toml', 'examples/', 'scripts/', 'src/', 'frontend/', 'tests/',
                '.github/')
EXCLUDED_EXAMPLES = ('examples/first_use/', 'examples/provider_matrix/')
# Synthetic decision ids used as parser sample data in tests, not references (see the DECISIONS preamble).
SYNTHETIC_IDS = {'D002', 'D007', 'D010', 'D098'}
# First number of new decisions, named by the DECISIONS preamble and AGENTS.md (P011-T023).
RESERVED_IDS = {'D230'}
# Links into an archive, or this repository's private phases; managed projects' archive/phase-000 is product behavior.
PRIVATE = [r'\]\([^)]*archive/phase-\d', r'archive/phase-0(0[1-9]|10)\b', r'docs/phase/P0', r'\bP0(0\d|1[01])-T\d{3}\b', r'/Users/(?!USER\b)', r'/private/tmp',
           r'(?i)reference_project', r'gpt-6', r'claude-sonnet', r'acosta@']
errors = []


def candidate(path: str) -> Path | None:
    """File of the candidate tree for a root-relative path, or None if the candidate would not contain it."""
    overlay = PUBLIC / path
    if overlay.exists():
        return overlay
    if path.startswith('docs/') or path in ('AGENTS.md', 'CLAUDE.md', 'GEMINI.md'):
        return None
    if path.startswith(EXCLUDED_EXAMPLES):
        return None
    if any(path == item or path.startswith(item) for item in ROOT_SOURCED) and (ROOT / path).exists():
        return ROOT / path
    return None


def public_documents() -> dict[str, Path]:
    docs = {str(p.relative_to(PUBLIC)): p for p in PUBLIC.rglob('*.md')}
    docs.update({name: ROOT / name for name in ('README.md', 'README.es.md', 'CONTRIBUTING.md', 'SECURITY.md',
                                                 'NOTICE.md', 'CHANGELOG.md')})
    return docs


def slug(text: str) -> str:
    text = re.sub(r'`', '', text.strip().lower())
    return ''.join(c for c in text if c.isalnum() or c in ' -_').replace(' ', '-')


def anchors(path: Path) -> set[str]:
    out, seen, in_code = set(), {}, False
    for line in path.read_text().splitlines():
        if line.startswith('```'):
            in_code = not in_code
        if not in_code and (m := re.match(r'#{1,6} (.*)', line)):
            s = slug(m.group(1))
            n = seen.get(s, 0)
            seen[s] = n + 1
            out.add(s if n == 0 else f'{s}-{n}')
    return out


def check_links(docs: dict[str, Path]) -> int:
    total = 0
    for name, path in sorted(docs.items()):
        text = re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
        for target in re.findall(r'\]\(([^)\s]+)\)', text):
            if re.match(r'[a-z]+:', target):
                continue
            total += 1
            file, _, anchor = target.partition('#')
            rel = (Path(name).parent / file).as_posix() if file else name
            rel = posixpath.normpath(rel)
            dest = candidate(rel) if file else path
            if dest is None:
                errors.append(f'link outside the candidate: {name} -> {target}')
            elif anchor and dest.suffix == '.md' and anchor not in anchors(dest):
                errors.append(f'missing anchor: {name} -> {target}')
    return total


def check_layout() -> dict:
    agents = (PUBLIC / 'AGENTS.md').read_text()
    if len(agents.splitlines()) > MAX_AGENTS_LINES or len(agents.encode()) > MAX_INSTRUCTIONS_BYTES:
        errors.append('AGENTS.md exceeds 60 lines or 32 KiB')
    for wrapper in ('CLAUDE.md', 'GEMINI.md'):
        text = (PUBLIC / wrapper).read_text()
        if len(text.splitlines()) > MAX_WRAPPER_LINES or '@AGENTS.md' not in text:
            errors.append(f'{wrapper} must import AGENTS.md within 15 lines')
    docs = PUBLIC / 'docs'
    state, next_steps = (docs / 'STATE.md').read_text(), (docs / 'NEXT_STEPS.md').read_text()
    phases = parse_roadmap((docs / 'ROADMAP.md').read_text())
    decisions = decision_index((docs / 'DECISIONS.md').read_text())
    base = base_section(state)
    if base is None:
        errors.append('STATE has no accumulated baseline')
    sizes = {'state': len(state.encode()), 'base': len((base or '').encode()), 'next_steps': len(next_steps.encode())}
    for key, size in sizes.items():
        if size > BUDGETS[key]:
            errors.append(f'{key} budget exceeded: {size} > {BUDGETS[key]}')
    if not phases or phases[0].get('code') != 'P001':
        errors.append(f'ROADMAP does not start at P001: {phases}')
    active = re.search(r'^## Active phase — (P\d{3}) ', state, re.M)
    if not active or active.group(1) != 'P001' or not next_steps.startswith('# P001 — '):
        errors.append('STATE/NEXT_STEPS do not agree on the active phase P001')
    if any(not (d['status'] or '').startswith(('accepted', 'superseded', 'proposed', 'rejected')) for d in decisions):
        errors.append('a decision lacks a recognized Status line')
    ids = [d['id'] for d in decisions]
    if len(ids) != len(set(ids)) or ids != sorted(ids) or any(int(i[1:]) >= 230 for i in ids):
        errors.append('decision ids must be unique, ascending and below D230 in the baseline')
    return {'phases': [p.get('code') for p in phases], 'tasks': len(plan_tasks(next_steps)),
            'decisions': len(ids), 'sizes': sizes, 'ids': set(ids)}


def check_code_references(ids: set[str]) -> int:
    files = subprocess.run(['git', 'ls-files', 'src', 'frontend/src', 'frontend/tests', 'scripts', 'tests', 'examples'],
                           cwd=ROOT, check=True, capture_output=True, text=True).stdout.split()
    cited = set()
    for name in files:
        if '/fixtures/' in name or name.startswith(EXCLUDED_EXAMPLES):
            continue
        try:
            text = (ROOT / name).read_text()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        for line in text.splitlines():
            if re.search(r"## D\d|\| D\d|D\d{3}-|'D\d{3}'|\"D\d{3}\"", line):
                continue  # synthetic decision documents and index rows in tests
            cited.update(re.findall(r'\bD\d{3}\b', line))
    missing = sorted(cited - ids - SYNTHETIC_IDS)
    if missing:
        errors.append(f'code cites decisions without a public entry: {missing}')
    return len(cited)


def check_document_references(docs: dict[str, Path], ids: set[str]) -> int:
    """P011-T023: every DNNN cited by a public document has a public entry (DECISIONS cites only itself)."""
    cited = set()
    for name, path in docs.items():
        if name != 'docs/DECISIONS.md':
            cited.update(re.findall(r'\bD\d{3}\b', path.read_text()))
    missing = sorted(cited - ids - RESERVED_IDS)
    if missing:
        errors.append(f'public documents cite decisions without a public entry: {missing}')
    return len(cited)


def check_private(docs: dict[str, Path]) -> None:
    for name, path in docs.items():
        text = path.read_text()
        for pattern in PRIVATE:
            if re.search(pattern, text):
                errors.append(f'private reference {pattern!r} in {name}')


def main() -> int:
    docs = public_documents()
    links = check_links(docs)
    layout = check_layout()
    ids = layout.pop('ids')
    cited = check_code_references(ids)
    documented = check_document_references(docs, ids)
    check_private(docs)
    print(f'{len(docs)} public Markdown files, {links} relative links; layout {layout}; {cited} DNNN cited by code, '
          f'{documented} by documents')
    for error in errors:
        print('ERROR', error)
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())

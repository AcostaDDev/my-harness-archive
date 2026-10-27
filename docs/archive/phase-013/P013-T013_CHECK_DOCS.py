"""Offline live-document checks for the T013 delivery. Reads archive targets only when linked."""
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

from harness_local.core.engine.documents import Layout, budget_warnings, decision_index, parse_roadmap, plan_tasks

root = Path(__file__).resolve().parents[2]
BASE = '984c287ab9f21ba7976fc7cdb5df86b4f235b118'
changed = subprocess.check_output(['git', 'diff', BASE, '--name-only'], cwd=root, text=True).splitlines()
changed += subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=root, text=True).splitlines()
paths = sorted({root / path for path in changed if path.endswith('.md') and not path.startswith('docs/public/')})
assert not any('/docs/archive/' in str(path)  for path in paths)
roadmap = parse_roadmap((root / 'docs/ROADMAP.md').read_text())
tasks = plan_tasks((root / 'docs/NEXT_STEPS.md').read_text(), 'P013')
decisions = decision_index((root / 'docs/DECISIONS.md').read_text())
assert len(roadmap) == 13 and len(tasks) == 15 and len(decisions) == 230
assert all(item['status'] for item in decisions)
assert not budget_warnings(Layout('docs', 'docs/STATE.md', 'docs/NEXT_STEPS.md'), {
    path: (root / path).read_text() for path in ('docs/STATE.md', 'docs/NEXT_STEPS.md')})
previous = subprocess.check_output(['git', 'show', BASE + ':docs/DECISIONS.md'], cwd=root, text=True)
current = (root / 'docs/DECISIONS.md').read_text()
assert previous[previous.index('## D001 —'):].strip() == current[current.index('## D001 —'):current.index('## D230 —')].strip()

def anchors(text):
    used, result = {}, set()
    for heading in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', text, re.M):
        slug = re.sub(r'[^\w\- ]', '', heading.lower().replace('`', '')).replace(' ', '-')
        count = used.get(slug, 0)
        used[slug] = count + 1
        result.add(slug + (f'-{count}' if count else ''))
    return result

links = 0
for path in paths:
    text = path.read_text()
    assert len(re.findall(r'^```', text, re.M)) % 2 == 0, path
    for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', text):
        if target.startswith(('https:', 'http:', 'mailto:', 'plugin:')):
            continue
        file, _, anchor = unquote(target).partition('#')
        destination = (path.parent / file).resolve() if file else path
        assert destination.exists(), (path, target)
        if anchor and destination.suffix == '.md':
            assert anchor in anchors(destination.read_text()), (path, target)
        links += 1
print(f'{len(roadmap)} phases; {len(tasks)} tasks; {len(decisions)} decisions; {links} links/anchors in {len(paths)} documents; budgets and frozen decisions OK')

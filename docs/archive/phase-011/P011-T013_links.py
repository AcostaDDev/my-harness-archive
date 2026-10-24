"""P011-T013: relative links and GitHub-style anchors of the given Markdown files (read-only).

Usage from the repository root: python3 docs/phase/P011-T013_links.py docs/*.md docs/flows/*.md docs/phase/*.md README.md
"""
import re
import sys
from pathlib import Path

def slug(text):
    text = re.sub(r'`', '', text.strip().lower())
    text = ''.join(c for c in text if c.isalnum() or c in ' -_')
    return text.replace(' ', '-')

def anchors(path):
    out, seen = set(), {}
    in_code = False
    for line in path.read_text().splitlines():
        if line.startswith('```'):
            in_code = not in_code
        if not in_code and (m := re.match(r'#{1,6} (.*)', line)):
            s = slug(m.group(1)); n = seen.get(s, 0); seen[s] = n + 1
            out.add(s if n == 0 else f'{s}-{n}')
    return out

bad = total = 0
for name in sys.argv[1:]:
    path = Path(name)
    text = re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
    for target in re.findall(r'\]\(([^)\s]+)\)', text):
        if re.match(r'[a-z]+:', target):
            continue
        total += 1
        file, _, anchor = target.partition('#')
        dest = (path.parent / file).resolve() if file else path.resolve()
        if not dest.exists() or (anchor and dest.suffix == '.md' and anchor not in anchors(dest)):
            bad += 1; print('BROKEN', name, target)
print(f'{total} relative links, {bad} broken')

"""Synthetic Python/uv/Django validators. No dependencies, installs, providers or network."""
import json
import os
from pathlib import Path
import shutil
import sys

root = Path.cwd()
args = sys.argv[1:]
name = Path(sys.argv[0]).name
(root / '.harness-preparation' / 'probe.jsonl').open('a').write(json.dumps([name, args]) + '\n')
if args == ['--version']:
    print('uv 0.9.5' if name == 'synthetic-uv' else 'Python 3.13.1')
elif args[:4] == ['-I', '-m', 'venv', '--without-pip']:
    folder = root / '.venv' / 'bin'
    folder.mkdir(parents=True)
    (folder / 'python').symlink_to(Path(sys.argv[0]).resolve())
    for tool in ('pytest', 'ruff', 'mypy'):
        shutil.copyfile(Path(sys.argv[0]).resolve(), folder / tool)
        (folder / tool).chmod(0o700)
elif args[:2] == ['--no-config', 'pip']:
    if args[2] == 'install' and (root / '.harness-preparation/pause').exists():
        import time
        time.sleep(30)
elif args[:2] == ['-I', '-c']:
    print(json.dumps({'python':[3,13,1], 'packages':json.loads((root / '.harness-preparation/packages.json').read_text())}))
elif args[:2] == ['-m', 'django']:
    if args[2] == 'startproject':
        source, target = root / args[6], root / args[4]
    else:
        source, target = root / args[6], root / args[4]
    shutil.copytree(source, target, dirs_exist_ok=True)
elif args[:2] == ['manage.py', 'migrate']:
    (root / 'db.sqlite3').write_text('synthetic sqlite evidence')
elif name == 'pytest':
    folder = root / 'reports'
    folder.mkdir(exist_ok=True)
    failure = '<failure/>' if (root / '.harness-preparation/bad-junit').exists() else ''
    (folder / 'pytest.xml').write_text('<testsuites><testsuite><testcase name="synthetic-index">'+failure+'</testcase></testsuite></testsuites>')

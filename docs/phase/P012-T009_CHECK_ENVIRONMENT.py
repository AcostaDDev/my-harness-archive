"""Reproduce T009's data-only composition check with synthetic paths and no processes.

Run from the repository root with the installed offline development environment.
Reads the proposed synthetic T001 configuration, never the operational area.
"""
from copy import deepcopy
import os
from pathlib import Path
import pwd
import re
import shutil
import tempfile
import tomllib
from unittest.mock import patch

from harness_local.services.local_config import build


def main():
    proposal = Path(__file__).with_name('P012-T001_PROPUESTA_OPERATIVA.md').read_text()
    tables = [tomllib.loads(block) for block in re.findall(r'```toml\n(.*?)\n```', proposal, re.S)]
    data = next(table for table in tables if table.get('format') == 'local-config-7')
    with tempfile.TemporaryDirectory(prefix='p012-t009-synthetic-') as raw:
        root = Path(raw).resolve()
        projects, state = root / 'projects', root / 'state'
        projects.mkdir()
        state.mkdir()
        old, new = projects / 'b', projects / 'b-t009'
        for child in (old, new):
            (child / '.venv/bin').mkdir(parents=True)
            for name in ('python', 'pytest', 'ruff', 'mypy'):
                path = child / '.venv/bin' / name
                path.write_text('synthetic placeholder; never executed\n')
                path.chmod(0o700)
        temporary = new / '.local/codex-tmp'
        temporary.mkdir(parents=True, mode=0o700)
        # The TypeScript recipe does not participate in this Django proposal.
        data.pop('recipes')
        data['compositions'].pop('typescript')
        data['service'] = {'state_dir': str(state), 'supervisor': False}
        data['registration'] = {'roots': [str(projects)], 'bootstrap_enabled': True}
        for role in ('reviewer', 'executor'):
            entry = data['agents'][role]
            entry['executable'] = ['/synthetic/' + entry['provider']]
            entry['environment'] = {
                'HOME': str(root), 'USER': pwd.getpwuid(os.getuid()).pw_name,
                'PATH': '/synthetic/node:/usr/bin:/bin', 'LANG': 'C.UTF-8',
                'PYTHONDONTWRITEBYTECODE': '1',
            }
        composition = data['compositions']['django']
        composition['executables'] = {
            name: str(old / '.venv/bin' / name) for name in ('python', 'pytest', 'ruff', 'mypy')
        }
        composition['environment'] = {
            'HOME': str(root), 'PATH': str(old / '.venv/bin') + ':/usr/bin:/bin',
            'TMPDIR': str(root), 'LANG': 'C.UTF-8', 'CI': 'true',
            'DJANGO_SETTINGS_MODULE': 'config.settings', 'PYTHONDONTWRITEBYTECODE': '1',
        }
        policy = {
            'planning_mode': 'agent', 'executor_mode': 'catalog',
            'executor_models': ['gpt-6-luna'], 'executor_efforts': ['low'], 'max_revision_cycles': 0,
        }
        item = {
            'id': 'b', 'root': str(old), 'composition': 'django',
            'repository_trusted': True, 'policy': policy,
        }
        # Any attempt to launch a CLI, Git, shell or service makes the check fail.
        with patch('subprocess.Popen', side_effect=AssertionError('Unexpected process')):
            original = build(deepcopy(data), root / 'original.toml')
            before, _ = original.registrar.compose(item, 'synthetic')
            changed = deepcopy(data)
            presets = {}
            for role, name in [('reviewer', 'claude-t009'), ('executor', 'codex-t009')]:
                entry = deepcopy(data['agents'][role])
                entry.pop('model', None)
                entry.pop('effort', None)
                entry.update(
                    roles=[role], models=['sonnet' if role == 'reviewer' else 'gpt-6-luna'],
                    efforts=['low'], allow_open_executor=False,
                )
                presets[name] = entry
            environment = presets['codex-t009']['environment']
            environment['PATH'] = str(new / '.venv/bin') + ':' + environment['PATH']
            environment['TMPDIR'] = str(temporary)
            changed['agent_presets'] = presets
            changed['compositions']['django-t009'] = deepcopy(composition)
            changed['compositions']['django-t009']['executables'] = {
                name: str(new / '.venv/bin' / name) for name in composition['executables']
            }
            changed['compositions']['django-t009']['environment']['PATH'] = (
                str(new / '.venv/bin') + ':/usr/bin:/bin'
            )
            current = build(changed, root / 'copy.toml')
            after, _ = current.registrar.compose(item, 'synthetic')
            assert before.versions == after.versions
            fresh = {
                **item, 'id': 'b-t009', 'root': str(new), 'composition': 'django-t009',
                'agent_selection': {
                    'reviewer': {'preset_id': 'claude-t009', 'model': 'sonnet', 'effort': 'low'},
                    'executor': {'preset_id': 'codex-t009'},
                },
            }
            project, composed = current.registrar.compose(fresh, 'synthetic-new')
            executor_environment = dict(composed[4]['executor'].environment)
            original_environment = data['agents']['executor']['environment']
            assert set(executor_environment) == set(original_environment) | {'TMPDIR'}
            assert {
                key for key, value in executor_environment.items()
                if value != original_environment.get(key)
            } == {'PATH', 'TMPDIR'}
            assert shutil.which('python', path=environment['PATH']) == str(new / '.venv/bin/python')
            assert temporary.is_relative_to(new) and temporary.stat().st_mode & 0o777 == 0o700
            assert project.context.policy.max_revision_cycles == 0
            assert dict(composed[2].environment)['TMPDIR'] == str(root)
            assert composed[4]['reviewer'].environment == original.registrar.agents['reviewer'].environment
    print('PASS: data-only v7 delta; old versions preserved; only new executor PATH/TMPDIR change; '
          'Python resolves; private temporary within checkout; separate validator; zero revisions.')


if __name__ == '__main__':
    main()

"""Data-only T010 configuration proposal. Never writes or starts processes.

Pass the approved T009 TOML as the sole argument to inspect the proposed hash.
Materializing its return value in the operational area requires new consent.
"""
from copy import deepcopy
import hashlib
from pathlib import Path
import re
import sys
import tomllib


SOURCE_SHA256 = 'b11cce3d02fa3138127243e5cb4f634a45b75c4d836ca7b324afebded47e3cc9'
AREA = '$HOME/Documents/harness-validation/p012-20261024'
OLD_ROOT = AREA + '/projects/onboarding-b-t009'
NEW_ROOT = AREA + '/projects/managed-b-t010'


def proposed_text(source):
    """Keep previous tables intact; append isolated profile, presets and composition."""
    if hashlib.sha256(source.encode()).hexdigest() != SOURCE_SHA256:
        raise ValueError('The approved T009 source has changed')
    original = tomllib.loads(source)
    assert original['format'] == 'local-config-7'

    def table(name):
        match = re.search(r'^\[' + re.escape(name) + r'\]\n.*?(?=^\[|\Z)', source, re.M | re.S)
        if match is None:
            raise ValueError('Missing source table: ' + name)
        return match.group().rstrip() + '\n'

    profile = table('profiles.python-django').replace(
        '[profiles.python-django]', '[profiles.python-django-t010]', 1)
    profile += 'formatter_argv = ["ruff", "format", "--"]\nformatter_paths = ["*.py"]\n'
    additions = [profile]
    for name in ('agent_presets.claude-t009', 'agent_presets.codex-t009', 'compositions.django-t009'):
        section = table(name).replace('[' + name + ']', '[' + name.replace('-t009', '-t010') + ']', 1)
        section = section.replace(OLD_ROOT, NEW_ROOT)
        if name.startswith('compositions.'):
            section = section.replace('profile = "python-django"', 'profile = "python-django-t010"', 1)
        additions.append(section)
    result = source.replace('format = "local-config-7"', 'format = "local-config-8"', 1)
    result = result.rstrip() + '\n\n' + '\n'.join(additions)
    expected = deepcopy(original)
    expected['format'] = 'local-config-8'
    expected['profiles']['python-django-t010'] = {
        **deepcopy(original['profiles']['python-django']),
        'formatter_argv': ['ruff', 'format', '--'], 'formatter_paths': ['*.py'],
    }
    for name in ('claude', 'codex'):
        entry = deepcopy(original['agent_presets'][name + '-t009'])
        entry['environment'] = {key: value.replace(OLD_ROOT, NEW_ROOT)
                                for key, value in entry['environment'].items()}
        expected['agent_presets'][name + '-t010'] = entry
    entry = deepcopy(original['compositions']['django-t009'])
    entry['profile'] = 'python-django-t010'
    for key in ('environment', 'executables'):
        entry[key] = {name: value.replace(OLD_ROOT, NEW_ROOT) for name, value in entry[key].items()}
    expected['compositions']['django-t010'] = entry
    assert tomllib.loads(result) == expected
    return result


if __name__ == '__main__':
    source = Path(sys.argv[1]).read_text()
    result = proposed_text(source)
    print('PASS: exact v8 delta; old tables preserved; no writes/processes; proposed SHA256 '
          + hashlib.sha256(result.encode()).hexdigest())

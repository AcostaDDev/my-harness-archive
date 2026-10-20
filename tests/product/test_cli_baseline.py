"""P009-T013 (D122): Codex 0.163.0 and Claude 2.1.304 join the cli-12 baseline with the same argv.

The help texts under fixtures/cli_help are the real output of the pinned binaries. Everything
else runs through synthetic executables; no installed CLI, provider or network.
"""
from dataclasses import replace
from pathlib import Path
import re
import sys

import pytest

from harness_local.adapters.cli_agents import SUPPORTED, VERSION, WRITE_SUPPORTED, CLIConfig, CLIProcessAdapter, argv_for
from harness_local.adapters.cli_diagnostics import ACCESS_REQUIRED, REQUIRED, preflight_config
from harness_local.services.local_config import load_local_config
import test_agent_roles
from test_agent_roles import journey, request, v2
from test_local_config import launches, setup, write  # noqa: F401 (fixture)
from test_typescript_profile import repository, web  # noqa: F401 (fixtures)

HELP = Path(__file__).parents[1] / 'fixtures' / 'cli_help'
NEW = {'codex': '0.163.0', 'claude': '2.1.304'}
PREVIOUS = {'codex': '0.162.1', 'claude': '2.1.296'}
ROLES = ('planner', 'reviewer', 'phase', 'chat', 'bootstrap', 'definition', 'planning', 'executor')


def test_baseline_adds_the_pilot_versions_and_keeps_the_previous_ones():
    assert VERSION == 'cli-13'
    assert SUPPORTED == {'codex': ('0.161.0', '0.162.1', '0.163.0'), 'claude': ('2.1.295', '2.1.296', '2.1.304')}
    assert WRITE_SUPPORTED == {'codex': ('0.162.1', '0.163.0'), 'claude': SUPPORTED['claude']}


@pytest.mark.parametrize('provider,version', [('codex', '0.162.2'), ('codex', '0.164.0'), ('claude', '2.1.299'),
                                              ('claude', '2.1.300'), ('claude', '2.1.301'), ('claude', '2.1.303')])
def test_uncharacterized_neighbours_are_still_rejected(provider, version):
    with pytest.raises(ValueError, match='re-characterize'):
        CLIConfig(provider, ('/synthetic/cli',), version, (), 1)


@pytest.mark.parametrize('role', ROLES)
@pytest.mark.parametrize('provider', ['codex', 'claude'])
def test_new_versions_receive_exactly_the_characterized_argv(context, provider, role):
    tools = {'tools': ('Read', 'Edit'), 'allowed_tools': ('Read', 'Edit')} if provider == 'claude' else {}
    if provider == 'claude' and role != 'executor':
        tools = {}
    old = CLIConfig(provider, ('/synthetic/cli',), PREVIOUS[provider], (), 1, **tools)
    assert argv_for(replace(old, cli_version=NEW[provider]), context, request(role)) == argv_for(
        old, context, request(role))


def test_codex_writer_names_every_characterized_version(context):
    codex = CLIConfig('codex', ('/synthetic/cli',), '0.161.0', (), 1)
    with pytest.raises(ValueError, match='0.162.1, 0.163.0 only'):
        argv_for(codex, context, request('executor'))
    with pytest.raises(ValueError, match='not characterized'):
        CLIProcessAdapter({'reviewer': replace(codex, cli_version='0.163.0'), 'executor': codex}, '/tmp/artifacts')


@pytest.mark.parametrize('provider,name,args', [('codex', 'codex-0.163.0-exec-help.txt', ('exec', '--help')),
                                                ('claude', 'claude-2.1.304-help.txt', ('--help',))])
def test_real_help_of_the_pinned_binaries_passes_preflight(tmp_path, provider, name, args):
    text = (HELP / name).read_text()
    flags = set(re.findall(r'(?<![\w-])--[A-Za-z][A-Za-z0-9-]*(?![\w-])', text))
    for access in ('read', 'write'):
        assert not [flag for flag in REQUIRED[provider] + ACCESS_REQUIRED.get((provider, access), ())
                    if flag not in flags]
    version = f'codex-cli {NEW[provider]}' if provider == 'codex' else f'{NEW[provider]} (Claude Code)'
    probe = tmp_path / 'probe.py'
    probe.write_text(f'''import sys
args = tuple(sys.argv[1:])
if args == ('--version',): print({version!r}); sys.exit(0)
assert args == {args!r}, args
sys.stdout.write(open({str(HELP / name)!r}).read())
''')
    config = CLIConfig(provider, (sys.executable, str(probe)), NEW[provider], (('PATH', '/usr/bin:/bin'),), 5)
    for access in ('read', 'write'):
        report = preflight_config(config, access=access)
        assert report['available'] and report['observed_version'] == NEW[provider], report


@pytest.mark.parametrize('reviewer,executor', test_agent_roles.PAIRS)
def test_four_pairings_through_the_real_adapter_with_the_pilot_versions(
        setup, repository, monkeypatch, reviewer, executor):
    for provider, version in NEW.items():
        monkeypatch.setitem(test_agent_roles.VERSIONS, provider, version)
    context, data, folder, tmp_path = setup
    config = load_local_config(write(folder, v2(data, reviewer, executor)))
    versions = config.projects[0].versions
    assert (versions['reviewer_cli'], versions['executor_cli']) == (NEW[reviewer], NEW[executor])
    job, record = journey(repository, config, f'{reviewer}-{executor}-new')
    assert record.status == 'ACCEPTANCE_READY', record.history.stop
    specs = [row['spec'] for row in repository.processes(job.id)]
    assert [(s['provider'], s['cli_version']) for s in specs] == [
        (reviewer, NEW[reviewer]), (executor, NEW[executor]), (reviewer, NEW[reviewer])]
    assert all(s['preflight_observed']['observed_version'] == s['cli_version'] for s in specs)
    assert len(launches(tmp_path)) == 3


@pytest.fixture
def context(setup):
    return setup[0]

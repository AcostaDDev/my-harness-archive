"""Explicit offline fixture copied beside an installed wheel, never a provider factory."""
import json
import os
from pathlib import Path

from harness_local.adapters.engine_fake import ScriptedCommandRunner
from harness_local.adapters.git import GitWorkspace
from harness_local.core.engine.commit import GitIdentity
from harness_local.core.engine.context import EnginePolicy, ProjectContext, ProjectProfile
from harness_local.core.engine.contracts import AgentResult, freeze
from harness_local.services.managed_runtime import ManagedConfig, ManagedProject


class Agent:
    def __init__(self, area):
        self.area = area

    def invoke(self, context, request):
        with (self.area / 'calls.jsonl').open('a') as stream:
            stream.write(freeze({'role': request.role, 'id': request.id}) + '\n')
        if request.role == 'executor':
            context.path('docs/DELIVERY_CHECKLIST.md').write_text(
                '# Synthetic delivery\n\nInput: local request.\nSuccess: recorded outcome.\n'
                'Failure: invalid input rejected.\nNo provider or network.\n')
            payload = {'result': 'synthetic installed executor'}
        elif request.role == 'reviewer':
            payload = {'task_id': json.loads(request.task_json)['task_id'], 'verdict': 'ACCEPT',
                       'findings': [], 'blocking_questions': [], 'scope_grants': []}
        else:
            raise AssertionError('Unexpected role in installed offline journey')
        return AgentResult(freeze(payload), terminal_observed=True, exit_code=0)


def build():
    area = Path(os.environ['HARNESS_E2E_ROOT']).resolve(strict=True)
    if (area / 'marker').read_text() != 'offline-installed-v1\n':
        raise ValueError('Not a prepared offline fixture')
    context = ProjectContext(area / 'project', ProjectProfile('installed-synthetic'),
        EnginePolicy(('synthetic-executor',), ('medium',), 'synthetic-planner', 'medium', 'synthetic-reviewer', 'high'))
    versions = {'engine': 'e2e-1', 'agent_adapter': 'synthetic-1', 'commands': 'synthetic-1',
                'evidence': 'git-1', 'provider_cli': None}
    agent = Agent(area)
    def writer(c, v):
        assert v == versions
        return GitWorkspace(GitIdentity('Offline E2E', 'e2e@example.invalid'))
    return ManagedConfig((ManagedProject('offline', context, versions, bootstrap_enabled=True),),
        ports_factory=lambda c, v: (agent, ScriptedCommandRunner(), writer(c, v)),
        commit_factory=writer, supervisor=True, poll_seconds=.02)

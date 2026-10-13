"""H4.2: demo opt-in exclusivamente sintética en un directorio nuevo, sin proveedores."""
import json
import os
from pathlib import Path
import sys

from harness_local.adapters.engine_fake import ScriptedCommandRunner
from harness_local.adapters.git import GitWorkspace
from harness_local.core.engine.commit import GitIdentity
from harness_local.core.engine.contracts import AgentResult, freeze
from harness_local.services.managed_runtime import ManagedConfig, ManagedProject
from examples.managed_demo import context

VERSIONS = {'engine': 'h42-demo-1', 'agent_adapter': 'synthetic-bootstrap-1',
            'commands': 'synthetic-1', 'evidence': 'git-1', 'provider_cli': None}


class BootstrapDemoAgent:
    def __init__(self, area):
        self.area = area

    def invoke(self, context, request):
        with (self.area / 'calls.jsonl').open('a') as stream:
            stream.write(freeze({'role': request.role, 'id': request.id}) + '\n')
        if request.role == 'bootstrap':
            data = {'summary': 'Propuesta sintética; no se ha llamado a un proveedor.',
                    'requirements': ['Un escenario local observable y documentado'],
                    'alternatives': ['Conservar el perfil configurado; decidir el stack después del escenario'],
                    'pending_decisions': ['Confirmar alcance, arquitectura y exclusiones']}
        elif request.role == 'executor':
            context.path('docs/DELIVERY_CHECKLIST.md').write_text(
                '# Escenario sintético de entrega\n\nUsuario: operador local.\nEntrada: una solicitud válida.\n'
                'Resultado esperado: un resultado persistido y consultable.\nCaso de error: solicitud inválida rechazada.\n'
                '\nComprobaciones observables: cada función mínima del brief tiene una entrada y un resultado.\n'
                'Restricciones: sin proveedores, instalación, red externa ni ampliación de alcance.\n')
            data = {'result': 'Escenario documental sintético creado'}
        elif request.role == 'reviewer':
            task = json.loads(request.task_json)
            data = {'task_id': task['task_id'], 'verdict': 'ACCEPT', 'findings': [],
                    'blocking_questions': [], 'scope_grants': []}
        else:
            raise ValueError('Unsupported bootstrap demo role: ' + request.role)
        return AgentResult(freeze(data), terminal_observed=True, exit_code=0)


def prepare(area):
    area = Path(area).resolve()
    area.mkdir(exist_ok=False)
    (area / 'bootstrap-demo-marker').write_text('synthetic-bootstrap-v1\n')
    (area / 'empty').mkdir()
    (area / 'existing').mkdir()
    (area / 'existing' / 'README.md').write_text('Synthetic existing data: preserve without overwriting.\n')
    return area


def build():
    area = Path(os.environ['HARNESS_BOOTSTRAP_DEMO_ROOT']).resolve(strict=True)
    if (area / 'bootstrap-demo-marker').read_text() != 'synthetic-bootstrap-v1\n':
        raise ValueError('Not a prepared synthetic bootstrap area')
    agent = BootstrapDemoAgent(area)
    def writer(ctx, versions):
        if versions != VERSIONS:
            raise ValueError('Frozen synthetic versions changed')
        return GitWorkspace(GitIdentity('Harness Bootstrap Demo', 'bootstrap@example.invalid'))
    def ports(ctx, versions):
        return agent, ScriptedCommandRunner(), writer(ctx, versions)
    return ManagedConfig(tuple(ManagedProject(name, context(area / name), VERSIONS, bootstrap_enabled=True)
        for name in ('empty', 'existing')), ports_factory=ports, commit_factory=writer,
        supervisor=True, poll_seconds=0.1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python -m examples.bootstrap_demo NEW_DIRECTORY')
    print(prepare(sys.argv[1]))

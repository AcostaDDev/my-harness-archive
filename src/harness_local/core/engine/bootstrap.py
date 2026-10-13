"""H4.2: plantilla documental mantenida; no proveedores, web, SQLite ni stack en el núcleo."""
from dataclasses import asdict, replace
from hashlib import sha256
from importlib.resources import files
import json
from pathlib import PurePosixPath

from harness_local.core.engine.contracts import context_snapshot
from harness_local.core.engine.evidence import ContentEvidence, check_paths
from harness_local.core.engine.phases import phase_definition
from harness_local.core.engine.planning import deterministic_task

BRIEF_FIELDS = ('problem', 'users', 'minimum_features', 'constraints', 'delivery_goal')
DECISION_FIELDS = ('scope', 'architecture', 'out_of_scope')


def accepted_input(data):
    if not isinstance(data, dict) or set(data) != {'brief', 'decisions'}:
        raise ValueError('Bootstrap requires brief and explicit decisions')
    result = {}
    for group, fields in (('brief', BRIEF_FIELDS), ('decisions', DECISION_FIELDS)):
        values = data[group]
        if not isinstance(values, dict) or set(values) != set(fields):
            raise ValueError(f'Complete bootstrap {group} required')
        if any(not isinstance(v, str) or not v.strip() or len(v) > 4000 or '\0' in v for v in values.values()):
            raise ValueError('Each brief/decision must contain 1–4000 NUL-free characters')
        result[group] = {key: values[key].strip() for key in fields}
    return result


def fenced(value):
    # Datos libres no pueden crear headings, fences, HTML ni bloques gestionados.
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)
    for char in '<>`&':
        text = text.replace(char, f'\\u{ord(char):04x}')
    return '```json\n' + text + '\n```\n'


def proposal(context, data):
    data = accepted_input(data)
    raw = files(__package__).joinpath('templates/bootstrap-foundation.json').read_text(encoding='utf-8')
    template = json.loads(raw)
    tid = template['name'] + ':' + template['version'] + ':' + sha256(raw.encode()).hexdigest()
    task_id, phase_code = 'P001-T001', 'P001'
    task_path = template['task_path']
    model, effort = context.policy.executor_models[0], context.policy.executor_efforts[0]
    # Solo selecciones del servidor; no se interpretan comandos ni globs del brief.
    for value in (model, effort):
        if any(char.isspace() or char in '`/\n\r' for char in value):
            raise ValueError('Bootstrap executor selection cannot be represented in the maintained plan')
    plan = ('# Primera tarea\n\n## P001-T001 — Escenario de entrega\n'
            '**Objective:** ' + template['objective'] + '\n'
            '**Allowed paths:** `' + task_path + '`\n'
            '**Acceptance criteria:**\n' + ''.join('- ' + c + '\n' for c in template['criteria']) +
            '**Constraints:** Consultar docs/BRIEF.md y docs/DECISIONS.md; no ampliar alcance ni crear código de aplicación.\n'
            '**Validation:** Revisar la correspondencia explícita entre funciones y comprobaciones; '
            'las validaciones del perfil se ejecutan por el flujo normal de tareas.\n'
            '**Executor:** ' + model + ' / ' + effort + ' — Selección explícita de la política del proyecto\n')
    documents = {
        'README.md': '# Proyecto\n\nBase documental creada desde decisiones confirmadas. '
                     'La aplicación aún no está implementada.\n\nConsultar docs/BRIEF.md, docs/DECISIONS.md '
                     'y el plan de primera tarea.\n',
        'docs/BRIEF.md': '# Brief aceptado\n\n' + fenced(data['brief']),
        'docs/DECISIONS.md': '# Decisiones aceptadas\n\n' + fenced(data['decisions']),
        'docs/PROJECT_PROFILE.md': '# Perfil y política del servidor\n\n' + fenced({
            'profile': asdict(context.profile), 'policy': asdict(context.policy), 'template': tid}) +
            '\nComandos declarados; el bootstrap no los ejecuta ni concede permisos.\n',
        context.state_file: '# Estado\n\nBase documental creada. Primera fase P001 activa; '
                            'primera tarea P001-T001 pendiente de ejecución, revisión y commit.\n',
        context.next_steps_file: plan,
    }
    if len(documents) != 6 or task_path in documents:
        raise ValueError('Bootstrap canonical paths must be distinct from template documents and task')
    for path in documents:
        if str(PurePosixPath(path)) != path or path == '.' or any(
                path.startswith(other + '/') for other in documents if other != path):
            raise ValueError('Bootstrap document paths must be canonical and cannot overlap directories')
        if path == '.git' or path.startswith('.git/'):
            raise ValueError('Bootstrap documents cannot target Git metadata')
    contract = deterministic_task(context, task_id, phase_code, plan)
    evidence = ContentEvidence('', '', tuple([*documents, task_path]), '')
    if check_paths(context, {'allowed_paths': [*documents, task_path], 'forbidden_paths': []}, evidence).hard_failure:
        raise ValueError('Bootstrap documents or first task conflict with profile path policy')
    definition = phase_definition(context, {'code': phase_code, 'objective': template['objective'],
        'exit_criteria': template['criteria'], 'tasks': [task_id], 'documents': sorted(documents), 'tag': None})
    return {'template': {'id': tid, 'name': template['name'], 'version': template['version'],
                         'sha256': sha256(raw.encode()).hexdigest()},
            'input': data, 'context_sha256': sha256(context_snapshot(context).encode()).hexdigest(),
            'documents': [{'path': path, 'content': content, 'sha256': sha256(content.encode()).hexdigest()}
                          for path, content in sorted(documents.items())],
            'phase': definition, 'first_task': json.loads(contract), 'task_text': plan,
            'preparation': [asdict(c) for c in context.profile.preparation],
            'validations': [asdict(c) for c in context.profile.validations],
            'policy': asdict(context.policy), 'profile': context.profile.name}


def execute(context, history, saved, git, journal):
    journal.checkpoint(history, 'bootstrap')
    result = git.execute_bootstrap(context, saved['preview'], saved['intent'])
    return replace(history, status='completed', stop=None), result

"""Versioned templates and strict, single-pass rendering. Standard library only."""
from dataclasses import asdict, dataclass
from hashlib import sha256
from importlib.resources import files
import json
import re

from harness_local.core.engine.contracts import ContractError, freeze

VARIABLES = {
    'bootstrap-project': ('BRIEF',),
    'plan-task': ('INPUT_JSON',),
    'executor-routing': ('POLICY_JSON',),
    'execute-task': ('INSTRUCTIONS', 'TASK_JSON', 'PROFILE_INSTRUCTIONS'),
    'review-task': ('INPUT_JSON',),
    'revise-task': ('INSTRUCTIONS', 'TASK_JSON', 'REVIEW_JSON', 'PROFILE_INSTRUCTIONS'),
    'reconcile-phase': ('PHASE_ID', 'REVIEW_JSON'),
    'close-phase': ('PHASE_ID', 'EVIDENCE_JSON'),
}
ROLES = {'plan-task': 'planner', 'review-task': 'reviewer', 'execute-task': 'executor', 'revise-task': 'executor'}
TOKEN = re.compile(r'{{([A-Z][A-Z0-9_]*)}}')


def digest(text: str) -> str:
    return sha256(text.encode('utf-8')).hexdigest()


def validate(name: str, template: str) -> tuple[str, ...]:
    if name not in VARIABLES:
        raise ContractError('Unknown prompt name')
    if not isinstance(template, str) or not template.strip() or len(template) > 100_000:
        raise ContractError('Template must contain 1–100000 characters')
    used = set(TOKEN.findall(template))
    rest = TOKEN.sub('', template)
    if '{{' in rest or '}}' in rest:
        raise ContractError('Malformed variable; use {{UPPERCASE_NAME}}')
    allowed = set(VARIABLES[name])
    if used != allowed:
        raise ContractError(f'Invalid variables: unknown={sorted(used - allowed)}, missing={sorted(allowed - used)}')
    return tuple(sorted(used))


@dataclass(frozen=True)
class Template:
    name: str
    id: str
    scope: str
    owner: str
    template: str
    sha256: str
    source: str

    def check(self):
        validate(self.name, self.template)
        if digest(self.template) != self.sha256:
            raise ContractError('Template hash mismatch')


def builtin_catalog() -> dict[str, Template]:
    result = {}
    for name in VARIABLES:
        template = files(__package__).joinpath('templates', name + '.md').read_text(encoding='utf-8')
        result[name] = Template(name, 'builtin-1:' + digest(template), 'core', 'core', template,
                                digest(template), 'core/engine/templates/' + name + '.md')
    return result


def dump_catalog(catalog: dict[str, Template]) -> str:
    if set(catalog) != set(VARIABLES):
        raise ContractError('Incomplete prompt catalog')
    for name, template in catalog.items():
        template.check()
        if name != template.name:
            raise ContractError('Prompt identity mismatch')
    return freeze({name: asdict(item) for name, item in catalog.items()})


def load_catalog(value: str) -> dict[str, Template]:
    result = {name: Template(**item) for name, item in json.loads(value).items()}
    dump_catalog(result)
    return result


def render(template: Template, values: dict[str, str]) -> str:
    template.check()
    if set(values) != set(VARIABLES[template.name]) or not all(isinstance(v, str) for v in values.values()):
        raise ContractError('Missing or unknown render variables')
    # Values are data: inserted braces are never evaluated again.
    return TOKEN.sub(lambda match: values[match[1]], template.template)


def output_schema(role: str) -> dict:
    fields = {
        'planner': {'task_id': 'string', 'phase_id': 'string', 'title': 'string', 'objective': 'string',
                    'executor_prompt': 'string', 'allowed_paths': 'array', 'forbidden_paths': 'array',
                    'acceptance_criteria': 'array', 'validation_commands': 'array', 'executor_selection': 'object'},
        'reviewer': {'task_id': 'string', 'verdict': 'string'},
        'executor': {'result': 'string'},
    }
    if role not in fields:
        raise ContractError('No output schema for role')
    return {'type': 'object', 'properties': {key: {'type': value} for key, value in fields[role].items()},
            'required': list(fields[role]), 'additionalProperties': True}


def render_attempt(catalog, name, values, context):
    parts = [{'version': asdict(catalog[name]), 'variables': values}]
    text = render(catalog[name], values)
    role = ROLES[name]
    if role in {'planner', 'reviewer'}:
        routing = {'POLICY_JSON': freeze({'models': context.policy.executor_models, 'efforts': context.policy.executor_efforts})}
        text += '\n' + render(catalog['executor-routing'], routing)
        parts.append({'version': asdict(catalog['executor-routing']), 'variables': routing})
    schema = output_schema(role)  # Fixed motor contract; the editor cannot weaken it.
    text += '\nReturn exactly one JSON object, without Markdown fences. JSON Schema:\n' + freeze(schema)
    snapshot = {'parts': parts, 'output_schema': schema, 'schema_sha256': digest(freeze(schema)),
                'document_references': [context.next_steps_file, context.state_file],
                'rendered': text, 'rendered_sha256': digest(text)}
    return text, freeze(snapshot)

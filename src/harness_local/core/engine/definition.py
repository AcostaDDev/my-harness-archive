"""H6.5 (D072 §5.1, D073): creación y planificación conversacionales. Biblioteca estándar, sin efectos.

Dos conversaciones sobre la infraestructura del chat (D035): `definition` (proyecto nuevo, desde un
brief) y `phase_planning` (plan de la fase siguiente). Cada turno es una invocación nueva, de solo
lectura, del revisor con el contexto congelado al encolarlo. La salida tiene un esquema fijo; una
salida inválida detiene el turno sin fallback ni reintento. El agente nunca escribe: los borradores
los escribe el harness al aplicar una propuesta confirmada, con CAS sobre el hash leído en el turno.
La aceptación es una vista previa determinista que lleva al bootstrap D037 con la plantilla v2.
"""

from dataclasses import asdict, replace
import hashlib
import json
from pathlib import PurePosixPath
import re

from harness_local.core.engine.chat import _text, _texts, digest
from harness_local.core.engine.context import policy_payload
from harness_local.core.engine.contracts import (
    ContractError, IncompleteContract, Selection, context_snapshot, freeze, invoke_agent, stop_history,
)
from harness_local.core.engine.documents import (
    ANY_MARKER, MAX_DOCUMENT_BYTES, Layout, _fields, _first, blocks, budget_warnings, decision_index, inline,
    parse_roadmap, phase_data, plan_tasks, render_decisions, render_next_steps, render_roadmap, render_state,
    protected_write, replace_block, require_layout, skeleton,
)
from harness_local.core.engine.phases import phase_definition
from harness_local.core.engine.planning import FIELD_NAMES, bullet_items, deterministic_task, section
from harness_local.core.engine.prompts import dump_catalog, render_attempt

MAX_BRIEF_BYTES = 256 * 1024
# Borradores congelados en un turno: todos, íntegros; por encima, el turno no se encola.
MAX_CONTEXT_DRAFT_BYTES = 2 * 1024 * 1024
MAX_DRAFTS = 20
MAX_QUESTIONS = 30
MAX_PENDING = 30
DRAFT_NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,99}\.md')
KINDS = {'definition': ('define-project', 'definition'), 'phase_planning': ('plan-phase', 'planning')}
TEMPLATE = {'name': 'project-definition', 'version': '3'}  # 3: plantilla unificada D088


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def brief(text) -> dict:
    """Markdown del usuario congelado con su hash. No se interpretan comandos, rutas ni selecciones."""
    if not isinstance(text, str) or not text.strip() or '\0' in text:
        raise ValueError('The brief must be non-empty, NUL-free Markdown text')
    size = len(text.encode('utf-8'))
    if size > MAX_BRIEF_BYTES:
        raise ValueError(f'The brief exceeds {MAX_BRIEF_BYTES // 1024} KiB')
    return {'content': text, 'sha256': text_hash(text), 'size': size}


def question_id(text: str) -> str:
    return hashlib.sha256(' '.join(text.split()).encode('utf-8')).hexdigest()


# --- rutas de borrador -------------------------------------------------------------------------


def definition_layout(context) -> Layout:
    target = require_layout(context)
    if target.docs in ('', '.') or target.docs.startswith('/'):
        raise ValueError('The definition requires STATE and NEXT_STEPS inside a documentation folder')
    if '.git' in PurePosixPath(target.docs).parts:
        raise ValueError('The documentation folder cannot be Git metadata')
    return target


def fixed_drafts(target: Layout) -> tuple[str, ...]:
    """Rutas de la plantilla v2 de D088 (`skeleton`); ni el título ni los comandos cambian las rutas."""
    return tuple(sorted(skeleton(target, 'x')))


def required_documents(target: Layout) -> tuple[str, ...]:
    return (target.readme, target.specification, target.architecture, *target.phase_documents)


def draft_directories(target: Layout) -> frozenset[str]:
    parts = target.docs.split('/')
    return frozenset(['/'.join(parts[:n]) for n in range(1, len(parts) + 1)] + [target.flows_dir])


def allowed_draft(target: Layout, path: str) -> bool:
    """Solo la plantilla de D088 y `flows/*.md`; cualquier otro archivo es ajeno."""
    if not isinstance(path, str):
        return False
    if path in fixed_drafts(target):
        return True
    folder = target.flows_dir
    return path.startswith(folder + '/') and DRAFT_NAME.fullmatch(path[len(folder) + 1:]) is not None


def allowed_drafts_view(target: Layout) -> dict:
    return {'fixed': list(fixed_drafts(target)), 'patterns': [f'{target.flows_dir}/*.md'],
            'required': list(required_documents(target))}


def _block_names(target: Layout, path: str) -> set[str]:
    return {target.state: {'state'}, target.next_steps: {'state'}, target.roadmap: {'roadmap'},
            target.decisions: {'decisions'}}.get(path, set())


# --- salidas estructuradas ---------------------------------------------------------------------


def _questions(value) -> list[dict]:
    if not isinstance(value, list) or len(value) > MAX_QUESTIONS:
        raise ContractError(f'Questions must be a list of at most {MAX_QUESTIONS} items')
    result, seen = [], set()
    for item in value:
        if not isinstance(item, dict) or set(item) != {'text', 'blocking'} or type(item['blocking']) is not bool:
            raise ContractError('Each question must contain exactly text and a boolean blocking flag')
        text = _text(item['text'], 'question', limit=4000)
        if question_id(text) in seen:
            raise ContractError('Duplicate question')
        seen.add(question_id(text))
        result.append({'id': question_id(text), 'text': text, 'blocking': item['blocking']})
    return result


def _content(value, name) -> str:
    if not isinstance(value, str) or not value.strip() or '\0' in value:
        raise ContractError(f'{name} must be non-empty, NUL-free text')
    if len(value.encode('utf-8')) > MAX_DOCUMENT_BYTES:
        raise ContractError(f'{name} exceeds 512 KiB')
    return value


def validate_definition_result(data, target: Layout) -> dict:
    """Esquema fijo: respuesta, preguntas, borradores completos por documento y pendientes; nada más."""
    if not isinstance(data, dict) or set(data) != {'answer', 'questions', 'drafts', 'pending'}:
        raise ContractError('Definition result must contain exactly answer, questions, drafts and pending')
    drafts = data['drafts']
    if not isinstance(drafts, list) or len(drafts) > MAX_DRAFTS:
        raise ContractError(f'Drafts must be a list of at most {MAX_DRAFTS} items')
    result, paths = [], set()
    for item in drafts:
        if not isinstance(item, dict) or set(item) != {'path', 'content', 'reason'}:
            raise ContractError('Each draft must contain exactly path, content and reason')
        if not allowed_draft(target, item['path']):
            raise ContractError(f"Draft path {item['path']!r} is outside the v2 template, architecture/ and decisions/")
        if item['path'] in paths:
            raise ContractError('Each document may be proposed once per turn')
        paths.add(item['path'])
        result.append({'path': item['path'], 'content': _content(item['content'], 'Draft content'),
                       'reason': _text(item['reason'], 'draft reason', limit=4000)})
    return {'answer': _text(data['answer'], 'answer'), 'questions': _questions(data['questions']),
            'drafts': result, 'pending': _texts(data['pending'], 'pending items', limit=MAX_PENDING)}


def validate_plan(content: str, code: str) -> list[tuple[str, str]]:
    """Plan NEXT_STEPS de la fase siguiente: tareas con su prefijo y solo el bloque `managed-state`."""
    if set(blocks(content)) - {'state'}:
        raise ValueError('The plan may contain only the managed-state block of NEXT_STEPS')
    tasks = plan_tasks(content, code)
    if not tasks:
        raise ValueError(f'The plan of {code} needs at least one task heading')
    return tasks


def validate_planning_result(data, following: str | None) -> dict:
    if not isinstance(data, dict) or set(data) != {'answer', 'questions', 'plan', 'pending'}:
        raise ContractError('Planning result must contain exactly answer, questions, plan and pending')
    plan = data['plan']
    if plan is not None:
        if following is None:
            raise ContractError('ROADMAP has no further phase; the plan must be null')
        if not isinstance(plan, dict) or set(plan) != {'content', 'reason'}:
            raise ContractError('The plan must contain exactly content and reason')
        content = _content(plan['content'], 'Plan content')
        try:
            validate_plan(content, following)
        except ValueError as exc:
            raise ContractError(str(exc)) from exc
        plan = {'content': content, 'reason': _text(plan['reason'], 'plan reason', limit=4000)}
    return {'answer': _text(data['answer'], 'answer'), 'questions': _questions(data['questions']), 'plan': plan,
            'pending': _texts(data['pending'], 'pending items', limit=MAX_PENDING)}


# --- turno -------------------------------------------------------------------------------------


def planning_turn(context, history, snapshot: dict, agents, observe, journal, catalog):
    """Una invocación con la petición congelada; lo observado (borradores o checkout) no puede cambiar."""

    def done(history, status, reasons, *, result=None, observed=None):
        return replace(history, status='completed', stop=None) if status == 'ANSWERED' else history, {
            'status': status, 'reasons': list(reasons), 'result': result, 'observed': observed}

    kind = snapshot['kind']
    template, role = KINDS[kind]
    if digest(snapshot['context']) != snapshot['context_sha256']:
        raise ContractError('Frozen planning context changed after it was queued')
    journal.checkpoint(history, kind)
    try:
        before = observe()
    except Exception as exc:
        reason = f'Target could not be observed before the turn: {type(exc).__name__}: {exc}'
        return done(stop_history(history, kind, reason), 'FAILED', [reason])
    if snapshot.get('observed') is not None and before != snapshot['observed']:
        # La CAS de las propuestas usa los hashes congelados: si ya no coinciden, ni se invoca al agente.
        reason = 'Drafts changed after the message was queued; send the message again'
        return done(stop_history(history, kind, reason), 'FAILED', [reason], observed={'before': before})
    try:
        catalog_json = dump_catalog(catalog)
        prompt, prompt_snapshot = render_attempt(catalog, template, {
            'CONTEXT_JSON': freeze(snapshot['context']), 'MESSAGE': snapshot['message']}, context)
    except (ValueError, KeyError, TypeError) as exc:
        return done(stop_history(history, 'prompts', str(exc)), 'FAILED', [str(exc)])
    history = replace(history, prompt_catalog_json=catalog_json)
    selection = Selection(context.policy.planner_model, context.policy.planner_effort,
                          f'Explicit planner policy for the read-only {kind.replace("_", " ")} conversation')
    history, data = invoke_agent(context, history, agents, role, selection, prompt, journal,
                                 prompt_snapshot_json=prompt_snapshot)
    try:
        after = observe()
    except Exception as exc:
        reason = f'Target could not be re-observed after the turn: {type(exc).__name__}: {exc}'
        return done(stop_history(history, kind, reason) if history.stop is None else history, 'FAILED', [reason],
                    observed={'before': before, 'after': None})
    observed = {'before': before, 'after': after, 'unchanged': after == before}
    if after != before:
        reason = 'The target changed during a read-only turn; the answer and its proposals are discarded'
        return done(stop_history(history, kind, reason) if history.stop is None else history, 'FAILED', [reason],
                    result=data, observed=observed)
    if data is None:
        return done(history, 'FAILED', [history.stop.reason], observed=observed)
    try:
        if kind == 'definition':
            result = validate_definition_result(data, definition_layout(context))
        else:
            following = snapshot['context']['next']
            result = validate_planning_result(data, following['code'] if following else None)
    except ContractError as exc:
        return done(stop_history(history, kind, str(exc)), 'FAILED', [str(exc)], result=data, observed=observed)
    return done(history, 'ANSWERED', [], result=result, observed=observed)


# --- aceptación --------------------------------------------------------------------------------


def _task_fields(text: str, task_id: str) -> dict:
    raw = _fields('\n'.join(section(text, rf'^##\s+{re.escape(task_id)}\s+[—-].*$').splitlines()[1:]))
    return {key: _first(raw, names) for key, names in FIELD_NAMES.items()}


def template_identity(target: Layout) -> dict:
    sha = hashlib.sha256(freeze({'skeleton': skeleton(target, '{title}'), 'allowed': allowed_drafts_view(target)})
                         .encode('utf-8')).hexdigest()
    return {**TEMPLATE, 'sha256': sha, 'id': f"{TEMPLATE['name']}:{TEMPLATE['version']}:{sha}"}


def render_definition(conversation: dict, documents: list[dict]) -> str:
    """Resumen mecánico de la conversación desde SQLite; texto libre escapado en línea."""
    lines = ['# Definición del proyecto', '',
             'Generado por Harness Local desde SQLite al aceptar la definición (D072). Instantánea inmutable: '
             'la conversación completa sigue en SQLite.', '',
             f"**Conversación:** `{conversation['id']}` · **Título:** {inline(conversation['title'])}",
             f"**Brief:** [BRIEF.md](BRIEF.md) · `{conversation['brief']['sha256'][:12]}` "
             f"({conversation['brief']['size']} bytes)", '', '## Turnos', '',
             '| Turno | Estado | Mensaje | Respuesta | Borradores propuestos |', '|---|---|---|---|---|']
    for turn in conversation['turns']:
        lines.append(f"| {turn['number']} | {inline(turn['status'])} | {inline(turn['message'], 200)} "
                     f"| {inline(turn.get('answer'), 300)} | {len(turn.get('drafts') or [])} |")
    if not conversation['turns']:
        lines.append('| — | sin turnos | — | — | — |')
    lines += ['', '## Borradores aplicados y ediciones', '']
    lines += [f"- {inline(entry['path'])}: "
              + (f"propuesta {entry['proposal_number']} del turno {entry['turn_number']}"
                 if entry['source'] == 'proposal' else 'edición del usuario por API')
              + f" ({_short(entry.get('before'))} → {_short(entry.get('after'))})"
              for entry in conversation['log']] or ['- ninguno (borradores escritos solo por el usuario)']
    lines += ['', '## Preguntas del último turno', '']
    lines += [f"- {inline(q['text'])} — " + ('aplazada: ' + inline(q['deferred']['reason']) if q.get('deferred')
                                              else 'bloqueante' if q['blocking'] else 'no bloqueante')
              for q in conversation['questions']] or ['- ninguna']
    lines += ['', '## Pendientes declarados en el último turno', '']
    lines += [f'- {inline(item)}' for item in conversation['pending']] or ['- ninguno']
    lines += ['', '## Documentos aceptados', '', '| Documento | SHA-256 | Origen |', '|---|---|---|']
    lines += [f"| {inline(doc['path'])} | `{doc['sha256'][:12]}` | {inline(ORIGINS[doc['origin']])} |"
              for doc in documents]
    return '\n'.join(lines) + '\n'


ORIGINS = {'draft': 'borrador', 'draft+blocks': 'borrador con bloques regenerados',
           'template': 'plantilla v2', 'archive': 'archivo de la definición'}


def _short(value) -> str:
    return 'ausente' if value is None else f'`{value[:12]}`'


def acceptance(context, conversation: dict, inspection: dict, texts: dict[str, str]) -> dict:
    """Vista previa determinista de la aceptación: bloqueos o los archivos íntegros del commit raíz.

    `conversation`: snapshot SQLite (brief, turnos, preguntas abiertas con aplazamientos, pendientes,
    registro de borradores). `inspection`: borradores, archivos ajenos e inválidos del destino.
    `texts`: contenido de cada borrador, con el hash de la inspección."""
    target = definition_layout(context)
    blockers, warnings = [], []
    if inspection['import_required']:
        blockers.append('The target belongs to a Git repository or contains .git: use the import flow')
    if inspection['foreign']:
        blockers.append('Files outside the definition drafts block the acceptance (import flow): '
                        + ', '.join(inspection['foreign']) + (' …' if inspection.get('foreign_truncated') else ''))
    if inspection['invalid']:
        blockers.append('Drafts must be UTF-8, NUL-free, not executable and at most 512 KiB: '
                        + ', '.join(inspection['invalid']))
    missing = [path for path in required_documents(target) if path not in texts]
    if missing:
        blockers.append('Required documents are missing: ' + ', '.join(missing))
    for path, text in sorted(texts.items()):
        try:
            names = set(blocks(text))
        except ValueError as exc:
            blockers.append(f'{path}: {exc}')
            continue
        if names - _block_names(target, path):
            blockers.append(f'{path} contains managed blocks that belong to another document')
    if target.decisions in texts:
        try:
            decision_index(texts[target.decisions])
        except ValueError as exc:
            blockers.append(f'DECISIONS: {exc}')
    entry, tasks = None, []
    if target.roadmap in texts:
        try:
            entries = parse_roadmap(texts[target.roadmap])
        except ValueError as exc:
            entries = []
            blockers.append(f'ROADMAP: {exc}')
        if not entries:
            blockers.append('ROADMAP needs at least one phase section «## PNNN — título»')
        elif entries[0]['code'] != 'P001':
            blockers.append('The first ROADMAP phase must be P001')
        else:
            entry = entries[0]
            if not entry['objective'] or not entry['exit_criteria']:
                blockers.append('P001 needs an objective and at least one exit criterion in ROADMAP')
                entry = None
    if target.next_steps in texts:
        try:
            tasks = plan_tasks(texts[target.next_steps], 'P001')
        except ValueError as exc:
            blockers.append(f'NEXT_STEPS: {exc}')
        else:
            if not tasks:
                blockers.append('NEXT_STEPS needs at least one P001-TNNN task')
    first_task = None
    if tasks:
        task_id = tasks[0][0]
        fields = _task_fields(texts[target.next_steps], task_id)
        if not fields['objective'] or not bullet_items(fields['acceptance_criteria']):
            blockers.append(f'{task_id} needs an objective and acceptance criteria')
        elif context.policy.planning_mode != 'agent':
            try:
                first_task = json.loads(deterministic_task(context, task_id, 'P001', texts[target.next_steps]))
            except (IncompleteContract, ContractError) as exc:
                if context.policy.planning_mode == 'deterministic':
                    blockers.append(f'{task_id} does not satisfy the deterministic planning mode: {exc}')
        if first_task is None:
            first_task = {'task_id': task_id, 'title': tasks[0][1], 'planner': 'agent'}
    open_blocking = [q for q in conversation['questions'] if q['blocking'] and not q.get('deferred')]
    if open_blocking:
        blockers.append('Blocking questions remain open; answer them in a turn or defer them explicitly: '
                        + '; '.join(q['text'] for q in open_blocking))
    paths = sorted({*texts, *fixed_drafts(target)} | {f'{target.archive("P000")}/{name}'
                                                      for name in ('BRIEF.md', 'DEFINITION.md')})
    protected = [path for path in paths if protected_write(context, path)]
    if protected:
        blockers.append('Paths protected by the project profile: ' + ', '.join(protected))
    warnings += [f'Pendiente declarado por el revisor: {item}' for item in conversation['pending']]
    base = {'template': template_identity(target), 'input': {'conversation_id': conversation['id']},
            'definition': {'conversation_id': conversation['id'], 'conversation_version': conversation['version'],
                           'brief_sha256': conversation['brief']['sha256'], 'turns': len(conversation['turns']),
                           'drafts': dict(sorted(inspection['drafts'].items())),
                           'questions': conversation['questions'], 'pending': conversation['pending'],
                           'allowed': allowed_drafts_view(target)},
            'context_sha256': hashlib.sha256(context_snapshot(context).encode()).hexdigest(),
            'preparation': [asdict(c) for c in context.profile.preparation],
            'validations': [asdict(c) for c in context.profile.validations],
            'policy': policy_payload(context.policy), 'profile': context.profile.name}
    if blockers or entry is None:
        return {**base, 'documents': [], 'phase': None, 'first_task': None, 'task_text': None,
                'blockers': blockers or ['ROADMAP is missing'], 'warnings': warnings}
    definition = phase_definition(context, phase_data(target, entry, tasks))
    fresh = {'phase': {'code': 'P001', 'status': 'ACTIVE', 'objective': entry['objective']},
             'tasks': [{'task_id': task, 'status': None, 'planned': True} for task, _ in tasks],
             'open_questions': [], 'latest_check': None}
    rows = [{'code': item['code'], 'title': item['title'],
             **({'status': 'ACTIVE', 'tag': item['tag']} if item['code'] == 'P001' else {})}
            for item in parse_roadmap(texts[target.roadmap])]
    regenerated = {
        target.state: replace_block(texts[target.state], render_state(fresh)),
        target.next_steps: replace_block(texts[target.next_steps], render_next_steps(fresh)),
        target.roadmap: replace_block(texts[target.roadmap], render_roadmap(rows), 'roadmap'),
        target.decisions: replace_block(texts[target.decisions], render_decisions(decision_index(texts[target.decisions])),
                                        'decisions'),
    }
    # D088: AGENTS, CLAUDE, GEMINI y DDBB-DIAGRAM no redactados salen de la plantilla con el título y los
    # comandos del perfil congelado.
    template = skeleton(target, conversation['title'],
                        preparation=[command.argv for command in context.profile.preparation],
                        validations=[command.argv for command in context.profile.validations])
    documents = []
    for path in sorted({*texts, *(p for p in template if p not in required_documents(target))}):
        if path in texts:
            content = regenerated.get(path, texts[path])
            origin = 'draft+blocks' if content != texts[path] else 'draft'
            before = inspection['drafts'][path]
        else:
            content, origin, before = template[path], 'template', None
        documents.append({'path': path, 'content': content, 'sha256': text_hash(content), 'before_sha256': before,
                          'origin': origin})
    archive = target.archive('P000')
    brief_doc = conversation['brief']['content']
    record = render_definition(conversation, documents)
    documents += [{'path': f'{archive}/BRIEF.md', 'content': brief_doc, 'sha256': text_hash(brief_doc),
                   'before_sha256': None, 'origin': 'archive'},
                  {'path': f'{archive}/DEFINITION.md', 'content': record, 'sha256': text_hash(record),
                   'before_sha256': None, 'origin': 'archive'}]
    documents.sort(key=lambda doc: doc['path'])
    for doc in documents:
        if len(doc['content'].encode('utf-8')) > MAX_DOCUMENT_BYTES:
            raise ValueError(f"{doc['path']} would exceed 512 KiB")
        if doc['origin'] in ('template', 'archive') and ANY_MARKER.search(doc['content']) and doc['path'] != f'{archive}/BRIEF.md':
            raise ValueError(f"{doc['path']} unexpectedly contains managed markers")
    warnings += budget_warnings(target, {doc['path']: doc['content'] for doc in documents})
    return {**base, 'documents': documents, 'phase': definition, 'first_task': first_task,
            'task_text': regenerated[target.next_steps], 'blockers': [], 'warnings': warnings}

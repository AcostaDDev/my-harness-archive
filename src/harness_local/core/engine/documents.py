"""D072/H6.3 y D088: contrato documental por fase (layout v2 unificado). Biblioteca estándar, sin efectos.

SQLite manda en el estado operativo y Markdown en la intención. Los bloques gestionados son
proyecciones deterministas de SQLite o de archivos: se regeneran y se comparan byte a byte,
nunca se vuelven a leer como fuente. Los valores libres se escapan como texto en línea, de modo
que no pueden abrir encabezados, fences, HTML ni marcadores.
"""

from dataclasses import dataclass
import re
from pathlib import PurePosixPath
import shlex

from harness_local.core.engine.planning import FIELD_RE, TASK_RE, backticked, bullet_items, collapse

MAX_DOCUMENT_BYTES = 512 * 1024
BLOCK_REASON = 'Managed documentation blocks (D072)'
BLOCK_NAMES = ('state', 'roadmap', 'decisions')
PHASE_CODE = re.compile(r'P\d{3}')
PHASE_RE = re.compile(r'^##\s+(P\d{3})\s+[—-]\s+(.+?)\s*$', re.MULTILINE)
# D088: el índice de DECISIONS sale de sus propios encabezados y de la primera línea «Estado:» de cada uno.
DECISION_HEADING = re.compile(r'^##\s+D(\d{3,})\s+[—-]\s+(.+?)\s*$', re.MULTILINE)
DECISION_STATUS = re.compile(r'^(?:\*\*)?(?:Estado|Status)(?::\*\*|\*\*:|:)[ \t]*(.*)$', re.IGNORECASE)
BASE_HEADING = re.compile(r'^##\s+(?:Base acumulada|Accumulated baseline)\s*$', re.MULTILINE)
LEVEL_TWO = re.compile(r'^##\s', re.MULTILINE)
ANY_MARKER = re.compile(r'<!--\s*harness-local:managed-')
# Avisos, nunca truncado: un documento que los supera pide compactación en la reconciliación.
BUDGETS = {'state': 24 * 1024, 'base': 12 * 1024, 'next_steps': 48 * 1024}
SUMMARY_LIMIT = 600
ROADMAP_FIELDS = {'objective': ('objetivo', 'objective'), 'exit_criteria': ('criterios de salida', 'exit criteria'),
                  'dependencies': ('dependencias', 'dependencies'), 'out_of_scope': ('fuera de alcance', 'out of scope'),
                  'tag': ('tag',)}
# Límites de la plantilla de instrucciones (D088 punto 1), comprobados por test.
MAX_AGENTS_LINES = 60
MAX_WRAPPER_LINES = 15
MAX_TEMPLATE_COMMANDS = 12


@dataclass(frozen=True)
class Layout:
    """Rutas del layout v2 unificado (D088): README y archivos de instrucciones en la raíz; el resto bajo el
    directorio de STATE/NEXT_STEPS."""

    docs: str
    state: str
    next_steps: str
    readme: str = 'README.md'
    agents: str = 'AGENTS.md'
    claude: str = 'CLAUDE.md'
    gemini: str = 'GEMINI.md'

    def doc(self, name: str) -> str:
        return f'{self.docs}/{name}'

    @property
    def specification(self):
        return self.doc('SPECIFICATION.md')

    @property
    def architecture(self):
        return self.doc('ARCHITECTURE.md')

    @property
    def roadmap(self):
        return self.doc('ROADMAP.md')

    @property
    def decisions(self):
        return self.doc('DECISIONS.md')

    @property
    def ddbb_diagram(self):
        return self.doc('DDBB-DIAGRAM.md')

    @property
    def flows_dir(self):
        return self.doc('flows')

    @property
    def phase_dir(self):
        return self.doc('phase')

    @property
    def archive_dir(self):
        return self.doc('archive')

    def archive(self, code: str) -> str:
        if not PHASE_CODE.fullmatch(code):
            raise ValueError('Layout v2 phases use codes PNNN')
        return f'{self.archive_dir}/phase-{code[1:]}'

    @property
    def phase_documents(self) -> tuple[str, ...]:
        """Documentos ligados a la fase (READY y base adoptada): planificación y seguimiento."""
        return (self.roadmap, self.decisions, self.state, self.next_steps)

    @property
    def product_documents(self) -> tuple[str, ...]:
        return (self.readme, self.specification, self.architecture, self.ddbb_diagram)

    @property
    def instructions(self) -> tuple[str, ...]:
        """Archivos de instrucciones para agentes: AGENTS canónico y envoltorios por proveedor."""
        return (self.agents, self.claude, self.gemini)

    @property
    def harness_owned(self) -> tuple[str, ...]:
        """Ningún ejecutor normal los edita; la reconciliación edita su prosa salvo el índice."""
        return (self.state, self.next_steps, self.roadmap, self.decisions)

    @property
    def folders(self) -> tuple[str, ...]:
        return (self.flows_dir, self.phase_dir)

    def archived(self, path: str) -> bool:
        return path == self.archive_dir or path.startswith(self.archive_dir + '/')

    def editable(self, path: str) -> bool:
        """Documentos editables por el usuario mediante una edición confirmada."""
        pure = PurePosixPath(path)
        if path == self.readme:
            return True
        return (pure.suffix == '.md' and path.startswith(self.docs + '/') and not self.archived(path)
                and '..' not in pure.parts)


def layout(context) -> Layout | None:
    if getattr(context, 'documents', None) != 'v2':
        return None
    return Layout(str(PurePosixPath(context.state_file).parent), context.state_file, context.next_steps_file)


def protected_write(context, path: str) -> bool:
    """¿Rechaza el perfil que el harness escriba `path` en una operación documental confirmada?

    D081: las rutas protegidas del perfil limitan al ejecutor y a los permisos que se le conceden. En v2, el
    contrato documental (README, archivos de instrucciones de la raíz, Markdown de la documentación y el archivo
    de fases) se escribe solo con una confirmación del usuario sobre el contenido exacto y tiene sus propias
    reglas, como la regeneración mecánica de bloques en cada commit de tarea. Fuera de ese contrato, y en v1, la
    protección del perfil se mantiene. D088: AGENTS, CLAUDE y GEMINI se escriben en la creación; su edición
    confirmada (`Layout.editable`) llega con P008-T003."""
    from harness_local.core.engine.evidence import matches
    target = layout(context)
    pure = PurePosixPath(path)
    if (target is not None and '..' not in pure.parts
            and (target.editable(path) or path in target.instructions
                 or (target.archived(path) and pure.suffix == '.md'))):
        return False
    return matches(path, context.profile.protected_paths)


def require_layout(context) -> Layout:
    value = layout(context)
    if value is None:
        raise ValueError('This operation requires the D072 document layout (documents = "v2")')
    return value


# --- bloques gestionados -----------------------------------------------------------------------


def markers(name: str) -> tuple[str, str]:
    return f'<!-- harness-local:managed-{name}:start -->', f'<!-- harness-local:managed-{name}:end -->'


def _span(text: str, name: str):
    begin, end = markers(name)
    if begin not in text and end not in text:
        return None
    if text.count(begin) != 1 or text.count(end) != 1:
        raise ValueError('Mechanical markers must occur exactly once as a pair')
    start, stop = text.index(begin), text.index(end)
    if stop < start or (start and text[start - 1] != '\n') or (
            stop + len(end) < len(text) and text[stop + len(end)] not in '\r\n'):
        raise ValueError('Mechanical markers must be ordered and occupy their own lines')
    if not text[start + len(begin):].startswith(('\r\n', '\n')) or (stop and text[stop - 1] != '\n'):
        raise ValueError('Mechanical markers must occupy their own lines')
    suffix = text[stop + len(end):]
    if suffix and not suffix.startswith(('\r\n', '\n')):
        raise ValueError('Mechanical markers must occupy their own lines')
    return start, stop + len(end)


def replace_block(text: str, body: str, name: str = 'state') -> str:
    """No normaliza ni interpreta la prosa exterior, incluidas sus terminaciones de línea."""
    begin, end = markers(name)
    block = begin + '\n' + body + end
    span = _span(text, name)
    if span is None:
        return text + ('\n' if text and not text.endswith('\n') else '') + block + '\n'
    return text[:span[0]] + block + text[span[1]:]


def blocks(text: str) -> dict[str, str]:
    """Bloques presentes, validados; cualquier otro marcador gestionado es un error."""
    found = {}
    for name in BLOCK_NAMES:
        span = _span(text, name)
        if span is not None:
            found[name] = text[span[0]:span[1]]
    if len(ANY_MARKER.findall(text)) != 2 * len(found):
        raise ValueError('Unknown or partial harness-local managed markers')
    return found


def without_blocks(text: str) -> str:
    for name in BLOCK_NAMES:
        span = _span(text, name)
        if span is not None:
            text = text[:span[0]] + markers(name)[0] + text[span[1]:]
    return text


# --- escape y renderizado ----------------------------------------------------------------------


def inline(value, limit: int | None = None) -> str:
    """Texto en una sola línea: sin saltos, HTML, fences, tablas ni énfasis interpretables."""
    if value is None:
        return '—'
    text = ' '.join(str(value).split())
    if not text:
        return '—'
    if limit is not None and len(text) > limit:
        text = text[:limit].rstrip() + ' … (recortado; texto completo en el historial de SQLite)'
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return re.sub(r'([\\`*_\[\]|#~])', r'\\\1', text)


def _code(value) -> str:
    return '—' if not value else f'`{value[:12]}`'


def validation_counts(report) -> dict | None:
    """OK/KO de una validación: comandos y, si hay reportes JUnit legibles, casos por resultado."""
    if report is None:
        return None
    passed = sum(1 for entry in report.entries if entry.result.passed)
    counts = {'commands_passed': passed, 'commands_failed': len(report.entries) - passed}
    cases = None
    for entry in report.entries:
        for item in entry.reports:
            if item.status not in ('complete', 'partial'):
                continue
            cases = cases or {'passed': 0, 'failed': 0, 'error': 0, 'skipped': 0}
            for case in item.cases:
                cases[case.result if case.result in cases else 'error'] += 1
    return {**counts, 'cases': cases}


def tests_label(tests) -> str:
    if not tests:
        return '—'
    parts = []
    cases = tests.get('cases')
    if cases:
        parts.append(f"{cases.get('passed', 0)} OK · {cases.get('failed', 0) + cases.get('error', 0)} KO"
                     + (f" · {cases['skipped']} omitidos" if cases.get('skipped') else ''))
    total = tests.get('commands_passed', 0) + tests.get('commands_failed', 0)
    if total:
        parts.append(f"comandos {tests.get('commands_passed', 0)}/{total} OK")
    return ' · '.join(parts) or '—'


def _questions(snapshot) -> list[str]:
    items = snapshot.get('open_questions') or []
    return ['**Preguntas abiertas:**'] + ([f'- {inline(item)}' for item in items] or ['- ninguna'])


def _phase_line(phase) -> list[str]:
    if phase is None:
        return ['**Fase activa:** ninguna (roadmap completado o sin instalar).']
    lines = [f"**Fase:** {inline(phase['code'])} · estado {inline(phase['status'])}"]
    if phase.get('objective'):
        lines.append(f"**Objetivo:** {inline(phase['objective'])}")
    return lines


def render_state(snapshot: dict) -> str:
    lines = ['Estado gestionado por Harness Local desde SQLite (D072). No editar dentro de este bloque.', '']
    lines += _phase_line(snapshot['phase'])
    lines += ['', '| Tarea | Estado | Revisión | Commit | Tests |', '|---|---|---|---|---|']
    tasks = snapshot['tasks']
    for task in tasks:
        commit = 'este commit' if task.get('committing') else _code(task.get('commit'))
        lines.append(f"| {inline(task['task_id'])} | {inline(task.get('status'))} | {inline(task.get('verdict'))} "
                     f"| {commit} | {inline(tests_label(task.get('tests')))} |")
    if not tasks:
        lines.append('| — | sin tareas | — | — | — |')
    summaries = [task for task in tasks if task.get('summary')]
    if summaries:
        lines += ['', '**Resumen del ejecutor por tarea:**']
        lines += [f"- {inline(task['task_id'])}: {inline(task['summary'], SUMMARY_LIMIT)}" for task in summaries]
    lines += [''] + _questions(snapshot)
    check = snapshot.get('latest_check')
    if check:
        reasons = '; '.join(check.get('reasons') or []) or 'sin motivos registrados'
        lines += ['', f"**Último check:** {inline(check['status'])} — {inline(reasons, SUMMARY_LIMIT)}"]
    return '\n'.join(lines) + '\n'


def render_next_steps(snapshot: dict) -> str:
    lines = ['Estado del plan gestionado por Harness Local desde SQLite (D072). No editar dentro de este bloque.', '']
    lines += _phase_line(snapshot['phase'])
    planned = [task for task in snapshot['tasks'] if task.get('planned', True)]
    pending = next((task['task_id'] for task in planned if not task.get('commit') and not task.get('committing')), None)
    if snapshot['phase'] is not None:
        lines.append('**Siguiente tarea:** ' + (inline(pending) if pending else 'ninguna; todas tienen commit aceptado'))
    lines += ['', '| Tarea | Estado | Commit |', '|---|---|---|']
    for task in planned:
        commit = 'este commit' if task.get('committing') else _code(task.get('commit'))
        lines.append(f"| {inline(task['task_id'])} | {inline(task.get('status') or 'pendiente')} | {commit} |")
    if not planned:
        lines.append('| — | sin tareas | — |')
    extra = [task for task in snapshot['tasks'] if not task.get('planned', True)]
    if extra:
        lines += ['', '**Tareas añadidas fuera del plan:**']
        lines += [f"- {inline(task['task_id'])}: {inline(task.get('status'))}" for task in extra]
    lines += [''] + _questions(snapshot)
    return '\n'.join(lines) + '\n'


STATUS_LABELS = {None: 'pendiente', 'ACTIVE': 'activa', 'CLOSED': 'cerrada', 'ABANDONED': 'abandonada',
                 'CHECKING': 'en check', 'CLOSING': 'cerrándose', 'READY_TO_CLOSE': 'lista para cerrar',
                 'NEEDS_RECONCILIATION': 'requiere reconciliación', 'BLOCKED': 'bloqueada'}


def render_roadmap(phases: list[dict]) -> str:
    lines = ['Estado de las fases gestionado por Harness Local desde SQLite (D072). No editar dentro de este bloque.',
             '', '| Fase | Título | Estado | Tag |', '|---|---|---|---|']
    for phase in phases:
        label = STATUS_LABELS.get(phase.get('status'), phase.get('status'))
        tag = f"`{phase['tag']}`" if phase.get('tag') and phase.get('status') == 'CLOSED' else '—'
        lines.append(f"| {inline(phase['code'])} | {inline(phase['title'])} | {inline(label)} | {tag} |")
    if not phases:
        lines.append('| — | sin fases | — | — |')
    return '\n'.join(lines) + '\n'


def render_decisions(entries: list[dict]) -> str:
    lines = ['Índice generado por Harness Local desde los encabezados de este archivo (D088). '
             'No editar dentro de este bloque.', '', '| Decisión | Título | Estado |', '|---|---|---|']
    for entry in entries:
        lines.append(f"| {inline(entry['id'])} | {inline(entry['title'])} | {inline(entry['status'], SUMMARY_LIMIT)} |")
    if not entries:
        lines.append('| — | sin decisiones | — |')
    return '\n'.join(lines) + '\n'


# --- lectura estructural de la intención -------------------------------------------------------


def _fields(body: str) -> dict[str, str]:
    raw: dict[str, str] = {}
    current = None
    for line in body.splitlines():
        match = FIELD_RE.match(line.strip())
        if match:
            current = match.group(1).strip().rstrip(':').lower()
            raw[current] = match.group(2).strip()
        elif current is not None:
            raw[current] += '\n' + line
    return raw


def _first(raw: dict, names) -> str:
    return next((raw[name].strip() for name in names if raw.get(name, '').strip()), '')


def _section_after(text: str, start: int) -> str:
    following = LEVEL_TWO.search(text, start)
    return text[start:following.start() if following else len(text)]


def parse_roadmap(text: str) -> list[dict]:
    """Fases `## PNNN — título` en orden del documento, con campos en español o inglés."""
    entries, seen = [], set()
    for match in PHASE_RE.finditer(text):
        code = match.group(1)
        if code in seen:
            raise ValueError(f'Duplicate roadmap phase {code}')
        seen.add(code)
        raw = _fields(_section_after(text, match.end()))
        criteria = bullet_items(_first(raw, ROADMAP_FIELDS['exit_criteria']))
        tag = _first(raw, ROADMAP_FIELDS['tag']).split('\n', 1)[0]
        entries.append({'code': code, 'title': collapse(match.group(2)),
                        'objective': collapse(_first(raw, ROADMAP_FIELDS['objective'])),
                        'exit_criteria': [collapse(item) for item in criteria],
                        'dependencies': collapse(_first(raw, ROADMAP_FIELDS['dependencies'])) or None,
                        'out_of_scope': collapse(_first(raw, ROADMAP_FIELDS['out_of_scope'])) or None,
                        'tag': (backticked(tag) or [collapse(tag)])[0] if tag else None})
    return entries


def plan_tasks(text: str, code: str | None = None) -> list[tuple[str, str]]:
    tasks = [(match.group(1), collapse(match.group(2))) for match in TASK_RE.finditer(text)]
    ids = [task for task, _ in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate task headings in NEXT_STEPS')
    if code is not None and any(not task.startswith(code + '-T') for task in ids):
        raise ValueError(f'Every NEXT_STEPS task must belong to phase {code}')
    return tasks


def decision_index(text: str | None) -> list[dict]:
    """D088: decisiones `## DNNN — título` de DECISIONS.md, con el estado de la primera línea `Estado:` de su
    sección (solo esa línea). El bloque gestionado no se lee. Una numeración repetida, también con otro
    relleno de ceros (D7 y D007), se rechaza: el índice no elige entre dos decisiones."""
    source = without_blocks(text or '')
    entries, seen = [], {}
    for match in DECISION_HEADING.finditer(source):
        number = int(match.group(1))
        identity = 'D' + match.group(1)
        if number in seen:
            raise ValueError(f'Duplicate decision number in DECISIONS: {seen[number]} and {identity}')
        seen[number] = identity
        status = None
        for line in _section_after(source, match.end()).splitlines():
            found = DECISION_STATUS.match(line.strip())
            if found:
                status = collapse(found.group(1)) or None
                break
        entries.append({'id': identity, 'title': collapse(match.group(2)), 'status': status})
    return sorted(entries, key=lambda item: int(item['id'][1:]))


def base_section(text: str) -> str | None:
    """Sección «Base acumulada» literal, sin un bloque gestionado que pudiera seguirla."""
    match = BASE_HEADING.search(text)
    if match is None:
        return None
    body = _section_after(text, match.end())
    end = match.end() + len(body)
    marker = ANY_MARKER.search(text, match.start(), end)
    return text[match.start():marker.start() if marker else end]


def phase_data(target: Layout, entry: dict, tasks: list[tuple[str, str]]) -> dict:
    """Datos de `PhaseCreate` derivados de ROADMAP §PNNN y de NEXT_STEPS; los valida `phase_definition`."""
    return {'code': entry['code'], 'objective': entry['objective'], 'exit_criteria': entry['exit_criteria'],
            'tasks': [task for task, _ in tasks], 'documents': list(target.phase_documents), 'tag': entry['tag']}


def managed_bodies(target: Layout, snapshot: dict, phases: dict,
                   texts: dict[str, str | None]) -> dict[str, tuple[str, str]]:
    """Cuerpo de cada bloque gestionado: STATE/NEXT_STEPS desde SQLite; ROADMAP e índice, además, desde disco."""
    bodies = {target.state: ('state', render_state(snapshot)), target.next_steps: ('state', render_next_steps(snapshot))}
    if texts.get(target.roadmap) is not None:
        rows = [{'code': entry['code'], 'title': entry['title'], **phases.get(entry['code'], {})}
                for entry in parse_roadmap(texts[target.roadmap])]
        bodies[target.roadmap] = ('roadmap', render_roadmap(rows))
    if texts.get(target.decisions) is not None:
        bodies[target.decisions] = ('decisions', render_decisions(decision_index(texts[target.decisions])))
    return bodies


def budget_warnings(target: Layout, texts: dict[str, str]) -> list[str]:
    warnings = []
    # D088: DECISIONS es un registro único sin presupuesto; los agentes leen solo las decisiones citadas.
    limits = ((target.state, 'state', 'STATE'), (target.next_steps, 'next_steps', 'NEXT_STEPS'))
    for path, key, label in limits:
        text = texts.get(path)
        if text is not None and len(text.encode('utf-8')) > BUDGETS[key]:
            warnings.append(f'{label} ocupa {len(text.encode("utf-8"))} bytes; presupuesto {BUDGETS[key]}: '
                            'compactar en la reconciliación')
    base = base_section(texts.get(target.state) or '')
    if base is not None and len(base.encode('utf-8')) > BUDGETS['base']:
        warnings.append(f'La base acumulada ocupa {len(base.encode("utf-8"))} bytes; presupuesto {BUDGETS["base"]}')
    return warnings


# --- archivo de fase ---------------------------------------------------------------------------


def render_review(code: str, check: dict | None, status: str) -> str:
    lines = [f'# Evaluación de cierre de {code}', '',
             'Generado por Harness Local desde SQLite al archivar la fase (D072). Instantánea inmutable.', '']
    if status != 'CLOSED' or not check:
        lines.append(f'La fase terminó como {inline(status)} sin un check READY que habilitara el cierre.')
        if check:
            lines.append(f"Último check registrado: {inline(check.get('status'))}.")
        return '\n'.join(lines) + '\n'
    result = check.get('result') or {}
    binding = (check.get('binding') or {})
    lines += [f"**Veredicto:** {inline(check.get('status'))} · **HEAD evaluado:** {_code(binding.get('head'))} "
              f"· **Vínculo READY:** {_code(check.get('binding_sha256'))}",
              f"**Resumen del revisor:** {inline(result.get('summary'))}", '',
              '## Criterios de salida', '', '| Criterio | Cumplido | Evidencia |', '|---|---|---|']
    for item in result.get('exit_criteria_results') or []:
        lines.append(f"| {inline(item.get('criterion'))} | {'sí' if item.get('passed') else 'no'} "
                     f"| {inline(item.get('evidence'))} |")
    validation = check.get('validation')
    if validation is not None:
        entries = validation.get('entries') or []
        passed = sum(1 for entry in entries if (entry.get('result') or {}).get('exit_code') == 0)
        lines += ['', f'**Validación de base:** {passed}/{len(entries)} comandos con salida 0.']
    return '\n'.join(lines) + '\n'


def render_summary(summary: dict) -> str:
    phase = summary['phase']
    lines = [f"# Resumen de la fase {phase['code']}", '',
             'Generado por Harness Local desde SQLite al archivar la fase (D072). Instantánea inmutable: '
             'la autoridad operativa sigue en SQLite.', '',
             f"**Título:** {inline(phase.get('title'))}",
             f"**Estado final:** {inline(phase['status'])} · **Tag:** "
             + (f"`{phase['tag']}`" if phase.get('tag') and phase['status'] == 'CLOSED' else '—')
             + f" · **Definición:** versión {phase['definition_number']}",
             f"**Objetivo:** {inline(phase['objective'])}", '', '**Criterios de salida:**']
    lines += [f'- {inline(item)}' for item in phase['exit_criteria']]
    # H6.4: las fases archivadas después de 0014 añaden tokens y turnos; las anteriores conservan su forma.
    consumption = summary.get('consumption')
    usage = (consumption or {}).get('by_task') or {}
    lines += ['', '## Tareas', '',
              '| Tarea | Estado | Revisión | Intentos por rol | Correcciones | Commit | Tests |'
              + (' Tokens | Turnos |' if consumption is not None else ''),
              '|---|---|---|---|---|---|---|' + ('---|---|' if consumption is not None else '')]
    for task in summary['tasks']:
        attempts = ', '.join(f'{role} {count}' for role, count in sorted((task.get('attempts') or {}).items())) or '—'
        lines.append(f"| {inline(task['task_id'])} | {inline(task.get('status') or 'sin run')} | {inline(task.get('verdict'))} "
                     f"| {inline(attempts)} | {inline(task.get('revisions'))} | {_code(task.get('commit'))} "
                     f"| {inline(tests_label(task.get('tests')))} |"
                     + (f" {inline(tokens_label(usage.get(task['task_id'])))} "
                        f"| {inline(turns_label(usage.get(task['task_id'])))} |" if consumption is not None else ''))
    if not summary['tasks']:
        lines.append('| — | sin tareas | — | — | — | — | — |' + (' — | — |' if consumption is not None else ''))
    extra = summary.get('extra_tasks') or []
    if extra:
        lines += ['', '## Tareas añadidas fuera del plan', '']
        lines += [f"- {inline(task['task_id'])}: {inline(task.get('status'))}, commit {_code(task.get('commit'))}"
                  for task in extra]
    lines += ['', '## Preguntas', '']
    questions = summary.get('questions') or []
    lines += [f"- {inline(q['text'])} — {inline(q['status'])}" + (f": {inline(q['answer'])}" if q.get('answer') else '')
              for q in questions] or ['- ninguna']
    lines += ['', '## Definición y enmiendas', '']
    lines += [f"- Versión {item['number']} ({inline(item['origin'])})" + (f": {inline(item['reason'])}" if item.get('reason') else '')
              for item in summary.get('definitions') or []]
    if consumption is not None:
        lines += ['', '## Consumo', '',
                  'Tokens reportados por el proveedor o derivados del uso por mensaje, sin sumar acumulados con '
                  'incrementales; «—» es ausencia, no cero. Turnos reportados (Claude) y derivados (elementos de '
                  'Codex) por separado. Coste equivalente API reportado: no es factura ni cuota. Excluye el chat.', '',
                  '| Rol | Intentos | Entrada sin caché | Caché leída | Caché escrita | Salida | Total | Turnos '
                  '| Coste equivalente API (USD) |', '|---|---|---|---|---|---|---|---|---|']
        rows = sorted((consumption.get('by_role') or {}).items()) + [('total', consumption['total'])]
        for role, entry in rows:
            cost = entry['cost_usd']['sum']
            lines.append(f"| {inline(role)} | {entry['attempts']} "
                         + ''.join(f"| {_measure(entry[name], entry['attempts'])} " for name in (
                             'uncached_input_tokens', 'cache_read_tokens', 'cache_write_tokens', 'output_tokens',
                             'total_tokens'))
                         + f"| {inline(turns_label(entry))} | {'—' if cost is None else f'{cost:.4f}'} |")
    lines += ['', 'Evaluación de cierre: [REVIEW.md](REVIEW.md).']
    return '\n'.join(lines) + '\n'


def _measure(value, attempts) -> str:
    """Suma con su cobertura: «—» si ningún intento la aporta (ausencia, no cero); «n (k/m)» si solo algunos."""
    if not value or value['sum'] is None:
        return '—'
    return f"{value['sum']}" + (f" ({value['attempts']}/{attempts})" if value['attempts'] != attempts else '')


def tokens_label(entry) -> str:
    if not entry or entry['total_tokens']['sum'] is None:
        return '—'
    covered, attempts = entry['total_tokens']['attempts'], entry['attempts']
    return f"{entry['total_tokens']['sum']}" + (f' ({covered}/{attempts} intentos)' if covered != attempts else '')


def turns_label(entry) -> str:
    if not entry:
        return '—'
    parts = [f"{entry[key]['sum']} {label}" for key, label in (('turns_reported', 'reportados'),
                                                              ('turns_derived', 'derivados'))
             if entry[key]['sum'] is not None]
    return ' · '.join(parts) or '—'


# --- plantilla documental v2 unificada (D088) -----------------------------------------------------


def _command_lines(commands) -> list[str]:
    """Una línea por argv, sin saltos; un argv que podría cerrar el bloque de código no se transcribe."""
    lines = []
    for argv in list(commands)[:MAX_TEMPLATE_COMMANDS]:
        line = ' '.join(shlex.join(list(argv)).split())
        lines.append('# (comando omitido: contiene tres acentos graves seguidos; ver el perfil)' if '```' in line else line)
    if len(commands) > MAX_TEMPLATE_COMMANDS:
        lines.append(f'# … y {len(commands) - MAX_TEMPLATE_COMMANDS} más declarados en el perfil')
    return lines


def render_agents(target: Layout, name: str, preparation=(), validations=()) -> str:
    """AGENTS.md canónico (≤60 líneas): discovery, reglas inquebrantables y comandos del perfil."""
    lines = [f'# {name} — instrucciones para agentes', '',
             f'Fuente canónica para agentes; `{target.claude}` y `{target.gemini}` la importan. Para personas, '
             f'`{target.readme}`.', '',
             '## Discovery al empezar una sesión', '',
             f'1. `{target.state}`: base acumulada y fase activa.',
             f'2. `{target.next_steps}`: tareas de la fase activa y siguiente tarea.',
             f'3. `{target.roadmap}`: sección de la fase activa.',
             f'4. `{target.specification}` y `{target.architecture}`: solo las secciones que afecten a la tarea.',
             f'5. `{target.decisions}`: las decisiones que cite la tarea; el índice, para buscar precedentes.',
             f'6. `{target.ddbb_diagram}` y `{target.flows_dir}/` si la tarea toca datos o flujos.',
             f'7. `{target.archive_dir}/` solo cuando un documento lo cite.', '',
             '## Reglas inquebrantables', '',
             '- No inventar fuera de la especificación ni de lo decidido. Ante una incongruencia entre documentos, '
             'o entre documentos y código, preguntar antes de decidir.',
             f'- Paridad: un cambio de modelos de datos actualiza `{target.ddbb_diagram}`; un cambio de flujo, '
             f'`{target.flows_dir}/`, en la misma tarea.',
             f'- STATE, NEXT_STEPS, ROADMAP, DECISIONS y `{target.archive_dir}/` los mantiene Harness Local: una '
             'tarea normal no los edita.',
             '- Las decisiones nuevas se proponen en la salida de la tarea; no se escriben en DECISIONS.',
             f'- Artefactos de trabajo de la fase en curso en `{target.phase_dir}/`.',
             '- Ningún secreto, credencial ni dato privado en el repositorio.', '',
             '## Comandos', '']
    preparation, validations = _command_lines(preparation), _command_lines(validations)
    if not preparation and not validations:
        lines.append('Sin comandos declarados por el perfil del proyecto.')
    for label, items in (('Preparación', preparation), ('Validación (tests, lint y tipos)', validations)):
        if items:
            lines += [f'{label}:', '', '```sh', *items, '```', '']
    return '\n'.join(lines).rstrip('\n') + '\n'


def render_wrapper(target: Layout, provider: str) -> str:
    """Envoltorio de proveedor (≤15 líneas) que importa AGENTS.md."""
    return (f'# {provider}\n\n@{target.agents}\n\nNotas para {provider}: ninguna todavía. Las instrucciones '
            f'comunes viven en `{target.agents}`.\n')


def skeleton(target: Layout, title: str, phase_title: str = 'Primera fase', *, preparation=(),
             validations=()) -> dict[str, str]:
    """Documentos base de D088 con bloques vacíos en su sitio; el contenido real lo fija la creación (H6.5).

    `preparation` y `validations`: argv del perfil para la sección de comandos de AGENTS. `flows/` y `phase/`
    no tienen archivo de plantilla."""
    name, first = inline(title), inline(phase_title)
    state_begin, state_end = markers('state')
    road_begin, road_end = markers('roadmap')
    dec_begin, dec_end = markers('decisions')
    return {
        target.agents: render_agents(target, name, preparation, validations),
        target.claude: render_wrapper(target, 'Claude Code'),
        target.gemini: render_wrapper(target, 'Gemini CLI'),
        target.readme: (f'# {name}\n\nQué es, para quién y qué problema resuelve.\n\n## Estado\n\n'
                        f'Fases y progreso en [ROADMAP]({target.roadmap}) y [STATE]({target.state}).\n\n'
                        '## Requisitos\n\n## Instalación\n\n## Uso\n\n## Tests\n\n## Documentación\n\n'
                        f'- [Especificación]({target.specification})\n- [Arquitectura]({target.architecture})\n'
                        f'- [Diagrama de datos]({target.ddbb_diagram})\n- [Decisiones]({target.decisions})\n'
                        f'- Instrucciones para agentes: [AGENTS]({target.agents})\n'),
        target.specification: (f'# Especificación — {name}\n\n## Problema\n\n## Usuarios\n\n## Alcance\n\n'
                               '## Requisitos\n\n## Reglas de negocio\n\n## Fuera de alcance\n'),
        target.architecture: (f'# Arquitectura — {name}\n\n## Stack\n\n## Componentes\n\n## Flujos\n\n'
                              'Diagramas por módulo o funcionalidad en `flows/`.\n\n## Persistencia\n\n'
                              'Esquema en [DDBB-DIAGRAM](DDBB-DIAGRAM.md).\n\n## Límites\n'),
        target.roadmap: (f'# Roadmap — {name}\n\n{road_begin}\n{road_end}\n\n## P001 — {first}\n\n'
                         '**Objetivo:** Definir el objetivo verificable de la fase.\n**Criterios de salida:**\n'
                         '- Criterio observable de salida.\n'),
        target.decisions: (f'# Decisiones — {name}\n\nRegistro único: una sección por decisión con el encabezado '
                           '`DNNN — título` de nivel 2 y una primera línea `Estado:` (propuesta, aceptada, '
                           'sustituida por DMMM o rechazada). Las decisiones no se borran: se sustituyen. El índice '
                           f'lo genera Harness Local.\n\n{dec_begin}\n{dec_end}\n'),
        target.ddbb_diagram: (f'# Diagrama de datos — {name}\n\nSin persistencia.\n\nCuando el proyecto tenga '
                              'modelos de datos, este documento recoge su esquema en Mermaid `erDiagram`.\n'),
        target.state: (f'# Estado — {name}\n\n{state_begin}\n{state_end}\n\n## Base acumulada\n\n'
                       'Todavía no hay trabajo aceptado.\n\n'
                       f'## Fase activa — P001 {first}\n\nSin notas todavía.\n'),
        target.next_steps: (f'# P001 — {first}\n\nObjetivo y criterios de salida en [ROADMAP](ROADMAP.md).\n\n'
                            f'{state_begin}\n{state_end}\n\n## Restricciones compartidas\n\n'
                            '## P001-T001 — Primera tarea\n\n**Objetivo:** Describir el cambio acotado.\n'
                            '**Rutas permitidas:** `src/**`\n**Criterios de aceptación:**\n- Criterio verificable.\n'),
    }

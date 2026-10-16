"""P008-T009 (Flujo A, D088 punto 10): inventario de solo lectura de un proyecto de un harness anterior.

Reglas puras sobre hechos ya leídos por el adaptador (árbol de HEAD de un checkout limpio y el directorio de
runs legacy). Ninguna función accede a disco, a Git ni a SQLite, y nada aquí decide movimientos: clasifica cada
documento con la regla que lo justifica, detecta el origen, las fases, los archivos de instrucciones y los bloques
gestionados, y sella el resultado con una huella independiente de la raíz y de la fecha del commit. El mapa de
normalización (T010) y la propuesta del revisor (T011) parten de este inventario.
"""

from dataclasses import dataclass
import hashlib
import re
from pathlib import PurePosixPath

from harness_local.core.engine.contracts import freeze
from harness_local.core.engine.documents import (
    MAX_AGENTS_LINES, MAX_DOCUMENT_BYTES, MAX_WRAPPER_LINES, blocks,
)
from harness_local.core.engine.planning import TASK_RE

INVENTORY_FORMAT = 'harness-local/import-inventory/1'
# Límites de lectura: el inventario se rechaza antes que truncarse en silencio.
MAX_ENTRIES = 5000
MAX_ENTRY_BYTES = 16 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024
LEGACY_HARNESS = '.harness'
LEGACY_RUNS = '.harness/runs'

CLASSES = ('canonical', 'renameable', 'mergeable', 'historical', 'foreign')
ORIGINS = ('reference_project', 'v1', 'v2')
ROOT_DOCUMENTS = ('AGENTS.md', 'CLAUDE.md', 'GEMINI.md', 'README.md')
DOCS_DOCUMENTS = ('SPECIFICATION.md', 'ARCHITECTURE.md', 'ROADMAP.md', 'STATE.md', 'NEXT_STEPS.md',
                  'DECISIONS.md', 'DDBB-DIAGRAM.md')
INSTRUCTION_LIMITS = {'AGENTS.md': MAX_AGENTS_LINES, 'CLAUDE.md': MAX_WRAPPER_LINES, 'GEMINI.md': MAX_WRAPPER_LINES}
# Variantes inequívocas, además de las de mayúsculas. Lista explícita: lo que no está aquí no se renombra.
NAME_ALIASES = {'decissons.md': 'DECISIONS.md'}
ADR_NAME = re.compile(r'adrs?(?:[-_ ][^/]*)?\.md', re.IGNORECASE)
DECISION_FILE = re.compile(r'D\d{3,}-[^/]+\.md')
ARCHIVE_PHASE = re.compile(r'phase-(\d+)')
V1_FOUNDATION = ('BRIEF.md', 'PROJECT_PROFILE.md')
V1_CHECKLIST = 'DELIVERY_CHECKLIST.md'
SPECIFICATION_SOURCES = ('PROJECT.md', 'REQUIREMENTS.md')
V2_FOLDERS = ('decisions', 'architecture', 'research')
# Fases de ROADMAP: `## P001 — …` (este harness) o `## Phase 001 — …` (ReferenceProject).
ROADMAP_PHASE = re.compile(r'^##\s+(?:P|(?:Phase|Fase)\s+)(\d{1,3})\s*[—–:-]\s*(.+?)\s*$', re.MULTILINE)
STATE_HEADING = re.compile(r'^##\s+(?:Fase activa|Active phase)\s*[—–:-]\s*(P\d{3})\b', re.MULTILINE)
NEXT_STEPS_TITLE = re.compile(r'^#\s+(P\d{3})\b', re.MULTILINE)
FRONTMATTER_PHASE = re.compile(r'^phase:\s*["\']?(?:P)?(\d{1,3})["\']?\s*$', re.MULTILINE)
GIT_KINDS = {'100644': 'file', '100755': 'file', '120000': 'symlink', '160000': 'submodule'}


class ImportInventoryError(ValueError):
    """El checkout no admite inventario (no Git, sin commits, sucio, vacío o demasiado grande)."""


@dataclass(frozen=True)
class TreeEntry:
    """Entrada del árbol de HEAD dentro del ámbito documental. `data` es None si no se leyó."""

    path: str
    mode: str
    size: int | None
    data: bytes | None = None
    diagnostic: str | None = None


@dataclass(frozen=True)
class CheckoutSnapshot:
    root: str
    head: str
    tree: str
    entries: tuple[TreeEntry, ...]
    legacy_runs: dict


def code(number: str | int) -> str:
    return f'P{int(number):03d}'


def in_scope(path: str, docs: str) -> bool:
    """Ámbito documental: Markdown de la raíz, todo `docs/` y `.harness/` salvo sus runs (D027)."""
    if path == LEGACY_RUNS or path.startswith(LEGACY_RUNS + '/'):
        return False
    if '/' not in path:
        return path.lower().endswith('.md')
    return path.startswith(docs + '/') or path.startswith(LEGACY_HARNESS + '/')


def _canonical_name(name: str, choices) -> str | None:
    return next((choice for choice in choices if choice.lower() == name.lower()), None)


def candidate(path: str, docs: str) -> tuple[str, str, str | None]:
    """(clase, regla, documento canónico) de una ruta, sin mirar el resto del árbol."""
    pure = PurePosixPath(path)
    markdown = pure.suffix.lower() == '.md'
    if path.startswith(LEGACY_HARNESS + '/'):
        return 'foreign', 'previous-harness', None
    if '/' not in path:
        if path in ROOT_DOCUMENTS:
            return 'canonical', 'canonical-path', path
        if name := _canonical_name(path, ROOT_DOCUMENTS):
            return 'renameable', 'alias-case', name
        if name := _canonical_name(path, DOCS_DOCUMENTS) or NAME_ALIASES.get(path.lower()):
            return 'renameable', 'alias-root-document', f'{docs}/{name}'
        return 'foreign', 'root-markdown', None
    relative = path[len(docs) + 1:]
    parts = relative.split('/')
    if relative in DOCS_DOCUMENTS:
        return 'canonical', 'canonical-path', path
    if parts[0] == 'flows':
        if len(parts) == 2 and markdown:
            return 'canonical', 'flow', path
        return 'foreign', 'flows-other', None
    if parts[0] == 'phase':
        return 'canonical', 'phase-work', path
    if parts[0] == 'archive':
        match = ARCHIVE_PHASE.fullmatch(parts[1]) if len(parts) > 2 else None
        if match is None:
            return 'historical', 'archive-other', None
        if len(match[1]) == 3:
            return 'historical', 'archive-phase', path
        if len(match[1]) > 3:
            return 'historical', 'archive-other', None
        target = '/'.join([docs, 'archive', f'phase-{int(match[1]):03d}', *parts[2:]])
        return 'historical', 'archive-phase-renumber', target
    if len(parts) == 1:
        name = parts[0]
        if canonical := _canonical_name(name, DOCS_DOCUMENTS):
            return 'renameable', 'alias-case', f'{docs}/{canonical}'
        if canonical := NAME_ALIASES.get(name.lower()):
            return 'renameable', 'alias-name', f'{docs}/{canonical}'
        if ADR_NAME.fullmatch(name):
            return 'renameable', 'alias-adr', f'{docs}/DECISIONS.md'
        if name in V1_FOUNDATION:
            return 'historical', 'v1-foundation', None
        if name == V1_CHECKLIST:
            return 'mergeable', 'v1-checklist', None
        if name in SPECIFICATION_SOURCES:
            return 'mergeable', 'specification-source', f'{docs}/SPECIFICATION.md'
        return ('mergeable', 'unclassified-markdown', None) if markdown else ('foreign', 'docs-other', None)
    if parts[0] in V2_FOLDERS and len(parts) == 2 and parts[1] == 'README.md':
        return 'historical', 'v2-folder-readme', None
    if parts[0] == 'research':
        return 'historical', 'research', None
    if parts[0] == 'decisions' and len(parts) == 2 and DECISION_FILE.fullmatch(parts[1]):
        return 'mergeable', 'decision-file', f'{docs}/DECISIONS.md'
    if parts[0] == 'architecture' and relative == 'architecture/data-model.md':
        return 'renameable', 'data-model', f'{docs}/DDBB-DIAGRAM.md'
    if parts[0] == 'architecture' and markdown:
        return 'mergeable', 'architecture-detail', None
    return ('mergeable', 'unclassified-markdown', None) if markdown else ('foreign', 'docs-other', None)


def classify(paths: list[str], docs: str) -> dict[str, tuple[str, str, str | None]]:
    """Clasificación con conflictos: un alias nunca ocupa un destino existente ni compartido con otro alias."""
    result = {path: candidate(path, docs) for path in paths}
    existing = set(paths)
    targets: dict[str, list[str]] = {}
    for path, (kind, _, canonical) in result.items():
        if kind == 'renameable':
            targets.setdefault(canonical, []).append(path)
    for canonical, sources in targets.items():
        if canonical in existing or len(sources) > 1:
            for path in sources:
                result[path] = ('mergeable', 'alias-conflict', canonical)
    # Renumerar el archivo es por directorio: `phase-1` y `phase-01` no pueden ir ambos a `phase-001`.
    depth = len(docs.split('/')) + 2

    def folder(value: str) -> str:
        return '/'.join(value.split('/')[:depth])

    renumbered: dict[str, set[str]] = {}
    occupied = {folder(path) for path, (_, rule, _) in result.items() if rule == 'archive-phase'}
    for path, (_, rule, canonical) in result.items():
        if rule == 'archive-phase-renumber':
            renumbered.setdefault(folder(canonical), set()).add(folder(path))
    for path, (_, rule, canonical) in list(result.items()):
        if rule == 'archive-phase-renumber':
            target = folder(canonical)
            if target in occupied or len(renumbered[target]) > 1:
                result[path] = ('historical', 'archive-phase-conflict', None)
    return result


def _text(entry: TreeEntry) -> str | None:
    if entry.data is None or len(entry.data) > MAX_DOCUMENT_BYTES:
        return None
    try:
        return entry.data.decode('utf-8')
    except UnicodeDecodeError:
        return None


def _entry(entry: TreeEntry, classification) -> dict:
    kind, rule, canonical = classification
    item = {'path': entry.path, 'kind': GIT_KINDS.get(entry.mode, 'other'), 'size': entry.size,
            'sha256': hashlib.sha256(entry.data).hexdigest() if entry.data is not None else None,
            'class': kind, 'rule': rule, 'canonical': canonical,
            'status': 'read' if entry.data is not None else 'rejected', 'diagnostic': entry.diagnostic}
    if entry.data is not None and PurePosixPath(entry.path).suffix.lower() == '.md':
        text = _text(entry)
        if text is None:
            item['diagnostic'] = (f'Markdown over {MAX_DOCUMENT_BYTES} bytes; not analysed.'
                                  if len(entry.data) > MAX_DOCUMENT_BYTES else 'Markdown is not UTF-8; not analysed.')
        else:
            item['lines'] = len(text.splitlines())
            try:
                item['blocks'] = sorted(blocks(text))
            except ValueError as error:
                item['blocks'] = []
                item['diagnostic'] = f'Invalid managed blocks: {error}'
    return item


def _source(entries: list[dict], canonical: str) -> dict | None:
    """El documento canónico, o el único alias o fuente que corresponde a él."""
    exact = [item for item in entries if item['path'] == canonical]
    matches = exact or [item for item in entries if item['canonical'] == canonical
                        and item['class'] in ('renameable', 'mergeable')]
    return matches[0] if len(matches) == 1 else None


def _roadmap(text: str) -> dict:
    phases, seen, duplicates = [], set(), []
    for match in ROADMAP_PHASE.finditer(text):
        value = code(match[1])
        if value in seen:
            duplicates.append(value)
        seen.add(value)
        phases.append({'code': value, 'title': match[2]})
    return {'phases': phases, 'duplicates': sorted(set(duplicates))}


def _state(text: str) -> list[dict]:
    found = []
    if text.startswith('---\n'):
        end = text.find('\n---', 4)
        if end != -1 and (phase := FRONTMATTER_PHASE.search(text[4:end])):
            found.append({'code': code(phase[1]), 'source': 'frontmatter'})
    found.extend({'code': match[1], 'source': 'heading'} for match in STATE_HEADING.finditer(text))
    return found


def _next_steps(text: str) -> dict:
    tasks = [match[1] for match in TASK_RE.finditer(text)]
    title = NEXT_STEPS_TITLE.search(text)
    return {'title_code': title[1] if title else None, 'tasks': len(tasks),
            'task_phases': sorted({task.split('-')[0] for task in tasks})}


def _archive(entries: list[dict], docs: str) -> list[dict]:
    """Carpetas `archive/phase-N` con sus archivos; ReferenceProject archiva sin STATE."""
    archive: dict[str, dict] = {}
    prefix = f'{docs}/archive/'
    for item in entries:
        parts = item['path'][len(prefix):].split('/') if item['path'].startswith(prefix) else []
        if len(parts) < 2 or not ARCHIVE_PHASE.fullmatch(parts[0]):
            continue
        folder = archive.setdefault(parts[0], {'path': prefix + parts[0], 'files': []})
        folder['files'].append('/'.join(parts[1:]))
    for name, folder in archive.items():
        number = ARCHIVE_PHASE.fullmatch(name)[1]
        folder['code'] = code(number) if len(number) <= 3 else None
        folder['has_state'] = 'STATE.md' in folder['files']
    return [archive[name] for name in sorted(archive, key=lambda key: (int(ARCHIVE_PHASE.fullmatch(key)[1]), key))]


def _phases(entries: list[dict], texts: dict[str, str], docs: str) -> dict:
    result = {}
    for name, parse in (('roadmap', _roadmap), ('state', _state), ('next_steps', _next_steps)):
        source = _source(entries, f'{docs}/{name.upper()}.md')
        text = texts.get(source['path']) if source else None
        result[name] = None if text is None else {'path': source['path'], 'detected': parse(text)}
    result['archive'] = _archive(entries, docs)
    return result


def _instructions(entries: list[dict]) -> dict:
    result = {}
    for name, limit in INSTRUCTION_LIMITS.items():
        source = _source(entries, name)
        result[name] = None if source is None else {
            'path': source['path'], 'bytes': source['size'], 'lines': source.get('lines'), 'limit': limit,
            'within_limit': source.get('lines') is not None and source['lines'] <= limit}
    return result


def _origin(entries: list[dict], legacy_runs: dict, docs: str) -> dict:
    """Señales por origen. Uno solo con señales da el origen; varios, `mixed`; ninguno, `unified` o `unknown`."""
    paths = {item['path'] for item in entries}
    signals = {name: [] for name in ORIGINS}
    signals['reference_project'] += sorted(path for path in paths if path.startswith(LEGACY_HARNESS + '/'))
    if legacy_runs.get('present'):
        signals['reference_project'].append(LEGACY_RUNS)
    signals['reference_project'] += [f'{docs}/{name}' for name in SPECIFICATION_SOURCES if f'{docs}/{name}' in paths]
    archive = _archive(entries, docs)
    # phase-000 contiene la definición (BRIEF/DEFINITION) en v1/v2, nunca STATE: no es señal.
    signals['reference_project'] += [folder['path'] for folder in archive
                              if not folder['has_state'] and folder['code'] not in (None, 'P000')]
    signals['v1'] += [f'{docs}/{name}' for name in (*V1_FOUNDATION, V1_CHECKLIST) if f'{docs}/{name}' in paths]
    signals['v2'] += [f'{docs}/{folder}' for folder in V2_FOLDERS
                      if any(path.startswith(f'{docs}/{folder}/') for path in paths)]
    present = [name for name in ORIGINS if signals[name]]
    if len(present) == 1:
        kind = present[0]
    elif present:
        kind = 'mixed'
    else:
        required = [*ROOT_DOCUMENTS, *(f'{docs}/{name}' for name in DOCS_DOCUMENTS)]
        kind = 'unified' if all(path in paths for path in required) else 'unknown'
    return {'kind': kind, 'signals': signals}


def _blockers(entries: list[dict]) -> list[dict]:
    """Lo que el Flujo A no puede mover byte a byte. Un Markdown no analizable es un aviso, no un bloqueo."""
    return [{'code': f'{item["kind"]}_entry' if item['kind'] in ('symlink', 'submodule') else 'unread_entry',
             'path': item['path'], 'diagnostic': item['diagnostic']}
            for item in entries if item['status'] != 'read']


def fingerprint(inventory: dict) -> str:
    """Independiente de la raíz y del commit: cuentan el árbol, el contenido y los runs observados."""
    body = {key: value for key, value in inventory.items() if key not in ('root', 'head', 'inventory_sha256')}
    return hashlib.sha256(freeze(body).encode('utf-8')).hexdigest()


def build_inventory(snapshot: CheckoutSnapshot, docs: str = 'docs') -> dict:
    ordered = sorted(snapshot.entries, key=lambda entry: entry.path)
    classes = classify([entry.path for entry in ordered], docs)
    entries = [_entry(entry, classes[entry.path]) for entry in ordered]
    texts = {entry.path: text for entry in ordered
             if entry.path.lower().endswith('.md') and (text := _text(entry)) is not None}
    inventory = {
        'format': INVENTORY_FORMAT, 'root': snapshot.root, 'head': snapshot.head, 'tree': snapshot.tree,
        'docs': docs, 'origin': _origin(entries, snapshot.legacy_runs, docs),
        'counts': {name: sum(item['class'] == name for item in entries) for name in CLASSES},
        'entries': entries, 'phases': _phases(entries, texts, docs), 'instructions': _instructions(entries),
        'managed_blocks': [{'path': item['path'], 'blocks': item['blocks']}
                           for item in entries if item.get('blocks')],
        'legacy_runs': snapshot.legacy_runs, 'blockers': _blockers(entries),
    }
    inventory['inventory_sha256'] = fingerprint(inventory)
    return inventory

"""P008-T010 (Flujo A, D088 punto 10): mapa de normalización determinista hacia el layout unificado.

Reglas puras sobre el inventario de T009 y los bytes que leyó; nada accede a disco, Git ni SQLite, y nada aquí
escribe. El mapa calcula solo lo inequívoco: renombrados por alias explícito, renumeración del archivo, retirada de
v1 y de las carpetas v2 a `archive/phase-000/`, artefactos de fase hacia su archivo o `docs/phase/` y las
decisiones `decisions/DNNN-*.md` como secciones de DECISIONS. Cada operación cita su regla, un movimiento conserva
los bytes y ningún destino coincide (tampoco en mayúsculas) con una ruta que ya existe ni con otro destino. Lo
ambiguo queda para la propuesta del revisor (T011) y lo ajeno para el usuario; el commit es de T012.
"""

import hashlib
import re
from pathlib import PurePosixPath

from harness_local.core.engine.contracts import freeze
from harness_local.core.engine.documents import ANY_MARKER, blocks, decision_index, markers
from harness_local.core.project_import import DOCS_DOCUMENTS, INVENTORY_FORMAT, ROOT_DOCUMENTS, code, fingerprint

MAP_FORMAT = 'harness-local/import-map/1'
# Carpeta del archivo para lo retirado sin fase propia (v1, carpetas v2, decisiones compuestas), como en el Flujo B.
RETIRED_PHASE = 'phase-000'
RENAME_RULES = {'alias-case': 'rename-alias', 'alias-root-document': 'rename-alias', 'alias-name': 'rename-alias',
                'alias-adr': 'rename-alias', 'data-model': 'rename-data-model',
                'archive-phase-renumber': 'archive-renumber', 'v1-foundation': 'retire-v1-foundation',
                'v2-folder-readme': 'retire-v2-readme'}
KEPT_RULES = ('canonical-path', 'flow', 'phase-work', 'archive-phase')
REVIEW_REASONS = {'specification-source': 'merge-proposal', 'architecture-detail': 'merge-proposal',
                  'v1-checklist': 'merge-proposal', 'unclassified-markdown': 'merge-proposal',
                  'alias-conflict': 'alias-conflict',
                  'archive-phase-conflict': 'archive-conflict', 'archive-other': 'archive-unrecognised'}
PATH_PHASE = re.compile(r'(?<![A-Za-z0-9])P(\d{3})(?!\d)')
NAME_PHASE = re.compile(r'P(\d{3})(?!\d)')
DECISION_NAME = re.compile(r'(D\d{3,})-[^/]+\.md')
DECISION_TITLE = re.compile(r'#[ \t]+(D\d{3,})[ \t]+[—-][ \t]+\S.*')
UPPER_HEADING = re.compile(r'#{1,2}(?:[ \t]|$)')
FENCE = re.compile(r'(?:```|~~~)')
DECISIONS_BASE = '# Decisiones\n\n{}\n{}\n'.format(*markers('decisions'))


class ImportMapError(ValueError):
    """El inventario o sus contenidos no admiten un mapa (formato, huella o bytes que no coinciden)."""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def active_phase(inventory: dict) -> str | None:
    """La fase en curso solo si STATE y NEXT_STEPS, cuando la declaran, coinciden en un único código."""
    phases, found = inventory['phases'], set()
    if phases['state']:
        found.update(item['code'] for item in phases['state']['detected'])
    if phases['next_steps']:
        detected = phases['next_steps']['detected']
        found.update(detected['task_phases'])
        if detected['title_code']:
            found.add(detected['title_code'])
    return found.pop() if len(found) == 1 else None


def _phase_of(relative: str, top_level: bool) -> str | None:
    """Código de fase de un artefacto: el nombre empieza por PNNN (raíz de docs) o la ruta cita uno solo."""
    if top_level:
        match = NAME_PHASE.match(relative)
        return code(match[1]) if match else None
    found = {code(match[1]) for match in PATH_PHASE.finditer(relative)}
    return found.pop() if len(found) == 1 else None


def _archived_phases(entries: list[dict], docs: str) -> set[str]:
    """Fases con carpeta de archivo de tres dígitos, ya existente o tras su renumeración."""
    prefix, found = f'{docs}/archive/', set()
    for item in entries:
        path = item['canonical'] if item['rule'] == 'archive-phase-renumber' else item['path']
        if item['rule'] in ('archive-phase', 'archive-phase-renumber'):
            found.add(code(path[len(prefix):].split('/')[0].removeprefix('phase-')))
    return found


def _artifact(item: dict, docs: str, active: str | None, archived: set[str]):
    """(regla, destino) de un artefacto de fase, o (motivo, None) si su fase no es inequívoca. La ruta conserva su
    primer componente con el código, así que nunca ocupa los nombres que el cierre reserva (D091)."""
    if not item['path'].startswith(docs + '/'):
        return None
    relative = item['path'][len(docs) + 1:]
    top_level = '/' not in relative
    if top_level and item['rule'] not in ('unclassified-markdown', 'docs-other'):
        return None
    if not top_level and item['rule'] != 'research':
        return None
    inside = relative if top_level else relative.split('/', 1)[1]
    phase = _phase_of(inside, top_level)
    if phase is None:
        return None if top_level else ('phase-unknown', None)
    if phase == active:
        return 'phase-artifact-active', f'{docs}/phase/{inside}'
    if phase in archived:
        return 'phase-artifact-archived', f'{docs}/archive/phase-{phase[1:]}/{inside}'
    return 'phase-unknown', None


def _decision_section(name: str, data: bytes) -> tuple[str | None, str | None]:
    """(DNNN, diagnóstico): la sección es el archivo con su `# DNNN — título` bajado a nivel 2 (un `#` delante)."""
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        return None, 'not UTF-8'
    number = DECISION_NAME.fullmatch(name)[1]
    lines = text.splitlines()
    title = DECISION_TITLE.fullmatch(lines[0]) if lines else None
    if title is None or title[1] != number:
        return None, f'first line must be "# {number} — title"'
    fenced = False
    for line in lines[1:]:
        if FENCE.match(line.lstrip()):
            fenced = not fenced
        elif not fenced and UPPER_HEADING.match(line):
            return None, 'level 1 or 2 headings besides the title'
    if ANY_MARKER.search(text):
        return None, 'managed block markers'
    return number, None


def _section(data: bytes) -> bytes:
    return b'#' + data + (b'' if data.endswith(b'\n') else b'\n')


def compose_decisions(base: bytes, sections: list[bytes]) -> bytes:
    """Base intacta y, en orden, una línea en blanco y cada sección; el índice lo regenera el commit (T012)."""
    result = base + (b'' if not base or base.endswith(b'\n') else b'\n')
    for data in sections:
        result += b'\n' + _section(data)
    return result


def _parents(key: str) -> list[str]:
    return ['/'.join(key.split('/')[:depth]) for depth in range(1, key.count('/') + 1)]


def _clashes(target: str, source: str, existing: dict[str, set[str]], targets: dict[str, list[str]],
             directories: set[str]) -> bool:
    """Un destino choca con una ruta del árbol distinta de su origen, con otro destino o con un directorio."""
    key = target.lower()
    if existing.get(key, set()) - {source} or len(targets.get(key, [])) > 1 or key in directories:
        return True
    return any(parent in existing or parent in targets for parent in _parents(key))


def _contents(inventory: dict, contents: dict[str, bytes]) -> dict[str, bytes]:
    if inventory.get('format') != INVENTORY_FORMAT or fingerprint(inventory) != inventory.get('inventory_sha256'):
        raise ImportMapError('The inventory format or fingerprint does not match.')
    found = {}
    for item in inventory['entries']:
        if item['status'] != 'read':
            continue
        data = contents.get(item['path'])
        if data is None or _sha(data) != item['sha256']:
            raise ImportMapError(f'Content of {item["path"]} is missing or differs from the inventory.')
        found[item['path']] = data
    return found


def build_map(inventory: dict, contents: dict[str, bytes]) -> dict:
    """Mapa determinista del inventario; `contents` son los bytes leídos (se comprueban contra su hash)."""
    data = _contents(inventory, contents)
    docs, entries = inventory['docs'], inventory['entries']
    active, archived = active_phase(inventory), _archived_phases(entries, docs)
    decisions_path = f'{docs}/DECISIONS.md'
    moves, review, foreign, kept, decision_files = [], [], [], [], []

    def to_review(item, reason, diagnostic=None):
        review.append({'path': item['path'], 'reason': reason, 'class': item['class'], 'rule': item['rule'],
                       'canonical': item['canonical'], 'diagnostic': diagnostic})

    for item in entries:
        path, rule = item['path'], item['rule']
        if item['status'] != 'read':
            continue  # bloqueado en el inventario: el Flujo A no lo mueve ni lo lee
        if (artifact := _artifact(item, docs, active, archived)) is not None:
            reason, target = artifact
            if target is None:
                to_review(item, reason)
            else:
                moves.append({'rule': reason, 'source': path, 'target': target})
        elif rule in RENAME_RULES:
            target = item['canonical']
            if rule in ('v1-foundation', 'v2-folder-readme'):
                target = f'{docs}/archive/{RETIRED_PHASE}/{path[len(docs) + 1:]}'
            moves.append({'rule': RENAME_RULES[rule], 'source': path, 'target': target})
        elif rule == 'decision-file':
            decision_files.append(item)
        elif rule in KEPT_RULES:
            kept.append(path)
        elif item['class'] == 'foreign':
            foreign.append({'path': path, 'rule': rule})
        else:
            to_review(item, REVIEW_REASONS[rule])

    # Decisiones: cada archivo válido y de número único se archiva por bytes y entra como sección.
    numbered: dict[int, list[tuple[dict, str]]] = {}
    for item in decision_files:
        number, diagnostic = _decision_section(PurePosixPath(item['path']).name, data[item['path']])
        if diagnostic is not None:
            to_review(item, 'decision-unparsed', diagnostic)
        else:
            numbered.setdefault(int(number[1:]), []).append((item, number))
    for group in numbered.values():
        for item, number in group:
            if len(group) > 1:
                to_review(item, 'decision-duplicate', f'{number} is not unique')
            else:
                moves.append({'rule': 'archive-decision', 'source': item['path'],
                              'target': f'{docs}/archive/{RETIRED_PHASE}/{item["path"][len(docs) + 1:]}'})

    existing: dict[str, set[str]] = {}
    for item in entries:
        existing.setdefault(item['path'].lower(), set()).add(item['path'])
    targets: dict[str, list[str]] = {}
    for move in moves:
        targets.setdefault(move['target'].lower(), []).append(move['source'])
    directories = {parent for key in [*existing, *targets] for parent in _parents(key)}
    by_path = {item['path']: item for item in entries}
    surviving = []
    for move in moves:
        if _clashes(move['target'], move['source'], existing, targets, directories):
            to_review(by_path[move['source']], 'target-conflict', f'{move["rule"]} -> {move["target"]}')
        else:
            surviving.append(move)
    moved = {move['source'] for move in surviving}

    # Sin su archivo en `phase-000` la sección no se compone: el original quedaría sin conservar.
    compose = None
    candidates = sorted(((int(number[1:]), item, number) for group in numbered.values() if len(group) == 1
                         for item, number in group if item['path'] in moved), key=lambda value: value[0])
    if candidates:
        compose, rejected = _compose(decisions_path, data, by_path, surviving, review, candidates)
        for item, (reason, diagnostic) in rejected:
            surviving = [move for move in surviving if move['source'] != item['path']]
            to_review(item, reason, diagnostic)
    for move in surviving:
        move['sha256'], move['size'] = by_path[move['source']]['sha256'], by_path[move['source']]['size']

    tree = _tree(entries, surviving, compose)
    tree_paths = {item['path'] for item in tree}
    required = [*ROOT_DOCUMENTS, *(f'{docs}/{name}' for name in DOCS_DOCUMENTS)]
    result = {
        'format': MAP_FORMAT, 'inventory_sha256': inventory['inventory_sha256'], 'docs': docs,
        'active_phase': active, 'moves': sorted(surviving, key=lambda move: move['source']),
        'compose': compose, 'kept': sorted(kept), 'review': sorted(review, key=lambda item: item['path']),
        'foreign': foreign, 'blockers': inventory['blockers'],
        'missing': [path for path in required if path not in tree_paths], 'tree': tree,
    }
    result['map_sha256'] = map_fingerprint(result)
    return result


def _compose(decisions_path, data, by_path, moves, review, candidates):
    """Composición de DECISIONS sobre su base (el canónico, el alias que se renombra a él o la plantilla)."""
    def reject(reason, diagnostic):
        return None, [(item, (reason, diagnostic)) for _, item, _ in candidates]

    alias = next((move for move in moves if move['target'] == decisions_path), None)
    pending = any(item['canonical'] == decisions_path and item['rule'] != 'decision-file' for item in review)
    if decisions_path in by_path:
        base_source = decisions_path
    elif alias is not None:
        base_source = alias['source']
    elif pending:
        return reject('decision-base', 'DECISIONS depends on an alias that needs a merge proposal')
    else:
        base_source = None
    base = data[base_source] if base_source else DECISIONS_BASE.encode('utf-8')
    try:
        base_text = base.decode('utf-8')
        blocks(base_text)
        existing = {int(entry['id'][1:]) for entry in decision_index(base_text)}
    except (UnicodeDecodeError, ValueError) as error:
        return reject('decision-base', f'DECISIONS cannot be parsed: {error}')
    rejected, accepted = [], []
    for number, item, name in candidates:
        if number in existing:
            rejected.append((item, ('decision-duplicate', f'{name} is already in DECISIONS')))
        else:
            accepted.append((item, name))
    if not accepted:
        return None, rejected
    composed = compose_decisions(base, [data[item['path']] for item, _ in accepted])
    return {'rule': 'decision-sections', 'target': decisions_path, 'base': base_source,
            'base_sha256': _sha(base), 'sections': [{'source': item['path'], 'decision': number,
                                                     'sha256': item['sha256']} for item, number in accepted],
            'sha256': _sha(composed), 'size': len(composed)}, rejected


def _tree(entries: list[dict], moves: list[dict], compose: dict | None) -> list[dict]:
    """Árbol documental tras el mapa: lo movido en su destino, lo demás en su sitio hasta T011/T012."""
    sources = {move['source']: move for move in moves}
    tree = []
    for item in entries:
        move = sources.get(item['path'])
        tree.append({'path': move['target'] if move else item['path'], 'sha256': item['sha256'],
                     'source': item['path'], 'operation': move['rule'] if move else None})
    if compose is not None:
        tree = [node for node in tree if node['path'] != compose['target']]
        tree.append({'path': compose['target'], 'sha256': compose['sha256'], 'source': compose['base'],
                     'operation': compose['rule']})
    return sorted(tree, key=lambda node: node['path'])


def map_fingerprint(result: dict) -> str:
    body = {key: value for key, value in result.items() if key != 'map_sha256'}
    return hashlib.sha256(freeze(body).encode('utf-8')).hexdigest()


def materialize(result: dict, contents: dict[str, bytes]) -> dict[str, bytes]:
    """Bytes de cada ruta del árbol resultante, comprobados contra el mapa (T012 los escribe tras confirmar)."""
    output = {}
    for node in result['tree']:
        if node['operation'] == 'decision-sections':
            compose = result['compose']
            base = contents[compose['base']] if compose['base'] else DECISIONS_BASE.encode('utf-8')
            data = compose_decisions(base, [contents[section['source']] for section in compose['sections']])
        elif node['sha256'] is None:
            continue  # entrada bloqueada: no se leyó y sigue en su sitio
        else:
            data = contents[node['source']]
        if _sha(data) != node['sha256']:
            raise ImportMapError(f'Content for {node["path"]} differs from the map.')
        output[node['path']] = data
    return output


def snapshot_contents(snapshot) -> dict[str, bytes]:
    """Bytes leídos de un `CheckoutSnapshot`, por ruta."""
    return {entry.path: entry.data for entry in snapshot.entries if entry.data is not None}

"""P008-T011 (Flujo A, D088 punto 10): conversación `project_import` del revisor. Biblioteca estándar, sin efectos.

La conversación congela al crearse el inventario de T009 y el mapa de T010. Cada turno congela además los textos del
árbol resultante del mapa (comprobados contra sus hashes con `materialize`) y los borradores del área privada junto
a SQLite. El revisor, de solo lectura, propone documentos completos para las rutas de la plantilla D088 y
`flows/*.md`, con el esquema de la definición: fusiones (SPECIFICATION, ARCHITECTURE), adelgazamiento de AGENTS y
envoltorios, STATE y NEXT_STEPS de la fase activa, DDBB-DIAGRAM y flujos si faltan, y preguntas. El checkout no se
toca hasta la confirmación de T012, que parte de `readiness`.
"""

from pathlib import PurePosixPath

from harness_local.core.engine.documents import MAX_AGENTS_LINES, MAX_WRAPPER_LINES, Layout, blocks, decision_index
from harness_local.core.engine.definition import (
    _block_names, allowed_drafts_view, default_documents, required_documents,
)
from harness_local.core.project_normalization import ImportMapError, materialize

KIND = 'project_import'
# Textos del origen y borradores que un turno congela, íntegros; por encima, el turno no se encola.
MAX_SOURCE_BYTES = 2 * 1024 * 1024
MAP_FIELDS = ('moves', 'kept', 'review', 'foreign', 'blockers', 'missing')


def frozen_source(inventory: dict, mapping: dict) -> dict:
    if mapping['inventory_sha256'] != inventory['inventory_sha256']:
        raise ValueError('The normalization map belongs to another inventory')
    return {'inventory': inventory, 'map': mapping}


def identity(source: dict) -> dict:
    inventory, mapping = source['inventory'], source['map']
    return {'origin': inventory['origin']['kind'], 'head': inventory['head'], 'docs': inventory['docs'],
            'inventory_sha256': inventory['inventory_sha256'], 'map_sha256': mapping['map_sha256'],
            'active_phase': mapping['active_phase']}


def _resulting(source: dict, contents: dict[str, bytes]) -> dict[str, bytes]:
    try:
        return materialize(source['map'], contents)
    except (KeyError, ImportMapError) as exc:
        raise ValueError(f'The checkout no longer matches the frozen import map: {exc}') from exc


def _text(path: str, data: bytes | None) -> str | None:
    if data is None or PurePosixPath(path).suffix.lower() != '.md' or b'\0' in data:
        return None
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return None


def turn_context(target: Layout, source: dict, contents: dict[str, bytes], texts: dict[str, str],
                 inspection: dict) -> dict:
    """Lo que congela un turno: identidad del origen, inventario resumido, mapa, textos y borradores.

    `contents`: bytes del checkout (los del inventario congelado). `texts` e `inspection`: borradores del área."""
    inventory, mapping = source['inventory'], source['map']
    tree = _resulting(source, contents)
    archive = f"{mapping['docs']}/archive/"
    documents, listed = [], []
    for node in mapping['tree']:
        data = tree.get(node['path'])
        text = None if node['path'].startswith(archive) else _text(node['path'], data)
        entry = {'path': node['path'], 'source': node['source'], 'operation': node['operation'],
                 'sha256': node['sha256']}
        if text is None:
            listed.append(entry)  # archivo, no Markdown o no leído: solo ruta y hash
        else:
            documents.append({**entry, 'size': len(data), 'content': text})
    drafts = [{'path': path, 'sha256': inspection['drafts'][path], 'size': len(texts[path].encode('utf-8')),
               'content': texts[path]} for path in sorted(texts)]
    size = sum(item['size'] for item in documents) + sum(item['size'] for item in drafts)
    if size > MAX_SOURCE_BYTES:
        raise ValueError(f'Import documents and drafts exceed the {MAX_SOURCE_BYTES // (1024 * 1024)} MiB a turn '
                         'can freeze; shorten or remove some drafts')
    return {'source': {**identity(source), 'signals': inventory['origin']['signals'], 'phases': inventory['phases'],
                       'instructions': inventory['instructions'], 'managed_blocks': inventory['managed_blocks'],
                       'legacy_runs': inventory['legacy_runs']},
            'map': {**{key: mapping[key] for key in MAP_FIELDS},
                    'compose': None if mapping['compose'] is None else {
                        key: mapping['compose'][key] for key in ('rule', 'target', 'base', 'sections')}},
            'sources': documents, 'listed': listed, 'drafts': drafts, 'foreign': inspection['foreign'],
            'invalid': inspection['invalid'], 'allowed': allowed_drafts_view(target),
            'limits': {target.agents: MAX_AGENTS_LINES, target.claude: MAX_WRAPPER_LINES,
                       target.gemini: MAX_WRAPPER_LINES}}


def observation(inventory_sha256: str, inspection: dict) -> dict:
    """Lo que no puede cambiar durante un turno: el origen en el checkout y los borradores del área."""
    return {'inventory_sha256': inventory_sha256, 'drafts': dict(sorted(inspection['drafts'].items())),
            'invalid': list(inspection['invalid'])}


def readiness(target: Layout, source: dict, record: dict, inspection: dict, texts: dict[str, str],
              current: dict | None) -> dict:
    """¿Puede la importación pasar a la vista previa de T012? Bloqueos y avisos, sin efectos.

    `record`: preguntas (con aplazamientos), pendientes y turno pendiente de SQLite. `current`: inventario y bytes
    releídos del checkout, o None si no se pudieron leer (`current_error` en el registro)."""
    blockers, warnings = [], []
    inventory, mapping = source['inventory'], source['map']
    if record['pending_turn']:
        blockers.append('An import turn is pending; wait until it settles')
    tree, matched = {}, False
    if current is None:
        blockers.append(f"The checkout could not be read: {record.get('current_error')}")
    elif current['inventory']['inventory_sha256'] != inventory['inventory_sha256']:
        blockers.append('The checkout changed since the import conversation started; start a new import conversation')
    else:
        tree, matched = _resulting(source, current['contents']), True
    if mapping['blockers']:
        blockers.append('Entries the import cannot move byte for byte: '
                        + ', '.join(item['path'] for item in mapping['blockers']))
    if inspection['invalid']:
        blockers.append('Drafts must be UTF-8, NUL-free, not executable and at most 512 KiB: '
                        + ', '.join(inspection['invalid']))
    open_blocking = [q for q in record['questions'] if q['blocking'] and not q.get('deferred')]
    if open_blocking:
        blockers.append('Blocking questions remain open; answer them in a turn or defer them explicitly: '
                        + '; '.join(q['text'] for q in open_blocking))
    result = {path: text for path, data in tree.items() if (text := _text(path, data)) is not None}
    result.update(texts)
    if matched:
        missing = [path for path in required_documents(target) if path not in result]
        defaults = [path for path in missing if path in default_documents(target)]
        if defaults:
            warnings.append('Supplied by the template unless drafted: ' + ', '.join(defaults))
        if required := [path for path in missing if path not in defaults]:
            blockers.append('Required documents are missing from the map and the drafts: ' + ', '.join(required))
    for path, limit in ((target.agents, MAX_AGENTS_LINES), (target.claude, MAX_WRAPPER_LINES),
                        (target.gemini, MAX_WRAPPER_LINES)):
        if path in result and len(result[path].splitlines()) > limit:
            origin = 'draft' if path in texts else 'imported document'
            blockers.append(f'{path} ({origin}) must contain at most {limit} lines (D088)')
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
    warnings += [f"Map entry for the reviewer: {item['path']} ({item['reason']})" for item in mapping['review']]
    warnings += [f"Foreign file left for the user: {item['path']}" for item in mapping['foreign']]
    warnings += [f'Pendiente declarado por el revisor: {item}' for item in record['pending']]
    return {'ready': not blockers, 'blockers': blockers, 'warnings': warnings, 'source': identity(source),
            'drafts': dict(sorted(inspection['drafts'].items()))}

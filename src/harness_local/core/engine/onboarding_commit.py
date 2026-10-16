"""P008-T015: documentos confirmables del Flujo B, sin código generado ni fallback."""
from hashlib import sha256
import json

from harness_local.core.engine.contracts import context_snapshot, freeze
from harness_local.core.engine.definition import _block_names, allowed_draft, definition_layout, required_documents
from harness_local.core.engine.documents import MAX_AGENTS_LINES, MAX_WRAPPER_LINES, blocks
from harness_local.core.engine.import_commit import adopt_documents, check_destinations, preview_tree
from harness_local.core.engine.phases import digest

MESSAGE = 'docs: incorporar al control del harness'


def preview(context, source, contents, paths, drafts, record, inspection, writer):
    target = definition_layout(context)
    if record['pending_turn']:
        raise ValueError('An onboarding turn is pending; wait until it settles')
    if inspection['invalid'] or inspection['foreign']:
        raise ValueError('Invalid or foreign entries in the private onboarding drafts')
    if any(q['blocking'] and not q.get('deferred') for q in record['questions']):
        raise ValueError('Blocking questions remain open; answer or defer them explicitly')
    if any(not allowed_draft(target, path) for path in drafts):
        raise ValueError('Only documentation drafts are allowed')
    if not context.profile.validations:
        raise ValueError('The operator composition needs a profile with explicit validations')
    tree = dict(contents)
    tree.update({path: text.encode('utf-8') for path, text in drafts.items()})
    if missing := [path for path in required_documents(target) if not tree.get(path, b'').strip()]:
        raise ValueError('Required documents are missing: ' + ', '.join(missing))
    # An existing README is retained by bytes unless the user explicitly drafts its replacement.
    for path in (set(required_documents(target)) - {target.readme}) | set(drafts):
        data = tree[path]
        text = data.decode('utf-8')
        if set(blocks(text)) - _block_names(target, path):
            raise ValueError(f'{path} contains managed blocks for another document')
    for path, limit in ((target.agents, MAX_AGENTS_LINES), (target.claude, MAX_WRAPPER_LINES),
                        (target.gemini, MAX_WRAPPER_LINES)):
        if len(tree[path].decode('utf-8').splitlines()) > limit:
            raise ValueError(f'{path} must contain at most {limit} lines (D088)')
    phase = adopt_documents(context, tree)
    if phase['code'] != 'P001':
        raise ValueError('Onboarding must adopt P001 as its active phase')
    profile = json.loads(context_snapshot(context))['profile']
    preserved = []
    for path, original in sorted(contents.items()):
        if tree[path] != original:
            archive = f'{target.archive("P000")}/onboarding-originals/{path}'
            tree[archive] = original
            preserved.append({'source': path, 'target': archive, 'sha256': sha256(original).hexdigest()})
    archive = target.archive('P000')
    tree[archive + '/INVENTORY.json'] = (freeze(source['inventory']) + '\n').encode()
    summary = {'source': source['inventory']['head'], 'tree': source['inventory']['tree'],
               'conversation': record, 'profile': profile, 'preserved': preserved}
    tree[archive + '/SUMMARY.md'] = ('# Incorporación al harness\n\nBase existente documentada; P001 ACTIVE.\n'
        'Perfil de la composición y documentos sujetos a la confirmación de esta vista previa.\n\n'
        '```json\n' + json.dumps(summary, ensure_ascii=False, indent=2) + '\n```\n').encode()
    # Check all HEAD paths, including code outside the documentary preview. Never replace an existing archive.
    new = set(tree) - set(contents)
    check_destinations([*paths, *new])
    shown = preview_tree(context, source, contents, tree, phase, writer, {
        'flow': 'onboarding', 'origin': {'conversation_id': record['id'],
            'conversation_version': record['version'], 'drafts': inspection['drafts']},
        'source': {k: source['inventory'][k] for k in ('head', 'tree', 'inventory_sha256')},
        'profile': profile, 'profile_sha256': digest(profile),
        'profile_proposal': source['inventory']['profile_proposal'],
        'moves': [], 'preserved': preserved, 'foreign': [],
        'warnings': [f'Pendiente declarado por el revisor: {item}' for item in record['pending']]
            + [f"Pregunta aplazada: {q['text']} ({q['deferred']['reason']})"
               for q in record['questions'] if q.get('deferred')]}, MESSAGE)
    return shown

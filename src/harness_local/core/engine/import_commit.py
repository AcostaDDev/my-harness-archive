"""P008-T012: árbol documental confirmado del Flujo A; sin agentes ni efectos."""
from dataclasses import replace
from hashlib import sha256

from harness_local.core.engine.definition import default_documents, definition_layout, _block_names
from harness_local.core.engine.document_ops import _sealed_preview
from harness_local.core.engine.documents import (
    blocks, decision_index, parse_roadmap, phase_data, plan_tasks, render_decisions,
    render_next_steps, render_roadmap, render_state, replace_block, skeleton,
)
from harness_local.core.engine.phases import phase_definition
from harness_local.core.project_import import _state, _next_steps
from harness_local.core.project_normalization import materialize
from harness_local.core.engine.commit import CommitIntent, CommitPlan, MechanicalUpdate, git_provenance

MESSAGE = 'docs: normalizar al contrato documental'


def build_tree(context, source, contents, drafts, title):
    """Conserva cada original por bytes, también cuando un borrador o un bloque lo sustituye.

    Lo ambiguo del mapa se retira solo si no es archivo ni ajeno; la confirmación del árbol completo autoriza
    esa retirada. Un destino de conservación ocupado bloquea: nunca se sobrescribe ni se renumera el historial.
    """
    target = definition_layout(context)
    tree = materialize(source['map'], contents)
    template = skeleton(target, title, preparation=[c.argv for c in context.profile.preparation],
                        validations=[c.argv for c in context.profile.validations])
    for path in default_documents(target):
        tree.setdefault(path, template[path].encode())
    for item in source['map']['review']:
        path = item['path']
        if not path.startswith(target.docs + '/archive/'):
            tree.pop(path, None)
    tree.update({path: text.encode() for path, text in drafts.items()})
    texts = {path: tree[path].decode('utf-8') for path in target.phase_documents}
    for path, text in texts.items():
        if set(blocks(text)) - _block_names(target, path):
            raise ValueError(f'{path} contains managed blocks for another document')
    state_codes = {item['code'] for item in _state(texts[target.state])}
    plan = _next_steps(texts[target.next_steps])
    plan_codes = set(plan['task_phases']) | ({plan['title_code']} if plan['title_code'] else set())
    if len(state_codes) != 1 or len(plan_codes) != 1 or state_codes != plan_codes:
        raise ValueError('STATE and NEXT_STEPS must explicitly agree on one active phase; review the drafts')
    active = next(iter(state_codes))
    entries = parse_roadmap(texts[target.roadmap])
    entry = next((item for item in entries if item['code'] == active), None)
    if entry is None or not entry['objective'] or not entry['exit_criteria']:
        raise ValueError(f'ROADMAP needs {active} with its objective and exit criteria')
    tasks = plan_tasks(texts[target.next_steps], active)
    definition = phase_definition(context, phase_data(target, entry, tasks))
    fresh = {'phase': {'code': active, 'status': 'ACTIVE', 'objective': entry['objective']},
             'tasks': [{'task_id': task, 'status': None, 'planned': True} for task, _ in tasks],
             'open_questions': [], 'latest_check': None}
    generated = {
        target.state: replace_block(texts[target.state], render_state(fresh)),
        target.next_steps: replace_block(texts[target.next_steps], render_next_steps(fresh)),
        target.roadmap: replace_block(texts[target.roadmap], render_roadmap([
            {**item, **({'status': 'ACTIVE'} if item['code'] == active else {})} for item in entries]), 'roadmap'),
        target.decisions: replace_block(texts[target.decisions],
            render_decisions(decision_index(texts[target.decisions])), 'decisions'),
    }
    tree.update({path: text.encode() for path, text in generated.items()})
    preserved = []
    moved = {move['source']: move['target'] for move in source['map']['moves']}
    for path, data in sorted(contents.items()):
        if tree.get(path) == data or (path in moved and tree.get(moved[path]) == data):
            continue
        archive = f'{target.archive("P000")}/import-originals/{path}'
        if any(p.lower() == archive.lower() or p.lower().startswith(archive.lower() + '/')
               or archive.lower().startswith(p.lower() + '/') for p in tree):
            raise ValueError(f'Original archive destination already occupied: {archive}')
        tree[archive] = data
        preserved.append({'source': path, 'target': archive, 'sha256': sha256(data).hexdigest()})
    # Includes file/directory and case collisions, including destinations introduced by drafts.
    paths = {path.lower() for path in tree}
    if len(paths) != len(tree):
        raise ValueError('Import destinations conflict by case')
    for path in paths:
        if any('/'.join(path.split('/')[:n]) in paths for n in range(1, path.count('/') + 1)):
            raise ValueError(f'Import destinations conflict as file and directory: {path}')
    return tree, definition, preserved


def preview(context, source, contents, drafts, title, writer, *, origin, warnings):
    tree, phase, preserved = build_tree(context, source, contents, drafts, title)
    evidence = writer.capture(context)
    provenance = git_provenance(evidence)
    if evidence.base_revision != source['inventory']['head'] or evidence.changed_paths:
        raise ValueError('The checkout changed since the import conversation started')
    if provenance.index_tree != provenance.base_tree:
        raise ValueError('Import requires a clean index')
    def content(data):
        if data is None or b'\0' in data:
            return data
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return data
    changes = [(path, content(contents.get(path)), content(tree.get(path)))
               for path in sorted(set(contents) | set(tree))]
    shown = _sealed_preview(context, evidence, provenance, provenance.base_tree, changes, MESSAGE, {
        'operation': 'import_commit', 'origin': origin, 'source': {
            'inventory_sha256': source['inventory']['inventory_sha256'], 'map_sha256': source['map']['map_sha256']},
        'moves': source['map']['moves'], 'preserved': preserved, 'foreign': source['map']['foreign'],
        'phase': phase, 'baseline': {path: sha256(tree[path]).hexdigest() for path in phase['documents']},
        'result_tree': [{'path': path, 'sha256': sha256(data).hexdigest(), 'size': len(data)}
                        for path, data in sorted(tree.items())], 'warnings': warnings,
        'author': {'name': writer.identity.name, 'email': writer.identity.email}, 'message': MESSAGE})
    probe = CommitPlan(shown['head'], shown['tree'], tuple(MechanicalUpdate(**item) for item in shown['mechanical']),
                       MESSAGE + '\n', writer.identity.name, writer.identity.email, 0)
    proposed_tree, _ = writer.seal(context, probe)
    writer.check_tree_diff(context, shown['tree'], proposed_tree)
    shown['proposed_tree'] = proposed_tree
    for document in shown['documents']:
        document['exact_path'] = True
    # Delete case aliases before creating their canonical spelling on case-insensitive filesystems.
    shown['mechanical'].sort(key=lambda item: (item['content'] is not None, item['path']))
    return shown


def seal(context, shown, writer, operation_id, run_id, timestamp):
    updates = tuple(MechanicalUpdate(**item) for item in shown['mechanical'])
    message = f'{MESSAGE}\n\nHarness-Operation: {operation_id}\nHarness-Preview: {shown["preview_sha256"]}\n'
    plan = CommitPlan(shown['head'], shown['tree'], updates, message, writer.identity.name,
                      writer.identity.email, timestamp)
    tree, commit = writer.seal(context, plan)
    return CommitIntent(operation_id, run_id, 'IMPORT', shown['head'], shown['fingerprint'], shown['tree'],
                        shown['index_tree'], (), updates, tree, commit, message, plan.author_name,
                        plan.author_email, timestamp)


def execute(context, history, saved, writer, journal):
    journal.checkpoint(history, 'import_commit')
    intent = CommitIntent.from_json(saved['intent'])
    outcome = writer.execute_documents(context, intent, saved['preview']['documents'])
    committed = outcome.status != 'invalidated'
    return replace(history, status='completed' if committed else 'stopped',
                   stop=None if committed else history.stop), {
        'status': 'COMMITTED' if committed else 'INVALIDATED', 'commit': outcome.commit, 'tree': outcome.tree,
        'diagnostic': outcome.diagnostic, 'reconciled': outcome.status == 'reconciled'}

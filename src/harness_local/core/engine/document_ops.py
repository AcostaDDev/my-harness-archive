"""D072/H6.3: transición de fase y edición documental confirmada. Sin agentes.

Ambas operaciones siguen el patrón de la exportación D036: vista previa determinista con
contenido íntegro y diff, confirmación humana del hash exacto, intención de commit sellada
antes de escribir y escritor Git H2.4 conciliable tras una caída. Nunca se sobrescriben
bytes ajenos: cada documento admite solo su hash anterior (o ausencia) o el sellado.
"""

from dataclasses import asdict, replace
import difflib
import hashlib

from harness_local.core.engine.commit import (
    CommitIntent, CommitPlan, MechanicalUpdate, git_provenance, validate_mechanical_updates,
)
from harness_local.core.engine.documents import (
    MAX_DOCUMENT_BYTES, Layout, base_section, blocks, budget_warnings, decision_index, inline, markers,
    parse_roadmap, phase_data, plan_tasks, render_decisions, render_next_steps, render_review, render_roadmap,
    render_state, render_summary, replace_block, require_layout,
)
from harness_local.core.engine.evidence import matches
from harness_local.core.engine.phases import digest, document_hashes, phase_definition

EDIT_REASON = 'User-confirmed document edit (D072)'
TRANSITION_REASON = 'Phase transition: archive and fresh documents (D072)'
TERMINAL = ('CLOSED', 'ABANDONED')


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def read_text(context, path: str) -> str | None:
    """Documento regular UTF-8 acotado; None si no existe. Enlaces y otros tipos se rechazan."""
    target = context.path(path)
    if target.is_symlink() or (target.exists() and not target.is_file()):
        raise ValueError(f'{path} must be a regular file')
    if not target.exists():
        return None
    data = target.read_bytes()
    if len(data) > MAX_DOCUMENT_BYTES:
        raise ValueError(f'{path} exceeds 512 KiB')
    return data.decode('utf-8')


def read_decisions(context, target: Layout, overrides: dict[str, str | None] | None = None) -> dict[str, str]:
    """Archivos de `decisions/` (sin subcarpetas), con el contenido propuesto superpuesto."""
    folder = context.path(target.decisions_dir)
    files = {}
    if folder.is_symlink():
        raise ValueError('The decisions folder must not be a symlink')
    if folder.is_dir():
        for item in sorted(folder.iterdir()):
            if item.suffix == '.md' and not item.is_dir():
                files[item.name] = read_text(context, f'{target.decisions_dir}/{item.name}')
    for path, text in (overrides or {}).items():
        if path.startswith(target.decisions_dir + '/') and '/' not in path[len(target.decisions_dir) + 1:]:
            files[path[len(target.decisions_dir) + 1:]] = text
    return {name: text for name, text in files.items() if text is not None}


def diff(path: str, old: str | None, new: str) -> str:
    delta = difflib.unified_diff((old or '').splitlines(keepends=True), new.splitlines(keepends=True),
                                 fromfile='/dev/null' if old is None else 'a/' + path, tofile='b/' + path)
    return ''.join(line if line.endswith('\n') else line + '\n\\ No newline at end of file\n' for line in delta)


def _clean_capture(context, git):
    evidence = git.capture(context)
    provenance = git_provenance(evidence)
    if evidence.changed_paths or provenance.index_tree != provenance.base_tree:
        raise ValueError('This operation requires a clean checkout and index; confirm or remove local changes first')
    return evidence, provenance


def _sealed_preview(context, evidence, provenance, tree: str, changes: list[tuple[str, str | None, str]],
                    reason: str, extra: dict) -> dict:
    documents, updates, diffs = [], [], []
    for path, old, new in changes:
        if old == new:
            continue
        if len(new.encode('utf-8')) > MAX_DOCUMENT_BYTES:
            raise ValueError(f'{path} would exceed 512 KiB')
        documents.append({'path': path, 'before_sha256': None if old is None else text_hash(old),
                          'after_sha256': text_hash(new), 'content': new})
        updates.append(MechanicalUpdate(path, new, reason))
        diffs.append(diff(path, old, new))
    validate_mechanical_updates(context, (), tuple(updates))
    data = {**extra, 'head': evidence.base_revision, 'fingerprint': evidence.fingerprint, 'tree': tree,
            'index_tree': provenance.index_tree, 'documents': documents,
            'mechanical': [asdict(update) for update in updates], 'diff': ''.join(diffs)}
    return {**data, 'preview_sha256': digest(data)}


def _protected(context, paths):
    for path in paths:
        if matches(path, context.profile.protected_paths):
            raise ValueError(f'{path} is protected by the project profile')


# --- transición ------------------------------------------------------------------------------


def _state_title(text: str) -> str:
    first = text.splitlines()[0] if text else ''
    return first if first.startswith('# ') and 'harness-local:managed-' not in first else '# Estado'


def preview_transition(context, snapshot: dict, git, next_steps: str | None) -> dict:
    """Archivo por bytes de la fase terminada, documentos frescos y definición de la siguiente."""
    target = require_layout(context)
    closed = snapshot['phase']
    code, status = closed['code'], closed['status']
    if status not in TERMINAL:
        raise ValueError('Only a CLOSED or ABANDONED phase can be archived')
    baseline = closed['documents']
    if document_hashes(context, baseline) != baseline:
        raise ValueError('Phase documents changed externally; confirm or reconcile them before the transition')
    evidence, provenance = _clean_capture(context, git)
    texts = {path: read_text(context, path) for path in target.phase_documents}
    missing = sorted(path for path, text in texts.items() if text is None)
    if missing:
        raise ValueError('Transition requires ' + ', '.join(missing))
    entries = parse_roadmap(texts[target.roadmap])
    codes = [entry['code'] for entry in entries]
    if code not in codes:
        raise ValueError(f'ROADMAP has no section for {code}; describe the phase there first')
    following = entries[codes.index(code) + 1] if codes.index(code) + 1 < len(entries) else None
    archive = target.archive(code)
    folder = context.path(archive)
    if folder.exists() or folder.is_symlink():
        raise ValueError(f'{archive} already exists; nothing is overwritten')
    definition = None
    if following is not None:
        if following['code'] in snapshot['existing_codes']:
            raise ValueError(f"Phase {following['code']} already exists in this checkout")
        if not isinstance(next_steps, str) or not next_steps.strip():
            raise ValueError(f"Provide the NEXT_STEPS plan of {following['code']}")
        if '\0' in next_steps:
            raise ValueError('The plan must be NUL-free text')
        if set(blocks(next_steps)) - {'state'}:
            raise ValueError('The plan may contain only the managed-state block of NEXT_STEPS')
        tasks = plan_tasks(next_steps, following['code'])
        if not tasks:
            raise ValueError(f"The plan of {following['code']} needs at least one task heading")
        definition = phase_definition(context, phase_data(target, following, tasks))
        plan = next_steps
    else:
        if next_steps is not None:
            raise ValueError('ROADMAP has no further phase; the transition only archives')
        tasks = []
        plan = (f'# Sin fase activa\n\nEl roadmap no tiene más fases después de {inline(code)}. Añade una fase '
                'en ROADMAP y su plan aquí mediante una edición confirmada.\n')
    titles = {entry['code']: entry['title'] for entry in entries}
    upcoming = None if following is None else {'code': following['code'], 'status': 'ACTIVE',
                                               'objective': following['objective']}
    fresh = {'phase': upcoming, 'tasks': [{'task_id': task, 'status': None, 'planned': True} for task, _ in tasks],
             'open_questions': [], 'latest_check': None}
    base = (base_section(texts[target.state]) or '## Base acumulada\n\nTodavía no hay trabajo aceptado.\n').rstrip()
    begin, end = markers('state')
    active = (f"## Fase activa — {following['code']} {inline(following['title'])}\n\nSin notas todavía.\n"
              if following else '## Fase activa\n\nSin fase activa: roadmap completado.\n')
    state = replace_block(f'{_state_title(texts[target.state])}\n\n{begin}\n{end}\n\n{base}\n\n{active}',
                          render_state(fresh))
    plan = replace_block(plan, render_next_steps(fresh))
    phases = {**snapshot['phases'], code: {'status': status, 'tag': closed['definition'].get('tag')}}
    if following is not None:
        phases[following['code']] = {'status': 'ACTIVE', 'tag': following['tag']}
    rows = [{'code': entry['code'], 'title': entry['title'], **phases.get(entry['code'], {})} for entry in entries]
    roadmap = replace_block(texts[target.roadmap], render_roadmap(rows), 'roadmap')
    decisions = replace_block(texts[target.decisions],
                              render_decisions(decision_index(read_decisions(context, target))), 'decisions')
    summary = {**snapshot['summary'], 'phase': {**snapshot['summary']['phase'], 'title': titles[code]}}
    changes = [(f'{archive}/STATE.md', None, texts[target.state]),
               (f'{archive}/NEXT_STEPS.md', None, texts[target.next_steps]),
               (f'{archive}/REVIEW.md', None, render_review(code, snapshot['check'], status)),
               (f'{archive}/SUMMARY.md', None, render_summary(summary)),
               (target.state, texts[target.state], state), (target.next_steps, texts[target.next_steps], plan),
               (target.roadmap, texts[target.roadmap], roadmap), (target.decisions, texts[target.decisions], decisions)]
    for _, _, text in changes[4:]:
        blocks(text)  # ningún marcador inyectado ni parcial en los documentos frescos
    _protected(context, [path for path, _, _ in changes])
    after = {target.state: state, target.next_steps: plan, target.roadmap: roadmap, target.decisions: decisions}
    return _sealed_preview(context, evidence, provenance, provenance.worktree_tree, changes, TRANSITION_REASON, {
        'operation': 'phase_transition', 'snapshot': snapshot, 'closed': code, 'archive': archive,
        'next': definition, 'warnings': budget_warnings(target, after)})


# --- edición documental ----------------------------------------------------------------------


def _edit_checks(target: Layout, path: str, old: str | None, new: str):
    if not target.editable(path):
        raise ValueError(f'{path} is not an editable document (README or Markdown under {target.docs}, never the archive)')
    if not isinstance(new, str) or '\0' in new:
        raise ValueError(f'{path} must be NUL-free text')
    try:
        before = blocks(old or '')
        after = blocks(new)
    except ValueError as exc:
        raise ValueError(f'{path}: {exc}') from exc
    if before != after:
        raise ValueError(f'{path}: managed blocks are generated by Harness Local and cannot be edited')


def preview_edit(context, git, *, source: str, changes: list[dict] | None) -> dict:
    """`content`: documentos enviados sobre un checkout limpio. `worktree`: cambios locales de documentos."""
    target = require_layout(context)
    evidence = git.capture(context)
    provenance = git_provenance(evidence)
    proposed: dict[str, str] = {}
    previous: dict[str, str | None] = {}
    if source == 'content':
        if evidence.changed_paths or provenance.index_tree != provenance.base_tree:
            raise ValueError('The checkout has local changes; confirm them as a worktree edit or remove them first')
        if not changes:
            raise ValueError('Send at least one document')
        for item in changes:
            path, content = item.get('path'), item.get('content')
            if not isinstance(path, str) or path in proposed:
                raise ValueError('Each edited document needs a distinct path')
            if not target.editable(path):
                raise ValueError(f'{path} is not an editable document (README or Markdown under {target.docs}, never the archive)')
            previous[path] = read_text(context, path)
            proposed[path] = content
    elif source == 'worktree':
        if changes is not None:
            raise ValueError('A worktree edit takes the documents from the checkout')
        if not evidence.changed_paths:
            raise ValueError('There are no local document changes to confirm')
        import json
        deleted = json.loads(evidence.provenance_json).get('deleted_paths', [])
        if deleted:
            raise ValueError('Deleted files are not confirmed as document edits: ' + ', '.join(deleted[:20]))
        outside = [path for path in evidence.changed_paths if not target.editable(path)]
        if outside:
            raise ValueError('Local changes outside editable documents: ' + ', '.join(outside[:20]))
        for path in evidence.changed_paths:
            blob = git.read_blob(context, evidence.base_revision, path)
            previous[path] = None if blob is None else blob.decode('utf-8')
            proposed[path] = read_text(context, path)
    else:
        raise ValueError('Unknown edit source')
    for path, content in proposed.items():
        _edit_checks(target, path, previous[path], content)
    # Un cambio en decisions/ regenera el índice gestionado en el mismo commit.
    if any(path.startswith(target.decisions_dir + '/') for path in proposed):
        base = proposed.get(target.decisions)
        if base is None:
            previous[target.decisions] = read_text(context, target.decisions)
            base = previous[target.decisions] or f'# Decisiones\n\n{markers("decisions")[0]}\n{markers("decisions")[1]}\n'
        proposed[target.decisions] = replace_block(base, render_decisions(decision_index(
            read_decisions(context, target, proposed))), 'decisions')
    _protected(context, proposed)
    changes_list = [(path, previous[path], proposed[path]) for path in sorted(proposed)]
    preview = _sealed_preview(context, evidence, provenance, provenance.base_tree, changes_list, EDIT_REASON,
                              {'operation': 'document_edit', 'source': source})
    if not preview['documents']:
        raise ValueError('The documents already have this content; there is nothing to commit')
    if source == 'worktree':
        # Todo el cambio local debe quedar dentro de lo confirmado: los documentos locales, sobre la base,
        # reproducen el árbol del checkout. El índice regenerado por el harness se añade después.
        local = tuple(MechanicalUpdate(**item) for item in preview['mechanical']
                      if item['path'] in evidence.changed_paths)
        plan = CommitPlan(evidence.base_revision, provenance.base_tree, local, 'probe\n',
                          git.identity.name, git.identity.email, 0)
        tree, _ = git.seal(context, plan)
        if tree != provenance.worktree_tree:
            raise ValueError('Local changes are not exactly the listed documents')
    return preview


# --- ejecución común -------------------------------------------------------------------------


def execute(context, history, request, git, journal, now, *, label: str):
    """Intención previa sellada y escritor H2.4; una intención existente solo se concilia."""
    shown = request['preview']
    raw = request.get('commit_intent')
    if raw is None:
        if git.capture(context).fingerprint != shown['fingerprint']:
            return replace(history, status='stopped'), {'status': 'INVALIDATED', 'diagnostic': 'Checkout changed after preview'}
        updates = tuple(MechanicalUpdate(**item) for item in shown['mechanical'])
        message = (f"harness: {label}\n\nHarness-Operation: {request['operation_id']}\n"
                   f"Harness-Preview: {shown['preview_sha256']}\n")
        plan = CommitPlan(shown['head'], shown['tree'], updates, message, git.identity.name, git.identity.email,
                          int(now().timestamp()))
        tree, commit = git.seal(context, plan)
        kind = 'PHASE-TRANSITION' if shown['operation'] == 'phase_transition' else 'DOCUMENT-EDIT'
        intent = CommitIntent(request['operation_id'], history.id, kind, shown['head'], shown['fingerprint'],
                              shown['tree'], shown['index_tree'], (), updates, tree, commit, message,
                              plan.author_name, plan.author_email, plan.committed_at)
        journal.document_intent(intent)
    else:
        intent = CommitIntent.from_json(raw)
    outcome = git.execute_documents(context, intent, shown['documents'])
    committed = outcome.status != 'invalidated'
    return replace(history, status='completed' if committed else 'stopped'), {
        'status': 'COMMITTED' if committed else 'INVALIDATED', 'commit': outcome.commit, 'tree': outcome.tree,
        'diagnostic': outcome.diagnostic, 'reconciled': outcome.status == 'reconciled'}

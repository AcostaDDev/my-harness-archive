"""D072/H6.3: transición de fase y edición documental confirmada. Sin agentes.

Ambas operaciones siguen el patrón de la exportación D036: vista previa determinista con
contenido íntegro y diff, confirmación humana del hash exacto, intención de commit sellada
antes de escribir y escritor Git H2.4 conciliable tras una caída. Nunca se sobrescriben
bytes ajenos: cada documento admite solo su hash anterior (o ausencia) o el sellado.
"""

from dataclasses import asdict, replace
import base64
import difflib
import hashlib

from harness_local.core.engine.commit import (
    CommitIntent, CommitPlan, MechanicalUpdate, git_provenance, validate_mechanical_updates,
)
from harness_local.core.engine.documents import (
    MAX_DOCUMENT_BYTES, Layout, base_section, blocks, budget_warnings, decision_index, inline, markers,
    parse_roadmap, phase_data, plan_tasks, render_decisions, render_next_steps, render_review, render_roadmap,
    protected_write, render_state, render_summary, replace_block, require_layout, _span,
)
from harness_local.core.engine.phases import digest, document_hashes, phase_definition

EDIT_REASON = 'User-confirmed document edit (D072)'
TRANSITION_REASON = 'Phase transition: archive and fresh documents (D072)'
TERMINAL = ('CLOSED', 'ABANDONED')


class BaseChanged(ValueError):
    """El documento ya no tiene el hash con el que se abrió en el editor (CAS del hash base)."""


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


def _sealed_preview(context, evidence, provenance, tree: str,
                    changes: list[tuple[str, str | bytes | None, str | bytes | None]],
                    reason: str, extra: dict, disk: dict[str, str] | None = None) -> dict:
    """`disk`: bytes locales que el commit sustituye además de los de la base (bloques regenerados)."""
    documents, updates, diffs = [], [], []
    for path, old, new in changes:
        if old == new:
            continue
        raw = new if isinstance(new, bytes) else (new.encode('utf-8') if new is not None else None)
        before = old if isinstance(old, bytes) else (old.encode('utf-8') if old is not None else None)
        if raw is not None and len(raw) > MAX_DOCUMENT_BYTES:
            raise ValueError(f'{path} would exceed 512 KiB')
        binary = isinstance(new, bytes)
        content = base64.b64encode(new).decode('ascii') if binary else new
        documents.append({'path': path, 'before_sha256': None if before is None else hashlib.sha256(before).hexdigest(),
                          'after_sha256': None if raw is None else hashlib.sha256(raw).hexdigest(), 'content': content,
                          **({'encoding': 'base64'} if binary else {}),
                          **({'disk_sha256': text_hash(disk[path])} if disk and path in disk else {})})
        updates.append(MechanicalUpdate(path, content, reason, 'base64' if binary else 'utf-8'))
        diffs.append(f'Archive bytes: {path}\n' if isinstance(old, bytes) or binary else diff(path, old, new or ''))
    validate_mechanical_updates(context, (), tuple(updates))
    data = {**extra, 'head': evidence.base_revision, 'fingerprint': evidence.fingerprint, 'tree': tree,
            'index_tree': provenance.index_tree, 'documents': documents,
            'mechanical': [asdict(update) for update in updates], 'diff': ''.join(diffs)}
    return {**data, 'preview_sha256': digest(data)}


def _protected(context, paths):
    for path in paths:
        if protected_write(context, path):
            raise ValueError(f'{path} is protected by the project profile')


# --- transición ------------------------------------------------------------------------------


def _state_title(text: str) -> str:
    first = text.splitlines()[0] if text else ''
    return first if first.startswith('# ') and 'harness-local:managed-' not in first else '# Estado'


def preview_transition(context, snapshot: dict, git, next_steps: str | None, plan_origin: dict | None = None,
                       *, unified=False) -> dict:
    """Archivo por bytes de la fase terminada, documentos frescos y definición de la siguiente.

    `plan_origin` (H6.5): propuesta de la conversación `phase_planning` de la que sale el plan; entra en el
    hash revisado. Sin ella, la vista previa conserva exactamente su forma anterior."""
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
        if unified:
            next_steps = (f"# {following['code']} — {inline(following['title'])}\n\n"
                          f"**Objetivo:** {following['objective']}\n\n**Criterios de salida:**\n"
                          + ''.join(f'- {item}\n' for item in following['exit_criteria'])
                          + '\nPendiente de planificación confirmada.\n')
        if not isinstance(next_steps, str) or not next_steps.strip():
            raise ValueError(f"Provide the NEXT_STEPS plan of {following['code']}")
        if '\0' in next_steps:
            raise ValueError('The plan must be NUL-free text')
        if set(blocks(next_steps)) - {'state'}:
            raise ValueError('The plan may contain only the managed-state block of NEXT_STEPS')
        tasks = plan_tasks(next_steps, following['code'])
        if not tasks and not unified:
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
    if unified:
        phases[code]['archive'] = archive.removeprefix(target.docs + '/') + '/'
    if following is not None:
        phases[following['code']] = {'status': 'ACTIVE', 'tag': following['tag']}
    rows = [{'code': entry['code'], 'title': entry['title'], **phases.get(entry['code'], {})} for entry in entries]
    roadmap = replace_block(texts[target.roadmap], render_roadmap(rows), 'roadmap')
    decisions = replace_block(texts[target.decisions], render_decisions(decision_index(texts[target.decisions])),
                              'decisions')
    summary = {**snapshot['summary'], 'phase': {**snapshot['summary']['phase'], 'title': titles[code]}}
    changes = [(f'{archive}/STATE.md', None, texts[target.state]),
               (f'{archive}/NEXT_STEPS.md', None, texts[target.next_steps]),
               (f'{archive}/REVIEW.md', None, render_review(code, snapshot['check'], status)),
               (f'{archive}/SUMMARY.md', None, render_summary(summary)),
               (target.state, texts[target.state], state), (target.next_steps, texts[target.next_steps], plan),
               (target.roadmap, texts[target.roadmap], roadmap), (target.decisions, texts[target.decisions], decisions)]
    for _, _, text in changes[4:]:
        blocks(text)  # ningún marcador inyectado ni parcial en los documentos frescos
    if unified:
        work = context.path(target.phase_dir)
        if work.exists():
            if not work.is_dir():
                raise ValueError(f'{target.phase_dir} must be a directory')
            reserved = {'STATE.md', 'NEXT_STEPS.md', 'REVIEW.md', 'SUMMARY.md'}
            for path in sorted(work.rglob('*')):
                relative = path.relative_to(work).as_posix()
                source = f'{target.phase_dir}/{relative}'
                safe = context.path(source)  # rechaza enlaces de archivos y directorios
                if safe.is_dir():
                    continue
                if not safe.is_file():
                    raise ValueError(f'{source} must be a regular file')
                if relative.split('/')[0] in reserved:
                    raise ValueError(f'{source} conflicts with the phase archive documents')
                if safe.stat().st_size > MAX_DOCUMENT_BYTES:
                    raise ValueError(f'{source} exceeds 512 KiB')
                data = safe.read_bytes()
                changes.extend([(f'{archive}/{relative}', None, data), (source, data, None)])
    _protected(context, [path for path, _, _ in changes])
    after = {target.state: state, target.next_steps: plan, target.roadmap: roadmap, target.decisions: decisions}
    return _sealed_preview(context, evidence, provenance, provenance.worktree_tree, changes, TRANSITION_REASON, {
        'operation': 'phase_close' if unified else 'phase_transition', 'snapshot': snapshot, 'closed': code, 'archive': archive,
        'next': definition, 'warnings': budget_warnings(target, after),
        **({'plan_origin': plan_origin} if plan_origin is not None else {})})


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


def restore_blocks(local: str, base: str | None, path: str) -> str:
    """Prosa local con los bloques gestionados de la base: «regenerar» ante una edición local de un bloque."""
    try:
        theirs, ours = blocks(local), blocks(base or '')
    except ValueError as exc:
        raise ValueError(f'{path}: {exc}; restore the markers by hand before regenerating') from exc
    if set(theirs) != set(ours):
        raise ValueError(f'{path}: managed markers were added or removed; restore them by hand before regenerating')
    for name, block in ours.items():  # bytes exactos del bloque base, incluidas sus terminaciones de línea
        start, stop = _span(local, name)
        local = local[:start] + block + local[stop:]
    return local


def preview_edit(context, git, *, source: str, changes: list[dict] | None, regenerate_blocks: bool = False) -> dict:
    """`content`: documentos enviados sobre un checkout limpio. `worktree`: cambios locales de documentos.

    En `content`, un `base_sha256` (null: el documento no debe existir) es el CAS del editor. En `worktree`,
    `regenerate_blocks` sustituye los bloques gestionados editados en local por los de la base; la vista previa
    los lista con el diff de lo que se descarta y el escritor solo admite esos bytes locales exactos."""
    target = require_layout(context)
    if regenerate_blocks and source != 'worktree':
        raise ValueError('Only a worktree edit regenerates managed blocks')
    evidence = git.capture(context)
    provenance = git_provenance(evidence)
    proposed: dict[str, str] = {}
    previous: dict[str, str | None] = {}
    local: dict[str, str] = {}
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
            if 'base_sha256' in item:
                current = None if previous[path] is None else text_hash(previous[path])
                if current != item['base_sha256']:
                    raise BaseChanged(f'{path} changed since it was opened in the editor '
                                      f'(base {str(item["base_sha256"])[:12]}, now {str(current)[:12]})')
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
            if regenerate_blocks and previous[path] is not None:
                restored = restore_blocks(proposed[path], previous[path], path)
                if restored != proposed[path]:
                    local[path], proposed[path] = proposed[path], restored
        if regenerate_blocks and not local:
            raise ValueError('No local change touches a managed block; confirm the edit without regenerating')
    else:
        raise ValueError('Unknown edit source')
    for path, content in proposed.items():
        _edit_checks(target, path, previous[path], content)
    # D088: editar DECISIONS regenera su índice gestionado, desde sus encabezados, en el mismo commit.
    if target.decisions in proposed:
        try:
            index = render_decisions(decision_index(proposed[target.decisions]))
        except ValueError as exc:
            raise ValueError(f'{target.decisions}: {exc}') from exc
        regenerated = replace_block(proposed[target.decisions], index, 'decisions')
        if source == 'worktree' and regenerated != proposed[target.decisions]:
            # Como «regenerar»: el escritor admite los bytes locales exactos y la vista previa lista el cambio.
            local.setdefault(target.decisions, proposed[target.decisions])
        proposed[target.decisions] = regenerated
    _protected(context, proposed)
    changes_list = [(path, previous[path], proposed[path]) for path in sorted(proposed)]
    extra = {'operation': 'document_edit', 'source': source}
    if local:
        # Lo que se descarta de los bytes locales; forma parte del hash revisado.
        extra['regenerated'] = [{'path': path, 'local_sha256': text_hash(local[path]),
                                 'diff': diff(path, local[path], proposed[path])} for path in sorted(local)]
    preview = _sealed_preview(context, evidence, provenance, provenance.base_tree, changes_list, EDIT_REASON,
                              extra, disk=local)
    if not preview['documents']:
        raise ValueError('The documents already have this content; there is nothing to commit')
    if source == 'worktree':
        # Todo el cambio local debe quedar dentro de lo confirmado: los documentos locales, sobre la base,
        # reproducen el árbol del checkout. El índice regenerado por el harness se añade después.
        probe = tuple(MechanicalUpdate(item['path'], local.get(item['path'], item['content']), item['reason'])
                      for item in preview['mechanical'] if item['path'] in evidence.changed_paths)
        plan = CommitPlan(evidence.base_revision, provenance.base_tree, probe, 'probe\n',
                          git.identity.name, git.identity.email, 0)
        tree, _ = git.seal(context, plan)
        if tree != provenance.worktree_tree:
            raise ValueError('Local changes are not exactly the listed documents')
    return preview


# --- ejecución común -------------------------------------------------------------------------


def seal_operation(context, history, request, git, journal, now, *, label):
    """Persiste la intención completa antes del primer efecto del cierre (incluido el tag)."""
    shown = request['preview']
    raw = request.get('commit_intent')
    if raw is None:
        if git.capture(context).fingerprint != shown['fingerprint']:
            raise BaseChanged('Checkout changed after preview')
        updates = tuple(MechanicalUpdate(**item) for item in shown['mechanical'])
        message = (f"harness: {label}\n\nHarness-Operation: {request['operation_id']}\n"
                   f"Harness-Preview: {shown['preview_sha256']}\n")
        plan = CommitPlan(shown['head'], shown['tree'], updates, message, git.identity.name, git.identity.email,
                          int(now().timestamp()))
        tree, commit = git.seal(context, plan)
        kind = {'phase_transition': 'PHASE-TRANSITION', 'phase_close': 'PHASE-CLOSE'}.get(
            shown['operation'], 'DOCUMENT-EDIT')
        intent = CommitIntent(request['operation_id'], history.id, kind, shown['head'], shown['fingerprint'],
                              shown['tree'], shown['index_tree'], (), updates, tree, commit, message,
                              plan.author_name, plan.author_email, plan.committed_at)
        journal.document_intent(intent)
    else:
        intent = CommitIntent.from_json(raw)
    return intent


def execute(context, history, request, git, journal, now, *, label: str):
    """Intención previa sellada y escritor H2.4; una intención existente solo se concilia."""
    shown = request['preview']
    try:
        intent = seal_operation(context, history, request, git, journal, now, label=label)
    except BaseChanged as exc:
        return replace(history, status='stopped'), {'status': 'INVALIDATED', 'diagnostic': str(exc)}
    outcome = git.execute_documents(context, intent, shown['documents'])
    committed = outcome.status != 'invalidated'
    return replace(history, status='completed' if committed else 'stopped'), {
        'status': 'COMMITTED' if committed else 'INVALIDATED', 'commit': outcome.commit, 'tree': outcome.tree,
        'diagnostic': outcome.diagnostic, 'reconciled': outcome.status == 'reconciled'}

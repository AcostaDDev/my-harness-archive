"""Exportación mecánica pura: bloques delimitados, bytes deterministas y commit exacto."""
from dataclasses import asdict, replace
import difflib
import hashlib
import json

from harness_local.core.engine.commit import (
    CommitIntent, CommitPlan, MechanicalUpdate, git_provenance, validate_mechanical_updates,
)
from harness_local.core.engine.phases import digest, document_hashes
from harness_local.core.engine.evidence import matches

BEGIN = '<!-- harness-local:managed-state:start -->'
END = '<!-- harness-local:managed-state:end -->'
MAX_DOCUMENT_BYTES = 512 * 1024


def text_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def replace_block(text, body):
    """No normaliza ni interpreta la prosa exterior, incluidas sus terminaciones de línea."""
    block = BEGIN + '\n' + body + END
    if BEGIN not in text and END not in text:
        return text + ('\n' if text and not text.endswith('\n') else '') + block + '\n'
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise ValueError('Mechanical markers must occur exactly once as a pair')
    start, end = text.index(BEGIN), text.index(END)
    if end < start or (start and text[start - 1] != '\n') or (
            end + len(END) < len(text) and text[end + len(END)] not in '\r\n'):
        raise ValueError('Mechanical markers must be ordered and occupy their own lines')
    if not text[start + len(BEGIN):].startswith(('\r\n', '\n')) or (
            end and text[end - 1] != '\n'):
        raise ValueError('Mechanical markers must occupy their own lines')
    suffix = text[end + len(END):]
    if suffix and not suffix.startswith(('\r\n', '\n')):
        raise ValueError('Mechanical markers must occupy their own lines')
    return text[:start] + block + text[end + len(END):]


def render(snapshot, *, next_steps=False):
    """Representación legible; valores libres se escapan como JSON para no inyectar marcadores/HTML."""
    # JSON estable también conserva explícitamente datos ausentes (null) y preguntas sin responder.
    # No incluye versiones/eventos de exportación, fecha actual ni el commit de la propia exportación.
    if next_steps:
        data = {'phase': snapshot['phase'], 'pending_tasks': [
            task for task, value in snapshot['tasks'].items() if value['commit'] is None],
            'open_questions': snapshot['open_questions'], 'latest_check': snapshot['latest_check'],
            'batches': snapshot['batches']}
    else:
        data = snapshot
    # Escape HTML, Markdown fences y líneas de marcador en valores aportados por humanos.
    pretty = json.dumps(data, ensure_ascii=True, sort_keys=True, indent=2)
    pretty = pretty.replace('<', '\\u003c').replace('>', '\\u003e').replace('`', '\\u0060')
    return 'Estado gestionado por Harness Local (SQLite).\n\n```json\n' + pretty + '\n```\n'


def preview(context, snapshot, baseline, git):
    paths = (context.state_file, context.next_steps_file)
    if len(set(paths)) != 2 or not set(paths) <= baseline.keys():
        raise ValueError('STATE and NEXT_STEPS must be distinct adopted phase documents')
    if document_hashes(context, baseline) != baseline:
        raise ValueError('Phase documents changed externally; review and reconcile the document hashes first')
    evidence = git.capture(context)
    provenance = git_provenance(evidence)
    if evidence.changed_paths or provenance.index_tree != provenance.base_tree:
        raise ValueError('Document export requires a clean checkout and index')
    documents, updates, diffs = [], [], []
    for number, path in enumerate(paths):
        target = context.path(path)
        if not target.is_file() or target.is_symlink() or target.stat().st_size > MAX_DOCUMENT_BYTES:
            raise ValueError('Export requires adopted regular UTF-8 documents of at most 512 KiB')
        old = target.read_bytes().decode('utf-8')
        if text_hash(old) != baseline[path]:
            raise ValueError(f'{path} changed externally; review and reconcile the document hashes first')
        new = replace_block(old, render(snapshot, next_steps=number == 1))
        if len(new.encode('utf-8')) > MAX_DOCUMENT_BYTES:
            raise ValueError('Exported document exceeds 512 KiB')
        documents.append({'path': path, 'before_sha256': text_hash(old), 'after_sha256': text_hash(new),
                          'content': new})
        if old != new:
            updates.append(MechanicalUpdate(path, new, 'SQLite mechanical state export'))
        delta = difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True),
                                    fromfile='a/' + path, tofile='b/' + path)
        diffs.append(''.join(line if line.endswith('\n') else line + '\n\\ No newline at end of file\n'
                             for line in delta))
    validate_mechanical_updates(context, (), tuple(updates))
    for path in paths:
        if matches(path, context.profile.protected_paths):
            raise ValueError('Document export targets a protected profile path')
    data = {'snapshot': snapshot, 'baseline': baseline, 'head': evidence.base_revision,
            'fingerprint': evidence.fingerprint, 'tree': provenance.worktree_tree, 'index_tree': provenance.index_tree,
            'documents': documents, 'mechanical': [asdict(u) for u in updates], 'diff': ''.join(diffs)}
    return {**data, 'preview_sha256': digest(data)}


def execute(context, history, request, git, journal, now):
    """Sin agentes: confirmación humana del diff, intención previa y escritor H2.4."""
    shown = request['preview']
    raw = request.get('commit_intent')
    unchanged = {p: sha for p, sha in shown['baseline'].items()
                 if p not in (context.state_file, context.next_steps_file)}
    if document_hashes(context, unchanged) != unchanged:
        return replace(history, status='stopped'), {'status': 'INVALIDATED', 'diagnostic': 'Phase documents changed after preview'}
    if raw is None:
        if git.capture(context).fingerprint != shown['fingerprint']:
            return replace(history, status='stopped'), {'status': 'INVALIDATED', 'diagnostic': 'Checkout changed after preview'}
        updates = tuple(MechanicalUpdate(**u) for u in shown['mechanical'])
        message = (f"harness: export phase {shown['snapshot']['phase']['code']} documents\n\n"
                   f"Harness-Operation: {request['operation_id']}\nHarness-Preview: {shown['preview_sha256']}\n")
        plan = CommitPlan(shown['head'], shown['tree'], updates, message, git.identity.name, git.identity.email,
                          int(now().timestamp()))
        tree, commit = git.seal(context, plan)
        intent = CommitIntent(request['operation_id'], history.id, 'DOCUMENT-EXPORT', shown['head'],
                              shown['fingerprint'], shown['tree'], shown['index_tree'], (), updates, tree, commit,
                              message, plan.author_name, plan.author_email, plan.committed_at)
        journal.export_intent(intent)
    else:
        intent = CommitIntent.from_json(raw)
    outcome = git.execute_export(context, intent, shown['documents'])
    return replace(history, status='completed' if outcome.status != 'invalidated' else 'stopped'), {
        'status': 'COMMITTED' if outcome.status != 'invalidated' else 'INVALIDATED',
        'commit': outcome.commit, 'tree': outcome.tree, 'diagnostic': outcome.diagnostic,
        'reconciled': outcome.status == 'reconciled'}

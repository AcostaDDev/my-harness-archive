"""Flujo B sobre la intención conciliable y la adopción atómica de las importaciones (0020)."""
from hashlib import sha256

from harness_local.adapters.chat_snapshot import HeadSnapshot
from harness_local.adapters.project_import import _blobs
from harness_local.adapters.project_onboarding import _InventoryGit
from harness_local.core.engine.definition import allowed_draft, definition_layout
from harness_local.core.engine.onboarding_commit import preview as build_preview
from harness_local.storage.managed import Conflict
from harness_local.storage.onboarding import OnboardingDrafts
from harness_local.storage.project_import import ImportRepository


def check_filters(context, writer):
    """El escritor Git usa add/hash-object: rechazar filtros ejecutables antes de esas operaciones."""
    git = _InventoryGit(context.root, executable=writer.executable)
    if git.run('config', '--includes', '--get-regexp', r'^filter\..*\.(clean|process)$', ok=(0, 1)).strip():
        raise ValueError('Onboarding requires no local clean/process Git filters; project code cannot be executed')


class OnboardingRepository(ImportRepository):
    kind = 'onboarding'
    drafts_class = OnboardingDrafts

    def _build_preview(self, context, conversation_id, source, record, writer):
        check_filters(context, writer)
        reader = HeadSnapshot(context.root, executable=writer.executable)
        reader.git = _InventoryGit(context.root, executable=writer.executable)
        head = reader.head()
        if head != source['inventory']['head']:
            raise Conflict('The checkout changed since the onboarding conversation started')
        entries = reader.entries(head)
        target = definition_layout(context)
        selected = {path: entry for path, entry in entries.items() if allowed_draft(target, path)}
        blobs = _blobs(reader.git, sorted({entry[0] for entry in selected.values()}))
        contents = {path: blobs[entry[0]] for path, entry in selected.items()}
        inspection = self.drafts_class.of(self.managed.engine, conversation_id).inspect_definition(context, texts=True)
        drafts = inspection.pop('texts')
        shown = build_preview(context, source, contents, entries, drafts, record, inspection, writer)
        paths = b''.join(doc['path'].encode() + b'\0' for doc in shown['documents'])
        if reader.git.run('check-ignore', '-z', '--stdin', input=paths, ok=(0, 1)).strip(b'\0'):
            raise ValueError('Onboarding document destinations are ignored by Git; review the project ignore rules')
        proposed = reader.entries(shown['proposed_tree'])
        blobs = _blobs(reader.git, sorted({proposed[doc['path']][0] for doc in shown['documents']}))
        if any(sha256(blobs[proposed[doc['path']][0]]).hexdigest() != doc['after_sha256']
               for doc in shown['documents']):
            raise ValueError('Git attributes would transform the confirmed document bytes')
        return shown

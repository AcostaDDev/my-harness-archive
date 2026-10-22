"""Flujo B sobre la intención conciliable y la adopción atómica de las importaciones (0020)."""
from harness_local.adapters.chat_snapshot import HeadSnapshot
from harness_local.adapters.import_git import _blobs
from harness_local.adapters.local_git import LocalGit
from harness_local.core.engine.definition import allowed_draft, definition_layout
from harness_local.core.engine.onboarding_commit import preview as build_preview
from harness_local.storage.managed import Conflict
from harness_local.storage.onboarding import OnboardingDrafts
from harness_local.storage.project_import import ImportRepository


class OnboardingRepository(ImportRepository):
    kind = 'onboarding'
    drafts_class = OnboardingDrafts

    def _build_preview(self, context, conversation_id, source, record, writer):
        reader = HeadSnapshot(context.root, executable=writer.executable)
        reader.git = LocalGit(context.root, executable=writer.executable)
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
        return build_preview(context, source, contents, entries, drafts, record, inspection, writer)

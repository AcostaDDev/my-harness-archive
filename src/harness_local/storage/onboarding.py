"""P008-T014: conversación de ingeniería inversa sobre HEAD; borradores privados, sin efectos en el proyecto.

Reutiliza la exportación acotada de D083, la CAS de la importación y `planning_conversations.source` (0019).
No ejecuta fuentes ni comandos del perfil propuesto. La adopción y el commit pertenecen a T015.
"""
from harness_local.adapters.chat_snapshot import HeadSnapshot
from harness_local.adapters.project_onboarding import _InventoryGit, read_inventory as inventory_of
from harness_local.core.engine.contracts import freeze
from harness_local.core.engine.definition import MAX_CONTEXT_DRAFT_BYTES, allowed_drafts_view
from harness_local.core.engine.documents import MAX_AGENTS_LINES, MAX_WRAPPER_LINES
from harness_local.core.project_onboarding import OnboardingInventoryError
from harness_local.storage.private_drafts import PrivateDrafts
from harness_local.storage.managed import Conflict


class OnboardingDrafts(PrivateDrafts):
    area = 'onboarding-drafts'


def read_inventory(context, executable='git'):
    try:
        inventory = inventory_of(context.root, executable=executable)
        target = context.state_file, context.next_steps_file
        reader = HeadSnapshot(context.root, executable=executable)
        reader.git = _InventoryGit(context.root, executable=executable)
        entries = reader.entries(inventory['head'])
        if any(path in entries for path in target) or any(path.startswith('.harness/') for path in entries):
            raise Conflict('The repository already has harness documents or history; legacy/A support has been removed; register an already managed project instead')
        if len(freeze(inventory).encode('utf-8')) > MAX_CONTEXT_DRAFT_BYTES:
            raise ValueError('Onboarding inventory exceeds the 2 MiB a turn can freeze')
        return inventory
    except OnboardingInventoryError as exc:
        raise Conflict(f'The project cannot be onboarded: {exc}') from exc


def identity(source):
    inventory = source['inventory']
    return {key: inventory[key] for key in ('head', 'tree', 'inventory_sha256')}


def observation(inspection):
    return {'drafts': dict(sorted(inspection['drafts'].items())), 'invalid': list(inspection['invalid'])}


def turn_context(target, source, texts, inspection):
    drafts = [{'path': path, 'sha256': inspection['drafts'][path], 'size': len(content.encode('utf-8')),
               'content': content} for path, content in sorted(texts.items())]
    result = {'inventory': source['inventory'], **identity(source), 'snapshot_format': 'head-export-1',
              'drafts': drafts, 'foreign': inspection['foreign'], 'invalid': inspection['invalid'],
              'allowed': allowed_drafts_view(target),
              'limits': {target.agents: MAX_AGENTS_LINES, target.claude: MAX_WRAPPER_LINES,
                         target.gemini: MAX_WRAPPER_LINES}}
    if len(freeze(result).encode('utf-8')) > MAX_CONTEXT_DRAFT_BYTES:
        raise ValueError('Onboarding inventory and drafts exceed the 2 MiB a turn can freeze')
    return result


def export_snapshot(root, head, destination, executable='git'):
    reader = HeadSnapshot(root, executable=executable)
    # The same no-lazy-fetch requirement as the inventory; no filters, hooks or project processes.
    reader.git = _InventoryGit(root, executable=executable)
    return reader.export(head, destination)

"""D088: preparación y adopción del cierre documental sobre las operaciones existentes."""

from sqlalchemy import select

from harness_local.core.engine.document_ops import preview_transition
from harness_local.core.engine.phases import document_hashes
from harness_local.storage.managed import Conflict
from harness_local.storage.models import PhaseRow as Phase


def prepare(context, state, git):
    if git is None:
        raise Conflict('Unified phase closure requires the configured Git writer')
    try:
        return preview_transition(context, state, git, None, unified=True)
    except (ValueError, OSError, UnicodeError, RuntimeError) as exc:
        raise Conflict(str(exc)) from exc


def adopt(managed, session, run, op, phase, outcome):
    from harness_local.storage.documents import observed_documents, verify_committed
    from harness_local.storage.phases import insert_phase
    verify_committed(op, outcome)
    shown = op.request['preview']
    context = observed_documents(run, shown)
    phase.status = outcome['status']
    session.flush()  # libera la restricción de una sola fase abierta antes de crear N+1
    following = shown['next']
    if following:
        if session.scalar(select(Phase.id).where(Phase.root == phase.root, Phase.code == following['code'])):
            raise Conflict('The successor already exists; reconcile the recorded closure')
        outcome = {**outcome, 'next_phase_id': insert_phase(
            managed, session, phase.root, following, document_hashes(context, following['documents']),
            source={'kind': 'closure', 'operation_id': op.id, 'from_phase': phase.code, 'commit': outcome['commit']})}
    run.status, run.stage = 'COMMITTED', 'committed'
    return outcome

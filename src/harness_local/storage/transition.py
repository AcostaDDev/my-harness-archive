"""D072/H6.3: transición de fase sobre operaciones de fase y jobs existentes; SQLite es autoridad.

Después de CLOSED (o ABANDONED) y sin tocar el cierre D032: archiva por bytes la fase, abre
STATE/NEXT_STEPS frescos e instala la fase siguiente del ROADMAP en un único commit conciliable.
La fase nueva se crea en la transacción que registra el resultado, junto a su base adoptada.
"""

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness_local.core.engine.contracts import freeze
from harness_local.core.engine.document_ops import TERMINAL, preview_transition
from harness_local.core.engine.phases import document_hashes
from harness_local.storage.documents import (
    _resume_job, abort_operation, latest_phase, observed_documents, pending, phases_snapshot,
    record_operation_intent, summary_snapshot, unresolved, verify_committed,
)
from harness_local.storage.managed import Conflict, _job
from harness_local.storage.models import ManagedRunRow as Run, PhaseOperationRow as Operation, PhaseRow as Phase
from harness_local.storage.permissions import actor
from harness_local.storage.phases import PhaseRepository, _event, _latest, _operation, insert_phase


def snapshot(session, phase) -> dict:
    """Autoridad SQLite que la vista previa congela: fase terminada, estados, check y resumen."""
    check = _latest(session, phase.id, 'check')
    result = (check.result or {}) if check is not None else {}
    codes = sorted(session.scalars(select(Phase.code).where(Phase.root == phase.root)).all())
    return {'phase': {'id': phase.id, 'code': phase.code, 'status': phase.status, 'definition': phase.definition,
                      'definition_number': phase.definition_number, 'documents': phase.documents},
            'phases': phases_snapshot(session, phase.root),
            'check': None if check is None else {
                'status': check.status, 'result': result.get('result'), 'reasons': result.get('reasons') or [],
                'binding': result.get('binding'), 'binding_sha256': result.get('binding_sha256'),
                'validation': result.get('validation')},
            'summary': summary_snapshot(session, phase), 'existing_codes': codes}


def _phase(session, context, phase_id, expected=None):
    phase = session.get(Phase, phase_id)
    if phase is None or phase.root != str(context.root):
        raise LookupError('Unknown phase in this checkout')
    if expected is not None and (type(expected) is not int or phase.version != expected):
        raise Conflict('Phase changed; reload before the transition')
    if latest_phase(session, phase.root).id != phase.id:
        raise Conflict('Only the latest phase of the checkout can be archived')
    if phase.status not in TERMINAL:
        raise Conflict('Close or abandon the phase before archiving it')
    if PhaseRepository._root_pending(session, phase.root):
        raise Conflict('Checkout has unfinished jobs; archive at a stopped boundary')
    return phase


class TransitionRepository:
    def __init__(self, managed):
        self.managed = managed

    def preview(self, context, phase_id, git, next_steps=None):
        with Session(self.managed.engine) as session:
            phase = _phase(session, context, phase_id)
            stored = pending(session, phase, 'transition')
            if stored is not None:
                return {**stored.request['preview'], 'expected_version': phase.version,
                        'resume_operation_id': stored.id}
            if unresolved(session, phase.root):
                raise Conflict('A document intent awaits reconciliation; recover it first')
            state, version = snapshot(session, phase), phase.version
        try:
            shown = preview_transition(context, state, git, next_steps)
        except (ValueError, OSError, UnicodeError, RuntimeError) as exc:  # RuntimeError: captura/sellado Git
            raise Conflict(str(exc)) from exc
        return {**shown, 'expected_version': version, 'resume_operation_id': None}

    def submit(self, context, phase_id, expected, *, key, versions, preview_sha256, reason, confirmed, git,
               next_steps=None, resume_operation_id=None):
        if confirmed is not True or not isinstance(reason, str) or not reason.strip():
            raise ValueError('Explicit confirmation of the exact diff and reason required')
        marker = freeze({'action': 'phase_transition', 'phase_id': phase_id, 'expected_version': expected,
                         'preview_sha256': preview_sha256, 'reason': reason, 'confirmed': confirmed,
                         'resume_operation_id': resume_operation_id})
        with Session(self.managed.engine) as session:
            existing = self.managed._existing(session, key, marker)
            if existing:
                return _job(existing)
        try:
            shown = self.preview(context, phase_id, git, next_steps)
        except Conflict:
            with Session(self.managed.engine) as session:
                existing = self.managed._existing(session, key, marker)
                if existing:
                    return _job(existing)
            raise
        if shown['preview_sha256'] != preview_sha256 or shown['resume_operation_id'] != resume_operation_id:
            raise Conflict('Preview changed; review the exact diff again')
        assessment = self.managed.guard.assess(context.root)
        with self.managed._write() as session:
            existing = self.managed._existing(session, key, marker)
            if existing:
                return _job(existing)
            phase = _phase(session, context, phase_id, expected)
            if shown['expected_version'] != expected:
                raise Conflict('Phase changed since preview')
            if resume_operation_id is not None:
                op = pending(session, phase, 'transition')
                if op is None or op.id != resume_operation_id:
                    raise Conflict('Only the exact interrupted transition intent can resume')
                job = _resume_job(self.managed, session, op, context, versions, key, marker, assessment,
                                  'phase_transition')
            else:
                if unresolved(session, phase.root):
                    raise Conflict('A document intent awaits reconciliation; recover it first')
                if snapshot(session, phase) != shown['snapshot']:
                    raise Conflict('SQLite authority changed after preview')
                job = self.managed._queue_new_run(session, assessment, context, versions, f'{phase.code}-TRANSITION',
                                                  phase.code, key, marker, purpose='phase_transition')
                saved = {k: v for k, v in shown.items() if k not in ('expected_version', 'resume_operation_id')}
                op = Operation(id=str(uuid4()), phase_id=phase.id, kind='transition', run_id=job.run_id,
                               status='QUEUED', previous_status=phase.status, created_at=self.managed._now(),
                               request={'preview': saved, 'actor': actor(), 'reason': reason})
                session.add(op)
            _event(self.managed, session, phase, 'phase_transition_queued', {
                'operation_id': op.id, 'run_id': job.run_id, 'job_id': job.id, 'preview_sha256': preview_sha256,
                'next': (shown['next'] or {}).get('code'), 'actor': actor(), 'reason': reason})
            return job

    def request(self, run_id):
        with Session(self.managed.engine) as session:
            op, phase = _operation(session, session.get(Run, run_id))
            if op.kind != 'transition' or op.status != 'QUEUED':
                raise Conflict('Transition requires its queued operation')
            if not op.request.get('commit_intent') and snapshot(session, phase) != op.request['preview']['snapshot']:
                raise Conflict('SQLite authority changed after the transition was reviewed')
            return {**op.request, 'operation_id': op.id}



def record_intent(managed, session, run, intent):
    def matches(session, phase):
        op, _ = _operation(session, run)
        return snapshot(session, phase) == op.request['preview']['snapshot']
    record_operation_intent(managed, session, run, intent, 'transition', matches)


def settle(managed, session, run, outcome):
    op, phase = _operation(session, run)
    if op.status not in ('QUEUED', 'INTENT'):
        raise Conflict('Transition already settled')
    shown = op.request['preview']
    if outcome['status'] == 'COMMITTED':
        verify_committed(op, outcome)
        context = observed_documents(run, shown)
        following = shown['next']
        if following is not None:
            if session.scalar(select(Phase.id).where(Phase.root == phase.root, Phase.code == following['code'])):
                raise Conflict(f"Phase {following['code']} already exists; recover manually with the recorded evidence")
            if session.scalar(select(Phase.id).where(Phase.root == phase.root, Phase.status.notin_(TERMINAL))):
                raise Conflict('Another phase is open; recover manually with the recorded evidence')
            documents = document_hashes(context, following['documents'])
            outcome = {**outcome, 'next_phase_id': insert_phase(
                managed, session, phase.root, following, documents,
                source={'kind': 'transition', 'operation_id': op.id, 'from_phase': phase.code,
                        'commit': outcome['commit']})}
        run.status, run.stage = 'COMMITTED', 'committed'
    op.status, op.result, op.finished_at = outcome['status'], outcome, managed._now()
    _event(managed, session, phase, 'phase_transitioned' if outcome['status'] == 'COMMITTED'
           else 'phase_transition_invalidated', {'operation_id': op.id, 'archive': shown['archive'], **outcome})


def abort(managed, session, run, status, reason):
    abort_operation(managed, session, run, status, reason, 'transition')

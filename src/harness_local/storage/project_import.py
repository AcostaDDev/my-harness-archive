"""P008-T012: importación confirmada, con intención previa y adopción atómica de la fase."""
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness_local.adapters.import_git import check_filters, check_submodules, check_tree
from harness_local.adapters.git import GitWorkspace
from harness_local.adapters.local_git import LocalGit
from harness_local.core.engine.contracts import context_snapshot, freeze
from harness_local.core.engine.import_commit import seal
from harness_local.core.engine.commit import CommitIntent
from harness_local.storage.managed import Conflict, _job
from harness_local.storage.models import (
    ProjectImportRow as Import, ManagedRunRow as Run, ManagedJobRow as Job,
    PlanningConversationRow as Conversation, PlanningTurnRow as Turn,
)
from harness_local.storage.permissions import actor


def unresolved(session, root):
    return session.scalar(select(Import.id).where(Import.root == root, Import.status != 'COMPLETED')) is not None


def _operation(session, run):
    op = session.scalar(select(Import).where(Import.run_id == run.id))
    if op is None:
        raise Conflict('Import run lacks its operation')
    return op


def check_git(context, writer, shown=None, tree=None):
    """Shared onboarding boundary, including execution and sealed-intent recovery."""
    if isinstance(writer, GitWorkspace):
        # La guardia y todas las operaciones posteriores del escritor comparten la frontera local,
        # incluidas code(), recaptura, sellado, conciliación y refresco del índice.
        writer.local_objects_only = True
    git = LocalGit(context.root, executable=writer.executable, timeout=writer.timeout)
    check_filters(git)
    check_submodules(git)
    git.require_tree('HEAD')
    if shown is not None:
        proposed = tree or shown['proposed_tree']
        git.require_tree(proposed)
        check_tree(git, proposed, shown['result_tree'], shown['documents'])


def settle(managed, session, run, outcome):
    from harness_local.storage.phases import insert_phase
    from harness_local.core.engine.phases import document_hashes
    from harness_local.core.engine.serialization import restore_context
    op = _operation(session, run)
    intent = CommitIntent.from_json(op.intent)
    if op.status != 'QUEUED':
        raise Conflict('Import already settled')
    if outcome['status'] == 'COMMITTED':
        if outcome['commit'] != intent.expected_commit or outcome['tree'] != intent.expected_tree:
            raise Conflict('Import result differs from its sealed intent')
        baseline = op.preview['baseline']
        if document_hashes(restore_context(run.context_json), baseline) != baseline:
            raise Conflict('Import documents changed before adoption; reconcile the recorded intent')
        pid = insert_phase(managed, session, op.root, op.preview['phase'], baseline,
                           source={'import_id': op.id, 'run_id': run.id, 'commit': outcome['commit']})
        op.phase_id, op.status = pid, 'COMPLETED'
        run.status, run.stage = 'COMMITTED', 'committed'
    else:
        op.status = 'INTERRUPTED'
    op.result, op.finished_at = outcome, managed._now()
    managed._event(session, run, 'import_settled', {'operation_id': op.id, 'phase_id': op.phase_id, **outcome})


def abort(managed, session, run, status, reason):
    op = _operation(session, run)
    op.status, op.finished_at = 'INTERRUPTED', managed._now()
    op.result = {'reason': reason, 'effect': 'uncertain', 'job_status': status}
    managed._event(session, run, 'import_interrupted', {'operation_id': op.id, 'reason': reason})


class ImportRepository:
    kind = 'onboarding'
    drafts_class = None

    def __init__(self, managed):
        self.managed = managed

    def get(self, root):
        with Session(self.managed.engine) as session:
            op = session.scalar(select(Import).where(Import.root == str(root)))
            if op is None:
                return None
            run = session.get(Run, op.run_id)
            from harness_local.storage.retired_work import reason
            if reason(session, run):
                raise Conflict('Legacy/A or ambiguous operation is retained as data only; it cannot be onboarded')
            return {**{key: getattr(op, key) for key in ('id', 'root', 'conversation_id', 'run_id', 'phase_id',
                'status', 'preview', 'decision', 'result', 'created_at', 'finished_at')},
                'expected_version': run.version, 'run_status': run.status}

    @staticmethod
    def _idle(session, root):
        if session.scalar(select(Job.id).join(Run, Run.id == Job.run_id).where(Run.root == root,
                          Job.status.in_(('QUEUED', 'ACTIVE', 'RECOVERY_REQUIRED')))):
            raise Conflict('Checkout has unfinished jobs; confirm stopped writers before importing')

    def preview(self, context, conversation_id, versions, writer):
        with Session(self.managed.engine) as session:
            row = session.get(Conversation, conversation_id)
            if row is None or row.root != str(context.root):
                raise LookupError('Unknown conversation of this checkout')
            if row.kind != self.kind:
                raise Conflict('The conversation belongs to another import flow')
        saved = self.get(context.root)
        if saved is not None:
            if saved['conversation_id'] != conversation_id:
                raise Conflict('Import already exists; inspect the confirmed conversation')
            if saved['status'] == 'INTERRUPTED':
                try:
                    check_git(context, writer, saved['preview'])
                except (ValueError, OSError, RuntimeError) as exc:
                    raise Conflict(str(exc)) from exc
                return {**saved['preview'], 'resume_operation_id': saved['id'],
                        'expected_version': saved['expected_version']}
            if saved['status'] == 'COMPLETED':
                return {**saved['preview'], 'already_imported': True, 'documents': [], 'mechanical': [],
                        'diff': '', 'resume_operation_id': None, 'expected_version': saved['expected_version']}
            raise Conflict('Import is already queued')
        from harness_local.storage.planning import PlanningRepository
        planning = PlanningRepository(self.managed)
        with Session(self.managed.engine) as session:
            row = planning._conversation(session, conversation_id, context=context)
            if row.kind != self.kind:
                raise Conflict('Only an import conversation can normalize the project')
            planning._importable(session, str(context.root))
            self._idle(session, str(context.root))
            record, source = planning._record(session, row), row.source
            record['pending_turn'] = session.scalar(select(Turn.id).where(
                Turn.conversation_id == row.id, Turn.status == 'QUEUED')) is not None
        assessment = self.managed.guard.assess(context.root)
        if assessment.refusal:
            raise Conflict(assessment.refusal)
        try:
            check_git(context, writer)
            shown = self._build_preview(context, conversation_id, source, record, writer)
            check_git(context, writer, shown)
        except (ValueError, OSError, RuntimeError) as exc:
            raise Conflict(str(exc)) from exc
        shown = {**shown, 'versions': versions, 'context': context_snapshot(context)}
        from harness_local.core.engine.phases import digest
        shown['preview_sha256'] = digest({k: v for k, v in shown.items() if k != 'preview_sha256'})
        return {**shown, 'resume_operation_id': None, 'expected_version': None, 'already_imported': False}

    def _build_preview(self, *args):
        raise NotImplementedError("Use the onboarding repository")

    def submit(self, context, conversation_id, versions, writer, *, key, preview_sha256, reason, confirmed,
               resume_operation_id=None, expected_version=None, profile_sha256=None):
        if confirmed is not True or not isinstance(reason, str) or not reason.strip():
            raise ValueError('Explicit confirmation of the exact import and a reason required')
        confirmation = {'profile_sha256': profile_sha256} if self.kind == 'onboarding' else {}
        marker = freeze({'action': 'import_commit', 'root': str(context.root), 'conversation_id': conversation_id,
            'preview_sha256': preview_sha256, 'reason': reason, 'confirmed': confirmed,
            'resume_operation_id': resume_operation_id, 'expected_version': expected_version, **confirmation})
        with Session(self.managed.engine) as session:
            if existing := self.managed._existing(session, key, marker):
                return _job(existing)
        shown = self.preview(context, conversation_id, versions, writer)
        if self.kind == 'onboarding' and (not profile_sha256 or profile_sha256 != shown['profile_sha256']):
            raise Conflict('Explicit confirmation of the composition profile hash required')
        if (shown.get('already_imported') or not shown['mechanical'] or shown['preview_sha256'] != preview_sha256
                or shown['resume_operation_id'] != resume_operation_id or shown['expected_version'] != expected_version):
            raise Conflict('Import preview changed or has no changes; review it again')
        assessment = self.managed.guard.assess(context.root)
        with self.managed._write() as session:
            if existing := self.managed._existing(session, key, marker):
                return _job(existing)
            self._idle(session, str(context.root))
            if resume_operation_id:
                op = session.get(Import, resume_operation_id)
                if (op is None or op.root != str(context.root) or op.status != 'INTERRUPTED'
                        or op.conversation_id != conversation_id):
                    raise Conflict('Only the exact interrupted import can resume')
                run = session.get(Run, op.run_id)
                if (run.version != expected_version or run.context_json != context_snapshot(context)
                        or run.versions_json != freeze(versions) or shown['author'] != {
                            'name': writer.identity.name, 'email': writer.identity.email}):
                    raise Conflict('Frozen import context/versions/writer changed; restore before resuming')
                job = Job(idempotency_key=key, run_id=run.id, request_json=marker, status='QUEUED',
                    created_at=self.managed._now(), activation_id=self.managed._admit(session, assessment))
                session.add(job)
                session.flush()
                run.status, run.stage, op.status, op.finished_at = 'QUEUED', 'import_commit', 'QUEUED', None
                job = _job(job)
            else:
                from harness_local.storage.planning import PlanningRepository
                PlanningRepository._importable(session, str(context.root))
                origin = shown['origin']
                conversation = session.get(Conversation, conversation_id)
                if conversation.version != origin['conversation_version']:
                    raise Conflict('Import conversation changed since preview')
                area = self.drafts_class.of(self.managed.engine, conversation_id).inspect_definition(context)
                if area['drafts'] != origin['drafts'] or area['invalid']:
                    raise Conflict('Import drafts changed since preview')
                job = self.managed._queue_new_run(session, assessment, context, versions, 'IMPORT',
                    shown['phase']['code'], key, marker, purpose='import_commit')
                operation_id = str(uuid4())
                check_git(context, writer, shown)
                intent = seal(context, shown, writer, operation_id, job.run_id, int(self.managed.clock().timestamp()))
                op = Import(id=operation_id, root=str(context.root), conversation_id=conversation_id,
                    run_id=job.run_id, status='QUEUED', preview={k: v for k, v in shown.items()
                        if k not in ('resume_operation_id', 'expected_version', 'already_imported')},
                    intent=intent.to_json(), decision={'actor': actor(), 'reason': reason, 'confirmed': True,
                                                      **confirmation},
                    created_at=self.managed._now())
                session.add(op)
            self.managed._event(session, session.get(Run, job.run_id), 'import_confirmed', {
                'operation_id': op.id, 'preview_sha256': preview_sha256, 'reason': reason, 'actor': actor()})
            return job

    def request(self, run_id):
        with Session(self.managed.engine) as session:
            run = session.get(Run, run_id)
            from harness_local.storage.retired_work import reason
            if diagnostic := reason(session, run):
                raise Conflict(diagnostic)
            op = _operation(session, run)
            if op.status != 'QUEUED':
                raise Conflict('Import requires its queued operation')
            return {'preview': op.preview, 'intent': op.intent}

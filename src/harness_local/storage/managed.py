"""Autoridad H2.2. Toda transacción escritora termina antes de ejecutar puertos.

FIFO entre jobs elegibles, un escritor por raíz dentro de esta base. El lease
no libera el checkout: un ejecutor de resultado incierto requiere conciliación.
"""

from contextlib import contextmanager
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select, text, func, or_
from sqlalchemy.orm import Session

from harness_local.core.engine.commit import (
    CommitError, CommitIntent, CommitOutcome, MechanicalUpdate, git_provenance, validate_mechanical_updates,
)
from harness_local.core.engine.context import ProjectContext
from harness_local.core.engine.contracts import (
    AgentRequest, AgentResult, Attempt, RunHistory, context_snapshot, freeze, stop_history,
)
from harness_local.core.engine.serialization import dump_history, load_history, restore_context, restore_request
from harness_local.storage.models import (
    CheckoutLockRow as Lock, ManagedAttemptRow as AttemptRow, ManagedEventRow as Event,
    ManagedJobRow as Job, ManagedRunRow as Run, ManagedProcessRow as Process,
    ManagedCommitRow as Commit,
)
from harness_local.storage.migration import ModeConflict, ModeGuard
from harness_local.storage.metrics import executor_round, record as record_metrics
from harness_local.storage.schema import require_schema


class Conflict(ValueError):
    pass


class OwnershipLost(RuntimeError):
    pass


@dataclass(frozen=True)
class JobRecord:
    id: int
    run_id: str
    status: str
    request_json: str
    owner_token: str | None


@dataclass(frozen=True)
class RunRecord:
    history: RunHistory
    versions_json: str
    status: str
    stage: str
    version: int
    revisions: int


@dataclass(frozen=True)
class CommitRecord:
    operation_id: str
    run_id: str
    status: str
    intent: CommitIntent
    outcome: CommitOutcome | None
    commit: str | None


def _commit(row: Commit) -> CommitRecord:
    return CommitRecord(row.operation_id, row.run_id, row.status, CommitIntent.from_json(row.intent_json),
                        CommitOutcome.from_json(row.result_json) if row.result_json else None, row.commit_sha)


def _job(row: Job) -> JobRecord:
    return JobRecord(row.id, row.run_id, row.status, row.request_json, row.owner_token)


def _nonempty(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Explicit {name} required")


def existing_creation(session, row_type, key, request_sha256):
    """Alta sin job (conversaciones, 0018): misma clave y misma petición devuelven el mismo id."""
    _nonempty(key, "idempotency key")
    if len(key) > 200:
        raise ValueError("Idempotency key exceeds 200 characters")
    row = session.scalar(select(row_type).where(row_type.idempotency_key == key))
    if row is not None and row.request_sha256 != request_sha256:
        raise Conflict("Idempotency key already names a different conversation")
    return None if row is None else row.id


def independent_chat(job):
    return json.loads(job.request_json).get('action') in ('chat_snapshot', 'chat_command')


def _operation_module(run):
    """Autoridad del resultado de un run que no es de tarea: fase (H3.3) o turno de chat (H4.1)."""
    if run.purpose == "bootstrap_discovery":
        from harness_local.storage import bootstrap_discovery
        return bootstrap_discovery
    if run.purpose == "bootstrap":
        from harness_local.storage import bootstrap
        return bootstrap
    if run.purpose == "chat":
        from harness_local.storage import chat
        return chat
    if run.purpose == "document_export":
        from harness_local.storage import document_export
        return document_export
    if run.purpose == "document_edit":
        from harness_local.storage import documents
        return documents
    if run.purpose == "phase_transition":
        from harness_local.storage import transition
        return transition
    if run.purpose in ("definition", "phase_planning"):
        from harness_local.storage import planning
        return planning
    from harness_local.storage import phases
    return phases


def _lease(seconds: float) -> None:
    if not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or seconds <= 0:
        raise ValueError("Lease must be positive and finite")


class SQLiteManagedRepository:
    def __init__(self, engine, *, clock=None, mode_probe=None):
        require_schema(engine)
        self.engine = engine
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        # H2.5: exclusión legacy/gestionado. Checkouts sin estado legacy no cambian de comportamiento.
        self.guard = ModeGuard(engine, mode_probe)

    def _now(self) -> str:
        value = self.clock()
        if value.tzinfo is None:
            raise ValueError("Clock must return an aware UTC time")
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds")

    @contextmanager
    def _write(self):
        with Session(self.engine) as session, session.begin():
            # Primera operación DML: obtiene el lock SQLite antes de consultar.
            session.execute(text("UPDATE managed_runs SET version = version WHERE 0"))
            yield session

    def _event(self, session, run, kind, payload):
        run.version += 1
        run.updated_at = self._now()
        session.add(Event(run_id=run.id, sequence=run.version, kind=kind, recorded_at=run.updated_at,
                          payload={**payload, "status": run.status, "stage": run.stage,
                                   "revisions": run.revisions}))

    def _admit(self, session, assessment) -> str | None:
        try:
            return ModeGuard.enforce(session, assessment)
        except ModeConflict as exc:
            raise Conflict(str(exc)) from exc

    def _run_root(self, run_id: str) -> str | None:
        with Session(self.engine) as session:
            return session.scalar(select(Run.root).where(Run.id == run_id))

    def mode_refusal(self, claim: JobRecord) -> str | None:
        """Lectura de disco fuera de transacción: el modo del checkout sigue admitiendo este job."""
        with Session(self.engine) as session:
            job = session.get(Job, claim.id)
            if job is None:
                raise LookupError("Unknown managed job")
            root, admitted = session.get(Run, job.run_id).root, job.activation_id
        assessment = self.guard.assess(root)
        if assessment.refusal is not None:
            return assessment.refusal
        current = assessment.activation.id if assessment.activation else None
        if current != admitted:
            return "El modo del checkout cambió desde que se admitió el job; no se ejecuta."
        return None

    def _require_mode(self, claim: JobRecord) -> None:
        refusal = self.mode_refusal(claim)
        if refusal is not None:
            raise Conflict(refusal)

    def refuse(self, claim: JobRecord, diagnostic: str) -> None:
        """Job reclamado que no llegó a registrar propietario ni efectos: se cierra y libera el lock."""
        _nonempty(diagnostic, "refusal diagnostic")
        with self._write() as session:
            job, run = self._owned(session, claim)
            if job.process_owner is not None:
                raise Conflict("The job already registered a process owner; quarantine instead")
            history = load_history(run.history_json)
            job.status, job.finished_at, job.diagnostic = "REFUSED", self._now(), diagnostic
            run.status = (history.status.upper()
                          if history.status in {"stopped", "blocked", "revision_limit", "acceptance_ready"}
                          else "REFUSED")
            if self._live_commit(session, run.id, ("COMMITTED",)) is not None:
                run.status = "COMMITTED"
            run.stage = "mode_guard"
            self._release(session, job, run)
            self._event(session, run, "job_refused", {"job_id": job.id, "diagnostic": diagnostic})
            if run.purpose != "task":
                _operation_module(run).abort(self, session, run, "REFUSED", diagnostic)

    def _existing(self, session, key, request):
        _nonempty(key, "idempotency key")
        if len(key) > 200:
            raise ValueError("Idempotency key exceeds 200 characters")
        row = session.scalar(select(Job).where(Job.idempotency_key == key))
        if row and row.request_json != request:
            raise Conflict("Idempotency key already names a different action")
        return row

    def submit(self, context: ProjectContext, task_id: str, phase_id: str, text: str,
               versions: dict, *, key: str) -> JobRecord:
        for value, name in ((task_id, "task identity"), (phase_id, "phase identity"), (text, "plan text")):
            _nonempty(value, name)
        if (not isinstance(versions, dict)
                or not {"engine", "agent_adapter", "commands", "evidence"} <= versions.keys()
                or not all(isinstance(k, str) and k and (v is None or isinstance(v, str) and v.strip())
                           for k, v in versions.items())):
            raise ValueError("Explicit component versions required; unknown values use null")
        if Path(self.engine.url.database).resolve().is_relative_to(context.root):
            raise ValueError("Managed SQLite must be outside the agent checkout")
        request = freeze({"action": "start", "context_json": context_snapshot(context),
                          "versions_json": freeze(versions), "task_id": task_id, "phase_id": phase_id, "text": text})
        assessment = self.guard.assess(context.root)
        with self._write() as session:
            existing = self._existing(session, key, request)
            if existing:
                return _job(existing)
            return self._queue_new_run(session, assessment, context, versions, task_id, phase_id, key, request)

    def _queue_new_run(self, session, assessment, context, versions, task_id, phase_id, key, request,
                       purpose="task"):
        """Run nuevo y su primer job en la transacción del llamante (tareas y operaciones de fase H3.3)."""
        if purpose != "bootstrap":
            from harness_local.storage.bootstrap import unresolved
            if unresolved(session, str(context.root)):
                raise Conflict('Bootstrap awaits completion or explicit recovery')
        if purpose == "task":
            self._phase_open(session, str(context.root), phase_id)
        activation_id = self._admit(session, assessment)
        snapshot = context_snapshot(context)
        history = RunHistory(str(uuid4()), snapshot)
        now = self._now()
        action = json.loads(request)["action"]
        run = Run(id=history.id, root=str(context.root), task_id=task_id, phase_id=phase_id,
                  context_json=snapshot, versions_json=freeze(versions), history_json=dump_history(history),
                  status="QUEUED", stage=action, revisions=0, purpose=purpose,
                  revision_limit=context.policy.max_revision_cycles, version=0, created_at=now, updated_at=now)
        session.add(run)
        session.flush()
        job = Job(idempotency_key=key, run_id=run.id, request_json=request, status="QUEUED", created_at=now,
                  activation_id=activation_id)
        session.add(job)
        session.flush()
        self._event(session, run, "job_queued", {"job_id": job.id, "action": action})
        return _job(job)

    @staticmethod
    def _phase_open(session, root, code):
        """H3.3/H3.4: una fase cerrada, cerrándose o abandonada no acepta tareas, reanudaciones ni commits."""
        from harness_local.storage.models import PhaseRow
        from harness_local.storage.documents import unresolved
        if unresolved(session, root):
            raise Conflict('A document intent awaits reconciliation; recover it first')
        if session.scalar(select(PhaseRow.id).where(PhaseRow.root == root, PhaseRow.code == code,
                                                    PhaseRow.status.in_(("CLOSED", "CLOSING", "ABANDONED")))):
            raise Conflict("The phase is closed, closing or abandoned in this checkout; it does not advance")

    def resume(self, run_id: str, *, key: str, expected_version: int, retry_executor=False) -> JobRecord:
        if type(expected_version) is not int or type(retry_executor) is not bool:
            raise ValueError("Explicit resource version and boolean retry required")
        request = freeze({"action": "retry" if retry_executor else "revalidate", "run_id": run_id,
                          "expected_version": expected_version})
        root = self._run_root(run_id)
        assessment = self.guard.assess(root) if root is not None else None
        with self._write() as session:
            existing = self._existing(session, key, request)
            if existing:
                return _job(existing)
            run = session.get(Run, run_id)
            if run is None:
                raise LookupError("Unknown managed run")
            history = load_history(run.history_json)
            if run.version != expected_version:
                raise Conflict("Run changed; reload before resuming")
            if session.scalar(select(Job.id).where(Job.run_id == run_id,
                    Job.status.in_(("QUEUED", "ACTIVE", "RECOVERY_REQUIRED")))) is not None:
                raise Conflict("Run already has unfinished work")
            if session.scalar(select(Commit.operation_id).where(
                    Commit.run_id == run_id, Commit.status.in_(("INTENT", "COMMITTED")))) is not None:
                raise Conflict("Run has a recorded or pending commit operation; reconcile it instead")
            if history.status not in {"stopped", "blocked", "revision_limit"} or history.task_json is None:
                raise Conflict("Only a stopped run with a frozen contract can resume")
            if retry_executor and not json.loads(history.task_json)["allowed_paths"]:
                raise Conflict("Read-only tasks cannot retry implementation")
            self._phase_open(session, run.root, run.phase_id)
            activation_id = self._admit(session, assessment)
            job = Job(idempotency_key=key, run_id=run_id, request_json=request, status="QUEUED", created_at=self._now(),
                      activation_id=activation_id)
            session.add(job)
            session.flush()
            run.status, run.stage = "QUEUED", json.loads(request)["action"]
            self._event(session, run, "job_queued", {"job_id": job.id, "action": run.stage})
            return _job(job)

    def get_run(self, run_id: str) -> RunRecord:
        with Session(self.engine) as session:
            row = session.get(Run, run_id)
            if row is None:
                raise LookupError("Unknown managed run")
            return RunRecord(load_history(row.history_json), row.versions_json, row.status,
                             row.stage, row.version, row.revisions)

    def get_job(self, job_id: int) -> JobRecord:
        with Session(self.engine) as session:
            row = session.get(Job, job_id)
            if row is None:
                raise LookupError("Unknown managed job")
            return _job(row)

    def events(self, run_id: str, *, after=0, limit=100):
        if type(after) is not int or after < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError("Invalid managed event page")
        with Session(self.engine) as session:
            rows = session.scalars(select(Event).where(Event.run_id == run_id, Event.sequence > after)
                                   .order_by(Event.sequence).limit(limit)).all()
            return [{"id": row.id, "sequence": row.sequence, "kind": row.kind,
                     "recorded_at": row.recorded_at, "payload": row.payload} for row in rows]

    def claim(self, *, lease_seconds=30, lane=None) -> JobRecord | None:
        _lease(lease_seconds)
        with self._write() as session:
            # FIFO de trabajos elegibles: otro checkout puede avanzar mientras uno está bloqueado.
            independent = func.json_extract(Job.request_json, '$.action').in_(['chat_snapshot', 'chat_command'])
            query = select(Job).join(Run, Run.id == Job.run_id).where(
                Job.status == "QUEUED", or_(independent, ~Run.root.in_(select(Lock.root))))
            if lane is not None:
                query = query.where(independent if lane == 'chat' else ~independent)
            job = session.scalar(query.order_by(Job.id).limit(1))
            if job is None:
                return None
            run = session.get(Run, job.run_id)
            now = self._now()
            job.status, job.owner_token = "ACTIVE", str(uuid4())
            job.heartbeat_at = now
            job.lease_until = (datetime.fromisoformat(now) + timedelta(seconds=lease_seconds)).isoformat(timespec="microseconds")
            if not independent_chat(job):
                session.add(Lock(root=run.root, job_id=job.id))
            run.status, run.stage = "ACTIVE", json.loads(job.request_json)["action"]
            self._event(session, run, "job_claimed", {"job_id": job.id, "owner_token": job.owner_token})
            return _job(job)

    def _owned(self, session, claim):
        job = session.get(Job, claim.id)
        if (job is None or not claim.owner_token or job.owner_token != claim.owner_token
                or job.status != "ACTIVE" or job.lease_until <= self._now()):
            raise OwnershipLost("Job lease/ownership lost; reconciliation required")
        run = session.get(Run, job.run_id)
        lock = session.get(Lock, run.root)
        if not independent_chat(job) and (lock is None or lock.job_id != job.id):
            raise OwnershipLost("Checkout writer lock lost")
        return job, run

    def _release(self, session, job, run):
        if independent_chat(job):
            from harness_local.adapters.chat_snapshot import cleanup
            cleanup(self, job)
        else:
            session.delete(session.get(Lock, run.root))

    def heartbeat(self, claim: JobRecord, *, lease_seconds=30) -> None:
        _lease(lease_seconds)
        with self._write() as session:
            job, _ = self._owned(session, claim)
            job.heartbeat_at = self._now()
            job.lease_until = (datetime.fromisoformat(job.heartbeat_at) + timedelta(seconds=lease_seconds)).isoformat(timespec="microseconds")

    def _history(self, session, run, history):
        previous = load_history(run.history_json)
        if history.id != run.id or history.context_json != run.context_json:
            raise Conflict("Frozen run identity/context changed")
        if previous.task_json is not None and history.task_json != previous.task_json:
            raise Conflict("Frozen task contract changed")
        if history.task_json is not None:
            task = json.loads(history.task_json)
            if task.get("task_id") != run.task_id or task.get("phase_id") != run.phase_id:
                raise Conflict("Frozen task identity must match the managed run")
        if (history.attempts[:len(previous.attempts)] != previous.attempts
                or history.preparation_json[:len(previous.preparation_json)] != previous.preparation_json
                or history.stops[:len(previous.stops)] != previous.stops
                or len(history.cycles) < len(previous.cycles)):
            raise Conflict("Managed history cannot be discarded or replaced")
        for old, new in zip(previous.cycles, history.cycles):
            if old != new and (old.review_json is not None or replace(new, review_json=None) != old):
                raise Conflict("Recorded validation/review cannot change")
        completed = []
        roles = [attempt.request.role for attempt in history.attempts]
        for number, attempt in enumerate(history.attempts, start=1):
            row = session.get(AttemptRow, attempt.request.id)
            if (row is None or row.run_id != run.id or row.number != number
                    or restore_request(json.loads(row.request_json)) != attempt.request):
                raise Conflict("Attempt requires a previously persisted invocation intent")
            result = freeze(asdict(attempt.result))
            if row.result_json is not None and freeze(asdict(AgentResult(**json.loads(row.result_json)))) != result:
                raise Conflict("Frozen attempt result changed")
            if row.result_json is None:
                row.result_json, row.status, row.finished_at = result, (attempt.result.status or "COMPLETED").upper(), self._now()
                completed.append(row.id)
                # H6.4: métricas materializadas en la misma transacción que el resultado del intento.
                record_metrics(session, run, row, executor_round=executor_round(roles, number), recorded_at=row.finished_at)
        run.history_json = dump_history(history)
        run.revisions = history.revisions
        return completed

    def checkpoint(self, claim: JobRecord, history: RunHistory, stage: str) -> None:
        with self._write() as session:
            job, run = self._owned(session, claim)
            completed = self._history(session, run, history)
            run.stage = stage
            run.status = {"planner": "PLANNING", "executor": "EXECUTING", "preparation": "PREPARING",
                          "validation": "VALIDATING", "reviewer": "REVIEWING"}.get(stage, "ACTIVE")
            self._event(session, run, "checkpoint", {"job_id": job.id, "history_status": history.status,
                                                    "completed_attempts": completed})

    def agent_started(self, claim: JobRecord, history: RunHistory, request: AgentRequest) -> AgentRequest:
        self._require_mode(claim)
        with self._write() as session:
            job, run = self._owned(session, claim)
            self._history(session, run, history)
            if request.context_json != run.context_json or request.task_json != history.task_json or not request.fresh_session:
                raise Conflict("Attempt must use frozen context/task and a fresh session")
            attempts = session.scalars(select(AttemptRow).where(AttemptRow.run_id == run.id)
                                      .order_by(AttemptRow.number)).all()
            if any(row.result_json is None for row in attempts):
                raise Conflict("An earlier invocation still has an unknown outcome")
            executions = sum(json.loads(row.request_json)["role"] == "executor" for row in attempts)
            if request.role == "executor":
                run.revisions = max(0, executions)
                if run.revisions > run.revision_limit:
                    raise Conflict("Persisted correction budget exhausted")
            from harness_local.storage.permissions import authorize
            request = authorize(session, self, run, request)
            session.add(AttemptRow(id=request.id, run_id=run.id, number=len(attempts) + 1,
                                  request_json=freeze(asdict(request)), versions_json=run.versions_json,
                                  status="ACTIVE", started_at=self._now()))
            run.stage = request.role
            run.status = {"planner": "PLANNING", "executor": "EXECUTING", "reviewer": "REVIEWING",
                          "phase": "CHECKING", "chat": "ANSWERING", "bootstrap": "DISCOVERING",
                          "definition": "ANSWERING", "planning": "ANSWERING"}[request.role]
            self._event(session, run, "attempt_started", {"job_id": job.id, "attempt_id": request.id,
                                                        "number": len(attempts) + 1, "role": request.role})
            return request

    def effect(self, claim: JobRecord, kind: str, payload: dict) -> None:
        with self._write() as session:
            job, run = self._owned(session, claim)
            self._event(session, run, kind, {**payload, "job_id": job.id})

    def finish(self, claim: JobRecord, history: RunHistory, outcome: dict | None = None) -> None:
        """`outcome`: resultado de una operación de fase (H3.3) o de un turno de chat (H4.1), aplicado en
        la misma transacción."""
        with self._write() as session:
            job, run = self._owned(session, claim)
            terminal = {"stopped", "completed"} if run.purpose != "task" else {
                "stopped", "blocked", "revision_limit", "acceptance_ready"}
            if history.status not in terminal or (outcome is None) != (run.purpose == "task"):
                raise Conflict("Only a terminal engine action can finish a job")
            self._history(session, run, history)
            if session.scalar(select(AttemptRow.id).where(AttemptRow.run_id == run.id,
                    AttemptRow.result_json.is_(None))) is not None:
                raise Conflict("Cannot finish with an unknown invocation outcome")
            self._processes_stopped(session, job)
            run.status = history.status.upper()
            run.stage = history.stop.stage if history.stop else "finished"
            if self._live_commit(session, run.id, ("COMMITTED",)) is not None:
                run.status, run.stage = "COMMITTED", "committed"
            if outcome is not None:
                _operation_module(run).settle(self, session, run, outcome)
            job.status, job.finished_at = "DONE", self._now()
            self._release(session, job, run)
            self._event(session, run, "job_finished", {"job_id": job.id, "history_status": history.status})

    def quarantine(self, claim: JobRecord, reason: str) -> None:
        """Sin liberar el escritor ni inferir que un proceso terminó."""
        _nonempty(reason, "recovery reason")
        with self._write() as session:
            job = session.get(Job, claim.id)
            if job is None or job.owner_token != claim.owner_token or job.status not in {"ACTIVE", "RECOVERY_REQUIRED"}:
                raise OwnershipLost("Cannot quarantine a different/finished owner")
            if job.status == "RECOVERY_REQUIRED":
                return
            job.status, job.diagnostic = "RECOVERY_REQUIRED", reason
            run = session.get(Run, job.run_id)
            run.status = "RECOVERY_REQUIRED"
            self._event(session, run, "recovery_required", {"job_id": job.id, "reason": reason})

    def recover_expired(self) -> list[int]:
        """Conciliar al iniciar/periódicamente. Nunca reencola ni libera locks."""
        with self._write() as session:
            rows = session.scalars(select(Job).where(Job.status == "ACTIVE", Job.lease_until <= self._now())
                                   .order_by(Job.id)).all()
            for job in rows:
                job.status, job.diagnostic = "RECOVERY_REQUIRED", "Lease expired; previous executor may still be alive"
                run = session.get(Run, job.run_id)
                run.status = "RECOVERY_REQUIRED"
                self._event(session, run, "recovery_required", {"job_id": job.id, "reason": job.diagnostic})
            return [job.id for job in rows]

    def confirm_stopped(self, job_id: int, *, owner_token: str, expected_version: int, reason: str) -> None:
        """Acción explícita DESPUÉS de descartar al escritor anterior; no prueba su muerte."""
        _nonempty(reason, "confirmation evidence")
        with self._write() as session:
            job = session.get(Job, job_id)
            if job is None or job.owner_token != owner_token or job.status != "RECOVERY_REQUIRED":
                raise Conflict("Confirm the exact quarantined owner before unlocking")
            run = session.get(Run, job.run_id)
            if run.version != expected_version:
                raise Conflict("Run changed; reload before reconciling")
            self._processes_stopped(session, job, recovering=True)
            history = load_history(run.history_json)
            pending = session.scalars(select(AttemptRow).where(AttemptRow.run_id == run.id,
                                      AttemptRow.result_json.is_(None)).order_by(AttemptRow.number)).all()
            for row in pending:
                result = AgentResult(None, error="Interrupted invocation; outcome unknown, no automatic retry")
                row.status, row.result_json, row.finished_at = "INTERRUPTED", freeze(asdict(result)), self._now()
                history = replace(history, attempts=history.attempts + (Attempt(restore_request(json.loads(row.request_json)), result),))
                record_metrics(session, run, row, recorded_at=row.finished_at, executor_round=executor_round(
                    [attempt.request.role for attempt in history.attempts], row.number))
            history = stop_history(history, run.stage, reason)
            self._history(session, run, history)
            run.status = "COMMITTED" if self._live_commit(session, run.id, ("COMMITTED",)) else "INTERRUPTED"
            job.status, job.finished_at, job.diagnostic = "INTERRUPTED", self._now(), reason
            self._release(session, job, run)
            self._event(session, run, "writer_stopped_confirmed", {"job_id": job.id, "owner_token": owner_token, "reason": reason})
            if run.purpose != "task":
                _operation_module(run).abort(self, session, run, "INTERRUPTED", reason)


    # --- H2.4: commit aceptado ----------------------------------------------------

    @staticmethod
    def _live_commit(session, run_id, statuses=("INTENT", "COMMITTED")):
        return session.scalar(select(Commit).where(Commit.run_id == run_id, Commit.status.in_(statuses)))

    def submit_commit(self, run_id: str, *, key: str, expected_version: int,
                      mechanical: tuple[MechanicalUpdate, ...] = ()) -> JobRecord:
        """Encola el commit como acción escritora; una intención pendiente se concilia, no se repite."""
        if type(expected_version) is not int:
            raise ValueError("Explicit resource version required")
        updates = tuple(mechanical)
        request = freeze({"action": "commit", "run_id": run_id, "expected_version": expected_version,
                          "mechanical": [asdict(item) for item in updates]})
        root = self._run_root(run_id)
        assessment = self.guard.assess(root) if root is not None else None
        with self._write() as session:
            existing = self._existing(session, key, request)
            if existing:
                return _job(existing)
            run = session.get(Run, run_id)
            if run is None:
                raise LookupError("Unknown managed run")
            if run.version != expected_version:
                raise Conflict("Run changed; reload before committing")
            return self._queue_commit(session, run, key, request, updates, assessment)

    def _queue_commit(self, session, run, key, request, updates, assessment) -> JobRecord:
        """Comprobaciones y job de commit en la transacción del llamante (acción propia o lote H3.4)."""
        run_id = run.id
        if session.scalar(select(Job.id).where(Job.run_id == run_id,
                Job.status.in_(("QUEUED", "ACTIVE", "RECOVERY_REQUIRED")))) is not None:
            raise Conflict("Run already has unfinished work")
        live = self._live_commit(session, run_id)
        if live is not None and live.status == "COMMITTED":
            raise Conflict("Run already has a recorded commit")
        self._phase_open(session, run.root, run.phase_id)
        history = load_history(run.history_json)
        if live is not None:
            if updates and updates != CommitIntent.from_json(live.intent_json).mechanical:
                raise Conflict("A pending commit operation fixed different mechanical updates")
        else:
            if (history.status != "acceptance_ready" or history.acceptance is None
                    or not history.acceptance.eligible):
                raise Conflict("Only an eligible acceptance_ready run can be committed")
            try:
                git_provenance(history.acceptance.evidence)
                validate_mechanical_updates(restore_context(run.context_json),
                                            history.acceptance.evidence.changed_paths, updates)
            except (CommitError, ValueError) as exc:
                raise Conflict(str(exc)) from exc
        activation_id = self._admit(session, assessment)
        job = Job(idempotency_key=key, run_id=run_id, request_json=request, status="QUEUED",
                  created_at=self._now(), activation_id=activation_id)
        session.add(job)
        session.flush()
        run.status, run.stage = "QUEUED", "commit"
        self._event(session, run, "job_queued", {"job_id": job.id, "action": "commit"})
        return _job(job)

    def commit_record(self, run_id: str) -> CommitRecord | None:
        with Session(self.engine) as session:
            row = self._live_commit(session, run_id) or session.scalar(
                select(Commit).where(Commit.run_id == run_id).order_by(Commit.created_at.desc()).limit(1))
            return _commit(row) if row else None

    def pending_commit(self, claim: JobRecord) -> CommitIntent | None:
        with Session(self.engine) as session:
            job = session.get(Job, claim.id)
            if job is None or not claim.owner_token or job.owner_token != claim.owner_token:
                raise OwnershipLost("Job ownership lost; reconciliation required")
            row = self._live_commit(session, job.run_id, ("INTENT",))
            return CommitIntent.from_json(row.intent_json) if row else None

    def commit_intent(self, claim: JobRecord, intent: CommitIntent) -> None:
        """Intención durable ANTES de mover la referencia; transacción propia y corta."""
        self._require_mode(claim)
        with self._write() as session:
            job, run = self._owned(session, claim)
            history = load_history(run.history_json)
            if (intent.run_id != run.id or history.acceptance is None
                    or history.acceptance.evidence.fingerprint != intent.reviewed_fingerprint
                    or history.acceptance.evidence.base_revision != intent.base_revision):
                raise Conflict("Commit intent must name this run's reviewed acceptance evidence")
            if self._live_commit(session, run.id) is not None:
                raise Conflict("Run already has a live commit operation")
            self._phase_open(session, run.root, run.phase_id)
            session.add(Commit(operation_id=intent.operation_id, run_id=run.id, job_id=job.id, status="INTENT",
                               base_revision=intent.base_revision, reviewed_fingerprint=intent.reviewed_fingerprint,
                               expected_tree=intent.expected_tree, expected_commit=intent.expected_commit,
                               intent_json=intent.to_json(), created_at=self._now()))
            run.stage, run.status = "commit", "COMMITTING"
            self._event(session, run, "commit_intent", {
                "job_id": job.id, "operation_id": intent.operation_id, "base_revision": intent.base_revision,
                "expected_tree": intent.expected_tree, "expected_commit": intent.expected_commit,
                "reviewed_fingerprint": intent.reviewed_fingerprint})

    def commit_result(self, claim: JobRecord, outcome: CommitOutcome, adopt: dict | None = None) -> None:
        """`adopt` (D072): hashes de bloques gestionados que el propio commit regeneró, adoptados atómicamente."""
        with self._write() as session:
            job, run = self._owned(session, claim)
            row = session.get(Commit, outcome.operation_id) if outcome.operation_id else None
            if row is None or row.run_id != run.id or row.status != "INTENT":
                raise Conflict("Commit result requires its pending intent")
            row.result_json = outcome.to_json()
            row.finished_at = self._now()
            if outcome.status == "invalidated":
                row.status = "INVALIDATED"
                self._event(session, run, "commit_invalidated", {
                    "job_id": job.id, "operation_id": row.operation_id, "diagnostic": outcome.diagnostic})
                return
            if (outcome.commit != row.expected_commit or outcome.tree != row.expected_tree):
                raise Conflict("Commit result differs from the persisted intent")
            row.status, row.commit_sha = "COMMITTED", outcome.commit
            run.status, run.stage = "COMMITTED", "committed"
            if adopt:
                from harness_local.storage.documents import adopt_blocks
                adopt_blocks(self, session, run, adopt, outcome.commit)
            self._event(session, run, "commit_recorded", {
                "job_id": job.id, "operation_id": row.operation_id, "commit": outcome.commit,
                "tree": outcome.tree, "reconciled": outcome.status == "reconciled", "index": outcome.index})

    def commit_invalidated(self, claim: JobRecord, outcome: CommitOutcome) -> None:
        """Invalidación previa a cualquier intención: solo evidencia, sin fila de operación."""
        self.effect(claim, "commit_invalidated", {
            "operation_id": None, "diagnostic": outcome.diagnostic,
            "observed_fingerprint": outcome.observed_fingerprint, "head": outcome.head})

    def tag_intent(self, claim: JobRecord, intent: dict) -> None:
        """H3.3: intención del tag de cierre ANTES de crear la referencia; transacción propia y corta."""
        self._require_mode(claim)
        with self._write() as session:
            job, run = self._owned(session, claim)
            from harness_local.storage.phases import record_tag_intent
            record_tag_intent(self, session, run, intent)
            self._event(session, run, "phase_tag_intent", {"job_id": job.id, **intent})

    def export_intent(self, claim: JobRecord, intent: CommitIntent) -> None:
        """Intención de exportación confirmada, persistida antes de escribir documentos o Git."""
        self._require_mode(claim)
        with self._write() as session:
            _, run = self._owned(session, claim)
            from harness_local.storage.document_export import record_intent
            record_intent(self, session, run, intent)
            self._event(session, run, 'document_export_intent', {
                'operation_id': intent.operation_id, 'expected_commit': intent.expected_commit,
                'expected_tree': intent.expected_tree})

    def document_intent(self, claim: JobRecord, intent: CommitIntent) -> None:
        """D072: intención de transición o edición documental, persistida antes de escribir documentos o Git."""
        self._require_mode(claim)
        with self._write() as session:
            _, run = self._owned(session, claim)
            if run.purpose not in ("document_edit", "phase_transition", "phase_close"):
                raise Conflict("Document intents belong to document operations")
            _operation_module(run).record_intent(self, session, run, intent)
            self._event(session, run, f"{run.purpose}_intent", {
                "operation_id": intent.operation_id, "expected_commit": intent.expected_commit,
                "expected_tree": intent.expected_tree})

    def register_owner(self, claim, identity):
        with self._write() as session:
            job, run = self._owned(session, claim)
            if job.process_owner is not None:
                raise Conflict("Process owner already registered")
            job.process_owner = identity
            self._event(session, run, "process_owner_registered", {"job_id": job.id, "identity": identity})

    def close_owner(self, claim):
        # Closing the scope forbids future launches; may run after lease loss.
        with self._write() as session:
            job = session.get(Job, claim.id)
            if job is None or job.owner_token != claim.owner_token:
                raise OwnershipLost("Different process owner")
            job.owner_closed = True
            run = session.get(Run, job.run_id)
            self._event(session, run, "process_owner_closed", {"job_id": job.id})

    def process_intent(self, claim, attempt_id, spec):
        with self._write() as session:
            job, run = self._owned(session, claim)
            attempt = session.get(AttemptRow, attempt_id)
            if (not attempt or attempt.run_id != run.id or attempt.result_json is not None
                    or job.process_owner is None or job.owner_closed):
                raise Conflict("Live owner and pending invocation required")
            if session.get(Process, attempt_id):
                raise Conflict("One launch per attempt; no retry")
            session.add(Process(attempt_id=attempt_id, job_id=job.id, spec=spec, status="PENDING"))
            self._event(session, run, "process_intent", {"job_id": job.id, "attempt_id": attempt_id, "spec": spec})

    def process_update(self, claim, attempt_id, kind, payload):
        with self._write() as session:
            job, run = self._owned(session, claim)
            row = session.get(Process, attempt_id)
            if row is None or row.job_id != job.id:
                raise Conflict("Unknown process intent")
            if kind == "process_spawned":
                if job.owner_closed or row.identity is not None:
                    raise Conflict("Process identity cannot change")
                row.identity, row.status = payload, "RUNNING"
            elif kind == "process_finished":
                row.status = "STOPPED" if payload["group_state"] == "dead" else "UNCERTAIN"
                row.capture = payload
            self._event(session, run, kind, {"job_id": job.id, "attempt_id": attempt_id, **payload})

    def processes(self, job_id):
        with Session(self.engine) as session:
            return [{"attempt_id": row.attempt_id, "spec": row.spec, "identity": row.identity,
                     "status": row.status, "capture": row.capture}
                    for row in session.scalars(select(Process).where(Process.job_id == job_id))]

    def command_process_event(self, claim, command_id, kind, payload):
        from harness_local.storage.command_processes import PREFIX, for_job
        self._require_mode(claim)
        with self._write() as session:
            job, run = self._owned(session, claim)
            if job.process_owner is None or job.owner_closed:
                raise Conflict("Live command owner required")
            row = next((r for r in for_job(session, job) if r['command_id'] == command_id), None)
            if kind == 'intent':
                started = session.scalars(select(Event).where(Event.run_id == run.id,
                    Event.kind == 'command_started')).all()
                if row or not any(e.payload.get('command_id') == command_id
                                  and e.payload.get('job_id') == job.id for e in started):
                    raise Conflict("One process intent per started command")
            elif row is None or row['capture'] is not None:
                raise Conflict("Pending command process required")
            elif kind == 'spawned':
                if row['identity'] is not None:
                    raise Conflict("Command process identity cannot change")
            elif kind == 'bytes':
                if row['identity'] is None:
                    raise Conflict("Command has not spawned")
            elif kind != 'finished':
                raise Conflict("Unknown command process event")
            self._event(session, run, PREFIX + kind,
                        {**payload, 'job_id': job.id, 'command_id': command_id})

    def command_processes(self, job_id):
        from harness_local.storage.command_processes import for_job
        with Session(self.engine) as session:
            job = session.get(Job, job_id)
            if job is None:
                raise Conflict("Unknown job")
            return for_job(session, job)

    def _processes_stopped(self, session, job, *, recovering=False):
        from harness_local.adapters.processes import liveness
        if recovering and job.process_owner and not job.owner_closed:
            if liveness(job.process_owner) != "dead":
                raise Conflict("Previous owner may still launch effects; cannot unlock")
        from harness_local.storage.command_processes import for_job
        for command in for_job(session, job):
            if command['identity'] is None:
                if command['status'] == 'STOPPED':
                    continue  # Observed failure before spawn, no target executed.
                if not recovering or (not job.owner_closed and liveness(job.process_owner) != 'dead'):
                    raise Conflict("Pending command spawn requires stopped owner")
            elif liveness(command['identity'], group=True) != 'dead':
                raise Conflict("Previous command group is alive or uncertain; cannot unlock")
        for row in session.scalars(select(Process).where(Process.job_id == job.id)):
            if row.identity is None:
                # Gate cannot execute without a durable identity. Owner must first stop.
                if not recovering or (not job.owner_closed and liveness(job.process_owner) != "dead"):
                    raise Conflict("Pending spawn requires stopped owner")
            elif liveness(row.identity, group=True) != "dead":
                raise Conflict("Previous process group is alive or uncertain; cannot unlock")

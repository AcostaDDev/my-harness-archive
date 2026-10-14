"""Lecturas paginadas del estado gestionado para la API local. Sin escrituras.

La autoridad sigue en `SQLiteManagedRepository`; estas consultas solo proyectan
filas confirmadas. Ausencia y null se conservan: nada se rellena con defaults.
"""

from dataclasses import asdict
import base64
import hashlib
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness_local.core.engine.serialization import load_history
from harness_local.core.engine.validation import validation_payload
from harness_local.storage.models import (
    CheckoutLockRow as Lock, ManagedAttemptRow as AttemptRow, ManagedCommitRow as Commit,
    ManagedEventRow as Event, ManagedJobRow as Job, ManagedRunRow as Run,
)


def _loads(value):
    return json.loads(value) if value is not None else None


def job_view(row: Job) -> dict:
    return {"id": row.id, "run_id": row.run_id, "action": json.loads(row.request_json)["action"],
            "status": row.status, "idempotency_key": row.idempotency_key, "owner_token": row.owner_token,
            "lease_until": row.lease_until, "created_at": row.created_at, "finished_at": row.finished_at,
            "diagnostic": row.diagnostic, "activation_id": row.activation_id, "owner_closed": bool(row.owner_closed)}


def _commit_view(row: Commit | None) -> dict | None:
    if row is None:
        return None
    return {"operation_id": row.operation_id, "job_id": row.job_id, "status": row.status,
            "base_revision": row.base_revision, "reviewed_fingerprint": row.reviewed_fingerprint,
            "expected_tree": row.expected_tree, "expected_commit": row.expected_commit,
            "commit": row.commit_sha, "result": _loads(row.result_json),
            "created_at": row.created_at, "finished_at": row.finished_at}


def _history_view(history_json: str) -> dict:
    history = load_history(history_json)
    acceptance = history.acceptance
    return {
        "status": history.status,
        "task": _loads(history.task_json),
        "stop": {"stage": history.stop.stage, "reason": history.stop.reason} if history.stop else None,
        "stops": [{"stage": stop.stage, "reason": stop.reason} for stop in history.stops],
        "attempts": len(history.attempts),
        "cycles": [{"number": cycle.number, "verdict": cycle.verdict, "fingerprint": cycle.evidence.fingerprint,
                    "changed_paths": list(cycle.evidence.changed_paths), "diff": cycle.evidence.diff,
                    "provenance": _loads(cycle.evidence.provenance_json),
                    "validation": validation_payload(cycle.validation, include_cases=False),
                    "review": _loads(cycle.review_json)} for cycle in history.cycles],
        "acceptance": None if acceptance is None else {
            "eligible": acceptance.eligible, "reasons": list(acceptance.reasons),
            "base_revision": acceptance.evidence.base_revision, "fingerprint": acceptance.evidence.fingerprint,
            "changed_paths": list(acceptance.evidence.changed_paths)},
    }


class SQLiteManagedViews:
    def __init__(self, engine):
        self.engine = engine

    @staticmethod
    def _summary(row: Run) -> dict:
        return {"id": row.id, "root": row.root, "task_id": row.task_id, "phase_id": row.phase_id,
                "status": row.status, "stage": row.stage, "version": row.version, "revisions": row.revisions,
                "revision_limit": row.revision_limit, "created_at": row.created_at, "updated_at": row.updated_at,
                "purpose": row.purpose}

    def runs(self, root: str, offset: int, limit: int, phase: str | None = None, task: str | None = None) -> dict:
        """Filtros exactos opcionales por código de fase y de tarea (URLs de la UI, D076)."""
        with Session(self.engine) as session:
            query = select(Run).where(Run.root == root)
            if phase is not None:
                query = query.where(Run.phase_id == phase)
            if task is not None:
                query = query.where(Run.task_id == task)
            rows = session.scalars(query.order_by(Run.created_at.desc(), Run.id).offset(offset).limit(limit + 1)).all()
            items = [self._summary(row) for row in rows[:limit]]
            return {"items": items, "offset": offset, "next_offset": offset + limit if len(rows) > limit else None}

    def tasks(self, root: str, phase: str, planned: list[str], offset: int, limit: int) -> dict:
        """Tareas de una fase: las de la definición en su orden y después las que solo tienen runs.

        Solo cuenta runs de propósito `task`; el último run de cada tarea es el más reciente
        por creación. Sin runs, `latest` es null y `runs` es 0: no se infiere ningún estado.
        """
        with Session(self.engine) as session:
            rows = session.scalars(select(Run).where(Run.root == root, Run.phase_id == phase, Run.purpose == 'task')
                                   .order_by(Run.created_at.desc(), Run.id)).all()
        latest, counts = {}, {}
        for row in rows:
            latest.setdefault(row.task_id, row)
            counts[row.task_id] = counts.get(row.task_id, 0) + 1
        order = list(dict.fromkeys(planned)) + sorted(set(latest) - set(planned))
        items = [{"task_id": task, "planned": task in planned, "runs": counts.get(task, 0),
                  "latest": self._summary(latest[task]) if task in latest else None}
                 for task in order[offset:offset + limit]]
        return {"items": items, "offset": offset, "next_offset": offset + limit if len(order) > offset + limit else None}

    def run(self, run_id: str) -> dict:
        with Session(self.engine) as session:
            row = session.get(Run, run_id)
            if row is None:
                raise LookupError("Run gestionado desconocido.")
            live = session.scalar(select(Commit).where(Commit.run_id == run_id,
                                                       Commit.status.in_(("INTENT", "COMMITTED"))))
            latest = live or session.scalar(select(Commit).where(Commit.run_id == run_id)
                                            .order_by(Commit.created_at.desc()).limit(1))
            lock = session.scalar(select(Lock).join(Job, Job.id == Lock.job_id).where(Job.run_id == run_id))
            history = load_history(row.history_json)
            pending = session.scalar(select(Job.id).where(Job.run_id == run_id,
                Job.status.in_(('QUEUED', 'ACTIVE', 'RECOVERY_REQUIRED')))) is not None
            root_pending = session.scalar(select(Job.id).join(Run, Run.id == Job.run_id).where(
                Run.root == row.root, Job.status.in_(('QUEUED', 'ACTIVE', 'RECOVERY_REQUIRED')))) is not None
            actions = []
            if not pending and not lock:
                if live is None and history.task_json is not None and history.status in ('stopped', 'blocked', 'revision_limit'):
                    actions.append('revalidate')
                    executions = sum(a.request.role == 'executor' for a in history.attempts)
                    if json.loads(history.task_json)['allowed_paths'] and (not executions or history.revisions < row.revision_limit):
                        actions.append('retry_executor')
                if (live is not None and live.status == 'INTENT') or (live is None and history.acceptance and history.acceptance.eligible):
                    actions.append('commit')
            if not root_pending and row.purpose == 'task' and row.status in ('STOPPED', 'BLOCKED', 'REVISION_LIMIT', 'INTERRUPTED'):
                actions.append('permissions')
            return {**self._summary(row), "actions": actions, "versions": json.loads(row.versions_json),
                    "history": _history_view(row.history_json), "commit": _commit_view(latest),
                    "locked_by_job": lock.job_id if lock else None}

    def exists(self, run_id: str) -> None:
        with Session(self.engine) as session:
            if session.get(Run, run_id) is None:
                raise LookupError("Run gestionado desconocido.")

    def _report(self, run_id: str, cycle: int, entry: int, report: int):
        if min(cycle, entry, report) < 0:
            raise LookupError('Reporte JUnit desconocido.')
        with Session(self.engine) as session:
            row = session.get(Run, run_id)
            if row is None:
                raise LookupError('Run gestionado desconocido.')
            history = load_history(row.history_json)
            try:
                validation = history.cycles[cycle].validation
                command = validation.entries[entry]
                return validation, command, command.reports[report]
            except IndexError as exc:
                raise LookupError('Reporte JUnit desconocido.') from exc

    def test_cases(self, run_id, cycle, entry, report, offset, limit):
        validation, command, imported = self._report(run_id, cycle, entry, report)
        summary = validation_payload(validation, include_cases=False)['entries'][entry]['reports'][report]
        cases = imported.cases[offset:offset + limit]
        return {'report': summary, 'run_id': validation.run_id, 'source_attempt_id': validation.source_attempt_id,
                'command_id': command.command_id, 'evidence': asdict(validation.evidence),
                'items': [asdict(case) for case in cases], 'offset': offset,
                'next_offset': offset + limit if offset + limit < len(imported.cases) else None}

    def test_original(self, run_id, cycle, entry, report):
        _, _, imported = self._report(run_id, cycle, entry, report)
        if imported.original_base64 is None:
            raise LookupError('Original JUnit ausente: consulta el diagnóstico del reporte.')
        data = base64.b64decode(imported.original_base64, validate=True)
        if hashlib.sha256(data).hexdigest() != imported.sha256 or len(data) != imported.size_bytes:
            raise ValueError('Persisted JUnit original hash/size mismatch')
        return data, imported.sha256

    def jobs(self, run_id: str) -> list[dict]:
        self.exists(run_id)
        with Session(self.engine) as session:
            return [job_view(row) for row in session.scalars(select(Job).where(Job.run_id == run_id)
                                                              .order_by(Job.id))]

    def job(self, job_id: int) -> dict:
        with Session(self.engine) as session:
            row = session.get(Job, job_id)
            if row is None:
                raise LookupError("Job gestionado desconocido.")
            return job_view(row)

    def attempts(self, run_id: str, offset: int, limit: int) -> dict:
        self.exists(run_id)
        with Session(self.engine) as session:
            rows = session.scalars(select(AttemptRow).where(AttemptRow.run_id == run_id)
                                   .order_by(AttemptRow.number).offset(offset).limit(limit + 1)).all()
            items = []
            for row in rows[:limit]:
                request = json.loads(row.request_json)
                items.append({"id": row.id, "number": row.number, "role": request["role"],
                              "selection": request["selection"], "fresh_session": request["fresh_session"],
                              "prompt": request["prompt"], "permission_snapshot": _loads(request.get("permission_snapshot_json")), "prompt_snapshot": _loads(request.get("prompt_snapshot_json")),
                              "status": row.status, "versions": json.loads(row.versions_json),
                              "result": _loads(row.result_json), "started_at": row.started_at,
                              "finished_at": row.finished_at})
            return {"items": items, "offset": offset, "next_offset": offset + limit if len(rows) > limit else None}

    def events(self, run_id: str, after: int, limit: int) -> dict:
        """Cursor por secuencia del run: estable, sin huecos ni duplicados entre páginas."""
        self.exists(run_id)
        with Session(self.engine) as session:
            rows = session.scalars(select(Event).where(Event.run_id == run_id, Event.sequence > after)
                                   .order_by(Event.sequence).limit(limit + 1)).all()
            items = [{"id": row.id, "sequence": row.sequence, "kind": row.kind, "recorded_at": row.recorded_at,
                      "payload": row.payload} for row in rows[:limit]]
            return {"items": items, "cursor": items[-1]["sequence"] if items else after,
                    "has_more": len(rows) > limit}

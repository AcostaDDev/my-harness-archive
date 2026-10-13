"""Lecturas paginadas del estado gestionado para la API local. Sin escrituras.

La autoridad sigue en `SQLiteManagedRepository`; estas consultas solo proyectan
filas confirmadas. Ausencia y null se conservan: nada se rellena con defaults.
"""

from dataclasses import asdict
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness_local.core.engine.serialization import load_history
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
                    "validation": asdict(cycle.validation), "review": _loads(cycle.review_json)} for cycle in history.cycles],
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
                "revision_limit": row.revision_limit, "created_at": row.created_at, "updated_at": row.updated_at}

    def runs(self, root: str, offset: int, limit: int) -> dict:
        with Session(self.engine) as session:
            rows = session.scalars(select(Run).where(Run.root == root)
                                   .order_by(Run.created_at.desc(), Run.id).offset(offset).limit(limit + 1)).all()
            items = [self._summary(row) for row in rows[:limit]]
            return {"items": items, "offset": offset, "next_offset": offset + limit if len(rows) > limit else None}

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
            return {**self._summary(row), "versions": json.loads(row.versions_json),
                    "history": _history_view(row.history_json), "commit": _commit_view(latest),
                    "locked_by_job": lock.job_id if lock else None}

    def exists(self, run_id: str) -> None:
        with Session(self.engine) as session:
            if session.get(Run, run_id) is None:
                raise LookupError("Run gestionado desconocido.")

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
                              "prompt": request["prompt"], "prompt_snapshot": _loads(request.get("prompt_snapshot_json")),
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

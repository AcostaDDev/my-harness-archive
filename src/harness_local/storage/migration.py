"""Autoridad del modo H2.5 en SQLite. Ninguna transacción abarca lecturas de disco.

PREPARING → ACTIVE | FAILED; ACTIVE → REVERTING → REVERTED. Índices únicos
parciales impiden dos activaciones vivas por raíz canónica o por repositorio Git.
`owner_token` identifica a quien completa una transición; reanudar es explícito.
"""

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from uuid import uuid4

from sqlalchemy import or_, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from harness_local.core.engine.contracts import freeze
from harness_local.core.legacy import LegacyInventory
from harness_local.core.migration import (
    EXPORT_FORMAT, LIVE_STATUSES, RULES, ActivationView, CheckoutFacts, MigrationError, digest, marker_bytes,
    mode_refusal,
)
from harness_local.storage.legacy import SQLiteLegacyRepository
from harness_local.storage.models import (
    CheckoutLockRow as Lock, LegacyEventRow, LegacySourceRow, ManagedActivationRow as Activation,
    ManagedAttemptRow as AttemptRow, ManagedCommitRow as Commit, ManagedEventRow as Event,
    ManagedJobRow as Job, ManagedProcessRow as Process, ManagedRunRow as Run,
)
from harness_local.storage.schema import require_schema

UNFINISHED = ("QUEUED", "ACTIVE", "RECOVERY_REQUIRED")


class ModeConflict(MigrationError):
    pass


@dataclass(frozen=True)
class ActivationRecord:
    id: str
    root: str
    repository_key: str | None
    status: str
    preview_sha256: str
    marker: bytes
    marker_sha256: str
    snapshot_root: str
    manifest_json: str | None
    manifest_sha256: str | None
    owner_token: str | None
    version: int
    diagnostic: str | None
    export_path: str | None
    export_sha256: str | None

    def view(self) -> ActivationView:
        return ActivationView(self.id, self.root, self.repository_key, self.status, self.marker_sha256,
                              json.loads(self.manifest_json) if self.manifest_json else None, self.version)


def _record(row: Activation) -> ActivationRecord:
    return ActivationRecord(row.id, row.root, row.repository_key, row.status, row.preview_sha256,
                            row.marker.encode("utf-8"), row.marker_sha256, row.snapshot_root, row.manifest_json,
                            row.manifest_sha256, row.owner_token, row.version, row.diagnostic,
                            row.export_path, row.export_sha256)


def _live(session, root: str, repository_key: str | None):
    clause = Activation.root == root
    if repository_key is not None:
        clause = or_(clause, Activation.repository_key == repository_key)
    rows = session.scalars(select(Activation).where(clause, Activation.status.in_(LIVE_STATUSES))).all()
    if len(rows) > 1:
        # Raíz de una activación y repositorio de otra: ambigüedad, nunca se elige una.
        raise ModeConflict("Varias activaciones vivas coinciden con este checkout; modo ambiguo.")
    return rows[0] if rows else None


def live_conflict(record: ActivationRecord, root: str, preview_sha256: str) -> str | None:
    """None si la activación viva es la misma ya completada (activar es idempotente)."""
    if record.status == "ACTIVE" and record.root == root and record.preview_sha256 == preview_sha256:
        return None
    if record.status == "PREPARING" and record.root == root:
        return (f"Activación {record.id} en curso o interrumpida; reanudarla o abandonarla "
                "explícitamente tras confirmar que el proceso anterior terminó.")
    return f"Activación viva {record.id} ({record.status}) en {record.root} para esta raíz o repositorio."


@dataclass(frozen=True)
class Assessment:
    facts: CheckoutFacts | None
    activation: ActivationRecord | None
    refusal: str | None


class ModeGuard:
    """Exclusión legacy/gestionado: lectura de disco fuera de la transacción, verificación dentro."""

    def __init__(self, engine, probe=None, drift=None):
        from harness_local.adapters import migration as filesystem
        self.engine = engine
        self.probe = probe or filesystem.probe
        self.drift = drift or filesystem.legacy_drift

    def assess(self, root) -> Assessment:
        try:
            facts = self.probe(root)
            with Session(self.engine) as session:
                row = _live(session, facts.root, facts.repository_key)
                activation = _record(row) if row else None
            source, drift = None, None
            if activation is not None and activation.status == "ACTIVE":
                source = facts if activation.root == facts.root else self.probe(activation.root)
                drift = self.drift(activation.root, json.loads(activation.manifest_json))
            refusal = mode_refusal(facts, activation.view() if activation else None, source, drift)
            return Assessment(facts, activation, refusal)
        except (OSError, ValueError) as exc:
            return Assessment(None, None, f"No se pudo comprobar el modo del checkout {root}: {exc}")

    @staticmethod
    def enforce(session, assessment: Assessment) -> str | None:
        """Dentro de la transacción escritora: el modo no cambió desde la evaluación."""
        if assessment.refusal is not None:
            raise ModeConflict(assessment.refusal)
        row = _live(session, assessment.facts.root, assessment.facts.repository_key)
        expected = assessment.activation
        if (row is None) != (expected is None) or (row is not None and (
                row.id != expected.id or row.status != expected.status or row.version != expected.version)):
            raise ModeConflict("El modo del checkout cambió durante la comprobación; repetir la solicitud.")
        return row.id if row else None


class SQLiteMigrationRepository:
    def __init__(self, engine, *, clock=None):
        require_schema(engine)
        self.engine = engine
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def _now(self) -> str:
        value = self.clock()
        if value.tzinfo is None:
            raise ValueError("Clock must return an aware UTC time")
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds")

    @contextmanager
    def _write(self):
        with Session(self.engine) as session, session.begin():
            # Primera operación DML: lock SQLite escritor antes de consultar.
            session.execute(text("UPDATE managed_activations SET version = version WHERE 0"))
            yield session

    def get(self, activation_id: str) -> ActivationRecord:
        with Session(self.engine) as session:
            row = session.get(Activation, activation_id)
            if row is None:
                raise LookupError("Unknown activation")
            return _record(row)

    def history(self, root: str) -> list[ActivationRecord]:
        with Session(self.engine) as session:
            return [_record(row) for row in session.scalars(
                select(Activation).where(Activation.root == root).order_by(Activation.created_at))]

    def live(self, facts: CheckoutFacts) -> ActivationRecord | None:
        with Session(self.engine) as session:
            row = _live(session, facts.root, facts.repository_key)
            return _record(row) if row else None

    def unfinished_roots(self) -> set[str]:
        """Raíces con trabajo gestionado sin terminar o commit ambiguo (para sondear su repositorio)."""
        with Session(self.engine) as session:
            jobs = session.scalars(select(Run.root).join(Job, Job.run_id == Run.id)
                                   .where(Job.status.in_(UNFINISHED)))
            intents = session.scalars(select(Run.root).join(Commit, Commit.run_id == Run.id)
                                      .where(Commit.status == "INTENT"))
            locks = session.scalars(select(Lock.root))
            return {*jobs, *intents, *locks}

    @staticmethod
    def _managed_blockers(session, related: set[str], probed: set[str]) -> list[dict]:
        current = {*session.scalars(select(Run.root).join(Job, Job.run_id == Run.id).where(Job.status.in_(UNFINISHED))),
                   *session.scalars(select(Run.root).join(Commit, Commit.run_id == Run.id)
                                    .where(Commit.status == "INTENT")),
                   *session.scalars(select(Lock.root))}
        blockers = [{"code": "managed_writer", "root": root,
                     "diagnostic": "Trabajo gestionado sin terminar, lock o commit ambiguo en este repositorio."}
                    for root in sorted(current & related)]
        if current - probed:
            blockers.append({"code": "managed_state_changed",
                             "diagnostic": "Apareció trabajo gestionado durante la comprobación; repetir."})
        return blockers

    def blockers(self, facts: CheckoutFacts, related: set[str], probed: set[str]) -> list[dict]:
        """Solo lectura: lo que impediría activar en este momento según SQLite."""
        with Session(self.engine) as session:
            blockers = self._managed_blockers(session, related, probed)
            try:
                row = _live(session, facts.root, facts.repository_key)
            except ModeConflict as exc:
                return [*blockers, {"code": "ambiguous_activation", "diagnostic": str(exc)}]
            if row is not None:
                blockers.append({"code": "live_activation", "activation_id": row.id, "root": row.root,
                                 "status": row.status,
                                 "diagnostic": "Ya existe una activación viva para esta raíz o repositorio."})
            return blockers

    # --- activación ---------------------------------------------------------------

    def begin_activation(self, facts: CheckoutFacts, preview_sha256: str, legacy_stopped: str,
                         migrations_dir, related: set[str], probed: set[str]) -> tuple[ActivationRecord, bool]:
        """PREPARING nuevo, o la activación ACTIVE idéntica ya completada (idempotente)."""
        with self._write() as session:
            row = _live(session, facts.root, facts.repository_key)
            if row is not None:
                record = _record(row)
                if live_conflict(record, facts.root, preview_sha256) is None:
                    return record, False
                raise ModeConflict(live_conflict(record, facts.root, preview_sha256))
            blockers = self._managed_blockers(session, related, probed)
            if blockers:
                where = f" Raíz: {blockers[0]['root']}." if "root" in blockers[0] else ""
                raise ModeConflict(blockers[0]["diagnostic"] + where)
            identifier, now = str(uuid4()), self._now()
            marker = marker_bytes(identifier, facts.root, now)
            row = Activation(id=identifier, root=facts.root, repository_key=facts.repository_key, status="PREPARING",
                             preview_sha256=preview_sha256, legacy_stopped=legacy_stopped, rules_json=freeze(RULES),
                             marker=marker.decode("utf-8"), marker_sha256=digest(marker),
                             snapshot_root=str(migrations_dir / identifier / "checkout"), owner_token=str(uuid4()),
                             version=1, created_at=now)
            session.add(row)
            try:
                session.flush()
            except IntegrityError as exc:
                raise ModeConflict("Otra activación viva ocupa esta raíz o repositorio.") from exc
            return _record(row), True

    @staticmethod
    def _expected(row: Activation, expected_version: int | None) -> None:
        """Pantalla obsoleta: la versión vista por el llamante se comprueba en la misma transacción."""
        if expected_version is not None and row.version != expected_version:
            raise ModeConflict(f"La activación cambió (versión {row.version}); recargar antes de repetir.")

    def take_over(self, activation_id: str, status: str, reason: str, *,
                  expected_version: int | None = None) -> ActivationRecord:
        """Reanudación explícita: el llamante afirma que el proceso anterior terminó."""
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("Explicit confirmation that the previous process stopped is required")
        with self._write() as session:
            row = session.get(Activation, activation_id)
            if row is None:
                raise LookupError("Unknown activation")
            self._expected(row, expected_version)
            if row.status != status:
                raise ModeConflict(f"La activación está en {row.status}, no en {status}.")
            row.owner_token, row.version = str(uuid4()), row.version + 1
            row.diagnostic = f"Reanudada: {reason}"
            return _record(row)

    def _owned(self, session, activation_id: str, token: str, status: str) -> Activation:
        row = session.get(Activation, activation_id)
        if row is None or row.status != status or row.owner_token != token:
            raise ModeConflict("La transición pertenece a otro proceso o ya terminó; no se completa.")
        return row

    def fail_activation(self, activation_id: str, token: str, diagnostic: str) -> None:
        with self._write() as session:
            row = self._owned(session, activation_id, token, "PREPARING")
            row.status, row.owner_token, row.version = "FAILED", None, row.version + 1
            row.finished_at, row.diagnostic = self._now(), diagnostic

    def finalize_activation(self, activation_id: str, token: str, manifest_json: str,
                            snapshot: LegacyInventory) -> ActivationRecord:
        """Una transacción: índice del histórico copiado, observación del origen detenida y ACTIVE."""
        with self._write() as session:
            row = self._owned(session, activation_id, token, "PREPARING")
            if snapshot.root != row.snapshot_root:
                raise ModeConflict("La copia indexada no es la registrada por la activación.")
            SQLiteLegacyRepository.apply(session, snapshot)
            source = session.get(LegacySourceRow, row.root)
            now = self._now()
            if source is not None and source.watch_enabled:
                source.watch_enabled = False
                session.add(LegacyEventRow(root=row.root, kind="watch_changed", observed_at=now,
                                           payload={"enabled": False, "activation_id": row.id}))
            row.status, row.owner_token, row.version = "ACTIVE", None, row.version + 1
            row.manifest_json, row.manifest_sha256 = manifest_json, digest(manifest_json)
            row.activated_at, row.diagnostic = now, None
            return _record(row)

    def abandon(self, activation_id: str, token: str, reason: str) -> None:
        with self._write() as session:
            row = self._owned(session, activation_id, token, "PREPARING")
            row.status, row.owner_token, row.version = "FAILED", None, row.version + 1
            row.finished_at, row.diagnostic = self._now(), f"Abandonada: {reason}"

    # --- reversión ----------------------------------------------------------------

    def begin_revert(self, activation_id: str, reason: str, *,
                     expected_version: int | None = None) -> ActivationRecord:
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("Explicit revert reason required")
        with self._write() as session:
            row = session.get(Activation, activation_id)
            if row is None:
                raise LookupError("Unknown activation")
            self._expected(row, expected_version)
            if row.status != "ACTIVE":
                raise ModeConflict(f"Solo una activación ACTIVE puede revertirse (estado {row.status}).")
            busy = session.scalar(select(Job.id).join(Run, Run.id == Job.run_id).where(
                Job.status.in_(UNFINISHED), or_(Job.activation_id == row.id, Run.root == row.root)))
            intent = session.scalar(select(Commit.operation_id).join(Job, Job.id == Commit.job_id).join(
                Run, Run.id == Commit.run_id).where(Commit.status == "INTENT",
                                                    or_(Job.activation_id == row.id, Run.root == row.root)))
            from harness_local.storage.project_import import unresolved as import_unresolved
            if (busy is not None or intent is not None or session.get(Lock, row.root) is not None
                    or import_unresolved(session, row.root)):
                raise ModeConflict("Trabajo gestionado sin terminar o commit ambiguo bajo esta activación; "
                                   "terminarlo o conciliarlo antes de revertir.")
            row.status, row.owner_token, row.version = "REVERTING", str(uuid4()), row.version + 1
            row.revert_reason = reason
            return _record(row)

    def export_state(self, activation_id: str) -> bytes:
        """Estado gestionado admitido bajo la activación, serializado de forma determinista."""
        with Session(self.engine) as session:
            activation = session.get(Activation, activation_id)
            run_ids = sorted(set(session.scalars(select(Job.run_id).where(Job.activation_id == activation_id))))
            runs = []
            for run_id in run_ids:
                run = session.get(Run, run_id)
                runs.append({
                    "run": {name: getattr(run, name) for name in (
                        "id", "root", "task_id", "phase_id", "context_json", "versions_json", "history_json",
                        "status", "stage", "revisions", "revision_limit", "version", "created_at", "updated_at")},
                    "jobs": [{name: getattr(job, name) for name in (
                        "id", "idempotency_key", "request_json", "status", "created_at", "finished_at",
                        "diagnostic", "activation_id")}
                        for job in session.scalars(select(Job).where(Job.run_id == run_id).order_by(Job.id))],
                    "attempts": [{name: getattr(item, name) for name in (
                        "id", "number", "request_json", "versions_json", "status", "result_json", "started_at",
                        "finished_at")} for item in session.scalars(
                        select(AttemptRow).where(AttemptRow.run_id == run_id).order_by(AttemptRow.number))],
                    "events": [{"sequence": item.sequence, "kind": item.kind, "recorded_at": item.recorded_at,
                                "payload": item.payload} for item in session.scalars(
                        select(Event).where(Event.run_id == run_id).order_by(Event.sequence))],
                    "commits": [{name: getattr(item, name) for name in (
                        "operation_id", "job_id", "status", "base_revision", "reviewed_fingerprint", "expected_tree",
                        "expected_commit", "intent_json", "result_json", "commit_sha", "created_at", "finished_at")}
                        for item in session.scalars(select(Commit).where(Commit.run_id == run_id)
                                                    .order_by(Commit.created_at, Commit.operation_id))],
                    "processes": [{"attempt_id": item.attempt_id, "job_id": item.job_id, "spec": item.spec,
                                   "identity": item.identity, "status": item.status, "capture": item.capture}
                                  for item in session.scalars(select(Process).join(
                                      AttemptRow, AttemptRow.id == Process.attempt_id)
                                      .where(AttemptRow.run_id == run_id).order_by(Process.attempt_id))],
                })
            return (freeze({
                "format": EXPORT_FORMAT, "activation": {
                    "id": activation.id, "root": activation.root, "repository_key": activation.repository_key,
                    "snapshot_root": activation.snapshot_root, "manifest_sha256": activation.manifest_sha256,
                    "revert_reason": activation.revert_reason},
                "runs": runs}) + "\n").encode("utf-8")

    def finish_revert(self, activation_id: str, token: str, export_path: str, export_sha256: str) -> ActivationRecord:
        with self._write() as session:
            row = self._owned(session, activation_id, token, "REVERTING")
            row.status, row.owner_token, row.version = "REVERTED", None, row.version + 1
            row.export_path, row.export_sha256, row.finished_at = export_path, export_sha256, self._now()
            return _record(row)


def import_marker(guard, root):
    """D099: solo el marcador de una activación ACTIVE propia y sin deriva puede excluirse de Git."""
    assessment = guard.assess(root)
    live = assessment.activation
    if (assessment.refusal is None and live is not None and live.status == 'ACTIVE'
            and live.root == str(root)):
        return live.marker_sha256
    return None


def bind_git_mode(writer, guard):
    """Inyecta la autoridad de modo sin acoplar el adaptador Git a SQLite."""
    from harness_local.adapters.git import GitWorkspace
    if isinstance(writer, GitWorkspace):
        writer.marker_reader = lambda root: import_marker(guard, root)
    return writer

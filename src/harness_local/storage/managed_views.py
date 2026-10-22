"""Lecturas paginadas del estado gestionado para la API local. Sin escrituras.

La autoridad sigue en `SQLiteManagedRepository`; estas consultas solo proyectan
filas confirmadas. Ausencia y null se conservan: nada se rellena con defaults.
P010-T003 (D142): ninguna vista selecciona `history_json` ni decodifica historiales; leen la proyección
`run-projection-1`, escrita con el historial, con límites explícitos.
"""

import base64
import hashlib
import json

from sqlalchemy import func, select
from sqlalchemy.orm import Session, load_only

from harness_local.storage.managed import Conflict
from harness_local.storage.models import (
    CheckoutLockRow as Lock, ManagedAttemptRow as AttemptRow, ManagedCommitRow as Commit,
    ManagedEventRow as Event, ManagedJobRow as Job, ManagedRunRow as Run,
    RunProjectionCaseRow as Case, RunProjectionCycleRow as Cycle, RunProjectionDiffChunkRow as Chunk,
    RunProjectionReportRow as Report, RunProjectionRow as Projection, RunProjectionStopRow as Stop,
)
from harness_local.storage.run_projection import DIFF_CHUNK, PROJECTION, loads as _loads

# Columnas de `managed_runs` que leen las vistas; cualquier otra (historial, contexto) lanza en lugar de cargarse.
RUN_COLUMNS = load_only(Run.id, Run.root, Run.task_id, Run.phase_id, Run.status, Run.stage, Run.version,
                        Run.revisions, Run.revision_limit, Run.created_at, Run.updated_at, Run.purpose,
                        Run.versions_json, raiseload=True)


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


MAX_DIFF_PAGE = 512 * 1024


def window_page(read, size: int, offset: int, limit: int) -> dict:
    """Página por bytes UTF-8 del diff almacenado, terminada en fin de línea.

    Una línea mayor que `limit` se corta en el siguiente límite UTF-8. `offset` válido es 0 o un
    `next_offset` anterior; un cursor en medio de una secuencia UTF-8 se rechaza, no se sustituye.
    `read(start, end)` devuelve esos bytes: solo se piden `limit` + 4, lo justo para completar una secuencia.
    """
    if type(offset) is not int or type(limit) is not int or offset < 0 or not 1 <= limit <= MAX_DIFF_PAGE:
        raise ValueError('Invalid diff page')
    if offset > size:
        raise ValueError('Diff offset must be 0 or a previous next_offset')
    window = read(offset, min(offset + limit + 4, size)) if offset < size else b''
    if window and window[0] & 0xC0 == 0x80:
        raise ValueError('Diff offset must be 0 or a previous next_offset')
    end = min(limit, size - offset)
    if offset + end < size:
        newline = window.rfind(b'\n', 0, end)
        if newline >= 0:
            end = newline + 1
        else:
            while offset + end < size and window[end] & 0xC0 == 0x80:
                end += 1
    return {'offset': offset, 'next_offset': offset + end if offset + end < size else None,
            'text': window[:end].decode('utf-8')}


def diff_page(text: str, offset: int, limit: int) -> dict:
    data = text.encode('utf-8')
    return window_page(lambda start, end: data[start:end], len(data), offset, limit)


def _cycle_view(row: Cycle) -> dict:
    return {"number": row.number, "verdict": row.verdict, "fingerprint": row.fingerprint,
            "changed_paths": json.loads(row.changed_paths_json), "diff_sha256": row.diff_sha256,
            "diff_bytes": row.diff_bytes, "provenance": _loads(row.provenance_json),
            "validation": json.loads(row.validation_json), "review": _loads(row.review_json),
            "formatting": _loads(row.formatting_json)}


def _projection(session, run_id: str) -> Projection:
    row = session.get(Projection, run_id)
    if row is None:
        # Escrita con el historial y rellenada por la migración: su ausencia es una base inconsistente.
        raise RuntimeError(f'Run {run_id} sin proyección {PROJECTION}; la base no es consistente.')
    return row


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
            query = select(Run).options(RUN_COLUMNS).where(Run.root == root)
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
        Recuentos agregados en SQL; solo se lee el último run de las tareas de la página.
        """
        scope = (Run.root == root, Run.phase_id == phase, Run.purpose == 'task')
        with Session(self.engine) as session:
            counts = dict(session.execute(select(Run.task_id, func.count()).where(*scope).group_by(Run.task_id)).all())
            order = list(dict.fromkeys(planned)) + sorted(set(counts) - set(planned))
            items = []
            for task in order[offset:offset + limit]:
                latest = session.scalar(select(Run).options(RUN_COLUMNS).where(*scope, Run.task_id == task)
                                        .order_by(Run.created_at.desc(), Run.id).limit(1)) if task in counts else None
                items.append({"task_id": task, "planned": task in planned, "runs": counts.get(task, 0),
                              "latest": self._summary(latest) if latest is not None else None})
        return {"items": items, "offset": offset, "next_offset": offset + limit if len(order) > offset + limit else None}

    def run(self, run_id: str) -> dict:
        """Detalle sin decodificar el historial: resumen, paradas y último ciclo; el resto de ciclos, por páginas."""
        with Session(self.engine) as session:
            row = session.get(Run, run_id, options=[RUN_COLUMNS])
            if row is None:
                raise LookupError("Run gestionado desconocido.")
            live = session.scalar(select(Commit).where(Commit.run_id == run_id,
                                                       Commit.status.in_(("INTENT", "COMMITTED"))))
            latest = live or session.scalar(select(Commit).where(Commit.run_id == run_id)
                                            .order_by(Commit.created_at.desc()).limit(1))
            lock = session.scalar(select(Lock).join(Job, Job.id == Lock.job_id).where(Job.run_id == run_id))
            history = _projection(session, run_id)
            acceptance = _loads(history.acceptance_json)
            active_job = session.scalar(select(Job.id).where(Job.run_id == run_id,
                Job.status.in_(('QUEUED', 'ACTIVE', 'RECOVERY_REQUIRED'))).order_by(Job.id.desc()).limit(1))
            pending = active_job is not None
            root_pending = session.scalar(select(Job.id).join(Run, Run.id == Job.run_id).where(
                Run.root == row.root, Job.status.in_(('QUEUED', 'ACTIVE', 'RECOVERY_REQUIRED')))) is not None
            actions = []
            if not pending and not lock:
                if live is None and history.task_json is not None and history.history_status in ('stopped', 'blocked', 'revision_limit'):
                    actions.append('revalidate')
                    executions = history.executor_attempts
                    if json.loads(history.task_json)['allowed_paths'] and (not executions or max(0, executions - 1) < row.revision_limit):
                        actions.append('retry_executor')
                if (live is not None and live.status == 'INTENT') or (live is None and acceptance and acceptance['eligible']):
                    actions.append('commit')
            if not root_pending and row.purpose == 'task' and row.status in ('STOPPED', 'BLOCKED', 'REVISION_LIMIT', 'INTERRUPTED'):
                actions.append('permissions')
            stops = session.scalars(select(Stop).where(Stop.run_id == run_id).order_by(Stop.ordinal)).all()
            last = (session.get(Cycle, (run_id, history.cycle_count - 1)) if history.cycle_count else None)
            return {**self._summary(row), "actions": actions, "versions": json.loads(row.versions_json),
                    "history": {
                        "status": history.history_status, "task": _loads(history.task_json),
                        "stop": ({"stage": history.stop_stage, "reason": history.stop_reason}
                                 if history.stop_stage is not None else None),
                        "stops": [{"stage": stop.stage, "reason": stop.reason} for stop in stops],
                        "attempts": history.attempts, "cycle_count": history.cycle_count,
                        "latest_cycle": _cycle_view(last) if last is not None else None,
                        "acceptance": acceptance},
                    "commit": _commit_view(latest), "locked_by_job": lock.job_id if lock else None,
                    "active_job": active_job}

    def cycles(self, run_id: str, offset: int, limit: int) -> dict:
        """Ciclos de revisión por número ascendente, sin el texto del diff ni los casos JUnit."""
        self.exists(run_id)
        with Session(self.engine) as session:
            rows = session.scalars(select(Cycle).where(Cycle.run_id == run_id).order_by(Cycle.number)
                                   .offset(offset).limit(limit + 1)).all()
            return {"items": [_cycle_view(row) for row in rows[:limit]], "offset": offset,
                    "next_offset": offset + limit if len(rows) > limit else None}

    def exists(self, run_id: str) -> None:
        with Session(self.engine) as session:
            if session.scalar(select(Run.id).where(Run.id == run_id)) is None:
                raise LookupError("Run gestionado desconocido.")

    def _report(self, session, run_id: str, cycle: int, entry: int, report: int, *columns):
        if min(cycle, entry, report) < 0:
            raise LookupError('Reporte JUnit desconocido.')
        if session.scalar(select(Run.id).where(Run.id == run_id)) is None:
            raise LookupError('Run gestionado desconocido.')
        found = session.execute(select(*columns).where(Report.run_id == run_id, Report.cycle == cycle,
                                                       Report.entry == entry, Report.report == report)).one_or_none()
        if found is None:
            raise LookupError('Reporte JUnit desconocido.')
        return found

    def test_cases(self, run_id, cycle, entry, report, offset, limit):
        with Session(self.engine) as session:
            command_id, summary, count = self._report(session, run_id, cycle, entry, report,
                                                      Report.command_id, Report.summary_json, Report.case_count)
            validation = session.execute(select(Cycle.validation_evidence_json, Cycle.validation_run_id,
                                                Cycle.validation_source_attempt_id)
                                         .where(Cycle.run_id == run_id, Cycle.number == cycle)).one()
            cases = session.scalars(select(Case.case_json).where(
                Case.run_id == run_id, Case.cycle == cycle, Case.entry == entry, Case.report == report,
                Case.ordinal >= offset, Case.ordinal < offset + limit).order_by(Case.ordinal)).all()
        return {'report': json.loads(summary), 'run_id': validation.validation_run_id,
                'source_attempt_id': validation.validation_source_attempt_id, 'command_id': command_id,
                'evidence': json.loads(validation.validation_evidence_json),
                'items': [json.loads(case) for case in cases], 'offset': offset,
                'next_offset': offset + limit if offset + limit < count else None}

    def test_original(self, run_id, cycle, entry, report):
        with Session(self.engine) as session:
            original, sha256, size = self._report(session, run_id, cycle, entry, report,
                                                  Report.original_base64, Report.sha256, Report.size_bytes)
        if original is None:
            raise LookupError('Original JUnit ausente: consulta el diagnóstico del reporte.')
        data = base64.b64decode(original, validate=True)
        if hashlib.sha256(data).hexdigest() != sha256 or len(data) != size:
            raise ValueError('Persisted JUnit original hash/size mismatch')
        return data, sha256

    def cycle_diff(self, run_id: str, cycle: int, offset: int, limit: int, sha256: str | None = None) -> dict:
        """Diff revisado de un ciclo por páginas; `sha256`, si se da, debe ser el del resumen del run.

        Solo lee los tramos de `run_projection_diff_chunks` que cubre la página."""
        with Session(self.engine) as session:
            if session.scalar(select(Run.id).where(Run.id == run_id)) is None:
                raise LookupError('Run gestionado desconocido.')
            summary = session.execute(select(Cycle.diff_sha256, Cycle.diff_bytes)
                                      .where(Cycle.run_id == run_id, Cycle.number == cycle)).one_or_none()
            if summary is None:
                raise LookupError('Ciclo de revisión desconocido.')
            if sha256 is not None and sha256 != summary.diff_sha256:
                raise Conflict('El diff del ciclo no coincide con el hash pedido; relee el run.')

            def read(start: int, end: int) -> bytes:
                first, last = start // DIFF_CHUNK, (end - 1) // DIFF_CHUNK
                data = b''.join(session.scalars(select(Chunk.data).where(
                    Chunk.run_id == run_id, Chunk.cycle == cycle, Chunk.chunk >= first, Chunk.chunk <= last)
                    .order_by(Chunk.chunk)).all())
                return data[start - first * DIFF_CHUNK:end - first * DIFF_CHUNK]

            page = window_page(read, summary.diff_bytes, offset, limit)
        return {'run_id': run_id, 'cycle': cycle, 'sha256': summary.diff_sha256, 'size_bytes': summary.diff_bytes,
                **page}

    def jobs(self, run_id: str, offset: int = 0, limit: int = 30) -> dict:
        """Del más reciente al más antiguo: el job en curso o por recuperar está en la primera página."""
        self.exists(run_id)
        with Session(self.engine) as session:
            rows = session.scalars(select(Job).where(Job.run_id == run_id).order_by(Job.id.desc())
                                   .offset(offset).limit(limit + 1)).all()
            return {"items": [job_view(row) for row in rows[:limit]], "offset": offset,
                    "next_offset": offset + limit if len(rows) > limit else None}

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

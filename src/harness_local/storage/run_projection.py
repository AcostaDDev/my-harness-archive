"""Proyección derivada `run-projection-1` de los historiales gestionados (P010-T003, D142).

`managed_runs.history_json` sigue siendo la autoridad. La proyección se escribe en la misma transacción que el
historial desde sus dos únicos escritores (`_queue_new_run` y `_history`) y la migración 0023 la rellena para los
runs anteriores decodificando cada historial una vez. Las vistas de runs leen solo estas tablas; el motor, la
recuperación, los checks, el chat y los permisos siguen leyendo el historial. El backup recalcula y compara cada run.
"""

from dataclasses import asdict
import hashlib
import json

from sqlalchemy import insert, update

from harness_local.core.engine.contracts import freeze
from harness_local.core.engine.serialization import load_history
from harness_local.core.engine.validation import validation_payload
from harness_local.storage.models import (
    RunProjectionCaseRow, RunProjectionCycleRow, RunProjectionDiffChunkRow, RunProjectionReportRow,
    RunProjectionRow, RunProjectionStopRow,
)

PROJECTION = 'run-projection-1'
DIFF_CHUNK = 64 * 1024  # Tramo fijo del formato: cambiarlo exige otra versión de la proyección.

# Orden de escritura y de comparación; cada tabla con su clave primaria, que fija el orden estable.
TABLES = {
    'run_projections': (RunProjectionRow.__table__, ('run_id',)),
    'run_projection_stops': (RunProjectionStopRow.__table__, ('run_id', 'ordinal')),
    'run_projection_cycles': (RunProjectionCycleRow.__table__, ('run_id', 'number')),
    'run_projection_diff_chunks': (RunProjectionDiffChunkRow.__table__, ('run_id', 'cycle', 'chunk')),
    'run_projection_reports': (RunProjectionReportRow.__table__, ('run_id', 'cycle', 'entry', 'report')),
    'run_projection_cases': (RunProjectionCaseRow.__table__, ('run_id', 'cycle', 'entry', 'report', 'ordinal')),
}


class ProjectionMismatch(ValueError):
    pass


def diff_summary(diff: str) -> dict:
    data = diff.encode('utf-8')
    return {'diff_sha256': hashlib.sha256(data).hexdigest(), 'diff_bytes': len(data)}


def evidence_view(evidence: dict) -> dict:
    """Evidencia validada sin el texto del diff, que ya resume el ciclo: hash y tamaño en su lugar."""
    if 'diff' not in evidence:
        return evidence
    return {**{key: value for key, value in evidence.items() if key != 'diff'}, **diff_summary(evidence['diff'])}


def _summary(run_id: str, history_json: str, history) -> dict:
    acceptance, stop = history.acceptance, history.stop
    return {
        'run_id': run_id, 'projection': PROJECTION,
        'history_sha256': hashlib.sha256(history_json.encode('utf-8')).hexdigest(),
        'history_status': history.status, 'task_json': history.task_json, 'attempts': len(history.attempts),
        'executor_attempts': sum(attempt.request.role == 'executor' for attempt in history.attempts),
        'cycle_count': len(history.cycles), 'stop_count': len(history.stops),
        'stop_stage': stop.stage if stop else None, 'stop_reason': stop.reason if stop else None,
        'acceptance_json': None if acceptance is None else freeze({
            'eligible': acceptance.eligible, 'reasons': list(acceptance.reasons),
            'base_revision': acceptance.evidence.base_revision, 'fingerprint': acceptance.evidence.fingerprint,
            'changed_paths': list(acceptance.evidence.changed_paths)}),
    }


def _stops(run_id: str, history, start: int = 0) -> list[dict]:
    return [{'run_id': run_id, 'ordinal': ordinal, 'stage': stop.stage, 'reason': stop.reason}
            for ordinal, stop in enumerate(history.stops) if ordinal >= start]


def _cycle(run_id: str, cycle) -> dict[str, list[dict]]:
    payload = validation_payload(cycle.validation, include_cases=False)
    validation = {**payload, 'evidence': evidence_view(payload['evidence'])}
    diff = cycle.evidence.diff.encode('utf-8')
    reports, cases = [], []
    for e, (entry, source) in enumerate(zip(payload['entries'], cycle.validation.entries)):
        for r, (summary, imported) in enumerate(zip(entry['reports'], source.reports)):
            key = {'run_id': run_id, 'cycle': cycle.number, 'entry': e, 'report': r}
            reports.append({**key, 'command_id': source.command_id, 'summary_json': freeze(summary),
                            'original_base64': imported.original_base64, 'sha256': imported.sha256,
                            'size_bytes': imported.size_bytes, 'case_count': len(imported.cases)})
            cases += [{**key, 'ordinal': n, 'case_json': freeze(asdict(case))} for n, case in enumerate(imported.cases)]
    return {
        'run_projection_cycles': [{
            'run_id': run_id, 'number': cycle.number, 'verdict': cycle.verdict,
            'fingerprint': cycle.evidence.fingerprint, 'changed_paths_json': freeze(list(cycle.evidence.changed_paths)),
            **diff_summary(cycle.evidence.diff), 'provenance_json': cycle.evidence.provenance_json,
            'review_json': cycle.review_json, 'formatting_json': cycle.formatting_json,
            'validation_json': freeze(validation),
            'validation_evidence_json': freeze(evidence_view(asdict(cycle.validation.evidence))),
            'validation_run_id': cycle.validation.run_id,
            'validation_source_attempt_id': cycle.validation.source_attempt_id}],
        'run_projection_diff_chunks': [{'run_id': run_id, 'cycle': cycle.number, 'chunk': n,
                                        'data': diff[start:start + DIFF_CHUNK]}
                                       for n, start in enumerate(range(0, len(diff), DIFF_CHUNK))],
        'run_projection_reports': reports, 'run_projection_cases': cases,
    }


def rows(run_id: str, history_json: str, history=None, *, stops_from: int = 0, cycles_from: int = 0) -> dict:
    """Filas de la proyección en orden de clave primaria; `*_from` limita a lo añadido tras un prefijo."""
    history = load_history(history_json) if history is None else history
    result = {name: [] for name in TABLES}
    result['run_projections'].append(_summary(run_id, history_json, history))
    result['run_projection_stops'] = _stops(run_id, history, stops_from)
    for cycle in history.cycles[cycles_from:]:
        for name, items in _cycle(run_id, cycle).items():
            result[name] += items
    return result


def _insert(execute, data: dict) -> None:
    for name, (table, _) in TABLES.items():
        if data.get(name):
            execute(insert(table), data[name])


def create(session, run_id: str, history_json: str, history) -> None:
    _insert(session.execute, rows(run_id, history_json, history))


def advance(session, run_id: str, previous, history, history_json: str) -> None:
    """Incremental: `_history` ya garantiza solo-añadir y que un ciclo previo solo gana su revisión."""
    data = rows(run_id, history_json, history, stops_from=len(previous.stops), cycles_from=len(previous.cycles))
    summary = data.pop('run_projections')[0]
    table = TABLES['run_projections'][0]
    if session.execute(update(table).where(table.c.run_id == run_id).values(summary)).rowcount != 1:
        raise ProjectionMismatch(f'Run {run_id} sin proyección {PROJECTION}')
    cycles = TABLES['run_projection_cycles'][0]
    for old, new in zip(previous.cycles, history.cycles):
        if old.review_json != new.review_json:
            session.execute(update(cycles).where(cycles.c.run_id == run_id, cycles.c.number == new.number)
                            .values(verdict=new.verdict, review_json=new.review_json))
    _insert(session.execute, data)


def verify(db, run_id: str, history_json: str, history=None) -> dict:
    """Compara la proyección guardada con la recalculada desde el historial (conexión sqlite3 de solo lectura).

    Devuelve las filas esperadas por tabla para que el llamante detecte filas huérfanas por recuento."""
    expected = rows(run_id, history_json, history)
    counts = {}
    for name, (table, key) in TABLES.items():
        columns = [column.name for column in table.columns]
        stored = [dict(zip(columns, row)) for row in db.execute(
            f'SELECT {",".join(columns)} FROM {name} WHERE run_id=? ORDER BY {",".join(key)}', (run_id,))]
        if stored != expected[name]:
            raise ProjectionMismatch(f'Proyección {PROJECTION} distinta del historial en {name} (run {run_id}).')
        counts[name] = len(stored)
    return counts


def loads(value):
    return json.loads(value) if value is not None else None

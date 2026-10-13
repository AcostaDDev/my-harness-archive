import { useEffect, useState } from 'react';
import { managed } from './managed-api';
import type { S } from './managed-api';

const observed = (value: unknown) => value === null || value === undefined ? 'No observado' : String(value);
const results: Record<S['JUnitCaseRead']['result'], string> = {
  passed: 'Éxito observado', failed: 'Fallo', error: 'Error', skipped: 'Omitido', unknown: 'Desconocido',
};
const statuses: Record<S['JUnitReportRead']['status'], string> = {
  complete: 'Completo', partial: 'Parcial', invalid: 'Inválido', missing: 'Ausente',
  unreadable: 'No legible', limit: 'Límite excedido', stale: 'Sin cambio; ejecución actual no acreditada',
};
const freshness: Record<S['JUnitReportRead']['freshness'], string> = {
  created: 'Archivo nuevo observado', changed: 'Cambio observado', unchanged: 'Sin cambio', unknown: 'No acreditada',
};

export function Tests({ runId, cycle, validation }: { runId: string; cycle: number; validation: S['ValidationRead'] }) {
  return <section><h4>Validaciones y tests</h4>
    <p>Intento de ejecución: {observed(validation.source_attempt_id)} · Base: {observed(validation.evidence.base_revision)} · Huella: {observed(validation.evidence.fingerprint)}</p>
    {validation.entries.map((entry, index) => <div className="entry" key={entry.command_id ?? index}>
      <strong><code>{entry.requested}</code></strong>
      <p>Salida del comando: {observed(entry.result.exit_code)} · Duración del comando: {entry.result.duration_seconds == null ? 'No observada' : `${entry.result.duration_seconds} s`}</p>
      {entry.result.error != null && <p className="error">{String(entry.result.error)}</p>}
      {entry.result.timed_out === true && <p className="error">Tiempo del comando agotado</p>}
      {!entry.reports.length && <p>No hay reporte JUnit declarado para este comando. Sin detalle por test.</p>}
      {entry.reports.map((report, number) => <Report key={`${report.sha256}:${number}`} report={report}
        path={`/runs/${runId}/cycles/${cycle}/validations/${index}/reports/${number}`} />)}
    </div>)}
  </section>;
}

function Report({ report, path }: { report: S['JUnitReportRead']; path: string }) {
  const [open, setOpen] = useState(false);
  const [offset, setOffset] = useState(0);
  const [page, setPage] = useState<S['JUnitCasesRead']>();
  const [error, setError] = useState('');
  useEffect(() => {
    if (!open) return;
    let active = true;
    setPage(undefined); setError('');
    void managed<S['JUnitCasesRead']>(`${path}?offset=${offset}&limit=50`).then(value => {
      if (active) setPage(value);
    }).catch(e => { if (active) setError(e instanceof Error ? e.message : String(e)); });
    return () => { active = false; };
  }, [open, offset, path]);
  return <div>
    <p><code>{report.path}</code> · {statuses[report.status]} · {report.case_count} casos observados</p>
    <p>Cobertura declarada: {report.coverage}</p>
    <p>SHA-256: <code>{observed(report.sha256)}</code> · Bytes: {observed(report.size_bytes)} · Captura durante el comando: {freshness[report.freshness]}</p>
    {report.diagnostics.map((diagnostic, index) => <p className="error" key={index}>{diagnostic}</p>)}
    {report.original_available && <p><a href={`/api/managed${path}/original`} download="junit.xml">Descargar XML original conservado</a></p>}
    <button aria-expanded={open} onClick={() => setOpen(!open)}>{open ? 'Ocultar tests' : 'Ver tests individuales'}</button>
    {open && <>
      <p>Duraciones observadas por test; no se suman como tiempo total. Los resultados pertenecen al reporte y a su estado de captura.</p>
      {error && <p role="alert" className="error">{error}</p>}
      {!page && !error && <p role="status">Cargando tests…</p>}
      {page && <>
        <p>Comando: {observed(page.command_id)}</p>
        <div className="test-table-scroll" role="region" aria-label="Tests individuales" tabIndex={0}>
        <table className="test-table"><thead><tr><th>Suite / test</th><th>Resultado</th><th>Duración (s)</th><th>Error</th></tr></thead>
          <tbody>{page.items.map(test => <tr key={test.id}>
            <td>{test.suite.length ? test.suite.map(observed).join(' / ') : 'No observado'}<br />{observed(test.classname)} · {observed(test.name)}
              <details><summary>Identificador</summary><p>Id del reporte: {observed(test.reported_id)}</p><code>{test.id}</code></details></td>
            <td>{results[test.result]}</td><td>{observed(test.duration_seconds)}</td>
            <td>{test.message != null && <p>{test.message}</p>}{test.error_type != null && <p>{test.error_type}</p>}
              {test.error === null ? 'No observado' : <pre>{test.error}</pre>}</td>
          </tr>)}</tbody></table></div>
        {!page.items.length && <p>No hay casos observados en esta página.</p>}
        <div className="pagination"><button disabled={!offset} onClick={() => setOffset(Math.max(0, offset - 50))}>Anterior</button>
          <button disabled={page.next_offset === null} onClick={() => setOffset(page.next_offset!)}>Siguiente</button></div>
      </>}
    </>}
  </div>;
}

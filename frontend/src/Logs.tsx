import { useEffect, useState } from 'react';
import { managed } from './managed-api';
import type { S } from './managed-api';

const labels = { retained: 'Retenido y verificado', purged: 'Purgado con autorización',
  pending: 'Purga pendiente de conciliación', missing: 'Archivo perdido', unverified: 'No verificado' };

export function Logs({ runId, attemptId }: { runId: string; attemptId: string }) {
  const [logs, setLogs] = useState<S['ManagedLogRead'][]>();
  const [error, setError] = useState('');
  const [request, setRequest] = useState(0);
  useEffect(() => {
    if (!request) return;
    let active = true;
    managed<S['ManagedLogRead'][]>(`/runs/${runId}/attempts/${attemptId}/logs`).then(
      data => { if (active) { setLogs(data); setError(''); } },
      e => { if (active) { setLogs(undefined); setError(e instanceof Error ? e.message : String(e)); } });
    return () => { active = false; };
  }, [runId, attemptId, request]);
  return <div>
    <button onClick={() => { setLogs(undefined); setRequest(n => n + 1); }}>Comprobar originales de logs</button>
    {error && <p role="alert">{error}</p>}
    {logs?.length === 0 && <p>Sin captura CLI registrada.</p>}
    {logs?.map(log => <div key={log.stream}>
      <p>{log.stream}: {labels[log.state]} · {log.size_bytes} bytes registrados</p>
      {log.diagnostic && <p>{log.diagnostic}</p>}
      <details><summary>Procedencia y autorización</summary><pre>{JSON.stringify(log, null, 2)}</pre></details>
    </div>)}
  </div>;
}

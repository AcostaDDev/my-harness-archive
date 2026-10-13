import { useEffect, useState } from 'react';
import { managed } from './managed-api';
import type { S } from './managed-api';

type Props = { run: S['ManagedRunRead']; busy: boolean; refresh: number; operate: (f: () => Promise<unknown>) => Promise<void> };
const operations = { files: 'write', tools: 'use', network: 'connect', product: 'decide', acceptance: 'accept' };
const names = { files: 'Ficheros', tools: 'Herramientas', network: 'Red', product: 'Producto', acceptance: 'Aceptación y cierre' };

export function Permissions({ run, busy, refresh, operate }: Props) {
  const [requests, setRequests] = useState<S['PermissionRequestRead'][]>([]);
  const [error, setError] = useState('');
  const [kind, setKind] = useState<S['PermissionCreate']['kind']>('tools');
  const [target, setTarget] = useState('');
  const [source, setSource] = useState('');
  const [requester, setRequester] = useState('');
  const [reason, setReason] = useState('');
  const [ttl, setTtl] = useState(3600);
  const [supersedes, setSupersedes] = useState('');
  const [scope, setScope] = useState<S['PermissionDecisionCreate']['scope']>('once');
  const [confirmed, setConfirmed] = useState(false);
  useEffect(() => {
    let active = true;
    managed<S['PermissionRequestRead'][]>(`/runs/${run.id}/permissions`).then(r => { if (active) { setRequests(r); setError(''); } })
      .catch(e => { if (active) setError(String(e)); });
    return () => { active = false; };
  }, [run.id, run.version, refresh]);
  useEffect(() => { setConfirmed(false); }, [run.version, kind, target, source, supersedes, ttl, scope, reason]);
  const editable = !busy && !error && run.actions.includes('permissions');
  function decide(r: S['PermissionRequestRead'], decision: 'grant' | 'deny') {
    void operate(async () => {
      await managed(`/runs/${run.id}/permissions/${r.id}/decision`, {
        expected_version: run.version, expected_request_version: r.version, fingerprint: r.fingerprint,
        decision, scope, reason, confirmed: true,
      } satisfies S['PermissionDecisionCreate']);
      setConfirmed(false);
    });
  }
  return <details><summary>Permisos y decisiones</summary>
    <p>Conceder registra una autorización; después debes reintentar explícitamente. Revalidar conserva los cambios y ejecuta tests y revisión. Los permisos de ficheros, herramientas y red son independientes.</p>
    <p>Las decisiones de producto o aceptación quedan auditadas; resolver requisitos o confirmar un commit exige su acción propia. La CLI no admite concesiones de red por dominio. El alcance de ficheros conserva el contrato y las rutas protegidas.</p>
    <p>La auditoría registra el usuario del servicio local. El nombre del solicitante es declarado.</p>
    {error && <p role="alert" className="error">{error}</p>}
    <label>Motivo de la solicitud o decisión<input value={reason} maxLength={2000} onChange={e => setReason(e.target.value)} /></label>
    <form onSubmit={e => { e.preventDefault(); void operate(async () => {
      await managed(`/runs/${run.id}/permissions`, { expected_version: run.version, kind, target,
        operation: operations[kind], arguments: [], requested_by: requester, source_attempt_id: source,
        reason, ttl_seconds: ttl, supersedes: supersedes || null } satisfies S['PermissionCreate']);
      setConfirmed(false); setSupersedes('');
    }); }}>
      <label>Categoría<select value={kind} onChange={e => setKind(e.target.value as typeof kind)}>{Object.entries(names).map(([k, n]) => <option key={k} value={k}>{n}</option>)}</select></label>
      <label>Alcance exacto (ruta, regla de herramienta, dominio o decisión)<input required value={target} maxLength={2000} onChange={e => setTarget(e.target.value)} /></label>
      <label>Identificador del intento que originó la solicitud<input required value={source} maxLength={36} onChange={e => setSource(e.target.value)} /></label>
      <label>Solicitante declarado<input required value={requester} maxLength={120} onChange={e => setRequester(e.target.value)} /></label>
      <label>Vigencia en segundos (máximo 24 horas)<input type="number" required min={1} max={86400} value={ttl} onChange={e => setTtl(Number(e.target.value))} /></label>
      <label>Solicitud que se sustituye<select value={supersedes} onChange={e => setSupersedes(e.target.value)}><option value="">Nueva solicitud</option>{requests.filter(r => ['PENDING', 'GRANTED', 'DENIED'].includes(r.status)).map(r => <option value={r.id} key={r.id}>{r.id} · {String(r.request.target)}</option>)}</select></label>
      <button disabled={!editable || !reason.trim()}>Registrar solicitud</button>
    </form>
    <label>Duración de la concesión<select value={scope} onChange={e => setScope(e.target.value as typeof scope)}><option value="once">Una vez: próximo intento</option><option value="task">Esta tarea, hasta caducidad o sustitución</option></select></label>
    <label className="check"><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />He revisado el alcance, la vigencia y el motivo de la decisión seleccionada.</label>
    {requests.map(r => <div className="entry" key={r.id}><strong>{names[r.request.kind as keyof typeof names]} · {r.effective_status}</strong>
      <p>{String(r.request.operation)} · {String(r.request.target)} · Caduca: {r.expires_at}</p>
      <details><summary>Solicitud exacta, huella y auditoría</summary><pre>{JSON.stringify(r, null, 2)}</pre></details>
      {r.effective_status === 'PENDING' && <><button disabled={!editable || !confirmed || !reason.trim()} onClick={() => decide(r, 'grant')}>Conceder</button>
        <button disabled={!editable || !confirmed || !reason.trim()} onClick={() => decide(r, 'deny')}>Denegar</button></>}
    </div>)}
  </details>;
}

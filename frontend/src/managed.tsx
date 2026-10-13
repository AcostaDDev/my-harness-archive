import { Permissions } from "./Permissions";
import { Prompts } from "./Prompts";
import { useEffect, useRef, useState } from "react";
import { managed, managedApi, ManagedError, readPending, savePending, jobRequest } from "./managed-api";
import type { Pending, S } from "./managed-api";

function Evidence({ title, value }: { title: string; value: unknown }) {
  return <details><summary>{title}</summary><pre>{value === null ? "No registrado (null)" : JSON.stringify(value, null, 2)}</pre></details>;
}
const message = (e: unknown) => e instanceof Error ? e.message : String(e);

export function ManagedBrowser() {
  const [projects, setProjects] = useState<S["ManagedProjectRead"][]>([]);
  const [supervisor, setSupervisor] = useState<S["SupervisorRead"]>();
  const [project, setProject] = useState("");
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    const poll = async () => {
      try {
        const [p, s] = await Promise.all([managed<S["ManagedProjectRead"][]>("/projects"), managed<S["SupervisorRead"]>("/supervisor")]);
        if (active) { setProjects(p); setSupervisor(s); setError(""); }
      } catch (e) { if (active) setError(message(e)); }
    };
    void poll(); const timer = setInterval(() => void poll(), 2000);
    return () => { active = false; clearInterval(timer); };
  }, []);
  return <section className="legacy managed">
    <div className="intro"><p className="eyebrow">EJECUCIÓN LOCAL</p><h1>Proyectos gestionados</h1>
      <p>Ejecuta una tarea, revisa sus evidencias y confirma el commit del contenido aceptado.</p></div>
    {error && <p role="alert" className="error">{error}</p>}
    <p role="status">Supervisor: {error ? "sin conexión (última lectura conservada)" : supervisor ? supervisor.alive ? "activo" : "detenido" : "conectando…"} ·
      Puertos: {supervisor?.ports_configured ? "configurados" : "no configurados"} · Git: {supervisor?.commit_writer_configured ? "configurado" : "no configurado"}</p>
    {supervisor?.last_error && <p className="error">Último diagnóstico del supervisor: {supervisor.last_error}</p>}
    <ul className="legacy-list">{projects.map(p => <li key={p.id}><button className="choice" aria-pressed={project === p.id} onClick={() => setProject(p.id)}>
      <strong>{p.id}</strong><small>{p.root}</small><small>Perfil: {p.profile}</small></button></li>)}</ul>
    {!projects.length && !error && <p>No hay proyectos registrados. Configura los proyectos en el servidor local.</p>}
    {project && <Project key={project} id={project} />}
  </section>;
}

function Project({ id }: { id: string }) {
  const [mode, setMode] = useState<S["ModeRead"]>();
  const [preview, setPreview] = useState<S["MigrationPreviewRead"]>();
  const [runs, setRuns] = useState<S["Page_ManagedRunSummaryRead_"]>();
  const [offset, setOffset] = useState(0);
  const [runId, setRunId] = useState("");
  const [task, setTask] = useState("P001-T001");
  const [phase, setPhase] = useState("P001");
  const [text, setText] = useState("");
  const [reason, setReason] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [pending, setPending] = useState<Pending | undefined>(readPending);
  const pendingRef = useRef(pending);
  const [busy, setBusy] = useState(false);
  const guard = useRef(false);
  const [error, setError] = useState("");
  const [connection, setConnection] = useState("");
  const [refresh, setRefresh] = useState(0);
  useEffect(() => {
    let active = true;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try {
        const [m, r] = await Promise.all([managed<S["ModeRead"]>(`/projects/${id}/mode`), managed<S["Page_ManagedRunSummaryRead_"]>(`/projects/${id}/runs?offset=${offset}`)]);
        if (active) { setMode(m); setRuns(r); setConnection(""); }
      } catch (e) { if (active) setConnection(`Sin actualizar: ${message(e)}. Se conserva la última lectura.`); }
      if (active) timer = setTimeout(() => void poll(), 1500);
    }
    void poll(); return () => { active = false; clearTimeout(timer); };
  }, [id, offset, refresh]);
  function remember(p?: Pending) { savePending(p); pendingRef.current = p; setPending(p); }
  async function operate(action: () => Promise<unknown>) {
    if (guard.current) return;
    guard.current = true; setBusy(true); setError("");
    try { await action(); }
    catch (e) { setError(message(e)); }
    finally { guard.current = false; setBusy(false); setRefresh(n => n + 1); }
  }
  async function send(request: Pending) {
    remember(request);
    try {
      const job = await managed<S["ManagedJobRead"]>(request.path, request.body, request.key);
      remember(); setRunId(job.run_id);
    } catch (e) {
      // Definitive rejection permits a new explicit action after reloading the current version.
      if (e instanceof ManagedError && e.status >= 400 && e.status < 500) remember();
      throw e;
    }
  }
  const activation = mode?.activation;
  useEffect(() => { setConfirmed(false); }, [activation?.id, activation?.version]);
  return <div className="project-detail">
    <h2>{id}</h2><Prompts project={id} /><p>Modo: {activation?.status ?? "sin activación gestionada"}</p>
    {mode?.refusal && <p className="error">{mode.refusal}</p>}
    {connection && <p role="status" className="error">{connection}</p>}
    {error && <p role="alert" className="error">{error}</p>}
    <Evidence title="Modo, deriva e historial de activaciones" value={mode} />
    <details><summary>Migrar o revertir el proyecto</summary>
      <p>La activación copia el histórico y crea el marcador gestionado. La exclusión con el motor legacy es cooperativa. La reversión exporta el estado y retira el marcador.</p>
      <button disabled={busy} onClick={() => void operate(async () => { setPreview(await managed<S["MigrationPreviewRead"]>(`/projects/${id}/migration/preview`)); setConfirmed(false); })}>Vista previa</button>
      {preview && <><p>Vista previa: {preview.ready ? "lista" : "bloqueada"}</p><Evidence title="Inventario, cambios y bloqueos" value={preview} /></>}
      <label>Motivo y comprobación realizada<input value={reason} onChange={e => setReason(e.target.value)} maxLength={2000} /></label>
      <label className="check"><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />Confirmo que el motor legacy está detenido y autorizo la transición seleccionada.</label>
      <div className="pagination">
        {preview && <button disabled={busy || !confirmed || !reason.trim() || !preview.ready} onClick={() => void operate(async () => {
          await managedApi.activate(id, { preview_sha256: preview.inventory_sha256, legacy_stopped: reason }); setPreview(undefined); setConfirmed(false);
        })}>Activar modo gestionado</button>}
        {activation && (activation.status === "PREPARING" ? ["resume", "abandon"] : activation.status === "ACTIVE" ? ["revert"] : activation.status === "REVERTING" ? ["resume-revert"] : []).map(action =>
          <button key={action} disabled={busy || !confirmed || !reason.trim()} onClick={() => void operate(async () => {
            await managedApi.transition(activation.id, action, { expected_version: activation.version, reason }); setConfirmed(false); setPreview(undefined);
          })}>{{ resume: "Reanudar activación", abandon: "Abandonar activación", revert: "Revertir a legacy", "resume-revert": "Reanudar reversión" }[action]}</button>)}
      </div>
    </details>
    <h3>Encolar tarea</h3>
    <form onSubmit={e => { e.preventDefault(); if (!pendingRef.current) void operate(() => send(jobRequest(`/projects/${id}/runs`, { task_id: task, phase_id: phase, text }))); }}>
      <div className="form-row"><label>Tarea<input value={task} onChange={e => setTask(e.target.value)} required maxLength={120} /></label>
        <label>Fase<input value={phase} onChange={e => setPhase(e.target.value)} required maxLength={120} /></label></div>
      <label>Contrato de tarea<textarea value={text} onChange={e => setText(e.target.value)} required maxLength={200000} rows={9} /></label>
      <button disabled={busy || !!pending || !text.trim()}>Encolar tarea</button>
    </form>
    {pending && <div className="error"><p>Envío sin respuesta confirmada. Repetir conserva exactamente el contenido y la clave.</p>
      <Evidence title="Solicitud pendiente" value={pending} /><button disabled={busy} onClick={() => void operate(() => send(pending))}>Repetir envío pendiente</button></div>}
    <h3>Historial de tareas</h3>
    <ul className="legacy-list">{runs?.items.map(run => <li key={run.id}><button className="choice" aria-pressed={runId === run.id} onClick={() => setRunId(run.id)}>
      <strong>{run.task_id} · {run.status}</strong><small>{run.id}</small></button></li>)}</ul>
    <div className="pagination"><button disabled={!offset} onClick={() => setOffset(Math.max(0, offset - 30))}>Anteriores</button>
      <button disabled={runs?.next_offset == null} onClick={() => setOffset(runs!.next_offset!)}>Siguientes</button></div>
    {runId && <Run key={runId} id={runId} refresh={refresh} busy={busy || !!pending} operate={operate} send={send} />}
  </div>;
}

function Run({ id, refresh, busy, operate, send }: { id: string; refresh: number; busy: boolean; operate: (f: () => Promise<unknown>) => Promise<void>; send: (p: Pending) => Promise<void> }) {
  const [run, setRun] = useState<S["ManagedRunRead"]>();
  const [jobs, setJobs] = useState<S["ManagedJobRead"][]>([]);
  const [attempts, setAttempts] = useState<S["Page_ManagedAttemptRead_"]>();
  const [offset, setOffset] = useState(0);
  const [events, setEvents] = useState<S["ManagedEventRead"][]>([]);
  const cursor = useRef(0);
  const [error, setError] = useState("");
  const [reason, setReason] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [commitConfirmed, setCommitConfirmed] = useState(false);
  useEffect(() => {
    let active = true;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try {
        const [r, j, a, e] = await Promise.all([managed<S["ManagedRunRead"]>(`/runs/${id}`), managed<S["ManagedJobRead"][]>(`/runs/${id}/jobs`),
          managed<S["Page_ManagedAttemptRead_"]>(`/runs/${id}/attempts?offset=${offset}`), managed<S["ManagedEventsRead"]>(`/runs/${id}/events?after=${cursor.current}&limit=50`)]);
        if (active) {
          setRun(r); setJobs(j); setAttempts(a); setError(""); cursor.current = e.cursor;
          setEvents(previous => [...previous, ...e.items.filter(item => !previous.some(old => old.sequence === item.sequence))]);
          timer = setTimeout(() => void poll(), e.has_more ? 0 : 1500);
        }
      } catch (e) { if (active) { setError(`Sin actualizar: ${message(e)}`); timer = setTimeout(() => void poll(), 1500); } }
    }
    void poll(); return () => { active = false; clearTimeout(timer); };
  }, [id, offset, refresh]);
  useEffect(() => { setCommitConfirmed(false); setConfirmed(false); }, [run?.version]);
  if (!run) return <p role="status">{error || "Cargando ejecución…"}</p>;
  const locked = run.locked_by_job !== null;
  function action(name: S["RunActionCreate"]["action"]) {
    void operate(() => send(jobRequest(`/runs/${id}/actions`, { action: name, expected_version: run!.version })));
  }
  return <section className="evidence-detail">
    <h2>{run.task_id} · {run.status}</h2><p>Etapa: {run.stage} · Versión observada: {run.version}</p>
    {error && <p role="status" className="error">{error}</p>}
    {run.history.stop && <p className="error">Bloqueo: {run.history.stop.reason}</p>}
    <p>{run.status === "COMMITTED" ? "Contenido revisado guardado en el commit indicado." : run.history.acceptance?.eligible ? "Contenido aceptado y elegible para commit." : "Sin aceptación vigente para commit."}</p>
    {run.commit && <p>Commit: {run.commit.status} · <code>{run.commit.commit ?? run.commit.expected_commit}</code></p>}
    <p className="hint">COMMITTED conserva un checkpoint del trabajo revisado; la integración en la rama destino queda pendiente.</p>
    {run.history.cycles.map(c => <div key={c.number}><h3>Revisión {c.number} · {c.verdict ?? "sin veredicto"}</h3>
      <details><summary>Diff revisado</summary><pre>{c.diff}</pre></details>
      <Evidence title="Tests y evidencia validada" value={c.validation} /><Evidence title="Hallazgos y revisión" value={c.review} />
    </div>)}
    <Evidence title="Contrato, revisiones y aceptación" value={run.history} />
    <Evidence title="Evidencia de commit y versiones" value={{ commit: run.commit, versions: run.versions }} />
    <div className="pagination">
      <button disabled={busy || locked || !!error || !run.actions.includes("revalidate")} onClick={() => action("revalidate")}>Revalidar y revisar</button>
      <button disabled={busy || locked || !!error || !run.actions.includes("retry_executor")} onClick={() => { if (window.confirm("¿Reintentar el ejecutor? Consume el presupuesto de correcciones y puede modificar el trabajo.")) action("retry_executor"); }}>Reintentar ejecutor</button>
    </div>
    <label className="check"><input type="checkbox" checked={commitConfirmed} onChange={e => setCommitConfirmed(e.target.checked)} />He revisado la evidencia de esta versión y confirmo el commit.</label>
    <button disabled={busy || locked || !!error || !commitConfirmed || !run.actions.includes("commit")} onClick={() => action("commit")}>Confirmar commit</button>
    <Permissions run={run} busy={busy || !!error} refresh={refresh} operate={operate} />
    <h3>Jobs y recuperación</h3>
    {jobs.map(job => <div key={job.id} className="entry"><strong>Job {job.id} · {job.action} · {job.status}</strong>
      {job.diagnostic && <p>{job.diagnostic}</p>}
      {job.status === "RECOVERY_REQUIRED" && <>
        <p>El lease vencido no prueba que el escritor terminó. Comprueba su parada antes de liberar el checkout; después podrás revalidar sin repetir el ejecutor.</p>
        <label>Evidencia de parada<input value={reason} onChange={e => setReason(e.target.value)} maxLength={2000} /></label>
        <label className="check"><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />Confirmo explícitamente que el escritor anterior está detenido.</label>
        <button disabled={busy || !!error || !confirmed || !reason.trim() || !job.owner_token} onClick={() => void operate(async () => {
          await managedApi.confirm(job.id, { owner_token: job.owner_token!, expected_version: run.version, reason }); setConfirmed(false);
        })}>Confirmar escritor detenido</button>
      </>}
      <Evidence title={`Datos del job ${job.id}`} value={job} />
    </div>)}
    <h3>Intentos</h3>
    {attempts?.items.map(a => <div className="entry" key={a.id}><strong>{a.number} · {a.role} · {a.status}</strong>
      <Evidence title="Selección, resultado, revisión y consumo reportado" value={a} /></div>)}
    <div className="pagination"><button disabled={!offset} onClick={() => setOffset(Math.max(0, offset - 30))}>Intentos anteriores</button>
      <button disabled={attempts?.next_offset == null} onClick={() => setOffset(attempts!.next_offset!)}>Más intentos</button></div>
    <h3>Eventos confirmados ({events.length})</h3>
    <ol>{events.map(e => <li key={e.sequence}><strong>{e.sequence} · {e.kind}</strong><time>{e.recorded_at}</time><Evidence title="Evidencia del evento" value={e.payload} /></li>)}</ol>
  </section>;
}

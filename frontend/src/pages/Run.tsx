import { useEffect, useRef, useState } from "react";
import { Logs } from "../Logs";
import { managed, managedApi, jobRequest, ManagedError } from "../managed-api";
import type { S } from "../managed-api";
import { Link, navigate } from "../navigation";
import { Permissions } from "../Permissions";
import { href, runRoute } from "../router.ts";
import { Tests } from "../Tests";
import { Empty, Evidence, Fields, Hash, Loading, PageHeader, Pagination, Stale, Status, message, usePoll, when } from "../ui";
import { useWorkspace } from "../workspace";

/** `/runs/:id`: resuelve la URL canónica del run y la sustituye en el historial. */
export function RunRedirect({ run }: { run: string }) {
  const read = usePoll<S["ManagedRunRead"]>(`/runs/${encodeURIComponent(run)}`, 0);
  useEffect(() => {
    const route = read.data && runRoute(read.data);
    if (route) navigate(route, { replace: true });
  }, [read.data]);
  if (read.missing) return <Empty title="No existe ese run"><p>Comprueba el enlace o vuelve a la <Link to={{ name: "home" }}>lista de proyectos</Link>.</p></Empty>;
  if (read.data && !read.data.project_id) return <Empty title="El run pertenece a un checkout sin proyecto registrado"><p>Se conserva su evidencia, pero no tiene página en esta interfaz.</p></Empty>;
  return read.error ? <p role="alert" className="state state-error">{read.error}</p> : <Loading>Buscando el run…</Loading>;
}

export function RunPage({ phase, task, run: id }: { phase: string; task: string; run: string }) {
  const { project, busy, refresh, operate, send } = useWorkspace();
  const [run, setRun] = useState<S["ManagedRunRead"]>();
  const [jobs, setJobs] = useState<S["ManagedJobRead"][]>([]);
  const [attempts, setAttempts] = useState<S["Page_ManagedAttemptRead_"]>();
  const [offset, setOffset] = useState(0);
  const [events, setEvents] = useState<S["ManagedEventRead"][]>([]);
  const [missing, setMissing] = useState(false);
  const cursor = useRef(0);
  const [error, setError] = useState("");
  const [reason, setReason] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [commitConfirmed, setCommitConfirmed] = useState(false);
  const path = `/runs/${encodeURIComponent(id)}`;
  useEffect(() => {
    let active = true;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try {
        const [r, j, a, e] = await Promise.all([managed<S["ManagedRunRead"]>(path), managed<S["ManagedJobRead"][]>(`${path}/jobs`),
          managed<S["Page_ManagedAttemptRead_"]>(`${path}/attempts?offset=${offset}`), managed<S["ManagedEventsRead"]>(`${path}/events?after=${cursor.current}&limit=50`)]);
        if (active) {
          setRun(r); setJobs(j); setAttempts(a); setError(""); cursor.current = e.cursor;
          setEvents(previous => [...previous, ...e.items.filter(item => !previous.some(old => old.sequence === item.sequence))]);
          timer = setTimeout(() => void poll(), e.has_more ? 0 : 1500);
        }
      } catch (e) {
        if (!active) return;
        if (e instanceof ManagedError && e.status === 404) setMissing(true);
        setError(message(e)); timer = setTimeout(() => void poll(), 3000);
      }
    }
    void poll(); return () => { active = false; clearTimeout(timer); };
  }, [path, offset, refresh]);
  useEffect(() => { setCommitConfirmed(false); setConfirmed(false); }, [run?.version]);
  // Una URL con otra fase, tarea o proyecto se corrige a la canónica sin añadir historial.
  const canonical = run && runRoute(run);
  useEffect(() => {
    if (canonical && href(canonical) !== window.location.pathname) navigate(canonical, { replace: true });
  }, [canonical && href(canonical)]);
  if (missing && !run) return <Empty title="No existe ese run"><p>Vuelve a la tarea <Link className="mono" to={{ name: "task", project, phase, task }}>{task}</Link>.</p></Empty>;
  if (!run) return error ? <p role="alert" className="state state-error">{error}</p> : <Loading>Cargando run…</Loading>;
  const locked = run.locked_by_job !== null;
  const stale = !!error;
  function action(name: S["RunActionCreate"]["action"]) {
    void operate(() => send(jobRequest(`/runs/${run!.id}/actions`, { action: name, expected_version: run!.version })));
  }
  const documentRun = run.purpose === "document_export" || run.purpose === "bootstrap";
  const outcome = documentRun ? (run.purpose === "bootstrap"
    ? "Creación documental confirmada. El commit inicial y la primera fase se consultan en el resumen del proyecto."
    : "Exportación documental confirmada por su diff. El resultado y el commit se consultan en el historial de la fase.")
    : run.status === "COMMITTED" ? "Contenido revisado guardado en el commit indicado."
      : run.history.acceptance?.eligible ? "Contenido aceptado y elegible para commit." : "Sin aceptación vigente para commit.";
  return <>
    <PageHeader code title={`Run ${run.id.slice(0, 8)}`} aside={<Status value={run.status} />}>
      <p>Tarea <Link className="mono" to={{ name: "task", project, phase: run.phase_id, task: run.task_id }}>{run.task_id}</Link> de la fase <Link className="mono" to={{ name: "phase", project, phase: run.phase_id }}>{run.phase_id}</Link>. {outcome}</p>
    </PageHeader>
    <Stale error={error} />
    {run.history.stop && <p className="state state-attention">Bloqueo en {run.history.stop.stage}: {run.history.stop.reason}</p>}

    <section className="panel" aria-labelledby="run-summary">
      <h2 id="run-summary">Resumen</h2>
      <Fields items={[
        ["Etapa", run.stage], ["Versión observada", `${run.version}`], ["Revisiones", `${run.revisions} de ${run.revision_limit}`],
        ["Commit", run.commit ? <><Status value={run.commit.status} /> <Hash value={run.commit.commit ?? run.commit.expected_commit} /></> : <span className="muted">sin commit</span>],
        ["Creado", when(run.created_at)], ["Identificador", <code>{run.id}</code>],
      ]} />
      {!documentRun && <p className="hint">Un commit conserva un checkpoint del trabajo revisado; la integración en la rama destino queda pendiente.</p>}
      <Evidence title="Contrato, revisiones y aceptación" value={run.history} />
      <Evidence title="Evidencia de commit y versiones" value={{ commit: run.commit, versions: run.versions }} />
    </section>

    {run.purpose === "task" && ["revalidate", "retry_executor", "commit"].some(a => run.actions.includes(a as S["RunActionCreate"]["action"])) && <section className="decision decision-attention" aria-labelledby="run-decision">
      <h2 id="run-decision">Decisión</h2>
      <div className="actions">
        <button className="button-quiet" disabled={busy || locked || stale || !run.actions.includes("revalidate")} onClick={() => action("revalidate")}>Revalidar y revisar</button>
        <button className="button-quiet" disabled={busy || locked || stale || !run.actions.includes("retry_executor")} onClick={() => { if (window.confirm("¿Reintentar el ejecutor? Consume el presupuesto de correcciones y puede modificar el trabajo.")) action("retry_executor"); }}>Reintentar ejecutor</button>
      </div>
      <label className="check"><input type="checkbox" checked={commitConfirmed} onChange={e => setCommitConfirmed(e.target.checked)} />He revisado la evidencia de esta versión y confirmo el commit.</label>
      <button disabled={busy || locked || stale || !commitConfirmed || !run.actions.includes("commit")} onClick={() => action("commit")}>Confirmar commit</button>
    </section>}

    {run.history.cycles.length > 0 && <section className="panel" aria-labelledby="run-cycles">
      <h2 id="run-cycles">Revisiones</h2>
      {run.history.cycles.map(c => <div className="entry" key={c.number}>
        <h3>Revisión {c.number}: {c.verdict ?? "sin veredicto"}</h3>
        <details className="evidence"><summary>Diff revisado ({c.changed_paths.length} rutas)</summary><pre className="diff">{c.diff}</pre></details>
        <Tests runId={run.id} cycle={c.number} validation={c.validation} />
        <Evidence title="Tests y evidencia validada" value={c.validation} /><Evidence title="Hallazgos y revisión" value={c.review} />
      </div>)}
    </section>}

    {run.purpose === "task" && <Permissions run={run} busy={busy || stale} refresh={refresh} operate={operate} />}

    <section className="panel" aria-labelledby="run-jobs">
      <h2 id="run-jobs">Trabajos y recuperación</h2>
      {!jobs.length && <p className="hint">Sin trabajos registrados.</p>}
      {jobs.map(job => <div key={job.id} className={job.status === "RECOVERY_REQUIRED" ? "entry entry-open" : "entry"}>
        <p><strong>Trabajo {job.id}</strong> {job.action} <Status value={job.status} /></p>
        {job.diagnostic && <p>{job.diagnostic}</p>}
        {job.status === "RECOVERY_REQUIRED" && <div className="decision decision-attention">
          <p>El lease vencido no prueba que el escritor terminó. Comprueba su parada antes de liberar el checkout; {run.purpose === "bootstrap" ? "después concilia el bootstrap confirmado en el resumen del proyecto." : run.purpose === "bootstrap_discovery" ? "la propuesta queda desconocida; solicitar otra requiere una acción propia." : run.purpose === "document_export" ? "después previsualiza la exportación en la fase para conciliar la intención conservada." : "después podrás revalidar sin repetir el ejecutor."}</p>
          <label>Evidencia de parada<input value={reason} onChange={e => setReason(e.target.value)} maxLength={2000} /></label>
          <label className="check"><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />Confirmo explícitamente que el escritor anterior está detenido.</label>
          <button disabled={busy || stale || !confirmed || !reason.trim() || !job.owner_token} onClick={() => void operate(async () => {
            await managedApi.confirm(job.id, { owner_token: job.owner_token!, expected_version: run.version, reason }); setConfirmed(false);
          })}>Confirmar escritor detenido</button>
        </div>}
        <Evidence title={`Datos del trabajo ${job.id}`} value={job} />
      </div>)}
    </section>

    <section className="panel" aria-labelledby="run-attempts">
      <h2 id="run-attempts">Intentos</h2>
      {!attempts?.items.length && <p className="hint">Sin intentos registrados.</p>}
      {attempts?.items.map(a => <div className="entry" key={a.id}>
        <p><strong>Intento {a.number}</strong> {a.role} <Status value={a.status} /></p>
        <Logs runId={run.id} attemptId={a.id} />
        <Evidence title="Selección, resultado, revisión y consumo reportado" value={a} /></div>)}
      <Pagination offset={offset} next={attempts?.next_offset} onChange={setOffset} label="Páginas de intentos" />
    </section>

    <details className="panel panel-collapsible">
      <summary><h2>Eventos confirmados <span className="count">{events.length}</span></h2></summary>
      <ol className="events">{events.map(e => <li key={e.sequence}><p><strong>{e.sequence}</strong> {e.kind} {when(e.recorded_at)}</p><Evidence title="Evidencia del evento" value={e.payload} /></li>)}</ol>
    </details>
  </>;
}

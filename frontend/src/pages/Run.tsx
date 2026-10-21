import { memo, useEffect, useRef, useState } from "react";
import { appendDiffPage, byteSize } from "../diff.ts";
import type { LoadedDiff } from "../diff.ts";
import { Logs } from "../Logs";
import { managed, managedApi, jobRequest, ManagedError } from "../managed-api";
import type { S } from "../managed-api";
import { Link, navigate } from "../navigation";
import { Permissions } from "../Permissions";
import { href, runRoute } from "../router.ts";
import { Tests } from "../Tests";
import { DiffLines, Empty, Evidence, Fields, Hash, Loading, PageHeader, Pagination, Stale, Status, message, usePoll, when } from "../ui";
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

// Con un job en cola, en curso o por recuperar el run cambia solo; sin él, solo cambia por una acción nueva
// (de esta página, que relee al momento, o de otra pestaña), así que basta un sondeo espaciado.
const ACTIVE_POLL = 1500;
const SETTLED_POLL = 15000;

export function RunPage({ phase, task, run: id }: { phase: string; task: string; run: string }) {
  const { project, busy, refresh, operate, send } = useWorkspace();
  const [run, setRun] = useState<S["ManagedRunRead"]>();
  const [jobs, setJobs] = useState<S["Page_ManagedJobRead_"]>();
  const [jobOffset, setJobOffset] = useState(0);
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
        const [r, j, a, e] = await Promise.all([managed<S["ManagedRunRead"]>(path), managed<S["Page_ManagedJobRead_"]>(`${path}/jobs?offset=${jobOffset}`),
          managed<S["Page_ManagedAttemptRead_"]>(`${path}/attempts?offset=${offset}`), managed<S["ManagedEventsRead"]>(`${path}/events?after=${cursor.current}&limit=50`)]);
        if (active) {
          setRun(r); setJobs(j); setAttempts(a); setError(""); cursor.current = e.cursor;
          setEvents(previous => [...previous, ...e.items.filter(item => !previous.some(old => old.sequence === item.sequence))]);
          timer = setTimeout(() => void poll(), e.has_more ? 0 : r.active_job === null ? SETTLED_POLL : ACTIVE_POLL);
        }
      } catch (e) {
        if (!active) return;
        if (e instanceof ManagedError && e.status === 404) setMissing(true);
        setError(message(e)); timer = setTimeout(() => void poll(), 3000);
      }
    }
    void poll(); return () => { active = false; clearTimeout(timer); };
  }, [path, offset, jobOffset, refresh]);
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
      {typeof run.history.task?.additional_notes === "string" && <div className="entry"><h3>Notas adicionales</h3><p className="turn-answer">{run.history.task.additional_notes}</p></div>}
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
        <CycleDiff runId={run.id} number={c.number} sha256={c.diff_sha256} bytes={c.diff_bytes} paths={c.changed_paths.length} />
        <Tests runId={run.id} cycle={c.number} validation={c.validation} />
        {c.formatting && <Evidence title={`Formateo del perfil (${(c.formatting.paths as string[] | undefined)?.length ?? 0} archivos)`} value={c.formatting} />}
        <Evidence title="Tests y evidencia validada" value={c.validation} /><Evidence title="Hallazgos y revisión" value={c.review} />
      </div>)}
    </section>}

    {run.purpose === "task" && <Permissions run={run} busy={busy || stale} refresh={refresh} operate={operate} />}

    <section className="panel" aria-labelledby="run-jobs">
      <h2 id="run-jobs">Trabajos y recuperación</h2>
      {!jobs?.items.length && <p className="hint">Sin trabajos registrados.</p>}
      {jobs?.items.map(job => <div key={job.id} className={job.status === "RECOVERY_REQUIRED" ? "entry entry-open" : "entry"}>
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
      <Pagination offset={jobOffset} next={jobs?.next_offset} onChange={setJobOffset} label="Páginas de trabajos" />
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

/**
 * Diff revisado de un ciclo: se lee al abrirlo, por páginas de 64 KiB ligadas al hash del resumen del run, y no
 * se vuelve a pedir en cada sondeo. Una página que no continúa lo mostrado lo descarta en lugar de mezclarlo.
 * Props escalares y memo: el sondeo del run no repinta un diff de miles de líneas, y cada página es su tramo.
 */
const CycleDiff = memo(function CycleDiff({ runId, number, sha256, bytes, paths }: { runId: string; number: number; sha256: string; bytes: number; paths: number }) {
  const [diff, setDiff] = useState<LoadedDiff>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const request = useRef(0);
  useEffect(() => { request.current++; setDiff(undefined); setError(""); setLoading(false); }, [runId, number, sha256]);
  async function more(current?: LoadedDiff) {
    const id = ++request.current;
    setLoading(true); setError("");
    try {
      const page = await managed<S["CycleDiffRead"]>(`/runs/${encodeURIComponent(runId)}/cycles/${number}/diff?offset=${current?.next ?? 0}&sha256=${sha256}`);
      if (id !== request.current) return;
      const next = appendDiffPage(current, page);
      setDiff(next ?? undefined);
      if (!next) setError("La página leída no continúa el diff mostrado. Vuelve a cargarlo.");
    } catch (e) {
      if (id === request.current) setError(message(e));
    } finally {
      if (id === request.current) setLoading(false);
    }
  }
  return <details className="evidence" onToggle={e => { if (e.currentTarget.open && !diff && !loading) void more(); }}>
    <summary>Diff revisado ({paths} rutas, {byteSize(bytes)})</summary>
    {diff && (diff.size ? <pre className="diff" aria-label={`Diff revisado de la revisión ${number}`}>{diff.pages.map((page, index) => <DiffLines key={index} text={page} />)}</pre>
      : <p className="hint">Sin cambios de contenido.</p>)}
    {loading && <Loading>Cargando diff…</Loading>}
    {error && <p role="alert" className="state state-error">{error}</p>}
    {diff && diff.size > 0 && <p className="hint">{diff.next === null ? "Completo" : `${byteSize(diff.loaded)} de ${byteSize(diff.size)}`} · <Hash value={diff.sha256} /></p>}
    {(diff?.next != null || (error && !loading)) && <button type="button" className="button-quiet" disabled={loading} onClick={() => void more(diff)}>
      {diff ? "Cargar más" : "Cargar el diff"}</button>}
  </details>;
});

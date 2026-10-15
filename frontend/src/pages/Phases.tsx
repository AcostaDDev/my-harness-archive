import { lazy, Suspense, useState } from "react";
import type { S } from "../managed-api";
import { Link } from "../navigation";
import { PhaseCreate, PhaseDetail } from "../Phases";
import { Empty, Loading, PageHeader, Pagination, PhaseRail, Stale, Status, usePoll, when } from "../ui";
import { useWorkspace } from "../workspace";
import { TaskForm } from "./shared";

const TransitionPanel = lazy(() => import("./Planning").then(module => ({ default: module.TransitionPanel })));

export function PhaseListPage() {
  const { project, refresh } = useWorkspace();
  const phases = usePoll<S["PhaseSummaryRead"][]>(`/projects/${project}/phases`, 3000, refresh);
  const open = phases.data?.some(p => !["CLOSED", "ABANDONED"].includes(p.status));
  return <>
    <PageHeader title="Fases"><p>Cada fase agrupa tareas aceptadas y se cierra con su propia autorización sobre la evidencia READY.</p></PageHeader>
    <Stale error={phases.data ? phases.error : undefined} />
    {!phases.data ? <Loading /> : !phases.data.length ? <Empty title="Este proyecto aún no tiene fases">
      <p>Define la primera con su objetivo y sus criterios de salida.</p></Empty>
      : <div className="table-scroll" role="region" aria-label="Fases del proyecto" tabIndex={0}>
        <table className="table">
          <thead><tr><th scope="col">Fase</th><th scope="col">Objetivo</th><th scope="col">Estado</th><th scope="col">Actualizada</th></tr></thead>
          <tbody>{[...phases.data].reverse().map(p => <tr key={p.id}>
            <td><Link className="mono strong" to={{ name: "phase", project, phase: p.code }}>{p.code}</Link></td>
            <td className="wide">{p.objective}</td>
            <td><Status kind="phase" value={p.status} /></td>
            <td>{when(p.updated_at)}</td>
          </tr>)}</tbody>
        </table>
      </div>}
    {phases.data && !open && <PhaseCreate />}
  </>;
}

export function PhasePage({ code }: { code: string }) {
  const { project, refresh } = useWorkspace();
  const [offset, setOffset] = useState(0);
  const base = `/projects/${project}/phases/${encodeURIComponent(code)}`;
  const phase = usePoll<S["PhaseRead"]>(base, 1500, refresh);
  const tasks = usePoll<S["Page_PhaseTaskRead_"]>(`${base}/tasks?offset=${offset}`, 2000, refresh);
  const info = usePoll<S["ManagedProjectRead"]>(`/projects/${project}`, 0);
  const phases = usePoll<S["PhaseSummaryRead"][]>(`/projects/${project}/phases`, 5000, refresh);
  const data = phase.data;
  const v2 = info.data?.documents === "v2";
  // La fase siguiente en el checkout (la lista va en orden de creación); null si esta es la última.
  const index = phases.data?.findIndex(p => p.code === code) ?? -1;
  const following = phases.data && index >= 0 ? phases.data[index + 1]?.code ?? null : undefined;
  const undefinedPhase = phase.missing && !!tasks.data;
  const open = data && !["CLOSED", "ABANDONED"].includes(data.status);
  if (phase.missing && tasks.data && !tasks.data.items.length && !offset) return <>
    <PageHeader code title={code} />
    <Empty title={`No hay ninguna fase ${code} en este proyecto`}>
      <p>Ni definida ni con runs. Vuelve a <Link to={{ name: "phases", project }}>Fases</Link> para ver las existentes o definir una.</p>
    </Empty>
  </>;
  return <>
    <PageHeader code title={code} aside={data && <Status kind="phase" value={data.status} />}>
      {data ? <p>{String(data.definition.objective)}</p> : undefinedPhase ? <p>Runs agrupados con este código, sin definición de fase gestionada.</p> : <Loading />}
    </PageHeader>
    <Stale error={data ? phase.error : undefined} />
    {data && <PhaseRail status={data.status} />}
    <section className="panel" aria-labelledby="phase-tasks">
      <h2 id="phase-tasks">Tareas</h2>
      {!tasks.data ? <Loading /> : !tasks.data.items.length ? <Empty title="Sin tareas todavía">
        <p>{data ? "La definición no enumera tareas y ninguna tiene runs. " : ""}Encola la primera abajo.</p></Empty>
        : <div className="table-scroll" role="region" aria-label="Tareas de la fase" tabIndex={0}>
          <table className="table">
            <thead><tr><th scope="col">Tarea</th><th scope="col">En la definición</th><th scope="col">Último run</th><th scope="col" className="numeric">Runs</th><th scope="col">Commit aceptado</th></tr></thead>
            <tbody>{tasks.data.items.map(t => {
              const commit = data?.tasks[t.task_id];
              return <tr key={t.task_id}>
                <td><Link className="mono strong" to={{ name: "task", project, phase: code, task: t.task_id }}>{t.task_id}</Link></td>
                <td>{t.planned ? "Sí" : "No"}</td>
                <td>{t.latest ? <Status value={t.latest.status} /> : <span className="muted">sin runs</span>}</td>
                <td className="numeric">{t.runs}</td>
                <td>{commit?.commit ? <code className="hash" title={commit.commit}>{commit.commit.slice(0, 12)}</code> : <span className="muted">{data ? "pendiente" : "no aplica"}</span>}</td>
              </tr>;
            })}</tbody>
          </table>
        </div>}
      <Pagination offset={offset} next={tasks.data?.next_offset} onChange={setOffset} label="Páginas de tareas" />
    </section>
    {(open || undefinedPhase) && <TaskForm phase={code} title="Encolar tarea en esta fase" />}
    {data && v2 && following !== undefined && (["CLOSED", "ABANDONED"].includes(data.status) || following)
      && <Suspense fallback={<Loading />}><TransitionPanel phase={data} following={following} /></Suspense>}
    {data && v2 && !following && !["CLOSED", "ABANDONED"].includes(data.status) && <p className="hint">Al cerrar o abandonar la fase podrás pasar a la siguiente del ROADMAP. Puedes <Link to={{ name: "plan", project, phase: code }}>planificarla ya con el revisor</Link>.</p>}
    {data && <PhaseDetail phase={data} stale={!!phase.error} />}
  </>;
}

import { useState } from "react";
import type { S } from "../managed-api";
import { Link } from "../navigation";
import { Empty, Loading, PageHeader, Pagination, PhaseRail, Stale, Status, usePoll } from "../ui";
import { useWorkspace } from "../workspace";
import { Preparation } from "./Preparation";
import { RunTable, TaskForm } from "./shared";

const OPEN: S["PhaseSummaryRead"]["status"][] = ["ACTIVE", "CHECKING", "READY_TO_CLOSE", "NEEDS_RECONCILIATION", "BLOCKED", "CLOSING"];
export function ProjectPage() {
  const { project, refresh } = useWorkspace();
  const [offset, setOffset] = useState(0);
  const detail = usePoll<S["ManagedProjectRead"]>(`/projects/${project}`, 10000, refresh);
  const mode = usePoll<S["ModeRead"]>(`/projects/${project}/mode`, 3000, refresh);
  const phases = usePoll<S["PhaseSummaryRead"][]>(`/projects/${project}/phases`, 3000, refresh);
  const runs = usePoll<S["Page_ManagedRunSummaryRead_"]>(`/projects/${project}/runs?offset=${offset}&limit=10`, 2000, refresh);
  if (detail.missing) return <Empty title={`No existe el proyecto ${project}`}><p>Comprueba el enlace o vuelve a la <Link to={{ name: "home" }}>lista de proyectos</Link>.</p></Empty>;
  const open = phases.data?.find(p => OPEN.includes(p.status));
  return <>
    <PageHeader code title={project}>
      {detail.data ? <p><code className="path">{detail.data.root}</code> con el perfil {detail.data.profile}{detail.data.documents === "v2" ? " y documentos por fase" : ""}.</p> : <Loading />}
    </PageHeader>
    <Stale error={detail.data ? detail.error ?? mode.error ?? phases.error ?? runs.error : undefined} />
    {mode.data?.refusal && <p className="state state-attention">{mode.data.refusal}</p>}

    {detail.data?.versions.project_recipe && !!phases.data?.length && <Preparation />}

    <section className="panel" aria-labelledby="active-phase">
      <h2 id="active-phase">Fase abierta</h2>
      {!phases.data ? <Loading /> : open ? <>
        <div className="phase-summary">
          <Link className="mono strong large" to={{ name: "phase", project, phase: open.code }}>{open.code}</Link>
          <Status kind="phase" value={open.status} />
        </div>
        <p>{open.objective}</p>
        <PhaseRail status={open.status} />
      </> : <Empty title="No hay ninguna fase abierta">
        <p>{phases.data.length ? `${phases.data.length} fases cerradas o abandonadas. ` : ""}Define la siguiente en <Link to={{ name: "phases", project }}>Fases</Link>.</p>
      </Empty>}
    </section>

    <section className="panel" aria-labelledby="recent-runs">
      <h2 id="recent-runs">Actividad reciente</h2>
      {runs.data ? <RunTable runs={runs.data.items} project={project} /> : <Loading />}
      <Pagination offset={offset} next={runs.data?.next_offset} onChange={setOffset} size={10} label="Páginas de runs" />
    </section>

    {detail.data?.documents === "v2" && !phases.data?.length && <p><Link to={{ name: "onboarding", project }}>Incorporar un repositorio sin harness</Link></p>}
    {detail.data?.documents === "v2" && !phases.data?.length ? <Creation /> : <TaskForm />}
  </>;
}

/** v2 project (H6.5/H6.2 E4): created through the definition conversation, on its own page. */
function Creation() {
  const { project, refresh } = useWorkspace();
  const status = usePoll<S["BootstrapStatusRead"]>(`/projects/${project}/bootstrap`, 5000, refresh);
  const op = status.data?.definition_operation;
  if (!status.data) return null;
  if (op?.status === "COMPLETED") return op.first_task_run ? <TaskForm /> : <section className="decision decision-attention" aria-labelledby="creation-title">
    <h2 id="creation-title">Proyecto creado: falta la primera tarea</h2>
    <p>El commit raíz y la fase P001 están hechos. Encola la primera tarea desde la <Link to={{ name: "setup", project }}>creación</Link>, con el plan de NEXT_STEPS.</p>
  </section>;
  if (!status.data.enabled && !op) return <TaskForm />;
  return <section className="decision decision-attention" aria-labelledby="creation-title">
    <h2 id="creation-title">{op ? "Creación en curso" : "Este proyecto aún no está creado"}</h2>
    {status.data.import_required ? <p>{status.data.diagnostic}</p>
      : <p>Defínelo con el revisor a partir de un brief: los borradores se aplican en la carpeta con tu confirmación y, al aceptar, el harness hace el commit raíz con la fase P001.</p>}
    <p><Link to={{ name: "setup", project }}>{op ? "Ver la creación" : "Ir a la creación"}</Link></p>
  </section>;
}

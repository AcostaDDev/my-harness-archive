import { useEffect, useState } from "react";
import { managed, managedApi } from "../managed-api";
import type { S } from "../managed-api";
import { Link } from "../navigation";
import { Empty, Evidence, Loading, PageHeader, Pagination, PhaseRail, Stale, Status, usePoll } from "../ui";
import { useWorkspace } from "../workspace";
import { RunTable, TaskForm } from "./shared";

const OPEN: S["PhaseSummaryRead"]["status"][] = ["ACTIVE", "CHECKING", "READY_TO_CLOSE", "NEEDS_RECONCILIATION", "BLOCKED", "CLOSING"];
const ACTIVATION: Record<S["ActivationRead"]["status"], string> = {
  PREPARING: "Activación en preparación", ACTIVE: "Modo gestionado activo", FAILED: "Activación fallida",
  REVERTING: "Reversión en curso", REVERTED: "Revertido al motor anterior",
};

export function ProjectPage() {
  const { project, refresh } = useWorkspace();
  const [offset, setOffset] = useState(0);
  const detail = usePoll<S["ManagedProjectRead"]>(`/projects/${project}`, 10000, refresh);
  const mode = usePoll<S["ModeRead"]>(`/projects/${project}/mode`, 3000, refresh);
  const phases = usePoll<S["PhaseSummaryRead"][]>(`/projects/${project}/phases`, 3000, refresh);
  const runs = usePoll<S["Page_ManagedRunSummaryRead_"]>(`/projects/${project}/runs?offset=${offset}&limit=10`, 2000, refresh);
  if (detail.missing) return <Empty title={`No existe el proyecto ${project}`}><p>Comprueba el enlace o vuelve a la <Link to={{ name: "home" }}>lista de proyectos</Link>.</p></Empty>;
  const open = phases.data?.find(p => OPEN.includes(p.status));
  const activation = mode.data?.activation;
  return <>
    <PageHeader code title={project} aside={activation ? <span className="status status-neutral">{ACTIVATION[activation.status]}</span> : undefined}>
      {detail.data ? <p><code className="path">{detail.data.root}</code> con el perfil {detail.data.profile}{detail.data.documents === "v2" ? " y documentos por fase" : ""}.</p> : <Loading />}
    </PageHeader>
    <Stale error={detail.data ? detail.error ?? mode.error ?? phases.error ?? runs.error : undefined} />
    {mode.data?.refusal && <p className="state state-attention">{mode.data.refusal}</p>}

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

    {detail.data?.documents === "v2" && !phases.data?.length && <p><Link to={{ name: "import", project }}>Importar un proyecto de un harness anterior</Link> · <Link to={{ name: "onboarding", project }}>Incorporar un repositorio sin harness</Link></p>}
    {detail.data?.documents === "v2" && !phases.data?.length ? <Creation /> : <TaskForm />}
    <Migration project={project} mode={mode.data} />
  </>;
}

/** Proyecto v2 (H6.5/H6.2 E4): se crea por la conversación de definición, en su propia página. */
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

export function Migration({ project, mode }: { project: string; mode?: S["ModeRead"] }) {
  const { busy, operate } = useWorkspace();
  const [preview, setPreview] = useState<S["MigrationPreviewRead"]>();
  const [reason, setReason] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const activation = mode?.activation;
  useEffect(() => { setConfirmed(false); }, [activation?.id, activation?.version]);
  const actions = !activation ? [] : activation.status === "PREPARING" ? ["resume", "abandon"] : activation.status === "ACTIVE" ? ["revert"] : activation.status === "REVERTING" ? ["resume-revert"] : [];
  const names: Record<string, string> = { resume: "Reanudar activación", abandon: "Abandonar activación", revert: "Revertir al motor anterior", "resume-revert": "Reanudar reversión" };
  return <details className="panel panel-collapsible">
    <summary><h2>Modo gestionado y migración</h2></summary>
    <p className="hint">La activación copia el histórico del motor anterior y crea el marcador gestionado. La exclusión con ese motor es cooperativa. La reversión exporta el estado y retira el marcador.</p>
    <Evidence title="Modo, deriva e historial de activaciones" value={mode ?? null} />
    <div className="decision">
      <button className="button-quiet" disabled={busy} onClick={() => void operate(async () => { setPreview(await managed<S["MigrationPreviewRead"]>(`/projects/${project}/migration/preview`)); setConfirmed(false); })}>Vista previa de la activación</button>
      {preview && <><p>Vista previa: {preview.ready ? "lista para activar" : "bloqueada"}.</p><Evidence title="Inventario, cambios y bloqueos" value={preview} /></>}
      <label>Motivo y comprobación realizada<input value={reason} onChange={e => setReason(e.target.value)} maxLength={2000} /></label>
      <label className="check"><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />Confirmo que el motor anterior está detenido y autorizo la transición seleccionada.</label>
      <div className="actions">
        {preview && <button disabled={busy || !confirmed || !reason.trim() || !preview.ready} onClick={() => void operate(async () => {
          await managedApi.activate(project, { preview_sha256: preview.inventory_sha256, legacy_stopped: reason }); setPreview(undefined); setConfirmed(false);
        })}>Activar modo gestionado</button>}
        {activation && actions.map(action => <button key={action} className={action === "revert" || action === "abandon" ? "button-danger" : undefined}
          disabled={busy || !confirmed || !reason.trim()} onClick={() => void operate(async () => {
            await managedApi.transition(activation.id, action, { expected_version: activation.version, reason }); setConfirmed(false); setPreview(undefined);
          })}>{names[action]}</button>)}
      </div>
    </div>
  </details>;
}

import { useState } from "react";
import { jobRequest } from "../managed-api";
import type { S } from "../managed-api";
import { Link } from "../navigation";
import { runRoute } from "../router.ts";
import { Empty, Status, when, usePoll } from "../ui";
import { useWorkspace } from "../workspace";
import { runBody, sourcePhases, sourceTasks } from "../task-sources.ts";
import { recipeLabel } from "../preparation.ts";

const PURPOSES: Record<S["ManagedRunSummaryRead"]["purpose"], string> = {
  task: "Tarea", phase_check: "Comprobación de fase", phase_close: "Cierre de fase", chat: "Chat",
  document_export: "Exportación documental", bootstrap: "Creación del proyecto", bootstrap_discovery: "Propuesta de creación",
  definition: "Definición", phase_planning: "Planificación de fase", project_import: "Importación", onboarding: "Incorporación", import_commit: "Commit de importación",
  document_edit: "Edición de documento",
  phase_transition: "Transición de fase",
};

/** Runs as rows linked to their canonical URL; the task and the phase link to their pages. */
export function RunTable({ runs, project, show = ["task", "phase"] }: { runs: S["ManagedRunSummaryRead"][]; project: string; show?: ("task" | "phase")[] }) {
  if (!runs.length) return <Empty title="Todavía no hay runs">
    <p>Encola una tarea para que el planificador, el ejecutor y el revisor trabajen sobre ella.</p></Empty>;
  return <div className="table-scroll" role="region" aria-label="Runs" tabIndex={0}>
    <table className="table">
      <thead><tr><th scope="col">Run</th>{show.includes("task") && <th scope="col">Tarea</th>}{show.includes("phase") && <th scope="col">Fase</th>}
        <th scope="col">Estado</th><th scope="col">Tipo</th><th scope="col" className="numeric">Revisiones</th><th scope="col">Actualizado</th></tr></thead>
      <tbody>{runs.map(run => {
        const route = runRoute({ ...run, project_id: run.project_id ?? project });
        return <tr key={run.id}>
          <td>{route ? <Link to={route} className="mono">{run.id.slice(0, 8)}</Link> : <code>{run.id.slice(0, 8)}</code>}</td>
          {show.includes("task") && <td><Link className="mono" to={{ name: "task", project, phase: run.phase_id, task: run.task_id }}>{run.task_id}</Link></td>}
          {show.includes("phase") && <td><Link className="mono" to={{ name: "phase", project, phase: run.phase_id }}>{run.phase_id}</Link></td>}
          <td><Status value={run.status} /></td>
          <td>{PURPOSES[run.purpose] ?? run.purpose}</td>
          <td className="numeric">{run.revisions} de {run.revision_limit}</td>
          <td>{when(run.updated_at)}</td>
        </tr>;
      })}</tbody>
    </table>
  </div>;
}

/**
 * Enqueue a task. By default it is chosen from the live NEXT_STEPS and the contract is its literal section, with
 * its hash so the server rejects a changed document (P009-T020); manual mode is for what is not in it.
 * The phase or the task can be fixed by the page.
 */
export function TaskForm({ phase, task, title = "Encolar tarea" }: { phase?: string; task?: string; title?: string }) {
  const { project, busy, operate, send } = useWorkspace();
  const preparation = usePoll<S["PreparationRead"]>(`/projects/${project}/preparation`, 2000);
  const preparationRequired = preparation.data?.available && !preparation.data.prepared;
  const sources = usePoll<S["TaskSourcesRead"]>(`/projects/${project}/task-sources`, 5000);
  const items = sources.data?.items ?? [];
  const phases = sourcePhases(items, phase);
  const [manual, setManual] = useState(false);
  const [chosenPhase, setChosenPhase] = useState(phase ?? "");
  const [chosenTask, setChosenTask] = useState(task ?? "");
  const [taskId, setTaskId] = useState(task ?? "");
  const [phaseId, setPhaseId] = useState(phase ?? "");
  const [text, setText] = useState("");
  const [notes, setNotes] = useState("");
  const selectedPhase = chosenPhase || (phases.length === 1 ? phases[0] : "");
  const tasks = sourceTasks(items, selectedPhase, task);
  const source = tasks.find(item => item.task_id === (chosenTask || (task ?? ""))) ?? null;
  const offered = phases.length > 0 && (!task || tasks.length > 0);
  const fromDocuments = !manual && offered;
  const body = runBody(fromDocuments ? source : null, { task: taskId, phase: phaseId, text }, notes);
  const ready = fromDocuments ? source !== null : !!(text.trim() && taskId.trim() && phaseId.trim());
  return <section className="panel" aria-labelledby="task-form">
    <h2 id="task-form">{title}</h2>
    <p className="hint">El planificador fija el contrato con la política del proyecto; el ejecutor trabaja en un worktree y el revisor decide. El commit se confirma aparte.</p>
    {preparationRequired && <p className="state state-attention">Prepara {recipeLabel(preparation.data?.recipe)} desde la creación o el resumen del proyecto antes de encolar tareas.</p>}
    <form onSubmit={e => { e.preventDefault(); if (!busy && !preparationRequired && ready) void operate(() => send(jobRequest(`/projects/${project}/runs`, body))); }}>
      {fromDocuments ? <>
        <div className="form-row">
          <label>Fase<select value={selectedPhase} onChange={e => { setChosenPhase(e.target.value); setChosenTask(""); }} disabled={!!phase} required>
            {!selectedPhase && <option value="">Elige una fase</option>}
            {phases.map(code => <option key={code} value={code}>{code}</option>)}
          </select></label>
          <label>Tarea<select value={source?.task_id ?? ""} onChange={e => setChosenTask(e.target.value)} disabled={!!task} required>
            {!source && <option value="">Elige una tarea</option>}
            {tasks.map(item => <option key={item.task_id} value={item.task_id}>{item.task_id} — {item.title}</option>)}
          </select></label>
        </div>
        {source && <label>Contrato de tarea<textarea value={source.text} readOnly rows={8} /></label>}
        {source && <p className="hint">Sección literal de <code>{sources.data?.path}</code> · SHA-256 <code>{source.sha256.slice(0, 12)}</code>. Si el documento cambia antes de encolar, el servidor lo rechaza.</p>}
      </> : <>
        {(!task || !phase) && <div className="form-row">
          {!task && <label>Tarea<input value={taskId} onChange={e => setTaskId(e.target.value)} required maxLength={120} placeholder={phase ? `${phase}-T001` : "P001-T001"} /></label>}
          {!phase && <label>Fase<input value={phaseId} onChange={e => setPhaseId(e.target.value)} required maxLength={120} placeholder="P001" /></label>}
        </div>}
        <label>Contrato de tarea<textarea value={text} onChange={e => setText(e.target.value)} required maxLength={200000} rows={8} /></label>
      </>}
      {sources.data?.diagnostics.map(item => <p key={item} className="hint">{item}</p>)}
      {offered && <label className="check"><input type="checkbox" checked={manual} onChange={e => setManual(e.target.checked)} />Escribir el contrato a mano</label>}
      {items.length > 0 && !offered && <p className="hint">{task ?? phase} no está en <code>{sources.data?.path}</code>; escribe el contrato a mano.</p>}
      <label>Notas adicionales (opcional)<textarea value={notes} onChange={e => setNotes(e.target.value)} maxLength={4000} rows={3} /></label>
      <p className="hint">Se congelan en el contrato y llegan al planificador, al ejecutor y al revisor. No amplían rutas, comandos ni permisos.</p>
      <button disabled={busy || preparationRequired || !ready}>Encolar tarea</button>
    </form>
  </section>;
}

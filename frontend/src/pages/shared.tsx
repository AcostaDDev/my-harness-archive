import { useState } from "react";
import { jobRequest } from "../managed-api";
import type { S } from "../managed-api";
import { Link } from "../navigation";
import { runRoute } from "../router.ts";
import { Empty, Status, when } from "../ui";
import { useWorkspace } from "../workspace";

const PURPOSES: Record<S["ManagedRunSummaryRead"]["purpose"], string> = {
  task: "Tarea", phase_check: "Comprobación de fase", phase_close: "Cierre de fase", chat: "Chat",
  document_export: "Exportación documental", bootstrap: "Creación del proyecto", bootstrap_discovery: "Propuesta de creación",
  definition: "Definición", phase_planning: "Planificación de fase", project_import: "Importación",
  document_edit: "Edición de documento",
  phase_transition: "Transición de fase",
};

/** Runs como filas enlazadas a su URL canónica; la tarea y la fase enlazan a sus páginas. */
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

/** Encolar una tarea con su contrato. La fase o la tarea pueden venir fijadas por la página. */
export function TaskForm({ phase, task, title = "Encolar tarea" }: { phase?: string; task?: string; title?: string }) {
  const { project, busy, operate, send } = useWorkspace();
  const [taskId, setTaskId] = useState(task ?? "");
  const [phaseId, setPhaseId] = useState(phase ?? "");
  const [text, setText] = useState("");
  return <section className="panel" aria-labelledby="task-form">
    <h2 id="task-form">{title}</h2>
    <p className="hint">El planificador fija el contrato con la política del proyecto; el ejecutor trabaja en un worktree y el revisor decide. El commit se confirma aparte.</p>
    <form onSubmit={e => { e.preventDefault(); if (!busy) void operate(() => send(jobRequest(`/projects/${project}/runs`, { task_id: taskId.trim(), phase_id: phaseId.trim(), text }))); }}>
      {(!task || !phase) && <div className="form-row">
        {!task && <label>Tarea<input value={taskId} onChange={e => setTaskId(e.target.value)} required maxLength={120} placeholder={phase ? `${phase}-T001` : "P001-T001"} /></label>}
        {!phase && <label>Fase<input value={phaseId} onChange={e => setPhaseId(e.target.value)} required maxLength={120} placeholder="P001" /></label>}
      </div>}
      <label>Contrato de tarea<textarea value={text} onChange={e => setText(e.target.value)} required maxLength={200000} rows={8} /></label>
      <button disabled={busy || !text.trim() || !taskId.trim() || !phaseId.trim()}>Encolar tarea</button>
    </form>
  </section>;
}

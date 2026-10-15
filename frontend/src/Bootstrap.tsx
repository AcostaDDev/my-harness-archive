import { useEffect, useRef, useState } from "react";
import { jobRequest, managed } from "./managed-api";
import type { Pending, S } from "./managed-api";

const initial: S["BootstrapInput"] = {
  brief: { problem: "", users: "", minimum_features: "", constraints: "", delivery_goal: "" },
  decisions: { scope: "", architecture: "", out_of_scope: "" },
};
const briefLabels = { problem: "Problema", users: "Usuarios", minimum_features: "Funciones mínimas", constraints: "Restricciones", delivery_goal: "Objetivo de entrega" };
const decisionLabels = { scope: "Alcance aceptado", architecture: "Arquitectura aceptada", out_of_scope: "Fuera de alcance" };

export function Bootstrap({ project, busy, refresh, operate, send }: {
  project: string; busy: boolean; refresh: number;
  operate: (f: () => Promise<unknown>) => Promise<void>; send: (p: Pending) => Promise<unknown>;
}) {
  const [status, setStatus] = useState<S["BootstrapStatusRead"]>();
  const [data, setData] = useState(initial);
  const [preview, setPreview] = useState<S["BootstrapPreviewRead"]>();
  const [confirmed, setConfirmed] = useState(false);
  const [reason, setReason] = useState("");
  const [error, setError] = useState("");
  const generation = useRef(0);
  useEffect(() => {
    let active = true;
    const poll = async () => {
      try {
        const value = await managed<S["BootstrapStatusRead"]>(`/projects/${project}/bootstrap`);
        if (active) { setStatus(value); setError(""); }
      } catch (e) { if (active) setError(e instanceof Error ? e.message : String(e)); }
    };
    void poll(); const timer = setInterval(() => void poll(), 1500);
    return () => { active = false; clearInterval(timer); };
  }, [project, refresh]);
  useEffect(() => { setConfirmed(false); }, [status?.operation?.expected_version]);
  if (!status?.enabled) return error ? <p className="state state-error" role="alert">{error}</p> : null;
  const op = status.operation;
  const discovery = status.discovery;
  const discoveryPending = !!discovery && (!discovery.outcome || discovery.run_status === 'RECOVERY_REQUIRED');
  const input = op?.preview.input ?? data;
  const shown = op ? { ...op.preview, resume_operation_id: op.status === "INTERRUPTED" ? op.id : null, expected_version: op.expected_version } : preview;
  const complete = Object.values(input.brief).every(v => v.trim()) && Object.values(input.decisions).every(v => v.trim());
  function edit(next: S["BootstrapInput"]) {
    generation.current += 1; setData(next); setPreview(undefined); setConfirmed(false);
  }
  return <section className="panel" aria-labelledby="bootstrap-title">
    <h2 id="bootstrap-title">Crear proyecto desde cero</h2>
    <p className="hint">Plantilla documental de primera fase. Define el escenario de entrega antes de implementar la aplicación.</p>
    {error && <p className="state state-error" role="alert">{error}</p>}
    {status.import_required ? <p role="status" className="state state-attention">{status.diagnostic} Abre «Modo gestionado y migración» para revisar la importación.</p> : <>
      <fieldset disabled={busy || !!op}>
        <legend>Brief</legend>
        {(Object.keys(briefLabels) as (keyof typeof briefLabels)[]).map(key => <label key={key}>{briefLabels[key]}
          <textarea rows={2} maxLength={4000} value={input.brief[key]} onChange={e => edit({ ...data, brief: { ...data.brief, [key]: e.target.value } })} /></label>)}
        <p className="legend">Decisiones explícitas</p>
        {(Object.keys(decisionLabels) as (keyof typeof decisionLabels)[]).map(key => <label key={key}>{decisionLabels[key]}
          <textarea rows={2} maxLength={4000} value={input.decisions[key]} onChange={e => edit({ ...data, decisions: { ...data.decisions, [key]: e.target.value } })} /></label>)}
      </fieldset>
      {!op && <>
        <p>Propuesta opcional de solo lectura del revisor{status.discovery_selection.provider ? ` (${status.discovery_selection.provider})` : ""}: {status.discovery_selection.model} / {status.discovery_selection.effort}.</p>
        <button disabled={busy || discoveryPending || !status.discovery_available || !Object.values(input.brief).every(v => v.trim())}
          onClick={() => void operate(() => send(jobRequest(`/projects/${project}/bootstrap/discovery`, { brief: input.brief, confirmed: true })))}>Solicitar propuesta del revisor</button>
        {discovery && <><p role="status">Propuesta: {discovery.outcome ? String(discovery.outcome.status) : discovery.run_status}.</p>
          {discovery.outcome?.reason && <p className="state state-error">{discovery.outcome.reason}</p>}
          {discovery.outcome?.result && <><p>{discovery.outcome.result.summary}</p>
            <h3>Requisitos propuestos</h3><ul>{discovery.outcome.result.requirements.map((v, i) => <li key={i}>{v}</li>)}</ul>
            <h3>Alternativas y costes</h3><ul>{discovery.outcome.result.alternatives.map((v, i) => <li key={i}>{v}</li>)}</ul>
            <h3>Decisiones pendientes</h3><ul>{discovery.outcome.result.pending_decisions.map((v, i) => <li key={i}>{v}</li>)}</ul></>}
          <p>Revisa los requisitos, alternativas y decisiones pendientes. Registra tu decisión en los campos de alcance y arquitectura antes de crear.</p></>}
      </>}
      {!op && <button disabled={busy || discoveryPending || !complete} onClick={() => void operate(async () => {
        const current = generation.current;
        const result = await managed<S["BootstrapPreviewRead"]>(`/projects/${project}/bootstrap/preview`, data);
        if (current === generation.current) { setPreview(result); setConfirmed(false); }
      })}>Previsualizar proyecto</button>}
      {shown && <>
        <p>Plantilla: {shown.template.name} · versión {shown.template.version} · perfil {shown.profile}</p>
        <p>Primera fase: {String(shown.phase.code)} · primera tarea: {String(shown.first_task.task_id)}.</p>
        {shown.documents.map(doc => <details className="evidence" key={doc.path}><summary>{doc.path}</summary><pre>{doc.content}</pre></details>)}
        <details className="evidence"><summary>Primera tarea, perfil, preparación y validación</summary><pre>{JSON.stringify({ task: shown.first_task, policy: shown.policy, preparation: shown.preparation, validations: shown.validations, git: shown.git, author: shown.author }, null, 2)}</pre></details>
        <p>La creación guarda documentos y un commit inicial. La preparación y la primera tarea se ejecutan después por una acción propia.</p>
        {(!op || op.status === "INTERRUPTED") && <>
          <label>Motivo de la decisión<input value={reason} maxLength={2000} onChange={e => setReason(e.target.value)} /></label>
          <label className="check"><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />Acepto el brief, el alcance y la arquitectura, y confirmo estos documentos y la primera fase.</label>
          <button disabled={busy || discoveryPending || !confirmed || !reason.trim() || !shown.ready || !!error} onClick={() => void operate(() => send(jobRequest(`/projects/${project}/bootstrap`, {
            input: shown.input, preview_sha256: shown.preview_sha256, confirmed: true, reason,
            resume_operation_id: op?.id ?? null, expected_version: op ? op.expected_version : null,
          })))}> {op ? "Conciliar bootstrap confirmado" : "Crear proyecto confirmado"}</button>
        </>}
      </>}
      {op && <><p role="status">Bootstrap: {op.status} · ejecución: {op.run_status}.</p>
        {op.run_status === "RECOVERY_REQUIRED" && <p>Comprueba y confirma la parada del escritor en el historial de jobs antes de conciliar.</p>}
        {op.status === "COMPLETED" && <><p>Commit inicial: <code>{String(op.result?.commit)}</code>. Primera tarea: {op.first_task_run?.status ?? "pendiente de ejecución y revisión"}.</p>
          <button disabled={busy || !!error || !!op.first_task_run} onClick={() => void operate(() => send(jobRequest(`/projects/${project}/runs`, {
            task_id: String(op.preview.first_task.task_id), phase_id: String(op.preview.phase.code), text: op.preview.task_text,
          })))}>Encolar primera tarea</button></>}
      </>}
    </>}
  </section>;
}

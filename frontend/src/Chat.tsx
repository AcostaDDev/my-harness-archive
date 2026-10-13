import { useEffect, useState } from "react";
import { managed, jobRequest } from "./managed-api";
import type { Pending, S } from "./managed-api";

type Props = { project: string; busy: boolean; refresh: number; operate: (f: () => Promise<unknown>) => Promise<void>; send: (p: Pending) => Promise<void> };
const lines = (value: string) => value.split("\n").map(item => item.trim()).filter(Boolean);
const message = (e: unknown) => e instanceof Error ? e.message : String(e);
const turnNames: Record<S["ChatTurnRead"]["status"], string> = {
  QUEUED: "En cola o en curso", ANSWERED: "Respondido", FAILED: "Fallido (sin reintento)", UNKNOWN: "Resultado desconocido (sin reintento)", REFUSED: "Rechazado por el modo del checkout",
};
const proposalNames: Record<S["ChatProposalRead"]["status"], string> = { PROPOSED: "Propuesta", ACCEPTED: "Aceptada", DISMISSED: "Descartada" };

function Evidence({ title, value }: { title: string; value: unknown }) {
  return <details><summary>{title}</summary><pre>{value === null ? "No registrado (null)" : JSON.stringify(value, null, 2)}</pre></details>;
}

export function Chat({ project, busy, refresh, operate, send }: Props) {
  const [conversations, setConversations] = useState<S["ChatConversationSummaryRead"][]>([]);
  const [phases, setPhases] = useState<S["PhaseSummaryRead"][]>([]);
  const [selected, setSelected] = useState("");
  const [title, setTitle] = useState("");
  const [phase, setPhase] = useState("");
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try {
        const [c, p] = await Promise.all([managed<S["ChatConversationSummaryRead"][]>(`/projects/${project}/conversations`),
          managed<S["PhaseSummaryRead"][]>(`/projects/${project}/phases`)]);
        if (active) { setConversations(c); setPhases(p); setError(""); }
      } catch (e) { if (active) setError(`Sin actualizar: ${message(e)}`); }
      if (active) timer = setTimeout(() => void poll(), 1500);
    }
    void poll(); return () => { active = false; clearTimeout(timer); };
  }, [project, refresh]);
  return <details open={conversations.length > 0}><summary>Chat contextual</summary>
    <p>Cada mensaje es una invocación nueva de solo lectura con el contexto que se congela al enviarlo: proyecto, fase, documentos y runs seleccionados, más los turnos anteriores. El chat no escribe, no concede permisos ni cambia contratos.</p>
    <p>Una propuesta no ejecuta nada. Solo al confirmarla se crea una tarea normal: el motor la planifica, la ejecuta y la revisa, y su commit se confirma aparte.</p>
    {error && <p role="alert" className="error">{error}</p>}
    <ul className="legacy-list">{conversations.map(c => <li key={c.id}><button className="choice" aria-pressed={selected === c.id} onClick={() => setSelected(c.id)}>
      <strong>{c.title}</strong><small>{c.phase_code ? `Fase ${c.phase_code} · ` : ""}{c.turns} turnos</small></button></li>)}</ul>
    <form onSubmit={e => { e.preventDefault(); void operate(async () => {
      const created = await managed<S["ChatConversationRead"]>(`/projects/${project}/conversations`, { title, phase_id: phase || null } satisfies S["ChatConversationCreate"]);
      setSelected(created.id); setTitle("");
    }); }}>
      <div className="form-row"><label>Nueva conversación<input value={title} maxLength={200} onChange={e => setTitle(e.target.value)} /></label>
        <label>Fase de contexto (opcional)<select value={phase} onChange={e => setPhase(e.target.value)}>
          <option value="">Sin fase</option>{phases.map(p => <option key={p.id} value={p.id}>{p.code} · {p.status}</option>)}</select></label></div>
      <button disabled={busy || !title.trim()}>Crear conversación</button>
    </form>
    {selected && <Conversation key={selected} id={selected} busy={busy} refresh={refresh} operate={operate} send={send} />}
  </details>;
}

function Conversation({ id, busy, refresh, operate, send }: Omit<Props, "project"> & { id: string }) {
  const [conversation, setConversation] = useState<S["ChatConversationRead"]>();
  const [error, setError] = useState("");
  const [text, setText] = useState("");
  const [documents, setDocuments] = useState("");
  const [runIds, setRunIds] = useState("");
  const [tasks, setTasks] = useState<Record<string, string>>({});
  const [phaseIds, setPhaseIds] = useState<Record<string, string>>({});
  const [confirmed, setConfirmed] = useState<Record<string, boolean>>({});
  const [reasons, setReasons] = useState<Record<string, string>>({});
  useEffect(() => {
    let active = true;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try { const c = await managed<S["ChatConversationRead"]>(`/conversations/${id}`); if (active) { setConversation(c); setError(""); } }
      catch (e) { if (active) setError(`Sin actualizar: ${message(e)}`); }
      if (active) timer = setTimeout(() => void poll(), 1500);
    }
    void poll(); return () => { active = false; clearTimeout(timer); };
  }, [id, refresh]);
  // Una confirmación solo vale para la versión y la propuesta exacta que se mostraron.
  useEffect(() => { setConfirmed({}); }, [conversation?.version]);
  if (!conversation) return <p role="status">{error || "Cargando conversación…"}</p>;
  const v = conversation.version;
  const canSend = !busy && !error && conversation.actions.includes("message");
  return <section className="evidence-detail">
    <h3>{conversation.title}</h3><p>{conversation.phase ? `Fase ${conversation.phase.code} (${conversation.phase.status})` : "Sin fase"} · Versión observada: {v}</p>
    {error && <p role="status" className="error">{error}</p>}
    {conversation.turns.map(t => {
      const result = t.result?.result as { answer?: string; references?: string[] } | null | undefined;
      return <div className="entry" key={t.id}><strong>Turno {t.number} · {turnNames[t.status]}</strong>
        <p>{t.message}</p>
        {t.status === "QUEUED" && t.run_status === "RECOVERY_REQUIRED" && <p className="error">El turno se interrumpió: su resultado es desconocido y no se reintenta. Confirma el escritor detenido en el run {t.run_id}.</p>}
        {t.status === "ANSWERED" && result?.answer && <p>{result.answer}</p>}
        {t.status === "ANSWERED" && !!result?.references?.length && <p><small>Referencias: {result.references.join(", ")}</small></p>}
        {t.status !== "ANSWERED" && Array.isArray(t.result?.reasons) && <p className="error">{(t.result!.reasons as string[]).join("; ")}</p>}
        <p><small>Run {t.run_id} · {t.run_status} · contexto <code>{t.context_sha256.slice(0, 12)}</code> · {t.documents.length} documentos · {t.run_ids.length} runs · {t.previous_turns} turnos previos</small></p>
        <Evidence title="Contexto congelado, resultado y comprobación del checkout" value={t} /></div>;
    })}

    <h4>Propuestas</h4>
    {!conversation.proposals.length && <p>Sin propuestas.</p>}
    {conversation.proposals.map(p => {
      const data = p.proposal as { title: string; objective: string; scope: string; acceptance_criteria: string[]; validation: string[]; rationale: string };
      const task = tasks[p.id] ?? `CHAT-T${String(p.number).padStart(3, "0")}`;
      const phaseId = phaseIds[p.id] ?? conversation.phase?.code ?? "";
      return <div className="entry" key={p.id}><strong>{p.number}. {data.title} · {proposalNames[p.status]}</strong>
        <p>{data.objective}</p>
        {data.scope && <p>Alcance: {data.scope}</p>}
        <ul>{data.acceptance_criteria.map(c => <li key={c}>{c}</li>)}</ul>
        {data.validation.length > 0 && <p>Validación: {data.validation.join("; ")}</p>}
        {data.rationale && <p><small>{data.rationale}</small></p>}
        <p><small>Turno {p.turn_number} · propuesta <code>{p.proposal_sha256.slice(0, 12)}</code></small></p>
        {p.run && <p>Tarea {p.run.task_id} (fase {p.run.phase_id}) · run {p.run_id} · {p.run.status}{p.run.commit ? ` · commit ${p.run.commit.slice(0, 12)}` : ""}</p>}
        {p.actions.includes("accept") && <>
          <div className="form-row"><label>Tarea<input value={task} maxLength={120} onChange={e => setTasks({ ...tasks, [p.id]: e.target.value })} /></label>
            <label>Fase<input value={phaseId} maxLength={120} onChange={e => setPhaseIds({ ...phaseIds, [p.id]: e.target.value })} /></label></div>
          <label className="check"><input type="checkbox" checked={!!confirmed[p.id]} onChange={e => setConfirmed({ ...confirmed, [p.id]: e.target.checked })} />Creo una tarea con esta propuesta exacta ({p.proposal_sha256.slice(0, 12)}). El planificador fija su contrato con la política del proyecto; la revisión y el commit siguen el flujo normal.</label>
          <button disabled={busy || !!error || !confirmed[p.id] || !task.trim() || !phaseId.trim()} onClick={() => void operate(() => send(jobRequest(`/conversations/${id}/proposals/${p.id}/accept`, {
            expected_version: v, proposal_sha256: p.proposal_sha256, task_id: task.trim(), phase_id: phaseId.trim(), confirmed: true,
          })))}>Crear tarea vinculada</button></>}
        {p.actions.includes("dismiss") && <div className="form-row"><label>Motivo del descarte<input value={reasons[p.id] ?? ""} maxLength={2000} onChange={e => setReasons({ ...reasons, [p.id]: e.target.value })} /></label>
          <button disabled={busy || !!error || !(reasons[p.id] ?? "").trim()} onClick={() => void operate(async () => {
            await managed(`/conversations/${id}/proposals/${p.id}/dismiss`, { expected_version: v, reason: reasons[p.id] } satisfies S["ChatProposalDismissCreate"]);
          })}>Descartar</button></div>}
        <Evidence title="Propuesta y decisión" value={p} /></div>;
    })}

    <h4>Nuevo mensaje</h4>
    {!conversation.actions.includes("message") && <p>El turno anterior sigue pendiente; espera su resultado.</p>}
    <form onSubmit={e => { e.preventDefault(); if (canSend && text.trim()) void operate(async () => {
      await send(jobRequest(`/conversations/${id}/messages`, { expected_version: v, text, documents: lines(documents).length ? lines(documents) : null, run_ids: lines(runIds) }));
      setText("");
    }); }}>
      <label>Mensaje<textarea rows={4} value={text} maxLength={20000} onChange={e => setText(e.target.value)} /></label>
      <div className="form-row"><label>Documentos de contexto (uno por línea; vacío: los de la fase o STATE y NEXT_STEPS)<textarea rows={2} value={documents} onChange={e => setDocuments(e.target.value)} /></label>
        <label>Runs de evidencia (un id por línea)<textarea rows={2} value={runIds} onChange={e => setRunIds(e.target.value)} /></label></div>
      <button disabled={!canSend || !text.trim()}>Enviar mensaje</button>
    </form>
  </section>;
}

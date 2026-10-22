import { useEffect, useState } from "react";
import { createOnce, managed, jobRequest, ManagedError } from "./managed-api";
import type { S } from "./managed-api";
import { Link, navigate } from "./navigation";
import { Empty, Evidence, Loading, PageHeader, Stale, Status, message, usePoll } from "./ui";
import { useWorkspace } from "./workspace";
import { ChatCommand } from "./ChatCommand";
import { commandNames, isCommand } from "./chat-commands";

const lines = (value: string) => value.split("\n").map(item => item.trim()).filter(Boolean);
const turnNames: Record<S["ChatTurnRead"]["status"], string> = {
  QUEUED: "En cola o en curso", ANSWERED: "Respondido", FAILED: "Fallido (sin reintento)", UNKNOWN: "Resultado desconocido (sin reintento)", REFUSED: "Rechazado por el modo del checkout",
};
const proposalNames: Record<S["ChatProposalRead"]["status"], string> = { PROPOSED: "Propuesta", ACCEPTED: "Aceptada", DISMISSED: "Descartada" };

/** Contextual chat (D035) with the conversation selected in the URL. */
export function Chat({ conversation }: { conversation?: string }) {
  const { project, busy, refresh, operate } = useWorkspace();
  const conversations = usePoll<S["ChatConversationSummaryRead"][]>(`/projects/${project}/conversations`, 3000, refresh);
  const phases = usePoll<S["PhaseSummaryRead"][]>(`/projects/${project}/phases`, 10000, refresh);
  const [title, setTitle] = useState("");
  const [phase, setPhase] = useState("");
  const [taskRun, setTaskRun] = useState("");
  const [runOffset, setRunOffset] = useState(0);
  const runs = usePoll<S["Page_ManagedRunSummaryRead_"]>(`/projects/${project}/runs?offset=${runOffset}&limit=20`, 5000, refresh);
  return <>
    <PageHeader title="Chat">
      <p>Las preguntas consultan una instantánea de HEAD en solo lectura, sin esperar al ejecutor. No incluyen cambios locales sin commit. Cada pregunta es un turno nuevo del revisor. El chat no escribe, no concede permisos ni cambia contratos. Una propuesta solo crea una tarea cuando la confirmas.</p>
    </PageHeader>
    <Stale error={conversations.data ? conversations.error : undefined} />
    <div className="split">
      <nav className="panel split-list" aria-label="Conversaciones">
        <h2>Conversaciones</h2>
        {!conversations.data ? <Loading /> : !conversations.data.length ? <p className="hint">Aún no hay conversaciones.</p>
          : <ul className="link-list">{conversations.data.map(c => <li key={c.id}>
            <Link to={{ name: "chat", project, conversation: c.id }} current={conversation === c.id}>
              <span className="link-title">{c.title}</span>
              <span className="link-meta">{c.phase_code ? <>Fase <code>{c.phase_code}</code>, </> : ""}{c.turns} turnos</span>
            </Link></li>)}</ul>}
        <form onSubmit={e => { e.preventDefault(); void operate(async () => {
          const created = await createOnce<S["ChatConversationRead"]>(`/projects/${project}/conversations`, { title, phase_id: phase || null, task_run_id: taskRun || null } satisfies S["ChatConversationCreate"]);
          setTitle(""); navigate({ name: "chat", project, conversation: created.id });
        }); }}>
          <label>Nueva conversación<input value={title} maxLength={200} onChange={e => setTitle(e.target.value)} /></label>
          <label>Fase de contexto (opcional)<select value={phase} onChange={e => setPhase(e.target.value)}>
            <option value="">Sin fase</option>{phases.data?.map(p => <option key={p.id} value={p.id}>{p.code}</option>)}</select></label>
          <label>Tarea de contexto (opcional, run observado)<select value={taskRun} onChange={e => setTaskRun(e.target.value)}>
            <option value="">Sin tarea</option>{runs.data?.items.filter(r => r.purpose === "task").map(r => <option key={r.id} value={r.id}>{r.task_id} · {r.id.slice(0, 8)}</option>)}</select></label>
          <div className="actions"><button type="button" className="button-quiet" disabled={!runOffset} onClick={() => { setRunOffset(Math.max(0, runOffset - 20)); setTaskRun(""); }}>Tareas anteriores</button>
            <button type="button" className="button-quiet" disabled={runs.data?.next_offset == null} onClick={() => { setRunOffset(runs.data!.next_offset!); setTaskRun(""); }}>Más tareas</button></div>
          <button className="button-quiet" disabled={busy || !title.trim()}>Crear conversación</button>
        </form>
      </nav>
      <div className="split-main">
        {conversation ? <Conversation key={conversation} id={conversation} />
          : <Empty title="Elige una conversación"><p>O crea una nueva con una fase o tarea como contexto por defecto.</p></Empty>}
      </div>
    </div>
  </>;
}

function Conversation({ id }: { id: string }) {
  const { project, busy, refresh, operate, send } = useWorkspace();
  const [missing, setMissing] = useState(false);
  const [conversation, setConversation] = useState<S["ChatConversationRead"]>();
  const [error, setError] = useState("");
  const [text, setText] = useState("");
  const [command, setCommand] = useState<S["ChatCommandRead"]>();
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
      try { const c = await managed<S["ChatConversationRead"]>(`/conversations/${encodeURIComponent(id)}`); if (active) {
        if (c.project_id !== project) { setConversation(undefined); setMissing(true); setError("La conversación pertenece a otro proyecto."); }
        else { setConversation(c); setMissing(false); setError(""); }
      } }
      catch (e) { if (active) { setError(message(e)); setMissing(e instanceof ManagedError && e.status === 404); } }
      if (active) timer = setTimeout(() => void poll(), 1500);
    }
    void poll(); return () => { active = false; clearTimeout(timer); };
  }, [id, project, refresh]);
  // A confirmation is only valid for the version and the exact proposal that were shown.
  useEffect(() => { setConfirmed({}); }, [conversation?.version]);
  if (!conversation) return missing ? <Empty title="No existe esa conversación"><p>Elige otra de la lista.</p></Empty>
    : error ? <p role="alert" className="state state-error">{error}</p> : <Loading>Cargando conversación…</Loading>;
  const v = conversation.version;
  const canSend = !busy && !error && (isCommand(text) || conversation.actions.includes("message"));
  return <section className="panel" aria-labelledby="conversation-title">
    <h2 id="conversation-title">{conversation.title}</h2>
    <p className="hint">{conversation.phase ? <>Contexto: fase <Link className="mono" to={{ name: "phase", project, phase: conversation.phase.code }}>{conversation.phase.code}</Link> <Status kind="phase" value={conversation.phase.status} /></> : "Sin fase de contexto"}. Versión observada {v}.</p>
    {conversation.task_run_id && <p className="hint">Tarea de contexto: <Link to={{ name: "run-short", run: conversation.task_run_id }}>run {conversation.task_run_id.slice(0, 8)}</Link>. Su evidencia se añade a cada turno.</p>}
    <Stale error={error} />
    {conversation.turns.map(t => {
      const result = t.result?.result as { answer?: string; references?: string[] } | null | undefined;
      return <div className="entry turn" key={t.id}><p className="turn-head"><strong>Turno {t.number}</strong> {turnNames[t.status]}</p>
        <p className="turn-message">{t.message}</p>
        <p className="hint">{t.command ? "Comando determinista · sin agente" : t.head ? <>Instantánea de HEAD <code className="hash">{t.head.slice(0, 12)}</code> · sin cambios locales</> : "Turno anterior al chat sobre instantáneas"}</p>
        {t.status === "QUEUED" && t.run_status === "RECOVERY_REQUIRED" && <p className="state state-attention">El turno se interrumpió: su resultado es desconocido y no se reintenta. Confirma el escritor detenido en el <Link to={{ name: "run-short", run: t.run_id }}>run {t.run_id.slice(0, 8)}</Link>.</p>}
        {t.status === "ANSWERED" && result?.answer && <p className="turn-answer">{result.answer}</p>}
        {t.status === "ANSWERED" && !!result?.references?.length && <p className="hint">Referencias: {result.references.map(r => <code key={r} className="chip">{r}</code>)}</p>}
        {t.status !== "ANSWERED" && Array.isArray(t.result?.reasons) && <p className="state state-error">{(t.result!.reasons as string[]).join("; ")}</p>}
        <p className="hint"><Link to={{ name: "run-short", run: t.run_id }}>Run {t.run_id.slice(0, 8)}</Link> <Status value={t.run_status} />, contexto <code className="hash">{t.context_sha256.slice(0, 12)}</code> con {t.documents.length} documentos, {t.run_ids.length} runs y {t.previous_turns} turnos previos.</p>
        <Evidence title="Contexto congelado, resultado y comprobación del checkout" value={t} /></div>;
    })}

    <h3>Propuestas</h3>
    {!conversation.proposals.length && <p className="hint">Sin propuestas.</p>}
    {conversation.proposals.map(p => {
      const data = p.proposal as { title: string; objective: string; scope: string; acceptance_criteria: string[]; validation: string[]; rationale: string };
      const task = tasks[p.id] ?? `CHAT-T${String(p.number).padStart(3, "0")}`;
      const phaseId = phaseIds[p.id] ?? conversation.phase?.code ?? "";
      return <div className={p.actions.includes("accept") ? "entry entry-open" : "entry"} key={p.id}><p><strong>{p.number}. {data.title}</strong> {proposalNames[p.status]}</p>
        <p>{data.objective}</p>
        {data.scope && <p>Alcance: {data.scope}</p>}
        <ul>{data.acceptance_criteria.map(c => <li key={c}>{c}</li>)}</ul>
        {data.validation.length > 0 && <p>Validación: {data.validation.join("; ")}</p>}
        {data.rationale && <p className="hint">{data.rationale}</p>}
        <p className="hint">Turno {p.turn_number}, propuesta <code className="hash">{p.proposal_sha256.slice(0, 12)}</code></p>
        {p.run && <p>Tarea <Link className="mono" to={{ name: "task", project, phase: p.run.phase_id, task: p.run.task_id }}>{p.run.task_id}</Link> en {p.run_id ? <Link to={{ name: "run-short", run: p.run_id }}>su run</Link> : "su run"} <Status value={p.run.status} />{p.run.commit ? <> con commit <code className="hash">{p.run.commit.slice(0, 12)}</code></> : null}</p>}
        {p.actions.includes("accept") && <>
          <div className="form-row"><label>Tarea<input value={task} maxLength={120} onChange={e => { setTasks({ ...tasks, [p.id]: e.target.value }); setConfirmed({ ...confirmed, [p.id]: false }); }} /></label>
            <label>Fase<input value={phaseId} maxLength={120} onChange={e => { setPhaseIds({ ...phaseIds, [p.id]: e.target.value }); setConfirmed({ ...confirmed, [p.id]: false }); }} /></label></div>
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

    <h3>Mensaje o comando</h3>
    <p className="hint">Los comandos abren los mismos controles que los botones de fase. /check inicia la comprobación normal al pulsar su botón; esa comprobación puede usar el revisor. /tarea crea una propuesta sin agente.</p>
    <div className="command-list" aria-label="Comandos disponibles">{commandNames.map(name => <button type="button" key={name} className="button-quiet mono" onClick={() => { setText(`/${name}${name === "tarea" ? " " : ""}`); setCommand(undefined); }}>/{name}</button>)}</div>
    {!conversation.actions.includes("message") && <p>El turno anterior sigue pendiente; espera su resultado.</p>}
    <form onSubmit={e => { e.preventDefault(); if (canSend && text.trim()) void operate(async () => {
      if (isCommand(text)) {
        const preview = await managed<S["ChatCommandRead"]>(`/conversations/${id}/commands/preview`, { expected_version: v, text } satisfies S["ChatCommandCreate"]);
        if (preview.name !== "tarea") { setCommand(preview); setText(""); return; }
      }
      await send(jobRequest(`/conversations/${id}/messages`, { expected_version: v, text, documents: lines(documents).length ? lines(documents) : null, run_ids: lines(runIds) }));
      setText(""); setCommand(undefined);
    }); }}>
      <label>Mensaje<textarea rows={4} value={text} maxLength={20000} onChange={e => { setText(e.target.value); setCommand(undefined); }} /></label>
      <div className="form-row"><label>Documentos de contexto (uno por línea; vacío: los de la fase o STATE y NEXT_STEPS)<textarea rows={2} value={documents} onChange={e => setDocuments(e.target.value)} /></label>
        <label>Runs de evidencia (un id por línea)<textarea rows={2} value={runIds} onChange={e => setRunIds(e.target.value)} /></label></div>
      <button disabled={!canSend || !text.trim()}>{isCommand(text) ? "Preparar comando" : "Enviar pregunta"}</button>
    </form>
    {command && <section className="decision chat-command" aria-label={`Resultado de /${command.name}`}>
      <div className="actions"><h3 className="mono">/{command.name}</h3><button type="button" className="button-quiet" onClick={() => setCommand(undefined)}>Cerrar comando</button></div>
      <p className="hint">Comando reconocido sin modelo. Revisa los datos y confirma la acción en su control; recargar descarta este panel.</p>
      <ChatCommand key={command.preview_sha256} command={command} />
    </section>}
  </section>;
}

import { useEffect, useState } from "react";
import { managed, jobRequest } from "./managed-api";
import type { Pending, S } from "./managed-api";

type Props = { project: string; busy: boolean; refresh: number; operate: (f: () => Promise<unknown>) => Promise<void>; send: (p: Pending) => Promise<void> };
const lines = (value: string) => value.split("\n").map(item => item.trim()).filter(Boolean);
const message = (e: unknown) => e instanceof Error ? e.message : String(e);
const statusNames: Record<S["PhaseRead"]["status"], string> = {
  ACTIVE: "Activa", CHECKING: "Comprobando", READY_TO_CLOSE: "Lista para cerrar", NEEDS_RECONCILIATION: "Necesita reconciliación",
  BLOCKED: "Bloqueada por decisiones", CLOSING: "Cerrando", CLOSED: "Cerrada", ABANDONED: "Abandonada",
};
const tagNames = { lightweight: "ligero", annotated: "anotado (mensaje, identidad y fecha fijados en la intención)" };

function Evidence({ title, value }: { title: string; value: unknown }) {
  return <details><summary>{title}</summary><pre>{value === null ? "No registrado (null)" : JSON.stringify(value, null, 2)}</pre></details>;
}

export function Phases({ project, busy, refresh, operate, send }: Props) {
  const [phases, setPhases] = useState<S["PhaseSummaryRead"][]>([]);
  const [selected, setSelected] = useState("");
  const [error, setError] = useState("");
  const [code, setCode] = useState("");
  const [objective, setObjective] = useState("");
  const [criteria, setCriteria] = useState("");
  const [tasks, setTasks] = useState("");
  const [documents, setDocuments] = useState("");
  const [tag, setTag] = useState("");
  useEffect(() => {
    let active = true;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try { const p = await managed<S["PhaseSummaryRead"][]>(`/projects/${project}/phases`); if (active) { setPhases(p); setError(""); } }
      catch (e) { if (active) setError(`Sin actualizar: ${message(e)}`); }
      if (active) timer = setTimeout(() => void poll(), 1500);
    }
    void poll(); return () => { active = false; clearTimeout(timer); };
  }, [project, refresh]);
  return <details open={phases.length > 0}><summary>Fases y cierre</summary>
    <p>Una fase agrupa tareas aceptadas. Comprobarla no la cierra; cerrarla exige una autorización propia sobre la evidencia READY mostrada. La ejecución por lote se autoriza aparte y nunca comprueba ni cierra la fase.</p>
    <p>Una fase abandonada o cerrada libera el checkout para definir otra.</p>
    {error && <p role="alert" className="error">{error}</p>}
    <ul className="legacy-list">{phases.map(p => <li key={p.id}><button className="choice" aria-pressed={selected === p.id} onClick={() => setSelected(p.id)}>
      <strong>{p.code} · {statusNames[p.status]}</strong><small>{p.objective}</small></button></li>)}</ul>
    <details><summary>Definir fase</summary>
      <p>La definición queda congelada: código, criterios de salida, tareas y documentos de referencia. El tag es opcional y se crea solo al cerrar.</p>
      <form onSubmit={e => { e.preventDefault(); void operate(async () => {
        const created = await managed<S["PhaseRead"]>(`/projects/${project}/phases`, {
          code, objective, exit_criteria: lines(criteria), tasks: lines(tasks),
          documents: lines(documents).length ? lines(documents) : null, tag: tag.trim() || null,
        } satisfies S["PhaseCreate"]);
        setSelected(created.id);
      }); }}>
        <div className="form-row"><label>Código<input required value={code} maxLength={120} onChange={e => setCode(e.target.value)} /></label>
          <label>Tag al cerrar (opcional)<input value={tag} maxLength={100} onChange={e => setTag(e.target.value)} /></label></div>
        <label>Objetivo<input required value={objective} maxLength={4000} onChange={e => setObjective(e.target.value)} /></label>
        <label>Criterios de salida (uno por línea)<textarea required rows={3} value={criteria} onChange={e => setCriteria(e.target.value)} /></label>
        <label>Tareas que deben estar aceptadas (una por línea)<textarea rows={3} value={tasks} onChange={e => setTasks(e.target.value)} /></label>
        <label>Documentos de referencia (uno por línea; vacío: STATE y NEXT_STEPS)<textarea rows={2} value={documents} onChange={e => setDocuments(e.target.value)} /></label>
        <button disabled={busy || !code.trim() || !objective.trim() || !lines(criteria).length}>Crear fase</button>
      </form>
    </details>
    {selected && <Phase key={selected} id={selected} busy={busy} refresh={refresh} operate={operate} send={send} />}
  </details>;
}

function Phase({ id, busy, refresh, operate, send }: Omit<Props, "project"> & { id: string }) {
  const [phase, setPhase] = useState<S["PhaseRead"]>();
  const [error, setError] = useState("");
  const [reason, setReason] = useState("");
  const [question, setQuestion] = useState("");
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [answerConfirmed, setAnswerConfirmed] = useState(false);
  const [reconcileConfirmed, setReconcileConfirmed] = useState(false);
  const [closeReason, setCloseReason] = useState("");
  const [closeConfirmed, setCloseConfirmed] = useState(false);
  const [batchTasks, setBatchTasks] = useState<string[]>([]);
  const [batchTtl, setBatchTtl] = useState(3600);
  const [batchReason, setBatchReason] = useState("");
  const [batchConfirmed, setBatchConfirmed] = useState(false);
  const [plan, setPlan] = useState("");
  const [chainCommits, setChainCommits] = useState(false);
  const [batchPlan, setBatchPlan] = useState("");
  const [amendObjective, setAmendObjective] = useState("");
  const [amendCriteria, setAmendCriteria] = useState("");
  const [amendTasks, setAmendTasks] = useState("");
  const [amendDocuments, setAmendDocuments] = useState("");
  const [amendTag, setAmendTag] = useState("");
  const [amendReason, setAmendReason] = useState("");
  const [amendConfirmed, setAmendConfirmed] = useState(false);
  const [abandonReason, setAbandonReason] = useState("");
  const [abandonConfirmed, setAbandonConfirmed] = useState(false);
  useEffect(() => {
    let active = true;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try { const p = await managed<S["PhaseRead"]>(`/phases/${id}`); if (active) { setPhase(p); setError(""); } }
      catch (e) { if (active) setError(`Sin actualizar: ${message(e)}`); }
      if (active) timer = setTimeout(() => void poll(), 1500);
    }
    void poll(); return () => { active = false; clearTimeout(timer); };
  }, [id, refresh]);
  // Las confirmaciones solo valen para la versión y la evidencia que se mostraron.
  useEffect(() => { setAnswerConfirmed(false); setReconcileConfirmed(false); setCloseConfirmed(false); setBatchConfirmed(false); setAmendConfirmed(false); setAbandonConfirmed(false); },
    [phase?.version, phase?.ready?.binding_sha256, phase?.documents.current_sha256]);
  // El formulario de enmienda parte de la definición vigente; cambia solo al cambiar de versión de definición.
  useEffect(() => {
    if (!phase) return;
    const d = phase.definition;
    setAmendObjective(String(d.objective)); setAmendCriteria((d.exit_criteria as string[]).join("\n"));
    setAmendTasks((d.tasks as string[]).join("\n")); setAmendDocuments((d.documents as string[]).join("\n"));
    setAmendTag(d.tag ? String(d.tag) : "");
  }, [phase?.definition_sha256]);
  if (!phase) return <p role="status">{error || "Cargando fase…"}</p>;
  const can = (action: S["PhaseRead"]["actions"][number]) => !busy && !error && phase.actions.includes(action);
  const v = phase.version;
  const open = phase.questions.filter(q => q.status === "OPEN");
  const batch = phase.authorizations.find(a => a.kind === "batch" && a.effective_status === "ACTIVE");
  return <section className="evidence-detail">
    <h3>{phase.code} · {statusNames[phase.status]}</h3><p>{phase.definition.objective as string} · Versión observada: {v} · Definición v{phase.definition_number}</p>
    {error && <p role="status" className="error">{error}</p>}
    <Evidence title="Definición congelada y commits de tareas aceptadas" value={{ definition: phase.definition, tasks: phase.tasks }} />
    <Evidence title={`Versiones de la definición (${phase.definitions.length})`} value={phase.definitions} />

    <h4>Documentos</h4>
    {phase.documents.drift === null ? <p className="error">No se pudieron leer los documentos actuales.</p>
      : phase.documents.drift.length ? <p className="error">Cambiados desde la base adoptada: {phase.documents.drift.join(", ")}</p>
        : <p>Sin cambios respecto a la base adoptada.</p>}
    <Evidence title="Hashes adoptados y actuales" value={phase.documents} />
    <label>Motivo de la reconciliación<input value={reason} maxLength={2000} onChange={e => setReason(e.target.value)} /></label>
    <label className="check"><input type="checkbox" checked={reconcileConfirmed} onChange={e => setReconcileConfirmed(e.target.checked)} />He revisado estos documentos y adopto su contenido actual como base de la fase.</label>
    <div className="pagination"><button disabled={!can("reconcile") || !reconcileConfirmed || !reason.trim() || !phase.documents.current_sha256} onClick={() => void operate(async () => {
      await managed(`/phases/${id}/reconcile`, { expected_version: v, documents_sha256: phase.documents.current_sha256!, reason, confirmed: true } satisfies S["PhaseReconcileCreate"]);
    })}>Adoptar documentos actuales</button>
      <button disabled={!can("reconcile_task")} onClick={() => void operate(() => send(jobRequest(`/phases/${id}/reconcile-task`, { expected_version: v })))}>Reconciliar con agente</button></div>
    <p>Reconciliar con agente crea una tarea normal con contrato determinista (plantilla reconcile-phase) limitada a estos documentos: se ejecuta, se revisa y su commit se confirma en la sección de runs. Después adopta aquí los documentos por hash.</p>

    <h4>Preguntas bloqueantes ({open.length} pendientes)</h4>
    {phase.questions.map(q => <div className="entry" key={q.id}><strong>{q.status === "OPEN" ? "Pendiente" : "Respondida"} · {q.text}</strong>
      {q.answer && <p>Respuesta: {String(q.answer.text)}</p>}
      {q.status === "OPEN" && <><label>Respuesta<input value={answers[q.id] ?? ""} maxLength={4000} onChange={e => setAnswers({ ...answers, [q.id]: e.target.value })} /></label>
        <button disabled={busy || !!error || !answerConfirmed || !(answers[q.id] ?? "").trim()} onClick={() => void operate(async () => {
          await managed(`/phases/${id}/questions/${q.id}/answer`, { expected_version: v, expected_question_version: q.version, answer: answers[q.id], confirmed: true } satisfies S["PhaseAnswerCreate"]);
        })}>Responder</button></>}
      <Evidence title="Origen y auditoría" value={q} /></div>)}
    {open.length > 0 && <label className="check"><input type="checkbox" checked={answerConfirmed} onChange={e => setAnswerConfirmed(e.target.checked)} />La respuesta es una decisión de producto registrada con mi identidad local.</label>}
    <form onSubmit={e => { e.preventDefault(); void operate(async () => {
      await managed(`/phases/${id}/questions`, { expected_version: v, text: question } satisfies S["PhaseQuestionCreate"]); setQuestion("");
    }); }}><div className="form-row"><label>Nueva pregunta bloqueante<input value={question} maxLength={4000} onChange={e => setQuestion(e.target.value)} /></label>
      <button disabled={!can("question") || !question.trim()}>Registrar pregunta</button></div></form>

    <h4>Comprobación</h4>
    <p>Las puertas deterministas (preguntas, documentos, árbol limpio, tareas alcanzables y validación base) se evalúan antes de la evaluación del agente.</p>
    <button disabled={!can("check")} onClick={() => void operate(() => send(jobRequest(`/phases/${id}/actions`, { action: "check", expected_version: v })))}>Comprobar fase</button>
    {phase.ready ? <><p>READY sobre <code>{String(phase.ready.binding.head)}</code> · evidencia <code>{phase.ready.binding_sha256}</code></p>
      {phase.ready.stale_reasons.length > 0 && <p className="error">READY obsoleto: {phase.ready.stale_reasons.join("; ")}. Comprueba de nuevo.</p>}
      <Evidence title="Evidencia READY vinculada" value={phase.ready} /></> : <p>Sin READY vigente.</p>}

    <div className="entry"><h4>Cierre de fase</h4>
      <p>Autoriza solo este cierre: vuelve a observar el contenido y, si coincide con READY, registra CLOSED{phase.definition.tag ? ` y crea el tag ${tagNames[phase.tag_kind ?? "lightweight"]} ${String(phase.definition.tag)} sin moverlo nunca` : ""}. No edita documentos ni integra ramas.</p>
      <label>Motivo de la autorización de cierre<input value={closeReason} maxLength={2000} onChange={e => setCloseReason(e.target.value)} /></label>
      <label className="check"><input type="checkbox" checked={closeConfirmed} onChange={e => setCloseConfirmed(e.target.checked)} />Autorizo cerrar la fase sobre la evidencia READY {phase.ready?.binding_sha256.slice(0, 12) ?? ""}.</label>
      <button disabled={!can("close") || !closeConfirmed || !closeReason.trim() || !phase.ready} onClick={() => void operate(() => send(jobRequest(`/phases/${id}/actions`, {
        action: "close", expected_version: v, binding_sha256: phase.ready!.binding_sha256, reason: closeReason, ttl_seconds: 3600, confirmed: true,
      })))}>Cerrar fase</button></div>

    <div className="entry"><h4>Ejecución por lote</h4>
      <p>Manual: encola las tareas seleccionadas de una en una cuando lo pides, sin confirmar commits. Desatendido: el supervisor encadena tarea → aceptación → commit de contenido exacto → siguiente tarea y se detiene en el primer bloqueo, pregunta, caducidad, revocación o evidencia invalidada. Ninguno comprueba ni cierra la fase.</p>
      {batch ? <>{batch.scope.chain_commits ? <p>Lote desatendido activo (encadena y confirma commits): {(batch.scope.tasks as string[]).join(", ")} · plan <code>{String(batch.scope.plan_sha256).slice(0, 12)}</code> · caduca {batch.expires_at}</p>
          : <><p>Lote manual activo: {(batch.scope.tasks as string[]).join(", ")} · caduca {batch.expires_at}</p>
            <label>Contrato de la siguiente tarea<textarea rows={6} value={plan} maxLength={200000} onChange={e => setPlan(e.target.value)} /></label></>}
        <div className="pagination">{!batch.scope.chain_commits && <button disabled={!can("batch_next") || !plan.trim()} onClick={() => void operate(() => send(jobRequest(`/phases/${id}/batch/next`, { expected_version: v, authorization_id: batch.id, text: plan })))}>Encolar siguiente tarea del lote</button>}
          <button disabled={busy || !!error || !batchReason.trim()} onClick={() => void operate(async () => {
            await managed(`/phases/${id}/authorizations/${batch.id}/revoke`, { expected_version: v, reason: batchReason } satisfies S["PhaseRevokeCreate"]);
          })}>Revocar lote</button></div></>
        : <>{(phase.definition.tasks as string[]).map(task => <label className="check" key={task}><input type="checkbox" checked={batchTasks.includes(task)}
          onChange={e => setBatchTasks(e.target.checked ? [...batchTasks, task] : batchTasks.filter(t => t !== task))} />{task}</label>)}
          <label>Vigencia en segundos (máximo 24 horas)<input type="number" min={1} max={86400} value={batchTtl} onChange={e => setBatchTtl(Number(e.target.value))} /></label>
          <label className="check"><input type="checkbox" checked={chainCommits} onChange={e => setChainCommits(e.target.checked)} />Desatendido: encadenar tareas y confirmar el commit de cada aceptación elegible.</label>
          {chainCommits && <label>Plan congelado con las secciones de las tareas<textarea rows={6} value={batchPlan} maxLength={200000} onChange={e => setBatchPlan(e.target.value)} /></label>}</>}
      <label>Motivo del lote o de su revocación<input value={batchReason} maxLength={2000} onChange={e => setBatchReason(e.target.value)} /></label>
      {!batch && <><label className="check"><input type="checkbox" checked={batchConfirmed} onChange={e => setBatchConfirmed(e.target.checked)} />{chainCommits ? "Autorizo ejecutar estas tareas y confirmar sus commits sin intervención; el cierre requerirá otra autorización." : "Autorizo ejecutar estas tareas en lote; el cierre requerirá otra autorización."}</label>
        <button disabled={!can("authorize_batch") || !batchConfirmed || !batchReason.trim() || !batchTasks.length || (chainCommits && !batchPlan.trim())} onClick={() => void operate(async () => {
          await managed(`/phases/${id}/authorizations`, { expected_version: v, tasks: batchTasks, ttl_seconds: batchTtl, reason: batchReason, confirmed: true,
            chain_commits: chainCommits, text: chainCommits ? batchPlan : null } satisfies S["PhaseBatchCreate"]);
          setBatchTasks([]);
        })}>Autorizar lote</button></>}</div>

    <div className="entry"><h4>Enmendar definición</h4>
      <p>Crea la versión {phase.definition_number + 1} de la definición y conserva las anteriores. Invalida el READY vigente y los lotes activos. El código no cambia; los documentos nuevos se adoptan con su hash actual.</p>
      <label>Objetivo<input value={amendObjective} maxLength={4000} onChange={e => setAmendObjective(e.target.value)} /></label>
      <label>Criterios de salida (uno por línea)<textarea rows={3} value={amendCriteria} onChange={e => setAmendCriteria(e.target.value)} /></label>
      <label>Tareas (una por línea)<textarea rows={3} value={amendTasks} onChange={e => setAmendTasks(e.target.value)} /></label>
      <label>Documentos (uno por línea)<textarea rows={2} value={amendDocuments} onChange={e => setAmendDocuments(e.target.value)} /></label>
      <label>Tag al cerrar (opcional)<input value={amendTag} maxLength={100} onChange={e => setAmendTag(e.target.value)} /></label>
      <label>Motivo de la enmienda<input value={amendReason} maxLength={2000} onChange={e => setAmendReason(e.target.value)} /></label>
      <label className="check"><input type="checkbox" checked={amendConfirmed} onChange={e => setAmendConfirmed(e.target.checked)} />Confirmo la nueva definición; el READY y los lotes actuales dejan de valer.</label>
      <button disabled={!can("amend") || !amendConfirmed || !amendReason.trim() || !amendObjective.trim() || !lines(amendCriteria).length || !lines(amendDocuments).length} onClick={() => void operate(async () => {
        await managed(`/phases/${id}/amend`, { expected_version: v, objective: amendObjective, exit_criteria: lines(amendCriteria), tasks: lines(amendTasks),
          documents: lines(amendDocuments), tag: amendTag.trim() || null, reason: amendReason, confirmed: true } satisfies S["PhaseAmendCreate"]);
        setAmendReason("");
      })}>Enmendar definición</button></div>

    <div className="entry"><h4>Abandonar fase</h4>
      <p>Estado terminal y auditado: no edita documentos ni Git, invalida lotes activos y libera el checkout para otra fase.</p>
      <label>Motivo del abandono<input value={abandonReason} maxLength={2000} onChange={e => setAbandonReason(e.target.value)} /></label>
      <label className="check"><input type="checkbox" checked={abandonConfirmed} onChange={e => setAbandonConfirmed(e.target.checked)} />Abandono esta fase de forma definitiva.</label>
      <button disabled={!can("abandon") || !abandonConfirmed || !abandonReason.trim()} onClick={() => void operate(async () => {
        await managed(`/phases/${id}/abandon`, { expected_version: v, reason: abandonReason, confirmed: true } satisfies S["PhaseAbandonCreate"]);
      })}>Abandonar fase</button></div>

    <h4>Historial</h4>
    {phase.operations.map(o => <div className="entry" key={o.id}><strong>{o.kind} · {o.status}</strong>
      {Array.isArray(o.result?.reasons) && (o.result!.reasons as string[]).length > 0 && <p>{(o.result!.reasons as string[]).join("; ")}</p>}
      <Evidence title="Solicitud, resultado y evidencia" value={o} /></div>)}
    <Evidence title="Autorizaciones de lote y de cierre" value={phase.authorizations} />
  </section>;
}

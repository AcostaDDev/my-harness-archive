import { useEffect, useState } from "react";
import { managed, jobRequest } from "./managed-api";
import type { S } from "./managed-api";
import { navigate } from "./navigation";
import { Evidence, Fields, Hash, PHASE } from "./ui";
import { useWorkspace } from "./workspace";

const lines = (value: string) => value.split("\n").map(item => item.trim()).filter(Boolean);
const tagNames = { lightweight: "ligero", annotated: "anotado (mensaje, identidad y fecha fijados en la intención)" };

/** Definición congelada de una fase nueva (H3.3); al crearla se abre su URL. */
export function PhaseCreate() {
  const { project, busy, operate } = useWorkspace();
  const [code, setCode] = useState("");
  const [objective, setObjective] = useState("");
  const [criteria, setCriteria] = useState("");
  const [tasks, setTasks] = useState("");
  const [documents, setDocuments] = useState("");
  const [tag, setTag] = useState("");
  return <section className="panel" aria-labelledby="phase-create">
    <h2 id="phase-create">Definir fase</h2>
    <p className="hint">La definición queda congelada: código, criterios de salida, tareas y documentos de referencia. El tag es opcional y se crea solo al cerrar. Solo puede haber una fase abierta por checkout.</p>
    <form onSubmit={e => { e.preventDefault(); void operate(async () => {
      const created = await managed<S["PhaseRead"]>(`/projects/${project}/phases`, {
        code, objective, exit_criteria: lines(criteria), tasks: lines(tasks),
        documents: lines(documents).length ? lines(documents) : null, tag: tag.trim() || null,
      } satisfies S["PhaseCreate"]);
      navigate({ name: "phase", project, phase: created.code });
    }); }}>
      <div className="form-row"><label>Código<input required value={code} maxLength={120} placeholder="P001" onChange={e => setCode(e.target.value)} /></label>
        <label>Tag al cerrar (opcional)<input value={tag} maxLength={100} onChange={e => setTag(e.target.value)} /></label></div>
      <label>Objetivo<input required value={objective} maxLength={4000} onChange={e => setObjective(e.target.value)} /></label>
      <label>Criterios de salida (uno por línea)<textarea required rows={3} value={criteria} onChange={e => setCriteria(e.target.value)} /></label>
      <label>Tareas que deben estar aceptadas (una por línea)<textarea rows={3} value={tasks} onChange={e => setTasks(e.target.value)} /></label>
      <label>Documentos de referencia (uno por línea; vacío: los del contrato documental o STATE y NEXT_STEPS)<textarea rows={2} value={documents} onChange={e => setDocuments(e.target.value)} /></label>
      <button disabled={busy || !code.trim() || !objective.trim() || !lines(criteria).length}>Crear fase</button>
    </form>
  </section>;
}

/** Operaciones de una fase sobre la lectura que muestra la página; cada confirmación vale para esa versión. */
export function PhaseDetail({ phase, stale, section }: { phase: S["PhaseRead"]; stale: boolean; section?: string }) {
  const { busy, operate, send } = useWorkspace();
  const id = phase.id;
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
  const [exportPreview, setExportPreview] = useState<S["DocumentExportPreviewRead"]>();
  const [exportReason, setExportReason] = useState("");
  const [exportConfirmed, setExportConfirmed] = useState(false);
  // Las confirmaciones solo valen para la versión y la evidencia que se mostraron.
  useEffect(() => { setAnswerConfirmed(false); setReconcileConfirmed(false); setCloseConfirmed(false); setBatchConfirmed(false); setAmendConfirmed(false); setAbandonConfirmed(false); },
    [phase.version, phase.ready?.binding_sha256, phase.documents.current_sha256]);
  useEffect(() => { setExportConfirmed(false); setExportPreview(undefined); }, [phase.version, phase.documents.current_sha256]);
  // El formulario de enmienda parte de la definición vigente; cambia solo al cambiar de versión de definición.
  useEffect(() => {
    const d = phase.definition;
    setAmendObjective(String(d.objective)); setAmendCriteria((d.exit_criteria as string[]).join("\n"));
    setAmendTasks((d.tasks as string[]).join("\n")); setAmendDocuments((d.documents as string[]).join("\n"));
    setAmendTag(d.tag ? String(d.tag) : "");
  }, [phase.definition_sha256]);
  const can = (action: S["PhaseRead"]["actions"][number]) => !busy && !stale && phase.actions.includes(action);
  const v = phase.version;
  const open = phase.questions.filter(q => q.status === "OPEN");
  const batch = phase.authorizations.find(a => a.kind === "batch" && a.effective_status === "ACTIVE");
  const criteria = phase.definition.exit_criteria as string[];
  return <>
    {(!section || section === "phase-definition") && <section className="panel" aria-labelledby="phase-definition">
      <h2 id="phase-definition">Definición</h2>
      <Fields items={[
        ["Versión de la definición", `${phase.definition_number}`],
        ["Versión observada", `${v}`],
        ["Tag al cerrar", phase.definition.tag ? <code>{String(phase.definition.tag)}</code> : <span className="muted">sin tag</span>],
        ["Documentos", (phase.definition.documents as string[]).map(d => <code key={d} className="chip">{d}</code>)],
      ]} />
      <h3>Criterios de salida</h3>
      <ul className="checklist">{criteria.map(c => <li key={c}>{c}</li>)}</ul>
      <Evidence title="Definición congelada y commits de tareas aceptadas" value={{ definition: phase.definition, tasks: phase.tasks }} />
      <Evidence title={`Versiones de la definición (${phase.definitions.length})`} value={phase.definitions} />
    </section>}

    {(!section || section === "phase-questions") && <section className="panel" aria-labelledby="phase-questions">
      <h2 id="phase-questions">Preguntas bloqueantes <span className="count">{open.length} pendientes</span></h2>
      {!phase.questions.length && <p className="hint">Sin preguntas registradas.</p>}
      {phase.questions.map(q => <div className={q.status === "OPEN" ? "entry entry-open" : "entry"} key={q.id}>
        <p><strong>{q.status === "OPEN" ? "Pendiente" : "Respondida"}</strong>: {q.text}</p>
        {q.answer && <p>Respuesta: {String(q.answer.text)}</p>}
        {q.status === "OPEN" && <div className="form-row"><label>Respuesta<input value={answers[q.id] ?? ""} maxLength={4000} onChange={e => setAnswers({ ...answers, [q.id]: e.target.value })} /></label>
          <button disabled={busy || stale || !answerConfirmed || !(answers[q.id] ?? "").trim()} onClick={() => void operate(async () => {
            await managed(`/phases/${id}/questions/${q.id}/answer`, { expected_version: v, expected_question_version: q.version, answer: answers[q.id], confirmed: true } satisfies S["PhaseAnswerCreate"]);
          })}>Responder</button></div>}
        <Evidence title="Origen y auditoría" value={q} /></div>)}
      {open.length > 0 && <label className="check"><input type="checkbox" checked={answerConfirmed} onChange={e => setAnswerConfirmed(e.target.checked)} />La respuesta es una decisión de producto registrada con mi identidad local.</label>}
      <form onSubmit={e => { e.preventDefault(); void operate(async () => {
        await managed(`/phases/${id}/questions`, { expected_version: v, text: question } satisfies S["PhaseQuestionCreate"]); setQuestion("");
      }); }}><div className="form-row"><label>Nueva pregunta bloqueante<input value={question} maxLength={4000} onChange={e => setQuestion(e.target.value)} /></label>
        <button className="button-quiet" disabled={!can("question") || !question.trim()}>Registrar pregunta</button></div></form>
    </section>}

    {(!section || section === "phase-documents") && <section className="panel" aria-labelledby="phase-documents">
      <h2 id="phase-documents">Documentos</h2>
      {phase.documents.drift === null ? <p className="state state-error">No se pudieron leer los documentos actuales.</p>
        : phase.documents.drift.length ? <p className="state state-attention">Cambiados desde la base adoptada: {phase.documents.drift.map(d => <code key={d} className="chip">{d}</code>)}</p>
          : <p className="hint">Sin cambios respecto a la base adoptada.</p>}
      <Evidence title="Hashes adoptados y actuales" value={phase.documents} />
      <div className="decision">
        <h3>Adoptar documentos actuales</h3>
        <label>Motivo de la reconciliación<input value={reason} maxLength={2000} onChange={e => setReason(e.target.value)} /></label>
        <label className="check"><input type="checkbox" checked={reconcileConfirmed} onChange={e => setReconcileConfirmed(e.target.checked)} />He revisado estos documentos y adopto su contenido actual como base de la fase.</label>
        <div className="actions"><button disabled={!can("reconcile") || !reconcileConfirmed || !reason.trim() || !phase.documents.current_sha256} onClick={() => void operate(async () => {
          await managed(`/phases/${id}/reconcile`, { expected_version: v, documents_sha256: phase.documents.current_sha256!, reason, confirmed: true } satisfies S["PhaseReconcileCreate"]);
        })}>Adoptar documentos actuales</button>
          <button className="button-quiet" disabled={!can("reconcile_task")} onClick={() => void operate(() => send(jobRequest(`/phases/${id}/reconcile-task`, { expected_version: v })))}>Reconciliar con agente</button></div>
        <p className="hint">Reconciliar con agente crea una tarea normal con contrato determinista (plantilla reconcile-phase) limitada a estos documentos: se ejecuta, se revisa y su commit se confirma en su run. Después adopta aquí los documentos por hash.</p>
      </div>
      <div className="decision">
        <h3>Exportar estado gestionado</h3>
        <p className="hint">Previsualiza los bloques mecánicos de STATE y NEXT_STEPS a partir de SQLite y conserva la prosa exterior. Confirmar crea un commit del diff exacto y adopta los hashes; el cierre de fase es otra acción.</p>
        <button className="button-quiet" disabled={busy || stale} onClick={() => void operate(async () => {
          const preview = await managed<S["DocumentExportPreviewRead"]>(`/phases/${id}/export`);
          setExportConfirmed(false); setExportPreview(preview);
        })}>Previsualizar exportación</button>
        {exportPreview && <>
          <Fields items={[["Base", <Hash value={exportPreview.head} />], ["Contenido", <Hash value={exportPreview.preview_sha256} />]]} />
          {exportPreview.resume_operation_id && <p className="hint">Conciliación de la intención conservada {exportPreview.resume_operation_id}. Reutiliza el mismo commit después de confirmar que el escritor anterior se detuvo.</p>}
          <pre className="diff">{exportPreview.diff || "Los bloques ya coinciden con SQLite."}</pre>
          <label>Motivo de la exportación<input value={exportReason} maxLength={2000} onChange={e => { setExportReason(e.target.value); setExportConfirmed(false); }} /></label>
          <label className="check"><input type="checkbox" checked={exportConfirmed} onChange={e => setExportConfirmed(e.target.checked)} />He revisado este diff y confirmo su commit y la adopción de estos documentos.</label>
          <button disabled={busy || stale || !exportConfirmed || !exportReason.trim() || !exportPreview.mechanical.length || exportPreview.expected_version !== v}
            onClick={() => void operate(() => send(jobRequest(`/phases/${id}/export`, {
              expected_version: exportPreview.expected_version, preview_sha256: exportPreview.preview_sha256,
              resume_operation_id: exportPreview.resume_operation_id, reason: exportReason, confirmed: true,
            } satisfies S["DocumentExportCreate"])))}>Confirmar exportación y commit</button>
        </>}
      </div>
    </section>}

    {(!section || section === "phase-check") && <section className="panel" aria-labelledby="phase-check">
      <h2 id="phase-check">Comprobación y cierre</h2>
      <p className="hint">Las puertas deterministas (preguntas, documentos, árbol limpio, tareas alcanzables y validación base) se evalúan antes de la evaluación del agente. Comprobar no cierra la fase.</p>
      <button disabled={!can("check")} onClick={() => void operate(() => send(jobRequest(`/phases/${id}/actions`, { action: "check", expected_version: v })))}>Comprobar fase</button>
      {phase.ready ? <>
        <Fields items={[["READY sobre", <Hash value={String(phase.ready.binding.head)} />], ["Evidencia", <Hash value={phase.ready.binding_sha256} />]]} />
        {phase.ready.stale_reasons.length > 0 && <p className="state state-attention">READY obsoleto: {phase.ready.stale_reasons.join("; ")}. Comprueba de nuevo.</p>}
        <Evidence title="Evidencia READY vinculada" value={phase.ready} /></> : <p className="hint">Sin READY vigente.</p>}
      <div className="decision">
        <h3>Cerrar fase</h3>
        <p className="hint">Autoriza solo este cierre: vuelve a observar el contenido y, si coincide con READY, registra la fase como {PHASE.CLOSED[0].toLowerCase()}{phase.definition.tag ? ` y crea el tag ${tagNames[phase.tag_kind ?? "lightweight"]} ${String(phase.definition.tag)} sin moverlo nunca` : ""}. No edita documentos ni integra ramas.</p>
        <label>Motivo de la autorización de cierre<input value={closeReason} maxLength={2000} onChange={e => setCloseReason(e.target.value)} /></label>
        <label className="check"><input type="checkbox" checked={closeConfirmed} onChange={e => setCloseConfirmed(e.target.checked)} />Autorizo cerrar la fase sobre la evidencia READY {phase.ready?.binding_sha256.slice(0, 12) ?? ""}.</label>
        <button disabled={!can("close") || !closeConfirmed || !closeReason.trim() || !phase.ready} onClick={() => void operate(() => send(jobRequest(`/phases/${id}/actions`, {
          action: "close", expected_version: v, binding_sha256: phase.ready!.binding_sha256, reason: closeReason, ttl_seconds: 3600, confirmed: true,
        })))}>Cerrar fase</button>
      </div>
    </section>}

    {(!section || section === "phase-batch") && <section className="panel" aria-labelledby="phase-batch">
      <h2 id="phase-batch">Ejecución por lote</h2>
      <p className="hint">Manual: encola las tareas seleccionadas de una en una cuando lo pides, sin confirmar commits. Desatendido: el supervisor encadena tarea, aceptación, commit del contenido exacto y siguiente tarea, y se detiene en el primer bloqueo, pregunta, caducidad, revocación o evidencia invalidada. Ninguno comprueba ni cierra la fase.</p>
      <div className="decision">
        {batch ? <>{batch.scope.chain_commits ? <p>Lote desatendido activo (encadena y confirma commits): {(batch.scope.tasks as string[]).map(t => <code key={t} className="chip">{t}</code>)} plan <Hash value={String(batch.scope.plan_sha256)} />, caduca {batch.expires_at}</p>
            : <><p>Lote manual activo: {(batch.scope.tasks as string[]).map(t => <code key={t} className="chip">{t}</code>)} caduca {batch.expires_at}</p>
              <label>Contrato de la siguiente tarea<textarea rows={6} value={plan} maxLength={200000} onChange={e => setPlan(e.target.value)} /></label></>}
          <div className="actions">{!batch.scope.chain_commits && <button disabled={!can("batch_next") || !plan.trim()} onClick={() => void operate(() => send(jobRequest(`/phases/${id}/batch/next`, { expected_version: v, authorization_id: batch.id, text: plan })))}>Encolar siguiente tarea del lote</button>}
            <button className="button-danger" disabled={busy || stale || !batchReason.trim()} onClick={() => void operate(async () => {
              await managed(`/phases/${id}/authorizations/${batch.id}/revoke`, { expected_version: v, reason: batchReason } satisfies S["PhaseRevokeCreate"]);
            })}>Revocar lote</button></div></>
          : <>{(phase.definition.tasks as string[]).map(task => <label className="check" key={task}><input type="checkbox" checked={batchTasks.includes(task)}
            onChange={e => setBatchTasks(e.target.checked ? [...batchTasks, task] : batchTasks.filter(t => t !== task))} /><code>{task}</code></label>)}
            <label>Vigencia en segundos (máximo 24 horas)<input type="number" min={1} max={86400} value={batchTtl} onChange={e => setBatchTtl(Number(e.target.value))} /></label>
            <label className="check"><input type="checkbox" checked={chainCommits} onChange={e => setChainCommits(e.target.checked)} />Desatendido: encadenar tareas y confirmar el commit de cada aceptación elegible.</label>
            {chainCommits && <label>Plan congelado con las secciones de las tareas<textarea rows={6} value={batchPlan} maxLength={200000} onChange={e => setBatchPlan(e.target.value)} /></label>}</>}
        <label>Motivo del lote o de su revocación<input value={batchReason} maxLength={2000} onChange={e => setBatchReason(e.target.value)} /></label>
        {!batch && <><label className="check"><input type="checkbox" checked={batchConfirmed} onChange={e => setBatchConfirmed(e.target.checked)} />{chainCommits ? "Autorizo ejecutar estas tareas y confirmar sus commits sin intervención; el cierre requerirá otra autorización." : "Autorizo ejecutar estas tareas en lote; el cierre requerirá otra autorización."}</label>
          <button disabled={!can("authorize_batch") || !batchConfirmed || !batchReason.trim() || !batchTasks.length || (chainCommits && !batchPlan.trim())} onClick={() => void operate(async () => {
            await managed(`/phases/${id}/authorizations`, { expected_version: v, tasks: batchTasks, ttl_seconds: batchTtl, reason: batchReason, confirmed: true,
              chain_commits: chainCommits, text: chainCommits ? batchPlan : null } satisfies S["PhaseBatchCreate"]);
            setBatchTasks([]);
          })}>Autorizar lote</button></>}
      </div>
    </section>}

    {!section && <details className="panel panel-collapsible">
      <summary><h2>Enmendar o abandonar</h2></summary>
      <div className="decision">
        <h3>Enmendar definición</h3>
        <p className="hint">Crea la versión {phase.definition_number + 1} de la definición y conserva las anteriores. Invalida el READY vigente y los lotes activos. El código no cambia; los documentos nuevos se adoptan con su hash actual.</p>
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
        })}>Enmendar definición</button>
      </div>
      <div className="decision decision-danger">
        <h3>Abandonar fase</h3>
        <p className="hint">Estado terminal y auditado: no edita documentos ni Git, invalida lotes activos y libera el checkout para otra fase.</p>
        <label>Motivo del abandono<input value={abandonReason} maxLength={2000} onChange={e => setAbandonReason(e.target.value)} /></label>
        <label className="check"><input type="checkbox" checked={abandonConfirmed} onChange={e => setAbandonConfirmed(e.target.checked)} />Abandono esta fase de forma definitiva.</label>
        <button className="button-danger" disabled={!can("abandon") || !abandonConfirmed || !abandonReason.trim()} onClick={() => void operate(async () => {
          await managed(`/phases/${id}/abandon`, { expected_version: v, reason: abandonReason, confirmed: true } satisfies S["PhaseAbandonCreate"]);
        })}>Abandonar fase</button>
      </div>
    </details>}

    {(!section || section === "phase-history") && <section className="panel" aria-labelledby="phase-history">
      <h2 id="phase-history">Historial</h2>
      {!phase.operations.length && <p className="hint">Sin operaciones registradas.</p>}
      {phase.operations.map(o => <div className="entry" key={o.id}><p><strong>{o.kind}</strong> {o.status}</p>
        {Array.isArray(o.result?.reasons) && (o.result!.reasons as string[]).length > 0 && <p>{(o.result!.reasons as string[]).join("; ")}</p>}
        <Evidence title="Solicitud, resultado y evidencia" value={o} /></div>)}
      <Evidence title="Autorizaciones de lote y de cierre" value={phase.authorizations} />
    </section>}
  </>;
}

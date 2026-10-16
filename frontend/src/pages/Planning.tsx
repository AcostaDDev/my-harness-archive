import { useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import { unifiedDiff } from "../diff.ts";
import { createOnce, jobRequest, managed, ManagedError } from "../managed-api";
import type { S } from "../managed-api";
import type { Route } from "../router";
import { Migration } from "./Project";
import { Link, navigate } from "../navigation";
import { Alert, DiffBlock, Empty, Evidence, Fields, Hash, Loading, PageHeader, Stale, Status, message, usePoll, when } from "../ui";
import { useWorkspace } from "../workspace";
import { EditProgress, MarkdownView } from "./Docs";

// Creación y planificación conversacionales en la UI (H6.2 E4) sobre la API de H6.5 (D075).
// El agente nunca escribe: cada borrador se aplica o se edita con CAS sobre el hash mostrado, y la aceptación
// y el plan se confirman sobre la vista previa exacta. Nada se escribe al teclear ni al recargar.

type Conversation = S["PlanningConversationRead"];
type Summary = S["PlanningConversationSummaryRead"];
type Proposal = S["PlanningProposalRead"];
type Turn = S["PlanningTurnRead"];
type Drafts = S["PlanningDraftsRead"];
type DraftRead = S["PlanningDraftContentRead"];
type Acceptance = S["DefinitionPreviewRead"];
type Operation = S["DefinitionOperationRead"];
type TurnResult = { answer?: string; questions?: { text: string; blocking: boolean }[]; pending?: string[];
  drafts?: { path: string; reason: string }[]; plan?: { reason: string } | null };

const q = encodeURIComponent;
const TURN: Record<Turn["status"], [string, "active" | "ok" | "danger" | "neutral" | "attention"]> = {
  QUEUED: ["En cola o en curso", "active"], ANSWERED: ["Respondido", "ok"], FAILED: ["Fallido, sin reintento", "danger"],
  UNKNOWN: ["Resultado desconocido, sin reintento", "attention"], REFUSED: ["Rechazado por el modo del checkout", "neutral"],
};
const PROPOSAL: Record<Proposal["status"], [string, "active" | "ok" | "danger" | "neutral" | "attention"]> = {
  PROPOSED: ["Propuesta", "attention"], APPLIED: ["Aplicada", "ok"], ACCEPTED: ["Plan confirmado", "ok"],
  DISMISSED: ["Descartada", "neutral"], SUPERSEDED: ["Sustituida", "neutral"],
};
const ORIGIN: Record<S["DefinitionDocumentRead"]["origin"], string> = {
  draft: "Borrador tal cual", "draft+blocks": "Borrador con bloques regenerados", template: "Plantilla unificada", archive: "Archivo de la definición",
};

function draftRoute(conversation: Conversation, project: string, path?: string): Route {
  return conversation.kind === "onboarding" ? { name: "onboarding", project, conversation: conversation.id, path }
    : conversation.kind === "project_import" ? { name: "import", project, conversation: conversation.id, path }
    : { name: "setup", project, path };
}

function Tone({ value }: { value: [string, string] }) {
  return <span className={`status status-${value[1]}`}><span className="status-mark" aria-hidden="true" />{value[0]}</span>;
}

/** Pasos de la creación con la misma vía que el ciclo de la fase: dónde está y qué falta. */
function Steps({ current, labels }: { current: number; labels: string[] }) {
  return <div className="rail" role="img" aria-label={`Paso ${current + 1} de ${labels.length}: ${labels[Math.min(current, labels.length - 1)]}`}>
    <ol className="rail-track">{labels.map((label, index) => <li key={label} className={index < current ? "rail-past" : index === current ? "rail-now" : "rail-next"}>
      <span className="rail-stop" aria-hidden="true" /><span className="rail-label">{label}</span></li>)}</ol>
  </div>;
}

function conflictText(error: unknown) {
  return error instanceof ManagedError && error.status === 409 ? message(error) : undefined;
}

// --- conversación compartida -------------------------------------------------------------------

function TurnList({ conversation }: { conversation: Conversation }) {
  if (!conversation.turns.length) return <p className="hint">Todavía no hay turnos. Escribe el primer mensaje abajo.</p>;
  return <ol className="entry-list">{conversation.turns.map(turn => {
    const result = (turn.result?.result ?? null) as TurnResult | null;
    const reasons = Array.isArray(turn.result?.reasons) ? turn.result!.reasons as string[] : [];
    return <li className="entry turn" key={turn.id}>
      <p className="turn-head"><strong>Turno {turn.number}</strong> <Tone value={TURN[turn.status]} /> <span className="muted">{when(turn.created_at)}</span></p>
      <p className="turn-message">{turn.message}</p>
      {turn.status === "QUEUED" && turn.run_status === "RECOVERY_REQUIRED" && <p className="state state-attention">El turno se interrumpió: su resultado es desconocido y no se repite. Confirma el escritor detenido en el <Link to={{ name: "run-short", run: turn.run_id }}>run {turn.run_id.slice(0, 8)}</Link>.</p>}
      {result?.answer && <p className="turn-answer">{result.answer}</p>}
      {!!result?.drafts?.length && <p className="hint">Borradores propuestos: {result.drafts.map(d => <code key={d.path} className="chip">{d.path}</code>)}</p>}
      {result && "plan" in result && <p className="hint">{result.plan ? "Propone un plan para la fase de destino." : "Sin plan propuesto."}</p>}
      {reasons.length > 0 && <p className="state state-error">{reasons.join("; ")}</p>}
      <p className="hint">
        <Link to={{ name: "run-short", run: turn.run_id }}>Run {turn.run_id.slice(0, 8)}</Link> <Status value={turn.run_status} />
        {" "}· contexto <Hash value={turn.context_sha256} />
        {turn.drafts.length > 0 && <> · {turn.drafts.length} borradores congelados</>}
        {turn.documents.length > 0 && <> · {turn.documents.length} documentos congelados</>}
        {turn.user_edits.length > 0 && <> · {turn.user_edits.length === 1 ? "1 edición tuya detectada" : `${turn.user_edits.length} ediciones tuyas detectadas`}</>}
      </p>
      <Evidence title="Contexto congelado y resultado" value={turn} />
    </li>;
  })}</ol>;
}

function MessageForm({ conversation, path, hint }: { conversation: Conversation; path: string; hint: ReactNode }) {
  const { busy, operate, send } = useWorkspace();
  const [text, setText] = useState("");
  const pending = conversation.turns.some(t => t.status === "QUEUED");
  const open = conversation.actions.includes("message");
  return <form onSubmit={e => { e.preventDefault(); if (open && text.trim()) void operate(async () => {
    await send(jobRequest(path, { expected_version: conversation.version, text } satisfies S["PlanningMessageCreate"]));
    setText("");
  }); }}>
    <label>Mensaje al revisor<textarea rows={4} value={text} maxLength={20000} onChange={e => setText(e.target.value)} disabled={!open} /></label>
    <p className="hint">{hint}</p>
    {pending && <p role="status" className="state state-loading">El turno anterior sigue en curso; su respuesta aparecerá aquí.</p>}
    <button disabled={busy || !open || !text.trim()}>Enviar mensaje</button>
  </form>;
}

function Dismiss({ conversation, proposal, base }: { conversation: Conversation; proposal: Proposal; base: string }) {
  const { busy, operate } = useWorkspace();
  const [reason, setReason] = useState("");
  if (!proposal.actions.includes("dismiss")) return null;
  return <div className="form-row">
    <label>Motivo del descarte<input value={reason} maxLength={2000} onChange={e => setReason(e.target.value)} /></label>
    <button type="button" className="button-quiet" disabled={busy || !reason.trim()} onClick={() => void operate(async () => {
      await managed(`${base}/proposals/${proposal.id}/dismiss`, { expected_version: conversation.version, reason } satisfies S["PlanningDismissCreate"]);
    })}>Descartar propuesta</button>
  </div>;
}

// --- creación: /projects/:p/setup ----------------------------------------------------------------

export function SetupPage({ path }: { path?: string }) {
  const { project, refresh } = useWorkspace();
  const info = usePoll<S["ManagedProjectRead"]>(`/projects/${project}`, 0);
  const v2 = info.data?.documents === "v2";
  const status = usePoll<S["BootstrapStatusRead"]>(v2 ? `/projects/${project}/bootstrap` : null, 4000, refresh);
  const list = usePoll<Summary[]>(v2 ? `/projects/${project}/planning` : null, 4000, refresh);
  if (!info.data) return info.error ? <Alert>{info.error}</Alert> : <Loading />;
  if (!v2) return <>
    <PageHeader title="Creación del proyecto" />
    <Empty title="Este proyecto usa el contrato documental anterior">
      <p>La creación conversacional usa el contrato unificado D088. Los proyectos anteriores requieren importación; vuelve al <Link to={{ name: "project", project }}>resumen</Link>.</p>
    </Empty>
  </>;
  if (!status.data || !list.data) return status.error ?? list.error ? <Alert>{status.error ?? list.error}</Alert> : <Loading />;
  const definition = list.data.find(c => c.kind === "definition");
  if (definition) return <Definition key={definition.id} id={definition.id} path={path} status={status.data} />;
  if (status.data.definition_operation) return <Empty title="El proyecto ya está creado"><p>Ve al <Link to={{ name: "project", project }}>resumen</Link>.</p></Empty>;
  if (!status.data.enabled) return <>
    <PageHeader title="Creación del proyecto" />
    <Empty title="El operador no ha autorizado crear este proyecto">
      <p>La creación escribe borradores y el commit raíz en la carpeta, así que necesita <code>bootstrap_enabled</code> en el registro (con el techo de <code>[registration]</code> del TOML) o en el proyecto del operador. Si la carpeta ya tiene un proyecto, se importa en lugar de crearse.</p>
    </Empty>
  </>;
  return <BriefForm status={status.data} />;
}

function BriefForm({ status }: { status: S["BootstrapStatusRead"] }) {
  const { project, busy, operate } = useWorkspace();
  const key = `harness-setup-brief-v1:${project}`;
  const [title, setTitle] = useState(() => { try { return JSON.parse(sessionStorage.getItem(key) ?? "null")?.title ?? ""; } catch { return ""; } });
  const [brief, setBrief] = useState(() => { try { return JSON.parse(sessionStorage.getItem(key) ?? "null")?.brief ?? ""; } catch { return ""; } });
  const [view, setView] = useState<"edit" | "preview">("edit");
  useEffect(() => { try { sessionStorage.setItem(key, JSON.stringify({ title, brief })); } catch { /* sin borrador */ } }, [key, title, brief]);
  const bytes = new TextEncoder().encode(brief).length;
  return <>
    <PageHeader title="Crear el proyecto">
      <p>Describe qué quieres construir. El revisor propone los documentos de la plantilla unificada en turnos de solo lectura; tú aplicas, editas o descartas cada borrador, y al aceptar el harness hace el commit raíz con la fase P001 activa.</p>
    </PageHeader>
    <Steps current={0} labels={["Brief", "Conversación y borradores", "Aceptación", "Primera tarea"]} />
    {status.import_required && <p role="alert" className="state state-attention">{status.diagnostic}</p>}
    <section className="panel" aria-labelledby="brief-title">
      <h2 id="brief-title">Brief</h2>
      <p className="hint">Markdown libre, como máximo 256 KiB. Se congela al empezar y se archiva en <code>archive/phase-000/BRIEF.md</code>; no se edita después.</p>
      <form onSubmit={e => { e.preventDefault(); void operate(async () => {
        await createOnce<Conversation>(`/projects/${project}/planning`, { kind: "definition", title: title.trim(), brief, phase_id: null } satisfies S["PlanningConversationCreate"]);
        try { sessionStorage.removeItem(key); } catch { /* sin borrador */ }
      }); }}>
        <label>Nombre del proyecto<input value={title} maxLength={200} onChange={e => setTitle(e.target.value)} required /></label>
        <div className="docs-editor-tabs" role="tablist">
          <button type="button" role="tab" aria-selected={view === "edit"} className={view === "edit" ? "" : "button-quiet"} onClick={() => setView("edit")}>Escribir</button>
          <button type="button" role="tab" aria-selected={view === "preview"} className={view === "preview" ? "" : "button-quiet"} onClick={() => setView("preview")}>Vista previa</button>
        </div>
        {view === "edit" ? <label><span className="visually-hidden">Brief en Markdown</span><textarea rows={16} value={brief} onChange={e => setBrief(e.target.value)} spellCheck
            placeholder={"# Qué construimos\n\nProblema, usuarios, funciones mínimas, restricciones y objetivo de entrega."} /></label>
          : <article className="doc-reader">{brief.trim() ? <MarkdownView source={brief} path="docs/BRIEF.md" /> : <p className="hint">Nada que mostrar todavía.</p>}</article>}
        <p className="hint">{bytes.toLocaleString("es-ES")} bytes{bytes > 256 * 1024 ? " · supera el límite de 256 KiB" : ""}</p>
        <button disabled={busy || !title.trim() || !brief.trim() || bytes > 256 * 1024 || status.import_required}>Empezar la definición</button>
      </form>
    </section>
  </>;
}

function Definition({ id, path, status }: { id: string; path?: string; status: S["BootstrapStatusRead"] }) {
  const { project, refresh } = useWorkspace();
  const base = `/projects/${project}/planning/${id}`;
  const read = usePoll<Conversation>(base, 1500, refresh);
  const c = read.data;
  const drafts = usePoll<Drafts>(c && !c.created ? `${base}/drafts` : null, 3000, refresh);
  if (!c) return read.error ? <Alert>{read.error}</Alert> : <Loading />;
  const op = c.operation ?? status.definition_operation ?? null;
  const proposed = c.proposals.filter(p => p.status === "PROPOSED");
  const step = op?.status === "COMPLETED" ? 3 : op ? 2 : 1;
  return <div className="docs-layout">
    <DraftTree conversation={c} drafts={drafts.data} current={path} error={drafts.error} />
    <div className="docs-main">
      {path && !c.created ? <DraftPage key={path} conversation={c} path={path} drafts={drafts.data} />
        : <>
          <PageHeader title={c.title} aside={c.created ? <span className="status status-ok"><span className="status-mark" aria-hidden="true" />Proyecto creado</span> : undefined}>
            <p>Definición conversacional del proyecto. El revisor solo propone: nada se escribe en la carpeta sin tu confirmación.</p>
          </PageHeader>
          <Stale error={read.error} />
          <Steps current={step} labels={["Brief", "Conversación y borradores", "Aceptación", "Primera tarea"]} />
          {op && <OperationPanel conversation={c} op={op} />}
          <BriefPanel base={base} brief={c.brief} />
          <section className="panel" aria-labelledby="def-turns">
            <h2 id="def-turns">Conversación <span className="count">{c.turns.length} turnos</span></h2>
            <TurnList conversation={c} />
            {!c.created && <MessageForm conversation={c} path={`${base}/messages`} hint="Cada mensaje es una invocación nueva de solo lectura del revisor con el brief, los borradores en disco y tus ediciones desde el último turno respondido." />}
          </section>
          <Questions conversation={c} base={base} />
          {(proposed.length > 0 || c.proposals.length > 0) && <section className="panel" aria-labelledby="def-proposals">
            <h2 id="def-proposals">Propuestas de borrador <span className="count">{proposed.length} por decidir</span></h2>
            {proposed.length === 0 && <p className="hint">No hay propuestas pendientes.</p>}
            {proposed.map(p => <ProposalEntry key={p.id} conversation={c} proposal={p} base={base} drafts={drafts.data} />)}
            <ProposalHistory proposals={c.proposals.filter(p => p.status !== "PROPOSED")} />
          </section>}
          {!c.created && !op && <AcceptPanel conversation={c} base={base} drafts={drafts.data} />}
        </>}
    </div>
  </div>;
}

function BriefPanel({ base, brief }: { base: string; brief: Conversation["brief"] }) {
  const [open, setOpen] = useState(false);
  const read = usePoll<S["PlanningBriefRead"]>(open ? `${base}/brief` : null, 0);
  return <details className="panel panel-collapsible" onToggle={e => setOpen((e.target as HTMLDetailsElement).open)}>
    <summary><h2>Brief congelado</h2></summary>
    <p className="hint">Hash <Hash value={brief ? String(brief.sha256) : null} /> · {brief ? `${Number(brief.size).toLocaleString("es-ES")} bytes` : ""}</p>
    {open && (read.data ? <article className="doc-reader"><MarkdownView source={read.data.content} path="docs/BRIEF.md" /></article> : read.error ? <Alert>{read.error}</Alert> : <Loading />)}
  </details>;
}

function Questions({ conversation, base }: { conversation: Conversation; base: string }) {
  const { busy, operate } = useWorkspace();
  const [reasons, setReasons] = useState<Record<string, string>>({});
  if (!conversation.questions.length && !conversation.pending.length) return null;
  const canDefer = conversation.actions.includes("defer_question");
  return <section className="panel" aria-labelledby="def-questions">
    <h2 id="def-questions">Preguntas y pendientes del último turno</h2>
    {conversation.questions.map(question => <div key={question.id} className={question.blocking && !question.deferred ? "entry entry-open" : "entry"}>
      <p><strong>{question.blocking ? "Bloqueante" : "Informativa"}</strong>{question.deferred ? " · aplazada" : ""}: {question.text}</p>
      {question.deferred && <p className="hint">Aplazada con motivo: {String(question.deferred.reason)}</p>}
      {question.blocking && !question.deferred && <>
        <p className="hint">Respóndela en un mensaje nuevo o aplázala de forma explícita; aplazar no la responde, solo deja de bloquear la aceptación y queda registrado en la conversación y su vista previa.</p>
        {canDefer && <div className="form-row"><label>Motivo del aplazamiento<input value={reasons[question.id] ?? ""} maxLength={2000} onChange={e => setReasons({ ...reasons, [question.id]: e.target.value })} /></label>
          <button type="button" className="button-quiet" disabled={busy || !(reasons[question.id] ?? "").trim()} onClick={() => void operate(async () => {
            await managed(`${base}/questions/defer`, { expected_version: conversation.version, question_id: question.id, reason: reasons[question.id] } satisfies S["PlanningDeferCreate"]);
          })}>Aplazar pregunta</button></div>}
      </>}
    </div>)}
    {conversation.pending.length > 0 && <><h3>Pendientes declarados</h3>
      <p className="hint">Son avisos del revisor, no bloqueos; aparecen en la vista previa de la aceptación.</p>
      <ul>{conversation.pending.map(item => <li key={item}>{item}</li>)}</ul></>}
  </section>;
}

function ProposalHistory({ proposals }: { proposals: Proposal[] }) {
  if (!proposals.length) return null;
  return <details className="evidence"><summary>Historial de propuestas ({proposals.length})</summary>
    <ul className="docs-changes">{proposals.map(p => <li key={p.id}>
      <span className="mono">#{p.number}</span> {p.path ? <code className="path">{p.path}</code> : "plan"} <Tone value={PROPOSAL[p.status]} />
      <span className="muted"> · turno {p.turn_number}{p.decision?.reason ? ` · ${String(p.decision.reason)}` : ""}</span></li>)}</ul>
  </details>;
}

/** Contenido actual de un borrador (null si no existe) por la misma inspección que la CAS. */
function useDraft(conversation: string, path: string | null, refresh: number, interval = 0) {
  const { project } = useWorkspace();
  const read = usePoll<DraftRead>(path ? `/projects/${project}/planning/${conversation}/drafts/content?path=${q(path)}` : null, interval, refresh);
  return { draft: read.data, missing: read.missing, error: read.missing ? undefined : read.error, loading: read.loading };
}

function ProposalEntry({ conversation, proposal, base, drafts }: { conversation: Conversation; proposal: Proposal; base: string; drafts?: Drafts }) {
  const { project } = useWorkspace();
  const [open, setOpen] = useState(false);
  const disk = drafts?.drafts.find(d => d.path === proposal.path);
  const moved = disk && disk.sha256 !== proposal.base_sha256 && disk.sha256 !== proposal.content_sha256;
  return <div className="entry entry-open">
    <p><strong>#{proposal.number}</strong> <Link to={draftRoute(conversation, project, proposal.path!)}><code className="path">{proposal.path}</code></Link>{" "}
      <span className="muted">· turno {proposal.turn_number} · {proposal.base_sha256 ? "sustituye un borrador" : "documento nuevo"}</span></p>
    <p>{proposal.reason}</p>
    {moved && <p className="state state-attention">El borrador cambió en disco desde el turno: aplicarla no sobrescribirá tu cambio y fallará. Pide otro turno o edítalo tú.</p>}
    <details onToggle={e => setOpen((e.target as HTMLDetailsElement).open)}><summary>Revisar el diff y decidir</summary>
      {open && <ProposalReview conversation={conversation} proposal={proposal} base={base} />}
    </details>
  </div>;
}

/** Diff del borrador en disco a la propuesta y confirmación ligada a su hash; el harness escribe con CAS. */
function ProposalReview({ conversation, proposal, base }: { conversation: Conversation; proposal: Proposal; base: string }) {
  const { busy, refresh, operate } = useWorkspace();
  const { draft, missing, error } = useDraft(conversation.id, proposal.path, refresh);
  const [confirmed, setConfirmed] = useState(false);
  const [conflict, setConflict] = useState<string>();
  const [view, setView] = useState<"diff" | "render">("diff");
  useEffect(() => { setConfirmed(false); }, [conversation.version, draft?.sha256]);
  if (error) return <Alert>{error}</Alert>;
  if (!draft && !missing) return <Loading />;
  const current = draft?.content ?? null;
  const diff = unifiedDiff(proposal.path!, current, proposal.content);
  const canApply = proposal.actions.includes("apply");
  return <div className="docs-review">
    <Fields items={[["En disco", draft ? <Hash value={draft.sha256} /> : "no existe"], ["Leído por el turno", proposal.base_sha256 ? <Hash value={proposal.base_sha256} /> : "no existía"],
      ["Propuesto", <Hash value={proposal.content_sha256} />], ["Propuesta", <Hash value={proposal.proposal_sha256} />]]} />
    <div className="docs-editor-tabs" role="tablist">
      <button type="button" role="tab" aria-selected={view === "diff"} className={view === "diff" ? "" : "button-quiet"} onClick={() => setView("diff")}>Diff</button>
      <button type="button" role="tab" aria-selected={view === "render"} className={view === "render" ? "" : "button-quiet"} onClick={() => setView("render")}>Documento propuesto</button>
    </div>
    {view === "render" ? <article className="doc-reader"><MarkdownView source={proposal.content} path={proposal.path!} /></article>
      : diff === null ? <p className="hint">Demasiado grande para compararlo aquí; revisa el documento propuesto completo.</p>
        : diff === "" ? <p className="hint">El borrador en disco ya es exactamente esta propuesta.</p>
          : <DiffBlock diff={diff} label={`Diff de ${proposal.path}`} />}
    {conflict && <p role="alert" className="state state-error">{conflict}</p>}
    {canApply && <>
      <label className="check"><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />He revisado esta propuesta exacta ({proposal.proposal_sha256.slice(0, 12)}) y quiero que el harness la escriba en <code>{proposal.path}</code>.</label>
      <div className="actions"><button type="button" disabled={busy || !confirmed} onClick={() => void operate(async () => {
        setConflict(undefined);
        try {
          await managed(`${base}/proposals/${proposal.id}/apply`, { expected_version: conversation.version, proposal_sha256: proposal.proposal_sha256, confirmed: true } satisfies S["PlanningApplyCreate"]);
        } catch (e) { const text = conflictText(e); if (text) setConflict(`No se aplicó: ${text}`); else throw e; }
      })}>Aplicar propuesta</button></div>
    </>}
    <Dismiss conversation={conversation} proposal={proposal} base={base} />
  </div>;
}

// --- borradores ----------------------------------------------------------------------------------

function matchesPattern(path: string, patterns: string[]) {
  return patterns.some(pattern => {
    const folder = pattern.slice(0, -"/*.md".length);
    const name = path.slice(folder.length + 1);
    return path.startsWith(`${folder}/`) && name.endsWith(".md") && !name.includes("/") && name.length > 3;
  });
}

function DraftTree({ conversation, drafts, current, error }: { conversation: Conversation; drafts?: Drafts; current?: string; error?: string }) {
  const { project } = useWorkspace();
  const pending = new Set(conversation.proposals.filter(p => p.status === "PROPOSED").map(p => p.path));
  const present = new Map(drafts?.drafts.filter(d => d.sha256).map(d => [d.path, d]));
  const required = new Set(drafts?.allowed.required);
  const paths = [...new Set([...(drafts?.allowed.fixed ?? []), ...present.keys(), ...[...pending].filter(Boolean) as string[]])].sort();
  // Carpeta de documentación (la de STATE): los nombres del árbol son relativos a ella; la ruta completa va en el título.
  const docsFolder = drafts?.allowed.required.find(p => p.endsWith("/STATE.md"))?.slice(0, -"/STATE.md".length);
  return <nav className="docs-tree" aria-label="Borradores">
    <p className="docs-tree-title"><Link to={draftRoute(conversation, project)} current={!current}>{conversation.kind === "onboarding" ? "Incorporación" : conversation.kind === "project_import" ? "Importación" : "Definición"}</Link></p>
    {conversation.created ? <p className="hint">{conversation.kind !== "definition" ? "Incorporación confirmada; borradores cerrados. Consulta la" : "Proyecto creado: consulta la"} <Link to={{ name: "docs", project }}>documentación</Link>.</p>
      : !drafts ? (error ? <Alert>{error}</Alert> : <Loading />) : <>
        <ul className="docs-tree-list">{paths.map(path => {
          const draft = present.get(path);
          return <li key={path}><Link to={draftRoute(conversation, project, path)} current={path === current} className="docs-tree-file">
            <span className={draft ? "docs-tree-name" : "docs-tree-name muted"} title={path}>{docsFolder && path.startsWith(`${docsFolder}/`) ? path.slice(docsFolder.length + 1) : path}</span>
            {pending.has(path) && <span className="docs-flag docs-flag-local" title="Propuesta pendiente de decidir">propuesta</span>}
            {draft?.user_edited && <span className="docs-flag docs-flag-drift" title="Cambiado desde el último turno respondido; el siguiente turno lo verá">editado</span>}
            {!draft && required.has(path) && <span className="docs-flag" title={conversation.kind === "project_import" ? "La vista previa combina los documentos del origen y los borradores" : "Obligatorio para aceptar"}>{conversation.kind === "project_import" ? "sin borrador" : "falta"}</span>}
          </Link></li>;
        })}</ul>
        {drafts.invalid.length > 0 && <p className="hint">Inválidos: {drafts.invalid.map(p => <code key={p} className="chip">{p}</code>)}</p>}
        {drafts.foreign.length > 0 && <div className="docs-tree-missing"><p className="hint">{conversation.kind === "project_import" ? "Archivos ajenos del área privada (no se importan):" : "Archivos ajenos (bloquean la aceptación):"}</p>
          <ul className="docs-tree-list">{drafts.foreign.map(p => <li key={p}><code className="path">{p}</code></li>)}</ul>
          {drafts.foreign_truncated && <p className="hint">Lista recortada.</p>}</div>}
        <NewDraft conversation={conversation} patterns={drafts.allowed.patterns} existing={new Set(paths)} />
      </>}
  </nav>;
}

function NewDraft({ conversation, patterns, existing }: { conversation: Conversation; patterns: string[]; existing: Set<string> }) {
  const { project } = useWorkspace();
  const [path, setPath] = useState("");
  const valid = matchesPattern(path.trim(), patterns) && !existing.has(path.trim());
  return <form className="docs-new" onSubmit={e => { e.preventDefault(); if (valid) navigate(draftRoute(conversation, project, path.trim())); }}>
    <label>Nuevo borrador<input value={path} onChange={e => setPath(e.target.value)} placeholder={patterns[0]?.replace("*", "D002-titulo")} maxLength={400} /></label>
    <p className="hint">Admitidos: {patterns.map(p => <code key={p} className="chip">{p}</code>)}</p>
    <button className="button-quiet" disabled={!valid}>Crear borrador</button>
  </form>;
}

type Edit = { base: string | null; text: string };

function loadEdit(key: string): Edit | undefined {
  try { return JSON.parse(sessionStorage.getItem(key) ?? "null") ?? undefined; } catch { return undefined; }
}
function saveEdit(key: string, value?: Edit) {
  try { if (value) sessionStorage.setItem(key, JSON.stringify(value)); else sessionStorage.removeItem(key); } catch { /* sin borrador guardado */ }
}

function DraftPage({ conversation, path, drafts }: { conversation: Conversation; path: string; drafts?: Drafts }) {
  const { project, refresh } = useWorkspace();
  const base = `/projects/${project}/planning/${conversation.id}`;
  // Se relee: una edición en disco se ve (y el editor la avisa) antes de intentar guardar.
  const { draft, missing, error } = useDraft(conversation.id, path, refresh, 3000);
  const key = conversation.kind === "onboarding" ? `harness-onboarding-draft-v1:${project}:${conversation.id}:${path}`
    : conversation.kind === "project_import" ? `harness-import-draft-v1:${project}:${conversation.id}:${path}`
    : `harness-setup-draft-v1:${project}:${path}`;
  const [editing, setEditing] = useState(() => !!loadEdit(key));
  const state = drafts?.drafts.find(d => d.path === path);
  const allowed = !!drafts && (drafts.allowed.fixed.includes(path) || matchesPattern(path, drafts.allowed.patterns));
  const proposal = conversation.proposals.find(p => p.status === "PROPOSED" && p.path === path);
  const canEdit = conversation.actions.includes("edit_draft");
  const blocked = canEdit ? undefined : conversation.turns.some(t => t.status === "QUEUED") ? "Hay un turno en curso; espera su respuesta para editar." : "La definición ya no admite cambios.";
  const name = path.split("/").pop()!;
  if (error) return <><PageHeader title={name} code><p><code className="path">{path}</code></p></PageHeader><Alert>{error}</Alert></>;
  if (!draft && !missing) return <Loading />;
  return <>
    <PageHeader title={name} code aside={!editing && canEdit && allowed && <button type="button" onClick={() => setEditing(true)}>{draft ? "Editar" : "Crear"}</button>}>
      <p><code className="path">{path}</code>{draft && <> · <Hash value={draft.sha256} /></>}{drafts?.allowed.required.includes(path) && " · obligatorio"}</p>
    </PageHeader>
    {drafts && !allowed && <p className="state state-attention">Esta ruta no es un borrador admitido; un archivo aquí sería ajeno y bloquearía la aceptación.</p>}
    {state?.user_edited && <p className="state state-neutral" role="status">Cambiado desde lo que vio el último turno respondido (<Hash value={state.known_sha256} length={8} /> → <Hash value={state.sha256} length={8} />). El próximo turno lo recibirá como edición tuya.</p>}
    {blocked && <p className="hint">{blocked}</p>}
    {proposal && <section className="decision decision-attention" aria-labelledby="draft-proposal">
      <h2 id="draft-proposal">Propuesta #{proposal.number} del turno {proposal.turn_number}</h2>
      <p>{proposal.reason}</p>
      <ProposalReview conversation={conversation} proposal={proposal} base={base} />
    </section>}
    {editing ? <DraftEditor conversation={conversation} path={path} draft={draft ?? null} editKey={key} blocked={blocked} onClose={() => setEditing(false)} />
      : draft ? <article className="doc-reader"><MarkdownView source={draft.content} path={path} /></article>
        : <Empty title="Este borrador no existe todavía"><p>{allowed ? "Créalo tú o pide al revisor que lo proponga." : "Vuelve a la definición."}</p></Empty>}
  </>;
}

/** Editor de un borrador: texto completo, vista previa y diff; se guarda con CAS sobre el hash con que se abrió. */
function DraftEditor({ conversation, path, draft, editKey, blocked, onClose }: {
  conversation: Conversation; path: string; draft: DraftRead | null; editKey: string; blocked?: string; onClose: () => void;
}) {
  const { project, busy, operate } = useWorkspace();
  const [edit, setEdit] = useState<Edit>(() => loadEdit(editKey) ?? { base: draft?.sha256 ?? null, text: draft?.content ?? "" });
  const [view, setView] = useState<"edit" | "preview" | "review">("edit");
  const [confirmed, setConfirmed] = useState(false);
  const [conflict, setConflict] = useState<string>();
  const [removing, setRemoving] = useState(false);
  useEffect(() => { saveEdit(editKey, edit); }, [editKey, edit]);
  useEffect(() => { setConfirmed(false); }, [edit.text, view, removing]);
  const stale = edit.base !== (draft?.sha256 ?? null);
  const after = removing ? null : edit.text;
  const diff = unifiedDiff(path, draft?.content ?? null, after);
  function close() { saveEdit(editKey); onClose(); }
  async function save() {
    setConflict(undefined);
    try {
      await managed(`/projects/${project}/planning/${conversation.id}/drafts`,
        { expected_version: conversation.version, path, content: after, base_sha256: edit.base } satisfies S["PlanningDraftEdit"], undefined, "PUT");
      close();
    } catch (e) {
      const text = conflictText(e);
      if (!text) throw e;
      setConflict(text.includes("changed since") ? "Conflicto: el borrador cambió en disco desde que lo abriste. No se ha escrito nada; copia tu texto y descarta este borrador para partir de la versión actual." : text);
    }
  }
  const blocks = /<!-- harness-local:managed-[a-z-]+:(start|end) -->/.test(edit.text);
  return <section className="docs-editor" aria-label={`Editar ${path}`}>
    {stale && <p className="state state-attention" role="status">El borrador cambió desde que empezaste a editarlo (base <Hash value={edit.base} length={8} />, ahora <Hash value={draft?.sha256} length={8} />). Guardar fallará: copia tu texto y descarta para partir de la versión actual.</p>}
    {blocks && <p className="hint">Los bloques gestionados (<code>harness-local:managed-…</code>) se regeneran al aceptar; lo que escribas dentro se sustituye. No borres sus marcadores.</p>}
    <div className="docs-editor-tabs" role="tablist">
      <button type="button" role="tab" aria-selected={view === "edit"} className={view === "edit" ? "" : "button-quiet"} onClick={() => setView("edit")}>Escribir</button>
      <button type="button" role="tab" aria-selected={view === "preview"} className={view === "preview" ? "" : "button-quiet"} onClick={() => setView("preview")}>Vista previa</button>
      <button type="button" role="tab" aria-selected={view === "review"} className={view === "review" ? "" : "button-quiet"} onClick={() => setView("review")}>Revisar y guardar</button>
    </div>
    {view === "edit" && <label className="docs-editor-prose"><span className="visually-hidden">Contenido de {path}</span>
      <textarea value={edit.text} spellCheck rows={Math.min(36, Math.max(16, edit.text.split("\n").length + 1))} onChange={e => { setRemoving(false); setEdit({ ...edit, text: e.target.value }); }} /></label>}
    {view === "preview" && <article className="doc-reader"><MarkdownView source={edit.text} path={path} /></article>}
    {view === "review" && <div className="docs-review">
      {diff === null ? <p className="hint">Demasiado grande para compararlo aquí.</p> : diff === "" ? <p className="hint">Sin cambios respecto al disco.</p> : <DiffBlock diff={diff} label={`Cambios en ${path}`} />}
      {draft && <label className="check"><input type="checkbox" checked={removing} onChange={e => setRemoving(e.target.checked)} />Borrar este borrador en lugar de guardarlo.</label>}
      <label className="check"><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />He revisado {removing ? "el borrado" : "este diff"} y confirmo {removing ? "borrar" : "escribir"} <code>{path}</code> si sigue siendo <Hash value={edit.base} length={8} />.</label>
    </div>}
    {conflict && <p role="alert" className="state state-error">{conflict}</p>}
    <div className="actions">
      {view === "review" && <button type="button" disabled={busy || !confirmed || !!blocked || diff === "" || stale} onClick={() => void operate(save)}>{removing ? "Borrar borrador" : "Guardar borrador"}</button>}
      <button type="button" className="button-quiet" disabled={busy} onClick={close}>{edit.text !== (draft?.content ?? "") ? "Descartar cambios" : "Cerrar editor"}</button>
      {blocked && <span className="hint">{blocked}</span>}
    </div>
  </section>;
}

// --- aceptación ------------------------------------------------------------------------------------

function AcceptPanel({ conversation, base, drafts }: { conversation: Conversation; base: string; drafts?: Drafts }) {
  const { busy, operate } = useWorkspace();
  const [preview, setPreview] = useState<Acceptance>();
  const signature = drafts?.drafts.map(d => `${d.path}:${d.sha256}`).join("|");
  // La vista previa vale para la versión de la conversación y los bytes en disco con que se pidió.
  const shownFor = useRef<string | undefined>(undefined);
  useEffect(() => { if (shownFor.current !== `${conversation.version}/${signature}`) setPreview(undefined); }, [conversation.version, signature]);
  const can = conversation.actions.includes("accept");
  return <section className="panel" aria-labelledby="def-accept">
    <h2 id="def-accept">Aceptar la definición</h2>
    <p className="hint">La vista previa muestra los archivos íntegros del commit raíz: tus borradores (con los bloques de STATE, NEXT_STEPS, ROADMAP y DECISIONS regenerados), los README que falten, <code>archive/phase-000/</code>, la fase P001 y su primera tarea. O los bloqueos que lo impiden.</p>
    {!can && <p className="hint">Hay un turno en curso; acepta cuando termine.</p>}
    <button type="button" disabled={busy || !can} onClick={() => void operate(async () => {
      const shown = await managed<Acceptance>(`${base}/accept/preview`, {});
      shownFor.current = `${conversation.version}/${signature}`;
      setPreview(shown);
    })}>{preview ? "Volver a revisar" : "Revisar la aceptación"}</button>
    {preview && <AcceptReview conversation={conversation} base={base} preview={preview} />}
  </section>;
}

function AcceptReview({ conversation, base, preview, resume }: { conversation: Conversation; base: string; preview: Acceptance; resume?: Operation }) {
  const { busy, operate, send } = useWorkspace();
  const [reason, setReason] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  useEffect(() => { setConfirmed(false); }, [preview.preview_sha256]);
  const phase = preview.phase as { code: string; objective: string; exit_criteria: string[]; tasks: string[]; tag?: string | null } | null;
  const task = preview.first_task as Record<string, unknown> | null;
  return <div className="docs-review">
    {preview.blockers.length > 0 ? <div className="state state-error" role="alert"><p className="state-title">No se puede aceptar todavía</p>
      <ul>{preview.blockers.map(b => <li key={b}>{b}</li>)}</ul></div>
      : <p className="state state-ok" role="status">Lista para crear el proyecto.</p>}
    {preview.warnings.length > 0 && <div className="state state-attention"><p className="state-title">Avisos</p><ul>{preview.warnings.map(w => <li key={w}>{w}</li>)}</ul></div>}
    {phase && <>
      <h3>Fase <span className="mono">{phase.code}</span></h3>
      <p>{phase.objective}</p>
      <ul className="checklist">{phase.exit_criteria.map(c => <li key={c}>{c}</li>)}</ul>
      <Fields items={[["Tareas", phase.tasks.map(t => <code key={t} className="chip">{t}</code>)], ["Tag al cerrar", phase.tag ? <code>{phase.tag}</code> : <span className="muted">sin tag</span>],
        ["Primera tarea", task ? <><code>{String(task.task_id)}</code> {task.planner === "agent" ? "· contrato del planificador" : "· contrato determinista"}</> : "—"],
        ["Perfil", preview.profile], ["Vista previa", <Hash value={preview.preview_sha256} />]]} />
    </>}
    {preview.documents.length > 0 && <>
      <h3>Archivos del commit raíz <span className="count">{preview.documents.length}</span></h3>
      <ul className="docs-changes">{preview.documents.map(doc => <li key={doc.path}><AcceptedDocument conversation={conversation.id} doc={doc} /></li>)}</ul>
    </>}
    <Evidence title="Definición, política, preparación, validaciones y Git" value={{ definition: preview.definition, policy: preview.policy, preparation: preview.preparation, validations: preview.validations, versions: preview.versions, git: preview.git, author: preview.author, first_task: preview.first_task }} />
    {preview.ready && <>
      <p className="hint">Crear hace el commit raíz con exactamente estos bytes y abre P001. La preparación y la primera tarea se encolan después, por una acción propia.</p>
      <label>Motivo<input value={reason} maxLength={2000} onChange={e => setReason(e.target.value)} placeholder="Qué revisaste y por qué aceptas" /></label>
      <label className="check"><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />He revisado estos archivos, la fase P001 y la primera tarea, y confirmo crear el proyecto con la vista previa {preview.preview_sha256.slice(0, 12)}.</label>
      <button type="button" disabled={busy || !confirmed || !reason.trim()} onClick={() => void operate(() => send(jobRequest(`${base}/accept`, {
        preview_sha256: preview.preview_sha256, confirmed: true, reason,
        resume_operation_id: resume?.id ?? null, expected_version: resume ? resume.expected_version : null,
      } satisfies S["DefinitionAcceptCreate"])))}>{resume ? "Conciliar la creación confirmada" : "Crear el proyecto"}</button>
    </>}
  </div>;
}

function AcceptedDocument({ conversation, doc }: { conversation: string; doc: S["DefinitionDocumentRead"] }) {
  const [open, setOpen] = useState(false);
  return <details onToggle={e => setOpen((e.target as HTMLDetailsElement).open)}>
    <summary><code className="path">{doc.path}</code> <span className="muted">· {ORIGIN[doc.origin]} · {doc.before_sha256 === doc.sha256 ? <>sin cambios, </> : doc.before_sha256 ? <>de <Hash value={doc.before_sha256} length={8} /> a </> : "nuevo, "}<Hash value={doc.sha256} length={8} /></span></summary>
    {open && (doc.origin === "draft+blocks" ? <RegeneratedDiff conversation={conversation} doc={doc} /> : <pre>{doc.content}</pre>)}
  </details>;
}

/** Lo que cambia la aceptación en un borrador: solo los bloques gestionados regenerados. */
function RegeneratedDiff({ conversation, doc }: { conversation: string; doc: S["DefinitionDocumentRead"] }) {
  const { refresh } = useWorkspace();
  const { draft, error } = useDraft(conversation, doc.path, refresh);
  if (error) return <Alert>{error}</Alert>;
  if (!draft) return <Loading />;
  if (draft.sha256 !== doc.before_sha256) return <p className="state state-attention">El borrador cambió después de esta vista previa: revísala de nuevo.</p>;
  const diff = unifiedDiff(doc.path, draft.content, doc.content);
  return <>{diff ? <DiffBlock diff={diff} label={`Bloques regenerados en ${doc.path}`} /> : <p className="hint">Sin cambios.</p>}
    <details><summary>Contenido completo</summary><pre>{doc.content}</pre></details></>;
}

function OperationPanel({ conversation, op }: { conversation: Conversation; op: Operation }) {
  const { project, busy, operate, send } = useWorkspace();
  const base = `/projects/${project}/planning/${conversation.id}`;
  const preview = op.preview;
  const task = preview.first_task as { task_id?: string } | null;
  const phase = preview.phase as { code?: string } | null;
  const commit = op.result?.commit ? String(op.result.commit) : undefined;
  return <section className={op.status === "COMPLETED" ? "decision" : "decision decision-attention"} aria-labelledby="def-operation">
    <h2 id="def-operation">{op.status === "COMPLETED" ? "Proyecto creado" : op.status === "INTERRUPTED" ? "Creación interrumpida" : "Creando el proyecto"}</h2>
    <Fields items={[["Estado", <><Status value={op.status} /> · run <Link to={{ name: "run-short", run: op.run_id }} className="mono">{op.run_id.slice(0, 8)}</Link> <Status value={op.run_status} /></>],
      ["Commit raíz", commit ? <Hash value={commit} /> : <span className="muted">pendiente</span>], ["Vista previa", <Hash value={preview.preview_sha256} />]]} />
    {op.run_status === "RECOVERY_REQUIRED" && <p>El escritor se interrumpió. Confirma en el <Link to={{ name: "run-short", run: op.run_id }}>run</Link> que está detenido; después concilia aquí la misma intención (mismo commit).</p>}
    {op.status === "INTERRUPTED" && <AcceptReview conversation={conversation} base={base} preview={{ ...preview, resume_operation_id: op.id, expected_version: op.expected_version }} resume={op} />}
    {op.status === "COMPLETED" && <>
      <p>La fase <Link className="mono" to={{ name: "phase", project, phase: phase?.code ?? "P001" }}>{phase?.code ?? "P001"}</Link> está activa con sus documentos adoptados. Los documentos están en la <Link to={{ name: "docs", project }}>documentación</Link>.</p>
      {op.first_task_run ? <p>Primera tarea: <Link to={{ name: "run-short", run: op.first_task_run.run_id }} className="mono">{task?.task_id ?? "run"}</Link> <Status value={op.first_task_run.status} /></p>
        : task?.task_id && phase?.code && <>
          <p>Encola la primera tarea, <code>{task.task_id}</code>, con el plan regenerado de NEXT_STEPS. El planificador fija su contrato con la política del proyecto.</p>
          <button type="button" disabled={busy} onClick={() => void operate(() => send(jobRequest(`/projects/${project}/runs`, {
            task_id: task.task_id!, phase_id: phase.code!, text: preview.task_text ?? "",
          } satisfies S["RunCreate"])))}>Encolar primera tarea</button>
        </>}
    </>}
  </section>;
}

// --- planificación de la fase activa: /projects/:p/phases/:code/plan ---------------------------

export function PlanPage({ phase, conversation }: { phase: string; conversation?: string }) {
  const { project, busy, refresh, operate } = useWorkspace();
  const read = usePoll<S["PhaseRead"]>(`/projects/${project}/phases/${q(phase)}`, 5000, refresh);
  const list = usePoll<Summary[]>(`/projects/${project}/planning`, 4000, refresh);
  const [title, setTitle] = useState("");
  const data = read.data;
  if (read.missing) return <Empty title={`No hay ninguna fase ${phase} definida`}><p>Vuelve a <Link to={{ name: "phases", project }}>Fases</Link>.</p></Empty>;
  if (!data || !list.data) return read.error ?? list.error ? <Alert>{read.error ?? list.error}</Alert> : <Loading />;
  const mine = list.data.filter(c => c.kind === "phase_planning" && c.phase_id === data.id);
  const canPlan = data.status === "ACTIVE" && !(data.definition.tasks as string[]).length && !read.error;
  return <>
    <PageHeader title={`Planificar ${phase}`}>
      <p>El revisor propone NEXT_STEPS para la fase activa sin tareas. Se confirma desde la <Link to={{ name: "phase", project, phase }}>página de {phase}</Link>, con el diff y el hash exactos.</p>
    </PageHeader>
    <Stale error={read.error ?? list.error} />
    <div className="split">
      <nav className="panel split-list" aria-label="Conversaciones de planificación">
        <h2>Conversaciones</h2>
        {!mine.length ? <p className="hint">Aún no hay ninguna.</p> : <ul className="link-list">{mine.map(c => <li key={c.id}>
          <Link to={{ name: "plan", project, phase, conversation: c.id }} current={conversation === c.id}>
            <span className="link-title">{c.title}</span><span className="link-meta">{c.turns} turnos · {when(c.updated_at)}</span></Link></li>)}</ul>}
        <form onSubmit={e => { e.preventDefault(); if (!canPlan) return; void operate(async () => {
          const created = await createOnce<Conversation>(`/projects/${project}/planning`, { kind: "phase_planning", title: title.trim(), brief: null, phase_id: data.id } satisfies S["PlanningConversationCreate"]);
          setTitle(""); navigate({ name: "plan", project, phase, conversation: created.id });
        }); }}>
          <label>Nueva conversación<input value={title} maxLength={200} onChange={e => setTitle(e.target.value)} placeholder={`Plan de ${phase}`} /></label>
          <button className="button-quiet" disabled={busy || !title.trim() || !canPlan}>Crear conversación</button>
        </form>
        {(data.status !== "ACTIVE" || !!(data.definition.tasks as string[]).length) && <p className="hint">Solo se planifica la fase ACTIVE sin tareas. Las conversaciones anteriores conservan su historial.</p>}
      </nav>
      <div className="split-main">
        {conversation ? <PlanConversation key={conversation} id={conversation} phase={phase} writable={canPlan} />
          : <Empty title="Elige o crea una conversación"><p>Cada conversación conserva sus turnos y sus planes propuestos.</p></Empty>}
      </div>
    </div>
  </>;
}

function PlanConversation({ id, phase, writable }: { id: string; phase: string; writable: boolean }) {
  const { project, refresh } = useWorkspace();
  const base = `/projects/${project}/planning/${id}`;
  const read = usePoll<Conversation>(base, 1500, refresh);
  const c = read.data;
  if (read.missing) return <Empty title="No existe esa conversación"><p>Elige otra de la lista.</p></Empty>;
  if (!c) return read.error ? <Alert>{read.error}</Alert> : <Loading />;
  if (c.kind !== "phase_planning" || c.phase?.code !== phase) return <Empty title="Esta conversación no planifica esta fase" />;
  const plans = c.proposals.filter(p => p.kind === "plan");
  return <section className="panel" aria-labelledby="plan-title">
    <h2 id="plan-title">{c.title}</h2>
    <p className="hint">Desde la fase <Link className="mono" to={{ name: "phase", project, phase }}>{phase}</Link> <Status kind="phase" value={c.phase.status} /> · versión {c.version}</p>
    <Stale error={read.error} />
    <TurnList conversation={c} />
    {c.questions.length > 0 && <><h3>Preguntas del revisor</h3><ul>{c.questions.map(question => <li key={question.id}>{question.blocking ? <strong>Bloqueante: </strong> : null}{question.text}</li>)}</ul>
      <p className="hint">Respóndelas en un mensaje nuevo; las de la fase se registran en su página.</p></>}
    {c.pending.length > 0 && <><h3>Pendientes declarados</h3><ul>{c.pending.map(item => <li key={item}>{item}</li>)}</ul></>}
    <h3>Planes propuestos</h3>
    {!plans.length && <p className="hint">Sin planes todavía.</p>}
    {plans.map(p => <div key={p.id} className={p.status === "PROPOSED" ? "entry entry-open" : "entry"}>
      <p><strong>Plan #{p.number}</strong> <Tone value={PROPOSAL[p.status]} /> <span className="muted">· turno {p.turn_number} · <Hash value={p.proposal_sha256} /></span></p>
      <p>{p.reason}</p>
      <details><summary>Ver el plan</summary><article className="doc-reader"><MarkdownView source={p.content} path="docs/NEXT_STEPS.md" /></article>
        <details><summary>Texto exacto</summary><pre>{p.content}</pre></details></details>
      {writable && p.status === "PROPOSED" && <p><Link to={{ name: "phase", project, phase }}>Confirmar el plan de {phase}</Link></p>}
      <Dismiss conversation={c} proposal={p} base={base} />
    </div>)}
    {writable && <><h3>Nuevo mensaje</h3>
      <MessageForm conversation={c} path={`${base}/messages`} hint="El turno congela los documentos del contrato unificado con su hash, el resumen de la fase y los turnos anteriores. Un plan nuevo sustituye al pendiente." /></>}
  </section>;
}

// --- plan confirmado de la fase activa (en la página de la fase) ---------------------------------------------------

type Source = { kind: "proposal"; conversation: string; proposal: Proposal; title: string } | { kind: "text" };

/** Planes propuestos (PROPOSED) de las conversaciones de planificación de esta fase. */
function usePlans(project: string, phaseId: string, refresh: number) {
  const list = usePoll<Summary[]>(`/projects/${project}/planning`, 5000, refresh);
  const mine = useMemo(() => list.data?.filter(c => c.kind === "phase_planning" && c.phase_id === phaseId) ?? [], [list.data, phaseId]);
  const signature = mine.map(c => `${c.id}:${c.version}`).join("|");
  const [plans, setPlans] = useState<{ conversation: Summary; proposal: Proposal }[]>();
  useEffect(() => {
    let active = true;
    void Promise.all(mine.map(c => managed<Conversation>(`/projects/${project}/planning/${c.id}`)
      .then(detail => detail.proposals.filter(p => p.kind === "plan" && p.status === "PROPOSED").map(proposal => ({ conversation: c, proposal })))))
      .then(items => { if (active) setPlans(items.flat().reverse()); }).catch(() => { if (active) setPlans([]); });
    return () => { active = false; };
  }, [project, signature]);
  return { plans: list.data ? plans : undefined, error: list.error };
}

/** Instala NEXT_STEPS por texto o propuesta en la fase ACTIVE vacía que deja el cierre. */
export function PhasePlanPanel({ phase, stale = false }: { phase: S["PhaseRead"]; stale?: boolean }) {
  const { project, busy, refresh, operate, send } = useWorkspace();
  const { plans } = usePlans(project, phase.id, refresh);
  const [choice, setChoice] = useState("");
  const [text, setText] = useState("");
  const [preview, setPreview] = useState<{ body: S["PhasePlanInput"]; shown: S["PhasePlanPreviewRead"] }>();
  const [reason, setReason] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [run, setRun] = useState<string>();
  const [refused, setRefused] = useState<string>();
  const sources: [string, Source][] = [
    ...(plans ?? []).map(({ conversation, proposal }) => [`plan:${proposal.id}`, { kind: "proposal", conversation: conversation.id, proposal, title: conversation.title }] as [string, Source]),
    ["text", { kind: "text" }],
  ];
  const selected = choice || sources[0][0];
  const source = sources.find(([key]) => key === selected)?.[1];
  const body: S["PhasePlanInput"] = source?.kind === "proposal"
    ? { next_steps: null, plan_proposal: { conversation_id: source.conversation, proposal_id: source.proposal.id, proposal_sha256: source.proposal.proposal_sha256 } }
    : { next_steps: text, plan_proposal: null };
  const signature = JSON.stringify(body);
  useEffect(() => { setPreview(undefined); setConfirmed(false); }, [phase.version, signature]);
  useEffect(() => { setConfirmed(false); }, [preview?.shown.preview_sha256]);
  const pending = [...phase.operations].reverse().find(op => op.kind === "document_edit"
    && ["QUEUED", "INTENT", "INTERRUPTED"].includes(op.status)
    && (op.request.preview as { phase_plan?: unknown } | undefined)?.phase_plan);
  if (phase.status !== "ACTIVE" || (phase.definition.tasks as string[]).length) return null;
  return <section className="panel" id="phase-plan" aria-labelledby="phase-plan-title">
    <h2 id="phase-plan-title">Planificar {phase.code}</h2>
    <p className="hint">La fase está activa sin tareas. Confirmar el plan escribe NEXT_STEPS, actualiza STATE y crea una nueva versión de la definición en un commit.</p>
    {pending && !run && <p className="state state-attention">Hay un plan {pending.status === "INTERRUPTED" ? "interrumpido: confirma el escritor detenido en su run y revisa la misma intención para conciliarla" : "en curso"}. {pending.run_id && <Link to={{ name: "run-short", run: pending.run_id }}>Ver run</Link>}.</p>}
    {run ? <EditProgress run={run} title="Plan encolado" done={<p>Plan confirmado en {phase.code}. Las tareas ya figuran en su definición.</p>} /> : <>
      <fieldset disabled={busy || stale}>
        <legend>Plan NEXT_STEPS de {phase.code}</legend>
        {plans === undefined && <Loading>Buscando planes propuestos…</Loading>}
        {sources.map(([value, item]) => <label key={value} className="check"><input type="radio" name="plan-source" checked={selected === value} onChange={() => setChoice(value)} />
          {item.kind === "proposal" ? <span>Plan #{item.proposal.number} de «{item.title}» (turno {item.proposal.turn_number}, <Hash value={item.proposal.proposal_sha256} length={8} />)</span> : "Escribir el plan aquí"}</label>)}
        <p className="hint"><Link to={{ name: "plan", project, phase: phase.code }}>Planificar {phase.code} con el revisor</Link></p>
        {source?.kind === "text" && <label>Plan (Markdown con tareas <code>## {phase.code}-TNNN — título</code>)<textarea rows={10} value={text} maxLength={512 * 1024} onChange={e => { setChoice("text"); setText(e.target.value); }} /></label>}
        {source?.kind === "proposal" && <details><summary>Ver el plan elegido</summary><article className="doc-reader"><MarkdownView source={source.proposal.content} path="docs/NEXT_STEPS.md" /></article></details>}
      </fieldset>
      <button type="button" disabled={busy || stale || (!pending && (!source || (source.kind === "text" && !text.trim())))} onClick={() => void operate(async () => {
        setRefused(undefined); setPreview(undefined);
        try { setPreview({ body, shown: await managed<S["PhasePlanPreviewRead"]>(`/phases/${phase.id}/plan/preview`, body) }); }
        catch (error) { const diagnostic = conflictText(error); if (diagnostic) setRefused(diagnostic); else throw error; }
      })}>Revisar el plan</button>
      {refused && <p role="alert" className="state state-error">{refused}</p>}
      {preview && <div className="docs-review">
        <h3>Revisa el commit del plan</h3>
        {preview.shown.resume_operation_id && <p className="state state-attention">Se concilia exactamente el plan confirmado y su mismo commit.</p>}
        <ul className="docs-changes">{preview.shown.documents.map(document => <li key={document.path}><code className="path">{document.path}</code> · <Hash value={document.after_sha256} /></li>)}</ul>
        <DiffBlock diff={preview.shown.diff} label="Diff del plan" />
        <Fields items={[["Base", <Hash value={preview.shown.head} />], ["Vista previa", <Hash value={preview.shown.preview_sha256} />]]} />
        <label>Motivo<input value={reason} maxLength={2000} onChange={e => setReason(e.target.value)} /></label>
        <label className="check"><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />He revisado este diff exacto y confirmo el plan de {phase.code}.</label>
        <button type="button" disabled={busy || stale || !confirmed || !reason.trim()} onClick={() => void operate(async () => {
          const job = await send(jobRequest(`/phases/${phase.id}/plan`, {
            ...preview.body, preview_sha256: preview.shown.preview_sha256,
            resume_operation_id: preview.shown.resume_operation_id ?? null, reason, confirmed: true,
          } satisfies S["PhasePlanCreate"]));
          setRun(job.run_id);
        })}>Confirmar el plan y hacer commit</button>
      </div>}
    </>}
  </section>;
}

// --- importación: /projects/:p/import[/:c/*borrador] ---------------------------------------------

export function ImportPage({ conversation, path, flow = "project_import" }: { conversation?: string; path?: string; flow?: "project_import" | "onboarding" }) {
  const onboarding = flow === "onboarding";
  const routeName = onboarding ? "onboarding" : "import";
  const { project, refresh, busy, operate } = useWorkspace();
  const entry = usePoll<S["ImportEntryRead"]>(`/projects/${project}/${routeName}`, 3000, refresh);
  const mode = usePoll<S["ModeRead"]>(onboarding ? null : `/projects/${project}/mode`, 4000, refresh);
  const list = usePoll<Summary[]>(`/projects/${project}/planning`, 4000, refresh);
  const [title, setTitle] = useState("");
  if (!entry.data || !list.data) return entry.error ?? list.error ? <Alert>{entry.error ?? list.error}</Alert> : <Loading />;
  if (entry.data.activation_required || entry.data.refusal) return <>
    <PageHeader title="Importar proyecto"><p>Primero activa el modo gestionado: conserva y verifica el histórico del harness anterior antes de normalizar los documentos.</p></PageHeader>
    {entry.data.refusal && <p className="state state-attention">{entry.data.refusal}</p>}
    {entry.data.activation_preview && <Evidence title="Vista previa de la activación requerida" value={entry.data.activation_preview} />}
    <Migration project={project} mode={mode.data} />
  </>;
  const mine = list.data.filter(c => c.kind === flow);
  const op = entry.data.operation;
  const operationRoute = op?.preview.flow === "onboarding" ? "onboarding" : "import";
  if (op && operationRoute !== routeName) return <p>Este proyecto tiene una incorporación confirmada. <Link to={{ name: operationRoute, project, conversation: op.conversation_id }}>Ver su operación</Link>.</p>;
  const selected = conversation ?? op?.conversation_id;
  return <>
    <PageHeader title={onboarding ? "Incorporar repositorio" : "Importar proyecto"}><p>{onboarding ? "El revisor documenta el código de HEAD. Confirma los documentos y el perfil de tu composición para adoptar P001 con un commit documental. El código del proyecto no se ejecuta." : "El revisor propone fusiones y documentos. Los borradores se guardan en un área privada. Revisa el árbol completo y confirma su hash para normalizar el checkout en un único commit."}</p></PageHeader>
    <Stale error={entry.error ?? list.error} />
    {!op && <section className="panel">
      <ul className="link-list">{mine.map(c => <li key={c.id}><Link to={{ name: routeName, project, conversation: c.id }} current={selected === c.id}>{c.title} · {c.turns} turnos</Link></li>)}</ul>
      <form onSubmit={e => { e.preventDefault(); void operate(async () => {
        const created = await createOnce<Conversation>(`/projects/${project}/planning`, { kind: flow, title: title.trim(), brief: null, phase_id: null } satisfies S["PlanningConversationCreate"]);
        setTitle(""); navigate({ name: routeName, project, conversation: created.id });
      }); }}><label>Nueva conversación de {onboarding ? "incorporación" : "importación"}<input value={title} maxLength={200} onChange={e => setTitle(e.target.value)} /></label><button disabled={busy || !title.trim()}>Inventariar y crear conversación</button></form>
    </section>}
    {op && selected !== op.conversation_id ? <p>Hay una importación confirmada. <Link to={{ name: routeName, project, conversation: op.conversation_id }}>Ver su operación</Link>.</p>
      : selected && <ImportConversation key={selected} id={selected} path={path} operation={op} kind={flow} />}
  </>;
}

function ImportConversation({ id, path, operation, kind }: { id: string; path?: string; operation: S["ImportOperationRead"] | null; kind: "project_import" | "onboarding" }) {
  const { project, refresh } = useWorkspace();
  const base = `/projects/${project}/planning/${id}`;
  const read = usePoll<Conversation>(base, 1500, refresh);
  const c = read.data;
  const drafts = usePoll<Drafts>(c && !c.created ? `${base}/drafts` : null, 3000, refresh);
  if (!c) return read.error ? <Alert>{read.error}</Alert> : <Loading />;
  if (c.kind !== kind) return <Alert>Esta conversación pertenece a otro flujo de incorporación.</Alert>;
  return <div className="docs-layout">
    <DraftTree conversation={c} drafts={drafts.data} current={path} error={drafts.error} />
    <div className="docs-main"><Stale error={read.error} />
      {path && !c.created ? <DraftPage key={path} conversation={c} path={path} drafts={drafts.data} /> : <>
        <h2>{c.title}</h2><Evidence title="Origen congelado" value={c.source} />
        <section className="panel"><h3>Conversación</h3><TurnList conversation={c} />
          {!c.created && <MessageForm conversation={c} path={`${base}/messages`} hint="El revisor recibe el inventario y los borradores; no escribe en el checkout." />}
        </section>
        <Questions conversation={c} base={base} />
        {c.proposals.filter(p => p.status === "PROPOSED").map(p => <ProposalEntry key={p.id} conversation={c} proposal={p} base={base} drafts={drafts.data} />)}
        <ProposalHistory proposals={c.proposals.filter(p => p.status !== "PROPOSED")} />
        <ImportConfirmation base={base} conversation={c} operation={operation} />
      </>}
    </div>
  </div>;
}

function ImportConfirmation({ base, conversation, operation }: { base: string; conversation: Conversation; operation: S["ImportOperationRead"] | null }) {
  const { project, busy, operate, send } = useWorkspace();
  const [shown, setShown] = useState<S["ImportPreviewRead"]>();
  const [confirmed, setConfirmed] = useState(false);
  const [reason, setReason] = useState("");
  useEffect(() => { setShown(undefined); setConfirmed(false); }, [conversation.version, operation?.status]);
  const onboarding = conversation.kind === "onboarding";
  const endpoint = onboarding ? "onboarding" : "import";
  const completed = operation?.status === "COMPLETED";
  const queued = operation?.status === "QUEUED";
  return <section className="panel">
    <h3>{completed ? "Proyecto incorporado" : onboarding ? "Confirmar la incorporación" : "Confirmar la normalización"}</h3>
    {operation && <><p><Status value={operation.status} /> · <Link to={{ name: "run-short", run: operation.run_id }}>Ver run</Link> <Status value={operation.run_status} /></p>
      {operation.result && <Evidence title="Resultado de la importación" value={operation.result} />}
      {completed && <p>Documentos adoptados. <Link to={{ name: "phase", project, phase: String(operation.preview.phase.code) }}>Continuar en {String(operation.preview.phase.code)}</Link>.</p>}
      {operation.run_status === "RECOVERY_REQUIRED" && <p>Confirma el escritor detenido en el run y vuelve aquí para conciliar el mismo commit.</p>}
    </>}
    {!completed && !queued && <button disabled={busy} onClick={() => void operate(async () => {
      setShown(undefined); setConfirmed(false);
      setShown(await managed<S["ImportPreviewRead"]>(`${base}/${endpoint}/preview`, {}));
    })}>{operation ? "Revisar la intención para conciliarla" : "Revisar el árbol y el commit"}</button>}
    {shown && <div className="docs-review">
      <p>Fase que se adoptará: <strong>{String(shown.phase.code)}</strong>. Los originales sustituidos o retirados se conservan en el archivo.</p>
      <Fields items={[["Base", <Hash value={shown.head} />], ["Vista previa", <Hash value={shown.preview_sha256} />]]} />
      <Evidence title="Árbol documental completo, movimientos y conservación de originales" value={{ tree: shown.result_tree, moves: shown.moves, preserved: shown.preserved, foreign: shown.foreign, phase: shown.phase }} />
      {shown.warnings.length > 0 && <ul>{shown.warnings.map((warning, i) => <li key={i}>{warning}</li>)}</ul>}
      {onboarding && <>
        <Evidence title="Perfil detectado: propuesta para tu TOML local" value={shown.profile_proposal} />
        <Evidence title="Perfil de la composición que confirmas" value={shown.profile} />
        <p>Revisa comandos, rutas y límites. Para cambiarlos, edita el TOML local y selecciona la composición en Ajustes antes de volver a generar esta vista previa.</p>
        <Fields items={[["Hash del perfil", <Hash value={shown.profile_sha256 ?? ""} />]]} />
      </>}
      <DiffBlock diff={shown.diff} label="Cambios documentales" />
      <details><summary>Bytes exactos de cada cambio (base64 en binarios)</summary>{shown.documents.map(doc => <details key={String(doc.path)}><summary>{String(doc.path)} · {doc.content === null ? "retirado" : String(doc.after_sha256).slice(0, 12)}</summary><pre>{String(doc.content ?? "Archivo retirado; original conservado en el árbol mostrado.")}</pre></details>)}</details>
      <label>Motivo<input value={reason} maxLength={2000} onChange={e => setReason(e.target.value)} /></label>
      <label className="check"><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />He revisado este árbol, {onboarding && "el perfil de la composición, "}la fase y los originales conservados, y confirmo el hash {shown.preview_sha256.slice(0, 12)}.</label>
      <button disabled={busy || !confirmed || !reason.trim()} onClick={() => void operate(async () => {
        await send(jobRequest(`${base}/${endpoint}/confirm`, { preview_sha256: shown.preview_sha256, reason, confirmed: true,
          resume_operation_id: shown.resume_operation_id ?? null, expected_version: shown.expected_version ?? null,
          ...(onboarding ? { profile_sha256: shown.profile_sha256 } : {}) }));
        setShown(undefined); setConfirmed(false);
      })}>{operation ? "Conciliar el mismo commit" : "Confirmar y hacer commit documental"}</button>
    </div>}
  </section>;
}

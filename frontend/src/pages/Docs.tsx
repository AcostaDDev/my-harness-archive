import { useEffect, useMemo, useRef, useState } from "react";
import type { MouseEvent, ReactNode } from "react";
import { jobRequest, managed, ManagedError } from "../managed-api";
import type { S } from "../managed-api";
import { blockBody, renderMarkdown, splitBlocks } from "../markdown.ts";
import type { Segment } from "../markdown.ts";
import { prefersDark, renderDiagram } from "../mermaid-view.ts";
import { Link, navigate } from "../navigation";
import { Alert, Empty, Fields, Hash, Loading, PageHeader, Stale, Status, message, usePoll } from "../ui";
import type { Poll } from "../ui";
import { useWorkspace } from "../workspace";

// Documentación de un proyecto con contrato v2 (H6.2 E3): árbol, visor seguro y edición confirmada (D072 §6).
// Toda escritura es un job `document_edit` sobre el diff exacto mostrado; nada se escribe al teclear.

type DocsStatus = S["DocumentsStatusRead"];
type Tree = S["DocumentTreeRead"];
type Preview = S["DocumentEditPreviewRead"];
type PhaseView = { id: string; code: string; status: S["PhaseRead"]["status"] };
type Draft = { base: string | null; texts: string[]; run?: string };

const q = encodeURIComponent;
const KIND: Record<S["DocumentTreeEntryRead"]["kind"], string> = {
  phase: "Documento de fase", product: "Documento de producto", archive: "Archivo de fase", other: "Documento",
};

/** Regla del servidor (`Layout.editable`): README o Markdown bajo la carpeta de documentación, nunca el archivo. */
function editablePath(path: string, docs: string) {
  if (path === "README.md") return true;
  const parts = path.split("/");
  return path.endsWith(".md") && path.startsWith(`${docs}/`) && !path.startsWith(`${docs}/archive/`)
    && !parts.includes("..") && !parts.includes(".") && !parts.includes("");
}

/** Motivo por el que ahora no se puede editar desde la interfaz; undefined si se puede. */
function editBlocker(status: DocsStatus | undefined): string | undefined {
  if (!status) return "Cargando el estado de los documentos…";
  const phase = status.phase as PhaseView | null;
  if (status.git_error) return "No se pudo leer el checkout con Git.";
  if (!phase) return "Crea o importa una fase antes de editar documentos con el harness.";
  if (phase.status === "CHECKING" || phase.status === "CLOSING") return `La fase ${phase.code} está ${phase.status === "CHECKING" ? "en comprobación" : "cerrándose"}; espera a que termine.`;
  if (status.unresolved_intent) return "Una operación documental espera recuperación en su run.";
  if (status.uncommitted?.length) return "Hay cambios locales sin confirmar en el checkout: confírmalos o regenera sus bloques antes de editar aquí.";
  return undefined;
}

export function DocsPage({ path }: { path?: string }) {
  const { project, refresh } = useWorkspace();
  const info = usePoll<S["ManagedProjectRead"]>(`/projects/${project}`, 0);
  const v2 = info.data?.documents === "v2";
  const status = usePoll<DocsStatus>(v2 ? `/projects/${project}/documents` : null, 4000, refresh);
  const tree = usePoll<Tree>(v2 ? `/projects/${project}/documents/tree` : null, 10000, refresh);
  if (!info.data) return info.error ? <Alert>{info.error}</Alert> : <Loading />;
  if (!v2) return <>
    <PageHeader title="Documentación" />
    <Empty title="Este proyecto usa el contrato documental anterior">
      <p>El visor y la edición confirmada necesitan <code>documents = "v2"</code> (D072). Los documentos siguen en el checkout y en la exportación de cada fase.</p>
    </Empty>
  </>;
  return <div className="docs-layout">
    <DocsTree tree={tree.data} status={status.data} current={path} error={tree.error} />
    <div className="docs-main">
      {path ? <DocumentView key={path} path={path} status={status} tree={tree.data} />
        : <DocsOverview status={status} tree={tree.data} />}
    </div>
  </div>;
}

// --- árbol --------------------------------------------------------------------------------------

type Node = { name: string; path: string; children: Map<string, Node>; file?: S["DocumentTreeEntryRead"] };

function buildTree(files: S["DocumentTreeEntryRead"][]): Node {
  const root: Node = { name: "", path: "", children: new Map() };
  for (const file of files) {
    let node = root;
    file.path.split("/").forEach((part, index, parts) => {
      const path = parts.slice(0, index + 1).join("/");
      if (!node.children.has(part)) node.children.set(part, { name: part, path, children: new Map() });
      node = node.children.get(part)!;
      if (index === parts.length - 1) node.file = file;
    });
  }
  return root;
}

function DocsTree({ tree, status, current, error }: { tree?: Tree; status?: DocsStatus; current?: string; error?: string }) {
  const { project } = useWorkspace();
  const root = useMemo(() => tree ? buildTree(tree.files) : undefined, [tree]);
  const drift = new Set(status?.documents.filter(d => d.drift).map(d => d.path));
  const local = new Set(status?.uncommitted?.map(c => c.path));
  const missing = status?.documents.filter(d => !d.exists) ?? [];
  function branch(node: Node, depth: number): ReactNode {
    const entries = [...node.children.values()].sort((a, b) => Number(!!b.file && !b.children.size) - Number(!!a.file && !a.children.size) || a.name.localeCompare(b.name));
    return <ul className="docs-tree-list">{entries.map(child => child.file && !child.children.size
      ? <li key={child.path}><Link to={{ name: "docs", project, path: child.path }} current={child.path === current} className="docs-tree-file">
          <span className="docs-tree-name">{child.name}</span>
          {local.has(child.path) && <span className="docs-flag docs-flag-local" title="Cambios locales sin confirmar">sin confirmar</span>}
          {drift.has(child.path) && !local.has(child.path) && <span className="docs-flag docs-flag-drift" title="Difiere de la base adoptada por la fase">deriva</span>}
          {child.file.archived && <span className="docs-flag" title="Solo lectura">archivo</span>}
        </Link></li>
      : <li key={child.path}><details open={depth < 1 || (!!current && current.startsWith(`${child.path}/`)) || !child.path.includes("archive")}>
          <summary className="docs-tree-folder">{child.name}/</summary>{branch(child, depth + 1)}</details></li>)}</ul>;
  }
  return <nav className="docs-tree" aria-label="Documentos">
    <p className="docs-tree-title"><Link to={{ name: "docs", project }} current={!current}>Documentación</Link></p>
    {!root ? (error ? <Alert>{error}</Alert> : <Loading />) : branch(root, 0)}
    {missing.length > 0 && <div className="docs-tree-missing">
      <p className="hint">Faltan en el checkout:</p>
      <ul className="docs-tree-list">{missing.map(d => <li key={d.path}><Link to={{ name: "docs", project, path: d.path }} current={d.path === current} className="docs-tree-file">
        <span className="docs-tree-name muted">{d.path.split("/").pop()}</span><span className="docs-flag">falta</span></Link></li>)}</ul>
    </div>}
    {tree?.truncated && <p className="hint">Lista recortada a los primeros 2000 documentos.</p>}
    {!!tree?.skipped.length && <p className="hint" title={tree.skipped.join("\n")}>{tree.skipped.length} enlaces u objetos no regulares no se muestran.</p>}
  </nav>;
}

// --- resumen ------------------------------------------------------------------------------------

function DocsOverview({ status, tree }: { status: Poll<DocsStatus>; tree?: Tree }) {
  const { project } = useWorkspace();
  const s = status.data;
  const phase = s?.phase as PhaseView | null | undefined;
  // El panel de cambios locales desaparece con el commit; su resultado se sigue mostrando aquí.
  const [run, setRun] = useState<string>();
  return <>
    <PageHeader title="Documentación">
      <p>Los documentos viven en el checkout y Git es su historial. Editar aquí crea un commit del harness con el diff exacto que confirmes; los bloques gestionados y el archivo de fases no se editan.</p>
    </PageHeader>
    <Stale error={s ? status.error : undefined} />
    {!s ? (status.error ? <Alert>{status.error}</Alert> : <Loading />) : <>
      {s.git_error && <Alert>No se pudo leer el checkout con Git: {s.git_error}</Alert>}
      {s.unresolved_intent && <div className="decision decision-attention" role="status">
        <h2>Operación documental pendiente de recuperación</h2>
        <p>Una edición, exportación o transición registró su intención y no terminó. Recupérala desde su run antes de editar; se reutiliza el mismo commit.</p>
        {phase && <p><Link to={{ name: "phase", project, phase: phase.code }}>Ver la fase {phase.code}</Link></p>}
      </div>}
      {!!s.uncommitted?.length ? <LocalChanges status={s} onQueued={setRun} />
        : run && <section className="decision"><EditProgress run={run} /></section>}
      <Drift status={s} />
      {!!s.warnings.length && <div className="state state-attention" role="status"><p className="state-title">Presupuestos superados</p>
        <ul>{s.warnings.map(w => <li key={w}>{w}</li>)}</ul></div>}
      <section className="panel" aria-labelledby="docs-set">
        <h2 id="docs-set">Documentos del contrato {phase && <span className="count">fase {phase.code} · <Status value={phase.status} kind="phase" /></span>}</h2>
        <div className="table-scroll" role="region" aria-label="Documentos del contrato" tabIndex={0}>
          <table className="table">
            <thead><tr><th scope="col">Documento</th><th scope="col">Tipo</th><th scope="col">Estado</th><th scope="col">Bloques</th></tr></thead>
            <tbody>{s.documents.map(d => <tr key={d.path}>
              <td><Link to={{ name: "docs", project, path: d.path }}><code className="path">{d.path}</code></Link></td>
              <td>{d.kind === "phase" ? "Fase" : "Producto"}</td>
              <td>{d.error ? <span className="status status-danger" title={d.error}><span className="status-mark" aria-hidden="true" />Ilegible</span>
                : !d.exists ? <span className="status status-neutral"><span className="status-mark" aria-hidden="true" />Falta</span>
                : d.drift ? <span className="status status-attention" title="El contenido no coincide con la base que adoptó la fase"><span className="status-mark" aria-hidden="true" />Difiere de la base</span>
                : <span className="status status-ok"><span className="status-mark" aria-hidden="true" />Al día</span>}</td>
              <td>{d.blocks.length ? d.blocks.map(b => <code key={b} className="chip">{b}</code>) : <span className="muted">ninguno</span>}</td>
            </tr>)}</tbody>
          </table>
        </div>
        <p className="hint">Carpetas: {s.folders.map(f => <span key={f.path}><code className="chip">{f.path}/</code>{!f.exists && <span className="muted">(falta) </span>}</span>)}</p>
      </section>
      <section className="panel" aria-labelledby="docs-decisions">
        <h2 id="docs-decisions">Decisiones <span className="count">{s.decisions.length}</span></h2>
        {!s.decisions.length ? <Empty title="Todavía no hay decisiones registradas"><p>Cada decisión es un archivo <code>decisions/DNNN-titulo.md</code>; el índice de DECISIONS se regenera al confirmarla.</p></Empty>
          : <div className="table-scroll" role="region" aria-label="Decisiones" tabIndex={0}><table className="table">
            <thead><tr><th scope="col">Id</th><th scope="col" className="wide">Título</th><th scope="col">Estado</th><th scope="col">Fase</th><th scope="col">Fecha</th></tr></thead>
            <tbody>{s.decisions.map(d => <tr key={d.id}>
              <td><Link className="mono" to={{ name: "docs", project, path: `${tree?.docs ?? "docs"}/decisions/${d.file}` }}>{d.id}</Link></td>
              <td>{d.title ?? <span className="muted">sin título</span>}</td><td>{d.status ?? "—"}</td><td>{d.phase ?? "—"}</td><td>{d.date ?? "—"}</td>
            </tr>)}</tbody></table></div>}
      </section>
      <section className="panel" aria-labelledby="docs-archive">
        <h2 id="docs-archive">Archivo de fases</h2>
        {!s.archive.length ? <p className="hint">Ninguna fase archivada todavía. La transición de fase copia aquí STATE, NEXT_STEPS, la revisión y el resumen.</p>
          : <ul className="docs-archive">{s.archive.map(a => <li key={a.path}><code className="path">{a.path}/</code>{" "}
            {a.files.filter(f => f.endsWith(".md")).map(f => <Link key={f} className="chip" to={{ name: "docs", project, path: `${a.path}/${f}` }}>{f}</Link>)}</li>)}</ul>}
      </section>
      <NewDocument docs={tree?.docs ?? "docs"} existing={new Set(tree?.files.map(f => f.path))} blocked={editBlocker(s)} />
    </>}
  </>;
}

function NewDocument({ docs, existing, blocked }: { docs: string; existing: Set<string>; blocked?: string }) {
  const { project } = useWorkspace();
  const [name, setName] = useState("");
  const path = `${docs}/${name.trim().replace(/^\/+/, "")}`;
  const valid = name.trim() !== "" && editablePath(path, docs);
  return <section className="panel" aria-labelledby="docs-new">
    <h2 id="docs-new">Nuevo documento</h2>
    <p className="hint">Markdown bajo <code>{docs}/</code>, fuera de <code>archive/</code>. Una decisión va en <code>decisions/DNNN-titulo.md</code>.</p>
    <form className="docs-new" onSubmit={e => { e.preventDefault(); if (valid && !existing.has(path)) navigate({ name: "docs", project, path }); }}>
      <label>Ruta<span className="docs-prefix"><code>{docs}/</code><input value={name} onChange={e => setName(e.target.value)} placeholder="decisions/D002-titulo.md" maxLength={400} /></span></label>
      <button disabled={!valid || existing.has(path) || !!blocked}>Crear y editar</button>
    </form>
    {existing.has(path) && <p className="hint">Ese documento ya existe; ábrelo desde el árbol.</p>}
    {name.trim() && !valid && <p className="hint">La ruta debe terminar en <code>.md</code> y no puede entrar en el archivo ni salir de la carpeta.</p>}
    {blocked && <p className="hint">{blocked}</p>}
  </section>;
}

// --- deriva -------------------------------------------------------------------------------------

/** Documentos commiteados que difieren de la base adoptada por la fase: se resuelven adoptándolos en la fase. */
function Drift({ status }: { status: DocsStatus }) {
  const { project } = useWorkspace();
  const local = new Set(status.uncommitted?.map(c => c.path));
  const drift = status.documents.filter(d => d.drift && !local.has(d.path));
  const phase = status.phase as PhaseView | null;
  if (!drift.length || !phase) return null;
  return <div className="decision decision-attention" role="status">
    <h2>Documentos de fase distintos de su base</h2>
    <p>{drift.map(d => <code key={d.path} className="chip">{d.path}</code>)}</p>
    <p>Cambiaron fuera de un commit del harness. Hasta adoptarlos, el check de la fase no queda listo y la transición se bloquea. Revisa el contenido y adóptalo por hash en la fase, o reconcílialo con una tarea.</p>
    <p><Link to={{ name: "phase", project, phase: phase.code }}>Adoptar o reconciliar en {phase.code}</Link></p>
  </div>;
}

/** Cambios del editor de código sin commit: confirmar sus bytes exactos o regenerar los bloques que tocan. */
function LocalChanges({ status, onQueued }: { status: DocsStatus; onQueued: (run: string) => void }) {
  const { project, busy, operate } = useWorkspace();
  const [review, setReview] = useState<{ body: S["DocumentEditInput"]; preview: Preview }>();
  const [refused, setRefused] = useState<string>();
  const changes = status.uncommitted ?? [];
  const outside = changes.filter(c => !c.editable);
  async function load(regenerate: boolean) {
    const body: S["DocumentEditInput"] = { source: "worktree", regenerate_blocks: regenerate };
    setRefused(undefined); setReview(undefined);
    try { setReview({ body, preview: await managed<Preview>(`/projects/${project}/documents/edit/preview`, body) }); }
    catch (e) { if (e instanceof ManagedError && e.status === 409) setRefused(e.message); else throw e; }
  }
  const blockRefusal = refused?.includes("managed blocks are generated");
  return <section className="decision decision-attention" id="local-changes" aria-labelledby="local-changes-title">
    <h2 id="local-changes-title">Cambios locales sin confirmar</h2>
    <ul className="docs-changes">{changes.map(c => <li key={c.path}>
      {c.editable ? <Link to={{ name: "docs", project, path: c.path }}><code className="path">{c.path}</code></Link> : <code className="path">{c.path}</code>}
      {!c.editable && <span className="muted"> · fuera de los documentos editables</span>}</li>)}</ul>
    <p>Mientras existan, no arranca ninguna tarea y se bloquean el check, la exportación y la transición de fase: el ejecutor no debe recibir estos cambios en su diff.</p>
    {outside.length > 0 ? <p className="hint">Hay cambios fuera de los documentos editables (código u otros archivos). No se confirman desde aquí: haz su commit o descártalos en tu editor, y vuelve.</p> : <>
      <p className="hint">Confirmar hace un commit del harness con estos bytes exactos. Si tocaste un bloque gestionado, regenerar conserva tu prosa y devuelve el bloque a su contenido actual.</p>
      <div className="actions">
        <button type="button" disabled={busy} onClick={() => void operate(() => load(false))}>Revisar y confirmar</button>
        {blockRefusal && <button type="button" className="button-quiet" disabled={busy} onClick={() => void operate(() => load(true))}>Regenerar bloques</button>}
      </div>
    </>}
    {refused && <p role="alert" className="state state-error">{blockRefusal ? "Estos cambios editan un bloque gestionado, que genera el harness. Puedes regenerarlo y confirmar solo tu prosa." : refused}</p>}
    {review && <EditReview body={review.body} preview={review.preview} onCancel={() => setReview(undefined)} onQueued={onQueued} />}
  </section>;
}

// --- confirmación común -------------------------------------------------------------------------

function DiffBlock({ diff, label }: { diff: string; label: string }) {
  const lines = diff.replace(/\n$/, "").split("\n");
  return <pre className="diff" aria-label={label}>{lines.map((line, index) => {
    const kind = line.startsWith("+++") || line.startsWith("---") ? "file" : line.startsWith("@@") ? "hunk" : line.startsWith("+") ? "add" : line.startsWith("-") ? "del" : "";
    return <span key={index} className={kind ? `diff-${kind}` : undefined}>{line}{"\n"}</span>;
  })}</pre>;
}

/** Diff exacto, motivo y confirmación; encola `document_edit` con clave idempotente y sigue su run. */
function EditReview({ body, preview, onCancel, onQueued, done }: {
  body: S["DocumentEditInput"]; preview: Preview; onCancel: () => void; onQueued?: (run: string) => void; done?: ReactNode;
}) {
  const { project, busy, operate, send } = useWorkspace();
  const [reason, setReason] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [run, setRun] = useState<string>();
  const users = new Set(body.changes?.map(c => c.path) ?? []);
  if (run) return <EditProgress run={run} done={done} />;
  return <div className="docs-review">
    <h3>Revisa el commit</h3>
    {preview.resume_operation_id && <p className="state state-attention">Hay una edición interrumpida ({preview.resume_operation_id.slice(0, 8)}): se muestra y se reanuda exactamente la que se confirmó, con el mismo commit.</p>}
    <ul className="docs-changes">{preview.documents.map(d => <li key={d.path}>
      <code className="path">{d.path}</code>{" "}
      <span className="muted">{d.before_sha256 === null ? "nuevo" : <>de <Hash value={d.before_sha256} length={8} /></>} a <Hash value={d.after_sha256} length={8} />
        {body.source === "content" && !users.has(d.path) && " · índice regenerado por el harness"}</span></li>)}</ul>
    {!!preview.regenerated?.length && <div className="state state-attention">
      <p className="state-title">Se descarta de tus archivos locales</p>
      <p>El harness sustituye en el disco los bloques gestionados que editaste por su contenido actual. Tu prosa se conserva.</p>
      {preview.regenerated.map(r => <DiffBlock key={r.path} diff={r.diff} label={`Bloques descartados en ${r.path}`} />)}
    </div>}
    <DiffBlock diff={preview.diff} label="Diff del commit" />
    <Fields items={[["Base", <Hash value={preview.head} />], ["Vista previa", <Hash value={preview.preview_sha256} />]]} />
    <label>Motivo<input value={reason} maxLength={2000} onChange={e => { setReason(e.target.value); setConfirmed(false); }} placeholder="Qué cambia y por qué" /></label>
    <label className="check"><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />He revisado este diff exacto y confirmo su commit{preview.regenerated?.length ? " y la regeneración de los bloques" : ""}.</label>
    <div className="actions">
      <button type="button" disabled={busy || !confirmed || !reason.trim()} onClick={() => void operate(async () => {
        const job = await send(jobRequest(`/projects/${project}/documents/edit`, {
          ...body, preview_sha256: preview.preview_sha256, resume_operation_id: preview.resume_operation_id ?? null,
          reason, confirmed: true,
        } satisfies S["DocumentEditCreate"]));
        setRun(job.run_id); onQueued?.(job.run_id);
      })}>Confirmar y hacer commit</button>
      <button type="button" className="button-quiet" disabled={busy} onClick={onCancel}>Volver</button>
    </div>
  </div>;
}

const FINAL = new Set(["COMMITTED", "STOPPED", "FAILED", "ABORTED", "INTERRUPTED", "RECOVERY_REQUIRED"]);

function EditProgress({ run, done, onBack }: { run: string; done?: ReactNode; onBack?: () => void }) {
  const read = usePoll<S["ManagedRunRead"]>(`/runs/${run}`, 1500);
  const r = read.data;
  const finished = r && FINAL.has(r.status);
  const route = r && r.project_id ? { name: "run" as const, project: r.project_id, phase: r.phase_id, task: r.task_id, run: r.id } : undefined;
  return <div className="docs-review" role="status">
    <h3>Edición encolada</h3>
    <p>{r ? <Status value={r.status} /> : "Consultando…"} {route && <Link to={route} className="mono">Run {run.slice(0, 8)}</Link>}</p>
    {r?.status === "COMMITTED" && (done ?? <p>Commit hecho y hashes adoptados por la fase.</p>)}
    {finished && r?.status !== "COMMITTED" && <>
      <p className="state state-error">No se hizo el commit{r.history.stop ? ` (${r.history.stop.stage}: ${r.history.stop.reason})` : ""}. Si algo cambió después de la vista previa, no se sobrescribió nada; los detalles están en el run.</p>
      {onBack && <button type="button" className="button-quiet" onClick={onBack}>Volver al borrador</button>}
    </>}
  </div>;
}

// --- documento ----------------------------------------------------------------------------------

function DocumentView({ path, status, tree }: { path: string; status: Poll<DocsStatus>; tree?: Tree }) {
  const { project } = useWorkspace();
  const read = usePoll<S["DocumentRead"]>(`/projects/${project}/documents/content?path=${q(path)}`, 8000);
  const draftKey = `harness-doc-draft-v1:${project}:${path}`;
  const [editing, setEditing] = useState(() => !!loadDraft(draftKey));
  const s = status.data;
  const docs = tree?.docs ?? "docs";
  const doc = read.data;
  const entry = s?.documents.find(d => d.path === path);
  const local = s?.uncommitted?.some(c => c.path === path);
  const archived = path.startsWith(`${docs}/archive/`);
  const canEdit = editablePath(path, docs);
  const blocker = editBlocker(s);
  const name = path.split("/").pop()!;
  const kind = tree?.files.find(f => f.path === path)?.kind ?? (entry?.kind as S["DocumentTreeEntryRead"]["kind"] | undefined);
  if (read.missing && !editing) return <>
    <PageHeader title={name} code><p><code className="path">{path}</code></p></PageHeader>
    <Empty title="Este documento no existe en el checkout">
      {canEdit ? <><p>Puedes crearlo: se confirma como cualquier edición, con un commit del harness.</p>
        {blocker ? <p className="hint">{blocker}</p> : <button type="button" onClick={() => setEditing(true)}>Crear documento</button>}</>
        : <p>Solo se muestran README y Markdown bajo <code>{docs}/</code>. Vuelve a la <Link to={{ name: "docs", project }}>documentación</Link>.</p>}
    </Empty>
  </>;
  if (!doc && !read.missing) return read.error ? <Alert>{read.error}</Alert> : <Loading />;
  return <>
    <PageHeader title={name} code aside={!editing && doc?.editable && <button type="button" disabled={!!blocker} title={blocker} onClick={() => setEditing(true)}>Editar</button>}>
      <p><code className="path">{path}</code> · {kind ? KIND[kind] : "Documento"}{doc && <> · <Hash value={doc.sha256} /></>}</p>
    </PageHeader>
    <Stale error={doc ? read.error : undefined} />
    {archived && <p className="state state-neutral docs-readonly">Archivo de fase · solo lectura. Lo escribe el harness al pasar de fase y nunca se edita.</p>}
    {local && <p className="state state-attention" role="status">Este documento tiene cambios locales sin confirmar. Lo que ves es el disco, no el último commit. <Link to={{ name: "docs", project }}>Confirmarlos o regenerar</Link>.</p>}
    {entry?.drift && !local && <p className="state state-attention" role="status">Difiere de la base que adoptó la fase: el check no queda listo hasta adoptarlo. <Link to={{ name: "docs", project }}>Ver deriva</Link>.</p>}
    {entry?.error && <Alert>{entry.error}</Alert>}
    {editing ? <Editor path={path} doc={read.missing ? null : doc!} draftKey={draftKey} blocker={blocker} onClose={() => setEditing(false)} />
      : doc && <article className="doc-reader"><MarkdownView source={doc.content} path={path} /></article>}
  </>;
}

/** Markdown renderizado (markdown.ts) con navegación interna y diagramas aislados (mermaid-view.ts). */
export function MarkdownView({ source, path }: { source: string; path: string }) {
  const { project } = useWorkspace();
  const rendered = useMemo(() => renderMarkdown(source, { project, path }), [source, project, path]);
  const container = useRef<HTMLDivElement>(null);
  const [dark, setDark] = useState(prefersDark);
  useEffect(() => {
    const update = () => setDark(prefersDark());
    const observer = new MutationObserver(update);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    const media = window.matchMedia?.("(prefers-color-scheme: dark)");
    media?.addEventListener("change", update);
    return () => { observer.disconnect(); media?.removeEventListener("change", update); };
  }, []);
  useEffect(() => {
    const root = container.current;
    if (!root || !rendered.mermaid.length) return;
    let active = true;
    const urls: string[] = [];
    root.querySelectorAll<HTMLElement>("figure[data-mermaid]").forEach(figure => {
      const source = rendered.mermaid[Number(figure.dataset.mermaid)];
      figure.querySelector("img, .doc-mermaid-error")?.remove();
      figure.classList.add("doc-mermaid-loading");
      renderDiagram(source, dark).then(url => {
        if (!active) { URL.revokeObjectURL(url); return; }
        urls.push(url);
        const img = document.createElement("img");
        img.src = url; img.alt = "Diagrama Mermaid (el código fuente se muestra debajo)";
        figure.prepend(img);
      }).catch(error => {
        if (!active) return;
        const note = document.createElement("p");
        note.className = "doc-mermaid-error";
        note.textContent = `No se pudo dibujar el diagrama: ${message(error).slice(0, 300)}`;
        figure.prepend(note);
      }).finally(() => figure.classList.remove("doc-mermaid-loading"));
    });
    return () => { active = false; urls.forEach(url => URL.revokeObjectURL(url)); };
  }, [rendered, dark]);
  useEffect(() => {
    const id = decodeURIComponent(window.location.hash.slice(1));
    if (id.startsWith("doc-")) document.getElementById(id)?.scrollIntoView();
  }, [rendered]);
  function follow(event: MouseEvent<HTMLDivElement>) {
    const link = (event.target as HTMLElement).closest<HTMLAnchorElement>("a[data-internal]");
    if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    navigate(link.getAttribute("href")!);
  }
  return <>
    {rendered.error && <p className="state state-attention">Marcadores de bloque mal formados: {rendered.error}. Se muestran como texto.</p>}
    <div ref={container} className="doc-prose" onClick={follow} dangerouslySetInnerHTML={{ __html: rendered.html }} />
  </>;
}

// --- editor -------------------------------------------------------------------------------------

function loadDraft(key: string): Draft | undefined {
  try { return JSON.parse(sessionStorage.getItem(key) ?? "null") ?? undefined; } catch { return undefined; }
}
function saveDraft(key: string, draft?: Draft) {
  try { if (draft) sessionStorage.setItem(key, JSON.stringify(draft)); else sessionStorage.removeItem(key); } catch { /* sin borrador guardado */ }
}

/**
 * Prosa editable y bloques gestionados bloqueados. El borrador sobrevive a una recarga (sessionStorage) con su hash
 * base; la vista previa compara ese hash (CAS) y el commit lleva el diff exacto confirmado.
 */
function Editor({ path, doc, draftKey, blocker, onClose }: { path: string; doc: S["DocumentRead"] | null; draftKey: string; blocker?: string; onClose: () => void }) {
  const { project, busy, operate } = useWorkspace();
  const original = doc?.content ?? "";
  const { segments, error } = useMemo(() => splitBlocks(original), [original]);
  const [draft, setDraft] = useState<Draft>(() => loadDraft(draftKey) ?? { base: doc?.sha256 ?? null, texts: segments.map(s => s.text) });
  const [view, setView] = useState<"edit" | "preview">("edit");
  const [review, setReview] = useState<{ body: S["DocumentEditInput"]; preview: Preview }>();
  const [conflict, setConflict] = useState<string>();
  useEffect(() => { saveDraft(draftKey, draft); }, [draftKey, draft]);
  // El borrador se escribió sobre otros segmentos (otra versión): se conserva, pero no se puede reconstruir aquí.
  const shape = draft.texts.length === segments.length && segments.every((s, i) => s.kind === "prose" || draft.texts[i] === s.text);
  const content = draft.texts.join("");
  const changed = draft.base !== (doc?.sha256 ?? null) || content !== original;
  const stale = draft.base !== (doc?.sha256 ?? null);
  function discard() { saveDraft(draftKey); onClose(); }
  if (draft.run) return <EditProgress run={draft.run} onBack={() => setDraft({ ...draft, run: undefined })}
    done={<p>Commit hecho y hashes adoptados por la fase. <button type="button" className="button-quiet" onClick={discard}>Volver al documento</button></p>} />;
  if (error) return <Alert>No se puede editar con seguridad: {error}. Corrige los marcadores en tu editor; el harness rechaza cualquier cambio de un bloque gestionado.</Alert>;
  async function check() {
    setConflict(undefined); setReview(undefined);
    const body: S["DocumentEditInput"] = { source: "content", changes: [{ path, content, base_sha256: draft.base }], regenerate_blocks: false };
    try { setReview({ body, preview: await managed<Preview>(`/projects/${project}/documents/edit/preview`, body) }); }
    catch (e) { if (e instanceof ManagedError && e.status === 409) setConflict(e.message); else throw e; }
  }
  return <section className="docs-editor" aria-label={`Editar ${path}`}>
    {stale && <p className="state state-attention" role="status">El documento cambió desde que empezaste este borrador (base <Hash value={draft.base} length={8} />, ahora <Hash value={doc?.sha256} length={8} />). La vista previa lo rechazará: copia tu texto y descarta el borrador para partir de la versión actual.</p>}
    {!shape ? <Alert>El borrador guardado no encaja con los bloques actuales del documento. Descártalo para editar la versión actual.</Alert> : review ? null : <>
      <div className="docs-editor-tabs" role="tablist">
        <button type="button" role="tab" aria-selected={view === "edit"} className={view === "edit" ? "" : "button-quiet"} onClick={() => setView("edit")}>Escribir</button>
        <button type="button" role="tab" aria-selected={view === "preview"} className={view === "preview" ? "" : "button-quiet"} onClick={() => setView("preview")}>Vista previa</button>
      </div>
      {view === "preview" ? <article className="doc-reader"><MarkdownView source={content} path={path} /></article>
        : segments.map((segment, index) => segment.kind === "block"
          ? <LockedBlock key={index} segment={segment} />
          : <label key={index} className="docs-editor-prose"><span className="visually-hidden">Texto {index ? "tras el bloque" : "del documento"}</span>
            <textarea value={draft.texts[index]} spellCheck rows={Math.min(30, Math.max(segments.length > 1 ? 4 : 16, draft.texts[index].split("\n").length + 1))}
              onChange={e => { const texts = [...draft.texts]; texts[index] = e.target.value; setDraft({ ...draft, texts }); }} /></label>)}
    </>}
    {conflict && <p role="alert" className="state state-error">{conflict.includes("document_changed") ? "Conflicto: el documento cambió en el checkout desde que lo abriste. No se ha escrito nada." : conflict}</p>}
    {review ? <EditReview body={review.body} preview={review.preview} onCancel={() => setReview(undefined)}
        onQueued={run => setDraft({ ...draft, run })} />
      : <div className="actions">
        <button type="button" disabled={busy || !changed || !shape || !!blocker} title={blocker} onClick={() => void operate(check)}>Revisar cambios</button>
        <button type="button" className="button-quiet" disabled={busy} onClick={discard}>{changed ? "Descartar borrador" : "Cerrar editor"}</button>
        {blocker && <span className="hint">{blocker}</span>}
      </div>}
  </section>;
}

function LockedBlock({ segment }: { segment: Extract<Segment, { kind: "block" }> }) {
  return <details className="docs-locked">
    <summary><span className="docs-lock" aria-hidden="true" />Bloque gestionado <code>{segment.name}</code> · lo regenera el harness en cada commit y no se edita</summary>
    <pre>{blockBody(segment) || "Vacío: se rellena en el próximo commit del harness."}</pre>
  </details>;
}

import { useEffect, useRef, useState } from "react";
import { managed } from "./managed-api";
import type { S } from "./managed-api";

type Scope = S["PromptDetailRead"]["scope"];
type Detail = S["PromptDetailRead"];
const message = (e: unknown) => e instanceof Error ? e.message : String(e);

export function Prompts({ project }: { project: string }) {
  const [scope, setScope] = useState<Scope>("project");
  const [name, setName] = useState("execute-task");
  const [names, setNames] = useState<string[]>([]);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    managed<Detail[]>(`/projects/${project}/prompts`).then(items => {
      if (active) setNames(items.map(item => item.name));
    }).catch(e => { if (active) setError(message(e)); });
    return () => { active = false; };
  }, [project]);
  return <details className="prompt-editor"><summary>Prompts versionados</summary>
    <p>Jerarquía: base → perfil → proyecto. Activar afecta a intentos futuros de runs en curso o nuevos.
      Los runs detenidos conservan su catálogo al reanudar. Editar no concede permisos.</p>
    {error && <p role="alert" className="error">{error}</p>}
    <label>Ámbito<select value={scope} onChange={e => setScope(e.target.value as Scope)}>
      <option value="project">Proyecto</option><option value="profile">Perfil compartido</option><option value="core">Base global</option>
    </select></label>
    <label>Plantilla<select value={name} onChange={e => setName(e.target.value)}>{names.map(n => <option key={n}>{n}</option>)}</select></label>
    <Editor key={`${project}:${scope}:${name}`} project={project} scope={scope} name={name} />
  </details>;
}

function Editor({ project, scope, name }: { project: string; scope: Scope; name: string }) {
  const base = `/projects/${project}/prompts/${name}`;
  const [detail, setDetail] = useState<Detail>();
  const [selected, setSelected] = useState("");
  const [before, setBefore] = useState("");
  const [text, setText] = useState("");
  const [diff, setDiff] = useState("");
  const [reason, setReason] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const guard = useRef(false);
  const alive = useRef(true);
  useEffect(() => {
    alive.current = true;
    managed<Detail>(`${base}?scope=${scope}`).then(d => {
      if (alive.current) { setDetail(d); setSelected(d.effective.id); setBefore(d.effective.id); setText(d.effective.template); }
    }).catch(e => { if (alive.current) setError(message(e)); });
    return () => { alive.current = false; };
  }, [base, scope]);
  useEffect(() => { setConfirmed(false); setDiff(""); setStatus(""); }, [selected, before, text, detail?.generation]);
  const version = detail?.versions.find(v => v.id === selected);
  const inactiveFlow = ["bootstrap-project", "reconcile-phase", "close-phase"].includes(name);
  async function operate(action: () => Promise<void>) {
    if (guard.current) return;
    guard.current = true; setBusy(true); setError("");
    try { await action(); }
    catch (e) { if (alive.current) setError(message(e)); }
    finally { guard.current = false; if (alive.current) setBusy(false); }
  }
  async function reload() {
    const d = await managed<Detail>(`${base}?scope=${scope}`);
    if (alive.current) { setDetail(d); setConfirmed(false); }
    return d;
  }
  async function draft(rollback: boolean) {
    if (!detail) return;
    const body: S["PromptDraftCreate"] = { expected_version: detail.generation,
      ...(rollback ? { from_version: selected } : { template: text }) };
    const v = await managed<S["PromptVersionRead"]>(`${base}/versions?scope=${scope}`, body);
    await reload();
    if (alive.current) { setSelected(v.id); setText(v.template); }
  }
  return <section>
    {inactiveFlow && <p>Plantilla conservada para un flujo aún no implementado. Activarla no ejecuta bootstrap, reconciliación ni cierre.</p>}
    {scope !== "project" && <p>Este ámbito afecta a otros proyectos que hereden {scope === "core" ? "la base global" : "este perfil"}.</p>}
    {error && <p role="alert" className="error">{error}</p>}
    {status && <p role="status">{status}</p>}
    {detail && <>
      <p>Generación: {detail.generation} · Activa en este ámbito: {detail.active_id ?? "heredada"}</p>
      <p>Efectiva: {detail.effective.scope} · {detail.effective.id}</p>
      <p>Variables obligatorias: {detail.variables.map(v => `{{${v}}}`).join(", ")}. No se permiten otras variables.</p>
      <label>Versión seleccionada<select disabled={busy} value={selected} onChange={e => {
        const v = detail.versions.find(v => v.id === e.target.value)!; setSelected(v.id); setText(v.template);
      }}>{detail.versions.map(v => <option key={v.id} value={v.id}>{v.scope} · {v.id === detail.active_id ? "activa · " : ""}{v.id}</option>)}</select></label>
      <p>Procedencia: {version?.source} · SHA-256: {version?.sha256}</p>
      <label>Contenido del borrador<textarea rows={16} disabled={busy} value={text} onChange={e => setText(e.target.value)} maxLength={100000} /></label>
      <div className="pagination">
        <button disabled={busy} onClick={() => void operate(async () => {
          await managed<S["PromptValidationRead"]>(`${base}/validate`, { template: text } satisfies S["PromptValidateCreate"]);
          if (alive.current) setStatus("Variables válidas. No se ha guardado ni activado el contenido.");
        })}>Validar variables</button>
        <button disabled={busy} onClick={() => void operate(() => draft(false))}>Guardar nueva versión borrador</button>
        <button disabled={busy || !version} onClick={() => void operate(() => draft(true))}>Rollback: copiar a nueva versión</button>
        <button disabled={busy} onClick={() => void operate(async () => { await reload(); })}>Recargar versiones</button>
      </div>
      <label>Comparar desde<select disabled={busy} value={before} onChange={e => setBefore(e.target.value)}>
        {detail.versions.map(v => <option key={v.id} value={v.id}>{v.scope} · {v.id}</option>)}
      </select></label>
      <button disabled={busy || !version} onClick={() => void operate(async () => {
        const d = await managed<S["PromptDiffRead"]>(`${base}/diff?before=${encodeURIComponent(before)}&after=${encodeURIComponent(selected)}`);
        if (alive.current) setDiff(d.diff || "Sin diferencias de contenido.");
      })}>Comparar con versión seleccionada</button>
      {diff && <pre aria-label="Diff de versiones">{diff}</pre>}
      <label>Motivo de activación<input disabled={busy} value={reason} onChange={e => setReason(e.target.value)} maxLength={2000} /></label>
      <label className="check"><input type="checkbox" disabled={busy} checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />
        Confirmo activar esta versión guardada en el ámbito {scope}.</label>
      <button disabled={busy || !confirmed || !reason.trim() || version?.scope !== scope || version?.owner !== detail.owner || selected.startsWith("builtin-") || text !== version?.template}
        onClick={() => void operate(async () => {
          const body: S["PromptActivateCreate"] = { expected_version: detail.generation, version_id: selected, reason, confirmed: true };
          const d = await managed<Detail>(`${base}/activate?scope=${scope}`, body);
          if (alive.current) { setDetail(d); setConfirmed(false); setReason(""); }
        })}>Activar versión seleccionada</button>
      <details><summary>Historial de activaciones de este ámbito</summary><pre>{JSON.stringify(detail.activations, null, 2)}</pre></details>
    </>}
  </section>;
}

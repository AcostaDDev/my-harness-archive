import { useRef, useState } from "react";
import type { ReactNode } from "react";
import { managed } from "../managed-api";
import type { S } from "../managed-api";
import { Link, navigate } from "../navigation";
import { Alert, Empty, Evidence, Fields, Hash, Loading, PageHeader, Stale, message, usePoll, when } from "../ui";

// Registro de proyectos (H6.2 E2, D054/D076). El TOML del operador fija lo que se ejecuta; aquí solo
// se eligen raíz, composición y política. Cada cambio pasa por una vista previa ligada a su hash y versión,
// y la confianza en el checkout se confirma aparte.

// Los campos con valor por defecto del servidor son opcionales al enviar (la baja no los lleva).
type Defaulted = "tag_kind" | "documents" | "bootstrap_enabled";
type Change = Omit<S["RegistryChangeInput"], Defaulted> & Partial<Pick<S["RegistryChangeInput"], Defaulted>>;
type Draft = {
  project_id: string; root: string; composition: string; planning_mode: "agent" | "deterministic";
  executor_mode: "catalog" | "open"; executor_models: string; executor_efforts: string[]; max_revision_cycles: string;
  tag_kind: "lightweight" | "annotated"; v2: boolean; bootstrap_enabled: boolean; permission_authority: string;
};

const PLANNING = { agent: "La hace el revisor", deterministic: "Determinista, desde NEXT_STEPS" } as const;
const SELECTION = { catalog: "Solo el catálogo", open: "Libre (catálogo como referencia)" } as const;
const ACTIONS: Record<Change["action"], string> = { register: "Alta", update: "Cambio", retire: "Baja" };
const FIELDS: Record<string, string> = {
  id: "Id", root: "Raíz", repository_trusted: "Confianza (se confirma aparte)", composition: "Composición", policy: "Política",
  tag_kind: "Tag al cerrar fases", documents: "Documentos", bootstrap_enabled: "Bootstrap",
  permission_authority: "Techo de permisos", status: "Estado",
};

function emptyDraft(options: S["RegistryRead"]): Draft {
  return { project_id: "", root: options.roots.length === 1 ? `${options.roots[0]}/` : "", composition: options.compositions[0]?.name ?? "",
    planning_mode: "agent", executor_mode: "catalog", executor_models: "", executor_efforts: [], max_revision_cycles: "",
    tag_kind: "lightweight", v2: true, bootstrap_enabled: false, permission_authority: "" };
}

function draftOf(row: Record<string, unknown>): Draft {
  const policy = (row.policy ?? {}) as Record<string, unknown>;
  return { project_id: String(row.id), root: String(row.root), composition: String(row.composition),
    planning_mode: policy.planning_mode === "deterministic" ? "deterministic" : "agent",
    executor_mode: policy.executor_mode === "open" ? "open" : "catalog",
    executor_models: ((policy.executor_models ?? []) as string[]).join("\n"),
    executor_efforts: (policy.executor_efforts ?? []) as string[],
    max_revision_cycles: policy.max_revision_cycles == null ? "" : String(policy.max_revision_cycles),
    tag_kind: row.tag_kind === "annotated" ? "annotated" : "lightweight", v2: row.documents === "v2",
    bootstrap_enabled: row.bootstrap_enabled === true,
    permission_authority: row.permission_authority ? JSON.stringify(row.permission_authority, null, 2) : "" };
}

/** Cambio exacto que se envía; un techo de permisos que no es JSON se rechaza aquí, sin llamar al servidor. */
function changeOf(draft: Draft, action: Change["action"], expected: number): Change {
  if (action === "retire") return { action, project_id: draft.project_id, expected_version: expected };
  let authority: Change["permission_authority"] = null;
  if (draft.permission_authority.trim()) {
    try { authority = JSON.parse(draft.permission_authority); }
    catch { throw new Error("El techo de permisos no es JSON válido."); }
  }
  const cycles = draft.max_revision_cycles.trim();
  return {
    action, project_id: draft.project_id.trim(), expected_version: expected,
    ...(action === "register" ? { root: draft.root.trim() } : {}),
    composition: draft.composition,
    policy: { planning_mode: draft.planning_mode, executor_mode: draft.executor_mode,
      executor_models: draft.executor_models.split(/[\n,]/).map(v => v.trim()).filter(Boolean),
      executor_efforts: draft.executor_efforts, ...(cycles ? { max_revision_cycles: Number(cycles) } : {}) },
    tag_kind: draft.tag_kind, documents: draft.v2 ? "v2" : null, bootstrap_enabled: draft.bootstrap_enabled,
    permission_authority: authority,
  };
}

/** Una operación cada vez: un segundo clic mientras responde el servidor no envía nada. */
function useOperation() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const guard = useRef(false);
  async function run(action: () => Promise<unknown>) {
    if (guard.current) return;
    guard.current = true; setBusy(true); setError("");
    try { await action(); } catch (e) { setError(message(e)); } finally { guard.current = false; setBusy(false); }
  }
  return { busy, error, run, clear: () => setError("") };
}

const show = (value: unknown) => value === undefined || value === null ? <span className="muted">sin valor</span>
  : typeof value === "object" ? <pre className="inline-json">{JSON.stringify(value, null, 2)}</pre> : <code>{String(value)}</code>;

/** Vista previa y confirmación. `trust` solo existe en el alta: confirmación aparte de la del cambio. */
function Confirmation({ preview, busy, danger, onConfirm }: {
  preview: S["RegistryPreviewRead"]; busy: boolean; danger?: boolean;
  onConfirm: (trustRoot: string | null, reason: string) => void;
}) {
  const [trusted, setTrusted] = useState(false);
  const [reviewed, setReviewed] = useState(false);
  const [reason, setReason] = useState("");
  const blocked = preview.unfinished_jobs.length > 0;
  const creating = preview.action === "register";
  return <section className={`decision ${danger ? "decision-danger" : "decision-attention"}`} aria-labelledby="registry-preview">
    <h3 id="registry-preview">{ACTIONS[preview.action]} de <code>{preview.project_id}</code>: revisa antes de confirmar</h3>
    <p>Checkout <code className="path">{preview.row.root as string}</code></p>
    <Fields items={[
      ["Versión", preview.expected_version ? `${preview.expected_version} → ${preview.version}` : `Nueva, versión ${preview.version}`],
      ["Perfil", preview.profile],
      ["Vista previa", <Hash value={preview.preview_sha256} />],
    ]} />
    <div className="table-scroll" role="region" aria-label="Cambios" tabIndex={0}>
      <table className="table">
        {/* En el alta no hay valor anterior: solo la fila que se registrará. */}
        <thead><tr><th scope="col">Campo</th>{!creating && <th scope="col">Antes</th>}<th scope="col">{creating ? "Valor" : "Después"}</th></tr></thead>
        <tbody>{preview.changes.map(c => <tr key={c.field}><th scope="row">{FIELDS[c.field] ?? c.field}</th>{!creating && <td>{show(c.before)}</td>}<td>{show(c.after)}</td></tr>)}</tbody>
      </table>
    </div>
    {preview.versions && <Evidence title="Versiones que congelará cada trabajo" value={preview.versions} />}
    {blocked && <p className="state state-attention" role="status">El checkout tiene trabajos sin terminar ({preview.unfinished_jobs.join(", ")}). Espera a que terminen o concílialos: el servidor rechazará el cambio.</p>}
    {preview.trust_required && <fieldset className="trust">
      <legend>Confianza en el checkout</legend>
      <p>{preview.trust_statement}</p>
      <label className="check"><input type="checkbox" checked={trusted} onChange={e => setTrusted(e.target.checked)} />
        <span>Confío en <code className="path">{preview.row.root as string}</code></span></label>
    </fieldset>}
    <label>Motivo (opcional, queda en la auditoría)<input value={reason} maxLength={2000} onChange={e => setReason(e.target.value)} /></label>
    <label className="check"><input type="checkbox" checked={reviewed} onChange={e => setReviewed(e.target.checked)} />
      <span>He revisado {preview.action === "retire" ? "la baja; el historial se conserva y el id no se reutiliza" : "la fila, los cambios y las versiones congeladas"}.</span></label>
    <div className="actions">
      <button type="button" className={danger ? "button-danger" : undefined} disabled={busy || blocked || !reviewed || (preview.trust_required && !trusted)}
        onClick={() => onConfirm(preview.trust_required ? String(preview.row.root) : null, reason.trim())}>
        {preview.action === "register" ? "Registrar proyecto" : preview.action === "update" ? "Guardar cambios" : "Dar de baja"}</button>
    </div>
  </section>;
}

function DraftFields({ draft, options, action, onChange }: {
  draft: Draft; options: S["RegistryRead"]; action: "register" | "update"; onChange: (d: Draft) => void;
}) {
  const set = <K extends keyof Draft>(key: K, value: Draft[K]) => onChange({ ...draft, [key]: value });
  const composition = options.compositions.find(c => c.name === draft.composition);
  return <>
    {action === "register" && <div className="form-row">
      <label>Id del proyecto<input value={draft.project_id} onChange={e => set("project_id", e.target.value)} required maxLength={64}
        pattern="[a-z0-9][a-z0-9._\-]{0,63}" placeholder="mi-web" aria-describedby="id-hint" /></label>
      <label>Raíz del checkout<input value={draft.root} onChange={e => set("root", e.target.value)} required maxLength={4096}
        className="mono" spellCheck={false} aria-describedby="root-hint" /></label>
    </div>}
    {action === "register" && <p className="hint" id="id-hint">Minúsculas, números, punto, guion y guion bajo. No puede coincidir con un proyecto del TOML ni con uno dado de baja.</p>}
    {action === "register" && <p className="hint" id="root-hint">Ruta absoluta real, sin enlaces simbólicos, dentro de {options.roots.length === 1 ? "la raíz autorizada" : "una de las raíces autorizadas"}: {options.roots.map(r => <code key={r} className="chip path">{r}</code>)}</p>}
    <fieldset>
      <legend>Composición del operador</legend>
      <label>Composición<select value={draft.composition} onChange={e => set("composition", e.target.value)}>
        {options.compositions.map(c => <option key={c.name} value={c.name}>{c.name} · {c.profile}</option>)}
      </select></label>
      {composition && <Fields items={[
        ["Perfil", composition.profile],
        ["Ejecutables", composition.executables.map(name => <code key={name} className="chip">{name}</code>)],
        ["Entorno", composition.environment_keys.length ? composition.environment_keys.map(name => <code key={name} className="chip">{name}</code>) : <span className="muted">vacío</span>],
        ["Comandos", composition.authorize_profile_commands ? "Los del perfil" : "Solo los adicionales"],
        ...(composition.extra_commands.length ? [["Adicionales", composition.extra_commands.map(argv => <code key={argv.join(" ")} className="chip">{argv.join(" ")}</code>)] as [string, ReactNode]] : []),
      ]} />}
      <p className="hint">Rutas y valores del entorno quedan en el TOML; aquí solo se nombran.</p>
    </fieldset>
    <fieldset>
      <legend>Política de agentes</legend>
      <div className="form-row">
        <label>Planificación<select value={draft.planning_mode} onChange={e => set("planning_mode", e.target.value as Draft["planning_mode"])}>
          {Object.entries(PLANNING).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
        <label>Selección del ejecutor<select value={draft.executor_mode} onChange={e => set("executor_mode", e.target.value as Draft["executor_mode"])}>
          {Object.entries(SELECTION).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
        <label>Ciclos de revisión<input type="number" min={0} max={20} value={draft.max_revision_cycles} placeholder="3"
          onChange={e => set("max_revision_cycles", e.target.value)} /></label>
      </div>
      <label>Modelos del ejecutor ({options.executor_provider ?? "sin proveedor"}), uno por línea
        <textarea rows={2} value={draft.executor_models} onChange={e => set("executor_models", e.target.value)} spellCheck={false} /></label>
      <p className="legend">Esfuerzos del ejecutor</p>
      <div className="effort-list">{options.executor_effort_vocabulary.map(effort => <label key={effort} className="check">
        <input type="checkbox" checked={draft.executor_efforts.includes(effort)} onChange={e => set("executor_efforts",
          e.target.checked ? options.executor_effort_vocabulary.filter(v => v === effort || draft.executor_efforts.includes(v)) : draft.executor_efforts.filter(v => v !== effort))} />{effort}</label>)}</div>
      <p className="hint">El revisor ({options.reviewer_provider ?? "sin proveedor"}) planifica con el modelo y el esfuerzo que fija el TOML.</p>
    </fieldset>
    <fieldset>
      <legend>Proyecto</legend>
      <div className="form-row">
        <label>Tag al cerrar fases<select value={draft.tag_kind} onChange={e => set("tag_kind", e.target.value as Draft["tag_kind"])}>
          <option value="lightweight">Ligero</option><option value="annotated">Anotado</option></select></label>
      </div>
      <label className="check"><input type="checkbox" checked={draft.v2} onChange={e => set("v2", e.target.checked)} />
        <span>Documentos por fase (contrato v2)</span></label>
      <label className="check"><input type="checkbox" checked={draft.bootstrap_enabled} disabled={!options.bootstrap_enabled}
        onChange={e => set("bootstrap_enabled", e.target.checked)} />
        <span>Permitir crear el proyecto desde cero en esta carpeta{options.bootstrap_enabled ? "" : " (el operador no lo autoriza)"}</span></label>
      <label>Techo de permisos (JSON opcional: capa → tipo → objetivos)
        <textarea rows={3} value={draft.permission_authority} onChange={e => set("permission_authority", e.target.value)} spellCheck={false}
          placeholder={'{"global": {}, "project": {"tools": ["Read"]}, "contract": {}, "provider": {}}'} /></label>
    </fieldset>
  </>;
}

/** Formulario con vista previa: cualquier edición invalida la vista previa ya mostrada. */
function RegistryForm({ options, action, initial, expected, onApplied }: {
  options: S["RegistryRead"]; action: "register" | "update"; initial: Draft; expected: number;
  onApplied: (result: S["RegistryApplyRead"], change: Change) => void;
}) {
  const [draft, setDraft] = useState(initial);
  const [preview, setPreview] = useState<{ change: Change; data: S["RegistryPreviewRead"] }>();
  const generation = useRef(0);
  const op = useOperation();
  function edit(next: Draft) { generation.current += 1; setDraft(next); setPreview(undefined); op.clear(); }
  const ready = draft.composition && draft.executor_efforts.length && draft.executor_models.trim()
    && (action === "update" || (draft.project_id.trim() && draft.root.trim()));
  return <form onSubmit={e => {
    e.preventDefault();
    void op.run(async () => {
      const current = generation.current;
      const change = changeOf(draft, action, expected);
      const data = await managed<S["RegistryPreviewRead"]>("/registry/preview", change);
      if (current === generation.current) setPreview({ change, data });
    });
  }}>
    <DraftFields draft={draft} options={options} action={action} onChange={edit} />
    {op.error && <Alert>{op.error}</Alert>}
    <div className="actions"><button className={preview ? "button-quiet" : undefined} disabled={op.busy || !ready}>
      {preview ? "Volver a revisar" : action === "register" ? "Revisar alta" : "Revisar cambios"}</button></div>
    {preview && <Confirmation key={preview.data.preview_sha256} preview={preview.data} busy={op.busy} onConfirm={(trust, reason) => void op.run(async () => {
      onApplied(await managed<S["RegistryApplyRead"]>("/registry/apply", {
        change: preview.change, preview_sha256: preview.data.preview_sha256, trust_root: trust, reason: reason || null }), preview.change);
      setPreview(undefined);
    })} />}
  </form>;
}

export function RegisterPage() {
  const read = usePoll<S["RegistryRead"]>("/registry", 0);
  const options = read.data;
  return <>
    <PageHeader title="Registrar proyecto">
      <p>Da de alta una carpeta bajo las raíces que autoriza el operador. Elige una composición del TOML; los ejecutables y el entorno nunca se definen aquí.</p>
    </PageHeader>
    {!options ? read.error ? <Alert>No se pudo leer el registro: {read.error}</Alert> : <Loading />
      : !options.available ? <Empty title="Este servicio no admite registrar proyectos">
        <p>El registro desde la interfaz necesita una configuración <code>local-config-3</code> con <code>[registration]</code> y al menos una composición. {options.format ? <>El servicio usa <code>{options.format}</code>.</> : "El servicio arrancó sin configuración local."}</p>
        <p>Los proyectos del TOML siguen en la <Link to={{ name: "home" }}>lista de proyectos</Link>.</p>
      </Empty>
      : !options.roots.length ? <Empty title="No hay raíces autorizadas"><p>Añade rutas a <code>[registration].roots</code> en el TOML del operador y reinicia el servicio.</p></Empty>
      : <section className="panel" aria-labelledby="register-form"><h2 id="register-form">Alta</h2>
        <RegistryForm options={options} action="register" initial={emptyDraft(options)} expected={0}
          onApplied={(result, change) => navigate(change.documents === "v2" && change.bootstrap_enabled
            // Un proyecto v2 con bootstrap se crea en su página (H6.2 E4); los demás van al resumen.
            ? { name: "setup", project: result.project.id } : { name: "project", project: result.project.id })} />
      </section>}
  </>;
}

/** Ajustes de un proyecto registrado: versión, auditoría, cambio y baja. Los del TOML solo se consultan. */
export function RegistrySettings({ project }: { project: string }) {
  const [refresh, setRefresh] = useState(0);
  const options = usePoll<S["RegistryRead"]>("/registry", 0, refresh);
  const detail = usePoll<S["RegisteredProjectRead"]>(`/registry/projects/${project}`, 0, refresh);
  const retire = useOperation();
  const [retirement, setRetirement] = useState<{ change: Change; data: S["RegistryPreviewRead"] }>();
  const item = detail.data;
  if (!item || !options.data) return detail.error && !detail.missing ? <Alert>No se pudo leer el registro: {detail.error}</Alert> : <Loading />;
  const change: Change = { action: "retire", project_id: project, expected_version: item.version };
  return <section className="panel" aria-labelledby="settings-registry">
    <h2 id="settings-registry">Registro</h2>
    <Stale error={detail.error ?? options.error} />
    <Fields items={[
      ["Versión", `${item.version} · ${item.status === "ACTIVE" ? "activo" : "dado de baja"}`],
      ["Confianza", item.trust.confirmed && item.trust.root === item.root ? "Confirmada en el alta sobre esta raíz" : "sin confirmar"],
      ["Fila", <Hash value={item.row_sha256} />],
      ["Trabajos sin terminar", item.unfinished_jobs.length ? item.unfinished_jobs.join(", ") : "ninguno"],
    ]} />
    {!item.available && item.diagnostic && <p className="state state-attention">No se compone con el TOML actual: {item.diagnostic}</p>}
    <h3>Auditoría</h3>
    <div className="table-scroll" role="region" aria-label="Historial del registro" tabIndex={0}>
      <table className="table">
        <thead><tr><th scope="col" className="numeric">Versión</th><th scope="col">Acción</th><th scope="col">Quién</th><th scope="col">Cuándo</th><th scope="col">Fila</th><th scope="col">Motivo</th></tr></thead>
        <tbody>{item.history.map(e => <tr key={e.version}>
          <td className="numeric">{e.version}</td><td>{ACTIONS[e.action]}</td><td>{String(e.actor.user ?? e.actor.uid)}</td>
          <td>{when(e.recorded_at)}</td><td><Hash value={e.row_sha256} /></td><td>{e.reason ?? <span className="muted">sin motivo</span>}</td>
        </tr>)}</tbody>
      </table>
    </div>
    {item.status === "ACTIVE" && options.data.available && <>
      <details className="registry-edit">
        <summary><h3>Cambiar el registro</h3></summary>
        <p className="hint">La raíz no cambia. Cambiar la versión invalida los trabajos admitidos con la anterior; con trabajos sin terminar el cambio se rechaza.</p>
        <RegistryForm key={item.version} options={options.data} action="update" initial={draftOf(item.row)} expected={item.version}
          onApplied={() => setRefresh(n => n + 1)} />
      </details>
      <div className="decision decision-danger">
        <h3>Dar de baja</h3>
        <p>El proyecto deja de estar disponible y sus runs quedan solo en lectura. El historial se conserva y el id no se reutiliza; la carpeta queda libre para otro registro.</p>
        {retire.error && <Alert>{retire.error}</Alert>}
        {!retirement ? <button type="button" className="button-danger" disabled={retire.busy}
          onClick={() => void retire.run(async () => setRetirement({ change, data: await managed<S["RegistryPreviewRead"]>("/registry/preview", change) }))}>Revisar baja</button>
          : <Confirmation preview={retirement.data} busy={retire.busy} danger onConfirm={(_, reason) => void retire.run(async () => {
            await managed<S["RegistryApplyRead"]>("/registry/apply", { change: retirement.change, preview_sha256: retirement.data.preview_sha256, trust_root: null, reason: reason || null });
            navigate({ name: "home" });
          })} />}
      </div>
    </>}
  </section>;
}

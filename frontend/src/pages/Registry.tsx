import { useRef, useState } from "react";
import type { ReactNode } from "react";
import { managed, confirmOnce, readConfirmation } from "../managed-api";
import type { S } from "../managed-api";
import { Link, navigate } from "../navigation";
import { Alert, Empty, Evidence, Fields, Hash, Loading, PageHeader, Stale, message, usePoll, when } from "../ui";
import { useI18n } from "../Language";
import type { Language } from "../i18n.ts";
import { WorkLanguageChoice, WorkLanguagePreview } from "../WorkLanguage";

// Project registry (H6.2 E2, D054/D076). The operator TOML sets what runs; here only root, composition and
// policy are chosen. Every change goes through a preview bound to its hash and version, and trust in the
// checkout is confirmed separately.

// Fields with a server default are optional when submitting (removal does not carry them).
type Defaulted = "tag_kind" | "documents" | "bootstrap_enabled";
type Change = Omit<S["RegistryChangeInput"], Defaulted> & Partial<Pick<S["RegistryChangeInput"], Defaulted>>;
type Draft = {
  project_id: string; root: string; composition: string; planning_mode: "agent" | "deterministic";
  executor_mode: "catalog" | "open"; executor_models: string; executor_efforts: string[]; max_revision_cycles: string;
  tag_kind: "lightweight" | "annotated"; bootstrap_enabled: boolean; permission_authority: string;
  agent_mode: "inherited" | "project"; reviewer_preset: string; reviewer_model: string; reviewer_effort: string; executor_preset: string;
  // D167: chosen once on registration/creation; undefined shows (and sends) the global default.
  work_language?: Language;
};

/** Formats with per-project agent presets: v5 and v6 (which adds the work language). */
const PRESET_FORMATS = ["local-config-5", "local-config-6"];

const PLANNING = { agent: "La hace el revisor", deterministic: "Determinista, desde NEXT_STEPS" } as const;
const SELECTION = { catalog: "Solo el catálogo", open: "Libre (catálogo como referencia)" } as const;
const ACTIONS: Record<Change["action"], string> = { register: "Alta", update: "Cambio", retire: "Baja" };
const FIELDS: Record<string, string> = {
  id: "Id", root: "Raíz", repository_trusted: "Confianza (se confirma aparte)", composition: "Composición", policy: "Política",
  tag_kind: "Tag al cerrar fases", documents: "Documentos", bootstrap_enabled: "Bootstrap",
  permission_authority: "Techo de permisos", status: "Estado",
  agent_selection: "Agentes del proyecto",
};

function emptyDraft(options: S["RegistryRead"]): Draft {
  return { project_id: "", root: options.roots.length === 1 ? `${options.roots[0]}/` : "", composition: options.compositions[0]?.name ?? "",
    planning_mode: "agent", executor_mode: "catalog", executor_models: "", executor_efforts: [], max_revision_cycles: "",
    tag_kind: "lightweight", bootstrap_enabled: false, permission_authority: "",
    agent_mode: "inherited", reviewer_preset: "", reviewer_model: "", reviewer_effort: "", executor_preset: "" };
}

function draftOf(row: Record<string, unknown>): Draft {
  const policy = (row.policy ?? {}) as Record<string, unknown>;
  const selection = row.agent_selection as S["AgentSelectionInput"] | undefined;
  return { project_id: String(row.id), root: String(row.root), composition: String(row.composition),
    planning_mode: policy.planning_mode === "deterministic" ? "deterministic" : "agent",
    executor_mode: policy.executor_mode === "open" ? "open" : "catalog",
    executor_models: ((policy.executor_models ?? []) as string[]).join("\n"),
    executor_efforts: (policy.executor_efforts ?? []) as string[],
    max_revision_cycles: policy.max_revision_cycles == null ? "" : String(policy.max_revision_cycles),
    tag_kind: row.tag_kind === "annotated" ? "annotated" : "lightweight",
    bootstrap_enabled: row.bootstrap_enabled === true,
    permission_authority: row.permission_authority ? JSON.stringify(row.permission_authority, null, 2) : "",
    agent_mode: selection ? "project" : "inherited", reviewer_preset: selection?.reviewer.preset_id ?? "",
    reviewer_model: selection?.reviewer.model ?? "", reviewer_effort: selection?.reviewer.effort ?? "",
    executor_preset: selection?.executor.preset_id ?? "" };
}

/** Exact change to submit; a permission ceiling that is not JSON is rejected here, without calling the server. */
function changeOf(draft: Draft, action: Change["action"], expected: number, work?: Language): Change {
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
    ...(draft.agent_mode === "project" ? { agent_selection: {
      reviewer: { preset_id: draft.reviewer_preset, model: draft.reviewer_model, effort: draft.reviewer_effort },
      executor: { preset_id: draft.executor_preset } } } : {}),
    policy: { planning_mode: draft.planning_mode, executor_mode: draft.executor_mode,
      executor_models: draft.executor_models.split(/[\n,]/).map(v => v.trim()).filter(Boolean),
      executor_efforts: draft.executor_efforts, ...(cycles ? { max_revision_cycles: Number(cycles) } : {}) },
    tag_kind: draft.tag_kind, documents: "v2", bootstrap_enabled: draft.bootstrap_enabled,
    permission_authority: authority,
    ...(action === "register" && work ? { work_language: work } : {}),
  };
}

/** One operation at a time: a second click while the server responds sends nothing. */
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

/** Preview and confirmation. `trust` only exists on registration: a confirmation separate from the change. */
function Confirmation({ preview, busy, danger, onConfirm }: {
  preview: S["RegistryPreviewRead"]; busy: boolean; danger?: boolean;
  onConfirm: (trustRoot: string | null, reason: string) => void;
}) {
  const [trusted, setTrusted] = useState(false);
  const [reviewed, setReviewed] = useState(false);
  const [reason, setReason] = useState("");
  const blocked = preview.unfinished_jobs.length > 0 || (preview.configuration_blockers ?? []).length > 0;
  const creating = preview.action === "register";
  return <section className={`decision ${danger ? "decision-danger" : "decision-attention"}`} aria-labelledby="registry-preview">
    <h3 id="registry-preview">{ACTIONS[preview.action]} de <code>{preview.project_id}</code>: revisa antes de confirmar</h3>
    <p>Checkout <code className="path">{preview.row.root as string}</code></p>
    <Fields items={[
      ["Versión", preview.expected_version ? `${preview.expected_version} → ${preview.version}` : `Nueva, versión ${preview.version}`],
      ["Perfil", preview.profile],
      ["Vista previa", <Hash value={preview.preview_sha256} />],
    ]} />
    {preview.work_language && <WorkLanguagePreview preview={preview.work_language} />}
    <div className="table-scroll" role="region" aria-label="Cambios" tabIndex={0}>
      <table className="table">
        {/* A registration has no previous value: only the row that will be registered. */}
        <thead><tr><th scope="col">Campo</th>{!creating && <th scope="col">Antes</th>}<th scope="col">{creating ? "Valor" : "Después"}</th></tr></thead>
        <tbody>{preview.changes.map(c => <tr key={c.field}><th scope="row">{FIELDS[c.field] ?? c.field}</th>{!creating && <td>{show(c.before)}</td>}<td>{show(c.after)}</td></tr>)}</tbody>
      </table>
    </div>
    {preview.versions && <Evidence title="Versiones que congelará cada trabajo" value={preview.versions} />}
    {!!preview.unfinished_jobs.length && <p className="state state-attention" role="status">El checkout tiene trabajos sin terminar ({preview.unfinished_jobs.join(", ")}). Espera a que terminen o concílialos: el servidor rechazará el cambio.</p>}
    {!!(preview.configuration_blockers ?? []).length && <Alert>{(preview.configuration_blockers ?? []).join(". ")}</Alert>}
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
  draft: Draft; options: S["RegistryRead"]; action: "register" | "update" | "create"; onChange: (d: Draft) => void;
}) {
  const set = <K extends keyof Draft>(key: K, value: Draft[K]) => onChange({ ...draft, [key]: value });
  const { preferences } = useI18n();
  const composition = options.compositions.find(c => c.name === draft.composition);
  const reviewer = (options.agent_presets ?? []).find(p => p.id === draft.reviewer_preset && p.roles.includes("reviewer"));
  const executor = (options.agent_presets ?? []).find(p => p.id === draft.executor_preset && p.roles.includes("executor"));
  const projectAgents = draft.agent_mode === "project";
  const efforts = projectAgents ? executor?.efforts ?? [] : options.executor_effort_vocabulary;
  return <>
    {action === "register" && <div className="form-row">
      <label>Id del proyecto<input value={draft.project_id} onChange={e => set("project_id", e.target.value)} required maxLength={64}
        pattern="[a-z0-9][a-z0-9._\-]{0,63}" placeholder="mi-web" aria-describedby="id-hint" /></label>
      <label>Raíz del checkout<input value={draft.root} onChange={e => set("root", e.target.value)} required maxLength={4096}
        className="mono" spellCheck={false} aria-describedby="root-hint" /></label>
    </div>}
    {action === "register" && <p className="hint" id="id-hint">Minúsculas, números, punto, guion y guion bajo. No puede coincidir con un proyecto del TOML ni con uno dado de baja.</p>}
    {action === "register" && <p className="hint" id="root-hint">Ruta absoluta real, sin enlaces simbólicos, dentro de {options.roots.length === 1 ? "la raíz autorizada" : "una de las raíces autorizadas"}: {options.roots.map(r => <code key={r} className="chip path">{r}</code>)}</p>}
    {action !== "update" && <WorkLanguageChoice value={draft.work_language ?? preferences?.default_work_language}
      onChange={value => set("work_language", value)} />}
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
      {PRESET_FORMATS.includes(options.format ?? "") ? <>
        <label>Agentes<select value={draft.agent_mode} onChange={e => onChange({ ...draft,
          agent_mode: e.target.value as Draft["agent_mode"], reviewer_preset: "", reviewer_model: "", reviewer_effort: "",
          executor_preset: "", executor_models: "", executor_efforts: [], executor_mode: "catalog" })}>
          <option value="inherited">Heredar la pareja del servicio</option><option value="project">Elegir para este proyecto</option>
        </select></label>
        {!projectAgents && <p className="hint">Se heredan proveedor, modelo y esfuerzo del revisor y proveedor del ejecutor del servicio. La política del ejecutor se define abajo.</p>}
        {projectAgents && <>
          {!(options.agent_presets ?? []).some(p => p.roles.includes("reviewer")) || !(options.agent_presets ?? []).some(p => p.roles.includes("executor"))
            ? <Alert>Faltan presets compatibles para ambos roles. El operador debe declararlos en la configuración del servicio.</Alert> : null}
          <div className="form-row">
            <label>Preset del revisor<select required value={draft.reviewer_preset} onChange={e => onChange({ ...draft,
              reviewer_preset: e.target.value, reviewer_model: "", reviewer_effort: "" })}>
              <option value="">Elige proveedor y preset</option>
              {(options.agent_presets ?? []).filter(p => p.roles.includes("reviewer")).map(p => <option key={p.id} value={p.id}>{p.provider} · {p.id}</option>)}
            </select></label>
            <label>Modelo del revisor<select required value={draft.reviewer_model} onChange={e => set("reviewer_model", e.target.value)}>
              <option value="">Elige modelo</option>{reviewer?.models.map(model => <option key={model} value={model}>{model}</option>)}
            </select></label>
            <label>Esfuerzo del revisor<select required value={draft.reviewer_effort} onChange={e => set("reviewer_effort", e.target.value)}>
              <option value="">Elige esfuerzo</option>{reviewer?.efforts.map(effort => <option key={effort} value={effort}>{effort}</option>)}
            </select></label>
          </div>
          <label>Preset del ejecutor<select required value={draft.executor_preset} onChange={e => onChange({ ...draft,
            executor_preset: e.target.value, executor_models: "", executor_efforts: [], executor_mode: "catalog" })}>
            <option value="">Elige proveedor y preset</option>
            {(options.agent_presets ?? []).filter(p => p.roles.includes("executor")).map(p => <option key={p.id} value={p.id}>{p.provider} · {p.id}</option>)}
          </select></label>
          {executor && <p className="hint">Modelos admisibles como catálogo: {executor.models.join(", ")}. {executor.allow_open_executor ? "Admite modo libre." : "Solo admite catálogo."}</p>}
          <p className="hint">El revisor decidirá el modelo y esfuerzo concretos del ejecutor, con motivo, en cada tarea y revisión. Al guardar se invalidan los planes aún no aceptados.</p>
        </>}
      </> : <p className="hint">Cambiar proveedores por proyecto requiere local-config-5/6 y presets del operador. Esta configuración conserva la pareja del servicio.</p>}
      <div className="form-row">
        <label>Planificación<select value={draft.planning_mode} onChange={e => set("planning_mode", e.target.value as Draft["planning_mode"])}>
          {Object.entries(PLANNING).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
        <label>Selección del ejecutor<select value={draft.executor_mode} onChange={e => set("executor_mode", e.target.value as Draft["executor_mode"])}>
          {Object.entries(SELECTION).map(([value, label]) => <option key={value} value={value} disabled={value === "open" && projectAgents && !executor?.allow_open_executor}>{label}</option>)}</select></label>
        <label>Ciclos de revisión<input type="number" min={0} max={20} value={draft.max_revision_cycles} placeholder="3"
          onChange={e => set("max_revision_cycles", e.target.value)} /></label>
      </div>
      <label>Catálogo de modelos del ejecutor ({projectAgents ? executor?.provider ?? "elige preset" : options.executor_provider ?? "sin proveedor"}), uno por línea
        <textarea rows={2} value={draft.executor_models} onChange={e => set("executor_models", e.target.value)} spellCheck={false} /></label>
      <p className="legend">Esfuerzos del ejecutor</p>
      <div className="effort-list">{efforts.map(effort => <label key={effort} className="check">
        <input type="checkbox" checked={draft.executor_efforts.includes(effort)} onChange={e => set("executor_efforts",
          e.target.checked ? efforts.filter(v => v === effort || draft.executor_efforts.includes(v)) : draft.executor_efforts.filter(v => v !== effort))} />{effort}</label>)}</div>
      {!projectAgents && <p className="hint">El revisor ({options.reviewer_provider ?? "sin proveedor"}) planifica con el modelo y el esfuerzo que fija el TOML.</p>}
    </fieldset>
    <fieldset>
      <legend>Proyecto</legend>
      <div className="form-row">
        <label>Tag al cerrar fases<select value={draft.tag_kind} onChange={e => set("tag_kind", e.target.value as Draft["tag_kind"])}>
          <option value="lightweight">Ligero</option><option value="annotated">Anotado</option></select></label>
      </div>
      <p className="hint">Todos los proyectos usan el contrato documental unificado: instrucciones, diagramas, flujos y archivo por fase.</p>
      {action !== "create" && <label className="check"><input type="checkbox" checked={draft.bootstrap_enabled} disabled={!options.bootstrap_enabled}
        onChange={e => set("bootstrap_enabled", e.target.checked)} />
        <span>Permitir crear el proyecto desde cero en esta carpeta{options.bootstrap_enabled ? "" : " (el operador no lo autoriza)"}</span></label>}
      <label>Techo de permisos (JSON opcional: capa → tipo → objetivos)
        <textarea rows={3} value={draft.permission_authority} onChange={e => set("permission_authority", e.target.value)} spellCheck={false}
          placeholder={'{"global": {}, "project": {"tools": ["Read"]}, "contract": {}, "provider": {}}'} /></label>
    </fieldset>
  </>;
}

/** Form with preview: any edit invalidates the preview already shown. */
function RegistryForm({ options, action, initial, expected, onApplied }: {
  options: S["RegistryRead"]; action: "register" | "update"; initial: Draft; expected: number;
  onApplied: (result: S["RegistryApplyRead"], change: Change) => void;
}) {
  const [draft, setDraft] = useState(initial);
  const [preview, setPreview] = useState<{ change: Change; data: S["RegistryPreviewRead"] }>();
  const generation = useRef(0);
  const op = useOperation();
  const { preferences } = useI18n();
  const work = draft.work_language ?? preferences?.default_work_language;
  function edit(next: Draft) { generation.current += 1; setDraft(next); setPreview(undefined); op.clear(); }
  const ready = draft.composition && draft.executor_efforts.length && draft.executor_models.trim()
    && (action === "update" || (draft.project_id.trim() && draft.root.trim() && work));
  return <form onSubmit={e => {
    e.preventDefault();
    void op.run(async () => {
      const current = generation.current;
      const change = changeOf(draft, action, expected, work);
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

function CreationRootPanel({ root, refresh }: { root: S["CreationRootRead"]; refresh: () => void }) {
  const [path, setPath] = useState("");
  const [preview, setPreview] = useState<{ change: S["CreationRootChangeInput"]; data: S["CreationRootPreviewRead"] }>();
  const [accepted, setAccepted] = useState(false);
  const generation = useRef(0);
  const op = useOperation();
  return <section className="panel" aria-labelledby="creation-root">
    <h2 id="creation-root">Carpeta de proyectos</h2>
    <p>{root.permission_statement} La elección se guarda para los siguientes proyectos; cada creación muestra su destino.</p>
    <Fields items={[["Carpeta vigente", root.status === "ACTIVE" ? <code className="path">{root.path}</code> : "Sin selección"],
      ["Revisión", root.version]]} />
    {!root.available ? <p>{root.diagnostic}</p> : <form onSubmit={e => {
      e.preventDefault();
      void op.run(async () => {
        const current = generation.current;
        const change: S["CreationRootChangeInput"] = { action: "select", expected_version: root.version, path };
        const data = await managed<S["CreationRootPreviewRead"]>("/project-creation-root/preview", change);
        if (current === generation.current) { setPreview({ change, data }); setAccepted(false); }
      });
    }}>
      <label>Ruta absoluta de la carpeta padre<input value={path} maxLength={4096} required className="mono" spellCheck={false}
        onChange={e => { generation.current++; setPath(e.target.value); setPreview(undefined); setAccepted(false); }} /></label>
      <p className="hint">Debe existir, ser accesible y estar fuera de repositorios. Escríbela explícitamente; no se buscan ubicaciones.</p>
      <div className="actions">
        <button disabled={op.busy || !path.trim()}>Revisar carpeta</button>
        {root.status === "ACTIVE" && <button type="button" className="button-quiet" disabled={op.busy} onClick={() => void op.run(async () => {
          const change: S["CreationRootChangeInput"] = { action: "retire", expected_version: root.version };
          setPreview({ change, data: await managed("/project-creation-root/preview", change) }); setAccepted(false);
        })}>Revisar retirada</button>}
      </div>
      {preview && <div className="decision decision-attention">
        <h3>{preview.change.action === "select" ? "Guardar carpeta" : "Retirar carpeta"}</h3>
        {preview.change.action === "select" ? <p className="path"><code>{preview.data.root.path}</code></p>
          : <p>Se detienen nuevas creaciones pendientes. Los proyectos registrados y las carpetas se conservan.</p>}
        <label className="check"><input type="checkbox" checked={accepted} onChange={e => setAccepted(e.target.checked)} />
          <span>{preview.change.action === "select" ? "Autorizo al servicio a crear hijos nuevos en esta ruta exacta." : "He revisado la retirada."}</span></label>
        <button type="button" disabled={op.busy || !accepted} onClick={() => void op.run(async () => {
          await confirmOnce("/project-creation-root/apply", { change: preview.change, preview_sha256: preview.data.preview_sha256,
            confirm_path: preview.data.root.path });
          setPreview(undefined); refresh();
        })}>{preview.change.action === "select" ? "Guardar carpeta" : "Retirar carpeta"}</button>
      </div>}
    </form>}
    {op.error && <Alert>{op.error}</Alert>}
    {!!root.history.length && <Evidence title="Historial de la carpeta" value={root.history} />}
  </section>;
}

function CreationOperation({ initial, rootVersion, editable, refresh }: {
  initial: S["CreationOperationRead"]; rootVersion: number; editable: boolean; refresh: () => void;
}) {
  const [operation, setOperation] = useState(initial);
  const [preview, setPreview] = useState<{ change: S["CreationResumeInput"]; data: S["CreationResumePreviewRead"] }>();
  const op = useOperation();
  function saved(value: S["CreationOperationRead"]) { setOperation(value); setPreview(undefined); refresh(); }
  return <article className="decision decision-attention">
    <h3><code>{operation.project_id}</code> · {operation.status}</h3>
    <p><code className="path">{operation.target}</code></p>
    <p>Operación <code>{operation.id}</code> · versión {operation.version}</p>
    {operation.diagnostic && <p role="status">{operation.diagnostic}</p>}
    {operation.reserved && operation.status !== "REGISTERED" && <p>El destino queda reservado; se conservan sus bytes.</p>}
    {editable && (operation.status === "REGISTERED" ? <Link to={{ name: "setup", project: operation.project_id }}>Continuar con la definición</Link>
      : (operation.status !== "CANCELLED" || operation.reserved) && <div className="actions">
        {operation.status !== "RECOVERY_REQUIRED" && operation.status !== "CANCELLED" && <button type="button" disabled={op.busy} onClick={() => void op.run(async () => {
          const change = { expected_version: operation.version, root_version: rootVersion };
          setPreview({ change, data: await managed(`/project-creations/${operation.id}/resume/preview`, change) });
        })}>Revisar reanudación</button>}
        <button type="button" className="button-quiet" disabled={op.busy} onClick={() => void op.run(async () => {
          saved(await confirmOnce(`/project-creations/${operation.id}/cancel`, {
            expected_version: operation.version, intent_sha256: operation.intent_sha256 }));
        })}>{operation.status === "CANCELLED" ? "Volver a comprobar ausencia" : "Cancelar futuros efectos"}</button>
      </div>)}
    {preview && <div className="decision">
      <p>Reanudar la misma operación en <code className="path">{preview.data.target}</code> con revisión de carpeta {rootVersion}.</p>
      <button type="button" disabled={op.busy} onClick={() => void op.run(async () => {
        saved(await confirmOnce(`/project-creations/${operation.id}/resume/confirm`, {
          change: preview.change, preview_sha256: preview.data.preview_sha256 }));
      })}>Confirmar reanudación</button>
    </div>}
    {op.error && <Alert>{op.error}</Alert>}
    <Evidence title="Intención e historial" value={operation} />
  </article>;
}

function NewDirectoryForm({ options, root, refresh }: {
  options: S["RegistryRead"]; root: S["CreationRootRead"]; refresh: () => void;
}) {
  const [draft, setDraft] = useState(() => emptyDraft(options));
  const [name, setName] = useState("");
  const [preview, setPreview] = useState<{ change: S["CreationInput"]; data: S["CreationPreviewRead"] }>();
  const [trusted, setTrusted] = useState(false);
  const generation = useRef(0);
  const op = useOperation();
  const { preferences } = useI18n();
  const work = draft.work_language ?? preferences?.default_work_language;
  function invalidate() { generation.current++; setPreview(undefined); setTrusted(false); }
  const ready = draft.project_id.trim() && name && draft.composition && draft.executor_models.trim() && draft.executor_efforts.length && work;
  return <section className="panel" aria-labelledby="new-directory"><h2 id="new-directory">Crear carpeta nueva</h2>
    <form onSubmit={e => { e.preventDefault(); void op.run(async () => {
      const current = generation.current;
      const fields = changeOf(draft, "register", 0);
      const change: S["CreationInput"] = { project_id: fields.project_id, directory_name: name, root_version: root.version,
        composition: fields.composition!, policy: fields.policy!, tag_kind: draft.tag_kind, documents: "v2",
        permission_authority: fields.permission_authority, agent_selection: fields.agent_selection, work_language: work! };
      const data = await managed<S["CreationPreviewRead"]>("/project-creations/preview", change);
      if (current === generation.current) setPreview({ change, data });
    }); }}>
      <div className="form-row">
        <label>Id del proyecto<input value={draft.project_id} required maxLength={64} pattern="[a-z0-9][a-z0-9._\-]{0,63}"
          onChange={e => { invalidate(); setDraft({ ...draft, project_id: e.target.value }); }} /></label>
        <label>Nombre de la carpeta hija<input value={name} required maxLength={64} pattern="[a-z0-9][a-z0-9._\-]{0,63}"
          onChange={e => { invalidate(); setName(e.target.value); }} /></label>
      </div>
      <p>Destino: <code className="path">{root.path}/{name || "…"}</code></p>
      <p className="hint">Solo una carpeta nueva; un destino existente, incluso vacío, se rechaza.</p>
      <DraftFields draft={draft} options={options} action="create" onChange={next => { invalidate(); setDraft(next); }} />
      <button disabled={op.busy || !ready}>Revisar creación</button>
      {preview && <div className="decision decision-attention">
        <h3>Crear <code>{preview.change.project_id}</code></h3>
        <p><code className="path">{preview.data.target}</code></p>
        <Fields items={[["Perfil", preview.data.profile], ["Revisión de carpeta", root.version]]} />
        <WorkLanguagePreview preview={preview.data.work_language} />
        <Fields items={[["Revisor", `${preview.data.agents.reviewer.provider} · ${preview.data.agents.reviewer.model} · ${preview.data.agents.reviewer.effort}`],
          ["Ejecutor", `${preview.data.agents.executor.provider} · selección del revisor`]]} />
        <p>Se creará y registrará la carpeta. Después podrás iniciar la definición documental con su revisor.</p>
        <p>{preview.data.trust_statement}</p>
        <Evidence title="Composición y versiones confirmadas" value={preview.data} />
        <label className="check"><input type="checkbox" checked={trusted} onChange={e => setTrusted(e.target.checked)} />
          <span>He revisado la composición y confío en el nuevo checkout <code className="path">{preview.data.target}</code>.</span></label>
        <button type="button" disabled={op.busy || !trusted} onClick={() => void op.run(async () => {
          const result = await confirmOnce<S["CreationOperationRead"]>("/project-creations/confirm", {
            change: preview.change, preview_sha256: preview.data.preview_sha256, trust_root: preview.data.target });
          setPreview(undefined); refresh();
          if (result.status === "REGISTERED") navigate({ name: "setup", project: result.project_id });
        })}>Crear y registrar</button>
      </div>}
      {op.error && <Alert>{op.error}</Alert>}
    </form>
  </section>;
}

export function RegisterPage() {
  const [revision, setRevision] = useState(0);
  const [mode, setMode] = useState<"create" | "register">("create");
  const read = usePoll<S["RegistryRead"]>("/registry", 0, revision);
  const folder = usePoll<S["CreationRootRead"]>("/project-creation-root", 0, revision);
  const retry = useOperation();
  const pending = readConfirmation();
  const refresh = () => setRevision(n => n + 1);
  const options = read.data;
  return <>
    <PageHeader title="Nuevo proyecto"><p>Elige una carpeta nueva o registra un checkout existente con la composición del operador.</p></PageHeader>
    {pending && <section className="decision decision-attention">
      <h2>Confirmación pendiente de respuesta</h2><p>Se conserva el envío exacto. Reenviarlo devuelve su resultado sin duplicar la operación.</p>
      <Evidence title="Envío pendiente" value={pending} />
      <button disabled={retry.busy} onClick={() => void retry.run(async () => {
        await confirmOnce(pending.path, pending.body); refresh();
      })}>Reenviar confirmación</button>
      {retry.error && <Alert>{retry.error}</Alert>}
    </section>}
    {folder.data ? <CreationRootPanel key={folder.data.version} root={folder.data} refresh={refresh} />
      : folder.error ? <Alert>{folder.error}</Alert> : <Loading />}
    <div className="actions" role="group" aria-label="Tipo de alta">
      <button type="button" className={mode === "create" ? undefined : "button-quiet"} aria-pressed={mode === "create"}
        onClick={() => setMode("create")}>Crear carpeta nueva</button>
      <button type="button" className={mode === "register" ? undefined : "button-quiet"} aria-pressed={mode === "register"}
        onClick={() => setMode("register")}>Registrar carpeta existente</button>
    </div>
    {!options ? read.error ? <Alert>{read.error}</Alert> : <Loading />
      : !options.available ? <Empty title="Este servicio no admite registrar proyectos"><p>Requiere local-config-3/4/5/6 con registro y composiciones.</p></Empty>
      : mode === "create" ? !options.creation_available ? <Empty title="Creación deshabilitada por el operador"><p>La configuración debe permitir bootstrap.</p></Empty>
        : folder.data?.status !== "ACTIVE" ? <Empty title="Elige una carpeta de proyectos"><p>Guarda primero la carpeta padre donde crear los hijos.</p></Empty>
        : <NewDirectoryForm key={folder.data.version} options={options} root={folder.data} refresh={refresh} />
      : !options.roots.length ? <Empty title="No hay raíces TOML para registrar carpetas existentes"><p>Esta autoridad es independiente de la carpeta elegida para hijos nuevos.</p></Empty>
      : <section className="panel"><h2>Registrar carpeta existente</h2>
        <RegistryForm options={options} action="register" initial={emptyDraft(options)} expected={0}
          onApplied={(result, change) => navigate(change.bootstrap_enabled
            ? { name: "setup", project: result.project.id } : { name: "project", project: result.project.id })} />
      </section>}
    {!!folder.data?.operations.length && <section className="panel"><h2>Operaciones de creación</h2>
      {folder.data.operations.map(operation => <CreationOperation key={`${operation.id}-${operation.version}`} initial={operation}
        rootVersion={folder.data!.version} editable={folder.data!.available} refresh={refresh} />)}
    </section>}
  </>;
}

/** Settings of a registered project: version, audit, change and removal. TOML projects are read-only. */
export function RegistrySettings({ project, onChanged }: { project: string; onChanged: () => void }) {
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
      ["Bloqueos de configuración", (item.configuration_blockers ?? []).length ? (item.configuration_blockers ?? []).join(". ") : "ninguno"],
      ["Agentes", item.row.agent_selection ? "Selección propia del proyecto" : "Pareja heredada del servicio"],
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
          onApplied={() => { setRefresh(n => n + 1); onChanged(); }} />
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

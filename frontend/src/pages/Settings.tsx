import { useState, type ReactNode } from "react";
import type { S } from "../managed-api";
import { Prompts } from "../Prompts";
import { Fields, Loading, PageHeader, Stale, usePoll } from "../ui";
import { RegistrySettings } from "./Registry";
import { WorkLanguageSettings } from "../WorkLanguage";
import { useWorkspace } from "../workspace";

const SELECTION = { catalog: "Solo el catálogo", open: "Libre (catálogo como referencia)" } as const;
const PLANNING = { auto: "Automática", agent: "La hace el revisor", deterministic: "Determinista, desde NEXT_STEPS" } as const;

/** Effective settings; per-project selection through the V5 registry and operator presets (D116). */
export function SettingsPage() {
  const { project } = useWorkspace();
  const [revision, setRevision] = useState(0);
  const read = usePoll<S["ManagedProjectRead"]>(`/projects/${project}`, 15000, revision);
  const p = read.data;
  return <>
    <PageHeader title="Ajustes"><p>Consulta los agentes efectivos y cambia su selección en el registro del proyecto, si el servicio ofrece presets. El revisor decide el modelo y esfuerzo del ejecutor en cada tarea. Ejecutables y entornos los fija el operador.</p></PageHeader>
    <Stale error={p ? read.error : undefined} />
    {!p ? <Loading /> : <>
      <section className="panel" aria-labelledby="settings-agents">
        <h2 id="settings-agents">Agentes</h2>
        <div className="agents">
          <div><h3>Revisor</h3><Fields items={[
            ["Proveedor", p.agents.reviewer.provider ?? "sin declarar"], ["Modelo", <code>{p.agents.reviewer.model}</code>], ["Esfuerzo", p.agents.reviewer.effort],
            ...(p.agents.planner.model !== p.agents.reviewer.model || p.agents.planner.effort !== p.agents.reviewer.effort
              ? [["Al planificar", <><code>{p.agents.planner.model}</code> con esfuerzo {p.agents.planner.effort}</>] as [string, ReactNode]] : []),
          ]} /></div>
          <div><h3>Ejecutor</h3><Fields items={[
            ["Proveedor", p.agents.executor.provider ?? "sin declarar"], ["Selección", SELECTION[p.agents.executor.selection_mode]],
            ["Modelos", p.agents.executor.models.map(m => <code key={m} className="chip">{m}</code>)], ["Esfuerzos", p.agents.executor.efforts.join(", ")],
          ]} /></div>
        </div>
        <Fields items={[["Planificación", PLANNING[p.agents.planning_mode]]]} />
      </section>
      <section className="panel" aria-labelledby="settings-project">
        <h2 id="settings-project">Proyecto</h2>
        <p>Checkout <code className="path">{p.root}</code></p>
        <p className="hint">{p.source === "registry" ? `Registrado desde la interfaz; versión ${p.registry_version} del registro.` : "Declarado en el TOML del operador; no se edita desde la interfaz."}</p>
        <Fields items={[
          ["Perfil", p.profile],
          ["Documentos", p.documents === "v2" ? "Contrato unificado" : "Contrato anterior"],
          ["Tag al cerrar fases", p.tag_kind === "annotated" ? "Anotado" : "Ligero"],
          ["Bootstrap", p.bootstrap_enabled ? "Permitido en este destino" : "No"],
        ]} />
        <h3>Versiones congeladas en cada trabajo</h3>
        <Fields items={Object.entries(p.versions).map(([k, v]) => [k, v === null ? <span className="muted">no registrada</span> : <code>{v}</code>])} />
      </section>
      <WorkLanguageSettings project={project} work={p.work_language} onChanged={() => setRevision(n => n + 1)} />
      {p.source === "registry" && <RegistrySettings project={project} onChanged={() => setRevision(n => n + 1)} />}
      <Prompts project={project} />
    </>}
  </>;
}

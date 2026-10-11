import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import type { components } from "./api.generated";
import { request } from "./api";

type Project = components["schemas"]["LegacyProjectRead"];
type Phase = components["schemas"]["LegacyPhaseRead"];
type Task = components["schemas"]["LegacyTaskRead"];
type Run = components["schemas"]["LegacyRunRead"];
type Artifact = components["schemas"]["LegacyArtifactRead"];
type Entry = components["schemas"]["EvidenceEntryRead"];
type Entries = components["schemas"]["EvidenceEntriesRead"];
type Content = components["schemas"]["EvidenceContentRead"];
type Field = components["schemas"]["FieldRead"];
type Page<T> = Omit<components["schemas"]["Page_LegacyProjectRead_"], "items"> & { items: T[] };

function useRead<T>(url: string) {
  const [state, setState] = useState<{ url: string; data?: T; error?: string }>();
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    let active = true;
    setState(undefined);
    request<T>(url).then((data) => { if (active) setState({ url, data }); })
      .catch((error: unknown) => {
        if (active) setState({ url, error: error instanceof Error ? error.message : "Error de lectura local." });
      });
    return () => { active = false; };
  }, [url, revision]);
  return { ...(state?.url === url ? state : {}), retry: () => setRevision((n) => n + 1) };
}

function Pagination({ offset, next, previous }: { offset: number; next: number | null; previous: (n: number) => void }) {
  return <div className="pagination" aria-label="Paginación">
    <button disabled={offset === 0} onClick={() => previous(Math.max(0, offset - 20))}>Anterior</button>
    <span>Desde {offset + 1}</span>
    <button disabled={next === null} onClick={() => { if (next !== null) previous(next); }}>Siguiente</button>
  </div>;
}

function RemoteList<T>({ url, children }: { url: string; children: (item: T) => ReactNode }) {
  const [offset, setOffset] = useState(0);
  const { data, error, retry } = useRead<Page<T>>(`${url}${url.includes("?") ? "&" : "?"}offset=${offset}&limit=20`);
  return <>
    {error ? <p className="error" role="alert">{error} <button onClick={retry}>Reintentar lectura</button></p> :
      !data ? <p role="status">Cargando…</p> : <>
        {data.items.length ? <ul className="legacy-list">{data.items.map((item, i) => <li key={i}>{children(item)}</li>)}</ul> :
          <p>No hay registros para esta selección.</p>}
        <Pagination offset={offset} next={data.next_offset} previous={setOffset} />
      </>}
  </>;
}

export function LegacyBrowser() {
  const [project, setProject] = useState<Project>();
  return <section className="legacy" aria-label="Navegación legacy">
    <div className="intro"><p className="eyebrow">LECTURA LOCAL · H1.2</p>
      <h1>Evidencias de tus proyectos.</h1>
      <p>El índice muestra la última importación explícita. Los originales son autoridad; los diagnósticos locales y pendientes no acreditan fallos de agente.</p>
    </div>
    <h2>Proyectos / orígenes</h2>
    <RemoteList<Project> url="/api/legacy/projects">{(item) => <button className="choice" aria-pressed={project?.id === item.id} onClick={() => setProject(item)}>
      <strong>{item.name}</strong><small>{item.root}</small><small>Indexado: {item.observed_at}</small>
    </button>}</RemoteList>
    <p className="hint">Importa una raíz con <code>python -m harness_local.cli legacy-import &lt;raíz&gt;</code>. Repite el comando para actualizar el índice.</p>
    {project && <ProjectView key={project.id} project={project} />}
  </section>;
}

function ProjectView({ project }: { project: Project }) {
  const [phase, setPhase] = useState<string>();
  const [task, setTask] = useState<string>();
  const [run, setRun] = useState<Run>();
  const base = `/api/legacy/projects/${project.id}`;
  const filters = new URLSearchParams();
  if (phase) filters.set("phase", phase);
  const taskUrl = `${base}/tasks?${filters}`;
  if (task) filters.set("task", task);
  const runUrl = `${base}/runs?${filters}`;
  return <div className="project-detail">
    <h2>{project.name} · Observación</h2>
    <p className="hint">Identidades del directorio o declaradas por los artefactos. ACCEPT y READY son veredictos históricos; aceptación aplicada, commit y cierre no se certifican aquí.</p>
    <h3>Fases</h3>
    <button onClick={() => { setPhase(undefined); setTask(undefined); setRun(undefined); }}>Todas las fases</button>
    <RemoteList<Phase> key={base} url={`${base}/phases`}>{(item) => <button className="choice" aria-pressed={phase === item.identity}
      onClick={() => { setPhase(item.identity); setTask(undefined); setRun(undefined); }}>
      <strong>{item.identity}</strong>{item.provenance.map((p, i) => <small key={i}>{p.origin} · {p.path}</small>)}
      {item.more_provenance && <small>Más procedencia en las evidencias del proyecto.</small>}
    </button>}</RemoteList>
    <h3>Tareas{phase ? ` de ${phase}` : ""}</h3>
    <button onClick={() => { setTask(undefined); setRun(undefined); }}>Todos los runs / cierre / reconciliación</button>
    <RemoteList<Task> key={taskUrl} url={taskUrl}>{(item) => <button className="choice" aria-pressed={task === item.identity}
      onClick={() => { setTask(item.identity); setRun(undefined); }}><strong>{item.identity}</strong><small>{item.origin}</small></button>}</RemoteList>
    <h3>{task ? `Runs observados de ${task}` : "Runs observados"}</h3>
    <p className="hint">Un run agrupa archivos; sus índices de evidencia no cuentan invocaciones. El contrato se consulta en task.json.</p>
    <RemoteList<Run> key={runUrl} url={runUrl}>{(item) => <button className="choice" aria-pressed={run?.id === item.id} onClick={() => setRun(item)}>
      <strong>{item.identity}</strong><small>{item.path}</small>
    </button>}</RemoteList>
    {run && <ArtifactList key={run.id} base={base} run={run} />}
    <details><summary>Documentos de estado y archivo de fases</summary><ArtifactList base={base} /></details>
  </div>;
}

const kindLabels: Record<string, string> = { task: "Contrato de tarea", request: "Selección solicitada", result: "Resultado reportado", usage: "Consumo reportado",
  review: "Revisión / hallazgos / preguntas", stop: "Bloqueo operativo", validation: "Validación / duración por comando", events: "Eventos observados",
  phase_review: "Revisión de fase", phase_metadata: "HEAD examinado", reconcile: "Reconciliación", resume: "Reanudación documentada" };

function ArtifactList({ base, run }: { base: string; run?: Run }) {
  const [artifact, setArtifact] = useState<Artifact>();
  const url = `${base}/artifacts${run ? `?run_id=${encodeURIComponent(run.id)}` : ""}`;
  return <section className="artifact-panel" aria-label={run ? "Timeline de evidencias" : "Documentos"}>
    <h3>{run ? "Timeline de evidencias" : "Documentos"}</h3>
    <p className="hint">Orden por ruta e índice del archivo. Fecha de cada evento: no registrada. Archivos ausentes y parciales permanecen visibles.</p>
    <RemoteList<Artifact> url={url}>{(item) => <button className="choice" aria-pressed={artifact?.id === item.id} onClick={() => setArtifact(item)}>
      <strong>{kindLabels[item.kind] ?? item.kind} · {item.status}</strong><small>{item.path}</small>
      {item.diagnostic && <small>{item.diagnostic}</small>}
    </button>}</RemoteList>
    {artifact && <ArtifactView key={artifact.id} base={base} artifact={artifact} />}
  </section>;
}

const fieldLabels: Record<string, string> = {
  model: "Modelo solicitado", effort: "Esfuerzo solicitado", requested: "Selección solicitada", executor_selection: "Selección del contrato",
  actual_models: "Modelos reportados (lista vacía no acredita modelo)", modelUsage: "Consumo por modelo reportado", model_usage: "Consumo por modelo reportado",
  usage: "Tokens reportados (sin sumar wrappers)", duration_ms: "Duración reportada de ejecución (ms)", duration_seconds: "Duración de comando (s)",
  total_cost_usd: "Coste API equivalente reportado (USD)", api_equivalent_cost_usd: "Coste API equivalente reportado (USD)",
};

function FieldValue({ name, field }: { name: string; field: Field }) {
  return <div className="field"><dt>{fieldLabels[name] ?? name}</dt><dd>
    {field.truncated ? "Valor excede el límite: consultar el contenido original por tramos." : field.state === "recorded" ?
      <pre>{JSON.stringify(field.value, null, 2)}</pre> : `no registrado (${field.state === "null" ? "null explícito" : "campo ausente"})`}
  </dd></div>;
}

function EntryView({ entry }: { entry: Entry }) {
  return <li className="entry"><strong>{entry.kind}</strong> <code>{entry.pointer}</code>
    {entry.truncated ? <p>Entrada supera el límite; consultar el original por tramos.</p> : entry.value != null && <pre>{JSON.stringify(entry.value, null, 2)}</pre>}
    <dl>{Object.entries(entry.fields ?? {}).map(([name, field]) => <FieldValue key={name} name={name} field={field} />)}</dl>
  </li>;
}

function ArtifactView({ base, artifact }: { base: string; artifact: Artifact }) {
  const [offset, setOffset] = useState(0);
  const [contentOffset, setContentOffset] = useState(0);
  const [previousOffsets, setPreviousOffsets] = useState<number[]>([]);
  const url = `${base}/artifacts/${artifact.id}`;
  const entries = useRead<Entries>(`${url}/entries?offset=${offset}&limit=20`);
  const content = useRead<Content>(`${url}/content?offset=${contentOffset}&limit=8192`);
  return <article className="evidence-detail" aria-label="Detalle de evidencia">
    <h3>{kindLabels[artifact.kind] ?? artifact.kind}</h3><p><code>{artifact.path}</code></p>
    <p className="hint">Estado indexado: {artifact.status} · SHA-256: <code>{artifact.sha256 ?? "no registrado"}</code> · Bytes: {artifact.size_bytes ?? "no registrado"}</p>
    {artifact.diagnostic && <p className="error">Diagnóstico local: {artifact.diagnostic}</p>}
    <p className="hint">Los campos siguientes proceden del payload indexado. SHA-256 de esa proyección: <code>{entries.data?.sha256 ?? "no registrado"}</code>. Coste equivalente API no es factura ni porcentaje de cuota. No se suman copias de consumo del mismo resultado.</p>
    {((entries.data && entries.data.sha256 !== artifact.sha256) || (content.data && content.data.indexed_sha256 !== artifact.sha256)) &&
      <p className="error">El índice se ha reimportado desde que abriste la lista. Recarga la página para volver a seleccionar la evidencia. Cada respuesta conserva su propio hash.</p>}
    {content.error && <p className="error" role="alert">{content.error} <button onClick={content.retry}>Reintentar</button></p>}
    {!content.data && !content.error && <p role="status">Comprobando contenido del origen…</p>}
    {content.data && <p className={content.data.status === "verified" ? "verified" : "error"} role="status">
      Contenido: {content.data.status}{content.data.diagnostic && ` · ${content.data.diagnostic}`}
      {content.data.status === "changed" && <> · Hash observado: <code>{content.data.observed_sha256}</code>. La proyección inferior sigue siendo la lectura anterior del índice.</>}
    </p>}
    {entries.error ? <p className="error" role="alert">{entries.error} <button onClick={entries.retry}>Reintentar</button></p> :
      !entries.data ? <p role="status">Cargando campos…</p> : <>
        <ul className="entry-list">{entries.data.items.map((entry) => <EntryView key={entry.pointer} entry={entry} />)}</ul>
        {!entries.data.items.length && <p>No hay campos estructurados disponibles. Consulta los bytes originales o el diagnóstico.</p>}
        <Pagination offset={offset} next={entries.data.next_offset} previous={setOffset} />
      </>}
    <h4>Contenido original · logs / diff / JSON / documentos</h4>
    <p className="hint">Texto plano verificado; tramo máximo 8192 bytes más el final UTF-8. No se ejecutan prompts, comandos ni HTML histórico.</p>
    {content.data?.text != null && <pre className="raw-content">{content.data.text || "(archivo vacío)"}</pre>}
    <div className="pagination">
      <button disabled={!previousOffsets.length} onClick={() => {
        setContentOffset(previousOffsets.at(-1) ?? 0); setPreviousOffsets((items) => items.slice(0, -1));
      }}>Tramo anterior</button><span>Byte {contentOffset}</span>
      <button disabled={content.data?.next_offset == null} onClick={() => {
        if (content.data?.next_offset != null) { setPreviousOffsets((items) => [...items, contentOffset]); setContentOffset(content.data.next_offset); }
      }}>Tramo siguiente</button><button onClick={content.retry}>Comprobar de nuevo</button>
    </div>
  </article>;
}

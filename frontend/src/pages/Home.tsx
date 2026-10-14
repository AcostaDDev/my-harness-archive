import type { S } from "../managed-api";
import { Link } from "../navigation";
import { Empty, Loading, PageHeader, Stale, usePoll } from "../ui";

export function Home() {
  const projects = usePoll<S["ManagedProjectRead"][]>("/projects", 5000);
  const registry = usePoll<S["RegistryRead"]>("/registry", 15000);
  const list = projects.data;
  const available = registry.data?.available;
  const unavailable = registry.data?.projects.filter(p => p.status === "ACTIVE" && !p.available) ?? [];
  return <>
    <PageHeader title="Proyectos" aside={available ? <Link className="button-link" to={{ name: "project-new" }}>Registrar proyecto</Link> : undefined}>
      <p>Elige un proyecto para ver su fase activa, sus tareas y lo que espera una decisión tuya.</p>
    </PageHeader>
    <Stale error={list ? projects.error : undefined} />
    {unavailable.length > 0 && <div className="state state-attention" role="status">
      <p className="state-title">Proyectos registrados que no se componen con el TOML actual</p>
      <ul>{unavailable.map(p => <li key={p.id}><code>{p.id}</code>: {p.diagnostic}</li>)}</ul>
    </div>}
    {!list ? projects.error ? <p role="alert" className="state state-error">No se pudieron leer los proyectos: {projects.error}</p> : <Loading>Cargando proyectos…</Loading>
      : !list.length ? <Empty title="No hay proyectos registrados">
        {available ? <p>Da de alta una carpeta en <Link to={{ name: "project-new" }}>Registrar proyecto</Link>, o declárala en el TOML del operador.</p>
          : <p>Los proyectos se declaran en la configuración local del servicio (<code>harness-local serve --config</code>). El alta desde esta interfaz necesita <code>local-config-3</code>.</p>}
        <p>Si tienes ejecuciones del harness anterior, consúltalas en <Link to={{ name: "legacy" }}>proyectos importados</Link>.</p>
      </Empty>
        : <div className="table-scroll" role="region" aria-label="Proyectos registrados" tabIndex={0}>
          <table className="table">
            <thead><tr><th scope="col">Proyecto</th><th scope="col">Origen</th><th scope="col">Perfil</th><th scope="col">Documentos</th><th scope="col">Revisor</th><th scope="col">Ejecutor</th><th scope="col">Checkout</th></tr></thead>
            <tbody>{list.map(p => <tr key={p.id}>
              <td><Link className="mono strong" to={{ name: "project", project: p.id }}>{p.id}</Link></td>
              <td className="nowrap">{p.source === "registry" ? `Registro v${p.registry_version}` : "TOML"}</td>
              <td className="nowrap">{p.profile}</td>
              <td>{p.documents === "v2" ? "Por fase (v2)" : "Anterior"}</td>
              <td>{p.agents.reviewer.provider ?? "sin declarar"} <span className="muted">{p.agents.reviewer.model}</span></td>
              <td>{p.agents.executor.provider ?? "sin declarar"} <span className="muted">{p.agents.executor.models.join(", ")}</span></td>
              <td><code className="path" title={p.root}>{p.root}</code></td>
            </tr>)}</tbody>
          </table>
        </div>}
  </>;
}

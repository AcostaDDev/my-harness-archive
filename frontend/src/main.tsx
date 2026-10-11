import { StrictMode, useEffect, useState } from "react";
import type { FormEvent } from "react";
import { createRoot } from "react-dom/client";
import { api } from "./api";
import type { Simulation } from "./api";
import { LegacyBrowser } from "./legacy";
import "./styles.css";

function App() {
  const [view, setView] = useState<"legacy" | "simulation">("legacy");
  const [simulations, setSimulations] = useState<Simulation[]>([]);
  const [selectedId, setSelectedId] = useState<string>();
  const [title, setTitle] = useState("Primera simulación local");
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string>();
  const selected = simulations.find((simulation) => simulation.id === selectedId);

  useEffect(() => {
    let active = true;
    api.list().then((items) => {
      if (active) {
        setSimulations(items);
        setSelectedId(items[0]?.id);
      }
    }).catch((reason: unknown) => {
      if (active) setError(reason instanceof Error ? reason.message : "No se pudo cargar el historial.");
    }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (creating) return;
    setCreating(true);
    setError(undefined);
    try {
      const simulation = await api.create({ title: title.trim() });
      setSimulations((items) => [simulation, ...items]);
      setSelectedId(simulation.id);
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "No se pudo crear la simulación.");
    } finally {
      setCreating(false);
    }
  }

  return (
    <main>
      <header>
        <div className="brand"><span className="brand-icon" aria-hidden="true">H</span> Harness Local</div>
        <span className="mode"><span aria-hidden="true">●</span> {view === "legacy" ? "Observación legacy" : "Modo simulado"}</span>
      </header>
      <nav className="view-tabs" aria-label="Modo de consulta">
        <button aria-pressed={view === "legacy"} onClick={() => setView("legacy")}>Proyectos importados</button>
        <button aria-pressed={view === "simulation"} onClick={() => setView("simulation")}>Simulaciones H0.3</button>
      </nav>
      {view === "legacy" ? <LegacyBrowser /> : <>
      <section className="intro">
        <p className="eyebrow">ENTORNO LOCAL · H0.3</p>
        <h1>Una ejecución, de principio a fin.</h1>
        <p>Prueba el recorrido con datos sintéticos. Cada resultado queda guardado y puedes volver a consultarlo.</p>
      </section>
      <section className="new-simulation" aria-labelledby="create-title">
        <div>
          <h2 id="create-title">Nueva simulación</h2>
          <p>El adaptador falso trabaja en este equipo, sin acceder a modelos ni modificar proyectos.</p>
        </div>
        <form onSubmit={create}>
          <label htmlFor="title">Título</label>
          <div className="form-row">
            <input id="title" value={title} onChange={(event) => setTitle(event.target.value)}
              required maxLength={120} disabled={creating} />
            <button type="submit" disabled={loading || creating || !title.trim()}>
              {creating ? "Simulando…" : "Ejecutar simulación"}<span aria-hidden="true"> →</span>
            </button>
          </div>
        </form>
      </section>
      {error && <p className="error" role="alert">{error}</p>}
      <section className="workspace" aria-label="Historial y resultado">
        <aside>
          <div className="section-heading"><h2>Historial</h2><span>{simulations.length}</span></div>
          {loading ? <p role="status" className="empty">Cargando historial…</p> : simulations.length === 0 ?
            <p className="empty">Aún no hay simulaciones. Crea la primera para ver su resultado.</p> :
            <ul className="history">{simulations.map((simulation) => (
              <li key={simulation.id}>
                <button className={selectedId === simulation.id ? "selected" : ""}
                  aria-pressed={selectedId === simulation.id} onClick={() => setSelectedId(simulation.id)}>
                  <strong>{simulation.title}</strong>
                  <time dateTime={simulation.created_at}>{new Date(simulation.created_at).toLocaleString("es-ES")}</time>
                </button>
              </li>
            ))}</ul>}
        </aside>
        <article aria-live="polite">
          {selected ? <>
            <div className="result-header"><p className="eyebrow">RESULTADO LOCAL</p><span className="completed">Completada</span></div>
            <h2>{selected.title}</h2>
            <ol className="events">{selected.events.map((message, index) => (
              <li key={index}><span className="step" aria-hidden="true">{index + 1}</span><p>{message}</p></li>
            ))}</ol>
            <div className="record"><span>Identificador</span><code>{selected.id}</code></div>
          </> : <div className="placeholder"><span aria-hidden="true">◎</span><h2>Tu próximo resultado aparecerá aquí</h2><p>Selecciona una simulación del historial o crea una nueva.</p></div>}
        </article>
      </section>
      <footer>Datos sintéticos · Sin agentes reales · Una simulación no acredita aceptación ni commit.</footer>
      </>}
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);

import { createContext, useContext, useRef, useState } from "react";
import type { ReactNode } from "react";
import { managed, ManagedError, readPending, savePending } from "./managed-api";
import type { Pending, S } from "./managed-api";
import { navigate } from "./navigation";
import { runRoute } from "./router.ts";
import { Evidence, message } from "./ui";

// Acciones de un proyecto compartidas por sus páginas. Un envío sin respuesta confirmada se
// conserva con su clave (también al recargar) y solo se repite por acción explícita (H2).
export type Workspace = {
  project: string;
  busy: boolean;
  refresh: number;
  operate: (action: () => Promise<unknown>) => Promise<void>;
  send: (request: Pending) => Promise<S["ManagedJobRead"]>;
};

const Context = createContext<Workspace | null>(null);

export function useWorkspace(): Workspace {
  const value = useContext(Context);
  if (!value) throw new Error("Workspace fuera de un proyecto");
  return value;
}

export function ProjectWorkspace({ project, children }: { project: string; children: ReactNode }) {
  const [pending, setPending] = useState<Pending | undefined>(readPending);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [refresh, setRefresh] = useState(0);
  const guard = useRef(false);
  function remember(value?: Pending) { savePending(value); setPending(value); }
  async function operate(action: () => Promise<unknown>) {
    if (guard.current) return;
    guard.current = true; setBusy(true); setError("");
    try { await action(); }
    catch (e) { setError(message(e)); }
    finally { guard.current = false; setBusy(false); setRefresh(n => n + 1); }
  }
  async function send(request: Pending) {
    remember(request);
    try {
      const job = await managed<S["ManagedJobRead"]>(request.path, request.body, request.key);
      remember();
      const run = await managed<S["ManagedRunRead"]>(`/runs/${job.run_id}`).catch(() => undefined);
      const route = run && runRoute(run);
      // Las acciones sobre un run ya abierto no cambian de página; las que crean uno, sí.
      if (route && (request.path.endsWith("/runs") || request.path.endsWith("/batch/next"))) navigate(route);
      return job;
    } catch (e) {
      // Un rechazo definitivo permite una acción nueva tras releer la versión actual.
      if (e instanceof ManagedError && e.status >= 400 && e.status < 500 && e.status !== 401) remember();
      throw e;
    }
  }
  const value: Workspace = { project, busy: busy || !!pending, refresh, operate, send };
  return <Context.Provider value={value}>
    {error && <div className="toast" role="alert"><p>{error}</p>
      <button type="button" className="button-quiet" onClick={() => setError("")}>Cerrar aviso</button></div>}
    {pending && <section className="decision decision-attention decision-pending" aria-labelledby="pending-title">
      <h2 id="pending-title">Envío sin respuesta confirmada</h2>
      <p>Repetirlo envía exactamente el mismo contenido con la misma clave, así que no crea un trabajo duplicado.</p>
      <Evidence title="Solicitud pendiente" value={pending} />
      <button type="button" disabled={busy} onClick={() => void operate(() => send(pending))}>Repetir envío pendiente</button>
    </section>}
    {children}
  </Context.Provider>;
}

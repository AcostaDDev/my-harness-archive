import { useEffect, useRef, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import type { components, operations } from "./api.generated";

type Session = components["schemas"]["SessionRead"];

export function SessionGate({ children }: { children: ReactNode }) {
  const epoch = useRef(0);
  const [session, setSession] = useState<Session>();
  const [checking, setChecking] = useState(true);
  const [key, setKey] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    const expired = () => { epoch.current++; setSession(undefined); setError("Sesión ausente, cerrada o caducada. Las acciones pendientes no se repiten automáticamente."); };
    window.addEventListener("harness-session-required", expired);
    const check = async () => {
      const version = epoch.current;
      try {
        const response = await fetch("/api/session");
        const observed = response.ok ? await response.json() as Session : undefined;
        if (!active || version !== epoch.current) return;
        if (observed) setSession(observed);
        else expired();
      } catch { if (active && version === epoch.current) { setSession(undefined); setError("No se pudo comprobar la sesión. Comprueba el servicio local."); } }
      finally { if (active) setChecking(false); }
    };
    void check();
    const timer = setInterval(() => { void check(); }, 15000);
    return () => { active = false; clearInterval(timer); window.removeEventListener("harness-session-required", expired); };
  }, []);
  useEffect(() => {
    if (!session) return;
    const timer = setTimeout(() => { epoch.current++; setSession(undefined); setError("Sesión caducada. Inicia sesión de nuevo."); }, session.expires_in * 1000);
    return () => clearTimeout(timer);
  }, [session]);
  async function login(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    epoch.current++;
    setBusy(true); setError("");
    const submitted: operations["start_session"]["requestBody"]["content"]["application/json"] = { key };
    setKey("");
    try {
      const response = await fetch("/api/session", { method: "POST",
        headers: { "Content-Type": "application/json", "X-Harness-Local": "1" }, body: JSON.stringify(submitted) });
      if (!response.ok) throw new Error(response.status === 429 ? "Espera un minuto antes de volver a intentar." : "No se pudo iniciar sesión. Comprueba la clave y el servicio.");
      setSession(await response.json() as Session);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "No se pudo iniciar sesión."); }
    finally { epoch.current++; setBusy(false); }
  }
  async function logout() {
    if (busy) return;
    epoch.current++;
    setBusy(true);
    try {
      const response = await fetch("/api/session", { method: "DELETE", headers: { "X-Harness-Local": "1" } });
      if (!response.ok && response.status !== 401) throw new Error();
      setSession(undefined); setError("Sesión cerrada. Los trabajos ya autorizados siguen su curso.");
    } catch { setError("No se pudo confirmar el cierre. Vuelve a intentarlo o detén el servicio."); }
    finally { epoch.current++; setBusy(false); }
  }
  if (checking) return <main><p role="status">Comprobando sesión local…</p></main>;
  if (session) return <><div className="session-bar"><button disabled={busy} onClick={() => void logout()}>Cerrar sesión</button>{error && <p role="alert">{error}</p>}</div>{children}</>;
  return <main><h1>Acceso a Harness Local</h1><p>Abre el archivo privado indicado al iniciar el servicio y copia su clave aquí. La sesión dura ocho horas; reiniciar el servicio la cierra.</p>
    <form onSubmit={login}><label htmlFor="login-key">Clave local</label><input id="login-key" type="password" autoComplete="off" value={key} onChange={e => setKey(e.target.value)} maxLength={128} required disabled={busy} />
      <button disabled={busy || !key}>Iniciar sesión</button></form>{error && <p role="alert">{error}</p>}</main>;
}

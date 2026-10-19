import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import type { S } from "./managed-api";
import { Link } from "./navigation";
import { href, trail } from "./router.ts";
import type { Route } from "./router.ts";
import { useSession } from "./SessionGate";
import { usePoll } from "./ui";

type Theme = "system" | "light" | "dark";
const THEMES: Record<Theme, string> = { system: "Tema del sistema", light: "Tema claro", dark: "Tema oscuro" };
const NEXT: Record<Theme, Theme> = { system: "light", light: "dark", dark: "system" };

// Preferencia de este navegador; si el almacenamiento no está disponible, sigue el sistema.
function storedTheme(): Theme {
  try { const value = localStorage.getItem("harness-theme"); return value === "light" || value === "dark" ? value : "system"; }
  catch { return "system"; }
}

function useTheme(): [Theme, () => void] {
  const [theme, setTheme] = useState<Theme>(storedTheme);
  useEffect(() => {
    if (theme === "system") document.documentElement.removeAttribute("data-theme");
    else document.documentElement.setAttribute("data-theme", theme);
    try { if (theme === "system") localStorage.removeItem("harness-theme"); else localStorage.setItem("harness-theme", theme); } catch { /* sin preferencia guardada */ }
  }, [theme]);
  return [theme, () => setTheme(NEXT[theme])];
}

function Supervisor() {
  const read = usePoll<S["SupervisorRead"]>("/supervisor", 5000);
  const s = read.data;
  const [label, tone] = read.error && !s ? ["Servicio sin respuesta", "danger"]
    : !s ? ["Conectando…", "neutral"]
      : !s.ports_configured ? ["Solo lectura: sin agentes configurados", "neutral"]
        : s.alive ? ["Supervisor activo", "ok"] : ["Supervisor detenido", "attention"];
  return <span className={`status status-${tone}`} title={s?.last_error ?? read.error ?? undefined}>
    <span className="status-mark" aria-hidden="true" />{label}{read.error && s ? " (sin actualizar)" : ""}</span>;
}

function SessionControls() {
  const { logout, busy, notice, expiresAt } = useSession();
  const until = new Date(expiresAt).toLocaleTimeString("es-ES", { hour: "2-digit", minute: "2-digit" });
  return <div className="session">
    <span className="muted" title="La sesión caduca a las ocho horas o al reiniciar el servicio">Sesión hasta las {until}</span>
    <button type="button" className="button-quiet" disabled={busy} onClick={() => void logout()}>Cerrar sesión</button>
    {notice && <p role="alert" className="session-notice">{notice}</p>}
  </div>;
}

function ProjectNav({ route, project }: { route: Route; project: string }) {
  const items: [string, Route, boolean][] = [
    ["Resumen", { name: "project", project }, route.name === "project"],
    ["Fases", { name: "phases", project }, ["phases", "phase", "task", "run"].includes(route.name)],
    ["Documentación", { name: "docs", project }, route.name === "docs"],
    ["Chat", { name: "chat", project }, route.name === "chat"],
    ["Estadísticas", { name: "project-stats", project }, route.name === "project-stats"],
    ["Ajustes", { name: "settings", project }, route.name === "settings"],
  ];
  return <div className="nav-group">
    <p className="nav-project mono" title={project}>{project}</p>
    <ul>{items.map(([label, to, current]) => <li key={label}><Link to={to} current={current}>{label}</Link></li>)}</ul>
  </div>;
}

export function Shell({ route, children }: { route: Route; children: ReactNode }) {
  const [theme, cycle] = useTheme();
  const items = trail(route);
  const project = "project" in route ? route.project : undefined;
  const path = href(route);
  const first = useRef(true);
  // Al cambiar de página: título del documento, scroll arriba y foco en el titular (lectores de pantalla).
  useEffect(() => {
    document.title = `${items[items.length - 1].label} | Harness Local`;
    if (first.current) { first.current = false; return; }
    window.scrollTo(0, 0);
    requestAnimationFrame(() => document.getElementById("page-title")?.focus({ preventScroll: true }));
  }, [path]);
  return <div className="shell">
    <a className="skip" href="#main">Saltar al contenido</a>
    <header className="topbar">
      <Link to={{ name: "home" }} className="brand"><span className="brand-mark" aria-hidden="true" />Harness Local</Link>
      <nav aria-label="Ubicación" className="crumbs">
        <ol>{items.map((item, index) => <li key={href(item.to)}>
          {index === items.length - 1 ? <span aria-current="page">{item.label}</span> : <Link to={item.to}>{item.label}</Link>}
        </li>)}</ol>
      </nav>
      <div className="topbar-tools">
        <Supervisor />
        <button type="button" className="button-quiet theme" onClick={cycle} aria-label={`${THEMES[theme]}. Cambiar tema`} title={THEMES[theme]}>
          <span aria-hidden="true" className={`theme-mark theme-${theme}`} />
        </button>
        <SessionControls />
      </div>
    </header>
    <nav className="sidebar" aria-label="Secciones">
      <div className="nav-group">
        <ul>
          <li><Link to={{ name: "home" }} current={route.name === "home"}>Proyectos</Link></li>
          <li><Link to={{ name: "project-new" }} current={route.name === "project-new"}>Nuevo proyecto</Link></li>
          <li><Link to={{ name: "stats" }} current={route.name === "stats"}>Estadísticas</Link></li>
          <li><Link to={{ name: "legacy" }} current={route.name === "legacy"}>Importados</Link></li>
        </ul>
      </div>
      {project && <ProjectNav route={route} project={project} />}
    </nav>
    <main id="main" className="content">{children}</main>
  </div>;
}

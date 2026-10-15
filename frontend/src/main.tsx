import { lazy, StrictMode, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { Chat } from "./Chat";
import { LegacyBrowser } from "./legacy";
import { Link, usePath } from "./navigation";
import { Home } from "./pages/Home";
import { PhaseListPage, PhasePage } from "./pages/Phases";
import { ProjectPage } from "./pages/Project";
import { RegisterPage } from "./pages/Registry";
import { RunPage, RunRedirect } from "./pages/Run";
import { SettingsPage } from "./pages/Settings";
import { TaskPage } from "./pages/Task";
import { parse } from "./router.ts";
import type { Route } from "./router.ts";
import { SessionGate } from "./SessionGate";
import { Shell } from "./Shell";
import { Empty, Loading, PageHeader } from "./ui";
import { ProjectWorkspace } from "./workspace";
import "./styles.css";

// La documentación (markdown-it y, al dibujar, Mermaid) se descarga solo al abrirla (H6.2 E3).
const DocsPage = lazy(() => import("./pages/Docs").then(module => ({ default: module.DocsPage })));

function Page({ route }: { route: Route }) {
  switch (route.name) {
    case "home": return <Home />;
    case "legacy": return <LegacyBrowser />;
    case "project-new": return <RegisterPage />;
    case "run-short": return <RunRedirect run={route.run} />;
    case "not-found": return <>
      <PageHeader title="Esta página no existe" />
      <Empty title={`No hay nada en ${route.path}`}><p>Puede que el enlace esté incompleto. Vuelve a la <Link to={{ name: "home" }}>lista de proyectos</Link>.</p></Empty>
    </>;
  }
  // Cada proyecto tiene su propio espacio de acciones; cambiar de proyecto lo reinicia.
  return <ProjectWorkspace key={route.project} project={route.project}><ProjectPageFor route={route} /></ProjectWorkspace>;
}

function ProjectPageFor({ route }: { route: Exclude<Route, { name: "home" | "legacy" | "project-new" | "run-short" | "not-found" }> }) {
  switch (route.name) {
    case "project": return <ProjectPage />;
    case "phases": return <PhaseListPage />;
    case "phase": return <PhasePage key={route.phase} code={route.phase} />;
    case "task": return <TaskPage key={`${route.phase}/${route.task}`} phase={route.phase} task={route.task} />;
    case "run": return <RunPage key={route.run} phase={route.phase} task={route.task} run={route.run} />;
    case "chat": return <Chat conversation={route.conversation} />;
    case "settings": return <SettingsPage />;
    case "docs": return <Suspense fallback={<Loading />}><DocsPage path={route.path} /></Suspense>;
  }
}

function App() {
  const route = parse(usePath());
  return <Shell route={route}><Page route={route} /></Shell>;
}

createRoot(document.getElementById("root")!).render(<StrictMode><SessionGate><App /></SessionGate></StrictMode>);

// Enrutador mínimo propio (D076): rutas de D072 §7 como datos puros, sin React ni dependencias.
// Solo se usan códigos y ids codificados; nada de la URL se interpreta como HTML.

export type Route =
  | { name: "home" }
  | { name: "stats" }
  | { name: "project-new" }
  | { name: "project"; project: string }
  | { name: "phases"; project: string }
  | { name: "phase"; project: string; phase: string }
  | { name: "task"; project: string; phase: string; task: string }
  | { name: "run"; project: string; phase: string; task: string; run: string }
  | { name: "chat"; project: string; conversation?: string }
  | { name: "settings"; project: string }
  | { name: "project-stats"; project: string }
  | { name: "docs"; project: string; path?: string }
  | { name: "onboarding"; project: string; conversation?: string; path?: string }
  | { name: "setup"; project: string; path?: string }
  | { name: "plan"; project: string; phase: string; conversation?: string }
  | { name: "run-short"; run: string }
  | { name: "not-found"; path: string };

const e = encodeURIComponent;

function decode(segment: string): string | undefined {
  try {
    const value = decodeURIComponent(segment);
    return value && !value.includes("/") ? value : undefined;
  } catch { return undefined; }
}

/** Ruta de una URL de la aplicación. Una barra final o repetida no cambia la ruta. */
export function parse(pathname: string): Route {
  const raw = pathname.split("/").filter(Boolean);
  const parts = raw.map(decode);
  if (parts.some(part => part === undefined)) return { name: "not-found", path: pathname };
  const [a, b, c, d, f, g, h, i] = parts as string[];
  const n = parts.length;
  if (n === 0) return { name: "home" };
  if (a === "stats" && n === 1) return { name: "stats" };
  if (a === "runs" && n === 2) return { name: "run-short", run: b };
  if (a !== "projects" || n < 2) return { name: "not-found", path: pathname };
  const project = b;
  // `new` está reservado: el servidor nunca registra un proyecto con ese id (D076).
  if (n === 2) return project === "new" ? { name: "project-new" } : { name: "project", project };
  if (c === "settings" && n === 3) return { name: "settings", project };
  if (c === "stats" && n === 3) return { name: "project-stats", project };
  // Documentación (H6.2 E3): el resto de la URL es la ruta del documento en el checkout, segmento a segmento.
  if (c === "docs") {
    const rest = (parts as string[]).slice(3);
    if (rest.some(part => part === "." || part === "..")) return { name: "not-found", path: pathname };
    return rest.length ? { name: "docs", project, path: rest.join("/") } : { name: "docs", project };
  }
  // Creación (H6.2 E4): igual que la documentación, el resto de la URL es la ruta de un borrador.
  if (c === "setup") {
    const rest = (parts as string[]).slice(3);
    if (rest.some(part => part === "." || part === "..")) return { name: "not-found", path: pathname };
    return rest.length ? { name: "setup", project, path: rest.join("/") } : { name: "setup", project };
  }
  if (c === "onboarding") {
    const rest = (parts as string[]).slice(4);
    if (rest.some(part => part === "." || part === "..")) return { name: "not-found", path: pathname };
    return { name: c, project, ...(d ? { conversation: d } : {}), ...(rest.length ? { path: rest.join("/") } : {}) };
  }
  if (c === "chat" && n <= 4) return n === 3 ? { name: "chat", project } : { name: "chat", project, conversation: d };
  if (c !== "phases") return { name: "not-found", path: pathname };
  if (n === 3) return { name: "phases", project };
  if (n === 4) return { name: "phase", project, phase: d };
  if (f === "plan" && n <= 6) return n === 5 ? { name: "plan", project, phase: d } : { name: "plan", project, phase: d, conversation: g };
  if (f === "tasks" && n === 6) return { name: "task", project, phase: d, task: g };
  if (f === "tasks" && h === "runs" && n === 8) return { name: "run", project, phase: d, task: g, run: i };
  return { name: "not-found", path: pathname };
}

/** URL canónica de una ruta; `parse(href(r))` devuelve `r` para toda ruta válida. */
export function href(route: Route): string {
  switch (route.name) {
    case "home": return "/";
    case "stats": return "/stats";
    case "project-new": return "/projects/new";
    case "project": return `/projects/${e(route.project)}`;
    case "phases": return `/projects/${e(route.project)}/phases`;
    case "phase": return `/projects/${e(route.project)}/phases/${e(route.phase)}`;
    case "task": return `/projects/${e(route.project)}/phases/${e(route.phase)}/tasks/${e(route.task)}`;
    case "run": return `/projects/${e(route.project)}/phases/${e(route.phase)}/tasks/${e(route.task)}/runs/${e(route.run)}`;
    case "chat": return `/projects/${e(route.project)}/chat${route.conversation ? `/${e(route.conversation)}` : ""}`;
    case "settings": return `/projects/${e(route.project)}/settings`;
    case "project-stats": return `/projects/${e(route.project)}/stats`;
    case "docs": return `/projects/${e(route.project)}/docs${route.path ? `/${route.path.split("/").map(e).join("/")}` : ""}`;
    case "onboarding": return `/projects/${e(route.project)}/${route.name}${route.conversation ? `/${e(route.conversation)}` : ""}${route.path ? `/${route.path.split("/").map(e).join("/")}` : ""}`;
    case "setup": return `/projects/${e(route.project)}/setup${route.path ? `/${route.path.split("/").map(e).join("/")}` : ""}`;
    case "plan": return `/projects/${e(route.project)}/phases/${e(route.phase)}/plan${route.conversation ? `/${e(route.conversation)}` : ""}`;
    case "run-short": return `/runs/${e(route.run)}`;
    case "not-found": return route.path;
  }
}

/** Ruta del proyecto activo, si la hay, para la navegación lateral. */
export function projectOf(route: Route): string | undefined {
  return "project" in route ? route.project : undefined;
}

/** Destino canónico de un run a partir de su lectura (`project_id`, `phase_id`, `task_id`). */
export function runRoute(run: { id: string; project_id: string | null; phase_id: string; task_id: string }): Route | undefined {
  return run.project_id ? { name: "run", project: run.project_id, phase: run.phase_id, task: run.task_id, run: run.id } : undefined;
}

/** Miga de pan: cada nivel de la ruta con su destino. La última entrada es la página actual. */
export function trail(route: Route): { label: string; to: Route }[] {
  const items: { label: string; to: Route }[] = [{ label: "Proyectos", to: { name: "home" } }];
  if (route.name === "stats") items.push({ label: "Estadísticas", to: route });
  if (route.name === "project-new") items.push({ label: "Nuevo proyecto", to: route });
  if (route.name === "run-short") items.push({ label: route.run, to: route });
  if (route.name === "not-found") items.push({ label: "Página no encontrada", to: route });
  if (!("project" in route)) return items;
  const { project } = route;
  items.push({ label: project, to: { name: "project", project } });
  if (route.name === "settings") items.push({ label: "Ajustes", to: route });
  if (route.name === "project-stats") items.push({ label: "Estadísticas", to: route });
  if (route.name === "docs") {
    items.push({ label: "Documentación", to: { name: "docs", project } });
    if (route.path) items.push({ label: route.path.split("/").pop()!, to: route });
  }
  if (route.name === "onboarding") items.push({ label: "Incorporación", to: route });
  if (route.name === "setup") {
    items.push({ label: "Creación", to: { name: "setup", project } });
    if (route.path) items.push({ label: route.path.split("/").pop()!, to: route });
  }
  if (route.name === "chat") {
    items.push({ label: "Chat", to: { name: "chat", project } });
    if (route.conversation) items.push({ label: "Conversación", to: route });
  }
  if (route.name === "phases" || "phase" in route) items.push({ label: "Fases", to: { name: "phases", project } });
  if ("phase" in route) items.push({ label: route.phase, to: { name: "phase", project, phase: route.phase } });
  if ("task" in route) items.push({ label: route.task, to: { name: "task", project, phase: route.phase, task: route.task } });
  if (route.name === "plan") {
    items.push({ label: "Planificación", to: { name: "plan", project, phase: route.phase } });
    if (route.conversation) items.push({ label: "Conversación", to: route });
  }
  if (route.name === "run") items.push({ label: `Run ${route.run.slice(0, 8)}`, to: route });
  return items;
}

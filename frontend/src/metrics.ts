// Statistics (H6.2 E6): formatting and scales without React or dependencies, to test them with `node --test`.
// Null is absence ("no data"), never zero; every sum says how many attempts contribute to it (D074).

export type Sum = { sum: number | null; attempts: number };

export const PROVENANCE: Record<string, [string, string]> = {
  requested: ["sol.", "Solicitado: selección congelada del intento"],
  reported: ["rep.", "Reportado por el proveedor"],
  derived: ["der.", "Derivado por el harness a partir de eventos reportados"],
  measured: ["med.", "Medido por el reloj del harness"],
  absent: ["—", "Ausente: nadie lo informó"],
};

export const ROLES: Record<string, string> = {
  planner: "Planificador", executor: "Ejecutor", reviewer: "Revisor", phase: "Evaluación de fase", chat: "Chat",
  bootstrap: "Propuesta de creación", definition: "Definición", planning: "Planificación",
};

export const PURPOSES: Record<string, string> = {
  task: "Tarea", phase_check: "Comprobación de fase", phase_close: "Cierre de fase", chat: "Chat",
  bootstrap_discovery: "Propuesta de creación", definition: "Definición", phase_planning: "Planificación de fase",
  project_import: "Importación",
  onboarding: "Incorporación",
};

const integer = new Intl.NumberFormat("es-ES", { maximumFractionDigits: 0 });
const short = new Intl.NumberFormat("es-ES", { notation: "compact", maximumFractionDigits: 1 });

/** Full integer (`12.345`). Null is "no data". */
export function count(value: number | null | undefined): string {
  return value == null ? "sin dato" : integer.format(value);
}

/** Compact for axes and headlines (`12,3 mil`); below 10 000, the full number. */
export function compact(value: number | null | undefined): string {
  if (value == null) return "sin dato";
  return Math.abs(value) < 10_000 ? integer.format(value) : short.format(value);
}

/** Reported API-equivalent cost: never an invoice or quota. Dollar cents below 1. */
export function usd(value: number | null | undefined): string {
  if (value == null) return "sin dato";
  return `${value.toLocaleString("es-ES", { minimumFractionDigits: value < 1 ? 4 : 2, maximumFractionDigits: value < 1 ? 4 : 2 })} US$`;
}

/** Human-readable duration from milliseconds or seconds. */
export function duration(value: number | null | undefined, unit: "ms" | "s" = "s"): string {
  if (value == null) return "sin dato";
  const seconds = unit === "ms" ? value / 1000 : value;
  if (seconds < 1) return `${Math.round(seconds * 1000)} ms`;
  if (seconds < 60) return `${seconds.toLocaleString("es-ES", { maximumFractionDigits: 1 })} s`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} min ${Math.round(seconds % 60)} s`;
  const hours = Math.floor(minutes / 60);
  return `${hours} h ${minutes % 60} min`;
}

export function percent(part: number, whole: number): string {
  return whole ? `${Math.round((part / whole) * 100)} %` : "sin dato";
}

/**
 * Coverage of a sum: "complete" if every attempt contributes, "partial" if only some do and "absent" if
 * none does. A partial sum is never presented as the total of the scope.
 */
export function coverage(value: Sum, attempts: number): "complete" | "partial" | "absent" {
  if (value.sum == null || value.attempts === 0) return "absent";
  return value.attempts >= attempts ? "complete" : "partial";
}

export function coverageText(value: Sum, attempts: number): string {
  const state = coverage(value, attempts);
  if (state === "absent") return attempts ? `ninguno de ${attempts} intentos lo informa` : "sin intentos";
  if (state === "partial") return `de ${value.attempts} de ${attempts} intentos`;
  return attempts === 1 ? "de 1 intento" : `de los ${attempts} intentos`;
}

/** "Round" step (1, 2 or 5 times a power of ten) not below `value`. */
export function niceStep(value: number): number {
  if (!(value > 0)) return 1;
  const power = 10 ** Math.floor(Math.log10(value));
  for (const step of [1, 2, 5, 10]) if (value <= step * power * (1 + 1e-9)) return step * power;
  return 10 * power;
}

/**
 * Axis from zero: top and ticks in round steps, about `count` divisions at most. With integer values the
 * ticks are integers (counts never show 2,5).
 */
export function axis(max: number, count = 4, integer = false): { top: number; ticks: number[] } {
  let step = niceStep(max > 0 ? max / count : 1);
  if (integer) step = Math.max(1, Math.round(step));
  const top = Math.max(step, Math.ceil(max / step - 1e-9) * step);
  const ticks = Array.from({ length: Math.round(top / step) + 1 }, (_, index) => Math.round(index * step * 1e6) / 1e6);
  return { top, ticks };
}

/** Linear scale from [0, max] to [0, length]; null has no length (it is not drawn as zero). */
export function scale(value: number | null, max: number, length: number): number | null {
  if (value == null) return null;
  return max > 0 ? (Math.max(0, value) / max) * length : 0;
}

/** Short name of a project from its root, if no id is registered for it. */
export function rootLabel(root: string | null, projects: { id: string; root: string }[]): string {
  if (root == null) return "sin raíz";
  return projects.find(project => project.root === root)?.id ?? root.split("/").filter(Boolean).pop() ?? root;
}

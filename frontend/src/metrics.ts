// Estadísticas (H6.2 E6): formato y escalas sin React ni dependencias, para probarlos con `node --test`.
// Null es ausencia («sin dato»), nunca cero; cada suma dice cuántos intentos la aportan (D074).

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

/** Entero completo (`12.345`). Null es «sin dato». */
export function count(value: number | null | undefined): string {
  return value == null ? "sin dato" : integer.format(value);
}

/** Compacto para ejes y titulares (`12,3 mil`); por debajo de 10 000, el número completo. */
export function compact(value: number | null | undefined): string {
  if (value == null) return "sin dato";
  return Math.abs(value) < 10_000 ? integer.format(value) : short.format(value);
}

/** Coste equivalente API reportado: nunca factura ni cuota. Céntimos de dólar por debajo de 1. */
export function usd(value: number | null | undefined): string {
  if (value == null) return "sin dato";
  return `${value.toLocaleString("es-ES", { minimumFractionDigits: value < 1 ? 4 : 2, maximumFractionDigits: value < 1 ? 4 : 2 })} US$`;
}

/** Duración legible desde milisegundos o segundos. */
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
 * Cobertura de una suma: «completa» si todos los intentos la aportan, «parcial» si solo algunos y «ausente» si
 * ninguno. Una suma parcial nunca se presenta como el total del ámbito.
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

/** Paso «redondo» (1, 2 o 5 por potencia de diez) que no baja de `value`. */
export function niceStep(value: number): number {
  if (!(value > 0)) return 1;
  const power = 10 ** Math.floor(Math.log10(value));
  for (const step of [1, 2, 5, 10]) if (value <= step * power * (1 + 1e-9)) return step * power;
  return 10 * power;
}

/**
 * Eje desde cero: tope y marcas en pasos redondos, unas `count` divisiones como mucho. Con valores enteros las
 * marcas son enteras (los conteos nunca muestran 2,5).
 */
export function axis(max: number, count = 4, integer = false): { top: number; ticks: number[] } {
  let step = niceStep(max > 0 ? max / count : 1);
  if (integer) step = Math.max(1, Math.round(step));
  const top = Math.max(step, Math.ceil(max / step - 1e-9) * step);
  const ticks = Array.from({ length: Math.round(top / step) + 1 }, (_, index) => Math.round(index * step * 1e6) / 1e6);
  return { top, ticks };
}

/** Escala lineal de [0, max] a [0, length]; null no tiene longitud (no se dibuja como cero). */
export function scale(value: number | null, max: number, length: number): number | null {
  if (value == null) return null;
  return max > 0 ? (Math.max(0, value) / max) * length : 0;
}

/** Nombre corto de un proyecto a partir de su raíz, si no hay id registrado para ella. */
export function rootLabel(root: string | null, projects: { id: string; root: string }[]): string {
  if (root == null) return "sin raíz";
  return projects.find(project => project.root === root)?.id ?? root.split("/").filter(Boolean).pop() ?? root;
}

/** P009-T020: elegir fase y tarea de los documentos en lugar de copiar el contrato a mano. */
import type { S } from "./managed-api";

type Source = S["TaskSourceRead"];

/** Fases que ofrece el documento, en su orden; una fase fijada por la página solo se ofrece a sí misma. */
export function sourcePhases(items: Source[], fixed?: string): string[] {
  const phases = [...new Set(items.map(item => item.phase_id))];
  return fixed ? phases.filter(phase => phase === fixed) : phases;
}

/** Tareas de la fase elegida; una tarea fijada por la página solo se ofrece a sí misma. */
export function sourceTasks(items: Source[], phase: string, fixed?: string): Source[] {
  return items.filter(item => item.phase_id === phase && (!fixed || item.task_id === fixed));
}

/** Cuerpo de `POST /runs`: con una tarea del documento lleva su hash (CAS); notas en blanco no se envían. */
export function runBody(source: Source | null, manual: { task: string; phase: string; text: string }, notes: string): S["RunCreate"] {
  const extra = notes.trim() ? { notes: notes.trim() } : {};
  if (source) return { task_id: source.task_id, phase_id: source.phase_id, text: source.text, source_sha256: source.sha256, ...extra };
  return { task_id: manual.task.trim(), phase_id: manual.phase.trim(), text: manual.text, ...extra };
}

// Diff unificado por líneas, sin dependencias (H6.2 E4). Solo muestra: la autoridad sigue siendo el hash
// que confirma el servidor, nunca este diff. Por encima del límite devuelve null en lugar de aproximar.

const CONTEXT = 3;
const MAX_CELLS = 4_000_000;

type Op = { kind: " " | "-" | "+"; line: string };

function lines(text: string): string[] {
  if (!text) return [];
  const parts = text.split("\n");
  if (parts[parts.length - 1] === "") parts.pop();
  return parts;
}

/** Operaciones de edición mínimas (LCS) entre dos listas de líneas; null si la tabla supera el límite. */
function operations(a: string[], b: string[]): Op[] | null {
  let start = 0;
  while (start < a.length && start < b.length && a[start] === b[start]) start++;
  let end = 0;
  while (end < a.length - start && end < b.length - start && a[a.length - 1 - end] === b[b.length - 1 - end]) end++;
  const x = a.slice(start, a.length - end), y = b.slice(start, b.length - end);
  if ((x.length + 1) * (y.length + 1) > MAX_CELLS) return null;
  const width = y.length + 1;
  const table = new Uint32Array((x.length + 1) * width);
  for (let i = x.length - 1; i >= 0; i--) {
    for (let j = y.length - 1; j >= 0; j--) {
      table[i * width + j] = x[i] === y[j] ? table[(i + 1) * width + j + 1] + 1
        : Math.max(table[(i + 1) * width + j], table[i * width + j + 1]);
    }
  }
  const middle: Op[] = [];
  let i = 0, j = 0;
  while (i < x.length && j < y.length) {
    if (x[i] === y[j]) { middle.push({ kind: " ", line: x[i] }); i++; j++; }
    else if (table[(i + 1) * width + j] >= table[i * width + j + 1]) middle.push({ kind: "-", line: x[i++] });
    else middle.push({ kind: "+", line: y[j++] });
  }
  while (i < x.length) middle.push({ kind: "-", line: x[i++] });
  while (j < y.length) middle.push({ kind: "+", line: y[j++] });
  return [...a.slice(0, start).map(line => ({ kind: " " as const, line })), ...middle,
    ...a.slice(a.length - end).map(line => ({ kind: " " as const, line }))];
}

/**
 * Diff unificado de `before` a `after` con tres líneas de contexto. `before` null es un archivo nuevo y `after`
 * null uno borrado. Devuelve "" si no hay cambios y null si el documento es demasiado grande para compararlo aquí.
 */
export function unifiedDiff(path: string, before: string | null, after: string | null): string | null {
  if (before === after) return "";
  const ops = operations(lines(before ?? ""), lines(after ?? ""));
  if (!ops) return null;
  const out = [`--- ${before === null ? "/dev/null" : `a/${path}`}`, `+++ ${after === null ? "/dev/null" : `b/${path}`}`];
  // Final de archivo distinto (con o sin salto de línea final): se marca como en Git.
  const eol = !!before && !!after && before.endsWith("\n") !== after.endsWith("\n");
  const changed = ops.map((op, index) => op.kind !== " " ? index : -1).filter(index => index >= 0);
  if (eol && changed[changed.length - 1] !== ops.length - 1) changed.push(ops.length - 1);
  let index = 0;
  while (index < changed.length) {
    const first = Math.max(0, changed[index] - CONTEXT);
    let last = Math.min(ops.length - 1, changed[index] + CONTEXT);
    while (index + 1 < changed.length && changed[index + 1] - CONTEXT <= last + 1) {
      index++;
      last = Math.min(ops.length - 1, changed[index] + CONTEXT);
    }
    index++;
    let oldStart = 1, newStart = 1;
    for (const op of ops.slice(0, first)) { if (op.kind !== "+") oldStart++; if (op.kind !== "-") newStart++; }
    const hunk = ops.slice(first, last + 1);
    const oldCount = hunk.filter(op => op.kind !== "+").length, newCount = hunk.filter(op => op.kind !== "-").length;
    out.push(`@@ -${oldCount ? oldStart : oldStart - 1},${oldCount} +${newCount ? newStart : newStart - 1},${newCount} @@`);
    for (const op of hunk) out.push(op.kind + op.line);
    if (eol && last === ops.length - 1) out.push("\\ Cambia el salto de línea final");
  }
  return out.join("\n") + "\n";
}

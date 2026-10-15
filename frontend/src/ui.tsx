import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import { managed, ManagedError } from "./managed-api";
import type { S } from "./managed-api";

export const message = (e: unknown) => e instanceof Error ? e.message : String(e);

/** Evidencia completa sin interpretar: null se muestra como «no registrado», nunca como vacío. */
export function Evidence({ title, value }: { title: string; value: unknown }) {
  return <details className="evidence"><summary>{title}</summary>
    <pre>{value === null ? "No registrado (null)" : JSON.stringify(value, null, 2)}</pre></details>;
}

export type Poll<T> = { data?: T; error?: string; missing: boolean; loading: boolean };

/**
 * Lectura periódica de un recurso de /api/managed. Un fallo conserva la última lectura y lo
 * indica; un 404 marca el recurso como ausente. `path` null no consulta nada.
 */
export function usePoll<T>(path: string | null, interval = 1500, refresh = 0): Poll<T> {
  const [state, setState] = useState<Poll<T>>({ missing: false, loading: path !== null });
  const current = useRef(path);
  useEffect(() => {
    // Releer el mismo recurso tras una acción conserva la lectura mostrada (y lo que cuelga de ella) hasta la nueva.
    const same = current.current === path;
    current.current = path;
    setState(previous => same && previous.data !== undefined ? { ...previous, loading: true } : { missing: false, loading: path !== null });
    if (path === null) return;
    let active = true;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try {
        const data = await managed<T>(path!);
        if (active) setState({ data, missing: false, loading: false });
      } catch (e) {
        if (!active) return;
        const missing = e instanceof ManagedError && e.status === 404;
        setState(previous => ({ data: missing ? undefined : previous.data, error: message(e), missing, loading: false }));
      }
      if (active && interval > 0) timer = setTimeout(() => void poll(), interval);
    }
    void poll();
    return () => { active = false; clearTimeout(timer); };
  }, [path, interval, refresh]);
  return state;
}

export function Loading({ children = "Cargando…" }: { children?: ReactNode }) {
  return <p role="status" className="state state-loading">{children}</p>;
}

export function Stale({ error }: { error?: string }) {
  return error ? <p role="status" className="state state-stale">Sin actualizar: {error}. Se muestra la última lectura.</p> : null;
}

export function Empty({ title, children }: { title: string; children?: ReactNode }) {
  return <div className="state state-empty"><p className="state-title">{title}</p>{children}</div>;
}

export function Alert({ children }: { children: ReactNode }) {
  return <p role="alert" className="state state-error">{children}</p>;
}

/** Titular de un recurso: su identificador (`P001-T003`) es el titular, en monoespaciada. */
export function PageHeader({ title, code = false, children, aside }: { title: ReactNode; code?: boolean; children?: ReactNode; aside?: ReactNode }) {
  return <header className="page-header">
    <div className="page-heading">
      <h1 tabIndex={-1} id="page-title" className={code ? "page-code" : undefined}>{title}</h1>
      {children && <div className="page-lede">{children}</div>}
    </div>
    {aside && <div className="page-aside">{aside}</div>}
  </header>;
}

export function Fields({ items }: { items: [string, ReactNode][] }) {
  return <dl className="fields">{items.map(([term, value]) => <div key={term}><dt>{term}</dt><dd>{value}</dd></div>)}</dl>;
}

export function Hash({ value, length = 12 }: { value?: string | null; length?: number }) {
  if (!value) return <span className="muted">no registrado</span>;
  return <code className="hash" title={value}>{value.slice(0, length)}</code>;
}

type Tone = "ok" | "active" | "attention" | "danger" | "neutral";

const RUN: Record<string, [string, Tone]> = {
  QUEUED: ["En cola", "active"], ACTIVE: ["En curso", "active"], PLANNING: ["Planificando", "active"],
  PREPARING: ["Preparando", "active"], EXECUTING: ["Ejecutando", "active"], REVIEWING: ["Revisando", "active"],
  VALIDATING: ["Validando", "active"], COMMITTING: ["Haciendo commit", "active"],
  ACCEPTANCE_READY: ["Aceptado, falta el commit", "attention"], BLOCKED: ["Bloqueado", "attention"],
  REVISION_LIMIT: ["Límite de revisiones", "attention"], RECOVERY_REQUIRED: ["Requiere recuperación", "attention"],
  STOPPED: ["Detenido", "neutral"], INTERRUPTED: ["Interrumpido", "danger"],
  COMMITTED: ["Commit hecho", "ok"], COMPLETED: ["Completado", "ok"], DONE: ["Terminado", "ok"],
  FAILED: ["Fallido", "danger"], ABORTED: ["Abortado", "danger"], INTENT: ["Intención registrada", "active"],
};

export const PHASE: Record<S["PhaseRead"]["status"], [string, Tone]> = {
  ACTIVE: ["Activa", "active"], CHECKING: ["Comprobando", "active"], READY_TO_CLOSE: ["Lista para cerrar", "attention"],
  NEEDS_RECONCILIATION: ["Necesita reconciliación", "attention"], BLOCKED: ["Bloqueada por decisiones", "attention"],
  CLOSING: ["Cerrando", "active"], CLOSED: ["Cerrada", "ok"], ABANDONED: ["Abandonada", "neutral"],
};

/** Estado con texto y tono; el color nunca es la única señal. Un estado desconocido se muestra tal cual. */
export function Status({ value, kind = "run" }: { value: string; kind?: "run" | "phase" }) {
  const known = kind === "phase" ? PHASE[value as S["PhaseRead"]["status"]] : RUN[value];
  const [label, tone] = known ?? [value, "neutral" as Tone];
  return <span className={`status status-${tone}`} title={value}><span className="status-mark" aria-hidden="true" />{label}</span>;
}

const TRACK: S["PhaseRead"]["status"][] = ["ACTIVE", "CHECKING", "READY_TO_CLOSE", "CLOSING", "CLOSED"];
const SIDINGS: Partial<Record<S["PhaseRead"]["status"], S["PhaseRead"]["status"]>> = {
  NEEDS_RECONCILIATION: "CHECKING", BLOCKED: "CHECKING", ABANDONED: "ACTIVE",
};

/** Ciclo de vida de la fase (D032/D034): la vía principal y, fuera de ella, los desvíos. */
export function PhaseRail({ status }: { status: S["PhaseRead"]["status"] }) {
  const siding = SIDINGS[status];
  const position = TRACK.indexOf(siding ?? status);
  return <div className="rail" role="img" aria-label={`Ciclo de vida de la fase: ${PHASE[status][0]}`}>
    <ol className="rail-track">
      {TRACK.map((step, index) => <li key={step} className={index < position ? "rail-past" : index === position ? (siding ? "rail-branch" : "rail-now") : "rail-next"}>
        <span className="rail-stop" aria-hidden="true" /><span className="rail-label">{PHASE[step][0]}</span>
        {index === position && siding && <span className="rail-siding">{PHASE[status][0]}</span>}
      </li>)}
    </ol>
  </div>;
}

export function Pagination({ offset, next, onChange, size = 30, label }: { offset: number; next: number | null | undefined; onChange: (offset: number) => void; size?: number; label: string }) {
  if (!offset && next == null) return null;
  return <nav className="pagination" aria-label={label}>
    <button type="button" className="button-quiet" disabled={!offset} onClick={() => onChange(Math.max(0, offset - size))}>Anteriores</button>
    <button type="button" className="button-quiet" disabled={next == null} onClick={() => onChange(next!)}>Siguientes</button>
  </nav>;
}

export function when(value: string | null | undefined) {
  if (!value) return <span className="muted">sin fecha</span>;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return <time dateTime={value} title={value}>{date.toLocaleString("es-ES", { dateStyle: "short", timeStyle: "short" })}</time>;
}

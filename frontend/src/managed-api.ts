import { sessionResponse } from "./session.ts";
import type { components } from "./api.generated";
export type S = components["schemas"];
export class ManagedError extends Error {
  status: number;
  constructor(status: number, message: string) { super(message); this.status = status; }
}
export async function managed<T>(path: string, body?: unknown, key?: string, method = "POST"): Promise<T> {
  const response = await fetch(`/api/managed${path}`, body === undefined ? undefined : {
    method, headers: { "Content-Type": "application/json", "X-Harness-Local": "1",
      ...(key ? { "Idempotency-Key": key } : {}) }, body: JSON.stringify(body),
  });
  sessionResponse(response);
  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new ManagedError(response.status, `${response.status} · ${data?.detail?.code ?? "request_failed"}: ${data?.detail?.diagnostic ?? JSON.stringify(data?.detail ?? "Servicio no disponible")}`);
  }
  return response.json() as Promise<T>;
}
// Keep the exact request and key until an acknowledged response, including across reloads.
export type Pending = { path: string; body: S["RunCreate"] | S["RunActionCreate"] | S["PhaseCheckCreate"] | S["PhaseCloseCreate"] | S["PhaseBatchNextCreate"] | S["PhaseReconcileTaskCreate"]
  | S["ChatMessageCreate"] | S["ChatProposalAcceptCreate"] | S["DocumentExportCreate"]
  | S["DocumentEditCreate"] | S["PlanningMessageCreate"] | S["DefinitionAcceptCreate"] | S["PhasePlanCreate"]; key: string };
const storageKey = "harness-managed-pending-v1";
export function readPending(): Pending | undefined {
  try { return JSON.parse(sessionStorage.getItem(storageKey) ?? "null") ?? undefined; } catch { return undefined; }
}
export function savePending(value?: Pending) {
  if (value) sessionStorage.setItem(storageKey, JSON.stringify(value));
  else sessionStorage.removeItem(storageKey);
}
export const managedApi = {
  activate: (id: string, body: S["ActivationCreate"]) => managed<S["ActivationRead"]>(`/projects/${id}/migration/activations`, body),
  transition: (id: string, action: string, body: S["ActivationTransition"]) => managed<S["ActivationRead"]>(`/activations/${id}/${action}`, body),
  confirm: (id: number, body: S["ConfirmStoppedCreate"]) => managed<S["ManagedRunRead"]>(`/jobs/${id}/confirm-stopped`, body),
};

// Reuse the last identical acknowledged request too: a fast response must not turn
// the second click into another job. A different body/version starts a new action.
export function jobRequest(path: string, body: Pending["body"]): Pending {
  const value = sessionStorage.getItem("harness-managed-last-request-v1");
  const previous: Pending | null = value ? JSON.parse(value) : null;
  if (previous?.path === path && JSON.stringify(previous.body) === JSON.stringify(body)) return previous;
  const request = { path, body, key: crypto.randomUUID() };
  sessionStorage.setItem("harness-managed-last-request-v1", JSON.stringify(request));
  return request;
}

// Altas sin job (conversaciones, D085): la clave se conserva mientras el mismo cuerpo no tenga respuesta
// confirmada, también al recargar; reenviar tras perder la respuesta devuelve la misma conversación.
// Tras la respuesta o un rechazo definitivo, el envío siguiente lleva otra clave y crea otra.
const creationKey = "harness-managed-creation-v1";
export async function createOnce<T>(path: string, body: unknown): Promise<T> {
  const text = JSON.stringify(body);
  let saved: { path: string; body: string; key: string } | null = null;
  try { saved = JSON.parse(sessionStorage.getItem(creationKey) ?? "null"); } catch { /* sin almacenamiento */ }
  const key = saved?.path === path && saved.body === text ? saved.key : crypto.randomUUID();
  const forget = () => { try { sessionStorage.removeItem(creationKey); } catch { /* sin almacenamiento */ } };
  try { sessionStorage.setItem(creationKey, JSON.stringify({ path, body: text, key })); } catch { /* sin almacenamiento */ }
  try {
    const created = await managed<T>(path, body, key);
    forget();
    return created;
  } catch (e) {
    if (e instanceof ManagedError && e.status >= 400 && e.status < 500 && e.status !== 401) forget();
    throw e;
  }
}

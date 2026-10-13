import type { components } from "./api.generated";
export type S = components["schemas"];
export class ManagedError extends Error {
  status: number;
  constructor(status: number, message: string) { super(message); this.status = status; }
}
export async function managed<T>(path: string, body?: unknown, key?: string): Promise<T> {
  const response = await fetch(`/api/managed${path}`, body === undefined ? undefined : {
    method: "POST", headers: { "Content-Type": "application/json", "X-Harness-Local": "1",
      ...(key ? { "Idempotency-Key": key } : {}) }, body: JSON.stringify(body),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new ManagedError(response.status, `${response.status} · ${data?.detail?.code ?? "request_failed"}: ${data?.detail?.diagnostic ?? JSON.stringify(data?.detail ?? "Servicio no disponible")}`);
  }
  return response.json() as Promise<T>;
}
// Keep the exact request and key until an acknowledged response, including across reloads.
export type Pending = { path: string; body: S["RunCreate"] | S["RunActionCreate"] | S["PhaseCheckCreate"] | S["PhaseCloseCreate"] | S["PhaseBatchNextCreate"] | S["PhaseReconcileTaskCreate"]
  | S["ChatMessageCreate"] | S["ChatProposalAcceptCreate"]; key: string };
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

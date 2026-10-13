import type { components, operations } from "./api.generated";

export type Simulation = components["schemas"]["SimulationRead"];
type SimulationCreate = operations["create_simulation"]["requestBody"]["content"]["application/json"];
type SimulationList = operations["list_simulations"]["responses"][200]["content"]["application/json"];
type Observation = components["schemas"]["ObservationRead"];

const SAFE = new Set(["GET", "HEAD", "OPTIONS"]);

// Every mutation carries the local CSRF header required by the service guard (D033).
export async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const method = (options?.method ?? "GET").toUpperCase();
  const init = SAFE.has(method) ? options : { ...options, headers: { ...(options?.headers as Record<string, string> | undefined), "X-Harness-Local": "1" } };
  const response = await fetch(path, init);
  if (!response.ok) {
    throw new Error(`La solicitud falló (${response.status}). Comprueba que el servicio esté disponible.`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  list: () => request<SimulationList>("/api/simulations"),
  create: (body: SimulationCreate) => request<Simulation>("/api/simulations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }),
  setObservation: (base: string, enabled: boolean) => request<Observation>(`${base}/observation`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ enabled }),
  }),
};

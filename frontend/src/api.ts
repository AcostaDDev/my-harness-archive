import type { components, operations } from "./api.generated";

export type Simulation = components["schemas"]["SimulationRead"];
type SimulationCreate = operations["create_simulation"]["requestBody"]["content"]["application/json"];
type SimulationList = operations["list_simulations"]["responses"][200]["content"]["application/json"];

export async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, options);
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
};

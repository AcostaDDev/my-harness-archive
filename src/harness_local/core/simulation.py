"""Recorrido H0.3; no es el motor de intentos ni una aceptación de tarea."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4


@dataclass(frozen=True)
class Simulation:
    id: str
    title: str
    created_at: datetime
    events: tuple[str, ...]


class SimulationAdapter(Protocol):
    def execute(self) -> tuple[str, ...]: ...


class SimulationRepository(Protocol):
    def save(self, simulation: Simulation) -> None: ...
    def list(self) -> list[Simulation]: ...
    def get(self, simulation_id: str) -> Simulation | None: ...


class SimulationService:
    def __init__(self, repository: SimulationRepository, adapter: SimulationAdapter):
        self.repository = repository
        self.adapter = adapter

    def create(self, title: str) -> Simulation:
        title = title.strip()
        if not 1 <= len(title) <= 120:
            raise ValueError("El título debe tener entre 1 y 120 caracteres.")
        # Ejecutar fuera de una transacción; solo guardar un resultado completo.
        events = self.adapter.execute()
        simulation = Simulation(str(uuid4()), title, datetime.now(timezone.utc), events)
        self.repository.save(simulation)
        return simulation

    def list(self) -> list[Simulation]:
        return self.repository.list()

    def get(self, simulation_id: str) -> Simulation | None:
        return self.repository.get(simulation_id)

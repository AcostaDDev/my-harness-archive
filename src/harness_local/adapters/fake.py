"""Deterministic adapter: uses no network, processes, CLI or checkouts."""


class FakeSimulationAdapter:
    def execute(self) -> tuple[str, ...]:
        return (
            "Preparación de datos sintéticos completada.",
            "El adaptador falso produjo un resultado local.",
            "Simulación terminada; no representa revisión, aceptación ni commit.",
        )

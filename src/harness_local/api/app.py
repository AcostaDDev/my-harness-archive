from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from harness_local.adapters.fake import FakeSimulationAdapter
from harness_local.api.schemas import HealthRead, SimulationCreate, SimulationRead
from harness_local.core.simulation import SimulationService
from harness_local.storage.database import database_url, make_engine
from harness_local.storage.repository import SQLiteSimulationRepository
from harness_local.storage.schema import require_schema


def create_app(url: str | None = None, ui_dir: Path | None = None) -> FastAPI:
    engine = make_engine(url or database_url())
    service = SimulationService(SQLiteSimulationRepository(engine), FakeSimulationAdapter())

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            require_schema(engine)
            yield
        finally:
            engine.dispose()

    app = FastAPI(title="Harness Local", version="0.1.0", lifespan=lifespan,
                  docs_url=None, redoc_url=None)

    @app.get("/api/health", response_model=HealthRead, operation_id="health")
    def health():
        with engine.connect() as connection:
            connection.execute(text("SELECT id FROM simulations LIMIT 1"))
        return HealthRead()

    @app.get("/api/simulations", response_model=list[SimulationRead], operation_id="list_simulations")
    def list_simulations():
        return service.list()

    @app.post("/api/simulations", response_model=SimulationRead, status_code=201,
              operation_id="create_simulation")
    def create_simulation(request: SimulationCreate):
        return service.create(request.title)

    @app.get("/api/simulations/{simulation_id}", response_model=SimulationRead,
             operation_id="get_simulation")
    def get_simulation(simulation_id: UUID):
        simulation = service.get(str(simulation_id))
        if simulation is None:
            raise HTTPException(404, "Simulación no encontrada.")
        return simulation

    assets = ui_dir if ui_dir is not None else Path.cwd() / "frontend/dist"
    if (assets / "index.html").is_file():
        app.mount("/", StaticFiles(directory=assets, html=True), name="ui")
    return app

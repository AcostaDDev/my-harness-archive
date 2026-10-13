import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy import text

from harness_local.adapters.fake import FakeSimulationAdapter
from harness_local.api.legacy import legacy_router
from harness_local.api.managed import managed_router
from harness_local.api.schemas import HealthRead, ProblemResponse, SimulationCreate, SimulationRead
from harness_local.api.security import local_request
from harness_local.core.simulation import SimulationService
from harness_local.storage.database import database_url, make_engine
from harness_local.storage.repository import SQLiteSimulationRepository
from harness_local.storage.schema import require_schema
from harness_local.storage.backup import is_read_only_archive, verify_bundle
from harness_local.services.managed_runtime import ManagedConfig, ManagedRuntime
from harness_local.services.observation import LegacyObserver


def create_app(url: str | None = None, ui_dir: Path | None = None,
               managed: ManagedConfig | None = None) -> FastAPI:
    """`managed` explícito o HARNESS_MANAGED_CONFIG al arrancar; sin ninguno, la API gestionada solo lee."""
    engine = make_engine(url or database_url())
    service = SimulationService(SQLiteSimulationRepository(engine), FakeSimulationAdapter())

    observer = LegacyObserver(engine)
    runtime = ManagedRuntime(engine, managed)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            require_schema(engine)
            restored = is_read_only_archive(engine)
            if restored:
                verify_bundle(Path(engine.url.database).resolve().parent)
            await asyncio.to_thread(runtime.start)
            try:
                if not restored:
                    await asyncio.to_thread(observer.scan, True)
                task = None if restored else asyncio.create_task(observer.run())
                try:
                    yield
                finally:
                    if task is not None:
                        observer.stop()
                        await task
            finally:
                await asyncio.to_thread(runtime.stop)
        finally:
            engine.dispose()

    app = FastAPI(title="Harness Local", version="0.1.0", lifespan=lifespan,
                  docs_url=None, redoc_url=None)
    app.include_router(legacy_router(engine))
    app.include_router(managed_router(runtime))

    @app.middleware('http')
    async def restored_read_only(request, call_next):
        if request.method not in ('GET', 'HEAD', 'OPTIONS') and is_read_only_archive(engine):
            return JSONResponse(status_code=409, content={'code': 'restored_read_only',
                'diagnostic': 'Restauración de consulta; no autoriza escritores ni reanudar procesos.'})
        return await call_next(request)

    @app.get("/api/health", response_model=HealthRead, operation_id="health")
    def health():
        with engine.connect() as connection:
            connection.execute(text("SELECT id FROM simulations LIMIT 1"))
        return HealthRead()

    @app.get("/api/simulations", response_model=list[SimulationRead], operation_id="list_simulations")
    def list_simulations():
        return service.list()

    # H3.4 (D033): las mutaciones H0/H1 comparten la guardia local de /api/managed.
    @app.post("/api/simulations", response_model=SimulationRead, status_code=201,
              operation_id="create_simulation", dependencies=[Depends(local_request)],
              responses={403: {"model": ProblemResponse}})
    def create_simulation(request: SimulationCreate):
        return service.create(request.title)

    @app.get("/api/simulations/{simulation_id}", response_model=SimulationRead,
             operation_id="get_simulation")
    def get_simulation(simulation_id: UUID):
        simulation = service.get(str(simulation_id))
        if simulation is None:
            raise HTTPException(404, "Simulación no encontrada.")
        return simulation

    assets = ui_dir if ui_dir is not None else Path(__file__).resolve().parents[1] / "web"
    if (assets / "index.html").is_file():
        app.mount("/", StaticFiles(directory=assets, html=True), name="ui")
    return app

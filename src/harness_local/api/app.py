import asyncio
import re
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text

from harness_local.adapters.fake import FakeSimulationAdapter
from harness_local.api.managed import managed_router
from harness_local.api.schemas import HealthRead, ProblemResponse, SimulationCreate, SimulationRead
from harness_local.api.security import local_request
from harness_local.api.session import LocalSessions, session_router
from harness_local.core.simulation import SimulationService
from harness_local.i18n import message
from harness_local.storage.database import database_url, make_engine
from harness_local.storage.repository import SQLiteSimulationRepository
from harness_local.storage.schema import require_schema
from harness_local.storage.preferences import language
from harness_local.storage.backup import is_read_only_archive, verify_bundle
from harness_local.services.managed_runtime import ManagedConfig, ManagedRuntime


def create_app(url: str | None = None, ui_dir: Path | None = None,
               managed: ManagedConfig | None = None) -> FastAPI:
    """Explicit `managed` or HARNESS_MANAGED_CONFIG at startup; with neither, the managed API only reads."""
    engine = make_engine(url or database_url())
    service = SimulationService(SQLiteSimulationRepository(engine), FakeSimulationAdapter())

    sessions = LocalSessions(lambda: language(engine))
    runtime = ManagedRuntime(engine, managed)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            require_schema(engine)
            restored = is_read_only_archive(engine)
            if restored:
                verify_bundle(Path(engine.url.database).resolve().parent)
            sessions.start()
            await asyncio.to_thread(runtime.start)
            try:
                yield
            finally:
                await asyncio.to_thread(runtime.stop)
        finally:
            sessions.stop()
            engine.dispose()

    app = FastAPI(title="Harness Local", version="0.1.0", lifespan=lifespan,
                  docs_url=None, redoc_url=None)
    app.state.sessions = sessions
    app.state.language = sessions.language
    app.include_router(session_router(sessions))
    app.include_router(managed_router(runtime))

    @app.middleware('http')
    async def restored_read_only(request, call_next):
        if request.url.path != '/api/session' and request.method not in ('GET', 'HEAD', 'OPTIONS') and is_read_only_archive(engine):
            return JSONResponse(status_code=409, content={'code': 'restored_read_only',
                'diagnostic': message('api.restored_read_only', language(engine))})
        return await call_next(request)

    @app.middleware('http')
    async def session_guard(request, call_next):
        try:
            local_request(request, request.headers.get('x-harness-local'))
            # Only the static login shell and the credential exchange are public.
            # Unknown API routes and OpenAPI also pass the guard.
            if (request.url.path.startswith('/api') or request.url.path == '/openapi.json') and not (
                    request.url.path == '/api/session' and request.method == 'POST'):
                sessions.require(request)
            response = await call_next(request)
        except HTTPException as error:
            response = JSONResponse(status_code=error.status_code, content={'detail': error.detail})
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @app.get("/api/health", response_model=HealthRead, operation_id="health")
    def health():
        with engine.connect() as connection:
            connection.execute(text("SELECT id FROM simulations LIMIT 1"))
        return HealthRead()

    @app.get("/api/simulations", response_model=list[SimulationRead], operation_id="list_simulations")
    def list_simulations():
        return service.list()

    # H3.4 (D033): the H0/H1 mutations share the local guard of /api/managed.
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
            raise HTTPException(404, message("api.simulation_not_found", language(engine)))
        return simulation

    assets = ui_dir if ui_dir is not None else Path(__file__).resolve().parents[1] / "web"
    if (assets / "index.html").is_file():
        app.mount("/", SPAStaticFiles(directory=assets, html=True), name="ui")
    return app


ASSET = re.compile(r"(^|/)assets/|\.(js|mjs|css|map|png|jpe?g|gif|svg|ico|webp|woff2?|ttf|json|txt|webmanifest)$")


class SPAStaticFiles(StaticFiles):
    """UI routes (D076): a GET without a file outside `/api/` receives `index.html`.

    API 404s remain JSON; a missing static asset is still 404
    so HTML is not served in its place. Phase codes may contain dots. A URL ending in `.md` is
    a viewer document (H6.2 E3), also under an `assets/` folder of the checkout.
    """

    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as error:
            if (error.status_code != 404 or scope["method"] not in ("GET", "HEAD")
                    or path.split("/", 1)[0] == "api" or (ASSET.search(path) and not path.endswith(".md"))):
                raise
            return await super().get_response("index.html", scope)

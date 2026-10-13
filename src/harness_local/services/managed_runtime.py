"""Composición opt-in del modo gestionado dentro del servicio local (salida H2, parte 1).

Sin configuración explícita no hay proyectos, puertos ni supervisor: la API
gestionada solo lee. Los proyectos se registran en el servidor; el cliente HTTP
los nombra por identificador y nunca aporta rutas, comandos ni selecciones.
El supervisor es un único hilo del proceso Uvicorn que llama a
`LocalSupervisor.run_once`; la cola, la exclusión y la recuperación siguen en
SQLite. Apagar el servicio no libera un job a medias: su lease vence y queda
RECOVERY_REQUIRED hasta una confirmación explícita.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import importlib
import logging
import os
from pathlib import Path
import re
from threading import Event, Lock, Thread

from harness_local.core.engine.context import ProjectContext
from harness_local.services.managed import LocalSupervisor
from harness_local.services.migration import MigrationService
from harness_local.storage.managed import SQLiteManagedRepository
from harness_local.storage.prompts import PromptRepository
from harness_local.storage.managed_views import SQLiteManagedViews

logger = logging.getLogger(__name__)

CONFIG_ENV = "HARNESS_MANAGED_CONFIG"
PROJECT_ID = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}")
REQUIRED_VERSIONS = frozenset({"engine", "agent_adapter", "commands", "evidence"})


@dataclass(frozen=True)
class ManagedProject:
    """Checkout gestionable con contexto y versiones congelables fijados por quien arranca el servicio."""

    id: str
    context: ProjectContext
    versions: Mapping[str, str | None]
    permission_authority: Mapping | None = None
    # H3.4: tipo del tag de cierre de fase; ligero por defecto, anotado con intención determinista.
    tag_kind: str = "lightweight"
    # H4.2: capacidad opt-in para crear exclusivamente en este destino vacío.
    bootstrap_enabled: bool = False


@dataclass(frozen=True)
class ManagedConfig:
    """`ports_factory(context, versions)` y `commit_factory(context, versions)` como en `LocalSupervisor`.

    Los adaptadores CLI H2.3 y Git H2.4 solo intervienen si se inyectan aquí.
    `supervisor=True` arranca el hilo ejecutor con el servicio; por defecto los jobs
    quedan en cola persistida sin ejecutarse.
    """

    projects: tuple[ManagedProject, ...] = ()
    ports_factory: Callable | None = None
    commit_factory: Callable | None = None
    supervisor: bool = False
    lease_seconds: float = 30.0
    poll_seconds: float = 0.5
    migrations_dir: Path | None = None


def load_config(spec: str | None = None) -> ManagedConfig:
    """`módulo:atributo` en HARNESS_MANAGED_CONFIG: un ManagedConfig o una función que lo devuelve."""
    spec = spec if spec is not None else os.environ.get(CONFIG_ENV)
    if not spec:
        return ManagedConfig()
    module, separator, attribute = spec.partition(":")
    if not separator or not module or not attribute:
        raise ValueError(f"{CONFIG_ENV} debe tener la forma módulo:atributo")
    value = getattr(importlib.import_module(module), attribute)
    config = value() if callable(value) and not isinstance(value, ManagedConfig) else value
    if not isinstance(config, ManagedConfig):
        raise TypeError(f"{spec} no produce un ManagedConfig")
    return config


def _validate(config: ManagedConfig, database: Path, migrations_dir: Path) -> None:
    ids, roots = set(), set()
    for project in config.projects:
        if not isinstance(project.id, str) or not PROJECT_ID.fullmatch(project.id):
            raise ValueError(f"Identificador de proyecto inválido: {project.id!r}")
        if project.id in ids:
            raise ValueError(f"Proyecto duplicado: {project.id}")
        if project.context.root in roots:
            raise ValueError(f"Dos proyectos comparten la raíz {project.context.root}")
        ids.add(project.id)
        roots.add(project.context.root)
        if type(project.bootstrap_enabled) is not bool:
            raise ValueError('bootstrap_enabled must be an explicit boolean')
        if project.bootstrap_enabled and config.commit_factory is None:
            raise ValueError('Bootstrap requires an explicit Git writer')
        if project.tag_kind not in ("lightweight", "annotated"):
            raise ValueError(f"Tipo de tag de fase inválido para {project.id}: {project.tag_kind!r}")
        if not isinstance(project.versions, Mapping) or not REQUIRED_VERSIONS <= project.versions.keys():
            raise ValueError(f"Versiones explícitas incompletas para {project.id}; desconocidas como null")
        if project.permission_authority is not None:
            from harness_local.core.engine.permissions import KINDS, LAYERS
            authority = project.permission_authority
            if set(authority) != set(LAYERS) or any(
                not isinstance(values, Mapping) or not set(values) <= set(KINDS)
                or any(not isinstance(targets, (list, tuple)) or not all(isinstance(t, str) and t.strip() for t in targets)
                       for targets in values.values()) for values in authority.values()):
                raise ValueError('Explicit global/project/contract/provider permission ceilings required')
        for path, name in ((database, "La base SQLite"), (migrations_dir, "El directorio de migraciones")):
            if path.is_relative_to(project.context.root) or project.context.root.is_relative_to(path):
                raise ValueError(f"{name} debe estar fuera del checkout de {project.id}")
    if config.supervisor and config.ports_factory is None:
        raise ValueError("El supervisor exige una ports_factory explícita")


class SupervisorWorker:
    """Un hilo, un job cada vez. Errores ya quedan en cuarentena por run_once; el bucle continúa."""

    def __init__(self, supervisor: LocalSupervisor, poll_seconds: float):
        self.supervisor = supervisor
        self.poll_seconds = poll_seconds
        self.wake, self.stopping = Event(), Event()
        self.thread: Thread | None = None
        self.last_error: str | None = None
        self._lock = Lock()

    def start(self) -> None:
        self.thread = Thread(target=self._loop, name="managed-supervisor", daemon=True)
        self.thread.start()

    def notify(self) -> None:
        self.wake.set()

    def _loop(self) -> None:
        while not self.stopping.is_set():
            try:
                claimed = self.supervisor.run_once()
            except Exception as exc:  # job en RECOVERY_REQUIRED o fallo local; nunca se reintenta solo
                with self._lock:
                    self.last_error = f"{type(exc).__name__}: {exc}"
                logger.exception("Job gestionado detenido; requiere conciliación explícita.")
                claimed = None
            if claimed is None:
                self.wake.wait(self.poll_seconds)
                self.wake.clear()

    def alive(self) -> bool:
        return self.thread is not None and self.thread.is_alive()

    def stop(self, timeout: float) -> None:
        """Sin interrumpir el job en curso: si no termina a tiempo, su lease decidirá la recuperación."""
        self.stopping.set()
        self.wake.set()
        if self.thread is not None:
            self.thread.join(timeout)

    def error(self) -> str | None:
        with self._lock:
            return self.last_error


class ManagedRuntime:
    """Se compone en el lifespan: exportar OpenAPI no conecta SQLite ni importa configuración."""

    def __init__(self, engine, config: ManagedConfig | None = None):
        self.engine = engine
        self._explicit = config
        self.config: ManagedConfig | None = None
        self.repository = self.migration = self.views = self.worker = None
        self.projects: dict[str, ManagedProject] = {}

    def start(self) -> None:
        from harness_local.storage.backup import is_read_only_archive
        # Ni importar configuración del usuario: una factory puede tener efectos al cargar.
        if is_read_only_archive(self.engine):
            config = ManagedConfig()
        else:
            config = self._explicit if self._explicit is not None else load_config()
        database = Path(self.engine.url.database).resolve()
        migration = MigrationService(self.engine, migrations_dir=config.migrations_dir)
        _validate(config, database, migration.migrations_dir)
        self.config, self.migration = config, migration
        self.repository = SQLiteManagedRepository(self.engine)
        self.views = SQLiteManagedViews(self.engine)
        self.prompts = PromptRepository(self.engine)
        from harness_local.storage.permissions import PermissionRepository
        self.permissions = PermissionRepository(self.repository)
        from harness_local.storage.phases import PhaseRepository
        self.phases = PhaseRepository(self.repository)
        from harness_local.storage.chat import ChatRepository
        self.chat = ChatRepository(self.repository)
        self.projects = {project.id: project for project in config.projects}
        if config.supervisor:
            supervisor = LocalSupervisor(self.repository, config.ports_factory, lease_seconds=config.lease_seconds,
                                         commit_factory=config.commit_factory)
            self.worker = SupervisorWorker(supervisor, config.poll_seconds)
            self.worker.start()

    def stop(self) -> None:
        if self.worker is not None:
            self.worker.stop(timeout=self.config.lease_seconds)

    def ready(self) -> None:
        if self.repository is None:
            raise RuntimeError("Servicio gestionado no iniciado")

    def project(self, project_id: str) -> ManagedProject:
        self.ready()
        try:
            return self.projects[project_id]
        except KeyError:
            raise LookupError("Proyecto gestionado no registrado en este servicio.") from None

    def project_id(self, root: str) -> str | None:
        return next((p.id for p in self.projects.values() if str(p.context.root) == root), None)

    def notify(self) -> None:
        if self.worker is not None:
            self.worker.notify()

    def supervisor_status(self) -> dict:
        self.ready()
        return {"enabled": self.worker is not None, "alive": bool(self.worker and self.worker.alive()),
                "last_error": self.worker.error() if self.worker else None,
                "ports_configured": self.config.ports_factory is not None,
                "commit_writer_configured": self.config.commit_factory is not None}

"""Polling agrupado de orígenes opt-in. Sin procesos, motor ni agentes."""
import asyncio
import logging
from pathlib import Path
import time

from sqlalchemy.exc import SQLAlchemyError

from harness_local.adapters.legacy import LocalLegacyReader
from harness_local.storage.legacy import SQLiteLegacyRepository
from harness_local.storage.observation import SQLiteObservationRepository

logger = logging.getLogger(__name__)


class LegacyObserver:
    def __init__(self, engine, interval=0.5, reconcile_interval=30.0):
        self.index = SQLiteLegacyRepository(engine)
        self.control = SQLiteObservationRepository(engine)
        self.interval = interval
        self.reconcile_interval = reconcile_interval
        self.readers = {}
        self.last_full = {}
        self.stopped = asyncio.Event()

    def scan(self, reconcile=False):
        roots = self.control.roots()
        self.readers = {root: reader for root, reader in self.readers.items() if root in roots}
        self.last_full = {root: value for root, value in self.last_full.items() if root in roots}
        for root in roots:
            reader = self.readers.setdefault(root, LocalLegacyReader(incremental=True))
            try:
                if Path(self.index.engine.url.database).resolve().is_relative_to(Path(root)):
                    raise ValueError("El índice SQLite debe estar fuera del checkout de origen.")
                now = time.monotonic()
                if reconcile or now - self.last_full.get(root, 0) >= self.reconcile_interval:
                    reader.clear()
                    self.last_full[root] = now
                inventory = reader.read(root)
                self.index.replace(inventory, watched=True)
            except (OSError, ValueError) as error:
                reader.clear()
                # No reemplazar todo el índice por ausencias si no se puede leer la raíz.
                self.control.failed(root, str(error))

    async def run(self):
        while not self.stopped.is_set():
            try:
                await asyncio.wait_for(self.stopped.wait(), timeout=self.interval)
            except TimeoutError:
                try:
                    await asyncio.to_thread(self.scan)
                except SQLAlchemyError:
                    logger.exception("Error local de persistencia del observador; reintentará en el siguiente ciclo.")

    def stop(self):
        self.stopped.set()

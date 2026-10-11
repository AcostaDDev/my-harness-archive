"""Control persistido y feed de invalidación; no son eventos del motor."""
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from harness_local.storage.models import LegacySourceRow as Source, LegacyEventRow as Event
from harness_local.storage.navigation import identifier


class SQLiteObservationRepository:
    def __init__(self, engine):
        self.engine = engine

    def roots(self):
        with Session(self.engine) as session:
            return list(session.scalars(select(Source.root).where(Source.watch_enabled).order_by(Source.root)))

    def set_watch(self, root, enabled):
        with Session(self.engine) as session, session.begin():
            session.execute(text("UPDATE legacy_sources SET root = root WHERE root = :root"), {"root": root})
            source = session.get(Source, root)
            if source is None:
                raise LookupError("Origen no importado.")
            if enabled and self.engine.url.database and Path(
                    self.engine.url.database).resolve().is_relative_to(Path(root)):
                raise ValueError("El índice SQLite debe estar fuera del checkout de origen.")
            if source.watch_enabled != enabled:
                source.watch_enabled = enabled
                session.add(Event(root=root, kind="watch_changed", observed_at=datetime.now(timezone.utc).isoformat(),
                                  payload={"enabled": enabled}))
        return self.status(root)

    def status(self, root):
        with Session(self.engine) as session:
            source = session.get(Source, root)
            if source is None:
                raise LookupError("Origen no importado.")
            return {"enabled": source.watch_enabled, "diagnostic": source.diagnostic}

    def failed(self, root, diagnostic):
        with Session(self.engine) as session, session.begin():
            session.execute(text("UPDATE legacy_sources SET root = root WHERE root = :root"), {"root": root})
            source = session.get(Source, root)
            if source is not None and source.watch_enabled and source.diagnostic != diagnostic:
                source.diagnostic = diagnostic
                session.add(Event(root=root, kind="observation_error", observed_at=datetime.now(timezone.utc).isoformat(),
                                  payload={"diagnostic": diagnostic}))

    def events(self, after=0, limit=100):
        with Session(self.engine) as session:
            head = session.scalar(select(func.max(Event.id))) or 0
            if after > head:
                raise ValueError("Cursor fuera del historial; recargar el índice y reiniciar desde cero.")
            rows = session.scalars(select(Event).where(Event.id > after).order_by(Event.id).limit(limit)).all()
            items = [{"id": r.id, "project_id": identifier(r.root), "root": r.root, "kind": r.kind,
                      "observed_at": r.observed_at, "payload": r.payload} for r in rows]
            return {"items": items, "cursor": items[-1]["id"] if items else after,
                    "has_more": bool(items and items[-1]["id"] < head)}

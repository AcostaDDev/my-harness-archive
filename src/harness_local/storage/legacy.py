from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from harness_local.core.legacy import LegacyArtifact, LegacyInventory, LegacyRun
from harness_local.storage.models import LegacyArtifactRow, LegacyRunRow, LegacySourceRow, LegacyEventRow


class SQLiteLegacyRepository:
    def __init__(self, engine: Engine):
        self.engine = engine

    def replace(self, inventory: LegacyInventory, *, watched: bool = False) -> None:
        root = inventory.root
        database = Path(self.engine.url.database).resolve()
        if database.is_relative_to(Path(root)):
            raise ValueError("El índice SQLite debe estar fuera del checkout de origen.")
        with Session(self.engine) as session, session.begin():
            # Serialize index comparisons/event insertion, including concurrent CLI imports.
            session.execute(text("UPDATE legacy_sources SET root = root WHERE root = :root"), {"root": root})
            source = session.get(LegacySourceRow, root)
            if watched and (source is None or not source.watch_enabled):
                return
            created = source is None
            if created:
                source = LegacySourceRow(root=root)
                session.add(source)
            now = datetime.now(timezone.utc).isoformat()
            source.observed_at = source.observed_at or now
            session.flush()
            changed = 0
            for run in inventory.runs:
                row = session.get(LegacyRunRow, (root, run.path))
                if row is None or row.identity != run.identity:
                    session.merge(LegacyRunRow(root=root, path=run.path, identity=run.identity))
                    changed += 1
            session.flush()
            observed_paths = {artifact.path for artifact in inventory.artifacts}
            for row in session.scalars(select(LegacyArtifactRow).where(LegacyArtifactRow.root == root)):
                if row.path not in observed_paths and row.status != "missing":
                    row.status = "missing"
                    row.payload = row.sha256 = row.size_bytes = None
                    row.diagnostic = "Archivo anteriormente observado, ahora ausente."
                    changed += 1
            fields = ("run_path", "kind", "format", "status", "sha256", "size_bytes", "payload", "diagnostic")
            for artifact in inventory.artifacts:
                row = session.get(LegacyArtifactRow, (root, artifact.path))
                values = {name: getattr(artifact, name) for name in fields}
                if row is None or any(getattr(row, name) != value for name, value in values.items()):
                    session.merge(LegacyArtifactRow(root=root, path=artifact.path, **values))
                    changed += 1
            recovered = source.diagnostic is not None
            source.diagnostic = None
            if created or changed or recovered:
                source.observed_at = now
                session.add(LegacyEventRow(root=root, kind="index_updated", observed_at=now,
                    payload={"changed_records": changed, "recovered": recovered}))

    def get(self, root: str) -> LegacyInventory | None:
        root = str(Path(root).expanduser().resolve())
        with Session(self.engine) as session:
            if session.get(LegacySourceRow, root) is None:
                return None
            runs = session.scalars(select(LegacyRunRow).where(LegacyRunRow.root == root)
                                   .order_by(LegacyRunRow.path))
            artifacts = session.scalars(select(LegacyArtifactRow).where(LegacyArtifactRow.root == root)
                                        .order_by(LegacyArtifactRow.path))
            return LegacyInventory(root, tuple(LegacyRun(r.path, r.identity) for r in runs), tuple(
                LegacyArtifact(a.path, a.run_path, a.kind, a.format, a.status,
                               a.sha256, a.size_bytes, a.payload, a.diagnostic) for a in artifacts))

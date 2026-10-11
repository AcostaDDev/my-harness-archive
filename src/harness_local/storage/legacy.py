from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from harness_local.core.legacy import LegacyArtifact, LegacyInventory, LegacyRun
from harness_local.storage.models import LegacyArtifactRow, LegacyRunRow, LegacySourceRow


class SQLiteLegacyRepository:
    def __init__(self, engine: Engine):
        self.engine = engine

    def replace(self, inventory: LegacyInventory) -> None:
        root = inventory.root
        database = Path(self.engine.url.database).resolve()
        if database.is_relative_to(Path(root)):
            raise ValueError("El índice SQLite debe estar fuera del checkout de origen.")
        with Session(self.engine) as session, session.begin():
            source = session.get(LegacySourceRow, root)
            if source is None:
                source = LegacySourceRow(root=root)
                session.add(source)
            source.observed_at = datetime.now(timezone.utc).isoformat()
            session.flush()
            for run in inventory.runs:
                session.merge(LegacyRunRow(root=root, path=run.path, identity=run.identity))
            session.flush()
            observed_paths = {artifact.path for artifact in inventory.artifacts}
            # Un archivo que desaparece deja de aportar payload/hash al índice actual.
            for row in session.scalars(select(LegacyArtifactRow).where(LegacyArtifactRow.root == root)):
                if row.path not in observed_paths:
                    row.status = "missing"
                    row.payload = row.sha256 = row.size_bytes = None
                    row.diagnostic = "Archivo anteriormente observado, ahora ausente."
            for artifact in inventory.artifacts:
                session.merge(LegacyArtifactRow(
                    root=root, path=artifact.path, run_path=artifact.run_path, kind=artifact.kind,
                    format=artifact.format, status=artifact.status, sha256=artifact.sha256,
                    size_bytes=artifact.size_bytes, payload=artifact.payload, diagnostic=artifact.diagnostic,
                ))

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

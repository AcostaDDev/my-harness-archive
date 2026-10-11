"""Consultas paginadas del índice H1.1. Las identidades no son intentos."""
import base64
import json
from itertools import islice
from pathlib import Path

from sqlalchemy import String, case, cast, func, literal, select, union_all
from sqlalchemy.orm import Session

from harness_local.core.evidence import evidence_entries
from harness_local.core.legacy import LegacyArtifact
from harness_local.storage.models import LegacyArtifactRow as Artifact, LegacyRunRow as Run, LegacySourceRow as Source


def identifier(value: str) -> str:
    return base64.urlsafe_b64encode(value.encode()).decode().rstrip("=")


def decode_identifier(value: str) -> str:
    try:
        decoded = base64.b64decode(value + "=" * (-len(value) % 4), altchars=b"-_", validate=True).decode()
        if identifier(decoded) == value:
            return decoded
    except (ValueError, UnicodeDecodeError):
        pass
    raise LookupError("Identidad no encontrada.")


def page(items, offset, limit):
    return {"items": items[:limit], "offset": offset,
            "next_offset": offset + limit if len(items) > limit else None}


def artifact_metadata(row):
    return {"id": identifier(row.path), "path": row.path,
            "run_id": identifier(row.run_path) if row.run_path else None,
            "kind": row.kind, "format": row.format, "status": row.status,
            "sha256": row.sha256, "size_bytes": row.size_bytes, "diagnostic": row.diagnostic}


def bounded_entry(entry):
    # Un hallazgo/comando puede contener texto arbitrario. El original sigue accesible
    # por tramos; truncar es explícito y nunca sustituye telemetría por un cero.
    if len(json.dumps(entry.get("value"), ensure_ascii=False)) > 16384:
        entry.pop("value", None)
        entry["truncated"] = True
    for observation in entry.get("fields", {}).values():
        if len(json.dumps(observation.get("value"), ensure_ascii=False)) > 16384:
            observation.pop("value", None)
            observation["truncated"] = True
    return entry


class SQLiteLegacyNavigation:
    def __init__(self, engine):
        self.engine = engine

    def root(self, session, project_id):
        root = decode_identifier(project_id)
        if session.get(Source, root) is None:
            raise LookupError("Proyecto no encontrado.")
        return root

    def projects(self, offset, limit):
        with Session(self.engine) as session:
            rows = session.scalars(select(Source).order_by(Source.root).offset(offset).limit(limit + 1))
            return page([{"id": identifier(r.root), "name": Path(r.root).name, "root": r.root,
                          "observed_at": r.observed_at, "mode": "observation", "authority": "source_files"}
                         for r in rows], offset, limit)

    def phase_evidence(self, root):
        # Identidad del directorio y declaración en JSON se exponen con procedencia.
        run_phase = func.substr(Run.identity, 1, func.instr(Run.identity, "-") - 1)
        queries = [select(run_phase.label("identity"), Run.path.label("path"),
                          literal("run_directory").label("origin")).where(
                              Run.root == root, Run.identity.like("P%-%"))]
        archive_phase = literal("P") + func.substr(Artifact.path, 20, func.instr(
            func.substr(Artifact.path, 20), "/") - 1)
        queries.append(select(archive_phase, Artifact.path, literal("archive_directory")).where(
            Artifact.root == root, Artifact.path.like("docs/archive/phase-%/%")))
        for field in ("phase_id", "next_phase_id"):
            value = cast(Artifact.payload[field].as_string(), String)
            queries.append(select(value, Artifact.path, literal(f"json:/{field}")).where(
                Artifact.root == root, value.like("P%")))
        return union_all(*queries).subquery()

    def phases(self, project_id, offset, limit):
        with Session(self.engine) as session:
            root = self.root(session, project_id)
            evidence = self.phase_evidence(root)
            identities = session.scalars(select(evidence.c.identity).distinct().order_by(evidence.c.identity)
                                          .offset(offset).limit(limit + 1)).all()
            items = []
            for identity in identities:
                # Proveniencia acotada; todas las evidencias son accesibles desde el proyecto.
                origins = session.execute(select(func.min(evidence.c.path), evidence.c.origin).where(
                    evidence.c.identity == identity).group_by(evidence.c.origin)
                    .order_by(evidence.c.origin).limit(6)).all()
                items.append({"identity": identity, "provenance": [
                    {"path": p, "origin": o} for p, o in origins[:5]], "more_provenance": len(origins) > 5})
            return page(items, offset, limit)

    def tasks(self, project_id, phase, offset, limit):
        with Session(self.engine) as session:
            root = self.root(session, project_id)
            query = select(Run.identity).where(Run.root == root, Run.identity.like("P%-T%"))
            if phase is not None:
                query = query.where(Run.identity.startswith(phase + "-", autoescape=True))
            identities = session.scalars(query.distinct().order_by(Run.identity).offset(offset).limit(limit + 1))
            return page([{"identity": i, "origin": "run_directory"} for i in identities], offset, limit)

    def runs(self, project_id, phase, task, offset, limit):
        with Session(self.engine) as session:
            root = self.root(session, project_id)
            query = select(Run).where(Run.root == root)
            if phase is not None:
                query = query.where(Run.identity.startswith(phase + "-", autoescape=True))
            if task is not None:
                query = query.where(Run.identity == task)
            rows = session.scalars(query.order_by(Run.path).offset(offset).limit(limit + 1))
            return page([{"id": identifier(r.path), "path": r.path, "identity": r.identity,
                          "origin": "run_directory"} for r in rows], offset, limit)

    def artifacts(self, project_id, run_id, offset, limit):
        with Session(self.engine) as session:
            root = self.root(session, project_id)
            query = select(Artifact).where(Artifact.root == root)
            if run_id is not None:
                path = decode_identifier(run_id)
                if session.get(Run, (root, path)) is None:
                    raise LookupError("Run no encontrado.")
                query = query.where(Artifact.run_path == path)
            else:
                query = query.where(Artifact.run_path.is_(None))
            # No cargar cuerpos JSON para presentar la timeline de metadatos.
            columns = [Artifact.path, Artifact.run_path, Artifact.kind, Artifact.format,
                       Artifact.status, Artifact.sha256, Artifact.size_bytes, Artifact.diagnostic]
            rows = session.execute(query.with_only_columns(*columns).order_by(Artifact.path)
                                   .offset(offset).limit(limit + 1)).all()
            return page([artifact_metadata(r) for r in rows], offset, limit)

    def artifact(self, project_id, artifact_id, include_payload=False):
        with Session(self.engine) as session:
            root = self.root(session, project_id)
            # Leer bytes no necesita recuperar JSON/JSONL pesados del índice.
            payload = case((Artifact.kind.in_(("task", "review", "phase_review", "stop", "resume",
                "reconcile", "phase_metadata", "validation", "result", "usage", "request")), Artifact.payload),
                else_=None) if include_payload else literal(None)
            row = session.execute(select(Artifact.path, Artifact.run_path, Artifact.kind, Artifact.format,
                Artifact.status, Artifact.sha256, Artifact.size_bytes, payload.label("payload"), Artifact.diagnostic)
                .where(Artifact.root == root, Artifact.path == decode_identifier(artifact_id))).one_or_none()
            if row is None:
                raise LookupError("Artefacto no encontrado.")
            return root, LegacyArtifact(row.path, row.run_path, row.kind, row.format, row.status,
                                        row.sha256, row.size_bytes, row.payload, row.diagnostic)

    def entries(self, project_id, artifact_id, offset, limit):
        _, artifact = self.artifact(project_id, artifact_id, include_payload=True)
        # El payload del índice es la última observación, no una relectura del origen.
        entries = [bounded_entry(e) for e in islice(
            evidence_entries(artifact.kind, artifact.payload), offset, offset + limit + 1)]
        return {**page(entries, offset, limit), "path": artifact.path, "sha256": artifact.sha256,
                "status": artifact.status, "diagnostic": artifact.diagnostic,
                "origin": "indexed_payload"}

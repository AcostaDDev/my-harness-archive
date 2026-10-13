from typing import Annotated
from dataclasses import replace
from pathlib import Path

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from harness_local.api.events import event_frames
from harness_local.api.security import local_request
from harness_local.storage.observation import SQLiteObservationRepository

from harness_local.adapters.evidence import read_content
from harness_local.api.schemas import (
    EvidenceContentRead, EvidenceEntriesRead, LegacyArtifactRead, LegacyPhaseRead,
    LegacyProjectRead, LegacyRunRead, LegacyTaskRead, Page, ProblemResponse,
    ObservationUpdate, ObservationRead, LegacyUpdatesRead,
)
from harness_local.storage.navigation import SQLiteLegacyNavigation, identifier


Offset = Annotated[int, Query(ge=0, le=2**53 - 1)]
Limit = Annotated[int, Query(ge=1, le=100)]
ContentLimit = Annotated[int, Query(ge=4, le=16384)]
Identity = Annotated[str | None, Query(max_length=120)]


def legacy_router(engine):
    router = APIRouter(prefix="/api/legacy")
    navigation = SQLiteLegacyNavigation(engine)
    observation = SQLiteObservationRepository(engine)

    def lookup(operation, *args):
        try:
            return operation(*args)
        except LookupError as error:
            raise HTTPException(404, str(error)) from error

    def root(project_id):
        with Session(engine) as session:
            return lookup(navigation.root, session, project_id)

    @router.get("/updates", response_model=LegacyUpdatesRead, operation_id="legacy_updates")
    def updates(after: Offset = 0, limit: Limit = 100):
        try:
            return observation.events(after, limit)
        except ValueError as error:
            raise HTTPException(409, str(error)) from error

    @router.get("/events", operation_id="legacy_events", response_class=StreamingResponse,
                responses={200: {"content": {"text/event-stream": {"schema": {"type": "string"}}},
                                 "description": "SSE legacy_update: LegacyEventRead; id creciente. reset exige snapshot."}})
    def events(request: Request, after: Offset = 0,
               last_event_id: Annotated[str | None, Header(max_length=20)] = None):
        cursor = after
        if last_event_id is not None:
            if not last_event_id.isascii() or not last_event_id.isdecimal() or int(last_event_id) > 2**53 - 1:
                raise HTTPException(422, "Last-Event-ID debe ser un cursor entero no negativo.")
            cursor = int(last_event_id)
        updates(cursor, 1)  # Validate before sending headers; Last-Event-ID wins on reconnect.
        async def disconnected():
            return (not request.app.state.sessions.remaining(
                request.cookies.get(request.app.state.sessions.cookie)) or await request.is_disconnected())
        return StreamingResponse(event_frames(observation, cursor, disconnected),
            media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    @router.get("/projects/{project_id}/observation", response_model=ObservationRead,
                operation_id="legacy_observation")
    def observation_status(project_id: str):
        return lookup(observation.status, root(project_id))

    @router.put("/projects/{project_id}/observation", response_model=ObservationRead,
                operation_id="legacy_set_observation", dependencies=[Depends(local_request)],
                responses={403: {"model": ProblemResponse}})
    def set_observation(project_id: str, body: ObservationUpdate):
        try:
            return lookup(observation.set_watch, root(project_id), body.enabled)
        except ValueError as error:
            raise HTTPException(409, str(error)) from error

    @router.get("/projects/{project_id}/artifacts/{artifact_id}", response_model=LegacyArtifactRead,
                operation_id="legacy_artifact")
    def artifact_metadata(project_id: str, artifact_id: str):
        _, artifact = lookup(navigation.artifact, project_id, artifact_id)
        return {"id": identifier(artifact.path), "run_id": identifier(artifact.run_path) if artifact.run_path else None,
                **{name: getattr(artifact, name) for name in ("path", "kind", "format", "status", "sha256", "size_bytes", "diagnostic")}}

    @router.get("/projects", response_model=Page[LegacyProjectRead], operation_id="legacy_projects")
    def projects(offset: Offset = 0, limit: Limit = 30):
        return navigation.projects(offset, limit)

    @router.get("/projects/{project_id}/phases", response_model=Page[LegacyPhaseRead], operation_id="legacy_phases")
    def phases(project_id: str, offset: Offset = 0, limit: Limit = 30):
        return lookup(navigation.phases, project_id, offset, limit)

    @router.get("/projects/{project_id}/tasks", response_model=Page[LegacyTaskRead], operation_id="legacy_tasks")
    def tasks(project_id: str, phase: Identity = None, offset: Offset = 0, limit: Limit = 30):
        return lookup(navigation.tasks, project_id, phase, offset, limit)

    @router.get("/projects/{project_id}/runs", response_model=Page[LegacyRunRead], operation_id="legacy_runs")
    def runs(project_id: str, phase: Identity = None, task: Identity = None,
             offset: Offset = 0, limit: Limit = 30):
        return lookup(navigation.runs, project_id, phase, task, offset, limit)

    @router.get("/projects/{project_id}/artifacts", response_model=Page[LegacyArtifactRead], operation_id="legacy_artifacts")
    def artifacts(project_id: str, run_id: Annotated[str | None, Query(max_length=4096)] = None,
                  offset: Offset = 0, limit: Limit = 30):
        return lookup(navigation.artifacts, project_id, run_id, offset, limit)

    @router.get("/projects/{project_id}/artifacts/{artifact_id}/entries",
                response_model=EvidenceEntriesRead, operation_id="legacy_entries")
    def entries(project_id: str, artifact_id: str, offset: Offset = 0, limit: Limit = 30):
        return lookup(navigation.entries, project_id, artifact_id, offset, limit)

    @router.get("/projects/{project_id}/artifacts/{artifact_id}/content",
                response_model=EvidenceContentRead, operation_id="legacy_content")
    def content(project_id: str, artifact_id: str, offset: Offset = 0, limit: ContentLimit = 8192):
        root, artifact = lookup(navigation.artifact, project_id, artifact_id)
        from harness_local.storage.backup import is_read_only_archive, restored_artifact
        if is_read_only_archive(engine):
            try:
                mapped = restored_artifact(engine, Path(root) / artifact.path)
                if mapped is None:
                    return {**read_content(root, replace(artifact, sha256=None), offset, limit),
                            'indexed_sha256': artifact.sha256, 'status': 'missing' if artifact.sha256 else 'unindexed',
                            'diagnostic': 'Original externo no incluido en la copia gestionada; no se relee el origen.'}
                bundle = Path(engine.url.database).resolve().parent
                result = read_content(str(bundle), replace(artifact, path=mapped.relative_to(bundle).as_posix()), offset, limit)
                return {**result, 'path': artifact.path}
            except (OSError, ValueError) as exc:
                raise HTTPException(409, str(exc)) from exc
        return read_content(root, artifact, offset, limit)

    return router

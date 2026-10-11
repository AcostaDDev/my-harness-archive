from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from harness_local.adapters.evidence import read_content
from harness_local.api.schemas import (
    EvidenceContentRead, EvidenceEntriesRead, LegacyArtifactRead, LegacyPhaseRead,
    LegacyProjectRead, LegacyRunRead, LegacyTaskRead, Page,
)
from harness_local.storage.navigation import SQLiteLegacyNavigation


Offset = Annotated[int, Query(ge=0, le=2**53 - 1)]
Limit = Annotated[int, Query(ge=1, le=100)]
ContentLimit = Annotated[int, Query(ge=4, le=16384)]
Identity = Annotated[str | None, Query(max_length=120)]


def legacy_router(engine):
    router = APIRouter(prefix="/api/legacy")
    navigation = SQLiteLegacyNavigation(engine)

    def lookup(operation, *args):
        try:
            return operation(*args)
        except LookupError as error:
            raise HTTPException(404, str(error)) from error

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
        return read_content(root, artifact, offset, limit)

    return router

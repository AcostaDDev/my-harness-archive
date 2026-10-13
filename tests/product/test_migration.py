"""H2.5: migración legacy → gestionado con checkouts Git y SQLite sintéticos.

Fixtures legacy sintéticos de H0.1, agentes/comandos falsos y Git real local.
Ningún proveedor, CLI de agente, red, run privado ni ReferenceProject.
"""

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from threading import Barrier

from alembic import command
from session_client import TestClient
import pytest
from sqlalchemy import func, inspect, select, text
from sqlalchemy.orm import Session

from harness_local.adapters.engine_fake import ScriptedAgentAdapter, ScriptedCommandRunner, SyntheticWorkspace
from harness_local.adapters.legacy import LocalLegacyReader
from harness_local.api.app import create_app
from harness_local.core.engine.context import Command, EnginePolicy, ProjectContext, ProjectProfile
from harness_local.core.legacy import LegacyImportService, artifact_summary
from harness_local.core.migration import MARKER_PATH, MigrationError, digest
from harness_local.services.managed import LocalSupervisor
from harness_local.services.migration import MigrationService
from harness_local.storage.database import make_engine
from harness_local.storage.legacy import SQLiteLegacyRepository
from harness_local.storage.managed import Conflict, SQLiteManagedRepository
from harness_local.storage.migration import ModeConflict
from harness_local.storage.models import (
    Base, LegacyEventRow, LegacySourceRow, ManagedActivationRow, ManagedJobRow, ManagedRunRow,
)
from harness_local.storage.navigation import identifier
from harness_local.storage.observation import SQLiteObservationRepository

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures/legacy"
CASES = ("accepted", "revise", "blocked", "interrupted", "closed-phase")
GIT_ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "Fixture Author", "GIT_AUTHOR_EMAIL": "author@example.invalid",
           "GIT_COMMITTER_NAME": "Fixture Author", "GIT_COMMITTER_EMAIL": "author@example.invalid"}
VERSIONS = {"engine": "h2.5", "agent_adapter": "synthetic-1", "commands": "synthetic-1",
            "evidence": "synthetic-1", "provider_cli": None}
PLAN = """# Synthetic H2.5 plan
## P001-T001 — Managed task
**Objective:** Change synthetic content.
**Allowed paths:** `app/**`
**Acceptance criteria:**
- Synthetic behavior is present.
**Validation commands:** `test-runner check`
**Executor:** synthetic-executor / medium — Explicit test selection
"""
STOPPED = "Usuario confirma que el motor legacy no está en ejecución (prueba sintética)"


class SyntheticCrash(BaseException):
    """Muerte simulada del proceso: ningún manejador de Exception la intercepta."""


def git(cwd, *args):
    result = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, env=GIT_ENV)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def legacy_checkout(tmp_path, case="accepted", name="checkout"):
    root = tmp_path / name
    shutil.copytree(FIXTURES / case, root)
    (root / "app").mkdir()
    (root / "app/main.txt").write_text("baseline", encoding="utf-8")
    (root / ".gitignore").write_text(".harness/runs/\n", encoding="utf-8")
    git(root, "init", "-q", "-b", "main")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "synthetic base")
    return root.resolve()


def tree(root):
    """Bytes y mtime de todo el checkout (incluido .git): detecta cualquier escritura."""
    return {path.relative_to(root).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in sorted(Path(root).rglob("*")) if path.is_file() and not path.is_symlink()}


def table_counts(engine):
    with Session(engine) as session:
        return {table.name: session.scalar(select(func.count()).select_from(table))
                for table in Base.metadata.sorted_tables}


def context_for(root):
    return ProjectContext(Path(root), ProjectProfile("synthetic", validations=(Command(("test-runner", "check")),),
                                                     allowed_command_prefixes=(("test-runner",),)),
                          EnginePolicy(("synthetic-executor",), ("medium",), "synthetic-planner", "medium",
                                       "synthetic-reviewer", "high", max_revision_cycles=1))


def review():
    return {"task_id": "P001-T001", "verdict": "ACCEPT", "findings": [], "blocking_questions": [], "scope_grants": []}


def edit(context, request):
    context.path("app/main.txt").write_text("implemented", encoding="utf-8")
    return {"result": "synthetic"}


class Ports:
    """Factory de puertos falsos que registra si el supervisor llegó a pedirlos."""

    def __init__(self, responses):
        self.responses = responses
        self.agents = None

    def __call__(self, context, versions):
        self.agents = ScriptedAgentAdapter(self.responses)
        return self.agents, ScriptedCommandRunner(), SyntheticWorkspace(context, ("app/main.txt",))


@pytest.fixture
def engine(migrated_database):
    engine = make_engine(migrated_database[0])
    yield engine
    engine.dispose()


@pytest.fixture
def service(engine):
    return MigrationService(engine)


def activate(service, root):
    preview = service.preview(root)
    assert preview["ready"], preview["blockers"]
    return service.activate(root, preview_sha256=preview["inventory_sha256"], legacy_stopped=STOPPED)


def activation_rows(engine):
    with Session(engine) as session:
        return [(row.id, row.status) for row in session.scalars(select(ManagedActivationRow))]


def job_row(engine, job_id):
    with Session(engine) as session:
        row = session.get(ManagedJobRow, job_id)
        return {"status": row.status, "activation_id": row.activation_id, "diagnostic": row.diagnostic}


# --- vista previa ---------------------------------------------------------------


def test_preview_writes_nothing_and_describes_history_identities_and_uncertainties(tmp_path, engine, service,
                                                                                  monkeypatch):
    roots = {case: legacy_checkout(tmp_path, case, case) for case in CASES}
    before = {case: tree(root) for case, root in roots.items()}
    counts = table_counts(engine)

    def forbidden(*args, **kwargs):
        raise AssertionError("La vista previa no lanza procesos")
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    previews = {case: service.preview(root) for case, root in roots.items()}
    monkeypatch.undo()

    assert {case: tree(root) for case, root in roots.items()} == before
    assert table_counts(engine) == counts and not service.migrations_dir.exists()
    accepted = previews["accepted"]
    assert accepted["ready"] and accepted["blockers"] == []
    assert accepted["activation"]["managed_runs_created"] == accepted["activation"]["attempts_inferred"] == 0
    assert [run["identity"] for run in accepted["read_only_history"]] == ["P900-T001"]
    assert accepted["identities"]["tasks"][0]["identity"] == "P900-T001"
    assert {s["field"] for s in accepted["identities"]["tasks"][0]["sources"]} == {"run_directory", "task_id"}
    assert accepted["documents"] == [{"path": "docs/STATE.md", "status": "available",
                                      "sha256": digest((roots["accepted"] / "docs/STATE.md").read_bytes())}]
    assert accepted["repository_key"] == str(roots["accepted"] / ".git")
    # JSON parcial y compañeros ausentes son incertidumbres observadas, no bloqueos.
    interrupted = previews["interrupted"]
    assert interrupted["ready"]
    assert {"pending", "missing"} <= {item["status"] for item in interrupted["uncertainties"]}
    assert all(preview["ready"] for preview in previews.values())
    closed = previews["closed-phase"]["identities"]["phases"]
    assert closed and all(item["sources"] for item in closed)


def test_preview_blocks_uncopyable_evidence_and_activation_writes_nothing(tmp_path, engine, service):
    root = legacy_checkout(tmp_path)
    run = next((root / ".harness/runs").iterdir())
    (run / "linked.json").symlink_to(root / "docs/STATE.md")
    before, counts = tree(root), table_counts(engine)
    preview = service.preview(root)
    assert not preview["ready"]
    assert preview["blockers"][0]["code"] == "uncopyable_evidence"
    with pytest.raises(MigrationError, match="uncopyable_evidence"):
        service.activate(root, preview_sha256=preview["inventory_sha256"], legacy_stopped=STOPPED)
    assert tree(root) == before and table_counts(engine) == counts
    assert not service.migrations_dir.exists()


# --- activación -----------------------------------------------------------------


@pytest.mark.parametrize("case", CASES)
def test_activation_copies_history_with_provenance_and_keeps_h1_distinctions(tmp_path, engine, service, case):
    root = legacy_checkout(tmp_path, case)
    before = tree(root)
    origin = LocalLegacyReader().read(str(root))
    record = activate(service, root)

    assert record.status == "ACTIVE"
    assert (root / MARKER_PATH).read_bytes() == record.marker
    assert {path: value for path, value in tree(root).items() if path != MARKER_PATH} == before
    manifest = json.loads(record.manifest_json)
    assert record.manifest_sha256 == digest(record.manifest_json)
    assert manifest["origin_root"] == str(root) and manifest["snapshot_root"] == record.snapshot_root
    assert [entry["path"] for entry in manifest["artifacts"]] == [a.path for a in origin.artifacts]
    snapshot = Path(record.snapshot_root)
    for entry in manifest["artifacts"]:
        if entry["copied"]:
            assert digest((snapshot / entry["path"]).read_bytes()) == entry["sha256"]
            assert (root / entry["path"]).read_bytes() == (snapshot / entry["path"]).read_bytes()
        else:
            assert entry["status"] == "missing" and not (snapshot / entry["path"]).exists()
    # El histórico importado se navega como en H1: ausente/null/cero idénticos al origen.
    summary = LegacyImportService(SQLiteLegacyRepository(engine), LocalLegacyReader()).summary(record.snapshot_root)
    assert summary["artifacts"] == [artifact_summary(a) for a in origin.artifacts]
    counts = table_counts(engine)
    assert counts["managed_runs"] == counts["managed_attempts"] == counts["managed_jobs"] == 0

    again = service.activate(root, preview_sha256=record.preview_sha256, legacy_stopped=STOPPED)
    assert again == record and table_counts(engine) == counts
    assert sorted(p.name for p in snapshot.parent.iterdir()) == ["checkout"]


def test_imported_history_stays_accessible_over_http_after_activation_and_revert(tmp_path, engine, service,
                                                                               migrated_database):
    root = legacy_checkout(tmp_path)
    record = activate(service, root)
    project = identifier(record.snapshot_root)
    raw = (root / ".harness/runs").joinpath(next(p.name for p in (root / ".harness/runs").iterdir()), "task.json")

    def check(client):
        assert project in [item["id"] for item in client.get("/api/legacy/projects").json()["items"]]
        runs = client.get(f"/api/legacy/projects/{project}/runs").json()["items"]
        assert [run["identity"] for run in runs] == ["P900-T001"]
        artifacts = client.get(f"/api/legacy/projects/{project}/artifacts",
                               params={"run_id": runs[0]["id"], "limit": 100}).json()["items"]
        task = next(item for item in artifacts if item["path"].endswith("/task.json"))
        content = client.get(f"/api/legacy/projects/{project}/artifacts/{task['id']}/content").json()
        assert content["status"] == "verified" and content["text"].encode() == raw.read_bytes()

    with TestClient(create_app(migrated_database[0], tmp_path / "ui")) as client:
        check(client)
        service.revert(record.id, reason="Volver al motor legacy (prueba sintética)")
        check(client)


def test_change_since_preview_fails_before_any_effect(tmp_path, engine, service):
    root = legacy_checkout(tmp_path)
    preview = service.preview(root)
    run = next((root / ".harness/runs").iterdir())
    (run / "late-01.json").write_text("{}", encoding="utf-8")
    before, counts = tree(root), table_counts(engine)
    with pytest.raises(MigrationError, match="vista previa"):
        service.activate(root, preview_sha256=preview["inventory_sha256"], legacy_stopped=STOPPED)
    assert tree(root) == before and table_counts(engine) == counts and not service.migrations_dir.exists()


@pytest.mark.parametrize("change", ["add", "modify"])
def test_legacy_writer_during_copy_fails_and_activates_nothing(tmp_path, engine, change):
    root = legacy_checkout(tmp_path)
    run = next((root / ".harness/runs").iterdir())
    victim = sorted(p for p in run.iterdir() if p.suffix == ".json")[-1]

    def hook(step, **info):
        if step == "copy_complete":
            if change == "add":
                (run / "claude-09.result.json").write_text("{}", encoding="utf-8")
            else:
                victim.write_bytes(victim.read_bytes() + b" ")
    service = MigrationService(engine, hook=hook)
    preview = service.preview(root)
    with pytest.raises(MigrationError, match="durante la copia"):
        service.activate(root, preview_sha256=preview["inventory_sha256"], legacy_stopped=STOPPED)
    [(activation_id, status)] = activation_rows(engine)
    assert status == "FAILED" and not (root / MARKER_PATH).exists()
    record = service.repository.get(activation_id)
    assert "durante la copia" in record.diagnostic and not Path(record.snapshot_root).exists()
    with Session(engine) as session:
        assert session.get(LegacySourceRow, record.snapshot_root) is None
    with pytest.raises(Conflict, match="no activado"):
        SQLiteManagedRepository(engine).submit(context_for(root), "P001-T001", "P001", PLAN, VERSIONS, key="k")


STEPS = ["activation_prepared", "inventory_verified", "copied", "copy_complete", "published", "marker_written",
         "finalize"]


@pytest.mark.parametrize("step", STEPS)
def test_crash_at_each_step_leaves_nothing_active_and_resumes_explicitly(tmp_path, migrated_database, step):
    root = legacy_checkout(tmp_path)
    url = migrated_database[0]
    first = make_engine(url)

    def hook(name, **info):
        if name == step:
            raise SyntheticCrash(name)
    service = MigrationService(first, hook=hook)
    if step == "finalize":
        def crash(*args, **kwargs):
            raise SyntheticCrash("finalize")
        service.repository.finalize_activation = crash
    preview = service.preview(root)
    with pytest.raises(SyntheticCrash):
        service.activate(root, preview_sha256=preview["inventory_sha256"], legacy_stopped=STOPPED)
    first.dispose()

    engine = make_engine(url)  # reinicio
    try:
        restarted = MigrationService(engine)
        [(activation_id, status)] = activation_rows(engine)
        assert status == "PREPARING"
        with Session(engine) as session:
            assert session.get(LegacySourceRow, restarted.repository.get(activation_id).snapshot_root) is None
        with pytest.raises(Conflict):
            SQLiteManagedRepository(engine).submit(context_for(root), "P001-T001", "P001", PLAN, VERSIONS, key="k")
        with pytest.raises(ModeConflict, match="reanudarla o abandonarla"):
            restarted.activate(root, preview_sha256=preview["inventory_sha256"], legacy_stopped=STOPPED)
        record = restarted.resume_activation(activation_id, reason="Proceso anterior terminado (caída simulada)")
        assert record.status == "ACTIVE" and (root / MARKER_PATH).read_bytes() == record.marker
        assert [status for _, status in activation_rows(engine)] == ["ACTIVE"]
        with Session(engine) as session:
            assert session.scalar(select(func.count()).select_from(LegacySourceRow)
                                  .where(LegacySourceRow.root == record.snapshot_root)) == 1
        assert restarted.status(root)["refusal"] is None
    finally:
        engine.dispose()


def test_abandoned_activation_restores_checkout_and_allows_a_new_one(tmp_path, engine):
    root = legacy_checkout(tmp_path)
    before = tree(root)

    def hook(name, **info):
        if name == "marker_written":
            raise SyntheticCrash(name)
    crashing = MigrationService(engine, hook=hook)
    preview = crashing.preview(root)
    with pytest.raises(SyntheticCrash):
        crashing.activate(root, preview_sha256=preview["inventory_sha256"], legacy_stopped=STOPPED)
    assert (root / MARKER_PATH).exists()
    service = MigrationService(engine)
    [(activation_id, _)] = activation_rows(engine)
    service.abandon_activation(activation_id, reason="Abandono explícito tras caída simulada")
    assert tree(root) == before and activation_rows(engine) == [(activation_id, "FAILED")]
    assert "no activado" in service.status(root)["refusal"]
    record = activate(service, root)
    assert record.id != activation_id and record.status == "ACTIVE"


def test_unexpected_error_marks_failed_and_removes_own_marker(tmp_path, engine):
    root = legacy_checkout(tmp_path)
    before = tree(root)

    def hook(name, **info):
        if name == "marker_written":
            raise OSError("disco sintético lleno")
    service = MigrationService(engine, hook=hook)
    preview = service.preview(root)
    with pytest.raises(OSError):
        service.activate(root, preview_sha256=preview["inventory_sha256"], legacy_stopped=STOPPED)
    assert [status for _, status in activation_rows(engine)] == ["FAILED"] and tree(root) == before


# --- exclusión ------------------------------------------------------------------


def test_concurrent_and_alias_activations_produce_a_single_activation(tmp_path, engine, service):
    root = legacy_checkout(tmp_path)
    alias = tmp_path / "alias"
    alias.symlink_to(root)
    preview = service.preview(root)
    barrier = Barrier(2)

    def run(path):
        barrier.wait()
        try:
            return MigrationService(engine).activate(path, preview_sha256=preview["inventory_sha256"],
                                                     legacy_stopped=STOPPED)
        except ModeConflict as exc:
            return exc

    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(run, [root, alias]))
    records = [item for item in results if not isinstance(item, Exception)]
    assert records and all(item.status == "ACTIVE" for item in records)
    assert len(activation_rows(engine)) == 1 and len({item.id for item in records}) == 1
    assert service.activate(alias, preview_sha256=preview["inventory_sha256"], legacy_stopped=STOPPED).id == records[0].id
    codes = {item["code"] for item in service.preview(alias)["blockers"]}
    assert {"live_activation", "marker_present"} <= codes


def test_worktrees_follow_the_repository_activation(tmp_path, engine, service):
    root = legacy_checkout(tmp_path)
    worktree = tmp_path / "task-worktree"
    git(root, "worktree", "add", "-q", "-b", "task", str(worktree))
    repository = SQLiteManagedRepository(engine)
    with pytest.raises(Conflict, match="checkout principal"):
        repository.submit(context_for(worktree), "P001-T001", "P001", PLAN, VERSIONS, key="early")
    record = activate(service, root)
    job = repository.submit(context_for(worktree.resolve()), "P001-T001", "P001", PLAN, VERSIONS, key="derived")
    assert job_row(engine, job.id)["activation_id"] == record.id
    # Un worktree con estado legacy propio no se activa ni se gestiona aparte.
    (worktree / ".harness/runs/20000102T000000+0000_P901-T001").mkdir(parents=True)
    (worktree / ".harness/runs/20000102T000000+0000_P901-T001/task.json").write_text("{}", encoding="utf-8")
    preview = service.preview(worktree)
    assert "live_activation" in {item["code"] for item in preview["blockers"]}
    with pytest.raises(ModeConflict):
        service.activate(worktree, preview_sha256=preview["inventory_sha256"], legacy_stopped=STOPPED)
    with pytest.raises(Conflict, match="estado legacy propio"):
        repository.submit(context_for(worktree.resolve()), "P001-T001", "P001", PLAN, VERSIONS, key="own")
    assert len(activation_rows(engine)) == 1


def test_unfinished_managed_writer_blocks_activation_and_unactivated_legacy_refuses_claim(tmp_path, engine, service):
    root = legacy_checkout(tmp_path)
    shutil.move(root / ".harness/runs", tmp_path / "held-runs")  # checkout aún sin estado legacy
    repository = SQLiteManagedRepository(engine)
    job = repository.submit(context_for(root), "P001-T001", "P001", PLAN, VERSIONS, key="plain")
    shutil.move(tmp_path / "held-runs", root / ".harness/runs")  # aparece un escritor legacy
    before, counts = tree(root), table_counts(engine)
    preview = service.preview(root)
    assert "managed_writer" in {item["code"] for item in preview["blockers"]}
    with pytest.raises(ModeConflict, match="sin terminar"):
        service.activate(root, preview_sha256=preview["inventory_sha256"], legacy_stopped=STOPPED)
    assert tree(root) == before and table_counts(engine) == counts
    ports = Ports([edit, review()])
    assert LocalSupervisor(repository, ports).run_once().status == "REFUSED"
    assert ports.agents is None
    assert job_row(engine, job.id)["status"] == "REFUSED"
    assert "no activado" in job_row(engine, job.id)["diagnostic"]
    assert table_counts(engine)["checkout_locks"] == 0 and table_counts(engine)["managed_attempts"] == 0
    assert activate(service, root).status == "ACTIVE"  # sin trabajo pendiente ya puede activarse


def test_mode_change_between_assessment_and_admission_refuses_the_job(tmp_path, engine, service):
    from harness_local.adapters.migration import legacy_drift
    root = legacy_checkout(tmp_path)
    record = activate(service, root)
    raced = []

    def racing_drift(path, manifest):
        drift = legacy_drift(path, manifest)
        if not raced:  # la reversión empieza tras leer la activación y antes de encolar
            raced.append(service.repository.begin_revert(record.id, reason="Carrera sintética"))
        return drift
    repository = SQLiteManagedRepository(engine)
    repository.guard.drift = racing_drift
    with pytest.raises(Conflict, match="cambió durante la comprobación"):
        repository.submit(context_for(root), "P001-T001", "P001", PLAN, VERSIONS, key="race")
    assert table_counts(engine)["managed_jobs"] == 0


def test_marker_without_activation_refuses_managed_work(tmp_path, engine):
    root = tmp_path / "plain"
    (root / ".harness").mkdir(parents=True)
    (root / MARKER_PATH).write_text("{}", encoding="utf-8")
    with pytest.raises(Conflict, match="sin activación viva"):
        SQLiteManagedRepository(engine).submit(context_for(root.resolve()), "P001-T001", "P001", PLAN, VERSIONS,
                                               key="k")


@pytest.mark.parametrize("tamper", ["legacy_run", "legacy_edit", "marker_edit", "marker_removed"])
def test_legacy_activity_after_activation_refuses_managed_work_before_effects(tmp_path, engine, service, tamper):
    root = legacy_checkout(tmp_path)
    record = activate(service, root)
    repository = SQLiteManagedRepository(engine)
    job = repository.submit(context_for(root), "P001-T001", "P001", PLAN, VERSIONS, key="managed")
    assert job_row(engine, job.id)["activation_id"] == record.id
    run = next((root / ".harness/runs").iterdir())
    if tamper == "legacy_run":
        (root / ".harness/runs/20000103T000000+0000_P900-T002").mkdir()
        (root / ".harness/runs/20000103T000000+0000_P900-T002/task.json").write_text("{}", encoding="utf-8")
    elif tamper == "legacy_edit":
        (run / "task.json").write_bytes((run / "task.json").read_bytes() + b"\n")
    elif tamper == "marker_edit":
        (root / MARKER_PATH).write_bytes(record.marker + b" ")
    else:
        (root / MARKER_PATH).unlink()
    app = (root / "app/main.txt").read_bytes()
    ports = Ports([edit, review()])
    assert LocalSupervisor(repository, ports).run_once().status == "REFUSED"
    assert ports.agents is None and (root / "app/main.txt").read_bytes() == app
    diagnostic = job_row(engine, job.id)["diagnostic"]
    assert ("Escritor legacy" in diagnostic) if tamper.startswith("legacy") else ("Marcador" in diagnostic)
    assert table_counts(engine)["checkout_locks"] == 0
    with pytest.raises(Conflict):
        repository.submit(context_for(root), "P001-T001", "P001", PLAN, VERSIONS, key="after")
    if tamper.startswith("legacy"):
        drift = service.status(root)["drift"]
        assert drift["added"] or drift["modified"]


def test_legacy_write_during_managed_run_stops_before_the_next_invocation(tmp_path, engine, service):
    root = legacy_checkout(tmp_path)
    activate(service, root)
    repository = SQLiteManagedRepository(engine)
    job = repository.submit(context_for(root), "P001-T001", "P001", PLAN, VERSIONS, key="managed")

    def executor_and_legacy_writer(context, request):
        edit(context, request)
        (root / ".harness/runs/20000104T000000+0000_P900-T003").mkdir()
        return {"result": "synthetic"}
    ports = Ports([executor_and_legacy_writer, review()])
    with pytest.raises(Exception, match="Escritor legacy"):
        LocalSupervisor(repository, ports).run_once()
    assert [request.role for request in ports.agents.requests] == ["executor"]  # el revisor no se invoca
    assert job_row(engine, job.id)["status"] == "RECOVERY_REQUIRED"


def test_documents_change_as_proposals_not_merged(tmp_path, engine, service):
    root = legacy_checkout(tmp_path)
    record = activate(service, root)
    (root / "docs/STATE.md").write_text("edición posterior del usuario\n", encoding="utf-8")
    [proposal] = service.status(root)["documents"]
    assert proposal["path"] == "docs/STATE.md" and proposal["state"] == "changed"
    assert proposal["activation_sha256"] == json.loads(record.manifest_json)["documents"][0]["sha256"]
    assert service.status(root)["refusal"] is None  # documentos de producto no son escritor legacy


def test_activated_origin_is_not_reimported_or_observed(tmp_path, engine, service):
    root = legacy_checkout(tmp_path)
    index = SQLiteLegacyRepository(engine)
    index.replace(LocalLegacyReader().read(str(root)))
    observation = SQLiteObservationRepository(engine)
    observation.set_watch(str(root), True)
    activate(service, root)
    assert observation.status(str(root))["enabled"] is False
    with Session(engine) as session:
        assert session.scalar(select(LegacyEventRow.payload).where(LegacyEventRow.root == str(root))
                              .order_by(LegacyEventRow.id.desc()).limit(1))["enabled"] is False
    with pytest.raises(ValueError, match="modo gestionado"):
        index.replace(LocalLegacyReader().read(str(root)))
    with pytest.raises(ValueError, match="modo gestionado"):
        observation.set_watch(str(root), True)


# --- reversión ------------------------------------------------------------------


def test_revert_exports_verified_state_removes_marker_and_returns_checkout_to_legacy(tmp_path, engine, service):
    root = legacy_checkout(tmp_path)
    before = tree(root)
    record = activate(service, root)
    repository = SQLiteManagedRepository(engine)
    job = repository.submit(context_for(root), "P001-T001", "P001", PLAN, VERSIONS, key="managed")
    with pytest.raises(ModeConflict, match="sin terminar"):
        service.revert(record.id, reason="Prematuro")
    assert service.repository.get(record.id).status == "ACTIVE"
    assert LocalSupervisor(repository, Ports([edit, review()])).run_once().status == "DONE"

    reverted = service.revert(record.id, reason="Volver al motor legacy (prueba sintética)")
    assert reverted.status == "REVERTED" and not (root / MARKER_PATH).exists()
    exported = Path(reverted.export_path).read_bytes()
    assert digest(exported) == reverted.export_sha256 == digest(service.repository.export_state(record.id))
    state = json.loads(exported)
    assert [item["run"]["id"] for item in state["runs"]] == [job.run_id]
    assert [a["number"] for a in state["runs"][0]["attempts"]] == [1, 2]
    assert state["activation"]["manifest_sha256"] == record.manifest_sha256
    changed = {path for path in tree(root) if before.get(path) != tree(root)[path]}
    assert changed == {"app/main.txt"}  # solo el trabajo gestionado; el resto del checkout intacto
    with pytest.raises(Conflict, match="no activado"):
        repository.submit(context_for(root), "P001-T001", "P001", PLAN, VERSIONS, key="after-revert")
    SQLiteLegacyRepository(engine).replace(LocalLegacyReader().read(str(root)))  # legacy vuelve a ser observable
    assert Path(record.snapshot_root).is_dir()


def test_crash_during_revert_resumes_explicitly(tmp_path, engine):
    root = legacy_checkout(tmp_path)
    record = activate(MigrationService(engine), root)

    def hook(name, **info):
        if name == "exported":
            raise SyntheticCrash(name)
    with pytest.raises(SyntheticCrash):
        MigrationService(engine, hook=hook).revert(record.id, reason="Reversión sintética")
    service = MigrationService(engine)
    assert service.repository.get(record.id).status == "REVERTING"
    assert "REVERTING" in service.status(root)["refusal"]
    with pytest.raises(ModeConflict):
        service.revert(record.id, reason="De nuevo")
    reverted = service.resume_revert(record.id, reason="Proceso anterior terminado (caída simulada)")
    assert reverted.status == "REVERTED" and not (root / MARKER_PATH).exists()


# --- esquema --------------------------------------------------------------------


def test_migration_0007_round_trip_preserves_managed_rows(tmp_path, engine, migrated_database):
    root = tmp_path / "plain"
    root.mkdir()
    SQLiteManagedRepository(engine).submit(context_for(root.resolve()), "P001-T001", "P001", PLAN, VERSIONS, key="k")
    config = migrated_database[1]
    command.downgrade(config, "0006_git_commits")
    engine.dispose()
    assert "managed_activations" not in inspect(engine).get_table_names()
    assert "activation_id" not in {column["name"] for column in inspect(engine).get_columns("managed_jobs")}
    command.upgrade(config, "head")
    command.check(config)
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(ManagedJobRow)) == 1
        assert session.scalar(select(func.count()).select_from(ManagedRunRow)) == 1
        assert session.execute(text("SELECT activation_id FROM managed_jobs")).scalar() is None

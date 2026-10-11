import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from alembic import command
import pytest
from sqlalchemy import func, inspect, select, text
from sqlalchemy.orm import Session

from harness_local.adapters.fake import FakeSimulationAdapter
from harness_local.adapters.legacy import LocalLegacyReader
from harness_local.cli import main
from harness_local.core.legacy import LegacyImportService
from harness_local.core.simulation import SimulationService
from harness_local.storage.database import make_engine
from harness_local.storage.legacy import SQLiteLegacyRepository
from harness_local.storage.models import LegacyArtifactRow, LegacyRunRow, LegacySourceRow
from harness_local.storage.repository import SQLiteSimulationRepository
from harness_local.storage.schema import require_schema


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures/legacy"
MANIFEST = json.loads((FIXTURES / "manifest.json").read_text())


@pytest.fixture
def importer(migrated_database):
    url, _ = migrated_database
    engine = make_engine(url)
    service = LegacyImportService(SQLiteLegacyRepository(engine), LocalLegacyReader())
    yield service, engine
    engine.dispose()


def artifacts(service, root):
    return {a["path"]: a for a in service.summary(str(root))["artifacts"]}


def synthetic_copy(tmp_path, case="interrupted"):
    target = tmp_path / case
    shutil.copytree(FIXTURES / case, target)
    return target


def test_all_five_scenarios_are_read_only_and_idempotent(importer, monkeypatch):
    service, engine = importer

    def forbidden(*args, **kwargs):
        raise AssertionError("Importar no debe ejecutar procesos.")

    monkeypatch.setattr(subprocess, "Popen", forbidden)
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in FIXTURES.rglob("*") if p.is_file()}
    simulation = SimulationService(SQLiteSimulationRepository(engine), FakeSimulationAdapter()).create("Separada")
    for case, metadata in MANIFEST["cases"].items():
        root = FIXTURES / case
        inventory = service.import_checkout(str(root))
        first = service.summary(str(root))
        service.import_checkout(str(root / "."))
        assert service.summary(str(root)) == first
        assert first["mode"] == "observation" and first["authority"] == "source_files"
        assert len(first["runs"]) == len(metadata["runs"])
        indexed = artifacts(service, root)
        for sample in MANIFEST["artifacts"]:
            if not sample["path"].startswith(case + "/"):
                continue
            relative = sample["path"][len(case) + 1:]
            # Extracto Git externo al formato legacy: nunca un certificado de commit.
            if relative == "synthetic-git-log.txt":
                assert relative not in indexed
                continue
            artifact = indexed[relative]
            raw = (root / relative).read_bytes()
            assert artifact["sha256"] == hashlib.sha256(raw).hexdigest()
            assert artifact["size_bytes"] == len(raw)
            assert artifact["status"] == ("pending" if sample["format"] == "partial_json" else "available")
            if sample["format"] == "json":
                assert artifact["payload"] == json.loads(raw)
        for absent in metadata["absent_files"]:
            artifact = indexed[absent[len(case) + 1:]]
            assert artifact["status"] == "missing"
            assert artifact["sha256"] is None and artifact["size_bytes"] is None
        assert len(inventory.runs) == len(metadata["runs"])
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(LegacySourceRow)) == 5
        assert session.scalar(select(func.count()).select_from(LegacyRunRow)) == 7
        count = session.scalar(select(func.count()).select_from(LegacyArtifactRow))
    for case in MANIFEST["cases"]:
        service.import_checkout(str(FIXTURES / case))
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(LegacyArtifactRow)) == count
    assert SQLiteSimulationRepository(engine).get(simulation.id) == simulation
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in FIXTURES.rglob("*") if p.is_file()}


def test_absent_null_and_observed_zero_remain_distinct(importer, tmp_path):
    service, _ = importer
    root = synthetic_copy(tmp_path, "blocked")
    service.import_checkout(str(root))
    indexed = artifacts(service, root)
    result = next(a for a in indexed.values() if a["path"].endswith("claude-00.result.json"))
    usage = next(a for a in indexed.values() if a["path"].endswith("claude-00.result.usage.json"))
    assert result["fields"]["duration_ms"] == {"state": "absent", "label": "no registrado"}
    assert usage["fields"]["duration_ms"] == {"state": "null", "label": "no registrado", "value": None}
    validation = next(a for a in indexed.values() if a["kind"] == "validation" and a["status"] == "available")
    assert validation["commands"][0]["duration_seconds"]["state"] == "absent"
    path = root / result["path"]
    payload = json.loads(path.read_text())
    payload.update(duration_ms=0, total_cost_usd=0, usage={"input_tokens": 0}, future_field={"keep": [0, None]})
    path.write_text(json.dumps(payload))
    service.import_checkout(str(root))
    result = artifacts(service, root)[result["path"]]
    assert result["fields"]["duration_ms"] == {"state": "recorded", "value": 0}
    assert result["fields"]["total_cost_usd"] == {"state": "recorded", "value": 0}
    assert result["payload"]["future_field"] == {"keep": [0, None]}
    # No defaults de modelo/esfuerzo desde el request posterior al contrato antiguo.
    task = next(a for a in indexed.values() if a["kind"] == "task")
    assert "executor_selection" not in task["payload"]


def test_partial_file_is_reread_and_changed_hash_replaces_same_record(importer, tmp_path):
    service, engine = importer
    root = synthetic_copy(tmp_path)
    service.import_checkout(str(root))
    first = service.summary(str(root))
    pending = next(a for a in first["artifacts"] if a["status"] == "pending")
    assert pending["kind"] == "review" and pending["payload"] is None
    assert pending["diagnostic"]
    with Session(engine) as session:
        count = session.scalar(select(func.count()).select_from(LegacyArtifactRow))
    complete = {"task_id": "P900-T004", "verdict": "REVISE", "future": None}
    (root / pending["path"]).write_text(json.dumps(complete))
    service.import_checkout(str(root))
    updated = artifacts(service, root)[pending["path"]]
    assert updated["status"] == "available" and updated["diagnostic"] is None
    assert updated["payload"] == complete and updated["sha256"] != pending["sha256"]
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(LegacyArtifactRow)) == count
    # Pérdida posterior de evidencia: no conservar un payload obsoleto como actual.
    (root / pending["path"]).unlink()
    service.import_checkout(str(root))
    removed = artifacts(service, root)[pending["path"]]
    assert removed["status"] == "missing" and removed["payload"] is None
    assert removed["sha256"] is None
    (root / pending["path"]).write_text(json.dumps(complete))
    engine.dispose()  # resumen vuelve a abrir SQLite; no depende de objetos en memoria.
    assert artifacts(service, root)[pending["path"]]["status"] == "missing"
    service.import_checkout(str(root))
    assert artifacts(service, root)[pending["path"]]["payload"] == complete


@pytest.mark.parametrize("content,status", [(b'{"x":', "pending"), (b'\xff', "pending"),
                                           (b'[]', "error"), (b'{"x": NaN}', "error")])
def test_invalid_files_do_not_abort_other_evidence(importer, tmp_path, content, status):
    service, _ = importer
    root = synthetic_copy(tmp_path, "accepted")
    run = next((root / ".harness/runs").iterdir())
    (run / "future.json").write_bytes(content)
    service.import_checkout(str(root))
    indexed = artifacts(service, root)
    invalid = indexed[(run / "future.json").relative_to(root).as_posix()]
    assert invalid["status"] == status and invalid["diagnostic"]
    assert invalid["sha256"] == hashlib.sha256(content).hexdigest()
    assert any(a["kind"] == "task" and a["status"] == "available" for a in indexed.values())


def test_partial_jsonl_preserves_prefix_and_reloads(importer, tmp_path):
    service, _ = importer
    root = synthetic_copy(tmp_path, "accepted")
    path = next((root / ".harness/runs").rglob("*.jsonl"))
    path.write_text('{"type":"future","unknown":0}\n{"type":')
    service.import_checkout(str(root))
    artifact = artifacts(service, root)[path.relative_to(root).as_posix()]
    assert artifact["status"] == "pending"
    assert artifact["payload"] == [{"type": "future", "unknown": 0}]
    path.write_text('{"type":"future","unknown":0}\n{"type":"result"}\n')
    service.import_checkout(str(root))
    artifact = artifacts(service, root)[path.relative_to(root).as_posix()]
    assert artifact["status"] == "available" and len(artifact["payload"]) == 2


def test_unreadable_file_and_symlinks_are_local_diagnostics(importer, tmp_path, monkeypatch):
    service, _ = importer
    root = synthetic_copy(tmp_path, "accepted")
    task = next(root.rglob("task.json"))
    from harness_local.adapters import legacy
    read_bytes = legacy.read_raw

    def deny_task(root_path, relative):
        if root_path / relative == task:
            raise PermissionError("Denegación sintética")
        return read_bytes(root_path, relative)

    monkeypatch.setattr(legacy, "read_raw", deny_task)
    run = task.parent
    (run / "outside.json").symlink_to(tmp_path / "never-read.json")
    (run / "outside-directory").symlink_to(tmp_path, target_is_directory=True)
    service.import_checkout(str(root))
    indexed = artifacts(service, root)
    assert indexed[task.relative_to(root).as_posix()]["status"] == "error"
    assert indexed[(run / "outside.json").relative_to(root).as_posix()]["status"] == "error"
    assert indexed[(run / "outside-directory").relative_to(root).as_posix()]["status"] == "error"
    assert any(a["kind"] == "review" and a["status"] == "available" for a in indexed.values())


def test_same_task_in_distinct_runs_and_checkouts_is_not_collapsed(importer, tmp_path):
    service, engine = importer
    root = synthetic_copy(tmp_path)
    service.import_checkout(str(FIXTURES / "interrupted"))
    service.import_checkout(str(root))
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(LegacyRunRow)) == 4
    assert len(service.summary(str(root))["runs"]) == 2
    assert not any("attempt" in key or "commit" in key or "accepted" in key
                   for key in service.summary(str(root)))


def test_cli_explicit_import_summary_and_errors(migrated_database, tmp_path, capsys):
    root = synthetic_copy(tmp_path, "accepted")
    assert main(["legacy-summary", str(root)]) == 1
    assert "Origen no importado" in capsys.readouterr().err
    assert main(["legacy-import", str(root)]) == 0
    first = json.loads(capsys.readouterr().out)
    assert main(["legacy-summary", str(root)]) == 0
    assert json.loads(capsys.readouterr().out) == first
    assert main(["legacy-import", str(root)]) == 0
    assert json.loads(capsys.readouterr().out) == first
    assert main(["legacy-import", str(tmp_path / "absent")]) == 1
    assert capsys.readouterr().err


def test_cli_rejects_database_inside_source_before_any_write(tmp_path, monkeypatch, capsys):
    root = synthetic_copy(tmp_path, "accepted")
    db = root / ".local/index.sqlite3"
    monkeypatch.setenv("HARNESS_DATABASE_URL", f"sqlite:///{db}")
    assert main(["legacy-import", str(root)]) == 1
    assert "fuera del checkout" in capsys.readouterr().err
    assert not db.parent.exists()


def test_cli_requires_migration_without_creating_tables(tmp_path, monkeypatch, capsys):
    db = tmp_path / "unmigrated.sqlite3"
    monkeypatch.setenv("HARNESS_DATABASE_URL", f"sqlite:///{db}")
    assert main(["legacy-import", str(FIXTURES / "accepted")]) == 1
    assert "alembic upgrade head" in capsys.readouterr().err
    engine = make_engine(f"sqlite:///{db}")
    try:
        assert inspect(engine).get_table_names() == []
    finally:
        engine.dispose()


def test_migration_back_to_h03_preserves_simulations(migrated_database):
    url, config = migrated_database
    engine = make_engine(url)
    try:
        simulation = SimulationService(SQLiteSimulationRepository(engine), FakeSimulationAdapter()).create("H0.3")
        service = LegacyImportService(SQLiteLegacyRepository(engine), LocalLegacyReader())
        service.import_checkout(str(FIXTURES / "accepted"))
        before = service.summary(str(FIXTURES / "accepted"))
        command.check(config)
        command.downgrade(config, "0001_simulations")
        assert inspect(engine).get_table_names() == ["alembic_version", "simulations"]
        assert SQLiteSimulationRepository(engine).get(simulation.id) == simulation
        with pytest.raises(RuntimeError, match="Migración incompatible"):
            require_schema(engine)
        command.upgrade(config, "head")
        command.check(config)
        with engine.connect() as connection:
            assert connection.execute(text("PRAGMA foreign_key_check")).all() == []
        assert service.summary(str(FIXTURES / "accepted")) is None
        service.import_checkout(str(FIXTURES / "accepted"))
        assert service.summary(str(FIXTURES / "accepted")) == before
        assert SQLiteSimulationRepository(engine).get(simulation.id) == simulation
    finally:
        engine.dispose()

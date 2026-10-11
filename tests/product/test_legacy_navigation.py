import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

from fastapi.testclient import TestClient
import pytest

from harness_local.adapters import evidence
from harness_local.adapters.legacy import LocalLegacyReader
from harness_local.api.app import create_app
from harness_local.core.legacy import LegacyImportService
from harness_local.storage.database import make_engine
from harness_local.storage.legacy import SQLiteLegacyRepository
from harness_local.storage.navigation import identifier


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures/legacy"
CASES = ("accepted", "revise", "blocked", "interrupted", "closed-phase")


@pytest.fixture
def navigation(migrated_database, tmp_path):
    url, _ = migrated_database
    engine = make_engine(url)
    service = LegacyImportService(SQLiteLegacyRepository(engine), LocalLegacyReader())
    roots = {}
    for case in CASES:
        roots[case] = tmp_path / case
        shutil.copytree(FIXTURES / case, roots[case])
        service.import_checkout(str(roots[case]))
    with TestClient(create_app(url, tmp_path / "ui")) as client:
        yield client, roots, service
    engine.dispose()


def all_pages(client, url, limit=2):
    items, offset = [], 0
    while True:
        response = client.get(url, params={"offset": offset, "limit": limit})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["offset"] == offset and len(data["items"]) <= limit
        items.extend(data["items"])
        if data["next_offset"] is None:
            return items
        assert data["next_offset"] > offset
        offset = data["next_offset"]


def base_for(root):
    return f"/api/legacy/projects/{identifier(str(root.resolve()))}"


def run_artifacts(client, base, run):
    # all_pages pasa parámetros separados para poder verificar también el filtro.
    items, offset = [], 0
    while True:
        data = client.get(base + "/artifacts", params={"run_id": run["id"], "offset": offset, "limit": 2}).json()
        items.extend(data["items"])
        if data["next_offset"] is None:
            return items
        offset = data["next_offset"]


@pytest.mark.parametrize("case", CASES)
def test_task_phase_run_evidence_round_trip_is_read_only(navigation, case, monkeypatch):
    client, roots, _ = navigation
    root = roots[case]
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.rglob("*") if p.is_file()}

    def forbidden(*args, **kwargs):
        raise AssertionError("Navegar no ejecuta comandos históricos ni agentes.")

    monkeypatch.setattr(subprocess, "Popen", forbidden)
    projects = all_pages(client, "/api/legacy/projects")
    assert len(projects) == 5 and len({p["id"] for p in projects}) == 5
    project = next(p for p in projects if p["name"] == case)
    assert project["mode"] == "observation" and project["authority"] == "source_files"
    base = base_for(root)
    phases = all_pages(client, base + "/phases")
    assert "P900" in [p["identity"] for p in phases]
    assert all(p["provenance"] for p in phases)
    tasks = all_pages(client, base + "/tasks")
    runs = all_pages(client, base + "/runs")
    assert len(runs) == (2 if case in ("interrupted", "closed-phase") else 1)
    assert all(t["origin"] == "run_directory" for t in tasks)
    for task in tasks:
        selected = client.get(base + "/runs", params={"task": task["identity"]}).json()["items"]
        assert selected and all(r["identity"] == task["identity"] for r in selected)
        for run in selected:
            artifacts = run_artifacts(client, base, run)
            assert any(a["kind"] == "task" for a in artifacts)
            assert any(a["kind"] == "review" for a in artifacts)
    for run in runs:
        artifacts = run_artifacts(client, base, run)
        assert len({a["id"] for a in artifacts}) == len(artifacts)
        for artifact in artifacts:
            content = client.get(f"{base}/artifacts/{artifact['id']}/content").json()
            if artifact["sha256"] is None:
                assert content["status"] == "unindexed" and content["text"] is None
                continue
            raw = (root / artifact["path"]).read_bytes()
            assert content["status"] == "verified"
            assert content["text"].encode() == raw
            assert content["observed_sha256"] == artifact["sha256"] == hashlib.sha256(raw).hexdigest()
    docs = all_pages(client, base + "/artifacts")
    assert all(a["run_id"] is None and a["path"].startswith("docs/") for a in docs)
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.rglob("*") if p.is_file()}
    assert not any(key in run for run in runs for key in ("attempt", "accepted", "commit", "closed"))
    # H0.3 conserva su recorrido al lado de la navegación.
    assert client.post("/api/simulations", json={"title": "Regresión"}).status_code == 201


def test_revise_history_findings_and_blocking_questions_have_provenance(navigation):
    client, roots, _ = navigation
    base = base_for(roots["revise"])
    run = all_pages(client, base + "/runs")[0]
    artifacts = run_artifacts(client, base, run)
    reviews = [a for a in artifacts if a["kind"] == "review"]
    assert [Path(a["path"]).name for a in reviews] == ["review-00.json", "review-01.json"]
    verdicts = []
    for review in reviews:
        url = f"{base}/artifacts/{review['id']}/entries"
        entries = all_pages(client, url)
        meta = client.get(url).json()
        assert meta["origin"] == "indexed_payload" and meta["sha256"] == review["sha256"]
        verdicts.append(next(e["fields"]["verdict"]["value"] for e in entries if e["pointer"] == "/verdict"))
        if review == reviews[0]:
            finding = next(e for e in entries if e["kind"] == "finding")
            assert finding["pointer"] == "/findings/0" and finding["value"]["required_fix"]
    assert verdicts == ["REVISE", "ACCEPT"]
    base = base_for(roots["blocked"])
    run = all_pages(client, base + "/runs")[0]
    artifacts = run_artifacts(client, base, run)
    review = next(a for a in artifacts if a["kind"] == "review" and a["status"] == "available")
    entries = all_pages(client, f"{base}/artifacts/{review['id']}/entries")
    question = next(e for e in entries if e["kind"] == "blocking_question")
    assert question["pointer"] == "/blocking_questions/0" and "saludo" in question["value"]
    stop = next(a for a in artifacts if a["kind"] == "stop" and a["status"] == "available")
    entries = all_pages(client, f"{base}/artifacts/{stop['id']}/entries")
    assert next(e for e in entries if e["pointer"] == "/reason")["fields"]["reason"]["state"] == "recorded"


def test_missing_partial_and_phase_close_are_not_promoted_to_results(navigation):
    client, roots, _ = navigation
    base = base_for(roots["interrupted"])
    runs = all_pages(client, base + "/runs")
    evidence_rows = [a for run in runs for a in run_artifacts(client, base, run)]
    partial = next(a for a in evidence_rows if a["status"] == "pending")
    assert partial["kind"] == "review" and partial["diagnostic"]
    data = client.get(f"{base}/artifacts/{partial['id']}/entries").json()
    assert data["items"] == [] and data["status"] == "pending"
    assert any(a["kind"] == "result" and a["status"] == "missing" for a in evidence_rows)
    base = base_for(roots["closed-phase"])
    phases = all_pages(client, base + "/phases")
    assert [p["identity"] for p in phases] == ["P900", "P901"]
    assert any(p["origin"] == "archive_directory" for p in phases[0]["provenance"])
    assert all_pages(client, base + "/tasks") == []
    runs = all_pages(client, base + "/runs")
    assert [r["identity"] for r in runs] == ["P900-RECONCILE", "P900-CLOSE"]
    assert not client.get(base + "/runs", params={"phase": "P901"}).json()["items"]


def test_absent_null_zero_requested_reported_and_command_duration(navigation):
    client, roots, importer = navigation
    root = roots["blocked"]
    base = base_for(root)
    result = next(root.rglob("claude-00.result.json"))
    url = f"{base}/artifacts/{identifier(result.relative_to(root).as_posix())}/entries"
    fields = {name: value for e in all_pages(client, url) for name, value in e["fields"].items()}
    assert fields["duration_ms"]["state"] == "absent"
    usage = next(root.rglob("claude-00.result.usage.json"))
    usage_url = f"{base}/artifacts/{identifier(usage.relative_to(root).as_posix())}/entries"
    fields = {name: value for e in all_pages(client, usage_url) for name, value in e["fields"].items()}
    assert fields["duration_ms"]["state"] == "null"
    payload = json.loads(result.read_text())
    payload.update(duration_ms=0, total_cost_usd=0, modelUsage={"reported-future-model": {"inputTokens": 0}})
    result.write_text(json.dumps(payload))
    importer.import_checkout(str(root))
    fields = {name: value for e in all_pages(client, url) for name, value in e["fields"].items()}
    assert fields["duration_ms"]["state"] == "recorded" and fields["duration_ms"]["value"] == 0
    assert fields["total_cost_usd"]["value"] == 0
    assert fields["modelUsage"]["value"] == payload["modelUsage"]
    validation = next(root.rglob("validation-00.json"))
    entries = all_pages(client, f"{base}/artifacts/{identifier(validation.relative_to(root).as_posix())}/entries")
    command = next(e for e in entries if e["kind"] == "command")
    assert command["pointer"] == "/commands/0" and command["fields"]["duration_seconds"]["state"] == "absent"
    assert (root / command["fields"]["stdout_file"]["value"]).is_file()
    base = base_for(roots["accepted"])
    request = next(roots["accepted"].rglob("*.request.json"))
    entries = all_pages(client, f"{base}/artifacts/{identifier(request.relative_to(roots['accepted']).as_posix())}/entries")
    assert next(e for e in entries if e["pointer"] == "/effort")["fields"]["effort"]["value"] == "medium"
    validation = next(roots["accepted"].rglob("validation-00.json"))
    entries = all_pages(client, f"{base}/artifacts/{identifier(validation.relative_to(roots['accepted']).as_posix())}/entries")
    command = next(e for e in entries if e["kind"] == "command")
    assert command["fields"]["duration_seconds"]["state"] == "recorded"
    assert command["fields"]["duration_seconds"]["value"] == 0.004
    task = next(root.rglob("task.json"))
    entries = all_pages(client, f"{base_for(root)}/artifacts/{identifier(task.relative_to(root).as_posix())}/entries")
    assert next(e for e in entries if e["pointer"] == "/executor_selection")["fields"]["executor_selection"]["state"] == "absent"


@pytest.mark.parametrize("mutation,expected", [("change", "changed"), ("remove", "missing"),
                                              ("file_symlink", "unsafe"), ("directory_symlink", "unsafe")])
def test_source_changes_or_links_do_not_serve_new_bytes(navigation, tmp_path, mutation, expected):
    client, roots, _ = navigation
    root = roots["accepted"]
    path = next(root.rglob("task.json"))
    relative = path.relative_to(root).as_posix()
    original = path.read_bytes()
    url = f"{base_for(root)}/artifacts/{identifier(relative)}/content"
    if mutation == "change":
        path.write_bytes(b"new bytes never indexed")
    elif mutation == "remove":
        path.unlink()
    elif mutation == "file_symlink":
        outside = tmp_path / "outside.txt"
        outside.write_bytes(original)
        path.unlink()
        path.symlink_to(outside)
    else:
        directory = path.parent
        moved = tmp_path / "moved-run"
        directory.rename(moved)
        directory.symlink_to(moved, target_is_directory=True)
    result = client.get(url).json()
    assert result["status"] == expected and result["text"] is None and result["next_offset"] is None
    # Consultar no reimporta ni pierde la evidencia previa del índice.
    entries = client.get(url.removesuffix("content") + "entries").json()
    assert entries["sha256"] == hashlib.sha256(original).hexdigest() and entries["status"] == "available"


def test_logs_diffs_utf8_and_empty_file_pages(navigation):
    client, roots, importer = navigation
    root = roots["accepted"]
    run = next((root / ".harness/runs").iterdir())
    for name, raw in (("large.patch", ("+línea🙂\n" * 5000).encode()), ("empty.log", b"")):
        path = run / name
        path.write_bytes(raw)
        importer.import_checkout(str(root))
        url = f"{base_for(root)}/artifacts/{identifier(path.relative_to(root).as_posix())}/content"
        chunks, offset = [], 0
        while True:
            data = client.get(url, params={"offset": offset, "limit": 73}).json()
            assert data["status"] == "verified" and len(data["text"].encode()) <= 76
            chunks.append(data["text"].encode())
            if data["next_offset"] is None:
                break
            offset = data["next_offset"]
        assert b"".join(chunks) == raw


def test_unindexed_routes_limits_and_traversal_are_rejected(navigation):
    client, roots, _ = navigation
    base = base_for(roots["accepted"])
    assert client.get("/api/legacy/projects/not-an-id/runs").status_code == 404
    assert client.get(f"{base}/artifacts/{identifier('../outside.txt')}/content").status_code == 404
    assert client.get(base + "/artifacts", params={"run_id": identifier("unknown")}).status_code == 404
    for params in ({"offset": -1}, {"offset": 2**63}, {"limit": 0}, {"limit": 101}):
        assert client.get(base + "/runs", params=params).status_code == 422
    artifact = next(roots["accepted"].rglob("task.json"))
    url = f"{base}/artifacts/{identifier(artifact.relative_to(roots['accepted']).as_posix())}/content"
    for params in ({"offset": -1}, {"limit": 0}, {"limit": 16385}):
        assert client.get(url, params=params).status_code == 422


def test_size_limits_and_invalid_utf8_are_explicit(navigation, monkeypatch):
    client, roots, importer = navigation
    root = roots["accepted"]
    run = next((root / ".harness/runs").iterdir())
    path = run / "large.log"
    path.write_bytes(b"a" * 101)
    invalid = run / "invalid.log"
    invalid.write_bytes(b"\xff")
    review = run / "review-99.json"
    review.write_text(json.dumps({"findings": [{"problem": "x" * 20000}]}))
    importer.import_checkout(str(root))
    monkeypatch.setattr(evidence, "MAX_VERIFY_BYTES", 100)
    base = base_for(root)
    result = client.get(f"{base}/artifacts/{identifier(path.relative_to(root).as_posix())}/content").json()
    assert result["status"] == "too_large" and result["text"] is None
    result = client.get(f"{base}/artifacts/{identifier(invalid.relative_to(root).as_posix())}/content").json()
    assert result["status"] == "invalid_utf8" and result["text"] is None
    entries = all_pages(client, f"{base}/artifacts/{identifier(review.relative_to(root).as_posix())}/entries")
    finding = next(e for e in entries if e["kind"] == "finding")
    assert finding["truncated"] and finding["value"] is None
    assert len(all_pages(client, base + "/runs")) == 1


def test_root_symlink_is_rejected(navigation, tmp_path):
    client, roots, _ = navigation
    root = roots["accepted"]
    path = next(root.rglob("task.json"))
    url = f"{base_for(root)}/artifacts/{identifier(path.relative_to(root).as_posix())}/content"
    moved = tmp_path / "moved-checkout"
    root.rename(moved)
    root.symlink_to(moved, target_is_directory=True)
    assert client.get(url).json()["status"] == "unsafe"


def test_nonregular_file_cannot_block_the_content_endpoint(navigation):
    client, roots, _ = navigation
    root = roots["accepted"]
    path = next(root.rglob("task.json"))
    url = f"{base_for(root)}/artifacts/{identifier(path.relative_to(root).as_posix())}/content"
    path.unlink()
    os.mkfifo(path)
    result = client.get(url).json()
    assert result["status"] == "unsafe" and result["text"] is None


def test_change_during_descriptor_read_is_not_served(navigation, monkeypatch):
    client, roots, _ = navigation
    root = roots["accepted"]
    path = next(root.rglob("task.json"))
    url = f"{base_for(root)}/artifacts/{identifier(path.relative_to(root).as_posix())}/content"
    original_read = evidence.os.read
    changed = False

    def change_after_first_read(fd, count):
        nonlocal changed
        chunk = original_read(fd, count)
        if not changed:
            with path.open("ab") as file:
                file.write(b"modified during read")
            changed = True
        return chunk

    monkeypatch.setattr(evidence.os, "read", change_after_first_read)
    result = client.get(url).json()
    assert result["status"] == "changed" and result["text"] is None
    assert "durante" in result["diagnostic"]


def test_local_reader_error_does_not_change_agent_result(navigation, monkeypatch):
    client, roots, _ = navigation
    root = roots["accepted"]
    path = next(root.rglob("task.json"))
    url = f"{base_for(root)}/artifacts/{identifier(path.relative_to(root).as_posix())}/content"
    original_open = evidence.os.open

    def deny(name, *args, **kwargs):
        if name == "task.json":
            raise PermissionError("Denegación sintética de lectura")
        return original_open(name, *args, **kwargs)

    monkeypatch.setattr(evidence.os, "open", deny)
    data = client.get(url).json()
    assert data["status"] == "unreadable" and data["text"] is None
    assert client.get(url.removesuffix("content") + "entries").json()["status"] == "available"

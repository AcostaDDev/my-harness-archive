import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import shutil
import time

from alembic import command
from session_client import TestClient
import pytest
from sqlalchemy import event, func, select
from sqlalchemy.orm import Session

from harness_local.adapters import legacy
from harness_local.api.app import create_app
from harness_local.api.events import event_frames
from harness_local.services.observation import LegacyObserver
from harness_local.storage.database import make_engine
from harness_local.storage.legacy import SQLiteLegacyRepository
from harness_local.storage.models import LegacyEventRow, LegacyRunRow
from harness_local.storage.navigation import identifier
from harness_local.storage.observation import SQLiteObservationRepository

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures/legacy"


LOCAL = {"base_url": "http://127.0.0.1:8013", "headers": {"X-Harness-Local": "1"}}  # guardia local D033


@pytest.fixture
def observation(migrated_database, tmp_path):
    url, config = migrated_database
    root = tmp_path / "source"
    shutil.copytree(FIXTURES / "accepted", root)
    engine = make_engine(url)
    index = SQLiteLegacyRepository(engine)
    index.replace(legacy.LocalLegacyReader().read(str(root)))
    control = SQLiteObservationRepository(engine)
    observer = LegacyObserver(engine)
    yield root, index, control, observer, url, config
    engine.dispose()


def indexed(index, root, path):
    return next(a for a in index.get(str(root)).artifacts if a.path == path.relative_to(root).as_posix())


@pytest.mark.parametrize("case", ["accepted", "revise", "blocked", "interrupted", "closed-phase"])
def test_five_scenarios_observed_without_duplicates_or_source_writes(observation, tmp_path, case):
    _, index, control, observer, _, _ = observation
    root = tmp_path / case
    shutil.copytree(FIXTURES / case, root)
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.rglob("*") if p.is_file()}
    index.replace(legacy.LocalLegacyReader().read(str(root)))
    initial = index.get(str(root))
    control.set_watch(str(root), True)
    observer.scan(reconcile=True)
    cursor = control.events()["cursor"]
    observer.scan()
    observer.scan(reconcile=True)
    assert control.events(after=cursor)["items"] == []
    assert index.get(str(root)) == initial
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.rglob("*") if p.is_file()}
    with Session(index.engine) as session:
        assert session.scalar(select(func.count()).select_from(LegacyRunRow).where(LegacyRunRow.root == str(root))) == len(initial.runs)


def test_partial_completion_disappearance_and_reappearance(observation):
    root, index, control, observer, _, _ = observation
    path = next(root.rglob("review-00.json"))
    control.set_watch(str(root), True)
    path.write_bytes(b'{"verdict":')
    observer.scan()
    partial = indexed(index, root, path)
    assert partial.status == "pending" and partial.payload is None
    cursor = control.events()["cursor"]
    observer.scan()
    assert control.events(after=cursor)["items"] == []
    path.write_text('{"verdict":"REVISE","future":0}')
    observer.scan()
    complete = indexed(index, root, path)
    assert complete.status == "available" and complete.sha256 != partial.sha256
    assert complete.payload["future"] == 0
    path.unlink()
    observer.scan()
    assert indexed(index, root, path).status == "missing"
    assert indexed(index, root, path).payload is None
    path.write_text('{"verdict":"ACCEPT"}')
    observer.scan()
    assert indexed(index, root, path).payload == {"verdict": "ACCEPT"}
    assert [e["kind"] for e in control.events(after=cursor)["items"]] == ["index_updated"] * 3


def test_jsonl_partial_prefix_and_batch_grouping(observation):
    root, index, control, observer, _, _ = observation
    path = next(root.rglob("*.jsonl"))
    other = next(root.rglob("review-00.json"))
    control.set_watch(str(root), True)
    cursor = control.events()["cursor"]
    path.write_bytes(b'{"type":"future"}\n{"type":')
    other.write_text('{"verdict":"REVISE"}')
    observer.scan()
    assert indexed(index, root, path).status == "pending"
    assert indexed(index, root, path).payload == [{"type": "future"}]
    assert len(control.events(after=cursor)["items"]) == 1
    path.write_text('{"type":"future"}\n{"type":"result"}\n')
    observer.scan()
    assert len(indexed(index, root, path).payload) == 2


def test_only_enabled_projects_reread_and_disable_wins_inflight(observation):
    root, index, control, observer, _, _ = observation
    path = next(root.rglob("review-00.json"))
    initial = indexed(index, root, path)
    path.write_text('{"verdict":"REVISE"}')
    observer.scan()
    assert indexed(index, root, path) == initial
    control.set_watch(str(root), True)
    inventory = legacy.LocalLegacyReader().read(str(root))
    control.set_watch(str(root), False)
    index.replace(inventory, watched=True)
    assert indexed(index, root, path) == initial
    control.set_watch(str(root), True)
    observer.scan()
    assert indexed(index, root, path).payload["verdict"] == "REVISE"


def test_incremental_reads_only_changes_and_retries_pending(observation, monkeypatch):
    root, _, control, observer, _, _ = observation
    control.set_watch(str(root), True)
    original = legacy.read_raw
    calls = []

    def track(root_path, relative):
        calls.append(relative)
        return original(root_path, relative)

    monkeypatch.setattr(legacy, "read_raw", track)
    observer.scan()
    assert calls
    calls.clear()
    observer.scan()
    assert calls == []
    path = next(root.rglob("review-00.json"))
    path.write_text('{"verdict":')
    observer.scan()
    assert calls == [path.relative_to(root).as_posix()]
    calls.clear()
    observer.scan()
    assert calls == [path.relative_to(root).as_posix()]
    calls.clear()
    observer.scan(reconcile=True)
    assert len(calls) > 1


def test_restart_reconciles_while_browser_closed(observation, tmp_path):
    root, index, control, _, url, _ = observation
    control.set_watch(str(root), True)
    cursor = control.events()["cursor"]
    path = next(root.rglob("review-00.json"))
    path.write_text('{"verdict":"REVISE"}')
    with TestClient(create_app(url, tmp_path)) as client:
        updates = client.get(f"/api/legacy/updates?after={cursor}").json()
        assert len(updates["items"]) == 1
        assert indexed(index, root, path).payload == {"verdict": "REVISE"}
    with TestClient(create_app(url, tmp_path)) as client:
        assert client.get(f"/api/legacy/updates?after={cursor}").json() == updates
        assert client.get(f"/api/legacy/updates?after={updates['cursor']}").json()["items"] == []


def test_running_observer_updates_without_browser_and_stops(observation, tmp_path):
    root, index, control, _, url, _ = observation
    control.set_watch(str(root), True)
    path = next(root.rglob("review-00.json"))
    with TestClient(create_app(url, tmp_path)):
        path.write_text('{"verdict":"REVISE"}')
        deadline = time.monotonic() + 4
        while indexed(index, root, path).payload != {"verdict": "REVISE"}:
            assert time.monotonic() < deadline
            time.sleep(0.05)
    path.write_text('{"verdict":"BLOCKED"}')
    time.sleep(0.6)
    assert indexed(index, root, path).payload == {"verdict": "REVISE"}


def test_root_unavailable_or_replaced_by_link_preserves_index_with_local_error(observation, tmp_path):
    root, index, control, observer, _, _ = observation
    initial = index.get(str(root))
    control.set_watch(str(root), True)
    moved = root.with_name("moved")
    root.rename(moved)
    observer.scan()
    assert index.get(str(root)) == initial
    assert control.status(str(root))["diagnostic"]
    cursor = control.events()["cursor"]
    observer.scan()
    assert control.events(after=cursor)["items"] == []
    root.symlink_to(moved, target_is_directory=True)
    observer.scan()
    assert index.get(str(moved)) is None
    root.unlink()
    moved.rename(root)
    observer.scan()
    assert control.status(str(root))["diagnostic"] is None
    assert index.get(str(root)) == initial
    assert control.events()["items"][-1]["payload"]["recovered"] is True


def test_special_files_and_links_cannot_block_observation(observation, tmp_path):
    root, index, control, observer, _, _ = observation
    run = next((root / ".harness/runs").iterdir())
    fifo = run / "pipe.log"
    os.mkfifo(fifo)
    link = run / "external.json"
    link.symlink_to(tmp_path / "external.json")
    control.set_watch(str(root), True)
    observer.scan()
    assert indexed(index, root, fifo).status == "error"
    assert indexed(index, root, link).status == "error"


def test_index_event_rollback_is_atomic(observation):
    root, index, control, _, _, _ = observation
    before = index.get(str(root))
    cursor = control.events()["cursor"]
    path = next(root.rglob("review-00.json"))
    path.write_text('{"verdict":"REVISE"}')

    def fail_event(connection, cursor, statement, parameters, context, executemany):
        if statement.startswith("INSERT INTO legacy_events"):
            raise RuntimeError("Caída sintética antes del commit")

    event.listen(index.engine, "before_cursor_execute", fail_event)
    try:
        with pytest.raises(RuntimeError, match="Caída sintética"):
            index.replace(legacy.LocalLegacyReader().read(str(root)))
    finally:
        event.remove(index.engine, "before_cursor_execute", fail_event)
    assert index.get(str(root)) == before
    assert control.events(after=cursor)["items"] == []
    index.replace(legacy.LocalLegacyReader().read(str(root)))
    assert len(control.events(after=cursor)["items"]) == 1


def test_concurrent_identical_imports_publish_once(observation):
    root, index, control, _, _, _ = observation
    path = next(root.rglob("review-00.json"))
    path.write_text('{"verdict":"REVISE"}')
    inventory = legacy.LocalLegacyReader().read(str(root))
    cursor = control.events()["cursor"]
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(index.replace, [inventory, inventory]))
    assert len(control.events(after=cursor)["items"]) == 1


def test_api_controls_cursor_validation_and_metadata(observation, tmp_path):
    root, _, _, _, url, _ = observation
    base = f"/api/legacy/projects/{identifier(str(root))}"
    with TestClient(create_app(url, tmp_path), **LOCAL) as client:
        assert client.get(base + "/observation").json() == {"enabled": False, "diagnostic": None}
        assert client.put(base + "/observation", json={"enabled": True}).json()["enabled"] is True
        assert client.put(base + "/observation", json={"enabled": "yes"}).status_code == 422
        assert client.put(base + "/observation", json={"enabled": False, "extra": 1}).status_code == 422
        assert client.get("/api/legacy/projects/unknown/observation").status_code == 404
        assert client.get("/api/legacy/updates?after=-1").status_code == 422
        assert client.get("/api/legacy/updates?after=9007199254740992").status_code == 422
        assert client.get("/api/legacy/updates?after=100000").status_code == 409
        assert client.get("/api/legacy/events", headers={"Last-Event-ID": "no"}).status_code == 422
        assert client.get("/api/legacy/events", headers={"Last-Event-ID": "-1"}).status_code == 422
        assert client.get("/api/legacy/events?after=100000").status_code == 409
        assert client.put(base + "/observation", json={"enabled": False}).json()["enabled"] is False
        path = next(root.rglob("review-00.json")).relative_to(root).as_posix()
        metadata = client.get(base + f"/artifacts/{identifier(path)}").json()
        assert metadata["path"] == path and metadata["status"] == "available"


def test_sse_http_last_event_id_precedence_and_wire_format(observation, tmp_path, monkeypatch):
    _, _, control, _, url, _ = observation
    head = control.events()["cursor"]
    # Terminate the actual production generator after its first database batch,
    # so TestClient can collect a finite response without buffering forever.
    import harness_local.api.legacy as api_legacy

    async def finite(repository, after, disconnected):
        iterations = 0

        async def disconnected_once():
            nonlocal iterations
            iterations += 1
            return iterations > 1 + head

        async for frame in event_frames(repository, after, disconnected_once, interval=0):
            yield frame

    monkeypatch.setattr(api_legacy, "event_frames", finite)
    with TestClient(create_app(url, tmp_path)) as client:
        response = client.get("/api/legacy/events?after=9999", headers={"Last-Event-ID": "0"})
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        assert response.headers["cache-control"] == "no-store"
        assert f"id: {head}\nevent: legacy_update\ndata: " in response.text
        item = json.loads(response.text.split("data: ")[1].split("\n\n")[0])
        assert item["id"] == head and item["kind"] == "index_updated"
        replay = client.get("/api/legacy/events", headers={"Last-Event-ID": str(head)})
        assert "data:" not in replay.text


def test_sse_replay_10000_events_ordered_in_bounded_batches(observation):
    root, index, control, _, _, _ = observation
    head = control.events()["cursor"]
    with Session(index.engine) as session, session.begin():
        session.add_all(LegacyEventRow(root=str(root), kind="index_updated", observed_at="synthetic",
                                      payload={"n": n}) for n in range(10000))

    async def collect():
        delivered = []

        async def disconnected():
            return len(delivered) == 10000

        async for frame in event_frames(control, head, disconnected, interval=0):
            if frame.startswith("id:"):
                delivered.append(json.loads(frame.split("data: ")[1])["id"])
        return delivered

    delivered = asyncio.run(collect())
    assert delivered == list(range(head + 1, head + 10001))
    assert control.events(after=delivered[-1])["items"] == []


def test_migration_h12_preserves_index_and_defaults_to_disabled(observation):
    root, index, control, _, _, config = observation
    initial = index.get(str(root))
    control.set_watch(str(root), True)
    command.downgrade(config, "0002_legacy_index")
    command.upgrade(config, "head")
    command.check(config)
    assert index.get(str(root)) == initial
    assert control.status(str(root))["enabled"] is False
    assert control.events()["items"] == []


def test_sse_waits_for_live_commit_and_reconnect_skips_delivered_id(observation):
    root, index, control, _, _, _ = observation
    head = control.events()["cursor"]
    path = next(root.rglob("review-00.json"))

    async def exercise():
        async def connected():
            return False

        stream = event_frames(control, head, connected, interval=0.01, duration=1)
        assert await anext(stream) == "retry: 1000\n\n"
        pending = asyncio.create_task(anext(stream))
        await asyncio.sleep(0.02)
        assert not pending.done()
        path.write_text('{"verdict":"REVISE"}')
        await asyncio.to_thread(index.replace, legacy.LocalLegacyReader().read(str(root)))
        frame = await asyncio.wait_for(pending, timeout=1)
        delivered = json.loads(frame.split("data: ")[1])["id"]
        await stream.aclose()
        replay = [frame async for frame in event_frames(control, delivered, connected, interval=0.001, duration=0.02)]
        assert replay == ["retry: 1000\n\n"]
        return delivered

    assert asyncio.run(exercise()) == head + 1


def test_file_changed_during_read_remains_pending_without_payload(observation, monkeypatch):
    root, index, control, observer, _, _ = observation
    path = next(root.rglob("review-00.json"))
    control.set_watch(str(root), True)
    read = os.read
    mutated = False

    def mutate(fd, limit):
        nonlocal mutated
        chunk = read(fd, limit)
        if not mutated and b'"verdict"' in chunk:
            mutated = True
            path.write_text('{"verdict":"REVISE"}')
        return chunk

    monkeypatch.setattr(legacy.os, "read", mutate)
    observer.scan()
    assert indexed(index, root, path).status == "pending"
    assert indexed(index, root, path).payload is None
    observer.scan()
    assert indexed(index, root, path).status == "available"

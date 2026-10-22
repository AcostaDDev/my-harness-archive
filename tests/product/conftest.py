from pathlib import Path
import shutil

from alembic import command
from alembic.config import Config
import pytest


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def _migrated_template(tmp_path_factory):
    """A single real migration to head per session; each test gets a copy of the closed file."""
    path = tmp_path_factory.mktemp("migrated") / "template.sqlite3"
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("HARNESS_DATABASE_URL", f"sqlite:///{path}")
        command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
    assert not path.with_name(path.name + "-wal").exists()
    return path


@pytest.fixture
def migrated_database(tmp_path, monkeypatch, _migrated_template):
    target = tmp_path / "synthetic.sqlite3"
    shutil.copyfile(_migrated_template, target)
    url = f"sqlite:///{target}"
    monkeypatch.setenv("HARNESS_DATABASE_URL", url)
    return url, Config(str(ROOT / "alembic.ini"))


@pytest.fixture
def _legacy_close(monkeypatch):
    """Simulates the previous producer to verify its frozen operations and their reconciliation.

    The new T004 tests use the real producer, without this fixture.
    """
    from harness_local.storage import closure
    from harness_local.storage.transition import TransitionRepository
    original = closure.prepare
    monkeypatch.setattr(closure, 'prepare', lambda context, state, git:
                        None if state['phase']['status'] == 'CLOSED' else original(context, state, git))
    monkeypatch.setattr(TransitionRepository, '_retired', lambda self: None)

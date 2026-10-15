from pathlib import Path

from alembic import command
from alembic.config import Config
import pytest


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def migrated_database(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'synthetic.sqlite3'}"
    monkeypatch.setenv("HARNESS_DATABASE_URL", url)
    config = Config(str(ROOT / "alembic.ini"))
    command.upgrade(config, "head")
    return url, config


@pytest.fixture
def _legacy_close(monkeypatch):
    """Simula el productor anterior para verificar sus operaciones congeladas y su conciliación.

    Las pruebas nuevas de T004 usan el productor real, sin este fixture.
    """
    from harness_local.storage import closure
    from harness_local.storage.transition import TransitionRepository
    original = closure.prepare
    monkeypatch.setattr(closure, 'prepare', lambda context, state, git:
                        None if state['phase']['status'] == 'CLOSED' else original(context, state, git))
    monkeypatch.setattr(TransitionRepository, '_retired', lambda self: None)

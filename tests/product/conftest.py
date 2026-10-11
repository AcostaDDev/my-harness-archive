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

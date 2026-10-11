import os
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine, make_url


def database_url() -> str:
    return os.environ.get("HARNESS_DATABASE_URL", "sqlite:///.local/harness.sqlite3")


def make_engine(url: str) -> Engine:
    parsed = make_url(url)
    if parsed.drivername != "sqlite" or not parsed.database or parsed.database == ":memory:":
        raise ValueError("H0.3 requiere un archivo SQLite local.")
    # La creación del directorio ocurre al conectar, nunca al exportar OpenAPI.
    engine = create_engine(url, connect_args={"check_same_thread": False, "autocommit": False})

    @event.listens_for(engine, "do_connect")
    def prepare_directory(dialect, connection_record, args, params):
        Path(parsed.database).parent.mkdir(parents=True, exist_ok=True)

    @event.listens_for(engine, "connect")
    def configure_sqlite(connection, connection_record):
        previous = connection.autocommit
        connection.autocommit = True
        cursor = connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=5000")
        finally:
            cursor.close()
            connection.autocommit = previous

    return engine

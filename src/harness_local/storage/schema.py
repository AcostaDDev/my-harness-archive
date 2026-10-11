from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


SCHEMA_REVISION = "0002_legacy_index"


def require_schema(engine: Engine) -> None:
    try:
        with engine.connect() as connection:
            revision = connection.scalar(text("SELECT version_num FROM alembic_version"))
            if revision != SCHEMA_REVISION:
                raise RuntimeError("Migración incompatible: ejecutar alembic upgrade head.")
            for table in ("simulations", "legacy_sources", "legacy_runs", "legacy_artifacts"):
                connection.execute(text(f"SELECT * FROM {table} LIMIT 0"))
    except SQLAlchemyError as error:
        raise RuntimeError("Base SQLite no preparada; ejecutar uv run --frozen alembic upgrade head.") from error

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


SCHEMA_REVISION = "0008_prompt_versions"


def require_schema(engine: Engine) -> None:
    try:
        with engine.connect() as connection:
            revision = connection.scalar(text("SELECT version_num FROM alembic_version"))
            if revision != SCHEMA_REVISION:
                raise RuntimeError("Migración incompatible: ejecutar alembic upgrade head.")
            for table in ("simulations", "legacy_sources", "legacy_runs", "legacy_artifacts", "legacy_events",
                          "managed_runs", "managed_jobs", "managed_attempts", "managed_events", "checkout_locks", "managed_processes",
                          "managed_commits", "managed_activations", "prompt_heads", "prompt_versions", "prompt_activations"):
                connection.execute(text(f"SELECT * FROM {table} LIMIT 0"))
    except SQLAlchemyError as error:
        raise RuntimeError("Base SQLite no preparada; ejecutar uv run --frozen alembic upgrade head.") from error

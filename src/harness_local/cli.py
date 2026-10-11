"""Entrada local H1.1 sin servicio, motor ni proveedores."""
import argparse
import json
from pathlib import Path
import sys

from sqlalchemy.exc import SQLAlchemyError

from harness_local.adapters.legacy import LocalLegacyReader
from harness_local.core.legacy import LegacyImportService
from harness_local.storage.database import database_url, make_engine
from harness_local.storage.legacy import SQLiteLegacyRepository
from harness_local.storage.schema import require_schema


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Índice legacy local de lectura")
    parser.add_argument("operation", choices=("legacy-import", "legacy-summary"))
    parser.add_argument("checkout", help="Raíz del checkout; contiene .harness/runs")
    args = parser.parse_args(argv)
    engine = None
    try:
        engine = make_engine(database_url())
        root = str(Path(args.checkout).expanduser().resolve())
        # Comprobar antes de abrir SQLite (WAL/creación también son escrituras).
        if Path(engine.url.database).resolve().is_relative_to(Path(root)):
            raise ValueError("El índice SQLite debe estar fuera del checkout de origen.")
        require_schema(engine)
        service = LegacyImportService(SQLiteLegacyRepository(engine), LocalLegacyReader())
        if args.operation == "legacy-import":
            service.import_checkout(root)
        summary = service.summary(root)
        if summary is None:
            raise ValueError("Origen no importado; ejecutar legacy-import explícitamente.")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    except (OSError, RuntimeError, ValueError, SQLAlchemyError) as error:
        print(str(error), file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())

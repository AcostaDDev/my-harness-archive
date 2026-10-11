"""Exportar contratos sin iniciar servicio, conectar SQLite ni ejecutar simulaciones."""
import json
from pathlib import Path

from harness_local.api.app import create_app


if __name__ == "__main__":
    target = Path("frontend/openapi.json")
    target.write_text(json.dumps(create_app().openapi(), ensure_ascii=False, indent=2) + "\n")
    print(target)

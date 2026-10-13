"""Entrada instalada: SQLite explícita, preparación separada y loopback fijo."""
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.engine import URL

from harness_local.storage.database import make_engine
from harness_local.storage.schema import require_schema


def local_database(value: str) -> tuple[Path, str]:
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise ValueError('SQLite requiere una ruta absoluta (--database).')
    return path, URL.create('sqlite', database=str(path)).render_as_string(hide_password=False)


def initialize(value: str) -> None:
    path, url = local_database(value)
    # Exclusivo: nunca migrar ni sobrescribir una base existente (incluidos enlaces).
    if any(Path(str(path) + suffix).exists() or Path(str(path) + suffix).is_symlink()
           for suffix in ('-wal', '-shm', '-journal')):
        raise ValueError('Hay archivos auxiliares SQLite; conservarlos y usar un destino nuevo.')
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('xb'):
            pass
    except FileExistsError as error:
        raise ValueError('El destino ya existe; init-db solo prepara una SQLite nueva.') from error
    config = Config()
    config.set_main_option('script_location', str(Path(__file__).parent / 'migrations').replace('%', '%%'))
    config.attributes['database_url'] = url
    command.upgrade(config, 'head')


def serve(value: str, port: int) -> None:
    import uvicorn
    from harness_local.api.app import create_app

    path, url = local_database(value)
    if not 1 <= port <= 65535:
        raise ValueError('El puerto debe estar entre 1 y 65535.')
    if not path.is_file():
        raise ValueError('SQLite ausente; preparar una base nueva con harness-local init-db --database RUTA.')
    assets = Path(__file__).parent / 'web'
    if not (assets / 'index.html').is_file():
        raise ValueError('Assets web ausentes; instalar el paquete construido con scripts/build_distribution.py.')
    engine = make_engine(url)
    try:
        require_schema(engine)
    except RuntimeError as error:
        raise RuntimeError('Esquema SQLite incompatible o incompleto; detener el servicio, conservar backup y '
                           'migrar explícitamente con la versión compatible. init-db no actualiza bases existentes.') from error
    finally:
        engine.dispose()
    # El lifespan conserva validación de configuración, restauraciones y opt-in.
    uvicorn.run(create_app(url=url), host='127.0.0.1', port=port, workers=1,
                proxy_headers=False)

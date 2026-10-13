"""Índice, backup, retención y version/help explícitos; sin inferencia."""
import argparse
import json
from pathlib import Path
import sys
import sqlite3

from sqlalchemy.exc import SQLAlchemyError

from harness_local.adapters.legacy import LocalLegacyReader
from harness_local.core.legacy import LegacyImportService
from harness_local.storage.database import database_url, make_engine
from harness_local.storage.legacy import SQLiteLegacyRepository
from harness_local.storage.schema import require_schema
from harness_local.storage.backup import create_backup, restore_backup, verify_bundle
from harness_local.storage.retention import preview_retention, apply_retention, inspect_logs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Índice legacy, backup, retención y diagnóstico local")
    operations = parser.add_subparsers(dest='operation', required=True)
    for name in ('legacy-import', 'legacy-summary'):
        command = operations.add_parser(name)
        command.add_argument('checkout', help='Raíz del checkout; contiene .harness/runs')
    command = operations.add_parser('backup-create', help='Servicio y escritores detenidos; destino nuevo')
    command.add_argument('database', help='Archivo SQLite explícito; no usa HARNESS_DATABASE_URL')
    command.add_argument('destination')
    command.add_argument('--artifact-root', action='append', default=[], help='Raíz permitida de artefactos; repetible')
    command.add_argument('--writers-stopped', action='store_true', help='Declaro detenidos servicio, observadores y escritores')
    command = operations.add_parser('backup-verify')
    command.add_argument('bundle')
    command = operations.add_parser('backup-restore', help='Destino nuevo; restauración solo de consulta')
    command.add_argument('bundle')
    command.add_argument('destination')
    for name in ('logs-preview', 'logs-apply'):
        command = operations.add_parser(name, help='Retención explícita de stdout/stderr CLI sellados')
        command.add_argument('database')
        command.add_argument('--artifact-root', action='append', required=True)
        command.add_argument('--before', required=True, help='Fecha de corte ISO-8601 UTC, exclusiva')
        command.add_argument('--min-bytes', type=int, default=1024 * 1024)
        if name == 'logs-apply':
            command.add_argument('--preview-sha256', required=True)
            command.add_argument('--reason', required=True)
            command.add_argument('--confirmed', action='store_true')
            command.add_argument('--writers-stopped', action='store_true')
    command = operations.add_parser('logs-inspect', help='Distinguir retenido, purgado, pendiente, perdido y no verificado')
    command.add_argument('database')
    command.add_argument('attempt_id')
    command = operations.add_parser('diagnose-cli', help='Version/help explícitos, sin autenticación ni inferencia')
    command.add_argument('configuration', help='JSON de una CLIConfig con entorno explícito; ejecutable de confianza')
    command = operations.add_parser('check-config', help='Validar el TOML local de uso real, sin ejecutar nada')
    command.add_argument('configuration', help='Ruta absoluta del TOML local, fuera de los checkouts')
    command.add_argument('--preflight', action='store_true', help='Además, version/help explícitos de la CLI de cada agente')
    for name in ('init-db', 'serve'):
        command = operations.add_parser(name, help='SQLite nueva explícita' if name == 'init-db' else 'UI/API en 127.0.0.1')
        command.add_argument('--database', required=True, help='Ruta absoluta SQLite; no usa HARNESS_DATABASE_URL')
        if name == 'serve':
            command.add_argument('--port', type=int, default=8013)
            command.add_argument('--config', help='TOML local de uso real (local-config-1); por defecto, sin proyectos')
    args = parser.parse_args(argv)
    engine = None
    try:
        if args.operation in ('init-db', 'serve'):
            from harness_local.launcher import initialize, serve
            if args.operation == 'init-db':
                initialize(args.database)
            else:
                serve(args.database, args.port, args.config)
            return 0
        if args.operation == 'check-config':
            from harness_local.services.local_config import inspect_local_config, summary
            config, agents = inspect_local_config(args.configuration)
            result = summary(config)
            if args.preflight:
                from harness_local.adapters.cli_agents import access_for
                from harness_local.adapters.cli_diagnostics import preflight_config
                # Mismo CLIConfig validado por agente para todos los proyectos; solo version/help.
                result['preflight'] = {agent: preflight_config(cli, access=access_for(agent))
                                       for agent, cli in agents.items()}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if not args.preflight or all(r['available'] for r in result['preflight'].values()) else 1
        if args.operation == 'diagnose-cli':
            from harness_local.adapters.cli_diagnostics import diagnose_file
            result = diagnose_file(args.configuration)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if (result.get('preflight') or {}).get('available') else 1
        if args.operation.startswith('logs-'):
            if args.operation == 'logs-inspect':
                result = inspect_logs(args.database, args.attempt_id)
            else:
                kwargs = dict(artifact_roots=args.artifact_root, before=args.before, min_bytes=args.min_bytes)
                if args.operation == 'logs-apply':
                    kwargs.update(preview_sha256=args.preview_sha256, reason=args.reason,
                                  confirmed=args.confirmed, writers_stopped=args.writers_stopped)
                    result = apply_retention(args.database, **kwargs)
                else:
                    result = preview_retention(args.database, **kwargs)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.operation.startswith('backup-'):
            if args.operation == 'backup-create':
                manifest = create_backup(args.database, args.destination, artifact_roots=args.artifact_root,
                                         writers_stopped=args.writers_stopped)
            elif args.operation == 'backup-restore':
                manifest = restore_backup(args.bundle, args.destination)
            else:
                manifest = verify_bundle(args.bundle)
            print(json.dumps(manifest, ensure_ascii=False, indent=2))
            return 0
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
    except (OSError, RuntimeError, ValueError, LookupError, SQLAlchemyError, sqlite3.Error) as error:
        print(str(error), file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())

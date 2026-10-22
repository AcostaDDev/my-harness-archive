"""Index, backup, retention, metrics backfill and explicit version/help; no inference."""
import argparse
from contextlib import closing
import json
from pathlib import Path
import sys
import sqlite3

from sqlalchemy.exc import SQLAlchemyError

from harness_local.storage.database import make_engine
from harness_local.storage.schema import require_schema
from harness_local.storage.backup import create_backup, restore_backup, verify_bundle
from harness_local.storage.retention import preview_retention, apply_retention, inspect_logs
from harness_local.i18n import DEFAULT_LANGUAGE, LANGUAGES, message


def cli_language(explicit: str | None, database: str | None) -> str:
    """D166: `--ui-language` for this invocation; otherwise the preferences of an existing database; otherwise en.

    The database is opened read-only and never created, migrated or repaired; nothing is saved.
    """
    if explicit is not None:
        return explicit
    path = Path(database).expanduser() if database else None
    if path is None or not path.is_absolute() or not path.is_file():
        return DEFAULT_LANGUAGE
    try:
        with closing(sqlite3.connect(f'{path.as_uri()}?mode=ro', uri=True)) as db:
            row = db.execute('SELECT format, ui_language FROM product_preferences WHERE id = 1').fetchone()
    except sqlite3.Error:
        return DEFAULT_LANGUAGE
    return row[1] if row and row[0] == 'product-preferences-1' and row[1] in LANGUAGES else DEFAULT_LANGUAGE


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Backup, retención y diagnóstico local")
    parser.add_argument('--ui-language', choices=LANGUAGES,
                        help="Language of this invocation's own messages; not saved "
                             "(default: database preferences, else en)")
    operations = parser.add_subparsers(dest='operation', required=True)
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
    command = operations.add_parser('metrics-backfill', help='Relleno explícito e idempotente de métricas por intento (H6.4)')
    command.add_argument('--database', required=True, help='Ruta absoluta SQLite existente; no usa HARNESS_DATABASE_URL')
    command.add_argument('--artifact-root', action='append', default=[],
                         help='Raíz autorizada de streams sellados, verificados por SHA-256; repetible. Sin ella, solo result_json')
    command = operations.add_parser('migrate', help='Actualizar SQLite existente con instantánea previa verificada')
    command.add_argument('--database', required=True, help='Ruta absoluta SQLite existente; no usa HARNESS_DATABASE_URL')
    command.add_argument('--snapshots', required=True, help='Directorio absoluto de instantáneas, fuera de los checkouts')
    command.add_argument('--writers-stopped', action='store_true', help='Declaro detenidos servicio, observadores y escritores')
    for name in ('init-db', 'serve'):
        command = operations.add_parser(name, help='SQLite nueva explícita' if name == 'init-db' else 'UI/API en 127.0.0.1')
        command.add_argument('--database', required=True, help='Ruta absoluta SQLite; no usa HARNESS_DATABASE_URL')
        if name == 'serve':
            command.add_argument('--port', type=int, default=8013)
            command.add_argument('--config', help='TOML local de uso real (local-config-5; también 1–4); por defecto, sin proyectos')
    args = parser.parse_args(argv)
    language = cli_language(args.ui_language, getattr(args, 'database', None))
    engine = None
    try:
        if args.operation == 'migrate':
            from dataclasses import asdict
            from harness_local.storage.migrate import migrate_database
            result = migrate_database(args.database, Path(args.snapshots), writers_stopped=args.writers_stopped)
            print(json.dumps(asdict(result), default=str, ensure_ascii=False, indent=2))
            return 0
        if args.operation in ('init-db', 'serve'):
            from harness_local.launcher import initialize, serve
            if args.operation == 'init-db':
                initialize(args.database, language)
            else:
                serve(args.database, args.port, args.config, language)
            return 0
        if args.operation == 'metrics-backfill':
            from harness_local.launcher import local_database
            from harness_local.storage.metrics import backfill
            path, url = local_database(args.database, language)
            if not path.is_file():
                raise ValueError(message('cli.backfill_missing', language))
            engine = make_engine(url)
            require_schema(engine)
            print(json.dumps(backfill(engine, artifact_roots=args.artifact_root), ensure_ascii=False, indent=2))
            return 0
        if args.operation == 'check-config':
            from harness_local.services.local_config import inspect_local_config, summary
            config, agents = inspect_local_config(args.configuration)
            result = summary(config)
            if args.preflight:
                from harness_local.adapters.cli_agents import access_for
                from harness_local.adapters.cli_diagnostics import preflight_config
                # Defaults and per-role capabilities of each preset; explicit version/help only.
                result['preflight'] = {agent: preflight_config(cli, access=access_for(agent.rsplit('.', 1)[-1]))
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
    except (OSError, RuntimeError, ValueError, LookupError, SQLAlchemyError, sqlite3.Error) as error:
        print(str(error), file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())

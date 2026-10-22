# P010-T012 — Migración explícita desde el paquete instalado

Fecha: 2026-10-22. Base: `b694c28`. Decisión:
[D150](../DECISIONS.md#d150--p010-t012-migración-explícita-de-bases-desde-la-cli-instalada).
**Estado: implementado y verificado offline** con SQLite temporal y datos sintéticos. Resuelve la ausencia de una
orden de actualización instalada identificada por T006/T007 (D148, D149). El recorrido del wheel queda para T009;
no se ha migrado ninguna instalación real ni iniciado servicios o proveedores.

## 1. Entrega y motivo

La CLI añade:

```sh
harness-local migrate --database /ruta/state/harness.sqlite3 --snapshots /ruta/copias-previas --writers-stopped
```

Reutiliza la migración con instantánea de D053 para cumplir SPECIFICATION §9 también fuera del checkout de
desarrollo. `init-db` conserva creación exclusiva y `serve` conserva arranque sin migración (D043).

| Pieza | Resultado |
|---|---|
| `cli.py` | Suborden, ayuda y salida JSON de `MigrationOutcome`: `action`, `previous`, `revision`, `snapshot`. Fallo con diagnóstico por stderr y código 1. |
| `storage/migrate.py` | Entrada `migrate_database` que exige declaración de parada y nunca crea bases; motor compartido con `prepare_database`. |
| Guardias | Rutas absolutas, sin enlaces ni `..`; auxiliares regulares; copias fuera de checkouts Git y raíces persistidas; revisiones conocidas, Alembic y exclusión de restauraciones. Propietarios de jobs/preparaciones y grupos CLI/validaciones vivos bloquean, también si la base está al día. |
| Instantánea | Formato `premigration-1` conservado; añade comprobación de revisión y fsync de SQLite, manifiesto y directorio antes de migrar. Integridad y SHA-256, archivo exclusivo 0600. |
| Distribución | `check_distribution.py` incluye ausencia de base, falta de declaración, `0022`→head, copia, repetición sin cambios y arranque posterior. Preparado; no ejecutado en esta tarea. |
| Documentación | README («Actualizar»), ARCHITECTURE §§9–10, [flujo](../flows/database-migration.md), matriz, estado, tareas, roadmap y D150. |

Sin migraciones nuevas ni cambios de modelos, DDBB-DIAGRAM, API, tipos o UI. La migración canónica `0023` se
ejecuta sin modificaciones y conserva la compatibilidad de los formatos 1–8.

## 2. Comportamiento y recuperación

1. El operador detiene servicio, observadores y escritores y escoge rutas absolutas. La orden ignora
   `HARNESS_DATABASE_URL`; no lee configuración global ni descubre proveedores.
2. Una base ausente se rechaza sin crear directorios ni archivos; la creación sigue siendo `init-db`. Enlaces,
   revisiones desconocidas/más nuevas, bases sin Alembic y restauraciones de consulta se rechazan antes de copiar.
3. Comprueba las identidades persistidas de jobs, preparaciones, procesos y eventos de comandos. Las revisiones
   antiguas sin esas tablas/columnas siguen siendo migrables. Valida el destino de copias sin crearlo.
4. Revisión actual: `current`, sin escritura ni copia. Revisión anterior: backup SQLite exclusivo, integridad,
   revisión y manifiesto con SHA-256; fsync antes de `upgrade head` y comprobación del esquema tras completarlo.
5. Fallo al copiar/sellar: no llama a Alembic y conserva parciales. Fallo al migrar: diagnóstico con ruta de copia,
   conservando el estado resultante y la copia anterior; no restaura, borra ni reintenta automáticamente.

`--writers-stopped` declara también que no hay un servicio inactivo sin propietario persistido. Es la misma
frontera cooperativa que backup; no se añade un registro global de procesos ni se deduce muerte por leases. El
operador mantiene detenidos los escritores durante toda la operación. La instantánea contiene solo SQLite, sin
artefactos externos: no sustituye el bundle de `backup-create` ni es una restauración de consulta.

`scripts/dev` conserva su interfaz, creación, ubicación de copias y migración previa al arranque. Comparte las
guardias ampliadas y la instantánea; no necesita los nuevos argumentos de la CLI instalada.

## 3. Evidencia sintética

`tests/product/test_installed_migration.py`: 26 casos nuevos.

- Base `0022` con historiales sintéticos de los ocho formatos: migración por la CLI, verificación de cada proyección
  y conservación literal de `context_json`, `versions_json` y `history_json` en origen y copia. Se verifica integridad,
  revisión y SHA-256 de la instantánea. Funciona desde otro cwd y con una variable de base ambiental incorrecta.
- La base resultante supera la comprobación real de esquema de `serve`; se sustituye `uvicorn.run` para no arrancar
  un servicio. Repetir devuelve `current`, conserva bytes y no genera otra copia. También se cubre `current` con
  un directorio de copias inexistente que permanece ausente.
- Negativas sin cambiar bytes de la base ni crear copias: falta de declaración, revisión futura, restauración,
  ausencia de Alembic y propietario/grupo vivo de cada fuente. Identidades del proceso de prueba, sin lanzar agentes.
- Base ausente, ruta relativa, directorio, enlace directo/roto/en padre y auxiliar enlazado; destino relativo,
  checkout Git, raíz persistida y directorio de copias enlazado.
- Fallo de copia impide ejecutar Alembic. Fallo sintético tras una escritura conserva tanto la escritura como la
  copia anterior, acreditando que no restaura automáticamente. Un historial inválido hace fallar realmente `0023`:
  rollback transaccional de tablas/revisión, historial intacto e instantánea previa conservada.
- Revisiones `0001` y `0004` migran sin exigir columnas de propietarios aún inexistentes.

Las pruebas existentes de desarrollo y launcher pasan sin modificar sus expectativas. Las instantáneas se comparan
por contenido SQL cuando procede: la API de backup puede cambiar contadores internos del archivo SQLite sin cambiar
los datos congelados.

## 4. Comprobaciones ejecutadas

Sobre el árbol de trabajo de esta tarea (base `b694c28`), el 2026-10-22:

- `pytest -q` completa (xdist): **1680 passed, 2 skipped, 121 subtests passed**, en 139 s. Las dos variantes opt-in
  reales (Django y TypeScript) siguen omitidas. Aviso existente de deprecación de FastAPI/httpx.
- Después se añaden los casos de fallo real de `0023` y base actual sin directorio de copias. Ejecución final de
  `test_installed_migration.py`, `test_dev_command.py` y `test_launcher.py`, en serie: **50 passed**. La suite completa
  anterior incluye los otros 24 casos nuevos; no se repite por estos dos tests adicionales ni por cambios documentales.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: **12 OK**.
- `alembic upgrade head` y `alembic check` sobre SQLite temporal mediante `_config`: **sin operaciones nuevas**.
- Ayuda de `migrate`, sintaxis del verificador, enlaces locales modificados y `git diff --check`: correctos.

Node, tipos y build no se ejecutan porque no cambian frontend, OpenAPI ni API. No se construye/instala el wheel ni se
ejecuta `check_distribution.py`; su recorrido se acreditará en T009, como requiere NEXT_STEPS. Sin descargas,
proveedores, smokes, servicios, configuración global, base operativa ni operación del hijo Django de P009.

Siguiente tarea: **P010-T008**, propuesta de validación real complementaria y decisión de alcance.

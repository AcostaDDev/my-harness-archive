# P010-T003 — Consultas de runs sin decodificar todo el historial

Fecha: 2026-10-22. Base: `bfbd006`. Decisión:
[D144](../DECISIONS.md#d144--p010-t003-proyección-run-projection-1-implementada).
**Estado: implementado y verificado offline** con historiales sintéticos, motor y agentes falsos y SQLite temporal.
Implementa el [contrato de T001 §2](P010-T001_CONTRATO_CONSOLIDACION.md#2-lecturas-de-runs-sin-decodificar-el-historial-t003-y-t011)
para las vistas de runs (D142). Métricas y vista previa de exportación siguen decodificando hasta T011. Sin
proveedores, smokes, servicios ni migración de la instalación real.

## 1. Qué se entrega

Las vistas de runs leen una proyección derivada, `run-projection-1`, escrita en la misma transacción que
`managed_runs.history_json`, que sigue siendo la autoridad. Ninguna vista selecciona `history_json` ni llama a
`load_history`.

| Pieza | Cambio |
|---|---|
| `storage/run_projection.py` (nuevo) | Filas derivadas de un historial en orden de clave primaria, escritura inicial e incremental y comparación para el backup. |
| `storage/models.py`, `migrations/versions/0023_run_projection.py` (nuevo), `storage/schema.py` | Seis tablas derivadas con FK a `managed_runs`. La migración rellena cada historial existente una vez, sin reescribirlo; el downgrade solo las elimina. Esquema `0023_run_projection`, 48 tablas. |
| `storage/managed.py` | `_queue_new_run` crea la proyección del run nuevo; `_history` la avanza tras validar el solo-añadir: añade paradas y ciclos, y actualiza la revisión de un ciclo previo. |
| `storage/managed_views.py` | Detalle, ciclos, diff, casos JUnit y original sobre la proyección. Las filas de run cargan solo columnas declaradas (`load_only` con `raiseload`). Las tareas de una fase cuentan en SQL y leen solo el último run de las tareas de la página. `exists` y los listados auxiliares consultan solo el id. |
| `storage/permissions.py` | La lista de permisos comprueba el run sin cargar el historial. |
| `storage/backup.py` | Recalcula la proyección de cada run y compara filas y recuentos por tabla; si difiere, `BackupError` con diagnóstico. |
| API (`schemas.py`, `managed.py`), OpenAPI y tipos | `history.cycles` pasa a `history.cycle_count` y `history.latest_cycle`; `GET /runs/{id}/cycles` pagina los ciclos (10 por defecto, hasta 100). |
| UI (`pages/Run.tsx`, `ChatCommand.tsx`) | La sección de revisiones pagina los ciclos y los sondea con el detalle; `tests` del chat usa el último ciclo. |
| Documentación | [DDBB-DIAGRAM](../DDBB-DIAGRAM.md#proyección-de-runs-p010-t003), [flujo de tarea](../flows/task-run.md#lectura-del-run-d144), ARCHITECTURE (módulos y límites). |

## 2. Diseño concreto

- **Tablas.** `run_projections` (estado del historial, contrato congelado, recuentos de intentos, ejecuciones, ciclos y
  paradas, parada actual, aceptación y `history_sha256`), `run_projection_stops`, `run_projection_cycles` (veredicto,
  huella, rutas, hash y tamaño del diff, procedencia, revisión, formateo, vista de validación sin casos y evidencia
  validada para los casos), `run_projection_diff_chunks`, `run_projection_reports` (resumen, original y recuento) y
  `run_projection_cases` (por ordinal). JSON en texto exacto del historial o congelado con `freeze`, para comparar
  por igualdad.
- **Diff por tramos.** El diff UTF-8 se guarda en tramos fijos de 64 KiB. Una página pide `limit + 4` bytes desde
  `offset` y lee solo los tramos que los cubren: lo justo para cortar en fin de línea o completar una secuencia
  UTF-8 como antes. Se mantienen el hash, el 409 por hash distinto, el 422 de cursores inválidos y el 404 de ciclos
  desconocidos. Se eligen tramos frente a `substr` o E/S incremental de blobs: SQLite carga el valor entero para
  `substr` y los tramos son medibles con SQL corriente.
- **Detalle.** Conserva la forma salvo los ciclos. `stops` sigue completo: crece con los jobs y sus filas son
  pequeñas. Las acciones se calculan con los mismos datos (estado, contrato, ejecuciones, aceptación).
- **Escritura.** La autoridad ya garantiza el solo-añadir y que un ciclo previo solo gana su revisión; la proyección
  sigue esa misma regla. Una caída antes de confirmar deshace historial y proyección juntos.
- **Consistencia.** El backup la comprueba. Una proyección ausente en una vista es una base inconsistente y responde
  error del servidor, sin reconstruir nada. La cuarentena no cambia: las versiones congeladas no incluyen la proyección.

## 3. Medidas

Historial sintético de 26,4 MiB (formato 8): 40 ciclos, 30 paradas, 2.000 casos JUnit por ciclo y un diff de 4 MiB en
el último. Mejor de cinco lecturas en este equipo (macOS arm64), con la implementación anterior como referencia
(solo decodificación, sin contar la lectura del texto desde SQLite):

| Lectura | Proyección | Respuesta | Anterior |
|---|---|---|---|
| Detalle del run | 7,2 ms | 3,9 KiB | 746 ms |
| Página de 10 ciclos | 0,5 ms | 16,7 KiB | 748 ms |
| Página de diff de 64 KiB en mitad de 4 MiB | 0,5 ms (2 tramos) | 75 KiB | 320 ms |
| Página de 100 casos JUnit | 0,8 ms | 21,6 KiB | 325 ms |

El relleno de la migración para ese historial tarda 1,5 s. En los tests, la instrumentación cuenta las llamadas al
codec y las sentencias SQL de cada vista: cero decodificaciones, ninguna sentencia con `history_json` y una sola
consulta de tramos que abarca como mucho dos tramos.

## 4. Pruebas

`tests/product/test_run_projection.py` (nuevo) compara cada vista con una copia de la implementación anterior:

- Migración sobre runs previos de los formatos 1 a 8, un run sin ciclos, uno listo para commit y uno con revisión
  pendiente: historiales idénticos byte a byte tras la migración y tras el downgrade, proyección igual a la
  recalculada y detalle, acciones, ciclos con varios tamaños de página, diff con varios límites, casos y originales
  iguales a los de la implementación anterior, sin decodificar ni seleccionar el historial.
- Historial grande: lecturas acotadas e iguales (§3).
- Escritores: un run real con dos ciclos (REVISE y ACCEPT, JUnit) deja la proyección igual a la recalculada. Una caída
  simulada tras escribir la proyección y antes de confirmar no cambia ni el historial ni la proyección; una
  reescritura rechazada por la autoridad, tampoco.
- Backup: un veredicto alterado, un caso borrado o una parada huérfana en el bundle impiden restaurar.
- Listados, tareas de fase, jobs, intentos, eventos y permisos sin seleccionar el historial; acceder a una columna no
  declarada lanza.

Tests existentes ajustados a la nueva forma del detalle: `test_cycle_diff.py`, `test_junit.py`, `test_e2e_offline.py`,
`test_managed_api.py` y la revisión de esquema en `test_storage_api.py`.

## 5. Límites y observaciones

- Métricas (`summary`, `tasks`, `validations`) y la vista previa de exportación siguen decodificando historiales:
  T011.
- El relleno usa el codec vigente; un historial ilegible hace fallar la migración, que se deshace entera. No se ha
  migrado la instalación real: se hará con el backup previo de siempre al actualizar.
- Cambiar el tamaño del tramo o las columnas exige otra versión de la proyección y su migración.
- QA visual de la página del run no realizado; la UI se cubre con tipos, build y los tests de API.

## 6. Comprobaciones ejecutadas

Sobre el árbol de trabajo de esta tarea (base `bfbd006`), el 2026-10-22:

- `pytest -q` completa (xdist): 1643 passed, 2 skipped (variantes reales opt-in de Django y TypeScript), 121 subtests
  passed.
- `test_run_projection.py`: 7 passed, también en serie (`-n 0`).
- `python3 -m unittest discover`: 12 tests OK.
- `alembic upgrade head` y `alembic check` en una SQLite temporal: sin operaciones nuevas. Downgrade a `0022` y nueva
  subida en la misma base temporal, correctos.
- OpenAPI exportado y tipos regenerados. `node --test frontend/tests/*.test.mjs`: 82 pass. `npm --prefix frontend
  run check` y `run build`: correctos (solo el aviso conocido de tamaño de chunk).
- Medidas de §3 con un script local sobre una SQLite temporal.

No se ejecutaron proveedores, smokes, servicios, el wheel ni descargas; no se tocó configuración global, la base
operativa ni el hijo Django de P009.

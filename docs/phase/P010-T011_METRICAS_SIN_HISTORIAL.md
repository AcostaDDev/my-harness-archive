# P010-T011 — Métricas y exportación sin decodificar historiales

Fecha: 2026-10-22. Base: `389a3b1`. Decisión:
[D145](../DECISIONS.md#d145--p010-t011-métricas-y-vista-previa-de-exportación-sobre-la-proyección).
**Estado: implementado y verificado offline** con historiales sintéticos, motor y agentes falsos y SQLite temporal.
Completa el [contrato de T001 §2](P010-T001_CONTRATO_CONSOLIDACION.md#2-lecturas-de-runs-sin-decodificar-el-historial-t003-y-t011)
(D142) sobre la proyección `run-projection-1` de T003 (D144). Sin migración, tablas nuevas ni cambios de API, tipos o
UI. Sin proveedores, smokes, servicios ni migración de la instalación real.

## 1. Qué se entrega

Las métricas (`summary`, `tasks`, `validations`) y la vista previa de la exportación documental leen la proyección y
`managed_attempts`. Ninguna de esas lecturas llama a `load_history` ni selecciona `history_json`.

| Pieza | Cambio |
|---|---|
| `storage/run_projection.py` | Nuevas lecturas agregadas: `require` (un run sin proyección es una base inconsistente y responde error, sin reconstruir) y `cycle_tests`, que da los recuentos de `validation_counts` y `all_passed` de cada ciclo. |
| `storage/metrics.py` | `_task` toma ejecuciones, primer veredicto, tests del último ciclo y paradas de la proyección. `validations` agrega los ciclos del ámbito sobre `cycle_tests`. Las paradas de `summary` se agrupan, cuentan y ordenan en SQL con el tope `STOP_LIMIT`. |
| `storage/documents.py` | `state_snapshot(..., projected=True)` toma de la proyección y `managed_attempts` los intentos por rol, el resumen del último ejecutor, el veredicto y los tests del último ciclo. Sin `projected`, el motor sigue leyendo el historial. |
| `storage/document_export.py` | `snapshot(..., projected=True)` también en la forma D036, donde la aceptación sale de `acceptance_json`. Solo `DocumentExportRepository.preview` lo usa. |
| Documentación | ARCHITECTURE (límites), DDBB-DIAGRAM (lectores de la proyección) y el flujo de [documentos](../flows/documents.md#vista-previa-de-la-exportación-d145). |

## 2. Diseño concreto

- **Validación por ciclo sin casos en Python.** Para cada comando de `validation_json`, SQL (`json_each`,
  `json_extract`) extrae solo lo que decide `CommandResult.passed`: tipo y valor del código de salida, `error`,
  `timed_out` y `capture_json`. No trae `stdout` ni `stderr`. El predicado se evalúa con la misma clase del motor. El
  código de salida solo cuenta si es un entero JSON: SQLite devuelve `false` como 0 y el historial no lo acepta como
  éxito (`type(...) is int`). Los casos JUnit se cuentan con `GROUP BY` por reporte y resultado; la frescura y el
  estado de cada reporte salen de `summary_json`. Se reproducen así las reglas de `validation_counts` (solo reportes
  `complete` o `partial`, y un resultado desconocido cuenta como `error`) y de `all_passed` (fallos en reportes
  `created` o `changed`).
- **Intentos.** `_history` exige que cada intento del historial tenga su fila en `managed_attempts`, con el mismo
  número, request y resultado. La vista toma las filas `1..run_projections.attempts`: una fila posterior sin resultado
  corresponde a un intento en curso que aún no está en el historial y no cuenta. El rol y el `payload_json` se
  extraen en SQL, y el orden de los roles es el de su primera aparición, como antes.
- **Orden.** Runs por `created_at, id`, ciclos por número y paradas por ordinal. El orden de las paradas de `summary`
  (recuento descendente y luego propósito, etapa y motivo) coincide con el anterior: SQLite compara UTF-8 por bytes, que
  equivale al orden por punto de código de Python.
- **Autoridad de la exportación.** La vista previa lee la proyección. El envío confirmado, la petición del job y el
  registro de la intención siguen recalculando la instantánea desde el historial y exigen que coincida con la revisada.
  Una proyección que difiera del historial no llega al commit: el envío responde `Conflict` sin encolar nada. Los
  bloques que regenera el commit de tarea, la transición y su vista previa (`summary_snapshot`) no cambian.
- **Límites.** `tasks` y `validations` conservan su paginación; `summary` agrega todo el ámbito, como antes, y limita
  las paradas a `STOP_LIMIT`. El esquema no cambia: la medida (§3) no justifica columnas ni tablas nuevas.

## 3. Medidas

Ámbito sintético de 61 runs de tarea (formato 8) y 35,4 MiB de historiales. Uno de ellos es el historial de 26 MiB de
T003 (40 ciclos, 2.000 casos por ciclo y diff de 4 MiB); los otros 60 tienen 4 ciclos y 200 casos por ciclo, en 30
tareas y 3 fases. Tres ejecuciones en este equipo (macOS arm64). La implementación anterior se mide igual, incluida la
lectura del texto desde SQLite.

| Lectura | Proyección | Anterior |
|---|---|---|
| `summary` del ámbito global | 153–157 ms | 1.177–1.193 ms |
| Página de 20 tareas | 84–86 ms | 532–539 ms |
| `validations` por fase | 256–273 ms | 527–538 ms |
| Hechos de una tarea en la vista previa (run de 26 MiB) | 8,4–8,9 ms | 361–376 ms |

En `validations` domina el recuento por resultado de unos 128.000 casos con `json_extract`. Una columna de resultado
lo abarataría, pero exigiría otra versión de la proyección y su migración; con estas medidas no se justifica. En los
tests, la instrumentación cuenta las llamadas al codec y las sentencias SQL de cada vista: cero decodificaciones y
ninguna sentencia con `history_json`.

## 4. Pruebas

`tests/product/test_metrics_projection.py` (nuevo) compara cada vista con una copia de la implementación anterior:

- Migración `0023` sobre runs previos de los formatos 1 a 8, con varias raíces, fases, tareas y propósitos, tareas con
  varios runs, un último run sin ciclos y un run de chat con paradas. Hay además un run con validaciones límite:
  captura viva, timeout, `error` vacío, códigos `false` y `0.0`, `capture_json` ilegible, reportes `partial`, `missing`
  y sin casos, frescura `unchanged`, un resultado `flaky`, ejecutores sin resumen y un intento en curso. `summary`,
  `tasks` y `validations` son iguales en seis ámbitos y con páginas de 1, 2 y 50. Los hechos por tarea y la aceptación
  de la vista previa coinciden con los del historial, sin decodificar. Una mutación que ignora el tipo del código de
  salida hace fallar el test.
- Un run sin proyección hace fallar `summary`, `validations` y la vista previa con diagnóstico.
- Ámbito grande: lecturas sin historial e iguales a las anteriores (§3).
- Exportación con el motor real, en las formas D036 y v2: la vista previa no decodifica, su instantánea es igual a la
  calculada desde el historial y el envío confirmado llega a COMMITTED. Con un veredicto alterado en la proyección, la
  vista previa lo muestra, pero el envío responde `Conflict` y no encola nada.

Los tests de métricas, documentos y exportación existentes pasan sin cambios.

## 5. Límites y observaciones

- `summary` recorre todas las tareas del ámbito con unas pocas consultas por tarea (N+1 acotado por el número de
  tareas), como antes, pero sin historiales.
- La transición y su vista previa (`summary_snapshot`), el commit de tarea, los checks, el chat y la recuperación
  siguen leyendo el historial: son lecturas del motor (contrato de T001 §2.1).
- La proyección no es autoridad. Si difiere del historial, la vista previa puede mostrar datos distintos, pero el
  envío los rechaza; el backup ya detecta esa diferencia (D144).
- QA visual no realizado: la UI y la API no cambian.

## 6. Comprobaciones ejecutadas

Sobre el árbol de trabajo de esta tarea (base `389a3b1`), el 2026-10-22:

- `pytest -q` completa (xdist): 1649 passed, 2 skipped (variantes reales opt-in de Django y TypeScript), 121 subtests
  passed.
- `test_metrics_projection.py`: 6 passed en serie (`-n 0`); medidas de §3 con `-s`.
- `python3 -m unittest discover`: 12 tests OK.
- `alembic upgrade head` y `alembic check` en una SQLite temporal: sin operaciones nuevas.
- Node, tipos y build no se ejecutan porque no cambian el cliente, OpenAPI ni la API.

No se ejecutaron proveedores, smokes, servicios, el wheel ni descargas. No se tocó la configuración global, la base
operativa ni el hijo Django de P009.

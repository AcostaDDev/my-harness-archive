# P008-T016 — Frontera Git del Flujo A

Fecha: 2026-10-17. Derivada de H1–H3 de la [revisión de salida](P008_REVISION_SALIDA.md).
Decisión: [D105](../DECISIONS.md#d105--p008-t016-frontera-git-y-bytes-confirmados-en-las-importaciones).

## Resultado

El Flujo A aplica las garantías de lectura sin ejecución y bytes exactos de D096/D100 usando las guardias
compartidas con el Flujo B. El inventario ya no alcanza `status` con filtros ejecutables configurados; la vista
previa no admite conversiones de bytes ni destinos nuevos ignorados. El job vuelve a comprobar la frontera antes
de llamar al escritor. La recuperación conserva el mismo run, intención y commit.

## Cambios y motivos

- `adapters/project_import.py`: `check_filters` inspecciona `filter.*.clean`/`process` con `config --includes`
  antes de `status`, sin ejecutar el filtro ni tocar configuración. `_tree` admite una revisión explícita para
  comprobar el árbol sellado. `check_tree` rechaza destinos nuevos ignorados, documentos ausentes/no regulares,
  blobs con SHA-256 diferente del árbol documental confirmado y eliminaciones aún presentes. Abarca todo
  `result_tree`, incluidos documentos no modificados, originales archivados y binarios.
- `storage/project_import.py`: la frontera compartida `check_git` se aplica antes y después de construir la
  vista previa, al recuperar una operación interrumpida y antes del sellado final. Las lecturas conservan
  `--no-lazy-fetch`. La confirmación recalcula la vista y mantiene sus hashes/contexto/versiones y CAS. Los
  fallos durante la transacción de confirmación no guardan run, job ni operación nuevos.
- `storage/onboarding_commit.py`: utiliza la frontera común de su repositorio base. Conserva la ingeniería
  inversa, comprobación de HEAD, borradores privados, perfil confirmado y P001 adoptada.
- `core/engine/import_commit.py`: el sellado final exige el mismo árbol que la vista previa validada. No puede
  crear una intención nueva con un árbol transformado entre ambos sellados.
- `services/managed.py`: todos los jobs `import_commit`, A/B, comprueban filtros, destinos y bytes del árbol
  de la intención antes de ejecutar. Se mantiene el escritor documental con recaptura/recálculo y CAS anteriores;
  una conversión nueva de atributos después de confirmar invalida la operación antes de escribir.
- `document_layout = "d088-9"`: la composición vigente rechaza puertos/escritor para versiones anteriores,
  incluida `d088-8`, antes de efectos. No cambian prompts, adaptador CLI, codec, esquema, API ni TOML. Ninguna
  intención o evidencia histórica se reescribe. Las transiciones antiguas ya selladas conservan su excepción
  documentada de conciliación, cubierta por sus pruebas.
- Flujos A/B, SPECIFICATION y ARCHITECTURE actualizados para estas garantías; STATE/NEXT_STEPS/ROADMAP al día.
  P008-T017 queda definida para los textos pendientes de H4; no se ejecuta ni se cierra la fase en esta tarea.

## Regresiones sintéticas

`tests/product/test_import_git_boundary.py` añade veinte casos:

- Filtros `clean` y `process`, locales y por include: el inventario rechaza antes de `status`/`add`/`hash-object`,
  sin marcador y con checkout/índice intactos. Vista previa y confirmación no llegan a captura/sellado.
- Los cuatro casos de filtro en el job se rechazan antes de invocar al escritor y quedan en recuperación.
  Retirado el filtro y confirmado detenido el escritor, se concilia el mismo run/commit sin cambiar la intención.
- Borrador GEMINI con CRLF y `text eol=lf`, original AGENTS archivado y binario movido: las conversiones bloquean
  vista previa/confirmación sin documentos escritos ni operación/commit/fase nuevos.
- GEMINI nuevo ignorado por `.gitignore`: bloquea vista previa/confirmación con origen, índice y exclusiones
  intactos. Una exclusión local introducida después de confirmar también bloquea antes de escribir.
- Conversión de atributos posterior a la confirmación: INVALIDATED sin escritura. Conversión introducida entre
  vista previa y sellado final: transacción rechazada sin run/job/operación nuevos.
- Caso válido con originales CRLF y binario: COMPLETED/COMMITTED; todos los blobs documentales de HEAD coinciden
  con los SHA-256 confirmados y los originales conservan sus bytes.

Se actualizan las pruebas de versión del contrato y de comandos Git de solo lectura. Los recorridos anteriores
de los tres orígenes A, activación D099, caídas en cinco puntos, continuación de tareas y Django/TypeScript B
siguen en la suite; no se sustituye la evidencia de entregas anteriores.

## Verificación

- `python3 -m unittest discover -s tests -p 'test_*.py'`: 12 checks correctos.
- Primera batería dirigida de inventario, frontera e importación A/B: 73 pruebas correctas. Se lanzó antes de
  añadir los dos casos finales de deriva de atributos/sellado; la suite completa incorpora los veinte nuevos.
- Suite pytest completa: **1.365 pruebas y 121 subtests correctos**, incluidos los veinte casos nuevos. Se
  recogieron los nodeids con `uv run --frozen --offline pytest --collect-only -q`; cuatro lotes de
  `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q <nodeids>` cubren exactamente la colección,
  sin duplicados ni solapamientos. Resultados: 342/341/341/341 OK; subtests 0/5/0/116, todos con exit 0.
  Duraciones pytest: 306,59/311,35/304,62/309,95 segundos. Solo el aviso conocido de Starlette/httpx.
- 33 Markdown activos/raíz/phase con 371 enlaces y anclas válidos; presupuestos de instrucciones, STATE/base y
  NEXT_STEPS correctos. Parsers: 105 decisiones, ocho fases y diecisiete tareas. Los dos flowcharts de
  `legacy-migration.md` pasan la gramática Mermaid local; se omiten DOM/sanitización de etiquetas/renderizado.
  El diagrama de estados existente no cambia. Diff revisado y `git diff --check` correcto.
- Sin Node, tipos/build ni Alembic independiente: no cambia UI, OpenAPI ni esquema. Sin comprobación visual.
- Sin proveedores reales, smokes, push, publicación, registro de este repositorio ni subagentes. Solo puertos
  falsos y repositorios/SQLite temporales; sin datos privados ni configuración global modificada.

## Límites y continuidad

Las guardias son cooperativas y no añaden aislamiento del sistema operativo. No certifican un entorno con
cambios concurrentes arbitrarios de configuración. Los blobs/árboles Git inalcanzables calculados para una vista
previa pueden materializarse, como antes; no se cambian refs ni el índice real durante esas comprobaciones.
Una operación antigua pendiente sigue ligada a sus versiones congeladas: no se actualiza su intención para
sortear la cuarentena. El consentimiento de esta sesión incluye el commit de desarrollo, sin push ni publicación.

Siguiente: T017 (H4), nueva revisión de salida y, solo en una operación posterior, cierre/archivo de P008.

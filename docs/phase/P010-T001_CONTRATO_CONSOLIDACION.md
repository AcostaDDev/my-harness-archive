# P010-T001 — Contrato de las correcciones y criterios de cierre

Fecha: 2026-10-22. Base investigada: `90efab0`. Decisión:
[D142](../DECISIONS.md#d142--p010-t001-receta-typescript-proyección-de-runs-y-tarea-t011).
**Estado: diseño terminado; producto pendiente de T002, T003 y T011.** No implementa código, tablas, API,
configuración ni recetas. Aplica [D141](../DECISIONS.md#d141--p010-consolidación-de-la-primera-versión-local) y
conserva D088, D116–D119 y D129–D130.

## 0. Decisiones del usuario (HITL, 2026-10-22)

La documentación no resolvía cuatro elecciones de diseño. Se plantearon al usuario y eligió:

| Pregunta | Elección |
|---|---|
| Mecanismo del `package.json` inicial | Segunda receta empaquetada en el marco D119, solo para hijos nuevos creados por el servicio. |
| Pasos de la preparación TypeScript | Archivos empaquetados, `npm ci` y validaciones del perfil antes del commit técnico. |
| Estrategia de lectura de runs | Proyección derivada en SQLite, escrita con el historial; `history_json` sigue siendo la autoridad. |
| Alcance frente a SPECIFICATION §9 | T003 se ocupa de las vistas de runs; la nueva P010-T011 mueve métricas y exportación documental. |

Descartadas: escritor ligero de manifiestos (otra vía de escritura protegida con recuperación propia) y
manifiestos dentro de la definición D088 (contradice D116). También la extracción JSON1 sobre `history_json`,
que sigue leyendo el blob entero, y dejar las métricas como límite declarado.

## 1. Arranque de un proyecto `typescript-web` nuevo (T002)

### 1.1 Consumidores inspeccionados

| Consumidor | Hoy | Cambio previsto |
|---|---|---|
| `profiles/typescript_web.py` | Protege `package.json`, `package-lock.json`, `tsconfig.json`, `scripts/**`, `tests/**` y `.gitignore`. Antes de cada tarea ejecuta `node`/`npm --version` y `npm ci --offline --ignore-scripts`. Valida con `npm run check/test/build` y JUnit en `.local/junit.xml`. | Ninguno. La receta usa el perfil integrado sin cambios; el ejecutor normal sigue sin poder escribir esos archivos. |
| `services/local_config.py` (`_composition`, `LocalComposer`, carga de `[recipes]`) | Solo admite `recipe = "django"` con perfil `python-django-recipe`. `install` asocia siempre `recipes['django']`, y `project_recipe` vale siempre `django-recipe-1`. | Tabla de recetas por nombre; `[recipes.typescript-web]` en v5; huella y versión por receta. |
| `services/project_preparation.py` | Todo el servicio está ligado a Django: `require`, preview, `snapshot` (enlaces de `.venv`), `_files`, `_publish`, `_verify_source`, comprobaciones de `_command`, mensaje de commit y recibo. | Separar el núcleo común (CAS, intención, pasos, lease, journal, commit, recuperación) de la parte de cada receta. |
| `adapters/preparation.py` (`environment_snapshot`, `verify_receipt`, `PreparedCommandRunner`) | El recibo exige un entorno `.venv`; los mensajes dicen «prepara Django». | Verificación del recibo por receta; mensajes genéricos. |
| `storage/preparation.py` (`admit`) | La lógica de la reserva y del recibo es genérica; solo el mensaje habla de Django. | Mensaje genérico; la lógica no cambia. |
| `recipes/django.py` | Modelo de receta empaquetada: contenido, perfil, pasos y huella. | Sin cambios; sirve de molde para `recipes/typescript_web.py`. |
| API `Preparation*` (`api/schemas.py`) | `recipe: str`; plan y recibo son diccionarios (`extra='allow'`). | En principio, compatible. Si cambia algún campo, se regeneran OpenAPI y tipos en T002. |
| UI `Preparation.tsx`, `Planning.tsx`, `shared.tsx` | Títulos, botón y avisos «Preparar Django». | Textos según la receta del proyecto; la misma vista previa, confirmación y journal. |
| Definición D088 y `render_agents` | `AGENTS.md` lista la preparación y las validaciones del perfil. | Ninguno. |
| `tests/fixtures/typescript_web` | Proyecto sintético verificado offline, con lock de `typescript@5.9.3` e integridad sha512. | Base del contenido empaquetado. No se reutiliza como fixture escribible. |

### 1.2 Configuración y composición

- `local-config-5` admite `[recipes.typescript-web]`, con `node_executable`, `node_version` y `npm_executable`,
  `npm_version` (versiones exactas), además de `npm_cache`, `timeout_seconds` (120–1800), `max_output_bytes` y
  `allow_network`. `npm_cache` es un directorio absoluto existente, fuera de los checkouts y del estado del servicio.
  Ejecutables absolutos y sin shells, con las mismas reglas que `[recipes.django]`.
- `[recipes.django]`, sus hashes y las composiciones sin receta no cambian. V1–v4 siguen rechazando `[recipes]`.
  El formato sigue siendo `local-config-5`: los archivos v5 existentes siguen siendo válidos y conservan su hash.
- Una composición con `recipe = "typescript-web"` exige el perfil integrado `typescript-web`. Sus ejecutables `node`
  y `npm` deben resolver a los mismos archivos que la receta, y su entorno debe declarar `npm_config_cache` igual a
  `npm_cache`. Así cada tarea reinstala con la misma caché que acreditó la preparación. No se reescribe el entorno.
- Versiones congeladas: `project_recipe = "typescript-web-recipe-1"` y `recipe_config_sha256` sobre la configuración y
  la huella del módulo (contenido, perfil e implementación), como en D119. Un cambio deja en cuarentena los jobs previos.

### 1.3 Quién puede preparar y qué se escribe

La elegibilidad es la de D119: hijo registrado por el servicio (`creation_id`), definición D088 con commit raíz
aceptado, HEAD igual a ese commit, índice limpio, árbol con solo los documentos aceptados y ningún archivo ajeno,
tampoco ignorado. Los destinos deben estar ausentes y no ignorados por Git. Los proyectos dados de alta o
importados (A/B) no son elegibles: conservan su comportamiento y aportan su propio manifiesto.

Contenido empaquetado, íntegro en la vista previa con hash y diff:

- `package.json`: nombre derivado del id del proyecto (el patrón del id cabe en el de npm), `private`, `"type": "module"`,
  `engines` con las versiones exactas de la receta, scripts `check`/`test`/`build` del fixture y
  `devDependencies.typescript = "5.9.3"`.
- `package-lock.json` v3 con la misma entrada `typescript@5.9.3` (`resolved` e `integrity`) que el fixture; solo varían
  el nombre y `engines` de la raíz. Cambiar la versión de TypeScript requiere una decisión nueva.
- `tsconfig.json`, `scripts/test.mjs` (`node --test` con JUnit en `.local/junit.xml`), `scripts/build.mjs`,
  `index.html`, un módulo mínimo en `src/` y su test en `tests/`. La primera tarea parte de algo que valida.
- `.gitignore` con `node_modules/`, `.build/`, `dist/`, `.local/`, `.harness-preparation/`, `.env` y `.env.*`.

### 1.4 Pasos, red y recibo

1. `files`: crea `.harness-preparation/{home,tmp}` y escribe el manifiesto. No hay generador, así que no hay paso `publish`.
2. `node --version` debe dar `v<node_version>`; `npm --version`, `<npm_version>`.
3. `npm ci --ignore-scripts --no-audit --no-fund`, con `--offline` en modo offline. `HOME` y `TMPDIR` quedan dentro de
   `.harness-preparation/`. Se fijan `npm_config_cache`, `npm_config_engine_strict=true`, registro
   `https://registry.npmjs.org/`, `fetch-retries=0` y una configuración de usuario vacía dentro del hijo, para no
   descubrir configuración ajena.
4. `npm run check`, `npm run test` (el JUnit debe ser completo y tener casos correctos) y `npm run build`.
5. `commit`: «harness: prepare TypeScript web (typescript-web-recipe-1)». Contiene exactamente el manifiesto,
   y `node_modules/`, `.build/`, `dist/` y `.local/` quedan locales e ignorados.

El modo offline usa solo la caché declarada: un fallo no cambia a red. El modo network exige `allow_network` y que
se elija en la vista previa. La vista previa muestra el registro y avisa de que la red escribe en la caché del
operador. Confirmar los documentos no concede instalar ni conectarse (D116).

Recibo: contrato, receta, identidad, `recipe_config_sha256`, configuración, hash del lock, commit, operación,
ejecutables `node`/`npm` resueltos con su hash y los archivos del manifiesto que coinciden con `protected_paths`
del perfil, comparados con la misma semántica glob que el perfil. No congela `node_modules`: la preparación del
perfil lo reinstala en cada tarea. `PreparedCommandRunner` y `admit` verifican identidad, archivos y ejecutables
antes de las tareas, los checks y cada comando.

### 1.5 Recuperación y compatibilidad

- Mismo contrato `project-preparation-1`, mismo binding `preparation-commands-1` y mismas tablas de
  operación/paso/evento, locks y procesos. El sobre común del plan conserva sus claves. La parte específica la
  identifica `recipe`. Los planes y recibos Django ya persistidos se leen y recuperan como hoy.
- Reglas D119 sin excepciones: intención y lock antes de efectos; la consulta no ejecuta herramientas; nada se
  repite automáticamente; una intención nueva enlazada confirma el primer paso no acreditado. Un `npm ci` fallido
  solo se reintenta si `node_modules/` sigue igual que en el último prefijo acreditado (normalmente, ausente). Si
  quedan bytes parciales o deriva, la operación pasa a `RECOVERY_REQUIRED` y requiere resolución externa, sin borrar.
  Si las pruebas de T002 muestran que un fallo offline corriente deja bytes que impiden reintentar, se consulta al
  usuario antes de relajar esta regla.
- El commit técnico es determinista y se concilia tras una caída, como en Django. Un destino existente o una deriva
  bloquean con diagnóstico y no se adoptan.
- Sin migración ni tablas nuevas; DDBB-DIAGRAM no cambia. `docs/flows/project-preparation.md` pasa a cubrir ambas
  recetas en T002. Backup, restauración y retención ya reconocen estas tablas.
- Límite heredado de D119: el recibo fija el manifiesto. Añadir dependencias después requiere un flujo confirmado
  futuro (fuera de P010) y T006 lo documenta. El perfil también protege `tests/**` frente al ejecutor (P007); T002
  no cambia esa protección y T007 la registra como observación.

### 1.6 Pruebas previstas en T002

Con herramientas falsas y caché sintética: recorrido desde la creación hasta la definición, la preparación y la
primera tarea con `npm ci` y validaciones; reenvío idempotente; caídas en cada paso y antes y después del commit;
caché vacía en modo offline; red sin techo; destino existente o ignorado; deriva del manifiesto antes de una tarea;
proyecto no elegible; Django sin cambios (hashes de plan, recibo y composición); v1–v4; y la UI con ambas recetas.

## 2. Lecturas de runs sin decodificar el historial (T003 y T011)

### 2.1 Inventario

Cada run guarda su historial completo en `managed_runs.history_json`, un único JSON con codec de formatos 1 a 8.
Solo lo escriben `_queue_new_run` (inserción) y `_history` (actualización en solo-añadir) de `storage/managed.py`.

| Lectura | Hoy | Clase | Tarea |
|---|---|---|---|
| `GET /runs/{id}` (`views.run`) | Decodifica el historial entero y calcula las acciones. Lo sondean `pages/Run.tsx`, `Docs.tsx` (1,5 s), `ChatCommand.tsx` (2 s) y `workspace.tsx`. | Vista | T003 |
| `GET /runs/{id}/cycles/{c}/diff` | Decodifica todo para servir una página del diff. | Vista | T003 |
| `GET …/validations/{e}/reports/{r}` y `/original` | Decodifican todo para servir casos JUnit o el original. | Vista | T003 |
| `GET /projects/{id}/runs`, `GET …/phases/{code}/tasks` | Paginados, pero `select(Run)` carga el texto `history_json` de cada fila. En tareas de fase, de todos los runs de la fase. | Vista | T003 |
| `exists`, `jobs`, `attempts`, `events`, `permissions` (lista), `logs` | Ya acotados, aunque `session.get(Run)` carga el texto del historial. | Vista | T003 (carga diferida) |
| Métricas: `summary`, `tasks`, `validations` | Decodifican todos los historiales del ámbito. | Vista | T011 |
| `GET /phases/{id}/export` (`document_export`, `state_snapshot`) | Decodifica el último run de cada tarea. | Vista | T011 |
| `_history`, reanudar, commit y recuperación (`managed.py`, `workflow`) | Decodifican para validar el solo-añadir y continuar. | Motor | Sin cambio |
| Fases: liquidación, evidencia del check, propuestas de ADR, lote | Leen el último ciclo y los intentos al ejecutar jobs. | Motor | Sin cambio |
| Chat y planificación: `settle`, `_run_evidence` (POST) | Congelan evidencia al crear o liquidar un turno. | Motor | Sin cambio |
| `state_snapshot` al hacer commit o transición | Regenera los bloques de STATE. | Motor | Sin cambio |
| Permisos (`binding`, `allowed`, `create`) | Leen `task_json` al decidir. | Motor | Sin cambio |
| Integridad del backup y `export_state` legacy | Leen todos los historiales. | Backup | Sin cambio, más comprobación de la proyección |

Las lecturas del motor pueden seguir decodificando: no pintan vistas y su coste va ligado a un efecto.

### 2.2 Proyección `run-projection-1`

- Tablas derivadas de cada run, con FK a `managed_runs`: resumen (estado del historial, contrato de tarea,
  marcadores para las acciones: intentos del ejecutor, rutas permitidas no vacías, aceptación y su elegibilidad,
  parada actual), paradas ordenadas y ciclos. Cada ciclo lleva veredicto, huella, rutas, hash y tamaño del diff,
  procedencia, revisión, formateo y resumen de validación sin casos. El diff va en una tabla aparte, que admite
  lectura por rangos. Hay además entradas de validación, reportes JUnit (resumen y original) y casos con su ordinal.
  T003 fija nombres y columnas con paridad en DDBB-DIAGRAM.
- Se escribe en la misma transacción que `history_json`, desde los dos únicos escritores. Es incremental: añade
  ciclos, paradas e intentos nuevos y actualiza la revisión del último ciclo, el único cambio que `_history` admite.
  Guarda `history_sha256` del texto del que se derivó.
- Migración aditiva `0023` (o la siguiente libre): crea las tablas y las rellena decodificando una vez cada historial
  existente con `load_history`, así que cubre los formatos 1 a 8. No modifica `history_json`; T003 lo acredita por hash.
  El downgrade elimina solo tablas derivadas. Se aplica con el backup previo de siempre y sin migrar la instalación
  real en esta fase.
- Las vistas no seleccionan `history_json`: usan carga diferida u otras columnas y la proyección. Tampoco llaman a
  `load_history`. Los límites son explícitos: ciclos paginados o con tope declarado en el detalle, diff por bytes desde
  la tabla de diffs (E/S incremental de blob o fragmentos, según la medición de T003), casos por ordinal. El orden
  sigue siendo estable: runs por `created_at desc, id`, ciclos por número, entradas, reportes y casos por índice, y
  eventos por secuencia.
- La respuesta del detalle conserva su forma salvo la paginación de ciclos. Cualquier cambio regenera OpenAPI y
  tipos y actualiza el cliente en la misma tarea. El hash del diff y su 409 se mantienen.
- Consistencia: el backup recalcula la proyección desde cada historial y la compara. Si difiere, falla con
  diagnóstico. La restauración sigue siendo de consulta y nunca reconstruye. La cuarentena no cambia, porque las
  versiones congeladas no incluyen la proyección. La retención no toca historiales.
- Acreditación: un historial sintético grande (muchos ciclos, diffs de varios MiB y JUnit con miles de casos) demuestra
  cero llamadas a `load_history` y ninguna consulta de vista que seleccione `history_json`. Para ello se
  instrumentan el codec y las sentencias SQL. Los resultados deben ser iguales a los de la implementación anterior
  y debe haber casos de los formatos 1 a 8 y de una migración sobre datos previos.

T011 reutiliza la proyección. Métricas (`summary`, `tasks`, `validations`) y la vista previa de exportación pasan a
agregaciones SQL sobre resumen, ciclos, validaciones, paradas y `managed_attempts`, con paginación explícita. Sin
tablas nuevas salvo que su medición lo justifique, en cuyo caso se documenta en su entrega.

## 3. Almacenamiento, formatos y versiones

| Elemento | T002 | T003/T011 |
|---|---|---|
| Esquema SQLite | Sin cambios (`0022`). | Migración aditiva y tablas derivadas; DDBB-DIAGRAM en T003. |
| Codec del historial (formato 8) y snapshots | Sin cambios. | Sin cambios; `history_json` se conserva byte a byte. |
| `cli-13`, `commands-1`, `preparation-commands-1`, `d088-12` | Sin cambios. | Sin cambios. |
| Configuración | `local-config-5` con nueva clave de receta; v1–v4 y v5 previos con el mismo hash. | Sin cambios. |
| Contratos de preparación | `project-preparation-1` con `recipe = typescript-web-recipe-1`; Django intacto. | — |
| Backup y restauración | Mismas tablas. | Tablas nuevas en el backup y comprobación de consistencia. Restaurar exige la misma revisión de esquema (regla vigente). |
| API y tipos | Solo si cambia la forma del plan. | Paginación de ciclos y nuevas lecturas, con OpenAPI y tipos regenerados. |

No se elige ninguna tecnología nueva ni se cambia el requisito no funcional.

## 4. Matriz inicial de aceptación (SPECIFICATION §10)

Evidencia localizada por lectura de código, tests y decisiones a partir de `90efab0`. **En T001 no se ha
reejecutado nada**: la columna «Vigencia» indica qué debe comprobar T007. «Real» remite a operaciones con
proveedores ya archivadas; no se amplía su alcance.

| # | Criterio (resumen) | Evidencia offline localizada | Real | Vigencia y huecos |
|---|---|---|---|---|
| 1 | Importar dos veces un historial no duplica ni inventa | `test_legacy_import.py` (`…read_only_and_idempotent`, `…absent_null_and_observed_zero…`) | No | Reejecutar. Se refiere a la importación legacy; A/B tienen otros tests (criterio 11). |
| 2 | Ejecución → fallo de test → corrección → revisión → commit | `test_e2e_offline.py::test_import_execute_block_revalidate_commit`, `test_engine.py` (revisiones), `test_managed_api.py::test_http_flow_…restart` | D050, D071, D139 | Reejecutar. La evidencia real es histórica (cli-9 a cli-13). |
| 3 | Sin dos escritores por checkout, ni tras reiniciar con proceso vivo | `test_managed.py` (`…double_requests…`, `…writer_lock`), `test_cli_agents.py` (`…live_owner…`, `…crash_restart_retains_group_lock…`) | No | Reejecutar. Contención cooperativa, sin aislamiento del sistema operativo. |
| 4 | Una denegación no ejecuta; aprobación caducada o doble no se reutiliza | `test_permissions.py` (`…denial_prevents_executor_call…`, `…expiry…`, `…never_reuses_once_grant`, `…concurrent_grant_and_deny…`) | No | Reejecutar. |
| 5 | Reinicio sin efectos a ciegas; caída tras el commit conciliada | `test_managed.py::…survive_restart`, `test_e2e_offline.py::test_quarantine_survives_restart…`, `test_git.py::test_crash_around_the_git_effect…` | No localizada | Reejecutar. D130 acredita el recibo tras reiniciar, no un reinicio con una ejecución en curso. |
| 6 | Editar prompts no cambia el intento pasado | `test_prompts.py` (`…keeps_snapshot…`, `…pins_catalog…`) | No | Reejecutar. |
| 7 | Un cambio tras el diff revisado invalida la aceptación | `test_engine.py::test_content_change_during_review_invalidates_acceptance`, `test_git.py::test_content_changed_between_intent_and_effect_never_commits` | No | Reejecutar. |
| 8 | Cierre con validación y autorización vigentes y archivo sin pérdida | `test_phase_closure.py` | D139 (cierre de P001 del hijo) | Reejecutar. T005 cambia la presentación, no el check. |
| 9 | Otro perfil sin cambiar el núcleo | `test_engine.py::test_reference_project_rules_are_in_declarative_profile_not_core`, `test_declared_profiles.py`, `test_typescript_profile.py` | Receta Django (D139) | El perfil declarativo de D095 no se ha confirmado en un proyecto real (T008). |
| 10 | Una petición del chat queda ligada a una tarea y su resultado | `test_chat.py::test_confirmed_proposal_becomes_a_linked_task…`, `…http_chat_flow…` | No localizada | Reejecutar. Falta evidencia real; T008 decide si se busca o se declara. |
| 11 | Proyecto vacío con primera tarea ejecutable; importación sin perder historial | `test_bootstrap.py`, `test_e2e_offline.py::test_create_confirm_restart_then_first_task_and_commit`, `test_import_commit.py`, `test_django_journey.py` | Creación Django (D127/D139); A/B no | **Hueco**: `typescript-web` nuevo sin `package.json` hasta T002. A/B solo con evidencia sintética (T008). |
| 12 | Backup y restauración con estados, referencias y hashes | `test_backup.py` | No | Reejecutar tras T003: tablas nuevas y comprobación de consistencia. |
| 13 | Salida fuera de esquema; ciclos sin cambios; SSE sin huecos ni duplicados | `test_engine.py` (`…invalid_review_is_retained…`, `…no_progress_loop_stops…`), `test_cli_agents.py`, `test_typed_json_schema.py`, `test_legacy_observation.py` (SSE) | No | **Cuestión**: el SSE solo existe en la observación legacy; la UI gestionada sondea eventos por cursor (D029). Ver §5. |

El requisito de §9 sobre lecturas acotadas no está en §10, pero lo cubren T003 y T011 y T007 lo añade como fila propia.

## 5. Cuestiones abiertas, sin bloqueo para T002–T005

- **SSE gestionado (§10.13).** D029 eligió sondeo con cursor y dejó pendiente el SSE gestionado. T007 debe plantear
  al usuario si el cursor sin huecos ni duplicados cumple el criterio en la UI gestionada o si hace falta una tarea
  nueva. No se decide aquí.
- **Manifiesto fijo tras preparar** (TypeScript y Django) y **`tests/**` protegido** en `typescript-web`: límites que
  T006 documenta. Cambiarlos requiere una decisión propia.
- **Evidencia real** del chat, de A/B y del perfil D095: T008 propone; nada se ejecuta sin consentimiento nuevo.
- El resto de criterios no presenta bloqueos de diseño. La nueva **P010-T011** entra en NEXT_STEPS con dependencia de
  T003 y antes de T006.

## 6. Comprobación de este contrato

- Contraste estático con `profiles/typescript_web.py`, `services/local_config.py`, `services/project_preparation.py`,
  `adapters/preparation.py`, `storage/preparation.py`, `recipes/django.py`, `storage/managed_views.py`,
  `storage/managed.py`, `storage/metrics.py`, `storage/documents.py`, `storage/document_export.py`,
  `storage/backup.py`, `api/managed.py`, `api/schemas.py` y las páginas `Run`, `Docs`, `ChatCommand` y `Preparation`.
- Decisiones contrastadas: D029, D088, D095, D116–D119, D129, D130 y D141. Enlaces relativos y anclas de este
  documento revisados.
- No se ejecutan unittest, pytest, Node, tipos/build, Alembic ni el wheel: esta tarea solo diseña. No hay cambios de
  código, esquema, API, flujos, configuración, instalaciones, servicios, agentes ni proveedores.

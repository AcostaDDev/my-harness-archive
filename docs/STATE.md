# Estado — my_harness

Actualizado: 2026-10-16. Sin bloques gestionados mientras el repositorio no esté registrado en el harness (D088).

## Base acumulada

Lo que existe y funciona, verificado offline con Git, SQLite y procesos temporales, agentes falsos y datos sintéticos
salvo donde se indica. Detalle por fase en `docs/archive/phase-NNN/SUMMARY.md`.

- **Núcleo y motor** ([P001](archive/phase-001/SUMMARY.md), [P003](archive/phase-003/SUMMARY.md)): paquete
  `harness_local` con contexto explícito por proyecto, contrato de tarea congelado, planificación determinista o por el
  revisor, bucle ejecución → validación → revisión con límite de correcciones, aceptación ligada al contenido exacto y
  commit determinista conciliable. Codec de historial en formato 7 (lee 1–6).
- **Persistencia y recuperación** ([P003](archive/phase-003/SUMMARY.md), [P006](archive/phase-006/SUMMARY.md)): SQLite
  `0019_import_conversations` (34 tablas, [diagrama](DDBB-DIAGRAM.md)); cola idempotente, lease, lock por checkout,
  cuarentena por versión y confirmación explícita del escritor detenido; backup y restauración de consulta; retención
  explícita de streams.
- **Agentes** ([P007](archive/phase-007/SUMMARY.md)): revisor y ejecutor Codex o Claude en cualquier combinación
  (`cli-11`, `local-config-2/3/4`), revisor en solo lectura con esquema tipado, memoria automática desactivada,
  supresión de confianza del escritor Codex. Validaciones nativas `commands-1` con JUnit. Perfiles: `typescript-web`
  (componible desde el TOML), `reference_project` (solo biblioteca) y perfiles declarados en `[profiles.*]` de
  `local-config-4`, con el ejemplo `python-django` (P008-T008).
- **Fases y documentos** ([P004](archive/phase-004/SUMMARY.md), [P007](archive/phase-007/SUMMARY.md)): check READY,
  reconciliación, preguntas, lote desatendido, enmiendas, abandono y cierre con tag. Contrato documental unificado y
  obligatorio de D088 desde P008-T002 (layout v2 modificado; DECISIONS único con índice): bloques regenerados en cada
  commit, edición confirmada, exportación y cierre unificado que archiva en `archive/phase-NNN/` (P008-T004, D091).
- **Creación y chat** ([P005](archive/phase-005/SUMMARY.md), [P007](archive/phase-007/SUMMARY.md)): creación por
  conversación con borradores en disco y CAS (la v1 se rechaza desde P008-T002); planificación de fase conversacional; chat
  sobre una instantánea de HEAD sin lock, con comandos deterministas y propuestas que crean tareas confirmadas.
- **API y UI** ([P007](archive/phase-007/SUMMARY.md)): `/api/managed` con sesión local, Host/Origin y CSRF; UI por URL
  (registro, proyecto, documentación, creación, fases, tareas, runs con diff paginado, chat, estadísticas); métricas por
  intento con procedencia; observación legacy en `/legacy`.
- **Operación** ([P006](archive/phase-006/SUMMARY.md)): wheel con UI y migraciones, `init-db`, `serve`,
  `check-config`, `metrics-backfill`, `diagnose-cli`; `scripts/dev` para desarrollo.
- **Evidencia con proveedores reales** (consentimientos agotados): transporte de las tres CLI (D025), primer uso real
  COMMITTED con fase cerrada (D050) y cuatro combinaciones revisor/ejecutor COMMITTED (D071).
- **Límites**: ningún recorrido de producto completo con CLI reales; contención cooperativa sin aislamiento del sistema
  operativo; validaciones sin hora; historial del run decodificado completo en cada lectura; `package.json` de un
  `typescript-web` nuevo; dos avisos *low* de KaTeX.

## Fase activa — P008 Contrato documental unificado, cierre de fase e importación de proyectos

Objetivo y criterios en [ROADMAP](ROADMAP.md); plan en [NEXT_STEPS](NEXT_STEPS.md); decisión de base D088.

**P008-T001 completada** (migración documental de este repositorio, sin cambios del motor):

- `docs/discovery/` eliminado; su contenido está en `docs/archive/phase-000…007/` con NEXT_STEPS, STATE y SUMMARY por
  fase y REVIEW donde hubo revisión de cierre. Registro e incongruencias del motor en
  [docs/phase](phase/P008-T001_MIGRACION_DOCUMENTAL.md).
- Nuevos SPECIFICATION, ARCHITECTURE, ROADMAP, DDBB-DIAGRAM y `docs/flows/` (seis flujos); DECISIONS con índice y
  D088; AGENTS (45 líneas), CLAUDE (8), GEMINI (5) y README (79).
- Código: solo la ruta de `baseline.json` (ahora en `tests/fixtures/legacy/`) en `tests/test_legacy_fixtures.py` y dos
  docstrings.
- Verificación: 12 checks ligeros; pytest 1120 pruebas y 121 subtests (un aviso de deprecación de Starlette sobre
  `httpx`, ajeno a esta tarea); 72 pruebas Node; ningún enlace relativo roto en los Markdown del repositorio; 16
  diagramas Mermaid válidos con el parser de `mermaid` 11.17.2; `parse_roadmap` (P001–P008) y `plan_tasks` (15 tareas)
  del motor aceptan ROADMAP y NEXT_STEPS; los 18 documentos activos pasan el parser de bloques; STATE 4,5 KiB (base
  3,2 KiB) y NEXT_STEPS 22 KiB dentro de presupuesto. No se ejecutaron `alembic check` ni el build del frontend: no
  cambian modelos, migraciones ni UI.

**P008-T002 completada** (layout unificado obligatorio y plantilla, [D089](DECISIONS.md#d089--p008-t002-layout-unificado-obligatorio-y-plantilla)):

- `Layout` con AGENTS, CLAUDE, GEMINI, DDBB-DIAGRAM, `flows/` y `phase/`, sin `decisions/`, `architecture/` ni
  `research/`; `skeleton()` genera exactamente la lista de D088 (AGENTS ≤60 líneas con los comandos del perfil,
  CLAUDE/GEMINI ≤15).
- Índice de DECISIONS desde sus encabezados `## DNNN — título` y la primera línea `Estado:`; numeración repetida
  rechazada en commit de tarea, edición, transición y aceptación de la definición; sin presupuesto de 8 KiB. La
  reconciliación puede añadir decisiones a la prosa de DECISIONS.
- La configuración compone siempre `documents = "v2"` y congela `document_layout = "d088-1"` (jobs anteriores en
  cuarentena). Creación v1 y descubrimiento rechazados con diagnóstico; plantilla `project-foundation` y
  `examples/bootstrap_demo.py` eliminados. `protected_write` exime AGENTS/CLAUDE/GEMINI para la creación.
- Verificación: 12 checks ligeros; pytest 1112 pruebas y 121 subtests (la suite completa dio 1111 OK y 1 fallo de
  `test_document_viewer`, ruta antigua en la prueba, corregida y re-ejecutada en su archivo: 7 OK); `alembic check`
  sobre una base temporal; 16
  diagramas Mermaid válidos con el parser local; el DECISIONS de este repositorio indexa 89 decisiones sin duplicados.
  No se ejecutaron pruebas Node ni el build: no cambian UI ni OpenAPI.
- En esta entrega quedaban prompts, cierre, API y UI; cierre resuelto en T004 y prompts en T005. API/UI e inyección
  de instrucciones siguen pendientes de T006/T007.

**P008-T003 completada** (rutas protegidas, paridad y propuestas de ADR,
[D090](DECISIONS.md#d090--p008-t003-rutas-del-ejecutor-paridad-de-diagramas-y-propuestas-de-adr)):

- `typescript-web` protege STATE, NEXT_STEPS, ROADMAP, DECISIONS, `docs/archive/**`, AGENTS, CLAUDE y GEMINI en lugar
  de `docs/**`; `harness_owned_paths` prohíbe además siempre AGENTS, CLAUDE y GEMINI. `executor_protected` deja a la
  reconciliación editar la prosa de los cuatro documentos de control aunque el perfil los proteja. AGENTS, CLAUDE y
  GEMINI son editables por edición confirmada. `reference_project` conserva `docs/**`.
- `ProjectProfile.data_model_paths`: con layout v2, un diff que toca modelos sin `DDBB-DIAGRAM.md` no es aceptable
  (motivo determinista en `assess_acceptance`, también al preparar el commit). `review-task` nuevo recibe
  `documentation` y exige los flujos.
- `decision_proposals` (≤5, `title`/`decision`/`rationale`) en la salida del ejecutor y del revisor; mal formadas
  detienen el run; se guardan con el intento y la revisión y llegan a la evidencia de la reconciliación sin escribir
  DECISIONS. Adaptador `cli-10` y `document_layout = "d088-2"` (jobs pendientes anteriores en cuarentena).
- Verificación: 12 checks ligeros; pytest 1122 pruebas y 121 subtests (un aviso de Starlette ajeno); tras dos
  retoques posteriores (validación de propuestas al revalidar, ajuste de línea) se re-ejecutaron los archivos
  afectados: 144 OK, incluidas 11 pruebas nuevas en `test_documentation_parity.py`. Enlaces relativos y anclas de los
  Markdown editados correctos; el diagrama de secuencia modificado de `flows/task-run.md` pasa el parser Mermaid
  local. Sin `alembic check`, pruebas Node ni build: no cambian modelos, migraciones, UI ni OpenAPI.

**P008-T004 completada** (cierre y archivo unificados,
[D091](DECISIONS.md#d091--p008-t004-cierre-y-archivo-unificados-con-planificación-posterior)):

- Cierre autorizado con tag sobre el HEAD evaluado y un commit de archivo conciliable: STATE/NEXT_STEPS por bytes,
  REVIEW/SUMMARY desde SQLite y todo `docs/phase/`, incluidos binarios. STATE fresco con base, NEXT_STEPS con
  objetivo/criterios de N+1 sin tareas, ROADMAP con enlace al archivo y sucesora ACTIVE adoptada atómicamente.
- Abandono por la misma vía sin READY ni tag; rechazo previo de deriva, checkout sucio, archivo existente o trabajo
  pendiente. Check bloqueado por STATE >24 KiB o base >12 KiB. Nuevas transiciones H6.3 retiradas, conservando la
  conciliación de sus intenciones selladas. `document_layout = "d088-3"`.
- Plan posterior confirmado desde texto o `phase_planning`: commit documental y nueva versión de la definición;
  endpoints mínimos y contratos generados actualizados. Prompts adaptados en T005; UI pendiente de T006.
- Verificación: 12 checks ligeros; pytest completo con 1.142 OK y 121 subtests, dos fixtures históricos de métricas
  corregidos y su archivo re-ejecutado (27 OK); 113 pruebas afectadas tras los ajustes finales, incluidos los 22 casos
  nuevos de cierre. 72 pruebas Node y build (incluye tipos) correctos. Dos diagramas Mermaid y enlaces/anclas de los
  siete Markdown editados/nuevos válidos. Sin `alembic check` independiente (no cambian modelos ni migraciones),
  proveedores reales ni smokes. Detalle en [registro](phase/P008-T004_CIERRE_UNIFICADO.md).

**P008-T005 completada** (prompts y definición unificados,
[D092](DECISIONS.md#d092--p008-t005-prompts-y-definición-bajo-el-contrato-unificado)):

- Siete prompts nuevos por hash, incluida la corrección `revise-task`: discovery de AGENTS, DECISIONS único,
  DDBB-DIAGRAM, flujos, artefactos de fase y propuestas de ADR; la reconciliación puede consolidarlas bajo su contrato.
- Definición versión 4: once documentos obligatorios al aceptar, con el completado por plantilla de D089 y sus valores
  congelados en el turno. Se conservan instrucciones personalizadas; AGENTS >60 líneas o CLAUDE/GEMINI >15 bloquean.
- Planificación sobre la fase ACTIVE vacía y confirmación propia del plan. Contexto con instrucciones y diagrama de
  datos. `document_layout = "d088-4"`: jobs anteriores en cuarentena; recuperación de transiciones ya selladas sin
  reescribir run ni intención. Sin cambios de modelo, migración, dependencias o esquema de salida.
- Verificación: 12 checks ligeros; pytest completo con 1.158 pruebas y 121 subtests correctos (aviso conocido de
  Starlette/httpx); primera pasada dirigida con 179 OK. Quince Markdown con enlaces/anclas válidos, tres diagramas
  Mermaid válidos y diff revisado. Sin Node/build ni `alembic check` independiente: no cambian UI, OpenAPI ni esquema.
  Sin proveedores reales ni smokes. Detalle en el [registro](phase/P008-T005_PROMPTS_DEFINICION.md).

**P008-T006 completada** (API y UI mínimas,
[D093](DECISIONS.md#d093--p008-t006-api-y-ui-del-contrato-unificado)):

- API con clases de instrucciones, diagrama de datos, flujos y trabajo de fase; instrucciones raíz en el árbol y el
  estado sin cambiar la base adoptada. Índice de decisiones con id, título y estado desde DECISIONS, enlazado a sus
  encabezados en el visor. OpenAPI y tipos regenerados.
- Retirados los endpoints de creación v1 y transición, sus esquemas de entrada y Bootstrap.tsx. El GET de estado
  conserva solo la definición conversacional. Las intenciones históricas siguen en el motor; no se reescriben.
- UI de cierre y abandono explica el archivo unificado; el plan posterior se confirma por texto o propuesta en la
  fase ACTIVE vacía, con diff, hash, motivo y clave idempotente. El registro usa siempre el contrato unificado.
- Verificación: 12 checks ligeros, 73 pruebas Node y build correctos; pytest completo con 1.163 OK y 121 subtests
  y un fallo de comparación de OpenAPI al regenerarlo durante la suite. Re-ejecutado el archivo de contratos en un
  proceso nuevo: 10 OK, incluida la igualdad con OpenAPI. Ocho Markdown, 235 enlaces/anclas y tres diagramas válidos.
  Sin `alembic check` independiente, comprobación visual, proveedores reales ni smokes. Detalle en el
  [registro](phase/P008-T006_API_UI.md).

**P008-T007 completada** (instrucciones del proyecto en el contexto congelado,
[D094](DECISIONS.md#d094--p008-t007-agentsmd-en-el-prompt-congelado-de-cada-rol)):

- Verificado sin ejecutar CLI (fuente del pin de Codex y documentación de Claude): el escritor Codex `untrusted` no
  carga `AGENTS.md`; el lector sí, desde el checkout vivo. Claude con `--setting-sources ""` no carga `CLAUDE.md`.
- El motor lee `AGENTS.md` en cada intento: regular, sin enlaces, UTF-8, no vacío y de 32 KiB como máximo. Lo inyecta
  con `{{PROJECT_INSTRUCTIONS}}` en todos los roles salvo la definición, con ruta, hash y tamaño en el snapshot. Sin
  él, el intento para en `prompts` antes de invocar. Las plantillas anteriores se siguen leyendo, pero no invocan.
- `cli-11` añade `project_doc_max_bytes=0` en Codex, de modo que el único `AGENTS.md` es el congelado.
  `document_layout = "d088-5"`: los jobs anteriores quedan en cuarentena.
- Verificación: 12 checks ligeros. Pytest completo: 1.192 OK y 121 subtests (aviso conocido de Starlette/httpx), con
  28 casos nuevos en `test_project_instructions.py`. Una primera pasada dio 17 fallos de fixtures v2 sin
  `AGENTS.md` (`web` de TypeScript y una prueba HTTP de fases), que se corrigieron antes de la pasada final. Hay 242
  enlaces y anclas válidos y DECISIONS indexa 94 decisiones. El diagrama de secuencia editado pasa el parser Mermaid
  local; el de estados, sin cambios, no se pudo comprobar sin DOM. Sin Node/build ni `alembic check`, porque no
  cambian UI, OpenAPI ni esquema. Sin proveedores reales ni smokes. Detalle en el
  [registro](phase/P008-T007_INSTRUCCIONES_CONTEXTO.md).

**P008-T008 completada** (perfiles declarativos en el TOML local,
[D095](DECISIONS.md#d095--p008-t008-perfiles-declarados-en-local-config-4)):

- `local-config-4` = `local-config-3` + `[profiles.<nombre>]`: preparación y validaciones como argv sin shell (JUnit
  junto a su validación), prefijos, rutas protegidas y sensibles, `data_model_paths` e instrucciones del ejecutor,
  todo explícito y con claves desconocidas rechazadas. Las composiciones nombran un perfil integrado o declarado.
- En v4 el contenido del perfil entra en `local_config_sha256` (cambiarlo pone en cuarentena los jobs pendientes);
  v1–v3 conservan comportamiento y hash. `check-config` muestra cada perfil declarado con su hash y sus argv.
- Ejemplo `python-django` en `examples/local_config.example.toml` (pytest con JUnit, ruff, mypy, `manage.py check` y
  `makemigrations --check`), pendiente de que el usuario lo confirme sobre su proyecto.
- Verificación: 12 checks ligeros. Pytest completo: 1.218 OK y 121 subtests, con 1 fallo de la prueba que fijaba el
  ejemplo a v3; se actualizó y se re-ejecutaron los tres archivos afectados (74 OK), incluidos 27 casos nuevos con un
  recorrido Django sintético hasta COMMITTED. 241 enlaces y anclas válidos. Sin Node/build ni `alembic check` (no
  cambian UI, OpenAPI ni esquema), sin proveedores reales, smokes ni herramientas Python reales. Los textos de
  ayuda, registro y UI que citan `local-config-3` quedan pendientes, fuera de las rutas de la tarea
  ([registro](phase/P008-T008_PERFILES_DECLARATIVOS.md)).

**P008-T009 completada** (Flujo A: inventario de solo lectura,
[D096](DECISIONS.md#d096--p008-t009-inventario-de-importación-desde-el-árbol-de-head)):

- `core/project_import.py` (reglas puras) y `adapters/project_import.py` (`read_inventory(context)`): lee el árbol de
  HEAD de un checkout limpio con Git de solo lectura (`rev-parse`, `status`, `ls-tree`, `cat-file --batch`, sin
  hooks, fsmonitor ni filtros). Rechaza sin Git, sin commits, con HEAD vacío o con cambios o archivos sin seguimiento.
  Lo ignorado no se lee; enlaces y submódulos son entradas rechazadas que bloquean; `.harness/runs` solo se cuenta.
- Ámbito: Markdown de la raíz, `docs/` y `.harness/` sin runs. Cada entrada con ruta, tamaño, SHA-256, clase
  (`canonical`, `renameable`, `mergeable`, `historical`, `foreign`), regla y canónico inequívoco; alias y renumeración
  del archivo nunca ocupan un destino existente o compartido. Origen por señales (ReferenceProject, v1, v2, `mixed`,
  `unified`, `unknown`), fases de ROADMAP/STATE/NEXT_STEPS/archivo sin reconciliar, tamaño de AGENTS/CLAUDE/GEMINI,
  bloques gestionados y huella `inventory_sha256` sin raíz ni commit.
- Sin persistencia, API ni UI (T011 congelará el inventario); sin modelos, migraciones, dependencias ni prompts.
- Verificación: 12 checks ligeros. Pytest completo: 1.233 OK y 121 subtests (aviso conocido de Starlette/httpx),
  con 14 casos nuevos en `test_project_import.py`: tres orígenes sintéticos con su clasificación completa, relectura
  idéntica sin cambios en el árbol ni en `.git`, huella sin raíz ni commit, solo Git de lectura, rechazos y enlaces.
  252 enlaces y anclas válidos y los tres diagramas de `flows/legacy-migration.md` pasan el parser Mermaid local.
  Sin Node/build ni `alembic check` (no cambian UI, OpenAPI ni esquema), sin proveedores reales ni smokes. Detalle
  en el [registro](phase/P008-T009_INVENTARIO_FLUJO_A.md).

**P008-T010 completada** (Flujo A: mapa de normalización determinista,
[D097](DECISIONS.md#d097--p008-t010-mapa-de-normalización-del-flujo-a)):

- `core/project_normalization.py`: `build_map(inventory, contents)` puro, con los bytes comprobados contra la huella
  y los SHA-256 del inventario, y `materialize` para obtener los bytes del árbol resultante. Formato
  `harness-local/import-map/1` y huella `map_sha256`.
- Reglas con identificador: alias hacia el canónico (`DECISSONS.md` → `DECISIONS.md`), `data-model` →
  DDBB-DIAGRAM, `phase-N` → `phase-NNN`, BRIEF/PROJECT_PROFILE v1 y README de las carpetas v2 a
  `archive/phase-000/`, artefactos de fase (`research/**` y `docs/PNNN*`) a `docs/phase/` o al archivo de su fase,
  y `decisions/DNNN-*.md` inequívocos compuestos en DECISIONS por número con su original en `phase-000`.
- Movimientos byte a byte; ningún destino coincide, ni en mayúsculas ni como directorio, con una ruta existente u
  otro destino (`target-conflict`). Lo ambiguo queda en `review` con su motivo para T011, lo ajeno en `foreign`, y
  `missing` lista los documentos de D088 que faltan. Sin adaptador, persistencia, API ni UI.
- Verificación: 12 checks ligeros. Pytest completo: 1.246 OK y 121 subtests (aviso conocido de Starlette/httpx), con
  13 casos nuevos en `test_project_normalization.py`; tras esa pasada se simplificó la detección de conflictos y se
  re-ejecutaron las pruebas de inventario y mapa (27 OK). 307 enlaces y anclas válidos en los documentos activos y
  los dos flowcharts de `flows/legacy-migration.md` pasan el parser de flujo de `mermaid` local (el de estados no
  cambia). Sin Node/build ni `alembic check` (no cambian UI, OpenAPI ni esquema), sin proveedores reales ni smokes.
  Detalle en el [registro](phase/P008-T010_MAPA_NORMALIZACION.md).

**P008-T011 completada** (Flujo A: propuesta del revisor,
[D098](DECISIONS.md#d098--p008-t011-conversación-de-importación-con-borradores-privados)):

- Conversación `project_import` sobre H6.5: inventario y mapa congelados al crearla (`planning_conversations.source`,
  migración `0019`), solo para proyectos sin creación ni fases. Cada turno exige la misma huella del checkout y
  congela los textos del árbol resultante (archivo solo por ruta y hash) y los borradores, como máximo 2 MiB.
- Revisor de solo lectura con el rol y el esquema `definition` y la plantilla `import-project` (adaptador `cli-11`,
  sin `AGENTS.md` inyectado). Rutas admitidas: plantilla D088 y `flows/*.md`; lo demás, FAILED sin fallback. Un
  cambio del checkout o del área durante el turno descarta la respuesta.
- Borradores en `import-drafts/<id>/` junto a SQLite (0700) con la CAS de la definición; el checkout no se escribe.
  `GET …/planning/{c}/import` da los bloqueos de la vista previa: preguntas bloqueantes sin responder ni aplazar,
  checkout cambiado, documentos de D088 ausentes, límites de AGENTS/CLAUDE/GEMINI, borradores inválidos.
- Extensiones técnicas: observación en `services/managed.py`, OpenAPI y tipos regenerados y etiqueta «Importación»
  del nuevo `purpose` en dos archivos de la UI. Límite: con runs legacy sin activar, la guardia D027 rechaza los
  turnos; el orden lo fija [D099](DECISIONS.md#d099--flujo-a-activación-d027-antes-de-la-importación) (activación primero), que se implementa en T012.
- Verificación: 12 checks ligeros. Pytest completo: 1.264 OK y 121 subtests (aviso conocido de Starlette/httpx),
  con 17 casos nuevos en `test_import_conversation.py`; tras un retoque de imports se re-ejecutaron cuatro archivos
  afectados (113 OK). `alembic check` sobre una base temporal, 73 pruebas Node, `tsc` y build correctos. 264 enlaces y
  anclas válidos y los dos flowcharts de `flows/legacy-migration.md` pasan el parser local. Sin proveedores reales ni
  smokes. Detalle en el [registro](phase/P008-T011_PROPUESTA_REVISOR.md).

**Siguiente:** P008-T012 (Flujo A: vista previa, commit y continuidad), sin iniciar. Este repositorio sigue sin
registrarse en el harness.

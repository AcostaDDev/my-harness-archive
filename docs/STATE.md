# Estado — my_harness

Actualizado: 2026-10-17. Sin bloques gestionados mientras el repositorio no esté registrado en el harness (D088).

## Base acumulada

Lo que existe y funciona, verificado offline con Git, SQLite y procesos temporales, agentes falsos y datos sintéticos
salvo donde se indica. Detalle por fase en `docs/archive/phase-NNN/SUMMARY.md`.

- **Núcleo y motor** ([P001](archive/phase-001/SUMMARY.md), [P003](archive/phase-003/SUMMARY.md)): paquete
  `harness_local` con contexto explícito por proyecto, contrato de tarea congelado, planificación determinista o por el
  revisor, bucle ejecución → validación → revisión con límite de correcciones, aceptación ligada al contenido exacto y
  commit determinista conciliable. Codec de historial en formato 7 (lee 1–6).
- **Persistencia y recuperación** ([P003](archive/phase-003/SUMMARY.md), [P006](archive/phase-006/SUMMARY.md)): SQLite
  `0020_project_imports` (35 tablas, [diagrama](DDBB-DIAGRAM.md)); cola idempotente, lease, lock por checkout,
  cuarentena por versión y confirmación explícita del escritor detenido; backup y restauración de consulta; retención
  explícita de streams.
- **Agentes** ([P007](archive/phase-007/SUMMARY.md)): revisor y ejecutor Codex o Claude en cualquier combinación
  (`cli-12`, `local-config-2/3/4`), revisor en solo lectura con esquema tipado, memoria automática desactivada,
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

- Archivo por fases P000–P007, seis flujos y documentos D088; retirada de discovery. Código: ruta del fixture legacy
  y dos docstrings. 12 checks, pytest 1.120 +121 subtests, 72 Node, enlaces y diagramas correctos; sin Alembic/build.
  Detalle e incongruencias en el [registro](phase/P008-T001_MIGRACION_DOCUMENTAL.md).

**P008-T002 completada** (layout y plantilla obligatorios,
[D089](DECISIONS.md#d089--p008-t002-layout-unificado-obligatorio-y-plantilla)):

- Layout D088 y DECISIONS único con índice, duplicados rechazados y sin presupuesto de 8 KiB. Instrucciones raíz
  con límites de líneas; creación v1 y discovery rechazados. `documents = "v2"`, `document_layout = "d088-1"`;
  jobs anteriores en cuarentena. Cierre, prompts, API/UI e instrucciones resueltos después en T004–T007.
- 12 checks, pytest 1.112 +121 subtests y Alembic temporal correctos; enlaces y diagramas válidos. Sin Node/build.

**P008-T003 completada** ([D090](DECISIONS.md#d090--p008-t003-rutas-del-ejecutor-paridad-de-diagramas-y-propuestas-de-adr)):

- `typescript-web` reserva instrucciones y documentos de control; SPECIFICATION, ARCHITECTURE, diagramas,
  flujos y trabajo de fase admitidos bajo contrato. `reference_project` conserva `docs/**`. Paridad de modelos y propuestas de ADR
  del ejecutor/revisor conservadas para reconciliación; `cli-10`, `document_layout = "d088-2"`.
- Verificación de entrega: 12 checks ligeros, pytest 1.122 +121 subtests, enlaces y diagrama válidos. Sin esquema/UI.
  Detalle duradero en D090; la revisión de salida posterior figura en D104.

**P008-T004 completada** ([D091](DECISIONS.md#d091--p008-t004-cierre-y-archivo-unificados-con-planificación-posterior)):

- Cierre READY y abandono por archivo unificado, commit conciliable, originales/binarios por bytes, STATE/NEXT_STEPS
  frescos y sucesora ACTIVE sin tareas; plan posterior confirmado y definido por versión. Límites de STATE/base y
  rechazo previo de deriva, suciedad, archivo ocupado o trabajo pendiente. `document_layout = "d088-3"`.
- Verificación de entrega: 12 checks, pytest 1.142 +121 subtests; fixtures de métricas revalidados (27 OK),
  72 Node, tipos/build y enlaces/diagramas correctos. Sin esquema ni proveedores reales.
  Detalle en el [registro](phase/P008-T004_CIERRE_UNIFICADO.md).

**P008-T005 completada** ([D092](DECISIONS.md#d092--p008-t005-prompts-y-definición-bajo-el-contrato-unificado)):

- Siete prompts nuevos por hash, incluida la corrección; definición v4 con once documentos obligatorios y defaults
  congelados de D089. Instrucciones personalizadas conservadas, límites de líneas y planificación sobre la fase
  ACTIVE vacía. `document_layout = "d088-4"`; conciliación de transiciones selladas sin reescribirlas.
- Verificación de entrega: 12 checks, pytest 1.158 +121 subtests, enlaces y tres diagramas válidos. Sin cambios de
  esquema/UI ni proveedores reales. Detalle en el [registro](phase/P008-T005_PROMPTS_DEFINICION.md).

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

**P008-T012 completada** (Flujo A: vista previa, commit y continuidad,
[D100](DECISIONS.md#d100--p008-t012-importación-confirmada-y-continuidad-del-flujo-a)):

- Árbol completo del mapa y borradores privados; originales sustituidos o retirados conservados por bytes en
  `archive/phase-000/import-originals/`, sin sobrescribir archivo previo. STATE/NEXT_STEPS deben coincidir en una
  fase de ROADMAP con objetivo y criterios; bloques regenerados y fase ACTIVE adoptada con sus documentos.
- `0020_project_imports`: intención sellada antes del efecto, confirmación por hash/motivo/clave y un commit
  «docs: normalizar al contrato documental». Caídas conciliables con el mismo run y commit; resultado, fase y fin
  del job atómicos. Intención incierta bloquea trabajo nuevo y reversión; borradores cerrados al confirmar.
- D099 implementada: activación antes de conversar si hay runs legacy; solo el marcador propio ACTIVE y validado
  se tolera y excluye de Git, también al continuar. Ningún `.gitignore` cambia. Grafías exactas en macOS y binarios
  por bytes. API, UI de importación y tipos generados; `document_layout = "d088-6"`.
- Verificación: 12 checks ligeros; suite pytest con 1.281 OK y 121 subtests, y dos fallos en el recorrido legacy
  por excluir un marcador ya ignorado. Corregidos y revalidados en 79 pruebas de Git/API/importación; cinco casos
  de recuperación re-ejecutados tras limpiar la parada antigua al conciliar. 74 pruebas Node, tipos, build y
  `alembic check` temporal correctos. Ocho Markdown con 276 enlaces/anclas válidos, siete ER y dos flowcharts
  válidos por parser/gramática; diff revisado. Sin comprobación visual, proveedores ni smokes reales. Detalle y
  límites en el [registro](phase/P008-T012_COMMIT_CONTINUIDAD.md).

**P008-T013 completada** (Flujo B,
[D101](DECISIONS.md#d101--p008-t013-inventario-estático-del-flujo-b-y-propuesta-de-perfil)):

- Inventario puro de HEAD: stack, entidades/relaciones, rutas locales, tests y CI con fuentes y hashes. Git de
  lectura sin filtros ni ejecutar el proyecto; límites y diagnósticos explícitos. Dinamismo sin resolver.
- Propuesta `local-config-4` con argv/cwd y evidencia, pendiente de confirmar; sin escribir TOML. Sin API, UI o
  persistencia; conversación/commit pendientes de T014/T015. [Registro](phase/P008-T013_INVENTARIO_FLUJO_B.md).
- Verificación: 12 checks; pytest 1.303 y 121 subtests; 20 casos finales, 284 enlaces/anclas y un diagrama válidos.
  Sin pruebas frontend ni Alembic independiente (sin UI/esquema), proveedores reales ni smokes.

**P008-T014 completada** (Flujo B: ingeniería inversa del revisor,
[D102](DECISIONS.md#d102--p008-t014-ingeniería-inversa-sobre-head-y-borradores-privados)):

- Conversación `onboarding` con inventario y HEAD congelados; revisor de solo lectura sobre exportación privada
  de ese commit. Propone documentos D088, diagrama desde modelos, flujos y decisiones inferidas; pregunta las
  incógnitas. Borradores privados con CAS, sin escribir checkout/README ni activar el perfil.
- Observación antes/después, respuesta inválida FAILED sin fallback y limpieza al terminar o confirmar detenido
  tras caída. `cli-12`, `document_layout = "d088-7"`, OpenAPI/tipos y etiquetas actualizados; sin cambio de esquema.
  UI específica, vista previa/commit y confirmación del perfil pendientes de T015.
- Verificación: pytest 1.322 OK y 121 subtests; recuento antiguo corregido y 29 prompts OK. 12 checks, 74 Node,
  build y Alembic correctos; [registro](phase/P008-T014_INGENIERIA_INVERSA.md).

**P008-T015 completada** (Flujo B: vista previa, commit y control del harness,
[D103](DECISIONS.md#d103--p008-t015-incorporación-confirmada-del-flujo-b)):

- Vista previa de documentos y perfil de la composición, ambos confirmados por hash. P001 ACTIVE adoptada con
  su base documental. Inventario y resumen en `archive/phase-000/`; originales sustituidos conservados por bytes.
- Reutiliza la intención, cola, recuperación y registro atómico de `project_imports` (0020); sin cambios de esquema.
  UI de incorporación y borradores privados; OpenAPI/tipos regenerados. `document_layout = "d088-8"`.
- Sin escribir TOML, ejecutar herramientas del proyecto ni modificar código durante la incorporación. Los filtros
  Git ejecutables y las transformaciones de bytes impiden la vista previa.
- Verificación: pytest 1.345 y 121 subtests, 12 checks ligeros, 75 Node, build y Alembic temporal correctos;
  enlaces y diagramas válidos. Sin UI visual, proveedores reales ni smokes. [Registro](phase/P008-T015_INCORPORACION_CONFIRMADA.md).

**Revisión de salida completada el 2026-10-17** ([D104](DECISIONS.md#d104--revisión-de-salida-de-p008-con-hallazgos-en-el-flujo-a)):

- Sobre `f650851`, tres fallos del Flujo A reproducidos con repositorios temporales y agentes falsos: el inventario
  ejecuta filtros locales; una conversión CRLF/LF acaba COMMITTED con bytes distintos de los confirmados; un destino
  ignorado se admite y deja documentos escritos con importación INTERRUPTED, sin commit. Las guardias del Flujo B
  ya cubren esos casos. También se detectaron ayudas y estados documentales desactualizados.
- Dictamen: P008 sigue activa y no está lista para cerrar. No cambia el código del producto ni se reescriben las ADR,
  snapshots o intenciones previas. Reproducciones, criterio por criterio y verificación en el
  [registro](phase/P008_REVISION_SALIDA.md).
- Verificación y límites en el registro: pytest, checks ligeros, Node, tipos/build, Alembic temporal y paridad
  documental correctos. Sin UI visual ni proveedores reales.

**P008-T016 completada** ([D105](DECISIONS.md#d105--p008-t016-frontera-git-y-bytes-confirmados-en-las-importaciones)):

- Frontera Git A/B compartida: filtros `clean`/`process` (incluidos includes) rechazados antes de `status`,
  captura/sellado y ejecución/reanudación. Destinos nuevos ignorados bloqueados antes de confirmar o escribir.
- Todos los blobs documentales coinciden con sus SHA-256 confirmados, incluidos originales archivados y binarios;
  el sellado final reproduce el árbol de la vista previa. CAS, D099 y conciliación del mismo commit conservadas.
  `document_layout = "d088-9"` pone en cuarentena composiciones anteriores; no se reescriben intenciones.
- Verificación: 1.365 pytest y 121 subtests, 12 checks ligeros, 371 enlaces/anclas y dos flowcharts correctos;
  diff revisado. [Registro](phase/P008-T016_FRONTERA_GIT.md). Sin Node/build/Alembic independiente (sin cambios
  de esquema/API/UI), proveedores reales ni smokes.

**P008-T017 completada** ([D106](DECISIONS.md#d106--p008-t017-referencias-vigentes-sin-cambiar-contratos)):

- F11/F18, arquitectura y ayudas CLI/registro/UI alineadas con lo implementado; Prompts distingue creación v1
  retirada, reconciliación y check previo al cierre. Solo textos, sin contratos ni históricos modificados.
- Verificación: 12 checks ligeros, 52 pytest dirigidas, 75 Node y tipos/build correctos; ayuda CLI comprobada.
  Detalle y límites en el [registro](phase/P008-T017_REFERENCIAS_VIGENTES.md).

**Siguiente:** nueva revisión de salida de P008 tras T016/T017; cierre y archivo separados. P008 sigue activa
y este repositorio sin registrarse en el harness.

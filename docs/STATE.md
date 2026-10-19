# Estado — my_harness

Actualizado: 2026-10-19. Sin bloques gestionados mientras el repositorio no esté registrado en el harness (D088).

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
- Verificación: 12 checks, 73 Node y build correctos; pytest 1.163 OK y 121 subtests, con un fallo OpenAPI al
  regenerarlo durante la suite, revalidado en un proceso nuevo (10 OK). Enlaces/diagramas válidos; sin Alembic
  independiente, UI visual ni proveedores/smokes reales. Detalle en el [registro](phase/P008-T006_API_UI.md).

**P008-T007 completada** (instrucciones del proyecto en el contexto congelado,
[D094](DECISIONS.md#d094--p008-t007-agentsmd-en-el-prompt-congelado-de-cada-rol)):

- El motor congela `AGENTS.md` regular, sin enlaces, UTF-8, no vacío y ≤32 KiB, con ruta, hash y tamaño; lo inyecta
  por `{{PROJECT_INSTRUCTIONS}}` salvo en definición. Su ausencia detiene antes de invocar. Fuente del pin de Codex
  y documentación de Claude verificadas sin CLI; `cli-11` desactiva carga automática de Codex con
  `project_doc_max_bytes=0`; Claude conserva `--setting-sources ""`. `d088-5` pone jobs anteriores en cuarentena.
- Verificación: 12 checks; pytest 1.192 OK y 121 subtests, incluidos 28 casos nuevos, tras corregir fixtures v2 sin
  AGENTS. Enlaces y secuencia Mermaid válidos; estados sin DOM no comprobados. Sin Node/build/Alembic ni
  proveedores/smokes reales. Evidencia y límites en el [registro](phase/P008-T007_INSTRUCCIONES_CONTEXTO.md).

**P008-T008 completada** ([D095](DECISIONS.md#d095--p008-t008-perfiles-declarados-en-local-config-4)):

- `local-config-4` añade `[profiles.<nombre>]` con argv sin shell, JUnit, prefijos, rutas y paridad de modelos;
  claves desconocidas rechazadas. Perfiles integrados o declarados en composiciones; contenido en el hash
  congelado v4 (v1–v3 conservados), `check-config` con hash y argv. Ejemplo `python-django` pendiente de confirmar
  sobre un proyecto real; recorrido Django sintético hasta COMMITTED cubierto.
- Verificación: 12 checks, pytest 1.218 y 121 subtests, con un fallo de expectativa del ejemplo v3 corregido y
  74 pruebas afectadas revalidadas; 241 enlaces correctos. Sin Node/build/Alembic ni herramientas/proveedores
  reales. Ayudas desactualizadas resueltas después en T017. [Registro](phase/P008-T008_PERFILES_DECLARATIVOS.md).

**P008-T009 completada** (Flujo A: inventario de solo lectura,
[D096](DECISIONS.md#d096--p008-t009-inventario-de-importación-desde-el-árbol-de-head)):

- Inventario documental determinista de HEAD limpio: rutas, bytes/hashes, clases/reglas, origen, fases,
  instrucciones, bloques y runs legacy por lstat; sin persistencia ni escrituras. Frontera Git reforzada
  después en T016/T018/T019; filtros, objetos locales y submódulos comprobados antes de efectos.
- Verificación de entrega: 12 checks, 1.233 pytest y 121 subtests; 14 casos nuevos, enlaces/diagramas válidos.
  Detalle y límites en el [registro](phase/P008-T009_INVENTARIO_FLUJO_A.md).

**P008-T010 completada** (Flujo A: mapa de normalización determinista,
[D097](DECISIONS.md#d097--p008-t010-mapa-de-normalización-del-flujo-a)):

- Mapa puro `harness-local/import-map/1` con huella y bytes comprobados: alias, renumeración, composición de
  decisiones y archivo por reglas. Movimientos byte a byte, conflictos sin sobrescritura, ambigüedades en
  `review`, ajenos en `foreign` y documentos ausentes en `missing`. Sin persistencia ni efectos.
- Verificación de entrega: 12 checks, 1.246 pytest y 121 subtests; 13 casos nuevos y 27 pruebas revalidadas,
  enlaces/diagramas válidos. Detalle y límites en el [registro](phase/P008-T010_MAPA_NORMALIZACION.md).

**P008-T011 completada** (Flujo A: propuesta del revisor,
[D098](DECISIONS.md#d098--p008-t011-conversación-de-importación-con-borradores-privados)):

- Conversación `project_import`: inventario/mapa congelados (`0019`), revisor de solo lectura `definition`
  con `import-project`, borradores privados con CAS y origen/área observados antes/después. Rutas D088/flows;
  inválidos FAILED sin fallback. Vista de bloqueos por preguntas, deriva, documentos ausentes y límites.
- Sin escribir checkout; activación legacy primero, decidida en D099 e implementada en T012. API/tipos y
  etiqueta de importación actualizados. Detalle y límites en el [registro](phase/P008-T011_PROPUESTA_REVISOR.md).
- Verificación de entrega: 12 checks, 1.264 pytest y 121 subtests, 113 casos revalidados; Alembic temporal,
  73 Node, tipos/build, 264 enlaces y dos flowcharts correctos. Sin proveedores ni smokes reales.

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
- Verificación de entrega y correcciones legacy/recuperación en el [registro](phase/P008-T012_COMMIT_CONTINUIDAD.md):
  12 checks, 1.281 pytest y 121 subtests, 79 casos revalidados, 74 Node, tipos/build y Alembic temporal;
  enlaces/diagramas correctos. Sin comprobación visual, proveedores ni smokes reales.

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

- Sobre `f650851`, H1–H3 reproducen filtros ejecutados, bytes transformados y escritura con destino ignorado
  en A; H4 detecta referencias desactualizadas. P008 no lista para cerrar. Sin cambios del producto.
  Evidencia, checks offline y límites en el [registro](phase/P008_REVISION_SALIDA.md); intactos.

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

**Segunda revisión de salida completada el 2026-10-17**
([D107](DECISIONS.md#d107--segunda-revisión-de-salida-de-p008), [registro](phase/P008_REVISION_SALIDA_2.md)):

- Sobre `a455ff9`, H1–H3 se rechazan sin efectos en reproducciones independientes y H4 concuerda con el código.
  Corregidas dos referencias residuales en la prosa de los flujos de documentos/creación; sin cambios del producto.
- H5 reproduce ejecución de `upload-pack` por lazy-fetch con un blob prometido ausente en A; B no lo ejecuta.
  P008 no está lista para cerrar. Verificación: 1.365 pytest y 121 subtests, 12 checks, 75 Node, build y Alembic
  temporal correctos. Evidencia y límites en el registro; sin proveedores/smokes reales ni comprobación visual.

**P008-T018 completada** ([D108](DECISIONS.md#d108--p008-t018-lecturas-de-importación-sin-lazy-fetch)):

- `LocalGit` compartido exige `--no-lazy-fetch` desde el primer comando A/B. Objetos o tamaños ausentes y
  respuestas de blobs incompletas bloquean con diagnóstico, sin transporte, objetos recuperados ni inventarios
  parciales; conversación, turnos, estado, vista previa y confirmación A heredan la misma frontera.
- `document_layout = "d088-10"` pone en cuarentena jobs anteriores; sin reescribir intenciones ni la evidencia de H5.
  Filtros, bytes exactos, D099, CAS y conciliación conservados. [Registro](phase/P008-T018_OBJETOS_LOCALES.md).
- Verificación: 12 checks; suite de 1.383 casos y 121 subtests, cuatro fallos iniciales corregidos y 128 pruebas
  revalidadas; 403 enlaces y cinco flowcharts válidos. Sin proveedores ni smokes reales.

**Tercera revisión de salida completada el 2026-10-17**
([D109](DECISIONS.md#d109--tercera-revisión-de-salida-de-p008), [registro](phase/P008_REVISION_SALIDA_3.md)):

- Sobre `0348b84`, H1–H5 resueltos; H6 reproduce filtros de submódulos desde `status` en A, dentro/fuera de
  `docs/`, directos/por include; B no los invoca. P008 no lista para cerrar. Corregido después en T019.
- 1.383 pytest y 121 subtests, 12 checks, 75 Node, tipos/build, Alembic temporal, OpenAPI, 413 enlaces y
  20 diagramas correctos. Evidencia y límites intactos en el registro; sin cambios del producto.

**P008-T019 completada** ([D110](DECISIONS.md#d110--p008-t019-gitlinks-rechazados-antes-de-inspeccionar-el-checkout)):

- Gitlinks en HEAD o índice rechazados antes de `status` en A y de captura/sellado/escritura/recuperación A/B,
  dentro o fuera de `docs/`. Solo lee el padre, sin filtros hijos ni configuración modificada; mantiene limpieza,
  D099, CAS y conciliación del mismo commit. `document_layout = "d088-11"` pone jobs anteriores en cuarentena.
- 27 regresiones nuevas; 1.410 pytest y 121 subtests cubiertos, con una expectativa antigua corregida y 14 casos
  revalidados; 12 checks, 425 enlaces y cinco flowcharts correctos. [Registro](phase/P008-T019_SUBMODULOS.md).
  Sin cambios de esquema/API/UI, Node/build/Alembic independiente ni proveedores o smokes reales.

**Cuarta revisión de salida completada el 2026-10-19**
([D111](DECISIONS.md#d111--cuarta-revisión-de-salida-de-p008), [registro](phase/P008_REVISION_SALIDA_4.md)):

- Sobre `2815b5c`, H1–H6 resueltos en sus comprobaciones; 18 escenarios nuevos H6 rechazan sin filtros ni
  cambios de bytes. H7 ejecuta `upload-pack` desde el escritor A/B al consultar el commit sellado aún ausente,
  incluso con todos los objetos del origen disponibles. Reproducido en ejecución y reanudación: COMPLETED
  con el mismo commit, pero con transporte falso invocado. P008 no lista para cerrar; T020 pendiente.
- 1.410 pytest y 121 subtests, 12 checks, 75 Node, tipos/build, Alembic temporal y OpenAPI correctos;
  35 tablas/377 columnas, 434 enlaces y 20 diagramas válidos. Script/JSON nuevos; sin cambiar producto ni evidencia previa,
  proveedores reales o smokes. Verificación documental y límites en el registro.

**P008-T020 completada** ([D112](DECISIONS.md#d112--p008-t020-escritor-de-importaciones-con-objetos-locales)):

- El escritor A/B usa `LocalGit` en captura/sellado, ejecución, conciliación e índice; `run`/`code` exigen
  `--no-lazy-fetch`, también al recuperar con un puerto nuevo. El commit futuro ausente se crea localmente;
  los objetos necesarios de HEAD/árbol sellado, incluidos blobs ajenos a documentos, bloquean si faltan.
- Git sin soporte falla también en consultas booleanas, sin fallback ni configuración modificada.
  `document_layout = "d088-12"` pone jobs anteriores en cuarentena; misma intención/run/commit y D099 conservados.
- Verificación: 12 checks, 1.436 pytest y 121 subtests, 442 enlaces y cinco flowcharts correctos; diff revisado.
  Detalle y límites en el [registro](phase/P008-T020_ESCRITOR_LOCAL.md). Sin esquema/API/UI ni proveedores reales.

**Quinta revisión de salida completada el 2026-10-19**
([D113](DECISIONS.md#d113--quinta-revisión-de-salida-de-p008), [registro](phase/P008_REVISION_SALIDA_5.md)):

- Sobre `7568215`, H1–H7 resueltos en las comprobaciones; sin nuevos bloqueos. A/B crean el commit futuro y
  recuperan la misma intención con puertos nuevos, sin transportes. Objetos necesarios ausentes y Git sin
  soporte bloquean sin efectos; restituir los bytes sintéticos permite completar la intención original.
- Siete criterios de ROADMAP cumplidos offline: 1.436 pytest y 121 subtests, 12 checks, 75 Node, tipos/build,
  Alembic temporal, OpenAPI, paridad de datos y enlaces/diagramas correctos. Script/JSON nuevos;
  evidencia previa intacta. P008 preparada para su cierre documental separado; límites en el registro.

**Siguiente:** cierre y archivo documental de P008 en una tarea separada, sin inventar fase sucesora.
P008 sigue activa y este repositorio sin registrarse ni ejecutar un check READY del producto sobre él.

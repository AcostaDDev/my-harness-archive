# P008 — Contrato documental unificado, cierre de fase e importación de proyectos

Objetivo y criterios de salida en [ROADMAP](ROADMAP.md#p008--contrato-documental-unificado-cierre-de-fase-e-importación-de-proyectos).
Decisión de base: [D088](DECISIONS.md#d088--contrato-documental-unificado-cierre-de-fase-automático-e-importación-de-proyectos-p008).
Análisis de incongruencias que originó la fase: [docs/phase](phase/P008-T001_MIGRACION_DOCUMENTAL.md).

**Siguiente:** repetir la revisión de salida de P008 tras corregir H6 en T019.
T001–T019 completadas. Tercera revisión de salida completada el 2026-10-17
([D109](DECISIONS.md#d109--tercera-revisión-de-salida-de-p008), [registro](phase/P008_REVISION_SALIDA_3.md)):
H1–H5 resueltos en sus comprobaciones; H6 ejecutaba un filtro del submódulo desde `status` antes de la conversación.
T019 lo corrige el 2026-10-19 ([D110](DECISIONS.md#d110--p008-t019-gitlinks-rechazados-antes-de-inspeccionar-el-checkout),
[registro](phase/P008-T019_SUBMODULOS.md)): gitlinks de HEAD/índice rechazados antes de inspeccionar hijos.
Las evidencias históricas de las dos revisiones anteriores permanecen intactas.
P008 sigue activa; después de T019 se repetirá la revisión de salida. Cierre y archivo son operaciones separadas.
No se ha ejecutado un check READY del producto ni registrado este repositorio. No se inventa una fase sucesora.

## Restricciones compartidas

- Desarrollo manual: no se ejecuta el harness sobre este repositorio ni se lanzan agentes o proveedores reales sin una
  propuesta y un consentimiento específicos.
- Verificación offline con Git y SQLite temporales, agentes y procesos falsos y datos sintéticos. Ningún run ni dato
  privado en fixtures; ReferenceProject solo se lee.
- Los historiales, contratos y snapshots congelados no se reescriben. Cambiar argv, prompts, codec o configuración
  congelada exige versión nueva y deja en cuarentena los jobs pendientes antes de efectos.
- Ninguna dependencia nueva sin decisión registrada. La UI solo cambia lo necesario para no romper referencias.
- Paridad: un cambio de modelos o migraciones actualiza `docs/DDBB-DIAGRAM.md`; un cambio de flujo, `docs/flows/`.
- Al cerrar cada tarea: checks pertinentes, STATE y NEXT_STEPS actualizados, decisiones nuevas en DECISIONS y
  artefactos de trabajo en `docs/phase/`.

## P008-T001 — Migración documental de este repositorio

**Objetivo:** Dejar my_harness bajo la estructura de D088 sin tocar la lógica del motor.
**Estado:** completada el 2026-10-15 (ver [registro](phase/P008-T001_MIGRACION_DOCUMENTAL.md)).
**Rutas permitidas:** `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `README.md`, `docs/**`, `tests/fixtures/legacy/**`,
`tests/test_legacy_fixtures.py`
**Criterios de aceptación:**
- `docs/discovery/` eliminado; su contenido en `docs/archive/phase-000…007/`, con los `*_SCOPE.md` fusionados en el
  NEXT_STEPS archivado de su fase y el STATE acumulado repartido sin perder líneas.
- Documentos activos de D088 presentes; AGENTS ≤60 líneas, CLAUDE y GEMINI ≤15, README ≈100.
- Ningún enlace relativo roto y todos los diagramas Mermaid válidos.
- Checks offline en verde con `baseline.json` en `tests/fixtures/legacy/`.
**Comandos de validación:**
- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
**Referencias:** D088, `docs/archive/phase-007/DOCUMENT_ORGANIZATION.md`

## P008-T002 — Layout unificado obligatorio y plantilla

**Objetivo:** Sustituir el layout v2 opcional por la estructura de D088, obligatoria para todo proyecto gestionado.
**Estado:** completada el 2026-10-15 ([D089](DECISIONS.md#d089--p008-t002-layout-unificado-obligatorio-y-plantilla)).
Adelantos mínimos de otras tareas, registrados en D089: `protected_write` exime AGENTS/CLAUDE/GEMINI para la creación
(T003), la reconciliación puede editar la prosa de DECISIONS y los borradores de definición admiten `docs/flows/*.md`
(T005). La API conserva la forma del índice hasta T006.
**Alcance:**
- `Layout`: añadir `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `docs/DDBB-DIAGRAM.md`, `docs/flows/` y `docs/phase/`;
  retirar `decisions/`, `architecture/` y `research/`. `archive(code)` conserva `phase-NNN`.
- `DECISIONS.md` único: el bloque `managed-decisions` indexa los encabezados `## DNNN — título` del propio archivo
  (id, título, estado de la primera línea `Estado:`); sin presupuesto de 8 KiB. El resto de presupuestos se mantienen.
- `skeleton()`: AGENTS (≤60 líneas: discovery, reglas inquebrantables y comandos del perfil), CLAUDE y GEMINI (≤15,
  `@AGENTS.md` más notas del proveedor), README, SPECIFICATION, ARCHITECTURE, ROADMAP, STATE, NEXT_STEPS, DECISIONS y
  DDBB-DIAGRAM con «Sin persistencia». `flows/` y `phase/` sin archivo de plantilla.
- Contrato obligatorio: un contexto sin la clave `documents` usa el layout unificado. Contextos y runs congelados con
  la forma anterior se siguen leyendo; los jobs pendientes afectados entran en cuarentena.
- Retirar la creación v1 (H4.2: formulario, plantilla `project-foundation` y descubrimiento de un turno) en el
  backend con un rechazo explícito; la lectura de proyectos v1 queda para el Flujo A.
**Rutas permitidas:** `src/harness_local/core/engine/**`, `src/harness_local/storage/**`, `src/harness_local/services/**`,
`src/harness_local/api/**`, `tests/**`, `docs/**`, `examples/**`
**Criterios de aceptación:**
- `skeleton()` genera exactamente la lista de D088 y nada de `decisions/`, `architecture/` ni `research/`.
- AGENTS generado ≤60 líneas y CLAUDE/GEMINI ≤15, comprobado por test.
- El índice gestionado de DECISIONS se regenera desde sus encabezados y rechaza numeración duplicada.
- Crear un proyecto v1 se rechaza con diagnóstico; un proyecto sin `documents` opera con el layout unificado.
- Snapshots y runs anteriores se leen sin cambios; las pruebas de documentos y definición se actualizan, no se borran.
**Comandos de validación:**
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline alembic check`
**Referencias:** D088 puntos 1, 2, 5, 7 y 9; D072; D073; [SPECIFICATION §6](SPECIFICATION.md)

## P008-T003 — Rutas protegidas, paridad diagramas‑código y propuestas de ADR

**Objetivo:** Permitir que el ejecutor mantenga los diagramas y la documentación de producto, y reservar al harness los
documentos de control.
**Estado:** completada el 2026-10-15 ([D090](DECISIONS.md#d090--p008-t003-rutas-del-ejecutor-paridad-de-diagramas-y-propuestas-de-adr)).
Mecanismo del ejecutor: campo opcional `decision_proposals` de su JSON final. `reference_project` conserva `docs/**` hasta el
Flujo A; `typescript-web` no declara `data_model_paths`.
**Alcance:**
- Perfiles: sustituir la protección `docs/**` por `docs/STATE.md`, `docs/NEXT_STEPS.md`, `docs/ROADMAP.md`,
  `docs/DECISIONS.md`, `docs/archive/**`, `AGENTS.md`, `CLAUDE.md` y `GEMINI.md`. `harness_owned_paths` igual.
- `protected_write` y `Layout.editable`: el harness escribe AGENTS, CLAUDE y GEMINI en creación, edición confirmada e
  importación.
- Paridad: el perfil declara patrones de modelos de datos (`data_model_paths`, p. ej. `**/models.py`,
  `**/migrations/**`). Si el diff los toca sin tocar `docs/DDBB-DIAGRAM.md`, la aceptación queda bloqueada con motivo
  determinista. Para flujos, `review-task` (versión nueva) obliga a rechazar cambios de flujo de negocio sin
  `docs/flows/` actualizado.
- ADR: el ejecutor no edita DECISIONS; puede proponer decisiones en su salida y el revisor las devuelve como
  `decision_proposals` acotadas, que se guardan con el intento y se muestran para consolidarlas en la reconciliación o
  por edición confirmada. El mecanismo exacto de la salida del ejecutor se decide en la tarea sin cambiar el veredicto.
**Rutas permitidas:** `src/harness_local/profiles/**`, `src/harness_local/core/engine/**`, `src/harness_local/adapters/cli_agents.py`,
`src/harness_local/storage/**`, `src/harness_local/api/**`, `tests/**`, `docs/**`
**Criterios de aceptación:**
- Un contrato con `docs/flows/x.md` o `docs/DDBB-DIAGRAM.md` permitido deja escribir al ejecutor; STATE, NEXT_STEPS,
  ROADMAP, DECISIONS y el archivo siguen prohibidos salvo en la reconciliación.
- Un diff que toca modelos sin DDBB-DIAGRAM no se acepta; con el diagrama, sí.
- Una propuesta de ADR queda registrada y visible sin escribir DECISIONS.
**Comandos de validación:**
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
**Referencias:** D088 puntos 2, 6 y 8; D081

## P008-T004 — Cierre de fase unificado

**Objetivo:** Que cerrar una fase tras READY ejecute el protocolo de [SPECIFICATION §7](SPECIFICATION.md#7-cierre-de-fase)
en un único flujo determinista.
**Estado:** completada el 2026-10-15 ([D091](DECISIONS.md#d091--p008-t004-cierre-y-archivo-unificados-con-planificación-posterior)).
**Alcance:**
- La autorización de cierre lanza un job que, con intenciones conciliables, crea el tag sobre el HEAD evaluado y
  después un único commit de archivo: `docs/archive/phase-NNN/` con STATE y NEXT_STEPS por bytes, REVIEW, SUMMARY y
  todo `docs/phase/**` movido sin cambiar bytes; STATE nuevo (título, bloque, base acumulada, «Fase activa — N+1»);
  NEXT_STEPS con el objetivo y los criterios de N+1 de ROADMAP y sin tareas; ROADMAP con N completada y la columna
  «Archivo» enlazando `archive/phase-NNN/`.
- La fase N+1 se crea ACTIVE sin tareas. Su plan llega después (conversación `phase_planning` o texto del usuario) como
  una operación confirmada que escribe NEXT_STEPS y enmienda la definición (D034).
- El abandono archiva por la misma vía. Sin más fases en ROADMAP, solo se archiva.
- El check devuelve `NEEDS_RECONCILIATION` si la base acumulada supera 12 KiB o STATE 24 KiB.
- La transición separada de H6.3 se retira; las intenciones pendientes de esa operación se siguen conciliando.
**Rutas permitidas:** `src/harness_local/core/engine/**`, `src/harness_local/storage/**`, `src/harness_local/services/**`,
`src/harness_local/api/**`, `tests/**`, `docs/**`. Extensiones técnicas necesarias: `src/harness_local/adapters/git.py`
para escritura binaria y borrado CAS; `frontend/openapi.json` y `frontend/src/api.generated.ts` para los contratos
generados de los endpoints mínimos (D091).
**Criterios de aceptación:**
- Recorrido sintético: READY → cierre → un tag y un commit con el archivo exacto, documentos frescos y N+1 ACTIVE.
- Caída en cada efecto (tag, escritura, commit, registro) concilia el mismo tag y commit sin duplicarlos.
- Rechazo previo, sin escrituras, con checkout sucio, documentos distintos de su base, archivo existente o trabajo
  pendiente.
- `docs/phase/` queda vacía y su contenido aparece byte a byte en el archivo.
**Comandos de validación:**
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
**Referencias:** D088 punto 4; D032; D034; [flujo](flows/phase-lifecycle.md)

## P008-T005 — Prompts, definición y reconciliación al nuevo layout

**Objetivo:** Alinear plantillas de prompts y la conversación de definición con la estructura unificada.
**Estado:** completada el 2026-10-15 ([D092](DECISIONS.md#d092--p008-t005-prompts-y-definición-bajo-el-contrato-unificado)).
Se conserva el completado por plantilla de D089; el resultado aceptado exige los once documentos.
**Alcance:**
- Versiones nuevas de `define-project`, `plan-phase`, `reconcile-phase`, `close-phase`, `review-task` y `execute-task`:
  DDBB-DIAGRAM y `flows/` en lugar de `architecture/`; DECISIONS único; `docs/phase/` para artefactos; ADR solo como
  propuesta; regla de paridad; discovery de AGENTS.
- `definition.py`: borradores admitidos = plantilla + `docs/flows/*.md` + archivos raíz de instrucciones; documentos
  obligatorios según D088; la aceptación escribe AGENTS, CLAUDE y GEMINI.
- `plan-phase` planifica la fase activa sin tareas que deja T004.
**Rutas permitidas:** `src/harness_local/core/engine/**`, `src/harness_local/storage/**`, `tests/**`, `docs/**`.
Extensión técnica: `services/local_config.py` y `services/managed.py` para congelar `document_layout = "d088-4"`
y conservar la conciliación de transiciones ya selladas, sin invocar agentes. `revise-task` recibe las mismas reglas
que `execute-task` para que las correcciones las conserven.
**Criterios de aceptación:**
- De una carpeta vacía a commit raíz con la estructura de D088 y P001, con conversación sintética.
- Ningún prompt menciona `decisions/`, `architecture/` ni `research/`; los intentos anteriores conservan su versión.
**Comandos de validación:**
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
**Referencias:** D088; D075; [flujo](flows/project-definition.md)

## P008-T006 — API y UI mínimas

**Objetivo:** Que la API y la UI dejen de depender de rutas y conceptos retirados, sin rediseño visual.
**Estado:** completada el 2026-10-15 ([D093](DECISIONS.md#d093--p008-t006-api-y-ui-del-contrato-unificado)).
El estado de creación conserva solo su GET; las escrituras v1 y los endpoints de transición se retiran. El plan
posterior usa la fase ACTIVE sin tareas de T004, por texto o propuesta confirmada.
**Alcance:**
- Esquemas: carpetas `flows/` y `phase/`, índice de decisiones desde DECISIONS, clases de documento para instrucciones,
  diagramas, flujos y trabajo de fase; acción de cierre unificada; sin endpoints de creación v1 ni de transición.
- OpenAPI y tipos regenerados. UI: `markdown.ts`, `pages/Docs.tsx`, `pages/Planning.tsx`, `pages/Project.tsx` y
  retirada de `Bootstrap.tsx`.
**Rutas permitidas:** `src/harness_local/api/**`, `frontend/src/**`, `frontend/tests/**`, `frontend/openapi.json`, `tests/**`
**Criterios de aceptación:**
- Ninguna referencia a `decisions/DNNN`, `architecture/` o `research/` en API ni UI.
- Pruebas Node y pytest de rutas actualizadas; build del frontend correcto.
**Comandos de validación:**
- `node --test frontend/tests/*.test.mjs`
- `npm --prefix frontend run build`
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
**Referencias:** D088; D080; D082

## P008-T007 — Instrucciones del proyecto en el contexto congelado

**Objetivo:** Garantizar que cada agente lee `AGENTS.md` del proyecto en cada intento.
**Estado:** completada el 2026-10-16 ([D094](DECISIONS.md#d094--p008-t007-agentsmd-en-el-prompt-congelado-de-cada-rol)).
Evidencia de los flags en el [registro](phase/P008-T007_INSTRUCCIONES_CONTEXTO.md): Codex solo carga `AGENTS.md` en el
lector (el escritor es `untrusted`) y Claude no carga `CLAUDE.md`. Cambio de flag seguro: `project_doc_max_bytes=0`
en Codex (`cli-11`). La definición no recibe la variable porque redacta el archivo.
**Alcance:**
- Verificar sin ejecutar proveedores (ayuda, documentación oficial y fuente de los pins) si Claude con
  `--setting-sources ""` carga `CLAUDE.md` y si Codex con `--ignore-rules` y proyecto `untrusted` carga `AGENTS.md`.
  Registrar la evidencia en `docs/phase/`.
- Inyectar el contenido de `AGENTS.md` (acotado, con hash) en el contexto congelado de todos los roles mediante una
  variable de plantilla nueva, con versiones nuevas de prompts y adaptador. Un proyecto sin `AGENTS.md` se detiene
  antes de invocar. Los flags solo cambian si la verificación demuestra que es seguro y se conservan los controles de
  memoria de D066.
**Rutas permitidas:** `src/harness_local/core/engine/**`, `src/harness_local/adapters/cli_agents.py`, `tests/**`, `docs/**`
**Criterios de aceptación:**
- El prompt renderizado de cada rol contiene `AGENTS.md` y su hash figura en el snapshot del intento.
- Cambiar `AGENTS.md` afecta solo a intentos posteriores; los jobs congelados anteriores entran en cuarentena.
**Comandos de validación:**
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
**Referencias:** D088 punto 8; D066; D068

## P008-T008 — Perfiles declarativos en el TOML local

**Objetivo:** Declarar perfiles de stack en el TOML del operador, empezando por Python/Django con pytest, ruff y mypy.
**Estado:** completada el 2026-10-16 ([D095](DECISIONS.md#d095--p008-t008-perfiles-declarados-en-local-config-4)).
JUnit declarado junto a su validación; en v4 el perfil de toda composición entra en el hash. Los textos de ayuda,
registro y UI que citan `local-config-3` quedan fuera de las rutas de la tarea ([registro](phase/P008-T008_PERFILES_DECLARATIVOS.md)).
**Alcance:**
- Formato nuevo del TOML (`local-config-4`) con `[profiles.<nombre>]`: preparación, validaciones (argv), prefijos
  permitidos, rutas protegidas y sensibles, reportes JUnit, `data_model_paths` e instrucciones del ejecutor. Las
  composiciones nombran un perfil declarado o uno integrado; los formatos 1–3 se siguen leyendo.
- Ejemplo `python-django` en `examples/local_config.example.toml`: `pytest --junitxml`, `ruff check`,
  `ruff format --check`, `mypy` y `manage.py check`/`makemigrations --check`, que el usuario confirma.
- El contenido del perfil entra en el hash congelado de la composición; cambiarlo pone en cuarentena los jobs
  pendientes.
**Rutas permitidas:** `src/harness_local/services/local_config.py`, `src/harness_local/profiles/**`,
`src/harness_local/core/engine/context.py`, `examples/**`, `tests/**`, `docs/**`
**Criterios de aceptación:**
- `check-config` valida un perfil `python-django` y rechaza claves desconocidas o argv con shell.
- Una tarea sintética con agentes y comandos falsos recorre validación, JUnit y commit con ese perfil.
- `typescript-web` y las composiciones existentes conservan su comportamiento.
**Comandos de validación:**
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
**Referencias:** D088 punto 11; D049; D078

## P008-T009 — Flujo A: inventario de solo lectura

**Objetivo:** Auditar un proyecto de un harness anterior sin modificarlo.
**Estado:** completada el 2026-10-16 ([D096](DECISIONS.md#d096--p008-t009-inventario-de-importación-desde-el-árbol-de-head)).
Lee el árbol de HEAD de un checkout limpio con Git de solo lectura; sin persistencia, API ni UI (T011 congela el
inventario). Clases, reglas y límites en el [registro](phase/P008-T009_INVENTARIO_FLUJO_A.md).
**Alcance:**
- Proyecto registrado no vacío, en Git y con checkout limpio. Detección del origen: tipo ReferenceProject (`.harness/`,
  `PROJECT.md`, `REQUIREMENTS.md`, `archive/phase-NNN` sin STATE), v1 de este harness (`BRIEF.md`,
  `PROJECT_PROFILE.md`, `DELIVERY_CHECKLIST.md`) o v2 (`decisions/`, `architecture/`, `research/`).
- Inventario con ruta, tamaño y hash; clase de cada documento (canónico, renombrable, fusionable, histórico, ajeno);
  fases detectadas en ROADMAP, archivo y STATE/NEXT_STEPS; tamaño de AGENTS y CLAUDE; bloques gestionados; runs
  legacy (que siguen la migración D027).
- Sin ejecutar código del proyecto; lecturas acotadas; enlaces simbólicos rechazados.
**Rutas permitidas:** `src/harness_local/core/**`, `src/harness_local/adapters/**`, `src/harness_local/storage/**`,
`src/harness_local/migrations/**`, `src/harness_local/api/**`, `tests/**`, `docs/**`
**Criterios de aceptación:**
- Tres fixtures sintéticos (ReferenceProject, v1, v2) producen inventarios deterministas sin escrituras en el checkout.
- Releer el mismo checkout devuelve el mismo inventario y hash.
**Comandos de validación:**
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
**Referencias:** D088 punto 10; D012; D027; [flujo](flows/legacy-migration.md)

## P008-T010 — Flujo A: mapa de normalización determinista

**Objetivo:** Calcular sin agentes los movimientos y renombrados inequívocos hacia la estructura de D088.
**Estado:** completada el 2026-10-16 ([D097](DECISIONS.md#d097--p008-t010-mapa-de-normalización-del-flujo-a)).
Función pura del inventario y sus bytes, sin persistencia (T011 congela el mapa). Lo retirado sin fase va a
`archive/phase-000/`; reglas, motivos de revisión y límites en el [registro](phase/P008-T010_MAPA_NORMALIZACION.md).
**Alcance:**
- Reglas con identificador: variantes de nombre (mayúsculas, `DECISSONS.md`, `decisions.md`, `ADR*.md`) hacia el
  nombre canónico por lista de alias explícita; `archive/phase-N` → `phase-NNN`; `decisions/DNNN-*.md` → secciones de
  DECISIONS en orden; `architecture/data-model.md` → `DDBB-DIAGRAM.md`; `research/**` y artefactos de fase → archivo
  de su fase o `docs/phase/`; v1 `BRIEF.md` y `PROJECT_PROFILE.md` → `archive/phase-000/`.
- Lo ambiguo (por ejemplo `PROJECT.md` + `REQUIREMENTS.md` → SPECIFICATION, `HARNESS_COMMANDS.md`, `UI_*.md`) queda
  marcado para la propuesta del revisor (T011). Los archivos ajenos se listan para decisión del usuario.
**Rutas permitidas:** `src/harness_local/core/**`, `tests/**`, `docs/**`
**Criterios de aceptación:**
- Cada movimiento conserva los bytes y cita su regla; ninguna regla sobrescribe un destino existente.
- Los fixtures de T009 dan mapas deterministas; `DECISSONS.md` acaba como `DECISIONS.md`.
**Comandos de validación:**
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
**Referencias:** D088 punto 10

## P008-T011 — Flujo A: propuesta del revisor

**Objetivo:** Que el revisor, en solo lectura, proponga las fusiones y el adelgazamiento que el mapa no resuelve.
**Estado:** completada el 2026-10-16 ([D098](DECISIONS.md#d098--p008-t011-conversación-de-importación-con-borradores-privados)).
Rol de solo lectura `definition` con la plantilla `import-project`; inventario y mapa congelados en
`planning_conversations.source` (`0019`); bloqueos de la vista previa en `GET …/planning/{c}/import`. El orden entre
la activación D027 y la importación con runs legacy lo fija [D099](DECISIONS.md#d099--flujo-a-activación-d027-antes-de-la-importación) para T012.
**Alcance:**
- Conversación `import` sobre la infraestructura de H6.5, con inventario, mapa y contenidos congelados: borradores de
  SPECIFICATION y ARCHITECTURE fusionados, AGENTS ≤60 líneas que conserve las reglas del proyecto, CLAUDE y GEMINI
  envoltorios, STATE y NEXT_STEPS sincronizados con la fase activa, DDBB-DIAGRAM y `flows/` si faltan, preguntas ante
  incongruencias.
- Borradores en un área privada junto a SQLite, editables desde la UI y con CAS; el checkout no se toca hasta la
  confirmación (T012).
**Rutas permitidas:** `src/harness_local/core/engine/**`, `src/harness_local/storage/**`, `src/harness_local/api/**`,
`src/harness_local/migrations/**`, `tests/**`, `docs/**`
**Criterios de aceptación:**
- Turno inválido o con rutas no admitidas: FAILED sin fallback; el agente no escribe.
- Las preguntas bloqueantes impiden pasar a la vista previa hasta responderlas o aplazarlas.
**Comandos de validación:**
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
**Referencias:** D088; D075

## P008-T012 — Flujo A: vista previa, commit y continuidad

**Estado:** completada el 2026-10-16 ([D100](DECISIONS.md#d100--p008-t012-importación-confirmada-y-continuidad-del-flujo-a)).
Vista previa con originales conservados, intención sellada, commit conciliable y fase activa adoptada. D099
implementada: activación antes de conversar, marcador local validado y excluido de Git. Detalle y extensiones
técnicas en el [registro](phase/P008-T012_COMMIT_CONTINUIDAD.md).

**Objetivo:** Aplicar la normalización en un único commit confirmado y dejar el proyecto listo para seguir trabajando.
**Alcance:**
- Vista previa con el árbol completo: movimientos, renombrados, borradores aplicados, archivos de fase y documentos
  retirados (siempre conservados en `archive/`). Confirmación por hash, motivo e Idempotency-Key; job con intención
  sellada; commit «docs: normalizar al contrato documental»; adopción de la fase activa y sus documentos.
- Si hay runs legacy, la migración D027 se ofrece como operación confirmada aparte y va primero ([D099](DECISIONS.md#d099--flujo-a-activación-d027-antes-de-la-importación)): el
  inventario tolera solo el marcador `.harness/managed-mode.json` de una activación viva, y el commit no lo versiona
  ni toca `.gitignore`.
**Rutas permitidas:** `src/harness_local/**`, `frontend/src/**`, `tests/**`, `docs/**`
**Criterios de aceptación:**
- Cada fixture de T009 acaba con la estructura de D088, sin bytes perdidos (todo original está movido o archivado) y
  con STATE y NEXT_STEPS coherentes con la fase activa.
- Repetir la importación no encuentra cambios; una caída concilia el mismo commit.
- Con runs legacy: sin activación, la importación ofrece la activación D027; tras activarla, el marcador no bloquea el
  inventario ni entra en el commit, y un marcador ajeno a la activación viva sí bloquea.
**Comandos de validación:**
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
- `node --test frontend/tests/*.test.mjs`
**Referencias:** D088; D027; D037; D099

## P008-T013 — Flujo B: inventario determinista

**Objetivo:** Describir un repositorio sin harness por análisis estático, sin ejecutar su código.
**Estado:** completada el 2026-10-16 ([D101](DECISIONS.md#d101--p008-t013-inventario-estático-del-flujo-b-y-propuesta-de-perfil)).
Inventario recalculable de HEAD con fuentes, hashes y límites explícitos; propuesta `[profiles.*]` de
`local-config-4` pendiente de confirmación. Sin API, UI, persistencia ni escritura de TOML: T014/T015 incorporarán
la conversación y la confirmación. Detalle en el [registro](phase/P008-T013_INVENTARIO_FLUJO_B.md).
**Alcance:**
- Detección de stack (`pyproject.toml`, `requirements*.txt`, `manage.py`, `package.json`, `go.mod`…), modelos de datos
  (SQLAlchemy, modelos Django, Prisma, entidades TypeORM) por lectura sintáctica, rutas (Django `urls.py`, decoradores
  FastAPI, Express), tests y CI. Ignora dependencias instaladas y artefactos de build.
- Propuesta de perfil en el formato de T008, que el usuario confirma o edita; nunca se escribe el TOML.
**Rutas permitidas:** `src/harness_local/core/**`, `src/harness_local/adapters/**`, `src/harness_local/storage/**`,
`src/harness_local/api/**`, `tests/**`, `docs/**`
**Criterios de aceptación:**
- Fixtures sintéticos Django y TypeScript dan inventarios deterministas con sus entidades, rutas y comandos de test.
- Ningún proceso del proyecto se ejecuta durante el inventario.
**Comandos de validación:**
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
**Referencias:** D088 punto 11

## P008-T014 — Flujo B: ingeniería inversa del revisor

**Estado:** completada el 2026-10-16 ([D102](DECISIONS.md#d102--p008-t014-ingeniería-inversa-sobre-head-y-borradores-privados)).
Conversación `onboarding` con el inventario y HEAD congelados, exportación privada de solo lectura y borradores
privados con CAS; preguntas y decisiones inferidas. Sin commit ni perfil activo hasta T015. Detalle y extensiones
técnicas en el [registro](phase/P008-T014_INGENIERIA_INVERSA.md).

**Objetivo:** Generar en solo lectura los documentos iniciales a partir del código real.
**Alcance:**
- Conversación `onboarding` con el inventario y una instantánea de solo lectura del HEAD (como el chat de D083):
  borradores de ARCHITECTURE, DDBB-DIAGRAM desde los modelos reales, SPECIFICATION base, `flows/` de los módulos
  principales, ROADMAP con P001, STATE con la base actual, NEXT_STEPS, DECISIONS con las decisiones observadas
  marcadas como inferidas, AGENTS, CLAUDE y GEMINI. Un README existente no se sustituye sin confirmación.
- Lo que no se puede deducir del código se pregunta; nada se inventa fuera de lo observado.
**Rutas permitidas:** `src/harness_local/core/engine/**`, `src/harness_local/storage/**`, `src/harness_local/api/**`,
`tests/**`, `docs/**`
**Criterios de aceptación:**
- Con el fixture Django, DDBB-DIAGRAM contiene exactamente sus entidades y relaciones.
- Turnos inválidos sin fallback; el agente no escribe.
**Comandos de validación:**
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
**Referencias:** D088; D083

## P008-T015 — Flujo B: vista previa, commit y control del harness

**Estado:** completada el 2026-10-16 ([D103](DECISIONS.md#d103--p008-t015-incorporación-confirmada-del-flujo-b)).
Vista previa y perfil de la composición confirmados por hash, originales conservados, commit conciliable y P001
ACTIVE adoptada. No escribe el TOML ni ejecuta comandos del proyecto. Detalle en el
[registro](phase/P008-T015_INCORPORACION_CONFIRMADA.md).

**Objetivo:** Dejar el repositorio bajo control del harness con un único commit documental confirmado.
**Alcance:**
- Vista previa con los documentos nuevos, `archive/phase-000/` (inventario y resumen de la incorporación) y las
  versiones anteriores de README, AGENTS o CLAUDE que se sustituyan. Confirmación por hash; commit sin tocar código;
  P001 ACTIVE con sus documentos adoptados; perfil confirmado en la composición.
**Rutas permitidas:** `src/harness_local/**`, `frontend/src/**`, `tests/**`, `docs/**`
**Criterios de aceptación:**
- Los fixtures Django y TypeScript terminan con la estructura de D088 y ningún archivo de código modificado.
- Repetir la incorporación no encuentra cambios; una caída concilia el mismo commit.
**Comandos de validación:**
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
- `node --test frontend/tests/*.test.mjs`
**Referencias:** D088; D037

## P008-T016 — Flujo A: filtros Git, bytes exactos y destinos ignorados

**Estado:** completada el 2026-10-17 ([D105](DECISIONS.md#d105--p008-t016-frontera-git-y-bytes-confirmados-en-las-importaciones)).
Guardias compartidas A/B antes de inventario/captura/sellado y ejecución; todos los blobs documentales contrastados
por SHA-256 y destinos nuevos ignorados rechazados. `document_layout = "d088-9"`; CAS, D099 y conciliación conservadas.
Detalle y verificación en el [registro](phase/P008-T016_FRONTERA_GIT.md). Derivada de H1–H3 de D104.
**Objetivo:** Cumplir las garantías ya decididas para el Flujo A antes de aceptar su inventario, vista previa y
commit: sin ejecución de filtros del proyecto, sin conversiones de bytes confirmados y sin escrituras de una
importación que no pueda incluir todos sus destinos en Git.
**Alcance:**
- Aplicar al Flujo A las guardias que ya utiliza B, reutilizando lo común cuando corresponda. Comprobar filtros
  `clean`/`process`, incluidos includes, antes de `status`/captura/sellado y de la ejecución del job.
- Contrastar los blobs del árbol propuesto con los bytes confirmados, incluidos originales archivados y binarios;
  rechazar conversiones y destinos nuevos ignorados antes de confirmar o escribir.
- Mantener CAS, D099, recuperación del mismo commit, compatibilidad de historiales y el Flujo B. Evaluar la versión
  congelada que requiere el cambio; no reescribir intenciones selladas ni configuración del usuario.
**Rutas permitidas:** `src/harness_local/adapters/**`, `src/harness_local/core/engine/import_commit.py`,
`src/harness_local/core/engine/documents.py`,
`src/harness_local/storage/project_import.py`, `src/harness_local/storage/onboarding_commit.py`,
`src/harness_local/services/managed.py`, `src/harness_local/services/local_config.py`, `tests/**`, `docs/**`.
**Criterios de aceptación:**
- H1: inventario/preview/job rechazan filtros locales y por include sin ejecutarlos; sin marcador sintético ni
  cambios en checkout/índice. La comprobación precede a cualquier comando Git que pueda invocarlos.
- H2: el borrador CRLF con `text eol=lf` se rechaza antes de escribir/adoptar; cada blob admitido coincide con su
  hash confirmado. Originales y binarios conservan sus bytes; los casos válidos A/B siguen llegando a COMMITTED.
- H3: un GEMINI nuevo ignorado bloquea antes de escribir, sin operación, commit ni fase nuevos; `.gitignore` intacto.
- Las caídas y reintentos conservan la conciliación documentada; las pruebas de regresión usan exclusivamente
  fixtures temporales sintéticos, agentes y herramientas falsas.
**Comandos de validación:**
- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
**Referencias:** D096; D099; D100; D103; D104; [revisión y reproducciones](phase/P008_REVISION_SALIDA.md).

## P008-T017 — Sincronizar referencias vigentes de P008

**Estado:** completada el 2026-10-17 ([D106](DECISIONS.md#d106--p008-t017-referencias-vigentes-sin-cambiar-contratos)).
Textos vigentes alineados con el código, sin cambios de contratos ni evidencias congeladas; verificación y límites
en el [registro](phase/P008-T017_REFERENCIAS_VIGENTES.md). Resuelve H4 de D104, tras la corrección funcional de T016.
**Objetivo:** Que los textos activos reflejen lo implementado, antes de repetir la revisión de salida.
**Alcance:** estados F11/F18 de SPECIFICATION, versión del adaptador en ARCHITECTURE, ayudas de registro/serve y
Home/Registry sobre `local-config-4`, y mensajes de Prompts sobre cierre/reconciliación. Contrastar otros textos
vigentes afectados; conservar ADR, archivos, snapshots e intenciones históricos.
**Rutas permitidas:** `docs/**`, `src/harness_local/cli.py`, `src/harness_local/services/project_registry.py`,
`frontend/src/**`, `tests/**`, `frontend/tests/**`.
**Criterios de aceptación:** las referencias vigentes concuerdan con D093, D095, D102 y D105 y los contratos actuales;
sin cambios de comportamiento, contratos ni evidencias congeladas.
**Comandos de validación:** checks ligeros, pruebas dirigidas a ayudas/registro, pruebas Node y build del frontend.
**Referencias:** D104 H4; [revisión](phase/P008_REVISION_SALIDA.md). Tras esta tarea, nueva revisión de salida;
cierre y archivo separados.

## P008-T018 — Flujo A: lecturas sin lazy-fetch y objetos ausentes

**Objetivo:** Impedir que el inventario A recupere objetos prometidos o ejecute transportes Git durante una lectura;
rechazar un objeto ausente con un diagnóstico explícito, sin ejecutar código ni acceder a remotos.
**Estado:** completada el 2026-10-17 ([D108](DECISIONS.md#d108--p008-t018-lecturas-de-importación-sin-lazy-fetch)).
`LocalGit` compartido exige `--no-lazy-fetch` desde el primer comando A/B; tamaños y objetos ausentes bloquean
con diagnóstico, sin respuestas parciales. `document_layout = "d088-10"`; guardias, D099, CAS y conciliación
conservadas. Detalle y verificación en el [registro](phase/P008-T018_OBJETOS_LOCALES.md). Derivada de H5 de D107.
**Alcance:**
- Desactivar lazy-fetch obligatoriamente desde el primer comando Git del lector A, incluidos `rev-parse`,
  `status`, `ls-tree -l` y `cat-file`; reutilizar la frontera local de B o extraer lo común sin dependencias circulares.
- Cubrir los puntos de inventario, conversación y vista previa que leen el origen mediante `read_checkout`.
  Rechazar tamaños/objetos ausentes sin `int('BAD')` ni respuestas parciales, también en los lectores compartidos
  con B. No recuperar objetos, ejecutar transportes ni modificar configuración para resolver la ausencia.
- Mantener las guardias de filtros, D099, CAS, hashes, conciliación y compatibilidad de historiales; evaluar
  la versión congelada que exige la corrección sin reescribir intenciones ni snapshots.
**Rutas permitidas:** `src/harness_local/adapters/**`, `src/harness_local/storage/import_drafts.py`,
`src/harness_local/storage/project_import.py`, `src/harness_local/storage/onboarding_commit.py`,
`src/harness_local/core/engine/documents.py`, `src/harness_local/services/local_config.py`, `tests/**`, `docs/**`.
**Criterios de aceptación:**
- Repositorio promisor sintético con blob ausente y `upload-pack` falso: inventario A rechazado con diagnóstico,
  sin marcador, red, cambios de checkout/índice/refs ni objetos recuperados. B conserva el rechazo sin transporte.
- El rechazo precede a un turno o sellado que pudiera invocar agentes/escritores; no hay operación, commit ni
  fase nuevos. Los inventarios completos, H1–H3, recorridos A/B y recuperación siguen funcionando.
- Regresiones exclusivamente con Git/SQLite temporales, herramientas falsas y fixtures sintéticos. Se conserva
  la evidencia histórica de H5; no se cambia para aparentar que describía el resultado corregido.
**Comandos de validación:**
- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
**Referencias:** D096; D100; D101; D105; D107; [revisión y reproducción](phase/P008_REVISION_SALIDA_2.md).
Después: nueva revisión de salida; cierre y archivo separados.

## P008-T019 — Flujo A: submódulos sin ejecución implícita

**Objetivo:** Que la consulta de un checkout con gitlinks no ejecute filtros ni código de submódulos antes de
aceptar o rechazar su inventario, conversación o vista previa.
**Estado:** completada el 2026-10-19 ([D110](DECISIONS.md#d110--p008-t019-gitlinks-rechazados-antes-de-inspeccionar-el-checkout)).
Guardia de HEAD/índice en todo el repositorio antes de `status` y de captura/sellado/escritura/recuperación A/B,
sin consultar hijos ni suavizar la limpieza; `document_layout = "d088-11"`. Verificación y límites en el
[registro](phase/P008-T019_SUBMODULOS.md). Derivada de H6 de [D109](DECISIONS.md#d109--tercera-revisión-de-salida-de-p008).
**Alcance:**
- Impedir la inspección ejecutable de submódulos desde `status --ignore-submodules=none`: la guardia del
  repositorio principal no cubre su configuración. Resolver antes del comando que pueda ejecutar el filtro,
  tanto con gitlinks dentro de `docs/` como fuera del ámbito documental, sin ampliar soporte de submódulos.
- Cubrir los consumidores de `read_checkout` (creación, turnos, estado, vista previa y confirmación); revisar
  también la captura/escritura compartida A/B y la recuperación, sin ocultar cambios del checkout ni suavizar
  el requisito de limpieza. No ejecutar filtros para averiguar si un submódulo está limpio.
- Mantener filtros del repositorio principal e includes, objetos locales sin lazy-fetch, bytes exactos,
  destinos ignorados, D099, CAS y conciliación del mismo commit. Evaluar la versión congelada del cambio;
  no modificar configuración ni evidencia, intenciones o snapshots históricos.
**Rutas permitidas:** `src/harness_local/adapters/**`, `src/harness_local/storage/import_drafts.py`,
`src/harness_local/storage/project_import.py`, `src/harness_local/storage/onboarding_commit.py`,
`src/harness_local/core/engine/import_commit.py`, `src/harness_local/core/engine/documents.py`,
`src/harness_local/services/managed.py`, `src/harness_local/services/local_config.py`, `tests/**`, `docs/**`.
**Criterios de aceptación:**
- Padre sintético limpio, sin filtros propios, con gitlink y submódulo inicializado cuyo filtro falso `clean`
  (directo o por include) crea un marcador: ninguna lectura A lo ejecuta, dentro o fuera de `docs/`.
  Si el checkout no es admisible, el rechazo llega con diagnóstico antes del efecto; los bytes del checkout,
  índice, refs, configuración y objetos permanecen intactos.
- El bloqueo precede a cualquier turno/agente o sellado/escritura; sin nueva operación, commit o fase.
  La creación de conversación también debe quedar protegida. Cubrir `process` cuando corresponda y no
  depender solo de los filtros del padre o de la selección documental posterior a `status`.
- H1–H5, checkout sucio, recorridos válidos A/B, D099 y recuperación siguen funcionando. Regresiones solo
  con Git/SQLite temporales, herramientas falsas y fixtures sintéticos; sin red ni proveedores reales.
**Comandos de validación:**
- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
**Referencias:** D096; D100; D103; D105; D108; D109;
[revisión y reproducciones](phase/P008_REVISION_SALIDA_3.md).
Después: nueva revisión de salida; cierre y archivo separados.

# P008 — Contrato documental unificado, cierre de fase e importación de proyectos

Objetivo y criterios de salida en [ROADMAP](ROADMAP.md#p008--contrato-documental-unificado-cierre-de-fase-e-importación-de-proyectos).
Decisión de base: [D088](DECISIONS.md#d088--contrato-documental-unificado-cierre-de-fase-automático-e-importación-de-proyectos-p008).
Análisis de incongruencias que originó la fase: [docs/phase](phase/P008-T001_MIGRACION_DOCUMENTAL.md).

**Siguiente tarea:** P008-T007. Orden de ejecución: T002 → T007 (motor y contrato), T008 (perfiles, que el usuario
necesita para su próximo proyecto Django), T009–T012 (Flujo A) y T013–T015 (Flujo B).

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

**Objetivo:** Aplicar la normalización en un único commit confirmado y dejar el proyecto listo para seguir trabajando.
**Alcance:**
- Vista previa con el árbol completo: movimientos, renombrados, borradores aplicados, archivos de fase y documentos
  retirados (siempre conservados en `archive/`). Confirmación por hash, motivo e Idempotency-Key; job con intención
  sellada; commit «docs: normalizar al contrato documental»; adopción de la fase activa y sus documentos.
- Si hay runs legacy, la migración D027 se ofrece como operación confirmada aparte.
**Rutas permitidas:** `src/harness_local/**`, `frontend/src/**`, `tests/**`, `docs/**`
**Criterios de aceptación:**
- Cada fixture de T009 acaba con la estructura de D088, sin bytes perdidos (todo original está movido o archivado) y
  con STATE y NEXT_STEPS coherentes con la fase activa.
- Repetir la importación no encuentra cambios; una caída concilia el mismo commit.
**Comandos de validación:**
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`
- `node --test frontend/tests/*.test.mjs`
**Referencias:** D088; D027; D037

## P008-T013 — Flujo B: inventario determinista

**Objetivo:** Describir un repositorio sin harness por análisis estático, sin ejecutar su código.
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

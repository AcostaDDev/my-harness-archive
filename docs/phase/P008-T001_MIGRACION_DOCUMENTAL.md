# P008-T001 — Migración documental y análisis de incongruencias

Artefacto de trabajo de P008 (se archivará en `docs/archive/phase-008/` al cerrar la fase). Base: `8622a43` (cierre
D087), decisión [D088](../DECISIONS.md#d088--contrato-documental-unificado-cierre-de-fase-automático-e-importación-de-proyectos-p008).

## 1. Incongruencias del motor con D088 (entrada de T002–T007)

| Tema | Situación en el código al empezar P008 | Tarea |
|---|---|---|
| Layout | `core/engine/documents.py` (`Layout`, `skeleton`, `FOLDER_READMES`): `decisions/` con índice gestionado, `architecture/` (con `data-model.md`), `research/`; sin AGENTS, CLAUDE, GEMINI, DDBB-DIAGRAM, `flows/` ni `phase/` | T002 |
| Opcionalidad | `documents = "v2"` opcional (`documents.layout`, `local_config.py`); sin la clave no hay contrato documental | T002 |
| Creación v1 | `core/engine/bootstrap.py` crea `BRIEF.md`, `PROJECT_PROFILE.md` y `DELIVERY_CHECKLIST.md`; `frontend/src/Bootstrap.tsx` | T002, T006 |
| Presupuestos | 8 KiB para DECISIONS.md (`BUDGETS`), incompatible con un registro único | T002 |
| Protección | Perfiles protegen `docs/**`, `AGENTS.md`, `CLAUDE.md`; `protected_write` solo exime README y Markdown de `docs/`, así que el harness no puede escribir los archivos raíz y el ejecutor no puede mantener diagramas | T003 |
| Cierre | `close` (D032) y `phase_transition` (H6.3) separados; la transición exige el plan de N+1, arrastra la base acumulada, no mueve artefactos de fase y ROADMAP no enlaza el archivo | T004 |
| Prompts y definición | `define-project.md`, `plan-phase.md` y `definition.py` (`allowed_draft`, `required_documents`) hablan de `decisions/` y `architecture/` | T005 |
| API y UI | `storage/documents.py`, `api/schemas.py` (carpetas, índice, clases de documento), `frontend/src/markdown.ts`, `pages/Docs.tsx`, `pages/Planning.tsx` | T006 |
| Instrucciones | Claude se lanza con `--setting-sources ""` y Codex con `--ignore-rules` y proyecto `untrusted` (`adapters/cli_agents.py`); no está verificado que lean AGENTS/CLAUDE del checkout | T007 |
| Perfiles | El TOML solo compone `typescript-web` (`local_config.py`); no hay perfil Python/Django ni forma de declararlo | T008 |
| Importación | La creación exige carpeta vacía (`adapters/bootstrap.py`); el lector legacy y la migración D027 no reescriben documentos | T009–T015 |

Compatibles sin cambios: el lector legacy (`adapters/legacy.py`, `storage/navigation.py`) lee `docs/STATE.md`,
`NEXT_STEPS.md`, `ROADMAP.md` y `docs/archive/phase-%/`. El nombre `DECISSONS.md` no aparece en este repositorio ni en
ReferenceProject: su normalización es una regla del Flujo A (T010).

## 2. Migración de este repositorio

Script reproducible fuera del repositorio, probado antes en un clon temporal:

- `docs/discovery/` tenía 131 archivos (111 Markdown y 20 JSON/Python). Con `git mv`: 71 Markdown y 19 JSON/Python
  → `docs/archive/phase-001…007/` (`H5_CLOSURE_REVIEW.md` y `H6.2_CLOSURE_REVIEW.md` como `REVIEW.md` de su fase) y
  `baseline.json` → fixtures; 01, 02, 03 y START_HERE → `phase-000/`. Los otros 40 Markdown son los alcances
  fusionados y las propuestas eliminadas.
- 31 `*_SCOPE.md` fusionados, con la sección del backlog de su hito, en el `NEXT_STEPS.md` archivado de cada fase
  (encabezados bajados de nivel, origen indicado). El NEXT_STEPS del cierre de P007 queda al final del de `phase-007`.
- `docs/STATE.md` (2854 líneas) repartido por secciones entre los `STATE.md` archivados; «Existe», «Todavía no existe»,
  «Trabajo activo» y «Coordinación» quedan en `phase-007` como instantánea al cerrar P007.
- 9 propuestas ya ejecutadas eliminadas (las de las matrices D055–D071, `H2.3_ENV_SMOKE_PROPOSAL`,
  `H2.3_SMOKE_CLI3_PREFLIGHT` y `FIRST_USE_PROPOSAL`); sus enlaces pasan a texto con `git show 8622a43:<ruta>`.
- `baseline.json` → `tests/fixtures/legacy/baseline.json`; ruta actualizada en `tests/test_legacy_fixtures.py` y dos
  docstrings (`core/engine/metrics.py`, `tests/product/test_metrics.py`).
- Enlaces relativos de todo lo movido, de DECISIONS y de los README de fixtures recalculados; los enlaces a STATE y
  NEXT_STEPS desde el archivo apuntan al de su fase. Los 14 enlaces que ya estaban rotos en los alcances (escritos
  relativos a `docs/`) quedan corregidos.
- D036 citaba los marcadores `harness-local:managed-state` literales dentro de la prosa, y el parser de bloques del
  motor los rechaza como marcadores mal colocados. Se citan ahora sin el comentario HTML, sin cambiar el contenido de la
  decisión, para que el repositorio pueda registrarse más adelante. Los 18 documentos activos pasan ese parser.
- Nuevos: SPECIFICATION, ARCHITECTURE, ROADMAP, STATE, NEXT_STEPS, DDBB-DIAGRAM (generado desde el metadata
  SQLAlchemy), seis flujos en `docs/flows/`, índice y D088 en DECISIONS, `SUMMARY.md` por fase y GEMINI.md; AGENTS,
  CLAUDE y README reescritos.

## 3. Verificación

Resultados en [STATE](../STATE.md#fase-activa--p008-contrato-documental-unificado-cierre-de-fase-e-importación-de-proyectos).
Comprobaciones usadas: enlaces relativos de todos los Markdown, parser Mermaid de `frontend/node_modules/mermaid`
(11.17.2, sin DOM: DOMPurify sustituido solo para analizar la sintaxis), `parse_roadmap` y `plan_tasks` del motor sobre
ROADMAP y NEXT_STEPS, tamaños de AGENTS, CLAUDE, GEMINI, README y presupuestos de STATE y NEXT_STEPS, checks ligeros y
pytest completo.

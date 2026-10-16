# P008-T009 — Flujo A: inventario de solo lectura

Fecha: 2026-10-16. Base: D088 punto 10, D012 y D027. Decisión: [D096](../DECISIONS.md#d096--p008-t009-inventario-de-importación-desde-el-árbol-de-head).

## Entrega

- `core/project_import.py` (puro, sin disco, Git ni SQLite): ámbito documental, clasificación por regla con
  resolución de conflictos, detección de origen, fases, instrucciones, bloques gestionados, bloqueos y huella
  `inventory_sha256`. Formato `harness-local/import-inventory/1`.
- `adapters/project_import.py`: `read_checkout` (Git de solo lectura con el entorno controlado de `adapters/git.py`)
  y `read_inventory(context)` para un proyecto registrado; la carpeta de documentación es la de STATE en su contexto.
- `tests/product/test_project_import.py`: 14 casos con tres orígenes sintéticos generados en la prueba (tipo
  ReferenceProject, v1 y v2), sin archivos de fixture en el árbol para no dejar `AGENTS.md` ni `CLAUDE.md` de prueba que
  una sesión de agente pudiera cargar como instrucciones.

Sin API, UI, SQLite ni migraciones: el inventario es un valor que se recalcula y que T011 congelará con la
conversación de importación. Una ruta HTTP cambiaría `frontend/openapi.json`, fuera de las rutas de la tarea.

## Lectura

1. `rev-parse --show-toplevel` igual a la raíz del contexto; `HEAD` debe existir.
2. `status --porcelain=v1 -z --untracked-files=all` vacío (con `GIT_OPTIONAL_LOCKS=0`, no reescribe el índice).
   Un cambio o un archivo sin seguimiento rechazan el inventario con las primeras rutas.
3. `ls-tree -r -z -l --full-tree HEAD`: un HEAD sin archivos se rechaza (un proyecto vacío usa la creación).
4. Ámbito: Markdown de la raíz, todo `docs/` y `.harness/` salvo `.harness/runs/`. Como mucho 5.000 entradas, 16 MiB
   por entrada y 256 MiB en total; por encima, rechazo o entrada no leída, nunca truncado.
5. `cat-file --batch` de los blobs regulares (sin filtros ni textconv). Enlaces simbólicos (`120000`) y submódulos
   (`160000`) son entradas rechazadas sin leer su destino y aparecen en `blockers`.
6. `.harness/runs` por lstat: presencia, tipo (`dir`, `symlink`, `other`), número de directorios y presencia del
   marcador de D027. No se lee ningún run; su historial sigue la migración a gestionado existente.

Leer HEAD de un checkout limpio en lugar del disco hace que lo ignorado (entornos, `.env`, cachés) no se lea nunca y
que releer el mismo checkout dé el mismo resultado. Los filtros `clean` definidos en la configuración local del
repositorio podrían ejecutarse en `status`; vienen de la configuración del usuario, no del contenido del proyecto, y
`adapters/git.py` ya documenta ese límite.

## Clasificación

| Clase | Reglas |
|---|---|
| `canonical` | `canonical-path` (AGENTS, CLAUDE, GEMINI, README y los siete documentos de `docs/`), `flow` (`docs/flows/*.md`), `phase-work` (`docs/phase/**`) |
| `renameable` | `alias-case` (mismo nombre en otras mayúsculas), `alias-root-document` (documento de `docs/` en la raíz), `alias-name` (`DECISSONS.md`), `alias-adr` (`ADR*.md`), `data-model` (`architecture/data-model.md` → DDBB-DIAGRAM) |
| `mergeable` | `specification-source` (`PROJECT.md`, `REQUIREMENTS.md`), `decision-file` (`decisions/DNNN-*.md`), `architecture-detail`, `v1-checklist`, `unclassified-markdown` (p. ej. `HARNESS_COMMANDS.md`, `UI_*.md`), `alias-conflict` |
| `historical` | `archive-phase`, `archive-phase-renumber` (`phase-N` → `phase-NNN`), `archive-phase-conflict`, `archive-other`, `v1-foundation` (`BRIEF.md`, `PROJECT_PROFILE.md`), `v2-folder-readme`, `research` |
| `foreign` | `previous-harness` (`.harness/**`), `root-markdown` (p. ej. `CHANGELOG.md`), `docs-other` y `flows-other` (no Markdown) |

Un alias nunca ocupa un destino existente ni compartido: si el canónico ya existe o dos alias apuntan a él, todos
pasan a `mergeable` con `alias-conflict`. La renumeración del archivo se resuelve por carpeta: si `phase-NNN` ya existe
o dos carpetas apuntan a la misma, pasan a `archive-phase-conflict` sin destino. El campo `canonical` es el documento
que corresponde a la entrada cuando es inequívoco; los movimientos los calcula T010.

## Origen, fases e instrucciones

- Señales: ReferenceProject (`.harness/`, runs, `PROJECT.md`, `REQUIREMENTS.md`, archivo sin STATE salvo `phase-000`, que en
  v1/v2 guarda la definición), v1 (`BRIEF`, `PROJECT_PROFILE`, `DELIVERY_CHECKLIST`) y v2 (`decisions/`,
  `architecture/`, `research/`). Un único origen con señales lo determina; varios dan `mixed`; ninguno, `unified` si
  están los once documentos de D088 o `unknown` (candidato al Flujo B).
- ROADMAP: `## P001 — …` o `## Phase 001 — …`, con duplicados. STATE: `phase:` del frontmatter (ReferenceProject) y
  `## Fase activa — PNNN`. NEXT_STEPS: código del título y fases de las tareas. Archivo: carpetas `phase-N` con sus
  archivos y si tienen STATE. Las fases se informan tal como se detectan; reconciliarlas es de T011.
- Instrucciones: AGENTS (≤60 líneas) y CLAUDE/GEMINI (≤15) con bytes, líneas y `within_limit`.
- Bloques: los marcadores `harness-local:managed-*` de cada Markdown; unos marcadores inválidos o un Markdown no UTF-8
  son un diagnóstico de la entrada, no un bloqueo.

## Verificación

Resultados en [STATE](../STATE.md#fase-activa--p008-contrato-documental-unificado-cierre-de-fase-e-importación-de-proyectos).
Las pruebas fijan la clasificación completa de los tres orígenes, sus señales, fases, instrucciones, bloques y runs;
comprueban que releer da el mismo inventario y que el árbol completo, `.git` incluido, no cambia (modo, tamaño, mtime
y hash), que la huella no depende de la raíz ni del commit y sí de los runs, que solo se invocan `rev-parse`,
`status`, `ls-tree` y `cat-file` con hooks y fsmonitor desactivados, los rechazos (sin Git, sin commits, HEAD vacío,
cambios, archivo sin seguimiento, raíz que no es el nivel superior) y que los enlaces no se siguen.

No se ejecutó el harness sobre este repositorio, ni proveedores, smokes, push o publicación. ReferenceProject solo se leyó
(estructura de `docs/`, encabezados de ROADMAP y STATE y reglas de `.gitignore`) para modelar el fixture sintético.

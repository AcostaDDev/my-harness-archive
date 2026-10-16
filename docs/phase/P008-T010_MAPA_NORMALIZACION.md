# P008-T010 — Flujo A: mapa de normalización determinista

Fecha: 2026-10-16. Base: D088 punto 10 e inventario de D096. Decisión: [D097](../DECISIONS.md#d097--p008-t010-mapa-de-normalización-del-flujo-a).

## Entrega

- `core/project_normalization.py` (puro, sin disco, Git ni SQLite): `build_map(inventory, contents)`,
  `materialize(map, contents)`, `compose_decisions`, `active_phase` y `snapshot_contents`. Formato
  `harness-local/import-map/1`, huella `map_sha256` que incluye `inventory_sha256`.
- `tests/product/test_project_normalization.py`: 13 casos con los tres orígenes sintéticos de T009 (importados de
  su prueba, sin fixtures en el árbol) y casos sintéticos en memoria para conflictos, fases y decisiones.

Sin adaptador, API, UI, SQLite ni migraciones: las rutas de la tarea son `core/**`, y el mapa es un valor que se
recalcula del inventario y de sus bytes. T011 lo congela con la conversación y T012 lo aplica.

## Entrada y comprobaciones

`build_map` exige el formato del inventario y su huella, y los bytes de cada entrada leída con el SHA-256 del
inventario; si falta uno o difiere, `ImportMapError`. Las entradas bloqueadas (enlaces, submódulos, no leídas) no se
mueven: siguen en su sitio y en `blockers`.

## Reglas

| Regla | Entrada (regla del inventario) | Destino |
|---|---|---|
| `rename-alias` | `alias-case`, `alias-root-document`, `alias-name` (`DECISSONS.md`), `alias-adr` | el canónico |
| `rename-data-model` | `architecture/data-model.md` | `DDBB-DIAGRAM.md` |
| `archive-renumber` | `archive/phase-N/…` | `archive/phase-NNN/…` |
| `retire-v1-foundation` | `BRIEF.md`, `PROJECT_PROFILE.md` | `archive/phase-000/<ruta bajo docs>` |
| `retire-v2-readme` | `decisions/`, `architecture/`, `research/` `README.md` | `archive/phase-000/<ruta bajo docs>` |
| `phase-artifact-active` | `research/**` o archivo de la raíz de `docs/` que empieza por `PNNN`, de la fase en curso | `docs/phase/<ruta bajo research o nombre>` |
| `phase-artifact-archived` | igual, de una fase con carpeta de archivo distinta de la activa | `archive/phase-NNN/<ruta>` |
| `archive-decision` | `decisions/DNNN-*.md` válido y de número único | `archive/phase-000/decisions/…` |
| `decision-sections` (composición) | las decisiones archivadas, por número | `DECISIONS.md` |

Todo movimiento conserva los bytes. Lo que se conserva en su sitio (`kept`): canónicos, flujos, `docs/phase/**` y
el archivo de tres dígitos.

**Fase de un artefacto.** La fase activa solo existe si STATE (frontmatter o encabezado) y NEXT_STEPS (título y
tareas) coinciden en un único código. El código del artefacto es el único `PNNN` de su ruta bajo `research/`, o el
prefijo del nombre en la raíz de `docs/`. Varias fases, ninguna, o una fase que no es la activa ni tiene archivo:
`phase-unknown`. Las rutas conservan el componente con el código, así que nunca ocupan `STATE.md`, `NEXT_STEPS.md`,
`REVIEW.md` ni `SUMMARY.md`, que el cierre reserva (D091).

**Decisiones.** Una decisión entra como sección si su primera línea es `# DNNN — título` con el número del nombre,
es UTF-8, no tiene otros encabezados de nivel 1 o 2 fuera de bloques de código ni marcadores gestionados
(`decision-unparsed` si no). La sección es el archivo con un `#` delante (el título pasa a nivel 2) y salto final si
faltaba. La composición es la base intacta, más una línea en blanco y la sección por cada decisión en orden
numérico. Base: el `DECISIONS.md` existente, el alias que se renombra a él o, si no hay ninguno, una plantilla mínima
con el bloque `managed-decisions` vacío. Si el destino depende de un alias en conflicto o la base no se puede leer
(UTF-8, bloques, numeración), `decision-base`. Un número repetido entre archivos (D003 y D0003 cuentan igual) o ya
presente en la base, `decision-duplicate`. El original se archiva por bytes en `phase-000`; si ese destino choca, la
sección no se compone. El índice gestionado no se recalcula aquí: lo regenera el commit (T012).

**Conflictos.** Un destino no puede coincidir, sin distinguir mayúsculas, con ninguna ruta del árbol original salvo
su propio origen (renombrado solo de mayúsculas), con otro destino, con un archivo que sería su directorio ni con un
directorio existente. Una sola pasada basta porque la ocupación se mide contra el árbol original; no hay cadenas. Lo
que choca va a `review` con `target-conflict` y la regla y destino que no se aplicaron.

## Salida

`moves` (regla, origen, destino, hash y tamaño), `compose`, `kept`, `review` (ruta, motivo, clase, regla del
inventario, canónico y diagnóstico), `foreign` (para el usuario), `blockers`, `missing` (documentos de D088 que el
árbol resultante no tiene, para los borradores de T011) y `tree`: el árbol documental completo tras el mapa, con el
origen y la operación de cada ruta. `materialize` devuelve los bytes de ese árbol y comprueba cada hash.

Motivos de `review`: `merge-proposal` (fuentes de SPECIFICATION, detalle de arquitectura, checklist v1, Markdown sin
clasificar), `alias-conflict`, `archive-conflict`, `archive-unrecognised`, `phase-unknown`, `decision-unparsed`,
`decision-duplicate`, `decision-base` y `target-conflict`.

| Origen sintético | Movimientos | Composición | Revisor | Faltan |
|---|---|---|---|---|
| ReferenceProject | `DECISSONS.md` → `DECISIONS.md` | — | PROJECT, REQUIREMENTS, HARNESS_COMMANDS, UI_REDESIGN | GEMINI, SPECIFICATION, DDBB-DIAGRAM |
| v1 | BRIEF y PROJECT_PROFILE → `phase-000` | — | DELIVERY_CHECKLIST | AGENTS, CLAUDE, GEMINI, SPECIFICATION, ARCHITECTURE, ROADMAP, DDBB-DIAGRAM |
| v2 | data-model → DDBB-DIAGRAM; tres README y D001 → `phase-000` | D001 en DECISIONS | `architecture/checkout.md`, `research/spike.md` | AGENTS, GEMINI |

## Verificación

Resultados en [STATE](../STATE.md#fase-activa--p008-contrato-documental-unificado-cierre-de-fase-e-importación-de-proyectos).
Las pruebas fijan el mapa completo de los tres orígenes, que releer y otra raíz dan el mismo mapa y huella sin tocar
el checkout ni `.git`, que cada movimiento conserva los bytes y cita su regla, que ningún destino coincide con una ruta
existente u otro destino (también por mayúsculas y por directorio), las fases de los artefactos, la composición en
orden numérico con sus rechazos, la plantilla y la base en conflicto, y los rechazos por bytes o huella distintos.

No se ejecutó el harness sobre este repositorio, ni proveedores, smokes, push o publicación. ReferenceProject solo se leyó
(listado de `docs/` en HEAD) para confirmar que no tiene `research/` ni artefactos con código de fase.

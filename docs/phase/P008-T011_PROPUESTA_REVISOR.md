# P008-T011 — Flujo A: propuesta del revisor

Fecha: 2026-10-16. Base: D088 punto 10, D075 (conversaciones H6.5), inventario de D096 y mapa de D097. Decisión:
[D098](../DECISIONS.md#d098--p008-t011-conversación-de-importación-con-borradores-privados).

## Entrega

- `core/engine/import_conversation.py` (puro): `frozen_source`, `identity`, `turn_context` (lo que congela un turno),
  `observation` (lo que no puede cambiar durante él) y `readiness` (bloqueos y avisos de la vista previa).
- `storage/import_drafts.py`: área privada `import-drafts/<conversación>/` junto a la base SQLite, con la interfaz del
  lector de la definición (`inspect_definition`, `write_draft`) y su CAS; `read_source` (árbol de HEAD con el
  adaptador de T009) y `observe`.
- `storage/planning.py`: tipo `project_import` (alta con inventario y mapa congelados, turnos, borradores, aplicar,
  editar, aplazar y `import_status`). `core/engine/definition.py`: el turno usa la plantilla nueva con el rol y el
  esquema `definition`. `core/engine/templates/import-project.md`: instrucciones del revisor.
- Migración `0019_import_conversations` (`planning_conversations.source`), `purpose = 'project_import'` en runs y
  métricas, observación del turno en `services/managed.py`.
- API: `kind = 'project_import'` en las rutas de planificación, `source` en la lectura de la conversación y
  `GET /api/managed/projects/{p}/planning/{c}/import`. OpenAPI y tipos regenerados.
- `tests/product/test_import_conversation.py`: 17 casos con los orígenes sintéticos de T009.

## Contexto congelado de un turno

| Clave | Contenido |
|---|---|
| `source` | Origen, HEAD, carpeta de documentos, huellas de inventario y mapa, fase activa, señales, fases detectadas, tamaño de las instrucciones, bloques gestionados y runs legacy |
| `map` | `moves`, `kept`, `review`, `foreign`, `blockers`, `missing` y la composición de DECISIONS sin bytes |
| `sources` | Texto íntegro de cada Markdown UTF-8 del árbol resultante fuera de `archive/`, con origen, operación y hash |
| `listed` | El resto del árbol (archivo, no Markdown, no leído) por ruta, origen y hash |
| `drafts`, `user_edits` | Borradores del área con hash y contenido; diferencias frente a lo que conoce el harness |
| `allowed`, `limits`, `template_defaults` | Rutas admitidas, límites de líneas de D088 y contenido por defecto de la plantilla |

Textos y borradores suman 2 MiB como máximo; si no, el turno no se encola. Lo observado antes y después de invocar es
`{inventory_sha256, drafts, invalid}`.

## Bloqueos de la vista previa (`readiness`)

Turno pendiente; checkout ilegible o con otra huella; entradas bloqueadas del inventario (enlaces, submódulos, no
leídas); borradores inválidos; preguntas bloqueantes sin responder ni aplazar; documentos de D088 que no están ni en
el mapa ni en los borradores (salvo los de la plantilla); AGENTS de más de 60 líneas o CLAUDE/GEMINI de más de 15, se
hayan importado o redactado; bloques gestionados en un documento ajeno; DECISIONS con numeración inválida. Avisos:
documentos que completaría la plantilla, entradas del mapa en revisión, archivos ajenos y pendientes del revisor.

| Origen sintético | Sin turnos | Tras aplicar borradores |
|---|---|---|
| ReferenceProject (sin runs) | AGENTS 70 líneas y CLAUDE 18 (bloqueos); SPECIFICATION y DDBB faltan | Listo al responder o aplazar la pregunta bloqueante |
| v1 | Faltan SPECIFICATION, ARCHITECTURE y ROADMAP | Listo con esos borradores e instrucciones |
| v2 | Listo: AGENTS y GEMINI saldrían de la plantilla; `checkout.md` y `spike.md` como avisos | Listo con AGENTS redactado |

## Verificación

Resultados en [STATE](../STATE.md#fase-activa--p008-contrato-documental-unificado-cierre-de-fase-e-importación-de-proyectos).
Las pruebas fijan: inventario y mapa congelados en `source`; contexto con el árbol resultante (DECISSONS ya
renombrado, PROJECT íntegro, archivo y `.harness` solo listados); rol `definition`, plantilla `import-project` y sin
`project_instructions`; checkout byte a byte igual tras turnos, aplicaciones y ediciones; área 0700; preguntas que
bloquean hasta aplazarlas o responderlas; ediciones del usuario congeladas en el turno siguiente; v1 y v2 hasta la
puerta de la vista previa; FAILED sin reintento con rutas no admitidas (`docs/PROJECT.md`, código, archivo) o salida
fuera de esquema; respuesta descartada si el agente escribe en el checkout o en el área; checkout sucio o con otro
commit (también tras encolar: no se invoca); rechazos al crear; CAS y rutas del área; límite de tamaño; guardia D027
con runs legacy; y el recorrido HTTP completo.

## Límites y preguntas para T012

- **Guardia D027.** Un checkout con `.harness/runs` sin activar rechaza los turnos. Activar el modo gestionado escribe
  `.harness/managed-mode.json`, que deja el checkout sucio salvo que esté ignorado, y el inventario exige un checkout
  limpio. El orden entre ambas operaciones debe decidirse en T012 (pregunta para el usuario).
- **Coherencia de fase.** No se comprueba que STATE, NEXT_STEPS y ROADMAP resultantes coincidan en la fase activa; es
  criterio de T012.
- **Entradas en revisión.** Las que no cubre un borrador quedan como aviso; su destino (archivo en `phase-000` u otro)
  lo fija la vista previa de T012.
- Sin UI propia: la UI de planificación filtra por `phase_planning`; la importación se usa por API hasta T012.

No se ejecutó el harness sobre este repositorio, ni proveedores, smokes, push o publicación. ReferenceProject no se leyó.

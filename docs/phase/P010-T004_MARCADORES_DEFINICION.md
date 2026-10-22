# P010-T004 — Marcadores opcionales de la definición

Fecha: 2026-10-22. Base: `4b99f05`. Decisión:
[D146](../DECISIONS.md#d146--p010-t004-marcadores-opcionales-en-la-definición).
**Estado: implementado y verificado offline** con SQLite y Git temporales y agentes falsos. Sin migración, API,
tipos generados ni cambios del motor. Sin proveedores, smokes, servicios ni QA visual.

## 1. Observación de partida

En P009-T007 ([evidencia](../archive/phase-009/P009-T007_CREACION_DJANGO.md#72-definición-con-revisor-codex), D127)
Codex respondió el primer turno de una carpeta nueva sin borradores y con una pregunta bloqueante: pedía «el contenido
actual y los marcadores gestionados» de STATE, NEXT_STEPS, ROADMAP y DECISIONS. La plantilla `define-project` decía
«Keep the managed markers … exactly where the drafts have them», sin aclarar que no había borradores ni que los
marcadores son opcionales. La aceptación ya lo admitía: `replace_block` añade al final el bloque que falta.

## 2. Qué se entrega

| Pieza | Cambio |
|---|---|
| `core/engine/templates/define-project.md` | Sustituye la frase de marcadores por dos párrafos: sin borradores en el contexto se redacta desde el brief y la conversación, sin pedir contenido ni marcadores previos; la definición solo crea documentos y el código figura como planificado. Los marcadores son opcionales y nunca hace falta añadirlos; la aceptación regenera los bloques y añade los que falten; si existen, se conservan por parejas y no se ponen en otros documentos. |
| `frontend/src/pages/Planning.tsx` | En la definición, con la carpeta sin borradores, un aviso explica que no hacen falta archivos previos y que los marcadores son opcionales. El aviso del editor de borradores deja de decir «No borres sus marcadores»: conservar cada pareja completa o quitarla entera; el bloque ausente se añade al final. |
| `tests/product/test_definition.py` | `test_new_folder_drafts_without_markers_get_their_blocks_appended`. |
| Documentación | D146, [flujo de definición](../flows/project-definition.md), STATE y NEXT_STEPS. |

Lo que no cambia: documentos obligatorios D088, bloqueos de aceptación (marcador parcial o de otro documento),
confirmación por contenido y CAS, `import-project` y `onboard-project`, que parten de un origen con contenido.

## 3. Versionado y prompts congelados

La plantilla incorporada se identifica por `builtin-1:` + SHA-256 de su texto, así que el cambio produce una identidad
nueva sin tocar código de versionado. Cada turno guarda su catálogo (`prompt_catalog_json`) y el snapshot del prompt
renderizado: los turnos anteriores siguen leyendo la plantilla con la que se invocaron
(`test_unified_prompts_retire_old_folders_without_rewriting_frozen_catalogs` cubre catálogos antiguos). Una versión
de `define-project` activada desde el editor de prompts tiene prioridad y no cambia; el editor muestra la incorporada
nueva como versión disponible. Ningún test ni documento fijaba el hash anterior.

## 4. QA con datos sintéticos

El test nuevo recorre las dos situaciones con brief y borradores sintéticos:

- **Carpeta nueva.** El contexto congelado del primer turno tiene `drafts == []` y el prompt renderizado incluye la
  guía de carpeta nueva y la de marcadores opcionales. El revisor falso propone los borradores sin ningún marcador.
- **Carpeta con borradores.** Tras aplicarlos, el segundo turno recibe los nueve borradores y la instrucción de
  conservar las parejas existentes.
- **Aceptación.** La vista previa queda lista sin bloqueos: STATE, NEXT_STEPS, ROADMAP y DECISIONS salen como
  `draft+blocks`, empiezan por el texto del borrador y terminan en su bloque regenerado (siguiente tarea P001-T001);
  README y SPECIFICATION quedan idénticos. El commit raíz se completa y P001 queda ACTIVE sin deriva documental.

Los casos con marcadores en su sitio, parciales o en otro documento siguen cubiertos por
`test_empty_folder_to_root_commit_with_p001_and_phase_000` y `test_acceptance_blockers_are_explicit_and_fail_closed`.

## 5. Verificación

| Comprobación | Resultado |
|---|---|
| `pytest -q` (paralelo) | 1650 pasan, 2 omitidos, 121 subtests |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 12 pasan |
| `node --test frontend/tests/*.test.mjs` | 82 pasan |
| `npm --prefix frontend run build` (incluye `tsc --noEmit`) | correcto; aviso de tamaño de chunk ya conocido |
| `alembic upgrade head` y `alembic check` en una SQLite temporal | sin operaciones nuevas |

`alembic check` sin `HARNESS_DATABASE_URL` apunta a la base local de desarrollo, que no está en `head`; no se migra.
Sin regeneración de OpenAPI ni tipos: la API no cambia.

## 6. Límites

- No se ha comprobado con un revisor real que la nueva redacción evite la pregunta bloqueante: no hay autorización
  para invocar proveedores. La guía queda acreditada en el prompt renderizado, no en el comportamiento de un modelo.
- QA visual no realizado, por decisión del usuario: el aviso de la UI se cubre con tipos y build.

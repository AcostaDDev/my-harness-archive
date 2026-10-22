# P010-T005 — Evidencia de una fase cerrada

Fecha: 2026-10-22. Base: `3e28b2e`. Decisión:
[D147](../DECISIONS.md#d147--p010-t005-evidencia-histórica-de-una-fase-cerrada).
**Estado: implementado y verificado offline** con Git y SQLite temporales y agentes falsos. Sin migración ni
tablas nuevas. La API añade un campo de lectura y se regeneran OpenAPI y los tipos. Sin proveedores, smokes,
servicios ni QA visual. No se lee ni modifica el estado operativo del Django hijo.

## 1. Observación de partida

Al consultar P001 cerrada del hijo de P009 ([REVIEW](../archive/phase-009/REVIEW.md)), la página mostraba STATE,
NEXT_STEPS, ROADMAP y DECISIONS como «cambiados desde la base adoptada». La causa es que la lectura de una fase
comparaba siempre los documentos vivos con `phase.documents`. Esa base es la del READY; el cierre la deja intacta y
después renueva esos documentos. La página de documentos repetía la deriva y decía que el check no quedaría listo.
Además, una fase cerrada no mostraba su check: `ready` solo existe mientras la fase está READY_TO_CLOSE o CLOSING.
Con sucesora ya había un aviso neutro. Sin sucesora, el caso del hijo, se presentaba como atención.

## 2. Qué se entrega

| Pieza | Cambio |
|---|---|
| `storage/phases.py` | `expected_documents`: base adoptada, renovación del cierre y ediciones o exportaciones COMMITTED posteriores, encadenadas por `before_sha256`. `closure_view`: cierre o abandono, check READY y su resultado, base (head, evidencia, documentos), tag, motivo, commit, archivo y clasificación `renewed`/`changed`/`archive_altered`. `closure_files` y `get(..., archive_documents)`. |
| `storage/documents.py` | `status` compara con `expected_documents`: igual que antes en fases abiertas; tras cerrar, con lo que dejó el cierre. |
| `api/managed.py`, `api/schemas.py` | `GET /phases/{id}` lee de disco cada archivo del archivo y devuelve `closure` (`PhaseClosureRead`); null en fases abiertas. OpenAPI y `api.generated.ts` regenerados. |
| `frontend/src/Phases.tsx` | Fase terminada: enlace al archivo, commit, integridad del archivo, renovados (esperados), deriva real o aviso de sucesora. El check muestra el resultado histórico y los criterios. Se ocultan «Adoptar documentos actuales» y «Cerrar fase». |
| `frontend/src/pages/Docs.tsx` | Con la última fase terminada, la deriva remite al cierre y no habla de un check pendiente. |
| Tests | Cuatro casos nuevos en `test_phase_closure.py`; el HTTP de cierre comprueba `closure`. `World.get` lee el archivo como la API. |
| Documentación | D147, [flujo del ciclo de fase](../flows/phase-lifecycle.md#consulta-de-una-fase-cerrada-p010-t005), STATE y NEXT_STEPS. |

`documents.drift` conserva su significado (frente a la base adoptada) para no cambiar el contrato existente. La
presentación de una fase terminada usa `closure`.

## 3. Lo que no cambia

- El check, el READY y su vínculo, la autorización de cierre y la adopción de documentos. Una fase abierta sigue
  mostrando deriva frente a su base, READY obsoleto y la acción de cierre retirada si los documentos cambian.
- `phase.documents` de una fase cerrada no se reescribe: sigue siendo la base del READY, visible como histórica.
- Un cierre anterior a D088, sin vista previa sellada, muestra su check y su base, pero sin archivo ni renovación
  esperada: sus documentos vivos se comparan con la base adoptada, como antes.

## 4. Casos sintéticos

| Caso | Test | Acredita |
|---|---|---|
| Fase abierta | `test_open_phase_has_no_closure_and_keeps_its_guards` | Sin `closure`; un cambio de STATE es deriva, deja el READY obsoleto, retira `close` y aparece en documentos. |
| Cerrada sin sucesora | `test_closed_phase_without_successor_separates_renewal_from_real_drift` | Resultado y base del check iguales al READY mostrado antes de cerrar; base adoptada intacta; renovados esperados y sin deriva en documentos. Una edición confirmada posterior sigue siendo esperada. |
| Deriva real | el mismo test | Un NEXT_STEPS editado fuera del harness aparece en `changed` y en documentos. Un SUMMARY alterado y un STATE borrado del archivo aparecen en `archive_altered`. Estado CLOSED y acciones intactos. |
| Cerrada con sucesora | `test_closed_phase_with_successor_leaves_live_documents_to_it` | `changed` es null y la deriva viva se atribuye a P002 en documentos. |
| Abandonada | `test_abandoned_phase_shows_its_closure_without_check` | `closure` sin check ni tag, con archivo íntegro, base y motivo. |
| HTTP | `test_http_closure_and_confirmed_plan_use_the_current_protocol` | La respuesta valida `PhaseClosureRead` y lee el archivo de disco. |

## 5. Verificación

| Comprobación | Resultado |
|---|---|
| `pytest -q` (paralelo) | 1654 pasan, 2 omitidos, 121 subtests |
| Tras ajustar la lectura de cierres anteriores a D088: fases, cierre, documentos, exportación, definición y API gestionada | 207 pasan |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 12 pasan |
| `node --test frontend/tests/*.test.mjs` | 82 pasan |
| `export_openapi.py` y `generate:types` | regenerados; solo añaden `closure`, `PhaseClosureRead` y `PhaseClosureCheckRead` |
| `npm --prefix frontend run build` (incluye `tsc --noEmit`) | correcto |
| `alembic upgrade head` y `alembic check` en una SQLite temporal | sin operaciones nuevas |

## 6. Límites

- QA visual no realizado; las páginas se cubren con tipos y build. No se ha mirado el hijo de P009: la observación se
  reproduce con datos sintéticos.
- Un commit hecho fuera del harness después del cierre sigue en `changed` aunque luego se confirme otra edición
  encima: la cadena solo acepta operaciones que parten de lo esperado.
- Leer el archivo cuesta una lectura de disco por archivo en cada consulta de la fase (como mucho 512 KiB cada uno,
  el límite del cierre).

# P008 — Segunda revisión de salida

Fecha: 2026-10-17. Código revisado: `a455ff9951f479994f42cee51d988cc605932da3` (T001–T017).
Decisión: [D107](../DECISIONS.md#d107--segunda-revisión-de-salida-de-p008).
La [primera revisión](P008_REVISION_SALIDA.md), sus reproducciones y su evidencia se conservan intactas.

## Dictamen

**Revisión completada; P008 todavía no está lista para cerrar.** H1–H3 de D104 están corregidos por
T016 y H4 por T017, pero un clon parcial con un objeto prometido ausente permite ejecutar el transporte
Git durante el inventario A (H5, reproducido abajo). Se corrigen aquí dos referencias adicionales en la
prosa de los flujos que todavía presentaban como pendientes capacidades implementadas.

La fase sigue activa: esta revisión no ejecuta el cierre, archivo, tag, registro del repositorio ni un check
READY del producto sobre él. El cierre y archivo son una operación posterior. La conclusión no certifica
recorridos con CLI reales, aislamiento del sistema operativo ni apariencia visual de la UI.

## Hallazgos anteriores y contraste independiente

| Hallazgo de D104 | Evidencia posterior y resultado |
|---|---|
| H1: inventario A ejecuta filtros | `check_filters` precede a `status` en `read_checkout`; `check_git` precede a captura/sellado y ejecución A/B. Reproducción original equivalente: rechazo, sin marcador y sin cambio del checkout/índice. La suite cubre `clean`/`process`, locales/includes, vista previa, confirmación, job y recuperación. Resuelto. |
| H2: bytes del commit distintos de los confirmados | `check_tree` lee y contrasta todos los blobs de `result_tree`; `seal` exige reproducir `proposed_tree`. `execute_documents` recaptura y recalcula antes de escribir, conservando CAS. La reproducción CRLF + `text eol=lf` se rechaza en la vista previa. Pruebas de originales/binarios y deriva posterior cubiertas. Resuelto. |
| H3: destino ignorado deja escritura parcial | `check-ignore` rechaza destinos nuevos antes de confirmar y ejecutar/reanudar. GEMINI ignorado bloquea la reproducción sin archivo escrito, operación, commit ni fase nuevos; las exclusiones locales posteriores también están cubiertas. Resuelto. |
| H4: referencias activas desactualizadas | F11/F18, `cli-12`, `d088-9`, ayudas CLI/registro/Home/Registry y mensajes de Prompts contrastados con código y D093/D095/D102/D105. Resuelto por T017. |

Se han leído las fronteras compartidas de `adapters/project_import.py`, `storage/project_import.py`,
`storage/onboarding_commit.py`, `core/engine/import_commit.py`, el despacho de `services/managed.py` y el
escritor de `adapters/git.py`. Se mantiene la intención sellada, la conciliación del mismo commit, la CAS
por documento, la adopción atómica y la cuarentena por versiones; las pruebas de recuperación A/B cubren
caídas antes/después de escritura, commit y registro. No se ha alterado ninguna intención histórica.

**Observación documental adicional, corregida en esta tarea:** `flows/documents.md` seguía llamando
«sin implementar» a las rutas y edición de instrucciones de T003; `flows/project-definition.md` hacía lo
mismo con los flujos A/B de T009–T015. Sus descripciones ahora citan D090/D100/D103 y enlazan las vías
implementadas. Solo cambia prosa vigente; los diagramas y los registros de entregas anteriores permanecen.

## H5 — Alta: el inventario A ejecuta lazy-fetch de objetos prometidos

`adapters/project_import.py:99` construye `Git`, sin `--no-lazy-fetch`; `_tree` llama a
`ls-tree -r -z -l --full-tree HEAD` (línea 29). En un clon parcial, consultar el tamaño de un blob
ausente provoca su recuperación implícita. La guardia de filtros de T016 no impide este transporte.

Reproducción offline: repositorio sintético con README versionado, remoto promisor local y su
`remote.origin.uploadpack` apuntando a un programa Python falso que solo crea un marcador y termina con
error. Se retira el objeto suelto del README para simular un blob prometido ausente; el checkout y el índice
siguen limpios. `read_checkout` llega a `ls-tree`, que ejecuta el programa antes de cualquier confirmación
o turno. El inventario acaba con `ValueError: invalid literal for int() with base 10: 'BAD'`, **después de
ejecutar el transporte**. La traza JSON acredita que el marcador aparece durante `ls-tree`, no en la preparación.

El control con el inventario B sobre el mismo repositorio no crea el marcador: `_InventoryGit` exige
`--no-lazy-fetch`. También rechaza el blob ausente, aunque su diagnóstico `BAD` debe manejarse de forma explícita.
No hubo red ni herramientas reales; el comando falso no devuelve objetos ni modifica el checkout/índice.

Incumple la lectura sin ejecución de D096 y SPECIFICATION §8; en un clon parcial real también podría iniciar
acceso a un remoto y materializar objetos durante una lectura. La corrección no requiere cambiar el diseño:
las lecturas A deben desactivar lazy-fetch de forma obligatoria, como B, desde el primer comando Git, y los
objetos ausentes deben rechazarse con un diagnóstico. Deben cubrirse los puntos de entrada de inventario y
conversación/vista previa que reutilizan ese lector, conservando filtros, D099, CAS, versiones y recuperación.
Se define P008-T018 para la corrección; no se modifica el producto durante esta revisión.

## Criterios de salida

| Criterio de ROADMAP | Evidencia y conclusión |
|---|---|
| Repositorio con D088, enlaces y diagramas | Instrucciones y documentos presentes, presupuestos y parsers correctos; enlaces comprobados y 20 diagramas válidos por parser/gramática. Las 35 tablas y sus 377 columnas coinciden con SQLAlchemy. Cumplido. |
| Plantilla, contratos, prompts y API unificados; creación v1 retirada | `test_documents`, `test_definition`, `test_prompts`, `test_storage_api`, `test_bootstrap` y `test_documentation_parity`; OpenAPI exportado contrastado y lectores históricos conservados, escrituras v1/transición retiradas. Cumplido. |
| Cierre READY, archivo, reinicio y commit conciliable | `test_phase_closure`: bytes originales/binarios, archivo completo, sucesora vacía, rechazo antes de efectos, recuperación del mismo tag/commit y plan posterior confirmado. Cumplido. |
| AGENTS congelado por intento | `test_project_instructions`: roles, hash, límites, cambios entre intentos, rechazo previo y versiones; excepciones documentadas de definition/import/onboarding. Cumplido. |
| Perfiles declarativos y Python/Django | `test_declared_profiles`: parser v4, compatibilidad, hashes/cuarentena y recorrido con validaciones/JUnit falsos. La confirmación del ejemplo en un proyecto Django real sigue fuera de esta fase offline. Cumplido. |
| Flujos A/B hasta commit confirmado y conservación | Fixtures ReferenceProject/v1/v2 y Django/TypeScript, D099, preservación de originales/código, idempotencia y recuperación; H1–H3 rechazados sin efectos. **Parcial: H5 impide acreditar la lectura sin ejecución en A con clones parciales.** |
| Checks offline y ningún proveedor sin consentimiento | Suite y checks indicados abajo; solo fixtures y herramientas sintéticos. La suite verde no cubre H5. |

## Evidencia reproducible

[Script posterior a T016](P008_REVISION_SALIDA_2_REPRO.py) y [salida JSON](P008_REVISION_SALIDA_2_EVIDENCE.json):

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python docs/phase/P008_REVISION_SALIDA_2_REPRO.py
```

Exige mediante aserciones el rechazo sin efectos de los escenarios H1–H3 de D104. Añade H5 y su control B:
**exit 0 acredita la reproducción del hallazgo, no su corrección**. El JSON identifica el commit revisado y
el hash del script histórico, que no se modifica.
La comparación del checkout incluye índice, refs y configuración local; excluye los objetos Git inalcanzables
que las vistas previas pueden materializar, como en D105. No se escriben documentos, refs ni índice real.
Las veinte regresiones de `test_import_git_boundary.py` amplían esos tres escenarios con includes,
confirmación, ejecución, deriva de atributos, originales/binarios y recuperación.

## Verificación

- Suite pytest completa: **1.365 pruebas y 121 subtests correctos**. Colección congelada en cuatro lotes
  disjuntos que cubren exactamente sus 1.365 nodeids: 342/341/341/341 OK, con 0/5/0/116 subtests y exit 0.
  Duraciones pytest: 345,83/347,53/345,83/346,42 s. Solo el aviso conocido de Starlette/httpx.
- 12 checks ligeros unittest, 75 pruebas Node y build del frontend (incluye `tsc --noEmit`) correctos;
  aviso conocido del build por chunks superiores a 500 kB. Sin assets versionados modificados.
- Alembic `upgrade head` y `check` sobre SQLite temporal: sin operaciones nuevas. No se migra la base del usuario.
- 35 Markdown activos/raíz/phase/flows con 395 enlaces relativos y anclas válidos. Instrucciones dentro de
  sus límites; STATE/base/NEXT_STEPS dentro de 24/12/48 KiB. Parsers: 107 decisiones, ocho fases y dieciocho
  tareas. Las 35 tablas y 377 columnas coinciden con el metadata SQLAlchemy.
- 20 diagramas Mermaid: siete ER y tres secuencias con `mermaid.parse`; siete flowcharts con su parser local
  y sanitización de etiquetas omitida; tres estados con gramática local sin procesar etiquetas mediante DOM.
  Esto valida sintaxis, no renderizado/apariencia.
- Reproducciones H1–H3 y H5/control B ejecutadas, JSON conservado y script validado sintácticamente;
  diff revisado y `git diff --check` correcto. No se añaden tests de la corrección aún no implementada.

Sin comprobación visual de UI ni renderizado DOM de diagramas; la validación Mermaid acredita sintaxis.
Sin Django/ruff/mypy reales, proveedores reales, smokes, push, publicación ni subagentes; sin modificar
configuración global ni ejecutar el harness sobre este repositorio. No cambia producto, esquema, API,
dependencias, prompts, versiones congeladas ni artefactos generados versionados.

## Continuidad

Siguiente: P008-T018, impedir lazy-fetch en las lecturas A y rechazar objetos ausentes con diagnóstico,
con pruebas de regresión sintéticas. Después se repetirá la revisión de salida. Cierre y archivo de P008
en una operación posterior y separada; ROADMAP no define una sucesora y no se inventa P009.

# P008-T020 — Escritor de importaciones con objetos locales

Fecha: 2026-10-19. Derivada de H7 de la [cuarta revisión de salida](P008_REVISION_SALIDA_4.md).
Decisión: [D112](../DECISIONS.md#d112--p008-t020-escritor-de-importaciones-con-objetos-locales).

## Resultado y motivo

El escritor A/B exige `--no-lazy-fetch` en todas sus operaciones Git, incluida la consulta del commit sellado
todavía ausente. Antes usaba `Git` después de una guardia con `LocalGit`: `_reachable` podía ejecutar
`upload-pack` al preguntar por ese commit futuro, incluso con todos los objetos del origen disponibles.
Ahora su ausencia permite crear localmente el commit confirmado sin invocar un transporte.

## Cambios

- `GitWorkspace.local_objects_only` selecciona `LocalGit` en su fábrica interna. `check_git` lo activa
  antes de captura/sellado y ejecución/reanudación A/B, también con puertos nuevos de la composición.
  Se cubren `run`/`code`, recapturas, cálculo/escritura del commit, comprobación de alcance y refresco del
  índice. Las instancias ajenas a importación conservan el comportamiento por defecto.
- `LocalGit.code` comprueba el soporte mediante `run(--version)` con el mismo ejecutable y flag antes de
  interpretar un código booleano. Un Git sin soporte falla con diagnóstico, sin tratar el error como
  ausencia normal del commit futuro ni recurrir a un modo menos restrictivo.
- `LocalGit.require_tree` comprueba los objetos de los árboles completos de HEAD y de la vista previa o
  intención sellada con `ls-tree -r -t` y `cat-file --batch-check`. Incluye árboles y blobs ajenos a la
  documentación, necesarios para capturar el checkout completo. Objetos ausentes y respuestas incompletas
  bloquean antes de escribir. La ausencia del propio árbol identifica la revisión requerida en el diagnóstico.
- La guardia mantiene filtros/includes, gitlinks, destinos ignorados y hashes de todos los documentos.
  No se recuperan objetos ni se cambia configuración para resolver un bloqueo. Restaurar los bytes
  sintéticos ausentes permite reanudar la misma intención, run y commit con una única fase adoptada.
- `document_layout = "d088-12"` congela el cambio y añade `d088-11` a las versiones incompatibles anteriores.
  La composición existente las rechaza antes de entregar puertos o escritor; no se reescriben intenciones,
  snapshots, historiales ni las reproducciones/JSON históricos de H5/H7. Sin cambios de esquema o API.
- SPECIFICATION, ARCHITECTURE, flujos A/B, STATE, NEXT_STEPS, ROADMAP e índice de decisiones actualizados.
  Se compacta el resumen activo de verificación de T012 con enlace a su registro íntegro para respetar
  el presupuesto de STATE; su evidencia de entrega no se modifica.

## Regresiones

`tests/product/test_import_writer_local_objects.py` añade 26 casos exclusivamente sintéticos:

- A/B con todos los objetos alcanzables de HEAD disponibles, remoto promisor local y `upload-pack` falso
  externo que solo crearía un marcador. Captura/sellado/confirmación y ejecución inicial usan el flag en
  todas las llamadas observadas de ambas APIs. No aparece el marcador ni cambian los bytes de configuración.
- Caídas antes del escritor, entre documentos, después del commit y antes del registro atómico. Tras
  confirmar detenido y reconfirmar, puertos nuevos concilian la misma intención/run/commit y una sola fase,
  sin más invocaciones de agentes. Un commit posterior también se concilia por `merge-base --is-ancestor`
  sin transportes; el índice final coincide con el árbol confirmado y el checkout queda limpio.
- Blob de código ajeno a la documentación, árbol del origen, blob documental sellado y árbol sellado ausentes:
  bloqueo del job y de su reconfirmación, sin transporte, objetos recuperados, bytes de checkout/índice/refs/
  configuración alterados ni fase adoptada. Restituir los bytes permite completar la intención original.
- Ejecutable Git falso sin soporte: rechazo de `run` y `code` y de vista previa, ejecución y reanudación
  A/B, sin fallback ni cambios de checkout/.git. La consulta booleana no oculta la incompatibilidad.
- Las suites existentes cubren H1–H6, limpieza, originales/binarios, hashes, destinos ignorados, D099,
  recorridos A/B válidos y recuperaciones posteriores a escritura/commit. Las pruebas de composición
  incluyen la cuarentena de `d088-11`; no se cambian contratos históricos para hacerlas pasar.

## Verificación

- `python3 -m unittest discover -s tests -p 'test_*.py'`: 12 checks correctos.
- Batería dirigida de objetos locales, frontera Git, submódulos, commit A e incorporación B: 106 pruebas
  correctas, sin fallos. Primera ejecución de las 26 regresiones nuevas: 24 correctas y dos fallos porque
  el árbol sellado ausente producía un diagnóstico genérico de Git. Se añadió el contexto del árbol
  requerido al diagnóstico y se revalidaron los dos casos: correctos. Solo el aviso conocido Starlette/httpx.
- Suite completa: **1.436 pruebas y 121 subtests correctos**, sin fallos. Colección congelada, cubierta
  exactamente por cuatro lotes disjuntos de 359 nodeids cada uno: 359/359/359/359 OK, con 5/0/116/0 subtests.
  Duraciones pytest: 332,77/332,76/332,76/348,38 s. Incluye las 26 regresiones nuevas tras corregir el
  diagnóstico y las expectativas de versión/cuarentena. Solo el aviso conocido Starlette/httpx.
- 40 Markdown activos/raíz/phase/flows: 442 enlaces relativos/anclas válidos; presupuestos de instrucciones,
  STATE/base/NEXT_STEPS correctos. Parsers del proyecto: 112 decisiones, ocho fases y veinte tareas.
- Cinco flowcharts de A/B aceptados por el parser Mermaid local, sin DOM/renderizado ni sanitización de
  etiquetas. La primera invocación necesitó vincular el objeto de datos al parser interno; la ejecución
  corregida no detectó errores de sintaxis. Diff revisado y `git diff --check` correcto.
- Sin Node/build/Alembic independiente: no cambian UI, API ni esquema. Evidencia histórica intacta.

## Límites y continuidad

Se mantiene la exclusión cooperativa de D105: las comprobaciones no aíslan frente a cambios concurrentes
arbitrarios del checkout/configuración. Las vistas previas válidas siguen pudiendo crear objetos locales
inalcanzables; los casos rechazados comparan todos los bytes del checkout y `.git` tras preparar el fixture.

Sin UI visual, Node/build/Alembic independiente (no cambian UI, API ni esquema), proveedores reales, smokes,
push, publicación, subagentes, registro ni ejecución del harness sobre este repositorio. Sin datos privados ni
configuración global modificada. El usuario autorizó el commit de desarrollo.

P008 sigue activa. Siguiente: nueva revisión de salida; cierre y archivo en una operación posterior separada.

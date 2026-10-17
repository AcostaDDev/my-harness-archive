# P008-T018 — Lecturas de importación con objetos locales

Fecha: 2026-10-17. Derivada de H5 de la [segunda revisión de salida](P008_REVISION_SALIDA_2.md).
Decisión: [D108](../DECISIONS.md#d108--p008-t018-lecturas-de-importación-sin-lazy-fetch).

## Resultado y motivo

El lector del Flujo A exige `--no-lazy-fetch` desde su primer comando Git, incluidos `rev-parse`, `config`,
`status`, `ls-tree -l` y `cat-file`. Un blob prometido ausente ya no autoriza un transporte ni una recuperación
implícita durante el inventario. La lectura se rechaza con diagnóstico antes de proponer documentos o sellar
un commit. Se comparten las garantías con B; no se ejecuta código del proyecto ni se edita configuración para
resolver la ausencia. La evidencia histórica de H5, su reproducción y su JSON permanecen intactos.

## Cambios

- `adapters/local_git.py` extrae la clase `LocalGit` de la frontera que B ya usaba. El flag es obligatorio,
  también con un Git antiguo que lo rechaza; no se sustituye por una variable que pudiera ignorarse.
  `project_onboarding._InventoryGit` conserva un alias para sus consumidores existentes, sin dependencias
  circulares ni necesidad de modificar el lector de conversaciones B fuera de las rutas de la tarea.
- `adapters/project_import.read_checkout` usa esa clase desde el primer comando. Normaliza los errores de
  lectura de HEAD, árbol, estado y blobs como errores de inventario. Sus consumidores existentes heredan
  la protección: creación de conversación, mensajes, observación del turno, estado, vista previa y confirmación.
- El lector de tamaños común distingue `BAD` o un blob sin tamaño de `-` en un submódulo. El diagnóstico
  identifica objeto y ruta; no hay `int('BAD')`. Lo usan A, B y `HeadSnapshot`, compartido con la exportación
  y vista previa B. El lector `cat-file --batch` común rechaza objetos ausentes y respuestas incompletas,
  sin devolver un prefijo parcial. La guardia de árboles sellados A/B utiliza la misma frontera local.
- `document_layout = "d088-10"` congela la corrección y deja en cuarentena composiciones anteriores, incluida
  `d088-9`, antes de efectos. La configuración local ya deriva su versión de la constante común; no necesita
  otra modificación. No cambia el formato del inventario o mapa, ni prompts, codec, adaptador CLI, esquema,
  API o dependencias. Las intenciones históricas y su conciliación no se reescriben.
- SPECIFICATION, ARCHITECTURE, flujos A/B, STATE, NEXT_STEPS y ROADMAP actualizados. El resumen activo de
  T008 se compacta con enlace a su registro original para mantener STATE dentro del presupuesto documental.
  Sin modelos ni migraciones: DDBB-DIAGRAM no cambia.

## Regresiones

`tests/product/test_import_local_objects.py` añade 18 casos con repositorios temporales y datos sintéticos:

- A/B, blob prometido ausente antes de `ls-tree -l` y después de listar, antes de `cat-file --batch`.
  Un `upload-pack` falso solo crearía un marcador: no llega a ejecutarse. Cada comando lleva el flag,
  el objeto sigue ausente y todos los bytes del checkout y de `.git` (incluidos objetos, índice, refs y
  configuración) coinciden con los anteriores, salvo la retirada deliberada del blob por el propio fixture.
- A: crear conversación, enviar un mensaje, consultar estado, vista previa y confirmar rechazan la fuente
  incompleta antes de agentes/captura/sellado/escritura. Sin jobs, conversaciones, operación, fase o commits
  nuevos; los agentes falsos no reciben peticiones adicionales. El estado muestra un bloqueo con diagnóstico.
- B: su vista previa rechaza el tamaño ausente mediante el lector de instantáneas compartido, antes de capturar
  o sellar. A/B también rechazan un árbol ausente sin transportar ni recuperar objetos.
- Cuatro respuestas batch ausentes o incompletas se rechazan sin resultados parciales. Git sin soporte del flag
  se rechaza en el primer comando de A/B, sin reintentar de forma menos restrictiva.

Las regresiones existentes conservan los casos válidos A/B hasta COMMITTED, D099, H1–H3, CAS y recuperación.
La prueba de configuración añade `d088-9` a las versiones anteriores que no reciben puertos/escritor.

## Verificación

- `python3 -m unittest discover -s tests -p 'test_*.py'`: 12 checks correctos.
- Primera batería dirigida de inventarios A/B, frontera Git y regresiones nuevas: 68 pruebas correctas.
  La batería final de objetos locales: 18 correctas, incluidos los casos añadidos después de esa primera pasada.
- Suite pytest completa, colección de 1.383 nodeids cubierta exactamente por cuatro lotes disjuntos:
  1.379 correctos y 121 subtests, con cuatro fallos iniciales. Tres eran los parámetros de la conciliación
  histórica que todavía fijaban `d088-9` como versión actual; ahora usan `DOCUMENT_LAYOUT`. El cuarto exigía
  un diagnóstico local para un árbol ausente en B; se precisó el mensaje. La suite ya estaba cargada cuando
  se corrigió ese mensaje, por lo que ese lote conserva su fallo inicial. Se revalidaron los archivos afectados
  en un proceso nuevo, sin fallos (resultado abajo). Los lotes duraron 272,00/259,83/280,09/295,22 s;
  resultados 345/345/345/344 correctos, con un fallo cada uno. Solo el aviso conocido de Starlette/httpx.
- Revalidación de los cinco archivos afectados (cierre histórico, inventario B, objetos locales, configuración
  y versiones): **128 pruebas correctas**, incluidos los cuatro casos inicialmente fallidos, en 117,70 s.
  Tras precisar el texto del helper compartido para no atribuir la protección local a consumidores de chat
  ajenos a esta tarea, se re-ejecutaron las **18 regresiones de objetos locales**, todas correctas (9,49 s).
  Los 1.383 nodeids de la colección quedan cubiertos por la suite y las revalidaciones; ningún fallo pendiente.
- 36 Markdown activos/raíz/phase/flows, 403 enlaces relativos y anclas correctos; instrucciones, STATE y
  NEXT_STEPS dentro de sus presupuestos. Cinco flowcharts de los flujos A/B aceptados por el parser Mermaid
  local; se omite sanitización de etiquetas/DOM/renderizado. El diagrama de estados existente no cambia.
- Diff revisado y `git diff --check` correcto. Sin Node/build ni Alembic independiente: no cambian UI, API ni
  esquema. Sin comprobación visual. Evidencia histórica de H5 sin modificar.

## Límites y continuidad

Las guardias siguen siendo cooperativas: no añaden aislamiento del sistema operativo ni certifican cambios
concurrentes arbitrarios de configuración. Un repositorio incompleto debe disponer de sus objetos locales antes
de importarlo; el lector no los recupera ni resuelve su ausencia. Las vistas previas completas pueden seguir
materializando blobs/árboles locales inalcanzables como en D105, sin cambiar refs ni el índice real.

Sin UI visual, Node/build/Alembic independiente (no cambia UI, API ni esquema), proveedores reales, smokes,
push, publicación, subagentes, registro o ejecución del harness sobre este repositorio. Sin datos privados ni
configuración global modificada. El consentimiento de la sesión incluye el commit de desarrollo.

P008 sigue activa. Siguiente: nueva revisión de salida; cierre y archivo en una operación posterior separada.

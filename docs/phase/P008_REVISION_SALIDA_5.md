# P008 — Quinta revisión de salida

Fecha: 2026-10-19. Código revisado: `7568215e3fc5d478d522db97194d1b4c2b1b83ec` (T020).
Decisión: [D113](../DECISIONS.md#d113--quinta-revisión-de-salida-de-p008).

## Dictamen

**Los siete criterios de salida de P008 están cumplidos en su alcance offline, sin nuevos bloqueos en esta
revisión.** H1–H7 mantienen sus garantías en las comprobaciones descritas abajo. En particular, H7 ya no
ejecuta el transporte falso cuando el escritor A/B pregunta por el commit futuro todavía ausente, ni al
reanudar con un puerto nuevo. Objetos necesarios ausentes y Git sin soporte bloquean antes de escribir.

P008 queda preparada para su cierre y archivo documental en una tarea separada; sigue activa hasta entonces.
Esta revisión no registra ni ejecuta el harness o un check READY del producto sobre este repositorio, ni crea
tag, archivo de fase o sucesora. ROADMAP no define una fase posterior.

## Hallazgos anteriores

| Hallazgo | Comprobación actual |
|---|---|
| H1: filtros del padre | Inventario rechazado sin filtro ejecutado ni bytes cambiados. Regresiones de `clean`/`process`, includes, vista previa, confirmación, ejecución y recuperación correctas. Resuelto en esos casos. |
| H2: bytes transformados | CRLF con `text eol=lf` rechaza la vista previa antes de escribir/adoptar. Regresiones de hashes, originales, binarios y deriva posterior correctas. Resuelto. |
| H3: destinos ignorados | GEMINI ignorado rechaza antes de confirmar/escribir, sin operación, fase o commit nuevos; la guardia se repite al ejecutar. Resuelto. |
| H4: referencias vigentes | F11/F18, `cli-12`, `local-config-4`, `d088-12`, ayudas de registro/serve, Home/Registry y Prompts alineados con T017–T020. Históricos conservados. Resuelto. |
| H5: objetos ausentes en lectores A/B | Blob prometido ausente bloquea con diagnóstico y todos los comandos observados llevan `--no-lazy-fetch`. Sin transporte, objeto recuperado ni bytes cambiados. Resuelto. |
| H6: filtros en submódulos | Dieciocho escenarios rechazan antes de `status` o crear conversación, dentro/fuera de `docs/`, filtros `clean`/`process` directos/por include y gitlinks solo en índice. Sin filtros invocados ni bytes cambiados. Regresiones de consumidores y recuperación también correctas. Resuelto. |
| H7: lazy-fetch del escritor A/B | Cuatro escenarios nuevos de ejecución/reanudación permiten crear localmente el commit futuro. Ambas APIs del escritor usan el flag; sin marcador de transporte ni cambios de configuración. Ocho escenarios de objetos necesarios ausentes y dos de Git sin soporte rechazan sin fallback. Resuelto. |

Se han contrastado inventarios, `LocalGit`, `GitWorkspace`, `check_git`, vistas previas/sellado, despacho del
job y recuperación compartidos A/B. La guardia vincula cada escritor nuevo al modo local antes de capturar,
sellar o escribir. La consulta booleana comprueba el soporte mediante `run(--version)` antes de interpretar
la ausencia del commit. Se mantienen filtros/includes, gitlinks antes de inspeccionar el checkout, destinos
ignorados, hashes, D099, CAS, intención previa, adopción atómica y cuarentena de versiones anteriores.

## Comprobación nueva de H7

Origen A tipo ReferenceProject sintético y B Django sintético, ambos con un archivo binario ajeno a la documentación.
Los revisores falsos solo proponen borradores privados; no se ejecuta código ni herramientas de los proyectos.

- Se comprueba que todos los objetos alcanzables del origen están disponibles. Se configura exclusivamente
  el fixture con un remoto promisor local y `upload-pack` falso que solo crearía un marcador y saldría con error.
- Se trazan `Git.run` y `Git.code` durante vista previa, sellado, escritura y conciliación. Todos los comandos
  llevan `--no-lazy-fetch`, incluidas las consultas al commit esperado aún ausente. No aparece el marcador.
- Ejecución inicial y reanudación tras caída anterior al escritor, con puertos `GitWorkspace` nuevos, terminan
  DONE/COMPLETED. HEAD e índice coinciden con el commit/árbol sellados; checkout limpio, misma intención/run,
  una sola fase adoptada, sin invocaciones adicionales del revisor ni cambios de configuración.
- Se retira, por separado, un blob de código del origen, su árbol, un blob documental sellado o el árbol sellado.
  Los ocho escenarios A/B bloquean el job y la reconfirmación, sin modificar bytes del checkout o `.git`,
  recuperar el objeto ni adoptar una fase. Restituir únicamente los bytes sintéticos retirados permite
  completar la intención original sin transporte.
- Un Git falso sin soporte rechaza `run` y `code` tras una sola invocación con diagnóstico; nunca entra en
  el fallback. Las regresiones de T020 cubren además vista previa/job/reanudación con ese ejecutable,
  caídas durante documentos, tras commit/antes del registro atómico y conciliación con un commit posterior.

## Criterios de salida de ROADMAP

| Criterio | Evidencia y conclusión |
|---|---|
| Este repositorio con D088, enlaces y diagramas | Documentos e instrucciones presentes, presupuestos y parsers correctos; enlaces y 20 diagramas comprobados. 35 tablas y 377 columnas coinciden con SQLAlchemy. Cumplido. |
| Plantilla, contratos, prompts y API unificados; creación v1 retirada | Código y suites de documentos/definición/prompts/bootstrap/API, OpenAPI idéntico y tipos/build correctos. Lectores históricos conservados. Cumplido. |
| Cierre READY, archivo, reinicio y commit conciliable | Suite de cierre/adopción: originales/binarios, archivo completo, sucesora vacía o ausente, rechazos, recuperación de tag/commit y plan posterior confirmado. Cumplido offline. |
| AGENTS congelado por intento | Roles, hashes, límites, cambios entre intentos, fallo previo y versiones; excepciones de definición/import/onboarding documentadas. Cumplido. |
| Perfiles declarativos y Python/Django | `local-config-4`, compatibilidad, hashes/cuarentena, JUnit y recorrido hasta commit con herramientas falsas. Ensayo Django real fuera del alcance de esta fase offline. Cumplido. |
| A/B hasta commit confirmado sin ejecución ni pérdida | Recorridos sintéticos, originales/código, D099, idempotencia, recuperación y las guardias H1–H7 correctos. Cumplido offline. |
| Checks offline y ningún proveedor sin consentimiento | Suite y checks siguientes correctos. Ningún proveedor real. Cumplido. |

## Evidencia reproducible

[Script nuevo](P008_REVISION_SALIDA_5_REPRO.py) y [JSON nuevo](P008_REVISION_SALIDA_5_EVIDENCE.json):

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python docs/phase/P008_REVISION_SALIDA_5_REPRO.py
```

Exit 0 exige H1–H3/H5–H7 corregidos, incluidos los rechazos y la recuperación de objetos locales de H7.
Reutiliza las funciones de guardias corregidas de revisiones anteriores, con un comprobador nuevo para H7;
no llama a las reproducciones históricas que exigen acreditar los fallos antiguos. H4 se contrasta por lectura.
Incluye HEAD revisado, Git y hash del script, más hashes de los ocho scripts/JSON históricos, contrastados
con HEAD y conservados intactos. H2/H3 permiten objetos locales inalcanzables de vista previa, como D105;
H5/H6 y rechazos de H7 comparan todos los bytes de checkout/`.git` después de preparar el fixture.

## Verificación

- Pytest completo: **1.436 pruebas y 121 subtests correctos**, sin fallos. Colección congelada cubierta
  exactamente por cuatro lotes disjuntos de 359 nodeids cada uno, con 5/0/116/0 subtests.
  Duraciones: 340,15/340,16/340,15/352,52 s. Solo el aviso conocido Starlette/httpx.
- 12 checks ligeros unittest, 75 pruebas Node, tipos y build correctos. Aviso conocido de chunks mayores
  de 500 kB; sin cambios de assets versionados, instalación de dependencias o actualización de npm.
- Alembic `upgrade head` y `check` sobre SQLite temporal: sin operaciones nuevas. OpenAPI generado en
  memoria idéntico al JSON versionado; sin arrancar servicio ni tocar la base del usuario.
- Paridad de datos: 35 tablas y 377 columnas idénticas al metadata. Veinte diagramas: siete ER y tres
  secuencias con `mermaid.parse`, siete flowcharts con su parser sin sanitización de etiquetas y tres
  estados con su gramática sin extracción/sanitización dependiente del DOM. Solo sintaxis; sin renderizado.
- 41 Markdown activos/raíz/phase/flows con 451 enlaces relativos/anclas válidos. Instrucciones y presupuestos
  correctos: STATE 24.017 bytes, base 3.374 y NEXT_STEPS 43.476. Los parsers reconocen 113 decisiones,
  ocho fases y veinte tareas. Diff revisado y `git diff --check` correcto.
- Script final ejecutado y hashes comprobados. Al prepararlo se adaptó el binario al helper de fixtures
  de texto y se admitió el diagnóstico de árbol ausente que llega desde la guardia anterior a `require_tree`.
  El comprobador temporal de paridad usa SQLite en archivo y combina las referencias abreviadas del ER
  con su declaración completa. Los ajustes no cambian el producto ni evidencia anterior.

## Límites y continuidad

Sin UI visual, renderizado DOM, Django/ruff/mypy reales, proveedores reales, smokes, push, publicación ni
subagentes. No se amplían los consentimientos previos. Contención cooperativa sin aislamiento frente a cambios
concurrentes arbitrarios del checkout/configuración; generación semántica de documentos sujeta a revisión humana.
Sin datos privados ni configuración global modificada. Sin cambios de producto, esquema, API, dependencias,
prompts, versiones congeladas, snapshots, intenciones o evidencia histórica; sin regenerar OpenAPI, tipos o assets.

Siguiente: cierre y archivo documental de P008 en una tarea separada; sin sucesora inventada y sin ejecutar
el harness sobre este repositorio. Esta revisión deja el dictamen y la continuidad, sin cerrar o archivar la fase.

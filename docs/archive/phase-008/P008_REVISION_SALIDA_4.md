# P008 — Cuarta revisión de salida

Fecha: 2026-10-19. Código revisado: `2815b5cbb5137e2d723e800a971b3e70fe7d2855` (T019).
Decisión: [D111](../DECISIONS.md#d111--cuarta-revisión-de-salida-de-p008).

## Dictamen

**P008 sigue activa y no está lista para cerrar por H7.** H1–H6 se mantienen resueltos en las comprobaciones
descritas abajo. H7 demuestra una ruta distinta a la lectura del inventario: el escritor Git compartido A/B
ejecuta un transporte por lazy-fetch al preguntar por un commit sellado que todavía no existe localmente.
No falta ningún objeto del origen y las importaciones llegan a COMPLETED después del efecto no autorizado.
Se define P008-T020 para corregir esa frontera; esta revisión no cambia el producto ni cierra o archiva la fase.

No se ha registrado este repositorio ni ejecutado un check READY del producto sobre él. La revisión manual,
la corrección del hallazgo y el cierre/archivo son tareas distintas. ROADMAP no define una sucesora.

## Hallazgos anteriores

| Hallazgo | Comprobación actual |
|---|---|
| H1: filtros del padre | La reproducción de inventario rechaza antes de `status`, sin marcador ni cambios. Regresiones de filtros `clean`/`process`, includes, confirmación y ejecución/recuperación en verde. Resuelto en esos casos. |
| H2: bytes transformados | CRLF con `text eol=lf` rechaza la vista previa antes de escribir/adoptar; regresiones de originales, binarios, hashes y deriva posterior correctas. Resuelto. |
| H3: destinos ignorados | GEMINI ignorado rechaza antes de confirmar/escribir, sin operación, fase o commit nuevos; comprobación reiterada al ejecutar. Resuelto. |
| H4: referencias vigentes | F11/F18, `cli-12`, `local-config-4`, `d088-11`, ayudas de registro/serve, Home/Registry y Prompts alineados con T017–T019. Históricos conservados. Resuelto. |
| H5: objetos ausentes en lectores A/B | El blob prometido ausente bloquea con diagnóstico y `--no-lazy-fetch` en todos los comandos observados, sin transporte ni bytes cambiados en checkout/.git ni objeto recuperado. Sus 18 regresiones y consumidores A/B pasan. Resuelto para esa ruta; H7 afecta al escritor posterior. |
| H6: filtros en submódulos | Dieciocho escenarios nuevos rechazan antes de `status` o crear conversación, dentro/fuera de `docs/`, filtros `clean`/`process` directos/por include y gitlinks solo en índice. Cero filtros invocados y todos los bytes intactos. Las 27 regresiones T019 cubren además consumidores, observaciones, gitdir separado, retirada del índice y recuperación A/B. Resuelto. |

Se han contrastado `LocalGit`, inventarios A/B, instantáneas de onboarding, `read_source`, creación/turnos/
estado, vista previa, sellado, despacho del job y escritor documental compartido. `check_submodules` precede
a `status` y al escritor, consulta solo HEAD/índice del padre y conserva el requisito de limpieza. D099,
CAS, confirmación por hashes, versiones, intención previa, adopción atómica y conciliación permanecen.
No se altera la evidencia histórica de H1–H6.

## H7 — Alta: el escritor A/B hace lazy-fetch del commit sellado ausente

`GitWorkspace._git` (`adapters/git.py:135`) crea `Git`, que no incluye el flag de `LocalGit`.
`execute_documents` llama a `_reachable` antes de escribir (`:428`) y finalmente a `execute` (`:464`),
que vuelve a comprobarlo (`:350`). `_reachable` (`:284`) pregunta con
`git.code("cat-file", "-e", "<expected_commit>^{commit}")`; el commit está calculado/sellado pero aún no
se ha escrito, por lo que su ausencia es normal. En un repositorio promisor, Git intenta recuperarlo y
ejecuta `upload-pack`. `Git.code` (`:74`) tampoco desactiva lazy-fetch.

La guardia del supervisor (`services/managed.py:201`) utiliza `LocalGit` para filtros/gitlinks/destinos/blobs,
pero el escritor que recibe después sigue usando `Git`. Completar los objetos del origen o aplicar las
guardias de inventario no evita la consulta de este identificador futuro.

Reproducción nueva, solo con Git/SQLite temporales:

- Origen A tipo ReferenceProject sintético y origen B Django sintético, sin ejecutar su código. Se crean conversación,
  borradores y confirmación con revisores falsos. El repositorio conserva **todos los objetos alcanzables de
  HEAD**, comprobados con `rev-list --objects` y `cat-file --batch-check` sin lazy-fetch; no se elimina ninguno.
- Configuración promisor local con URL al propio repositorio y `upload-pack` falso fuera del checkout. El
  programa solo añade una línea al marcador y termina con error; no tiene red ni entrega objetos.
- Vista previa/confirmación y control `LocalGit.code(cat-file -e <expected_commit>^{commit})` sin marcador.
  El control acepta que el commit futuro está ausente sin invocar transporte.
- Al ejecutar el job, la primera llamada trazada a `Git.code` es `cat-file -e` sobre ese mismo commit,
  **sin `--no-lazy-fetch`**, y el marcador ya aparece al retornar. Se repite la consulta antes del commit.
  En Git 2.50.1 del entorno, el transporte falso se invoca cuatro veces por escenario.
- Resultado en A/B, ejecución inicial y reanudación tras caída sintética anterior al escritor: job DONE,
  importación COMPLETED, HEAD igual al commit sellado, misma intención y una fase adoptada, sin invocaciones
  adicionales de agentes. Los archivos/refs/índice cambian por el commit confirmado; no se atribuye a H7
  pérdida documental, bytes alterados ni recuperación de objetos. El efecto acreditado es ejecutar el transporte.

Incumple la importación sin ejecución/transportes no autorizados de SPECIFICATION §8 y D100/D103/D108.
H5 mantiene su corrección en lectores; H7 es una ruta posterior en la comprobación de existencia del commit.
No se debe resolver recuperando objetos, cambiando la configuración del usuario o impidiendo la conciliación
normal cuando aún no se ha escrito el commit. T020 deberá evaluar la versión congelada, las llamadas `run`/`code`
del escritor de importación y su recuperación, manteniendo D099, CAS, hashes y el mismo commit.
Esta revisión no prescribe una implementación ni presenta H7 como corregido.

## Criterios de salida de ROADMAP

| Criterio | Evidencia y conclusión |
|---|---|
| Este repositorio con D088, enlaces y diagramas | Instrucciones/documentos presentes, presupuestos y parsers correctos; enlaces y 20 diagramas comprobados. 35 tablas y 377 columnas coinciden con SQLAlchemy. Cumplido. |
| Plantilla, contratos, prompts y API unificados; creación v1 retirada | Código y suites de documentos/definición/prompts/bootstrap/API, OpenAPI idéntico y tipos/build correctos. Lectores históricos conservados. Cumplido. |
| Cierre READY, archivo, reinicio y commit conciliable | Cierre/adopción y suite de `test_phase_closure`: originales/binarios, archivo completo, sucesora vacía o ausente, rechazos, recuperación de tag/commit y plan confirmado. Cumplido offline. |
| AGENTS congelado por intento | Roles, hashes, límites, cambios entre intentos, fallo previo y versiones; excepciones de definición/import/onboarding documentadas. Cumplido. |
| Perfiles declarativos y Python/Django | `local-config-4`, compatibilidad, hashes/cuarentena, JUnit y recorrido hasta commit con herramientas falsas. Ensayo Django real fuera de esta fase offline. Cumplido. |
| A/B hasta commit confirmado sin ejecución ni pérdida | Recorridos sintéticos válidos, conservación de originales/código, D099, idempotencia y recuperación pasan. H6 corregido. **Parcial por H7: el escritor ejecuta un transporte implícito incluso con todos los objetos del origen disponibles.** |
| Checks offline y ningún proveedor sin consentimiento | Suite y checks abajo correctos. La reproducción adicional revela H7, no cubierto por las regresiones existentes. Ningún proveedor real. |

## Evidencia reproducible

[Script nuevo](P008_REVISION_SALIDA_4_REPRO.py) y [JSON nuevo](P008_REVISION_SALIDA_4_EVIDENCE.json):

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python docs/phase/P008_REVISION_SALIDA_4_REPRO.py
```

Exit 0 exige las guardias H1–H3/H5/H6 y acredita **la reproducción de H7**, no su corrección. H4 se contrasta
por lectura. El script reutiliza las funciones de comprobación H1–H3/H5 de las revisiones anteriores; crea
fixtures y expectativas nuevos para H6/H7. Incluye HEAD revisado, Git, hash del script y hashes de los tres
scripts/JSON históricos. No modifica ninguno de ellos ni ejecuta el harness sobre este repositorio.
H2/H3 permiten los objetos inalcanzables de las vistas previas como en D105; H5/H6 comparan todos los bytes.

## Verificación

- Pytest completo: **1.410 pruebas y 121 subtests correctos**, sin fallos. Colección congelada repartida en
  cuatro lotes disjuntos que cubren exactamente los nodeids: 353/353/352/352 OK, con 116/0/5/0 subtests.
  Duraciones: 258,56/263,88/278,19/272,32 s. Solo el aviso conocido Starlette/httpx.
- 12 checks ligeros unittest, 75 pruebas Node, tipos y build correctos. Aviso conocido de chunks mayores
  de 500 kB; sin cambios de assets versionados. No se instalan dependencias ni se actualiza npm.
- Alembic `upgrade head` y `check` sobre SQLite temporal: sin operaciones nuevas. OpenAPI generado en memoria
  idéntico al JSON versionado; sin tocar la base del usuario ni arrancar el servicio.
- Paridad: 35 tablas y 377 columnas idénticas al metadata. Veinte diagramas: siete ER y tres secuencias
  con `mermaid.parse`, siete flowcharts con su parser sin sanitización de etiquetas y tres estados con su
  gramática local sin extracción/sanitización dependiente del DOM. Sintaxis comprobada; sin renderizado.
- 39 Markdown activos/raíz/phase/flows con 434 enlaces relativos/anclas válidos; presupuestos de instrucciones,
  STATE/base/NEXT_STEPS correctos, 111 decisiones, ocho fases y veinte tareas reconocidas por sus parsers.
  El resumen activo de T011 se compacta con enlace a su registro original para mantener STATE bajo 24 KiB;
  su evidencia de entrega permanece intacta. Diff revisado y `git diff --check` correcto.
- Reproducción ejecutada y hashes comprobados. Durante su preparación se corrigió la comparación de rutas
  temporales `/var`/`/private/var` del fixture y se usó la raíz canónica para consultar su operación SQLite;
  la ejecución final es correcta. Son ajustes del script nuevo, sin cambios del producto o evidencia previa.

Sin UI visual, renderizado DOM, Django/ruff/mypy reales, proveedores reales, smokes, push, publicación ni
subagentes. Sin datos privados ni configuración global modificada. Sin cambios de producto, esquema,
API, dependencias, prompts, versiones congeladas o artefactos generados versionados.

## Continuidad

Siguiente: P008-T020, impedir lazy-fetch/transportes del escritor de importaciones A/B y su recuperación.
Después corresponde otra revisión de salida. Cierre y archivo en una tarea posterior separada; sin P009 inventada.

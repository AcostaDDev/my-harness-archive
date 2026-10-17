# P008 — Tercera revisión de salida

Fecha: 2026-10-17. Código revisado: `0348b84bb0909b2de817e33e5c14a391a3945315` (T018).
Decisión: [D109](../DECISIONS.md#d109--tercera-revisión-de-salida-de-p008).

## Dictamen

**P008 sigue activa y no está lista para cerrar.** H1–H3 y H5 se rechazan sin los efectos prohibidos;
H4 conserva las referencias sincronizadas. H6 demuestra que la consulta de estado del Flujo A ejecuta un
filtro de un submódulo antes de cualquier confirmación. Con el submódulo fuera del ámbito documental se
aceptan inventario y conversación.
Se define P008-T019 para corregir esta frontera; esta revisión no cambia el producto ni cierra la fase.

No se ha ejecutado un check READY del producto sobre este repositorio ni se ha registrado en el harness.
La revisión manual de salida y el cierre/archivo siguen siendo operaciones distintas.

## Hallazgos anteriores

| Hallazgo | Comprobación actual |
|---|---|
| H1: filtros del repositorio principal | Configuración e includes comprobados antes de `status`, captura y escritura; reproducción sin marcador ni cambio del checkout. Las regresiones incluyen `clean`/`process`, confirmación, ejecución y recuperación. Resuelto para el caso original; H6 descubre otra vía en submódulos. |
| H2: conversiones de bytes | CRLF con `text eol=lf` rechaza la vista previa antes de escribir, crear operación o adoptar fase. Blobs documentales completos comprobados por SHA-256; originales/binarios y deriva posterior cubiertos por regresiones. Resuelto. |
| H3: destinos ignorados | GEMINI ignorado bloquea antes de confirmar/escribir; sin documento, operación, commit ni fase nuevos. Las comprobaciones se repiten al ejecutar/reanudar. Resuelto. |
| H4: referencias vigentes | F11/F18, `cli-12`, `local-config-4`, `d088-10`, ayudas CLI/registro/UI y Prompts contrastados con T017/T018 y el código. Resuelto; se conservan ADR y snapshots históricos. |
| H5: lazy-fetch y objetos ausentes | A/B rechazan el blob prometido ausente con diagnóstico de objeto/ruta, sin transporte falso, objetos recuperados ni cambios de bytes en checkout/índice/refs/configuración/objetos. Todos los comandos observados llevan `--no-lazy-fetch`. Las 18 regresiones de T018 amplían la comprobación a tamaños, batch, árboles ausentes, consumidores A y vista previa B. Resuelto. |

Se han contrastado `LocalGit`, lectores A/B, el lector de instantáneas, `read_source`, conversación,
vista previa/sellado, despacho del job y escritor documental compartido. Las guardias de D105/D108,
D099, CAS, versiones, intención persistida, conciliación del mismo commit y adopción atómica permanecen.
La evidencia histórica de H1–H5 y los scripts/JSON de las revisiones anteriores no se modifican.

## H6 — Alta: `status` ejecuta filtros de un submódulo durante el inventario A

`adapters/project_import.py:114` comprueba filtros en la configuración del repositorio principal.
Después, `read_checkout` llama a `status --porcelain=v1 -z --untracked-files=all --ignore-submodules=none`
(líneas 125–126). Ese estado inspecciona los submódulos inicializados, cuya configuración de filtros no
está cubierta por la consulta del padre. La selección del ámbito documental y el diagnóstico para modo
`160000` ocurren después, en las líneas 145 y 162–163.

Reproducción offline: padre v1 sintético limpio con `.gitmodules` y un gitlink a un repositorio hijo local,
sin filtros propios. El hijo tiene un README con atributo `filter=synthetic` en `.git/info/attributes` y
un `filter.synthetic.clean` falso que crea un marcador fuera del checkout y devuelve stdin sin cambios.
Se cambia solo el mtime del README para forzar la comprobación de contenido; sus bytes siguen limpios.
El script y marcador viven fuera del padre y no introducen archivos sin seguimiento en él.

La traza muestra que el primer marcador aparece al volver de `status`, pese a que cada comando directo
del lector lleva `--no-lazy-fetch`. Resultado reproducido con filtro directo y por `include.path`:

- Gitlink en `synthetic-module`: inventario aceptado sin bloqueos después de ejecutar el filtro.
- Gitlink en `docs/synthetic-module`: inventario con bloqueo `submodule_entry`, después de ejecutar el filtro.
- Crear conversación con el gitlink fuera de `docs/` y filtro por include también ejecuta el filtro y crea
  la conversación, sin turnos, jobs, agentes invocados ni operación de importación.
- Control del inventario B sobre los mismos cinco fixtures: sin ejecución del filtro. El adaptador B lee
  HEAD sin `status`; su inventario no acredita que la posterior incorporación admita submódulos.

Todos los bytes del checkout y de `.git`, también del hijo, permanecen idénticos; el efecto acreditado es
el marcador externo del programa falso. No hubo red ni herramientas de proyectos reales. No se atribuye
a esta reproducción recuperación de objetos, pérdida documental ni ejecución de un proveedor.

Incumple la lectura sin ejecución de D096 y SPECIFICATION §8. La guardia de filtros del padre no basta:
el rechazo o la inspección segura de gitlinks debe preceder al comando capaz de lanzar código del hijo,
también cuando el gitlink queda fuera de `docs/`. Los consumidores de `read_checkout` heredan esta vía.
T019 deberá revisar también la captura compartida, mantener la limpieza del checkout, D099, CAS y
recuperación y evaluar la versión congelada, sin ampliar soporte de submódulos ni modificar configuración.
No se prescribe aquí una implementación ni se presenta el hallazgo como corregido.

## Criterios de salida de ROADMAP

| Criterio | Evidencia y conclusión |
|---|---|
| Este repositorio con D088, enlaces y diagramas | Documentos/instrucciones presentes, presupuestos y parsers válidos; enlaces y 20 diagramas comprobados. 35 tablas y 377 columnas coinciden con SQLAlchemy. Cumplido. |
| Plantilla, contratos, prompts y API unificados; creación v1 retirada | Pruebas de documentos, definición, prompts, bootstrap y API, exportación OpenAPI contrastada; escritura v1/transición retirada y lectores históricos conservados. Cumplido. |
| Cierre READY, archivo, reinicio y commit conciliable | Código de cierre/adopción y `test_phase_closure`: originales/binarios, archivo completo, sucesora vacía, rechazos, recuperación de tag/commit y plan posterior confirmado. Cumplido. |
| AGENTS congelado por intento | `test_project_instructions`: roles, hashes, límites, cambios entre intentos, rechazo previo y versiones. Excepciones definition/import/onboarding documentadas. Cumplido. |
| Perfiles declarativos y Python/Django | `test_declared_profiles`: v4, compatibilidad, hash/cuarentena, validaciones/JUnit y commit con herramientas falsas. El ensayo Django real permanece fuera de la fase offline. Cumplido. |
| A/B hasta commit confirmado sin ejecución ni pérdida | Recorridos sintéticos ReferenceProject/v1/v2 y Django/TypeScript, originales/código, D099, idempotencia y recuperación en verde. **Parcial: H6 impide acreditar la lectura sin ejecución de A con submódulos.** |
| Checks offline y ningún proveedor sin consentimiento | Todos los checks indicados abajo pasan. La suite existente no cubre H6; el script adicional acredita el fallo. |

## Evidencia reproducible

[Script nuevo](P008_REVISION_SALIDA_3_REPRO.py) y [salida JSON](P008_REVISION_SALIDA_3_EVIDENCE.json):

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python docs/phase/P008_REVISION_SALIDA_3_REPRO.py
```

Exige el rechazo sin efectos de H1–H3 y H5/control B, y reproduce cinco escenarios H6. Su exit 0 acredita
el hallazgo actual, no su corrección. Solo usa Git/SQLite temporales, datos sintéticos y puertos/herramientas
falsos; no ejecuta el harness sobre este repositorio. El JSON identifica HEAD, versión Git y hashes de los
scripts nuevo e históricos. H4 se contrasta por lectura, no mediante este script.
H2/H3 permiten los objetos inalcanzables propios de la vista previa como en D105; H5/H6 comparan todos los
bytes del checkout y de `.git`, incluidos objetos. No se reescriben las reproducciones históricas.

## Verificación

- Pytest completo: **1.383 pruebas y 121 subtests correctos**, sin fallos. Colección congelada y repartida
  en cuatro lotes disjuntos que cubren exactamente todos sus nodeids: 346/346/346/345 OK y 0/116/0/5
  subtests, todos exit 0. Duraciones: 292,91/282,16/299,70/312,50 s. Solo el aviso conocido Starlette/httpx.
- 12 checks ligeros unittest, 75 pruebas Node, `npm run check` y build del frontend correctos. Se mantiene
  el aviso conocido de chunks de más de 500 kB. Sin assets versionados modificados.
- Alembic `upgrade head` y `check` sobre SQLite temporal: sin operaciones nuevas. OpenAPI generado en memoria
  idéntico al JSON versionado; no se migra la base del usuario ni se arranca el servicio.
- 37 Markdown activos/raíz/phase/flows con 413 enlaces relativos/anclas válidos; presupuestos correctos,
  109 decisiones, ocho fases y diecinueve tareas reconocidas por sus parsers. Los resúmenes activos de
  T009/T010 se compactan con enlaces a sus entregas para mantener STATE dentro de 24 KiB; los registros
  de trabajo originales permanecen intactos.
- Las 35 tablas y 377 columnas coinciden con el metadata. 20 diagramas: siete ER y tres secuencias con
  `mermaid.parse`; siete flowcharts con su parser y sin sanitización de etiquetas; tres estados con su
  gramática local sin DOM. Esto valida sintaxis, no renderizado ni apariencia.
- Reproducciones ejecutadas y script compilado; diff revisado y `git diff --check` correcto. Sin cambios
  del producto, esquema, API, dependencias, prompts, versiones congeladas o artefactos generados versionados.

Sin comprobación visual de UI o renderizado DOM, Django/ruff/mypy reales, proveedores reales, smokes,
push, publicación ni subagentes. Sin datos privados ni configuración global modificada.

## Continuidad

Siguiente: P008-T019, impedir la ejecución implícita de filtros/código de submódulos durante las lecturas A.
Después se repetirá la revisión de salida. Cierre y archivo en una tarea posterior separada;
ROADMAP no define una sucesora y no se inventa P009.

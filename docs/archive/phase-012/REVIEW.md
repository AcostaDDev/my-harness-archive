# Revisión de cierre — P012

Fecha: **2026-10-26**. Base: `ce4b5d2f8ed1a1ac1af9cec00316b10b1d95a814` (T006/D211).
**Dictamen: siete criterios cumplidos en el alcance declarado; cierre documental procedente y completado.**
[Decisión D212](../../DECISIONS.md#d212--cierre-documental-de-p012-y-validación-real-archivada).

La [revisión de T006](P012_REVIEW.md) fija la matriz completa de criterios, fallos, procedencia, consumo y límites.
Se conserva sin reescribirla. T007 completa las trece tareas mediante el [registro de cierre](P012_CIERRE.md),
el archivo exacto y los documentos vivos; no hay correcciones obligatorias pendientes dentro de este alcance.

## Contraste de criterios

| # | Criterio de ROADMAP | Dictamen y procedencia |
|---|---|---|
| 1 | Propuesta, pareja, presupuestos y consentimiento por tramo | Cumplido: T001/D184 y consentimientos T002–T004. Saldos sin autorización nueva |
| 2 | Plan → ejecución → validación → revisión → COMMITTED con cli-14 y v8 | Cumplido: T002/D198, perfil declarado, seis comandos/13 casos JUnit y ACCEPT; instalación de ese tramo |
| 3 | B Django sintética, originales intactos y tarea D095 | Cumplido con evidencia acumulada D191/D193/D198: dos B, reenvío idempotente y tarea sobre clon documental B2; sin tercera incorporación |
| 4 | Chat, propuesta y backup/restauración con runs reales | Cumplido con salvedad autorizada D200/D204: dos respuestas, comando, QUEUED, API/UI de consulta; identidad histórica unknown conservada |
| 5 | TypeScript v2/es nuevo, preparación, tarea y cierre con READY | Cumplido D206/D208/D209: recibo intacto, tarea COMMITTED, tercer check válido, P001 CLOSED/P002 vacía; dos checks rechazados conservados |
| 6 | Fallos acotados, regresiones sintéticas y parciales explícitos | Cumplido: T008–T013; sin reparar resultados reales, editar SQLite o relajar guardias. Causa del truncamiento no probada |
| 7 | Alcance público, candidato, suites, revisión y expediente sin ejecutar | Cumplido D210/D211: 401 archivos, paquete verificado offline y expediente P012. T007 preserva el candidato sin acciones remotas |

Los trece criterios globales de SPECIFICATION conservan el dictamen de P011 y sus regresiones en la suite T005;
P012 añade evidencia real concreta, sin afirmar una comprobación real nueva de todos los criterios globales.

## Conservación y continuidad

El [manifiesto](MANIFEST.json) fija los 42 originales con sus blobs, tamaños y SHA-256 en T006. Las revisiones,
propuestas y resultados parciales conservan exactamente sus bytes. Los documentos nuevos SUMMARY/REVIEW/P012_CIERRE
y comprobador/resultado acreditan T007; los estados pendientes de los snapshots no se corrigen retrospectivamente.
Los archivos P000–P011 y diagramas vigentes no cambian. Solo se reubican enlaces de decisiones y documentos técnicos.

El árbol público y paquete de T005 se conservan: manifiesto `cf191a40…9362a`, wheel `eef56a29…4504ab`;
P011 íntegra aparte. [Verificación de cierre](P012_CIERRE.md#verificación) con parsers, enlaces, presupuestos,
hashes y diff. Sin repetir suites de producto, builds o QA válidas por un cambio exclusivamente documental.

El [expediente vigente](P012_EXPEDIENTE_APERTURA.md) sigue preparado, con apertura sin ejecutar: su frase
«T007 pendiente» describe el momento T006; este cierre resuelve ese prerrequisito. Los comandos de reproducción
ya usan el commit T005 y sus rutas originales, por lo que no se adaptan los snapshots al archivarlos.
El siguiente paso requiere instrucciones del usuario para los parámetros y acciones de apertura.

Sin fase sucesora, cambio de versión, tag propio, push o publicación. Cierre manual conforme a D182,
separado del READY del producto y del cierre del hijo T004. No se registra ni opera este repositorio con el harness,
ni se consume un saldo operativo. Permanecen los límites de T006: pareja actual única, macOS ARM64/Chrome,
fixtures sintéticos, resultados fallidos/cola e identidad incierta; ninguna certificación nueva de escritores.

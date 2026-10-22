# P010 — Revisión de salida

Fecha: 2026-10-22. Base: `d6a69c8` (producto `dd7b958`).
**Dictamen: favorable en el alcance declarado, con los siete criterios cumplidos.** Decisión D152.
La revisión completa T009; el cierre documental se realiza en T010. No se declara cerrada la fase en esta entrega.
[Comprobaciones y alcance](P010-T009_VERIFICACION_FINAL.md).

## Criterios de ROADMAP

| # | Criterio | Estado de revisión | Evidencia y límite |
|---|---|---|---|
| 1 | Arranque TypeScript confirmado, recuperable y sin desproteger manifiestos | Cumplido offline | T002, D143: recorrido sintético reejecutado en T009; variante con node/npm reales/caché histórica, omitida en T009; sin proveedores reales. Los manifiestos siguen protegidos tras preparar |
| 2 | Lecturas de runs acotadas y compatibles sin reescribir snapshots | Cumplido offline | T003/T011, D144/D145: formatos 1–8, proyección transaccional, diff por tramos, JUnit paginado, métricas y exportación. Tests de historiales de 26,4 MiB y ámbito de 35,4 MiB reejecutados en T009 |
| 3 | Marcadores opcionales y evidencia de fases cerradas distinguida | Cumplido offline y con QA visual sintética | T004/T005, D146/D147: plantilla y UI; fases abierta, cerrada sin/con sucesora y deriva real, también documentos. T009 conserva doce capturas del wheel; sin revisor real |
| 4 | Instalación, versiones y alcance coherentes | Cumplido en el alcance verificado | T006/T012, D148/D150: README/ARCHITECTURE y `migrate` con copia previa; entrada instalada verificada por T009 en base sintética. D151 conserva los límites reales; versión `0.1.0`, sin publicación |
| 5 | Trece criterios globales con dictamen y evidencia trazable | Cumplido offline | T007, D149 y seguimiento T012/T008; suite completa reejecutada en T009: cursor gestionado interpretado expresamente por el usuario; el hueco de migración instalada se corrige en T012. Sin extrapolar la evidencia del hijo Django |
| 6 | Propuesta y decisión explícita sobre validación real complementaria | Cumplido | T008, D151: A/B y D095 aplazados por el usuario. No se añade tarea operativa ni se transforma evidencia sintética en real |
| 7 | Checks, QA, wheel final y dictamen antes del cierre | Cumplido | T009: pytest 1682 y 121 subtests, unittest 12, Node 82, tipos, Alembic, build y verificador del wheel instalado correctos; QA sintética acreditada y servicios detenidos. Dos opt-in omitidas; sin recurrencia del intermitente de T007 |

Las suites de T009 se ejecutan sobre la base identificada; las pruebas con herramientas/proveedores reales de
entregas previas siguen siendo históricas y no se repiten ni extrapolan. No se detectan bloqueos pendientes del
alcance declarado. El cierre manual de este repositorio seguirá separado de un check READY del producto; no se
opera el harness sobre él ni se crea tag o publicación.

Paquete verificado: `harness_local-0.1.0-py3-none-any.whl`, SHA-256
`94a6699e7c2e36cc42bcf45e1e2feb4d2028aa722756b47cb862087919792b17`.
[Evidencia saneada](P010-T009_EVIDENCE.json), [matriz global y seguimiento](P010_MATRIZ_ACEPTACION.md).
La fuente de producto es `dd7b958`; T008 y T009 solo cambian documentación y artefactos de evidencia.

## Alcance real conservado

A/B y perfil Django declarado: implementados, con agentes y herramientas falsos, sin uso real por decisión D151.
Receta Django: evidencia histórica D139 limitada a macOS arm64/Python 3.13. Chat, backup/restauración y receta
TypeScript: sin uso real. Contención cooperativa, manifiestos fijos, validaciones sin hora, avisos KaTeX y restantes
límites de ARCHITECTURE §10 conservados. Las verificaciones sintéticas del paquete no amplían esos consentimientos.

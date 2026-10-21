# Revisión de cierre — P009

**Dictamen:** siete criterios de ROADMAP cumplidos en el alcance del piloto documentado; sin bloqueos pendientes
para el cierre documental. Base revisada: `422357145d4120a9d55a65783864054ee3e96378` (T012/D139).
Cierre solicitado por el usuario el 2026-10-21 ([D140](../../DECISIONS.md#d140--cierre-documental-manual-de-p009)).
La revisión contrasta ROADMAP, plan, entregas y el informe final; no repite operaciones del piloto.

| Criterio de ROADMAP | Evidencia y resultado |
|---|---|
| Carpeta explícita, persistente y limitada a hijos nuevos | T002/D117: autoridad, retirada, destinos, recuperación y tests sintéticos; elección real desde UI en T007/D127. Cumplido. |
| Creación desde cero con destino visible e idempotencia | T002–T005 y T007: hijo nuevo, documentos y receta desde UI, sin scaffold manual; fronteras/recuperación offline. Cumplido. |
| D088, Django/SQLite/plantillas y dependencias/validaciones reales | T004/D119 y T005/D120; receta y commit técnico en T007, seis validaciones del hijo en T012. Migración de uso aplicada tras HITL con copia privada. Cumplido. |
| Roles por proyecto y elección motivada del ejecutor | T003/D118; registros v1–v4 del mismo hijo y contextos congelados contrastados en T008–T012. Cumplido. |
| Cuatro parejas COMMITTED en un mismo proyecto | Codex→Codex `98f4611`, Codex→Claude `2f2b13f`, Claude→Claude `882af9b`, Claude→Codex `a2de6ad`. Mismo id/checkout e historial conservado. Cumplido. |
| Funciones conjuntas, QA, tests, READY y archivo | QA UI completo de T012; 27 tests y seis validaciones verdes, READY en `47a0557`, P001 CLOSED, tag `p001`, archivo en `3d105c6`. Cumplido. |
| Checks offline y ensayo previos; salida separada del cierre | T005 ensayo temporal; T015 wheel D088 completo; suites por entrega, última completa T020; T012 recoge matriz, métricas, incidencias y límites. Este cierre documental es posterior. Cumplido. |

Fuentes principales: [plan de tareas](NEXT_STEPS.md), [creación](P009-T007_CREACION_DJANGO.md),
[matriz y revisión final de T012](P009-T012_CIERRE_PILOTO.md#revisión-final-de-salida),
[wheel](P009-T015_VERIFICACION_WHEEL.md) y [última entrega de código](P009-T020_ENCOLAR_DESDE_DOCUMENTOS.md).
Los estados de parada de informes y decisiones anteriores se conservan; sus continuaciones acreditan el resultado.
El primer REVISE de T012 se resolvió mediante tres ediciones documentales confirmadas y un nuevo check READY.

## Límites y observaciones

- El piloto acredita continuidad e interoperabilidad con cuatro tareas diferentes, sin clasificación comparativa
  de calidad, velocidad o coste entre modelos. Modelo/esfuerzo solicitados y reportados se distinguen en la matriz;
  esfuerzo efectivo sin medición independiente, coste total y tiempo humano completos ausentes.
- Evidencia real limitada a macOS arm64/Python 3.13.13. El perfil declarativo Python/Django de D095 sigue pendiente
  de confirmar sobre un proyecto real; el piloto usa la receta `python-django-recipe`. Contención cooperativa.
- Observaciones sin bloqueo: alta del hijo sin POST→redirect→GET; plantilla define-project sin aclarar los
  marcadores opcionales en una carpeta nueva; vista de fase cerrada que muestra deriva al comparar documentos
  vivos renovados con su base histórica. Se conservan como candidatas en [ROADMAP](../../ROADMAP.md#candidatas-sin-fase-asignada).
- La migración local pendiente se resolvió con autorización explícita; no se añade migración automática al producto.
  T012 agotó 2 de 2 llamadas y el piloto consumió 26 de 60. El margen global no autoriza más llamadas ni operaciones.

Esta síntesis manual no es un check READY del harness sobre este repositorio. El cierre no opera el Django hijo,
registra el repositorio, crea tag propio ni amplía consentimientos. Comprobaciones de la tarea en
[P009_CIERRE](P009_CIERRE.md); navegación y contexto de snapshots en [SUMMARY](SUMMARY.md#archivo-y-contexto).

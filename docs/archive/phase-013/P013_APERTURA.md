# Apertura documental de P013

Fecha: 2026-10-26. Petición: abrir una fase con las mejoras de instalación/configuración acordadas y
aplazar GitHub hasta cerrarla. [D215](../DECISIONS.md#d215--p013-instalación-guiada-y-configuración-desde-la-ui).

## Resultado

- P013 activa y planificada, con ocho criterios de salida y quince tareas pendientes. Siguiente P013-T001,
  contrato previo a implementación; el [plan](P013_PLAN.md) recoge alcance, límites y matriz de verificación.
- NEXT_STEPS detalla objetivos, dependencias, rutas, criterios, validación y entregables por tarea.
  STATE/ROADMAP señalan el aplazamiento de publicación y la nueva fase, conservando el cierre de P012.
- SPECIFICATION/ARCHITECTURE añaden una ampliación explícitamente planificada, separada del contrato actual;
  [flujo propuesto](../flows/configuration-setup.md) en paridad, sin afirmar implementación o migraciones nuevas.
- DECISIONS incorpora D215 y su índice; cuerpos anteriores y documentos archivados intactos. Sin cambios
  en README de producto, ejemplos, código, datos, dependencias, versión, candidato o paquetes anteriores.

## Verificación

- Parsers puros de `core.engine.documents`: **13 fases, ocho criterios P013, quince tareas pendientes y
  215 decisiones con estado**, sin duplicados. Campos de tareas y dependencias anteriores comprobados.
- **706 enlaces locales**, incluidos anchors, en los nueve documentos de esta apertura: correctos.
  Fences equilibrados y presupuestos STATE/NEXT_STEPS/base correctos (STATE 14.581 bytes,
  NEXT_STEPS 20.910 bytes en la comprobación).
- Cuerpos D001–D214 comparados con HEAD por bytes, salvo espacios de separación finales: intactos;
  `docs/archive/` sin cambios. El índice DECISIONS solo añade D215.
- Dos diagramas Mermaid parseados con el checker sintáctico ya existente de P011, sin modificarlo:
  `node docs/archive/phase-011/P011-T013_mermaid_check.mjs frontend docs/flows/configuration-setup.md`:
  dos `flowchart-v2`, cero fallos. No acredita renderizado ni sanitización visual.
  El primer intento directo en Node falló por ausencia de DOM para DOMPurify (`addHook`); el checker
  existente sustituye únicamente ese saneador para analizar sintaxis, sin cambiar el frontend.
- Diff revisado y `git diff --check` correcto. Solo documentación vigente nueva/modificada;
  sin cambios de código, modelos, migraciones, API o configuración operativa.

## Límites

Solo planificación documental. No se ejecutaron suites de producto, instalaciones, builds, servicios,
agentes/proveedores, smokes, harness sobre este repositorio ni operaciones remotas. No se modificó la
configuración global del equipo, no se reutilizaron bases/fixtures ni se hizo commit. Los recorridos
operativos futuros se realizarán en sus tareas con el alcance y autorización que correspondan.

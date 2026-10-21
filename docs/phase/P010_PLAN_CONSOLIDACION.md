# P010 — Plan de consolidación de la primera versión local

Fecha: 2026-10-21. Decisión: [D141](../DECISIONS.md#d141--p010-consolidación-de-la-primera-versión-local).
**Estado:** planificación documental aceptada; diez tareas pendientes. Sin implementación ni operación iniciada.
[Criterios de salida](../ROADMAP.md#p010--consolidación-de-la-primera-versión-local),
[contratos de tareas](../NEXT_STEPS.md), [base acumulada](../STATE.md).

## Resultado que se busca

Cerrar una primera versión local para uso individual en el alcance acreditado: creación y gestión de proyectos,
ejecución/revisión/commit, fases, documentación, chat, métricas y recuperación, incorporando las correcciones
pendientes y una revisión global de aceptación. La evidencia real sigue limitada a los entornos y recorridos
efectivamente probados. No se asume que «primera versión» signifique cambiar la versión del paquete a `1.0.0`.

P001–P009 están cerradas. La [revisión de P009](../archive/phase-009/REVIEW.md) acredita su piloto Django,
pero no constituye por sí sola una revisión de todos los requisitos del producto. SPECIFICATION §§9–10 aporta
el requisito de lecturas acotadas y los trece criterios globales que se contrastarán en esta fase.

## Brechas y entregas previstas

| Área | Situación al planificar | Entrega de P010 |
|---|---|---|
| TypeScript nuevo | Falta `package.json`; el ejecutor normal no puede crearlo por su protección. | T001 diseña y T002 implementa un arranque confirmado y recuperable. |
| Consulta de runs | Cada lectura decodifica el historial completo, límite reconocido frente a SPECIFICATION §9. | T001 inventaría consumidores; T003 acredita consultas acotadas sin reescribir el historial. |
| Definición | Los marcadores opcionales en una carpeta nueva necesitan aclaración. | T004 aclara plantilla/interfaz y respeta el contrato D088. |
| Fases cerradas | Comparar documentos vivos renovados con su base histórica produce una presentación confusa de deriva. | T005 distingue archivo/evidencia histórica y documentos actuales sin ocultar deriva real. |
| Instalación y compatibilidad | Hay referencias desactualizadas; README no incluye todas las CLI admitidas por D122/código. | T006 contrasta documentación, ejemplos y límites con el producto entregado. |
| Aceptación | Evidencia repartida por fases; falta una síntesis final de los trece criterios globales. | T007 mantiene una matriz con método, procedencia, resultados y huecos. |
| Evidencia real | A/B se acreditan sintéticamente; D095 no está confirmado en un proyecto real. P009 usa otra receta. | T008 prepara propuesta complementaria y decisión explícita de alcance. |
| Paquete y cierre | No hay dictamen final de esta consolidación. | T009 verifica el estado final; T010 archiva solo tras dictamen favorable. |

Las soluciones técnicas concretas son trabajo pendiente de T001: no se fija aquí una nueva receta, migración,
tabla, índice, versión de codec o protocolo. Se parte del producto actual y se conservan permisos, confirmación
por contenido, recuperación y compatibilidad. Una contradicción de diseño se consulta antes de resolverla.

## Secuencia y dependencias

1. T001: contrato de las dos correcciones, consumidores afectados y matriz inicial de aceptación.
2. T002–T005: implementar cada corrección en una tarea separada, con regresiones y paridad documental.
3. T006: consolidar documentación sobre lo efectivamente implementado.
4. T007: contrastar los trece criterios y localizar huecos de evidencia o defectos; acotar correcciones adicionales.
5. T008: preparar la validación real complementaria y resolver con el usuario qué se ejecuta y qué se limita.
6. T009: comprobar base/paquete finales y revisar salida. T010: síntesis y archivo documental posterior.

La numeración expresa el trabajo previsto, sin ejecución paralela ni lanzamiento de agentes. Si un hallazgo
exige nuevas tareas, se añaden de forma acotada con su decisión y dependencias antes del cierre. La preparación
de T008 puede reutilizar la evidencia existente; no requiere iniciar una segunda fase del hijo de P009.

## Evidencia real y alcance soportado

Se distinguen tres situaciones: comportamiento cubierto con datos y agentes falsos; recorrido probado con
herramientas/proveedores reales; y capacidad implementada cuya confirmación real está pendiente. La matriz
de aceptación identifica cada caso y no extrapola macOS arm64 a otras plataformas ni compara calidad de modelos.

T008 debe entregar una propuesta revisable para A/B y el perfil declarativo Python/Django de D095. El usuario
decidirá si se realiza la validación complementaria o se conservan esos límites en el alcance anunciado. Esta
decisión queda pendiente; no se interpreta el silencio como aprobación ni como aplazamiento.

Si se decide ejecutar, se añade una tarea operativa separada con autorización concreta: proyectos sintéticos,
ubicaciones, paquete instalado fuera del checkout (D051), versiones, configuración, proveedores/modelos/esfuerzos,
comandos, instalaciones/red, servicios, límites de consumo, parada, recuperación, evidencias y limpieza. Su
resultado se incorpora antes del dictamen final. Si se aplaza, el cierre declara qué no está validado en uso real.
No se repite automáticamente la matriz de cuatro parejas ni se usa ReferenceProject como fixture escribible.

## Condiciones de cierre

- Los siete criterios de P010 en ROADMAP se contrastan uno a uno; las entregas mantienen evidencia por tarea.
- Los trece criterios de SPECIFICATION §10 tienen dictamen trazable; una carencia del alcance declarado bloquea
  el cierre hasta corregirse. Un límite de validación se declara y se decide, no se convierte en aprobado.
- Historiales y snapshots congelados permanecen intactos. Modelos/flujos/API que cambien tienen paridad documental
  y de tipos en la entrega correspondiente; su diseño pendiente no aparece como implementación vigente.
- Checks offline pertinentes y QA verifican las correcciones; la verificación del wheel acredita el paquete final
  y no se sustituye por resultados de un wheel anterior. Se registran base, comandos, resultados y omisiones.
- REVIEW final favorable antes de archivar; el cierre documental manual no equivale a un check READY del producto
  sobre este repositorio. Sin cambio automático de versión, tag, commit, publicación o sucesora.

## Aplazamientos y límites de autoridad

Quedan fuera la hora de cada validación, los avisos *low* de KaTeX y el alta Django sin POST→redirect→GET,
que pertenece a la aplicación hija. También App Server/SDK, `project.yaml`, nube, multiusuario, aislamiento físico,
rediseño general de UI y publicación. No se amplía el catálogo CLI sin caracterización ni se promete corregir
otros límites operativos, como volver a elegir la carpeta de proyectos tras ciertos reinicios (D130).

El usuario ha pedido únicamente crear esta documentación. No se implementan correcciones, ejecutan tests del
producto, lanzan agentes/proveedores o smokes, instalan dependencias, levantan servicios, hacen commits/push ni
modifican configuraciones globales en esta entrega. Las comprobaciones documentales son de lectura/análisis
local. P009 y sus archivos se conservan; los consentimientos de aquel piloto siguen agotados.

## Comprobación de esta planificación

- Parsers documentales puros, sin supervisor ni proveedores: 141 decisiones, diez fases, siete criterios de P010
  y diez tareas de P010 en orden, todas pendientes y con campos reconocidos de objetivo, alcance, rutas,
  criterios, validación y entregables.
- Presupuestos: STATE 6.986/24.576 bytes, base acumulada 5.101/12.288 y NEXT_STEPS 16.343/49.152.
- Diecisiete destinos/anclas nuevos únicos por documento comprobados; sin enlaces a artefactos todavía pendientes.
- D001–D140 y su índice previo conservados por bytes; secciones P001–P009 de ROADMAP y archivos de fases
  cerradas intactos. Diff revisado y `git diff --check` correcto; solo seis archivos Markdown nuevos/modificados.
- No se ejecutan unittest, pytest, Node, tipos/build, Alembic ni verificación del wheel: esta entrega solo planifica.
  Sin cambios de código, esquema, API, flujos, versiones o configuración; sin instalaciones, servicios, agentes,
  proveedores, smokes o commits. Los checks previstos para T001–T010 no se consideran ejecutados por incluirlos aquí.

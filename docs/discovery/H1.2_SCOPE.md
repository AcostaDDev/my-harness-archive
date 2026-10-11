# Siguiente tarea — H1.2 (pendiente)

H1.1 completado el 2026-10-11. [Alcance y criterios originales](discovery/H1.1_SCOPE.md)
conservados para revisión; [entrega y verificaciones](discovery/H1.1_IMPORT.md).
Esta entrega no inicia H1.2.

## Objetivo

Implementar navegación de lectura por proyectos, fases, tareas y evidencias de
runs legacy importados. Desde una tarea se debe poder llegar a la ejecución
observada, revisión y evidencia que explican su resultado, sin inferir invocaciones
ni aceptación aplicada a partir de índices o veredictos legacy.

## Alcance de la siguiente sesión

1. Revisar H1.2 del backlog, la especificación de observación, D006/D010/D012,
   `discovery/LEGACY_FORMATS.md` y el índice H1.1. Usar fixtures sintéticos;
   no leer/copiar runs reales ni ejecutar el harness de referencia.
2. Añadir consultas y contratos HTTP de lectura para listar proyectos/orígenes,
   fases y tareas, con acceso a runs y evidencia de ejecución observada. Conservar
   procedencia y límites de identidad del legacy; review/validation no generan
   por sí solos nuevos intentos de agente ni aceptación/commits.
3. Incorporar navegación UI y timeline de evidencias, hallazgos de revisión,
   bloqueos, diffs y logs paginados. Lectura de artefactos desde el origen debe
   comprobar ruta/hash y mostrar ausencias o cambios sin presentar bytes nuevos
   como la versión indexada. No ejecutar contenido histórico.
4. Mostrar duración por comando y consumo con origen identificado; conservar
   «no registrado», null y cero, selección solicitada frente a datos reportados,
   y coste equivalente API frente a factura/cuota. Mostrar diagnósticos locales
   y pendientes sin equipararlos a errores de agente.
5. Generar OpenAPI/tipos desde los contratos del límite HTTP, ejecutar checks
   offline pertinentes y verificar el recorrido con los cinco escenarios.
   Mantener importación H1.1/simulaciones H0.3, actualizar STATE/NEXT_STEPS y
   registrar decisiones duraderas.

## Criterios de aceptación

- Desde una tarea importada se llega a su run/evidencia de ejecución, revisión
  y artefactos que explican los datos mostrados; historial REVISE se conserva.
- Los cinco escenarios se pueden inspeccionar sin inventar invocaciones,
  aceptación, commit ni cierre, y sin ocultar ausencias o revisión parcial.
- Timeline/hallazgos/bloqueos y logs/diffs paginados conservan procedencia;
  contenido ausente o con hash cambiado se presenta explícitamente.
- Duración/consumo muestran origen y campos no registrados sin defaults/cero
  ficticios. Contratos/tipos, checks offline y build pasan; H1.1/H0.3 siguen funcionando.

## Fuera de alcance

H1.3 observador/SSE/reconciliación automática, extracción del motor H2,
modo gestionado, adaptadores reales, chat, permisos interactivos, SDKs y distribución.
No ejecutar harness, agentes, tests/instalaciones en ReferenceProject ni modificar
configuración global. Cualquier smoke real con proveedores exige autorización
explícita de consumo en una tarea posterior.

# Siguiente tarea — H1.1 (pendiente)

H0.3 completado el 2026-10-11. [Alcance y criterios originales](discovery/H0.3_SCOPE.md)
conservados para revisión; [entrega y verificaciones](discovery/H0.3_SKELETON.md).
H0 está completado. Esta entrega no inicia H1.1.

## Objetivo

Implementar importación legacy de lectura, idempotente y tolerante a archivos
parciales, usando los fixtures sintéticos de H0.1. SQLite será un índice
reconstruible en modo observación; los archivos de origen seguirán siendo autoridad.

## Alcance de la siguiente sesión

1. Revisar `discovery/LEGACY_FORMATS.md`, `discovery/BASELINE.md`, decisiones
   D006/D009/D010 y fixtures `tests/fixtures/legacy`. Usar únicamente datos
   sintéticos; no leer/copiar runs reales ni ejecutar el harness de referencia.
2. Leer `task.json`, resultados, reviews, validaciones, stops y metadatos de fases.
   Conservar campos desconocidos relevantes y distinguir ausencia, null y cero;
   no inferir invocaciones, aceptación o commits de iteraciones/estados legacy.
3. Añadir el modelo mínimo de importación/índice y su migración. Identificar
   procedencia por ruta, identidad y hash; reimportar no debe duplicar registros.
   Mantener las simulaciones H0.3 separadas de los intentos importados.
4. Registrar errores por archivo sin abortar el inventario completo. Un JSON
   parcial puede quedar pendiente de relectura; un archivo ausente no acredita
   fallo ni consumo cero. Incorporar una entrada local explícita para importar
   y consultar el resumen; no implementar aún navegación H1.2 ni observador H1.3.
5. Ejecutar checks offline de importación, migración y regresión pertinentes.
   Actualizar comandos comprobados, STATE/NEXT_STEPS y decisiones duraderas.

## Criterios de aceptación

- Los cinco escenarios sintéticos se importan con sus evidencias y ausencias;
  la segunda importación no duplica registros.
- Ausencia de consumo o duración se conserva como «no registrado», sin
  convertirla en cero o una estimación; null y cero observado siguen distinguibles.
- Un archivo inválido/parcial genera diagnóstico local y permite importar el
  resto; una relectura explícita puede incorporar una versión completa.
- No se modifica el origen ni se ejecutan agentes. Migración y checks offline
  pasan, y el recorrido simulado H0.3 sigue funcionando.

## Fuera de alcance

H1.2 navegación/timeline, H1.3 observador/SSE, extracción del motor H2,
adaptadores reales, chat, permisos interactivos, SDKs y distribución.
No ejecutar harness, agentes, tests/instalaciones en ReferenceProject ni modificar
configuración global. Cualquier smoke real con proveedores exige autorización
explícita de consumo en una tarea posterior.

# Plan archivado — P002 Visor útil sin ejecutar agentes (antes H1)

Reconstruido en P008-T001 (D088) a partir de la sección del backlog y de los alcances que `docs/discovery/*_SCOPE.md` conservaba de `docs/NEXT_STEPS.md` antes de cada entrega (hasta `8622a43`). Los enlaces apuntan al archivo de cada fase.

## Plan del backlog

### Hito 1 — Visor útil sin ejecutar agentes

#### H1.1 Importación legacy

- Leer `task.json`, resultados, reviews, validaciones, stops y metadatos de fases.
- Registrar errores de importación sin abortar el inventario completo.
- Usar importación idempotente y tratar archivos parciales como pendientes.
- Criterio: segunda importación no duplica registros; ausencia de consumo o duración aparece como no registrada.

#### H1.2 Navegación y evidencias

- Listado de proyectos, fases, tareas e intentos.
- Timeline, hallazgos de revisión, bloqueos, diffs y logs paginados.
- Duración por comando y consumo con origen identificado.
- Criterio: desde una tarea se puede llegar al intento, revisión y evidencia que explican su resultado.

#### H1.3 Actualización incremental

- Observador de archivos con relectura controlada y reconciliación al iniciar.
- Eventos SSE persistidos y reconexión por cursor.
- Criterio: cerrar y abrir el navegador no pierde ni duplica actividad; un archivo a medio escribir no se presenta como fallo de agente.

**Salida del hito:** panel usable con históricos. Todavía no permite lanzar el motor anterior desde la web.

## Alcances conservados

### Siguiente tarea — H1.1 (pendiente)

_Origen: `docs/discovery/H1.1_SCOPE.md`._

H0.3 completado el 2026-10-11. [Alcance y criterios originales](../phase-001/NEXT_STEPS.md)
conservados para revisión; [entrega y verificaciones](../phase-001/H0.3_SKELETON.md).
H0 está completado. Esta entrega no inicia H1.1.

#### Objetivo

Implementar importación legacy de lectura, idempotente y tolerante a archivos
parciales, usando los fixtures sintéticos de H0.1. SQLite será un índice
reconstruible en modo observación; los archivos de origen seguirán siendo autoridad.

#### Alcance de la siguiente sesión

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

#### Criterios de aceptación

- Los cinco escenarios sintéticos se importan con sus evidencias y ausencias;
  la segunda importación no duplica registros.
- Ausencia de consumo o duración se conserva como «no registrado», sin
  convertirla en cero o una estimación; null y cero observado siguen distinguibles.
- Un archivo inválido/parcial genera diagnóstico local y permite importar el
  resto; una relectura explícita puede incorporar una versión completa.
- No se modifica el origen ni se ejecutan agentes. Migración y checks offline
  pasan, y el recorrido simulado H0.3 sigue funcionando.

#### Fuera de alcance

H1.2 navegación/timeline, H1.3 observador/SSE, extracción del motor H2,
adaptadores reales, chat, permisos interactivos, SDKs y distribución.
No ejecutar harness, agentes, tests/instalaciones en ReferenceProject ni modificar
configuración global. Cualquier smoke real con proveedores exige autorización
explícita de consumo en una tarea posterior.

### Siguiente tarea — H1.2 (pendiente)

_Origen: `docs/discovery/H1.2_SCOPE.md`._

H1.1 completado el 2026-10-11. [Alcance y criterios originales](NEXT_STEPS.md)
conservados para revisión; [entrega y verificaciones](H1.1_IMPORT.md).
Esta entrega no inicia H1.2.

#### Objetivo

Implementar navegación de lectura por proyectos, fases, tareas y evidencias de
runs legacy importados. Desde una tarea se debe poder llegar a la ejecución
observada, revisión y evidencia que explican su resultado, sin inferir invocaciones
ni aceptación aplicada a partir de índices o veredictos legacy.

#### Alcance de la siguiente sesión

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

#### Criterios de aceptación

- Desde una tarea importada se llega a su run/evidencia de ejecución, revisión
  y artefactos que explican los datos mostrados; historial REVISE se conserva.
- Los cinco escenarios se pueden inspeccionar sin inventar invocaciones,
  aceptación, commit ni cierre, y sin ocultar ausencias o revisión parcial.
- Timeline/hallazgos/bloqueos y logs/diffs paginados conservan procedencia;
  contenido ausente o con hash cambiado se presenta explícitamente.
- Duración/consumo muestran origen y campos no registrados sin defaults/cero
  ficticios. Contratos/tipos, checks offline y build pasan; H1.1/H0.3 siguen funcionando.

#### Fuera de alcance

H1.3 observador/SSE/reconciliación automática, extracción del motor H2,
modo gestionado, adaptadores reales, chat, permisos interactivos, SDKs y distribución.
No ejecutar harness, agentes, tests/instalaciones en ReferenceProject ni modificar
configuración global. Cualquier smoke real con proveedores exige autorización
explícita de consumo en una tarea posterior.

### Siguiente tarea — H1.3 (pendiente)

_Origen: `docs/discovery/H1.3_SCOPE.md`._

H1.2 completado el 2026-10-11. [Alcance y criterios originales](NEXT_STEPS.md)
conservados para revisión; [entrega y verificaciones](H1.2_NAVIGATION.md).
Esta entrega no inicia H1.3.

#### Objetivo

Añadir actualización incremental de observación: watcher con relectura controlada,
reconciliación al iniciar y eventos SSE persistidos con reconexión por cursor.
Cerrar y abrir el navegador debe recuperar actividad sin pérdidas ni duplicados,
sin presentar un archivo parcial como fallo del agente.

#### Alcance de la siguiente sesión

1. Revisar H1.3 del backlog, observación/persistencia de la especificación y
   D012/D013. Usar fixtures/copias sintéticas; conservar autoridad del origen,
   importación explícita H1.1 y navegación H1.2, sin iniciar motor ni agentes.
2. Implementar observación local controlada por proyecto, agrupación de cambios y
   relectura de evidencias. Reconciliar al iniciar y preservar identidad/idempotencia,
   ausencias y archivos parciales pendientes de relectura. Cambios no convierten
   review/validación en intentos ni ACCEPT/READY en aceptación/commit/cierre.
3. Persistir eventos de actualización del índice y servir SSE con cursor estable.
   Resolver consistencia entre transacción del índice/evento, reconexión, orden,
   duplicación y recuperación tras reinicio; no implementar event sourcing del motor.
4. Actualizar listas/detalles de la UI por eventos, manteniendo selección coherente,
   procedencia y hashes. Un tramo previamente abierto no se mezcla con contenido
   de un hash nuevo; separar error local de lectura y evidencia de fallo del agente.
5. Generar contratos/tipos y comprobar offline los cinco escenarios, escrituras
   parciales que se completan, cambios/desapariciones, reconexión y reinicio.
   Mantener H0.3/H1.1/H1.2, actualizar STATE/NEXT_STEPS y registrar decisiones.

#### Criterios de aceptación

- Cambios sintéticos se reflejan tras relectura controlada, sin duplicar runs ni
  perder historial/evidencia disponible; archivos parciales permanecen pendientes.
- Reiniciar el servicio reconcilia el origen; cerrar/abrir el navegador o reconectar
  por cursor recupera actividad sin pérdidas ni duplicados.
- UI conserva identidades/procedencia, muestra cambios/ausencias y evita mezclar
  bytes de versiones diferentes. Diagnósticos de lectura no declaran fallo de agente.
- Contratos/tipos, checks offline y build pasan; H0.3/H1.1/H1.2 siguen funcionando.

#### Fuera de alcance

H2 motor/supervisor/cola/bloqueo escritor, modo gestionado, adaptadores reales,
chat, permisos interactivos, SDKs y distribución. No ejecutar harness/agentes,
tests/instalaciones en ReferenceProject ni modificar configuración global. No usar runs
reales; cualquier smoke con proveedores exige autorización explícita de consumo
en una tarea posterior.

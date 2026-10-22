# P010 — Consolidación de la primera versión local

Objetivo y criterios en [ROADMAP](ROADMAP.md#p010--consolidación-de-la-primera-versión-local).
Decisión: [D141](DECISIONS.md#d141--p010-consolidación-de-la-primera-versión-local).
[Plan y alcance](phase/P010_PLAN_CONSOLIDACION.md).
[Contrato de T001](phase/P010-T001_CONTRATO_CONSOLIDACION.md), decisión
[D142](DECISIONS.md#d142--p010-t001-receta-typescript-proyección-de-runs-y-tarea-t011).

**Estado:** fase planificada el 2026-10-21. T001 completada el 2026-10-22: diseño y matriz inicial, sin producto.
Añade T011 (métricas y exportación sobre la proyección de runs). T002 completada el 2026-10-22 (D143): receta
`typescript-web-recipe-1` implementada y verificada offline. T003 completada el 2026-10-22 (D144): proyección
`run-projection-1` y vistas de runs sin decodificar historiales. T004–T011 pendientes; sin operación iniciada.
**Siguiente:** T011, métricas y vista previa de exportación sobre la proyección (depende de T003).

## Restricciones compartidas

- Una tarea acotada cada vez. Estados y criterios de este plan son trabajo pendiente, no capacidades entregadas.
- Desarrollo manual; no ejecutar el harness sobre este repositorio ni lanzar agentes, proveedores o smokes sin
  autorización explícita. El plan no concede instalaciones, red, servicios, commits, push ni publicación.
- Fixtures y checkouts de prueba sintéticos; ReferenceProject solo se lee. Sin datos privados, credenciales ni runs
  operativos en el repositorio; no tocar configuración global ni operar el Django hijo de P009.
- Conservar CAS, permisos separados, intención previa, idempotencia, locks, cuarentena y recuperación. No
  reescribir historiales/snapshots ni quitar protecciones de manifiestos al ejecutor normal.
- Modelos/migraciones con DDBB-DIAGRAM; flujos con docs/flows; API con OpenAPI/tipos en la misma tarea que cambie
  su implementación. No dibujar tablas o flujos pendientes como si ya existieran.
- Documentar decisiones duraderas en DECISIONS y evidencia por tarea en docs/phase. No ampliar el diseño ante
  contradicciones: identificarlas y resolverlas con el usuario. Detalles reversibles con criterio.
- Validaciones futuras según AGENTS y alcance de cada entrega. Los checks de este documento son previsiones;
  resultados, omisiones y límites se registran al ejecutarlos, sin reutilizar consentimientos agotados de P009.

## P010-T001 — Contrato de las correcciones y criterios de cierre

**Estado:** completada el 2026-10-22 ([contrato](phase/P010-T001_CONTRATO_CONSOLIDACION.md), D142). Cuatro
elecciones de diseño resueltas con el usuario: receta D119, `npm ci` y validaciones, proyección derivada y T011.
**Objetivo:** Dejar implementables las dos correcciones técnicas y precisar cómo se acreditará la primera versión.
**Alcance:** inventario de consumidores de `typescript-web` y de lecturas de runs; diseño de preparación inicial
confirmada, consultas acotadas, compatibilidad y recuperación; mapa inicial de los trece criterios globales.
**Rutas permitidas:** `docs/**`.
**Criterios de aceptación:**

- El contrato identifica el punto que puede generar `package.json`, sus archivos/comandos y confirmación,
  dependencias/locks, repetición, caídas y destinos existentes, sin abrir manifiestos al ejecutor normal.
- Se enumeran vistas/endpoints que hoy decodifican el historial completo y la estrategia para eliminarlos de
  la navegación. Se distingue lectura de UI de recuperación del motor; se identifican límites y orden estable.
- Se evalúan almacenamiento, migraciones, formatos, versiones congeladas, backup y recuperación si resultan
  afectados; no se elige una tecnología nueva por anticipación ni se cambia el requisito no funcional.
- La matriz inicial vincula los trece criterios de SPECIFICATION §10 con evidencia existente, vigencia y huecos,
  sin dar resultados aún no verificados. Cualquier cuestión de diseño bloqueante queda explícita.

**Validación:** contraste estático con código y decisiones, citas de tests y enlaces comprobados; sin suites.
**Entregables:** `docs/phase/P010-T001_CONTRATO_CONSOLIDACION.md`, con matriz inicial (§4).

## P010-T002 — Arranque confirmado de un proyecto TypeScript web

**Estado:** completada el 2026-10-22 ([entrega](phase/P010-T002_ARRANQUE_TYPESCRIPT.md), D143). Receta
`typescript-web-recipe-1` en el marco D119; sin migración ni cambios de API. **Depende de:** T001.
**Objetivo:** Que un proyecto `typescript-web` nuevo tenga un manifiesto inicial utilizable.
**Alcance:** implementar el contrato de T001 en creación/preparación, perfil y UI correspondientes; proteger
proyectos existentes y conservar el flujo documental D088.
**Rutas permitidas:** `src/harness_local/**`, `frontend/**`, `tests/**`, `examples/**`, `docs/**`.
**Criterios de aceptación:**

- Un recorrido sintético desde proyecto nuevo obtiene `package.json` y deja la primera tarea ejecutable con
  las validaciones del perfil, sin exigir que el ejecutor normal escriba archivos protegidos.
- Archivos, comandos, dependencias y cualquier instalación/red tienen vista previa y autoridad exacta;
  confirmar documentos no concede por sí solo instalar. Esta tarea no ejecuta instalaciones reales no autorizadas.
- Reenvío, caída y recuperación no duplican efectos ni sobrescriben bytes ajenos; destinos existentes/deriva
  bloquean con diagnóstico. Los proyectos previos conservan su comportamiento.
- Tests de fronteras/recuperación y documentación de flujo actualizados; esquema/API/versiones solo si procede.

**Validación:** pytest completa, unittest, Alembic, Node, tipos y build (resultados en la entrega §6); recorrido
sintético con node/npm falsos y variante opt-in con node/npm reales sobre `.local/npm-cache`, offline. Sin
proveedores ni smoke real.
**Entregables:** `docs/phase/P010-T002_ARRANQUE_TYPESCRIPT.md`, `examples/typescript-web-recipe.example.toml`.

## P010-T003 — Consultas de runs sin decodificar todo el historial

**Estado:** completada el 2026-10-22 ([entrega](phase/P010-T003_LECTURAS_RUNS.md), D144). Migración `0023`,
proyección escrita con el historial y comprobada en el backup; `GET /runs/{id}/cycles` pagina los ciclos.
**Depende de:** T001.
**Objetivo:** Cumplir SPECIFICATION §9 en las lecturas que alimentan las vistas de runs.
**Alcance:** repositorios/vistas de lectura, API y consumidores identificados en T001; compatibilidad histórica
y proyecciones o índices que el contrato justifique, sin cambiar el significado de la evidencia.
**Rutas permitidas:** `src/harness_local/**`, `frontend/**`, `tests/**`, `scripts/**`, `docs/**`.
**Criterios de aceptación:**

- Listados, detalle y páginas de intentos, validaciones, logs y diffs obtienen solo los datos necesarios con
  límites explícitos; ninguna de esas consultas requiere decodificar todo el historial del run.
- Un historial sintético grande demuestra la acotación con medidas de lectura/decodificación y resultados
  equivalentes; no basta con paginar en el frontend después de cargar el historial entero.
- Se conservan orden, paginación, evidencia exacta y formatos históricos legibles. Si hay proyección derivada,
  se prueba consistencia/recuperación y su preparación para datos previos sin reescribir el historial original.
- Backup/restauración, migraciones y cuarentena mantienen su contrato; paridad documental y API/tipos al día.

**Validación:** pytest completa, unittest, Alembic en SQLite temporal, OpenAPI/tipos, Node y build (resultados en la
entrega §6); medidas sobre un historial sintético de 26 MiB. Sin datos operativos ni migración de la instalación real.
**Entregables:** `docs/phase/P010-T003_LECTURAS_RUNS.md`.

## P010-T004 — Aclarar los marcadores opcionales de definición

**Estado:** pendiente. **Depende de:** T001.
**Objetivo:** Que definir un proyecto en una carpeta nueva no haga interpretar marcadores opcionales como requisitos.
**Alcance:** texto de plantilla/prompts y presentación de define-project según la observación de P009.
**Rutas permitidas:** `src/harness_local/core/engine/templates/**`, `frontend/**`, `tests/**`, `docs/**`.
**Criterios de aceptación:**

- Se explica qué marcadores son opcionales y qué hacer si no existen archivos previos en un proyecto nuevo.
- La aclaración mantiene documentos D088 obligatorios y confirmación por contenido; no da por implementado
  el código del proyecto ni modifica prompts ya congelados. Si cambia una plantilla, se respeta su versionado.
- QA con datos sintéticos de carpeta nueva y existente acredita el texto en su contexto.

**Validación:** (prevista) comprobaciones de plantilla pertinentes, Node/tipos/build si procede y QA visual autorizado.
**Entregables:** (previstos) `docs/phase/P010-T004_MARCADORES_DEFINICION.md`.

## P010-T005 — Presentar la evidencia de una fase cerrada

**Estado:** pendiente. **Depende de:** T001.
**Objetivo:** Distinguir documentos archivados y documentos vivos al consultar una fase cerrada.
**Alcance:** presentación de fase/check y lecturas documentales necesarias; observación de deriva de P009.
**Rutas permitidas:** `src/harness_local/**`, `frontend/**`, `tests/**`, `docs/**`.
**Criterios de aceptación:**

- Una fase cerrada muestra el resultado y la base histórica del check y permite identificar su archivo;
  renovar STATE/NEXT_STEPS tras cerrar no se presenta como fallo nuevo de aquel check.
- Se distingue una diferencia esperada de documentos vivos de una alteración real de evidencia. Los checks de
  fases abiertas conservan sus guardias; no se ocultan avisos reales ni se modifica un READY histórico.
- Casos sintéticos de fase abierta, cerrada sin sucesora, cerrada con sucesora y deriva real cubren la presentación.

**Validación:** (prevista) pytest de lecturas/contratos, Node/tipos/build y QA visual autorizado. Sin leer ni modificar
el estado operativo del Django hijo para completar la prueba.
**Entregables:** (previstos) `docs/phase/P010-T005_FASES_CERRADAS.md`.

## P010-T006 — Documentación de instalación y alcance soportado

**Estado:** pendiente. **Depende de:** T002–T005 y T011.
**Objetivo:** Que la documentación de la primera versión coincida con el producto entregado.
**Alcance:** README, instalación/operación, compatibilidad, ejemplos y límites; consolidación de los cambios de P010.
**Rutas permitidas:** `README.md`, `docs/**`, `examples/**`.
**Criterios de aceptación:**

- Versiones CLI contrastadas con el catálogo del código y D122, diferenciando lectura/escritura; no se anuncia
  compatibilidad con versiones no caracterizadas ni se cambia la configuración global.
- Instalación desde wheel, requisitos del servicio y del proyecto hijo, sesión local, backup/restauración y
  límites operativos quedan coherentes con ARCHITECTURE §9 y evidencia disponible.
- Se distinguen capacidades implementadas, verificadas offline, probadas con proveedores y pendientes. Se
  corrigen referencias obsoletas, incluidos formatos del historial/configuración/esquema cuando proceda.
- Se mantiene el significado de «primera versión local» sin convertirlo automáticamente en versión `1.0.0`,
  publicación o compatibilidad multiplataforma. Snapshots archivados e instrucciones históricas intactos.

**Validación:** (prevista) contraste estático, parsers, enlaces y revisión de ejemplos sin ejecutar sus comandos.
**Entregables:** (previstos) `docs/phase/P010-T006_DOCUMENTACION_VERSION.md`.

## P010-T007 — Matriz de aceptación global

**Estado:** pendiente. **Depende de:** T002–T006 y T011.
**Objetivo:** Evaluar la primera versión contra los trece criterios de SPECIFICATION §10.
**Alcance:** actualizar la matriz inicial, comprobar vigencia de evidencia y cubrir huecos mediante pruebas sintéticas
pertinentes. No repetir todas las operaciones reales de fases anteriores.
**Rutas permitidas:** `tests/**`, `frontend/tests/**`, `docs/**`.
**Criterios de aceptación:**

- Cada criterio tiene referencia precisa, alcance, método, resultado, fecha/base y limitaciones. Un resultado
  histórico se identifica como tal; la ausencia de evidencia no se convierte en aprobado.
- Recuperación, exclusión de escritor, permisos, invalidación de aceptación, cierre, importaciones y backup
  tienen cobertura trazable; se diferencia evidencia de producto de la de la aplicación Django hija.
- Se registran bloqueos y faltas de cobertura; fixes que cambien producto se acotan como tarea propia antes de
  continuar. Ningún criterio del alcance declarado se cierra solo porque su fase original figure completada.

**Validación:** (prevista) pruebas dirigidas a huecos identificados; sin proveedores, servicios operativos ni smokes.
**Entregables:** (previstos) `docs/phase/P010_MATRIZ_ACEPTACION.md`.

## P010-T008 — Propuesta de validación real complementaria y alcance

**Estado:** pendiente. **Depende de:** T006, T007.
**Objetivo:** Resolver qué evidencia adicional se necesita antes de declarar el alcance soportado de la versión.
**Alcance:** propuesta concreta para importaciones A/B y perfil Python/Django declarativo; decisión explícita de
ejecutar posteriormente o conservar esos límites. Esta tarea prepara la propuesta y no ejecuta el recorrido.
**Rutas permitidas:** `docs/**`.
**Criterios de aceptación:**

- Se diferencia evidencia sintética A/B, receta Django acreditada y perfil declarativo pendiente de D095;
  se concreta qué afirmación verificaría cada recorrido, evitando repetir la matriz de cuatro parejas sin motivo.
- Propuesta revisable con repositorios/datos sintéticos, destinos elegidos por el usuario, wheel fuera del
  checkout, versiones, proveedores/modelos/esfuerzos, comandos, red/instalaciones, puertos, límites de consumo,
  parada, recuperación, evidencia saneada y limpieza. Las elecciones pendientes se declaran, no se inventan.
- Antes de T010 queda una decisión explícita del usuario sobre ejecutar o aplazar y sobre el alcance que puede
  anunciarse. Si se ejecuta, se añade una tarea operativa acotada y autorizada con su evidencia antes del cierre;
  si se aplaza, documentos y dictamen conservan la falta de validación real. No hay aprobación por silencio.
- No se reutiliza el consentimiento de P009 ni se opera su hijo o este repositorio con el harness.

**Validación:** (prevista) revisión de alcance/evidencia y enlaces; sin proveedores, instalaciones, servicios o smokes.
**Entregables:** (previstos) `docs/phase/P010-T008_PROPUESTA_VALIDACION_REAL.md`.

## P010-T009 — Verificación final del paquete y revisión de salida

**Estado:** pendiente. **Depende de:** T002–T008, T011 y las correcciones/evidencias adicionales que se acuerden.
**Objetivo:** Acreditar el estado final del producto y emitir un dictamen de cierre revisable.
**Alcance:** checks offline finales, QA de las pantallas modificadas y verificación del wheel en entorno temporal;
contraste del paquete final con la matriz de aceptación y el alcance real decidido.
**Rutas permitidas:** `docs/**`; incidencias de código se corrigen en tareas acotadas previas, no en este informe.
**Criterios de aceptación:**

- unittest, pytest, Node, tipos/build y Alembic pertinentes sobre una base identificada, con resultados y omisiones;
  no repetir suites ya correctas si no hay cambios o incertidumbres que lo justifiquen.
- Wheel con UI/migraciones verificado fuera de la instalación operativa, con CLI falsas y datos sintéticos.
  Las instalaciones/servicios o smokes que requiera el recorrido se concretan y autorizan antes de ejecutarlos;
  ninguna dependencia ausente dispara descarga implícita.
- QA visual pertinente y pruebas de lecturas acotadas acreditadas; matriz de aceptación y límites actualizados.
- Revisión expresa cada criterio de ROADMAP como cumplido, pendiente o bloqueado, con evidencia; un fallo del
  alcance declarado impide pasar a T010. No se declara la versión terminada antes del dictamen favorable.

**Validación:** (prevista) comandos de AGENTS y recorrido de distribución aplicable, dentro del alcance autorizado.
**Entregables:** (previstos) `docs/phase/P010-T009_VERIFICACION_FINAL.md` y `docs/phase/P010_REVIEW.md`.

## P010-T010 — Cierre documental de P010 y de la primera versión

**Estado:** pendiente. **Depende de:** T009 con dictamen favorable y decisión de alcance de T008 resuelta.
**Objetivo:** Dejar una fotografía final verificable de la primera versión local y sus límites.
**Alcance:** síntesis y archivo documental de P010, referencias vigentes, STATE/NEXT_STEPS y ROADMAP.
**Rutas permitidas:** `README.md`, `docs/**`.
**Criterios de aceptación:**

- SUMMARY y REVIEW vinculan entregas, criterios globales, paquete verificado, evidencia real y límites; no se
  confunden planificación, implementación y operación. No hay tareas obligatorias pendientes ocultas.
- Se archivan STATE/NEXT_STEPS y artefactos de fase preservando bytes y referencias; se actualizan documentos
  vivos sin reescribir P001–P009. No se inventa una sucesora.
- El cierre manual queda separado del check READY del producto; no registra ni ejecuta este repositorio,
  opera proyectos hijos, crea tags/commits, publica o cambia versiones por sí mismo.

**Validación:** (prevista) parsers/enlaces, presupuestos, manifiesto de archivo por hashes y diff documental.
**Entregables:** (previstos) `docs/phase/P010_CIERRE.md` antes de archivar y `docs/archive/phase-010/` al cerrar.

## P010-T011 — Métricas y exportación sin decodificar historiales

**Estado:** pendiente. **Depende de:** T003. Añadida por T001 (D142); precede a T006.
**Objetivo:** Cumplir SPECIFICATION §9 en las vistas que no son de runs y hoy decodifican historiales.
**Alcance:** métricas (`summary`, `tasks`, `validations`) y vista previa de exportación documental sobre la
proyección `run-projection-1` de T003 y `managed_attempts`; API/tipos y cliente si cambian. Las lecturas del motor
no cambian.
**Rutas permitidas:** `src/harness_local/**`, `frontend/**`, `tests/**`, `docs/**`.
**Criterios de aceptación:**

- Las vistas de métricas y la vista previa de exportación no llaman a `load_history` ni seleccionan `history_json`;
  agregan en SQL con paginación y límites explícitos.
- Resultados iguales a los actuales sobre datos sintéticos con formatos 1–8 e historiales grandes, con medidas.
- Ninguna tabla nueva sin medición que la justifique; si se añade, paridad en DDBB-DIAGRAM y backup.
- Bloques de STATE, checks y exportación confirmada conservan su contenido y su autoridad.

**Validación:** (prevista) pytest de métricas/exportación y regresiones; Node/tipos/build si cambia el cliente.
**Entregables:** (previstos) `docs/phase/P010-T011_METRICAS_SIN_HISTORIAL.md`.

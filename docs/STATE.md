# Estado de desarrollo

Actualizado: 2026-10-11.

## Existe

- Especificación y backlog aceptados por el usuario como base de desarrollo.
- Documentación de arranque, decisiones y contratos de trabajo para Codex/Claude Code.
- Carpeta raíz: `$HOME/Documents/projects/my_harness`.
- H0.1 completado: [inventario de procedencia y separación núcleo/perfil](discovery/BASELINE.md),
  [formatos y contratos mínimos legacy](discovery/LEGACY_FORMATS.md) y
  [manifiesto SHA-256](discovery/baseline.json) de 21 archivos de referencia.
- Cinco [escenarios sintéticos](../tests/fixtures/legacy/README.md): aceptación,
  REVISE, BLOCKED, interrupción y cierre. Incluyen historial, campos no registrados,
  archivos ausentes y una review deliberadamente parcial; cuatro snapshots de esquemas.
- Cuatro comprobaciones offline con biblioteca estándar en
  `tests/test_legacy_fixtures.py`; sin dependencias instaladas para esta entrega.
- H0.2 completado: [versiones, matriz de capacidades y autenticación](discovery/H0.2_COMPATIBILITY.md),
  con [snapshot de restricciones y resolución](discovery/h0.2-version-metadata.json).
  Python 3.14.4, uv 0.12.19, Node 24.15.0 y npm 11.12.1; pins directos
  documentados, TypeScript 5.9.3 por compatibilidad con openapi-typescript.
- CLI instaladas verificadas por versión/help: Codex 0.161.0 y Claude Code 2.1.295.
  Usuario confirma suscripciones propias mediante CLI ya autenticadas; Codex
  reporta ChatGPT. El status de Claude en sandbox no acredita sesión: no se
  interpreta como ausencia de login en el Mac. App Server/SDK no integrados.
- Ocho [muestras de streams sintéticos](../tests/fixtures/streams/README.md),
  sonda incremental bajo `tests/stream_probe.py` y ocho checks nuevos offline
  en `tests/test_stream_contracts.py`; esa entrega no incorporó código del producto.
- H0.3 completado: [esqueleto y verificaciones](discovery/H0.3_SKELETON.md),
  [alcance original](discovery/H0.3_SCOPE.md). Paquete Python bajo `src/harness_local`:
  núcleo de biblioteca estándar, adaptador falso, API FastAPI/Pydantic y
  persistencia SQLAlchemy/SQLite con migración Alembic `0001_simulations`.
- UI React/TypeScript/Vite que crea y consulta simulaciones sintéticas persistidas.
  Tipos del cliente generados desde OpenAPI y versionados, sin contratos manuales duplicados.
- Dependencias reales instaladas en `.venv` / `frontend/node_modules`, locks
  `uv.lock` / `frontend/package-lock.json`. Pins H0.2 usados conservados;
  backend de paquete `uv_build==0.12.19`. Comandos comprobados en README/AGENTS.
- 116 casos de producto en `tests/product/`; pytest ejecuta 128 pruebas en total.
  La comprobación ligera anterior conserva sus 12 checks sin dependencias.
- H1.1 completado: [importación legacy y verificaciones](discovery/H1.1_IMPORT.md),
  [alcance original](discovery/H1.1_SCOPE.md). Lector local explícito de
  `.harness/runs`, documentos de estado/fase y archivo documental de fases;
  núcleo de biblioteca estándar y CLI `python -m harness_local.cli`.
- Índice SQLite de observación reconstruible: `legacy_sources`, `legacy_runs`,
  `legacy_artifacts`, migración `0002_legacy_index`. Unicidad por raíz canónica
  y ruta; identidad del run y SHA-256 de bytes leídos, sin crear intentos inferidos.
  Conserva JSON/campos desconocidos, ausencias, null, cero y diagnósticos locales.
- Importación y consulta de resumen por CLI, sin observador ni navegación web.
  Relectura explícita actualiza parciales/cambios; evidencia desaparecida queda
  ausente sin payload obsoleto. Los originales son autoridad y no se modifican.
  Texto/logs/diffs se indexan por ruta/hash/tamaño, sin duplicar sus cuerpos.
- H1.2 completado: [navegación y verificaciones](discovery/H1.2_NAVIGATION.md),
  [alcance original](discovery/H1.2_SCOPE.md). Consultas HTTP de lectura y UI
  por proyecto/origen, fase, tarea y run observado, con timeline de metadatos,
  revisiones/hallazgos/preguntas, bloqueos operativos, comandos y telemetría.
- Listas y entradas estructuradas paginadas, con ruta/hash/JSON pointer y
  distinción ausencia/null/cero. Selección solicitada separada de modelos/consumo
  reportados; coste equivalente API separado de factura/cuota, sin sumar wrappers.
- Contenido original servido como texto plano por tramos UTF-8, previa comprobación
  de ruta, archivo regular y SHA-256/tamaño. Cambios, ausencias, enlaces, errores
  locales y límites explícitos no sirven bytes nuevos como versión indexada.
  Documentos de estado y archivo de fases accesibles sin certificar cierre/Git.
  Esquema `0002_legacy_index` conservado; no hay migración nueva ni entidades gestionadas.

- H1.3 completado: [observación y verificaciones](discovery/H1.3_OBSERVATION.md),
  [alcance original](discovery/H1.3_SCOPE.md). Observación opt-in persistida por origen;
  polling agrupado, lecturas incrementales y reconciliación al iniciar/periódica.
- Migración `0003_legacy_observation`: control/diagnóstico por origen y feed de
  actualización atómico con el índice. JSON paginado/SSE con cursor estable,
  Last-Event-ID, deduplicación y recuperación tras reinicio; sin event sourcing del motor.
- UI actualiza listas y detalle seleccionado, conserva identidades, recupera actividad
  con navegador cerrado y reinicia tramos al actualizar, ocultando hashes diferentes.
  Lecturas de evidencias regulares por descriptores, sin enlaces/FIFO y máximo 64 MiB.

- H2.1 completado: [extracción aislada y verificaciones](discovery/H2.1_ENGINE.md),
  [alcance original](discovery/H2.1_SCOPE.md). `core/engine` contiene contexto explícito,
  planificación, evidencia/política, validación, review, aceptación y flujo offline.
- `ProjectContext` y puertos de biblioteca estándar independientes de web, SQLite,
  proveedores y stack. Perfil ReferenceProject declarativo separado; solo adaptadores falsos.
- Historial/snapshots inmutables en memoria, sesiones nuevas por invocación y
  presupuesto de correcciones conservado al revalidar/reintentar. Stops separados
  de veredictos; errores sin fallback. ACCEPT no supera política/tests/evidencia.
- Extracción sin entrada API/CLI, escritores Git ni persistencia gestionada:
  `acceptance_ready` solo indica elegibilidad offline. Esquema H1.3 conservado.

## Todavía no existe

Intentos gestionados, motor conectado a ejecución real, supervisor, cola, bloqueo por checkout,
adaptadores reales, permisos interactivos, chat ni distribución.
La navegación H1.2 muestra evidencia legacy;
el recorrido H0.3 solo guarda simulaciones, que no representan intentos reales
ni aceptación de tareas. Ninguna integración
con proveedores se ha ejecutado.

## Trabajo activo

H0, H1 y H2.1 completados. Próxima tarea: H2.2,
detallada en `NEXT_STEPS.md`, pendiente de una nueva sesión dirigida por el usuario.

## Verificación de H0.1

- `python3 -m unittest discover -s tests -p 'test_*.py' -v`: 4 checks correctos,
  ejecución inferior a 0,1 segundos en este equipo. Parseo/inventario, campos de
  contrato, identidades/referencias, coherencia de escenarios y hashes de esquemas.
- Los 21 archivos inventariados coinciden con el commit
  `5be3b8a1328f7725a0f81c98af4f365e3528a767`; cambios de aplicación del origen
  registrados por separado. Revisados los cambios locales de esta entrega.
- Inspección estática y comprobación offline; no se abrió ningún run real ni se
  ejecutaron harness, helpers, instalaciones o tests de ReferenceProject, ni proveedores.
- Límites: no es auditoría exhaustiva ni validador JSON Schema completo. No se
  probó importador, versiones/autenticación CLI, streaming robusto, commits ni cierre real.

## Verificación de H0.2

- `python3 -m unittest discover -s tests -p 'test_*.py' -v`: 12 checks correctos
  (4 H0.1 + 8 H0.2), menos de 0,1 segundos en este equipo. Incluye cortes JSON
  y UTF-8, errores, salida malformada, falta de terminal, campos/eventos futuros,
  preservación de bytes y distinción ausencia/null/cero.
- Metadatos públicos PyPI/npm consultados; resolución conjunta Python para
  CPython 3.14.4/macOS ARM64 solo wheels: 27 paquetes. Resolución npm con engines
  y peers estrictos: 102 entradas, package-lock-only e ignore-scripts.
  Ambos exit code cero en directorios temporales, sin instalaciones ni build.
- Autenticación solo en lectura con campos filtrados en memoria; sin extraer
  credenciales, imprimir identidades o modificar login/configuración global.
  Decisiones D007–D009; alcance original conservado en `discovery/H0.2_SCOPE.md`.
- Revisados diff y whitespace. Sin agentes, harness, proveedores, tests de
  ReferenceProject ni SDK. Límites: no se probaron cuota/modelos, reintentos internos
  de CLI, cancelación, permisos vivos, aplicación ni dependencias importadas.

## Verificación de H0.3

- `uv run --frozen --offline pytest -q`: 26 pruebas y 121 subtests correctos,
  12 casos anteriores y 14 H0.3. Núcleo importado con `python -S`, frontera de
  imports, errores sin reintentos, validación HTTP y persistencia tras reinicio.
- Los 12 checks de biblioteca estándar continúan pasando sin dependencias.
  Upgrade/downgrade/upgrade y `alembic check` correctos en SQLite sintética;
  WAL, foreign keys y revisión de esquema comprobados.
- Instalación local con locks, regeneración OpenAPI/tipos, TypeScript y build
  Vite comprobados. Uvicorn/API/UI compilada probados desde Chrome: crear
  simulación, leer sus tres eventos, reiniciar el servicio y recuperar el mismo ID.
- Vite arrancado en :5173, con solicitudes de historial al proxy/API respondidas
  200. Comprobación del contenido por accesibilidad sobre la UI compilada;
  la captura de pantalla falló por ScreenCaptureKit. Servicios de prueba detenidos.
- Aviso upstream: Starlette 1.7.0 depreca TestClient con HTTPX 0.28.1 y recomienda
  HTTPX2; se conserva el pin H0.2 y el aviso visible, sin fallos de pruebas.
- Diff/whitespace revisados; decisiones D010–D011. Sin commits, agentes,
  harness, proveedores, importación real ni cambios globales. Bases/cachés locales
  ignoradas; no se tocó el entorno activo externo que uv ignoró.
- Límites: no se probaron concurrencia, intentos reales, cancelación, cuota,
  otros sistemas, importador ni motor. H1.1 queda pendiente.

## Verificación de H1.1

- `uv run --frozen --offline pytest -q`: 40 pruebas y 121 subtests correctos;
  14 casos nuevos de importación/CLI/migración y regresión completa de H0.
  Los 12 checks de biblioteca estándar continúan pasando. El nuevo núcleo
  se importa con `python -S` y conserva la frontera de dependencias.
- Cinco fixtures importados dos veces mediante CLI en SQLite sintética local:
  5 orígenes, 7 runs y 105 entradas (89 disponibles, 1 pendiente, 15 ausentes).
  Resumen idéntico tras reimportar/consultar.
- Comprobados hashes/payloads y mtime/bytes de origen sin cambios, ausencia/null/
  cero, campos futuros, JSON/UTF-8 inválidos, JSONL parcial, errores de lectura,
  enlaces no seguidos, desaparición de archivo y relectura tras completar JSON.
  La consulta no relee el origen ni oculta el carácter pendiente del índice.
- Upgrade/downgrade a H0.3/upgrade, reconstrucción de índice y `alembic check`
  correctos; claves foráneas/WAL y simulaciones conservadas. CLI exige migración
  explícita y rechaza SQLite dentro del checkout de origen antes de conectar.
- TypeScript y build Vite correctos; OpenAPI sigue sincronizado por la prueba
  existente. Regresión de API/UI estática y persistencia tras reinicio correctas
  mediante TestClient, sin arrancar servidores ni repetir el recorrido en navegador.
- Diff/whitespace revisados; decisión D012. Sin red, proveedores, agentes, harness,
  runs reales, acceso a ReferenceProject ni configuración global. Se usa `.venv` local;
  uv ignora el entorno activo externo. Persiste el aviso upstream HTTPX/Starlette.
- Límites: no hay watcher/SSE, navegación H1.2, entidades gestionadas, certificación
  de aceptación/commit, migración a modo gestionado ni prueba de escritores
  concurrentes. Solo fixtures sintéticos y relecturas manuales; H1.2 no iniciado.

## Verificación de H1.2

- `uv run --frozen --offline pytest -q`: 59 pruebas y 121 subtests correctos;
  19 casos nuevos, regresión completa H0/H1.1, núcleo con `python -S`, frontera
  de imports, OpenAPI sincronizado y checks de migración existentes correctos.
  Los 12 checks de biblioteca estándar continúan pasando sin dependencias.
- Cinco escenarios recorridos por HTTP: proyecto/fase/tarea/run/artefacto,
  paginación sin pérdidas ni duplicados, hash/contenido/mtime de copias sintéticas
  conservados. REVISE → ACCEPT, hallazgos, preguntas, stop operativo, revisión
  parcial y resultados ausentes se mantienen separados; READY no acredita cierre.
- Comprobados ausencia/null/cero, selección antigua ausente frente a request
  posterior, modelos reportados, duración al nivel del comando, logs/diffs UTF-8
  por tramos y archivo vacío. Truncamiento estructurado y límite de verificación
  explícitos; rutas desconocidas y parámetros fuera de límites rechazados.
- Cambios antes/durante lectura, desaparición, enlaces de archivo/directorio/raíz,
  FIFO y denegación local no sirven contenido nuevo ni cambian el juicio del agente.
  Consulta no reimporta; metadata/texto/JSONL no cargan cuerpos del índice al listar
  o servir bytes. Los payloads JSON estructurados se cargan por artefacto.
- OpenAPI/tipos regenerados, TypeScript y build Vite correctos. Chrome sobre UI
  compilada con SQLite/copias locales sintéticas: cinco escenarios, historial,
  revisión parcial, preguntas, telemetría, duración, documentos archivados,
  paginación de artefactos/log UTF-8 y cambio de hash visible sin bytes nuevos.
  Captura de UI inspeccionada; simulación H0.3 creada correctamente. Servicio detenido.
- Diff/whitespace revisados; decisión D013. Sin red externa, proveedores, agentes,
  harness, runs reales, acceso a ReferenceProject ni configuración global. uv sigue
  ignorando el entorno activo externo; persiste el aviso upstream HTTPX/Starlette.
- Límites: solo macOS actual y fixtures sintéticos; sin certificación frente a
  escritores concurrentes, pruebas de carga, otros sistemas ni proveedor real.
  Verificar cada tramo relee el archivo para su hash (máximo 64 MiB); no hay cache,
  watcher/SSE ni actualización automática. H1.3 no iniciado.

## Verificación de H1.3

- `uv run --frozen --offline pytest -q`: 80 pruebas y 121 subtests correctos;
  21 casos nuevos y regresión completa. Los 12 checks de biblioteca estándar,
  frontera de imports, OpenAPI/tipos, TypeScript y build Vite correctos.
- Cinco escenarios, lectura incremental sin releer disponibles idénticos,
  JSON/JSONL parcial/completado, cambios durante lectura, agrupación, desaparición,
  reaparición, raíz ausente/enlace, FIFO y diagnóstico local sin resultados inferidos.
- Persistencia opt-in, desactivación durante lectura, reconciliación antes de servir,
  actualización sin navegador y reinicio idempotente comprobados. Eventos e índice
  revierten juntos ante fallo; importaciones concurrentes idénticas publican una vez.
- Migración ida/vuelta con H1.2 y checks existentes conservan índice/simulaciones;
  `alembic check` correcto. SSE valida cursores/Last-Event-ID y recupera 10.000 filas
  por lotes sin huecos/duplicados; espera de cambio en vivo y cierre acotado correctos.
- Chrome con copias/base sintéticas en :8014: activar, partial → available sin recargar,
  selección conservada, hash nuevo en log desde byte 8192 reiniciado a byte 0,
  cerrar/abrir con actividad IDs 1–10 únicos y reconexión tras reinicio.
  Captura inspeccionada; apagado normal SIGTERM con SSE abierto y servicio detenido.
  :8013 ocupado no se tocó. Ctrl+C del ejecutor produjo cancelación, no certificó apagado.
- Diff/whitespace revisados; decisión D014. Sin agentes, harness, proveedores,
  runs reales, ReferenceProject ni configuración global. Consulta pública de documentación
  SSE; verificaciones offline. uv ignora el entorno externo; aviso HTTPX/Starlette sigue.
- Límites: macOS actual/un proceso, polling sin snapshot de varios archivos ni garantía
  de capturar versiones sobrescritas entre ciclos. Cache JSON/JSONL y feed sin retención;
  sin medición de memoria/latencia bajo carga. Restauraciones que reutilicen IDs exigen
  limpiar cursor local. No hay motor/entidades gestionadas; H2.1 no iniciado.

## Verificación de H2.1

- `uv run --frozen --offline pytest -q`: 128 pruebas y 121 subtests correctos;
  48 casos nuevos de caracterización en repositorios Git temporales y regresión
  completa H0/H1. Los 12 checks de biblioteca estándar continúan pasando.
- Núcleo importado con `python -S` y frontera de imports ampliada recursivamente.
  OpenAPI sincronizado; migraciones ida/vuelta y `alembic check` existentes correctos.
  TypeScript y build Vite correctos, sin cambios en API/UI/esquema.
- Planificación documental/agente, selección explícita por corrección, peticiones
  frescas, snapshots independientes, historial conservado y límite de correcciones
  al revalidar/reintentar. Errores/parciales no generan fallback/review posterior.
- Caracterizados stops de entorno/permisos y ciclos sin progreso, con preguntas
  y reviews separadas. ACCEPT inelegible ante tests/política fallidos, preguntas,
  grants o cambios de evidencia; no restaura archivos ni prepara commits.
- Preparación/baseline ReferenceProject solo mediante runner falso; perfil genérico usa
  el mismo núcleo. Comandos argv/cwd/entorno/timeout, deduplicación y duración
  ausente conservados. No se infiere confianza ni permiso real de sus prefijos.
- Referencia leída estáticamente, sin importar/ejecutar; hashes de motor/config,
  workflow tests y helper coinciden con H0.1. Diff/whitespace revisados; decisión D015.
  Sin agentes, harness, proveedores/red, runs reales, servicios nuevos ni cambios
  globales. uv ignora el entorno externo; persiste el aviso HTTPX/Starlette.
- Límites: solo adaptadores falsos, historial en memoria y rutas sintéticas
  explícitas, sin captura Git completa ni snapshot atómico. Formatter/helpers
  declarados sin ejecución real; no hay cola, exclusión, cancelación, permisos
  interactivos, commits o fases gestionadas. H2.2 pendiente, sin iniciar.

## Coordinación

Desarrollo manual con el usuario. Una única sesión implementadora sobre los mismos archivos a la vez. La otra herramienta puede revisar una entrega terminada.

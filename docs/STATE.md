# Estado de desarrollo

Actualizado: 2026-10-12.

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
- CLI instaladas verificadas en H0.2 por versión/help: Codex 0.161.0 y Claude Code 2.1.295.
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
- 199 casos de producto en `tests/product/`; pytest ejecuta 211 pruebas en total.
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

- H2.2 completado: [persistencia, cola y verificaciones](discovery/H2.2_PERSISTENCE.md),
  [alcance original](discovery/H2.2_SCOPE.md). Migración `0004_managed_queue`:
  autoridad gestionada en tablas propias de runs/intentos/jobs/eventos/locks.
- Journal opcional del motor y codec JSON versionado; intención previa a efectos,
  estados/historial/resultados/eventos atómicos, snapshots congelados y presupuesto
  conservado tras reiniciar. Versiones declaradas y datos ausentes diferenciados.
- Jobs idempotentes por clave/payload, FIFO entre elegibles y exclusión por raíz
  canónica; checkouts distintos pueden ejecutar concurrentemente. Supervisor
  explícito `run_once`, heartbeat/lease y transacciones cortas, solo puertos falsos.
- Lease vencido/fallo conserva lock y recuperación pendiente. Confirmación explícita
  del escritor detenido, con job/token/versión/evidencia, libera atómicamente;
  intentos inciertos quedan interrumpidos y reservan presupuesto. Sin llamadas ocultas.
- API/CLI/UI conservan H0/H1; ninguna entrada gestionada ni arranque automático.
  No se activan proyectos legacy gestionados ni commits de producto.

- H2.3 implementado y verificado offline: [adaptadores, procesos y límites](discovery/H2.3_CLI.md),
  [alcance original](discovery/H2.3_SCOPE.md). Codex planificador/revisor y Claude
  ejecutor por inyección explícita, versiones/help comprobados en lectura.
- Historial CLI en codec formato 2; formato 1 H2.2 sigue leyéndose sin reemplazar
  sus resultados anteriores. Configuración congelada por hash, argv/cwd/entorno/timeout y selección explícitos;
  sesiones nuevas y permisos de próximo intento. Sin fallback/reinvocación del adaptador.
- JSONL incremental y bytes stdout/stderr con fsync/hash/rango en artefactos externos;
  eventos futuros y datos ausentes/null/cero conservados. Resultados completos,
  parciales, inválidos, fallidos, timeout y cancelados persistidos.
- Migración `0005_cli_processes`: propietario del supervisor y grupos por intento.
  Gate de lanzamiento exige identidad confirmada antes de ejecutar la CLI.
  Cancelación TERM/KILL y liberación condicionada a liveness local conservadora;
  PID/grupo vivo, host distinto o permiso denegado mantienen el checkout bloqueado.
- `scripts/smoke_cli.py` preparado, con guardia explícita de consumo, modelos y
  esfuerzos obligatorios; hasta tres invocaciones, 60 s cada una, herramientas
  vacías y checkout desechable. **Smoke autorizado ejecutado: primera CLI Codex
  fallida por configuración reservada; Claude/revisor no lanzados (D018).**
  [Resultado real y evidencias](discovery/H2.3_SMOKE.md); sin relanzamiento.
- Corrección H2.3 verificada offline: adaptador `cli-2` elimina los overrides
  reservados y conserva el proveedor integrado OpenAI; límites de retries internos
  registrados como desconocidos. Fakes rechazan el argv antiguo, y jobs `cli-1`
  no ejecutan silenciosamente el nuevo comportamiento. [Entrega](discovery/H2.3_CONFIG_FIX.md).
- Nuevo smoke `cli-2` autorizado y ejecutado el 2026-10-12: Codex planificador
  COMPLETE con terminal/uso, Claude FAILED por configuración MCP inválida;
  revisor no lanzado. Parada conservada, sin relanzar ni corregir en esta entrega.
  [Resultado y evidencias](discovery/H2.3_SMOKE_RETRY.md), D020.
- Corrección MCP Claude verificada offline: `cli-3` usa `{"mcpServers":{}}`
  con modo estricto y conserva permisos/configuración aislados. Regresión
  independiente reproduce el rechazo de `{}` antes de inferencia simulada;
  jobs congelados `cli-2`/`cli-1` bloqueados sin reescribir historial anterior.
  [Contrato y verificaciones](discovery/H2.3_MCP_FIX.md), D021. Esa entrega no ejecutó smoke.
- Smoke `cli-3` autorizado y ejecutado: planificador Codex COMPLETE con terminal/JSON;
  Claude acepta MCP vacío, pero FAILED por `authentication_failed`, con terminal
  de error y exit 1. Revisor no lanzado, sin login/corrección/relanzamiento.
  [Resultado y evidencias](discovery/H2.3_SMOKE_CLI3.md), D022.

## Todavía no existe

Recorrido CLI real completo exitoso con ambos proveedores ni entradas gestionadas API/CLI/UI,
captura Git completa/worktrees/commit de producto, activación/migración de proyectos
gestionados, interfaz gestionada, permisos interactivos, chat ni distribución.
La navegación H1.2 muestra evidencia legacy;
el recorrido H0.3 solo guarda simulaciones, que no representan intentos reales
ni aceptación de tareas. El primer smoke real lanzó Codex y falló al cargar
configuración; no acredita inferencia, autenticación, cuota ni acceso al modelo.
Los nuevos smokes completan el transporte del planificador Codex. D020 falló al
validar MCP; D022 supera ese rechazo y falla en autenticación Claude con terminal
de error, sin inferencia acreditada. Revisor no probado.

## Trabajo activo

H0, H1, H2.1 y H2.2 completados. H2.3 implementado y verificado offline.
Smoke `cli-3` D022 concluido conforme a la rama de error: planificador Codex
COMPLETE; ejecutor Claude FAILED por autenticación, MCP vacío aceptado;
revisor no lanzado. [Informe](discovery/H2.3_SMOKE_CLI3.md).
Históricos D018/D019/D020/D021 y preflight conservados. Consentimiento D022
agotado al fallo; sin login, corrección ni nueva inferencia autorizados.
Siguiente tarea acotada: diagnóstico de autenticación Claude en lectura según
NEXT_STEPS, sin iniciarlo. Transporte real completo sigue pendiente.
H2.4 no iniciado.

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

## Verificación de H2.2

- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`: 158 pruebas
  y 121 subtests correctos; 30 casos H2.2 y regresión completa. Los 12 checks
  ligeros de biblioteca estándar, núcleo con `python -S` y frontera de imports pasan.
- Reinicio sobre la misma SQLite conserva historial, contratos/contexto/prompts/
  versiones, resultados, eventos y presupuesto. Revalidar conserva trabajo;
  reintentar usa intento fresco y presupuesto anterior, también ante fallo/caída.
- Ocho solicitudes/hilos concurrentes y seis procesos Python sintéticos independientes
  producen un run/job y una sola ejecución falsa. Alias comparten lock; checkouts
  distintos ejecutan simultáneamente mientras una segunda acción de la misma raíz espera.
- Escritura SQLite y heartbeat completados mientras un adaptador espera: sin
  transacción SQL larga. Expiración/fallo de heartbeat, tokens/lecturas obsoletos y
  confirmaciones duplicadas no duplican efectos ni liberan locks silenciosamente.
- Fallos inyectados en cola/claim/intención/resultado/comandos/finalización prueban
  rollback atómico y conservación de intención desconocida. Corrección interrumpida
  preserva archivos y reserva presupuesto; recuperación exige conciliación explícita.
- Migración/check/ida-vuelta H1.3 conservan índice legacy/simulaciones. OpenAPI/tipos
  regenerados sin diferencias; TypeScript y build Vite correctos. Diff/whitespace revisados;
  decisión D016. Commit solicitado por el usuario al terminar esta entrega.
- Sin red, agentes/proveedores, harness de desarrollo, servicios/navegador nuevos,
  datos reales, ReferenceProject ni cambios globales. uv ignora su entorno externo;
  se conserva el aviso conocido Starlette/HTTPX.
- Límites: exclusión cooperativa de raíces canónicas en una base local; no cubre
  escritores externos/otra base/raíces anidadas. `confirm_stopped` registra evidencia
  del llamante, sin detectar procesos reales. No hay UI/CLI gestionada, blobs pesados,
  cancelación real, worktrees/commit ni exactamente una vez externa. H2.3 sin iniciar.

## Verificación de H2.3

- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`: 204 pruebas
  y 121 subtests correctos; 46 casos nuevos y regresión completa. Los 12 checks
  ligeros pasan; núcleo con `python -S` y frontera de imports conservados.
- Procesos Python sintéticos prueban argv/cwd/entorno, sesiones frescas, splits
  JSON/UTF-8, finales/errores/cuota sintéticos, eventos futuros, salida inválida,
  terminal ausente, timeout, cancelación y conservación exacta de stdout/stderr.
- Captura disponible antes del exit; eventos por rango/hash y archivos fsync.
  Errores detienen el flujo sin reviewer ni llamada adicional. Recorridos completos
  documental/agente falso, historial tras reinicio y presupuesto con retry explícito.
- Cancelación del grupo con hijo resistente; caída real de supervisor sintético y
  reapertura SQLite conservan bytes/lock. Ni lease vencido ni muerte del propietario
  liberan una CLI falsa viva. Host/liveness inciertos bloquean; gate sin registro
  no ejecuta efectos. Fallos de persistencia detienen y conservan intención.
- Migración 0005/check/ida-vuelta a 0004 preserva historial previo. Regresión de
  migraciones completas, legacy/simulaciones y OpenAPI correcta. OpenAPI/tipos
  regenerados sin diferencias; TypeScript y build Vite correctos. Diff revisado.
- Preflight local final: Codex 0.162.1 y Claude Code 2.1.295, sin autenticación,
  credenciales ni inferencia. Fuentes oficiales consultadas para configuración/
  streaming. 0.161.0 permanece soportada explícitamente como baseline histórica;
  la versión instalada 0.162.1 se selecciona/valida sin sustitución automática.
  `ps` restringido por sandbox requirió permiso de lectura; la solución
  usa liveness por señal 0, sin dependencia de ps ni señales a PIDs recuperados.
- Sin agentes/proveedores, smoke real, harness de desarrollo, acceso a ReferenceProject,
  instalaciones/red de dependencias, servicios nuevos, push o cambios globales.
  uv ignora el entorno externo; persiste el aviso conocido Starlette/HTTPX.
- Límites: POSIX/macOS local, una base cooperativa, procesos que permanezcan en su
  grupo. PID reutilizado se considera vivo conservadoramente; procesos escapados,
  permisos de SO externos y aislamiento de Claude no quedan certificados. Codex
  solicita retries HTTP/stream cero; retries internos Claude no controlables ni
  caracterizados con cuenta real. Artefactos sin retención/GC ni UI de contenido.
- Al cerrar la entrega offline, smoke preparado **pendiente de autorización
  explícita y selecciones** (ejecutado posteriormente: sección siguiente);
  no se presentan los procesos sintéticos como CLI real ni se inicia H2.4.
  Decisión D017. Commit de esta entrega solicitado por el usuario.

## Verificación real H2.3 — 2026-10-11

- Git inicial limpio en `7a805c0`; script, D017 y criterios revisados.
  Autorización explícita recibida y selección delegada por el usuario (D018):
  Codex `gpt-6-luna`/`low`, Claude `claude-sonnet-4-6`/`low`, fijados antes de lanzar.
- Preflight solo versión/help correcto: Codex 0.162.1 y Claude Code 2.1.295;
  hashes del help coinciden con la entrega. Ayuda/guardia del smoke comprobadas.
- Regresión offline: 204 pruebas pytest y 121 subtests, 12 checks ligeros correctos.
  Persiste el aviso Starlette/HTTPX; uv ignora el entorno externo sin usarlo.
- Una invocación CLI real Codex, exit 1 por rechazo de `model_providers.openai`;
  stdout vacío, stderr 217 bytes, sin terminal ni telemetría observada.
  Adaptador sin fallback/reintentos: Claude y reviewer no lanzados.
- SQLite conserva intento FAILED, run/job RECOVERY_REQUIRED, propietario cerrado
  y lock retenido. Once eventos consecutivos; hashes/rangos de bytes y prompt
  comprobados, grupo muerto y checkout desechable intacto. Evidencias externas y
  límites en [H2.3_SMOKE.md](discovery/H2.3_SMOKE.md).
- No se verificó inferencia exitosa, autenticación/cuota/acceso al modelo, stream
  real del proveedor, esfuerzo efectivo ni retries internos. Timeout/cancelación
  siguen caracterizados solo offline. No hubo pruebas nuevas de API/UI/build,
  cambios de código, relanzamiento, push, harness de desarrollo ni avance a H2.4.
- Próxima tarea: corregir configuración Codex y añadir regresión offline; no
  ejecutada en esta entrega. Verificación real concluida con resultado fallido,
  no presentada como integración exitosa.
- Diff y whitespace revisados; 60 enlaces locales de documentación comprobados.
  Commit documental solicitado por el usuario, sin cambios de implementación.

## Corrección offline H2.3 — 2026-10-11

- Git inicial limpio en `61ddf42`. Eliminados `model_providers.openai.*`,
  conservando `model_provider="openai"`, versiones/modelos explícitos y sesión nueva.
  No se sustituye el proveedor para obtener controles de retries personalizados.
- Capabilities y spec persistida declaran `built-in-defaults/unknown` para Codex.
  No hay control cero verificado en este camino; el adaptador conserva una sola
  invocación por intento y ausencia de fallback/reintento propio. D019.
- Versión `cli-2` impide ejecutar jobs `cli-1` con el comportamiento nuevo;
  resultados/historial/evidencias antiguos y esquema 0005 conservados.
- Cinco casos nuevos: cada override anterior en ambas versiones Codex sintéticas
  falla una vez, conserva stderr/hash, resultado FAILED e historial tras reiniciar;
  la versión antigua del adaptador no lanza procesos. Los fakes parsean TOML y
  rechazan IDs reservados independientemente del código del adaptador.
- 51 pruebas de adaptadores correctas; regresión completa: 209 pruebas y 121
  subtests correctos. Los 12 checks ligeros pasan. Incluye migraciones, arquitectura
  del núcleo, OpenAPI y recuperación/cancelación de procesos sintéticos existentes.
- Referencia/esquema oficiales y help local consultados. `debug models --bundled`
  se exploró sin refresh/inferencia: no valida los overrides ni admite strict-config;
  su éxito no se usa como prueba de configuración válida. No se lanzó `codex exec`
  real, Claude ni el smoke; no se extrajeron credenciales ni se modificó configuración
  global. Persiste el aviso conocido Starlette/HTTPX; uv ignora el entorno externo.
- Evidencias D018 conservadas. Nuevo smoke concreto preparado en NEXT_STEPS, sin
  ejecutarlo ni avanzar a H2.4. Compatibilidad real exitosa, consumo/auth/cuota y
  retries efectivos siguen pendientes; no se repitieron frontend/build ni navegador
  porque no cambia API/UI. Detalles y límites en [H2.3_CONFIG_FIX.md](discovery/H2.3_CONFIG_FIX.md).
- Diff/whitespace revisados y 67 enlaces locales de documentación correctos.
  Hashes de stdout/stderr/prompt del smoke D018 conservados. Commit al terminar
  conforme a la instrucción del usuario; sin push.

## Nuevo smoke real H2.3 — 2026-10-12

- Git inicialmente limpio en `c9cbd2f`. Script/criterios/D019 revisados;
  usuario autoriza explícitamente una nueva ejecución con las selecciones
  Codex `gpt-6-luna`/`low` y Claude `claude-sonnet-4-6`/`low`. D020.
- 209 pruebas pytest y 121 subtests correctos, 12 checks ligeros correctos;
  ayuda/guardia del script y preflight de Codex 0.162.1/Claude 2.1.295 correctos.
  Aviso conocido Starlette/HTTPX conservado, sin instalaciones ni cambios de código.
- Una ejecución, dos invocaciones: planificador Codex COMPLETE (exit 0, terminal,
  objeto JSON y uso reportado); ejecutor Claude FAILED (exit 1) por `mcpServers`
  ausente en `--mcp-config '{}'`, sin stdout/terminal/payload ni telemetría.
  Revisor no lanzado, sin fallback, cambios de selección ni relanzamiento.
- SQLite reabierta conserva ambas respuestas, run/job RECOVERY_REQUIRED,
  propietario cerrado, grupos STOPPED y lock retenido. 24 eventos consecutivos,
  hashes/rangos completos de streams, prompts, `cli-2` y selecciones comprobados.
  Ambos grupos muertos; README sintético intacto, sin HEAD ni cambios de agentes.
- [Informe y evidencias temporales externas](discovery/H2.3_SMOKE_RETRY.md).
  Modelo/esfuerzo efectivo y coste Codex ausentes; uso observado no certifica
  factura/cuota. No se acredita inferencia/auth/acceso al modelo Claude.
- Transporte completo fallido; tarea de verificación concluida conforme a su
  rama de error. Corrección MCP es la siguiente tarea, sin iniciarla. Retries
  internos, permisos vivos y cancelación/timeout reales siguen sin medir.
  API/UI/build/navegador no repetidos por entrega documental. Sin harness de
  desarrollo, colaboración automática, push, ReferenceProject ni cambios globales.
- Diff/whitespace revisados y 76 enlaces locales correctos en los ocho documentos
  de la entrega. Commit solicitado por el usuario; solo documentación, sin
  corrección MCP ni avance a la siguiente tarea.

## Corrección MCP offline H2.3 — 2026-10-12

- Git inicialmente limpio en `2f92914`, rama `main`. Alcance activo conservado
  en [H2.3_MCP_FIX_SCOPE.md](discovery/H2.3_MCP_FIX_SCOPE.md). D021.
- Claude Code 2.1.295 y help consultados localmente en lectura, documentación
  oficial consultada. `cli-3` sustituye `{}` por `{"mcpServers":{}}`; modo
  estricto, herramientas vacías, dontAsk, prompts none, fuentes/settings/hooks,
  sesiones, selección, auth y entorno explícitos conservados. No hay print real.
- Regresión independiente reproduce planificador completo → ejecutor FAILED
  antes de emitir inferencia simulada, con preflight correcto. Conserva stderr/
  hash, stdout vacío, payload null, terminal ausente y telemetría ausente;
  parada sin revisor/reintento. Historial/specs/capturas y JSON exacto de resultados
  sintéticos `cli-2` preservados tras reabrir SQLite con `cli-3`.
- Jobs `cli-2`/`cli-1` bloqueados antes de efectos sin mutación del run. Ninguna
  migración/codec nuevo. Los casos de éxito validan el JSON corregido, MCP vacío,
  aislamiento por flags, prompts/hashes y distinción ausencia/null/cero.
- 53 pruebas de adaptadores correctas; suite completa: 211 pruebas y 121 subtests
  correctos, incluidos checks existentes de migraciones, OpenAPI, arquitectura,
  captura/cancelación/recuperación. Los 12 checks ligeros pasan. Aviso conocido
  Starlette/HTTPX conservado, uv ignora el entorno externo.
- Informes históricos D018/D020 intactos. Capturas temporales D018 ya ausentes
  en su ruta documentada; no se reconstruyen ni se certifica su retención.
  Las seis capturas/prompts D020 disponibles coinciden con sus hashes documentados.
  No se copian runs reales a fixtures. Detalles en [H2.3_MCP_FIX.md](discovery/H2.3_MCP_FIX.md).
- Diff/whitespace y enlaces locales revisados. Sin inferencia/smoke, fallback,
  relanzamiento, credenciales, configuración global, harness de desarrollo,
  colaboración automática, ReferenceProject ni push. API/UI/build/navegador no repetidos
  porque no cambian esas fronteras. Commit solicitado por el usuario.
- Siguiente propuesta real preparada en NEXT_STEPS, sin ejecutarla: transporte
  completo, Claude auth/cuota/modelo, revisor y retries efectivos siguen pendientes.
  H2.4 no iniciado.

## Preparación del smoke cli-3 — 2026-10-12

- Git inicialmente limpio en `main`, `725e65f`; AGENTS, STATE, NEXT_STEPS,
  DECISIONS, alcance H2.3 y script revisados. Tarea activa conservada.
- 211 pruebas pytest y 121 subtests correctos, 12 checks ligeros correctos;
  ayuda/guardia del script y preflight de Codex 0.162.1/Claude 2.1.295 correctos.
  Aviso conocido Starlette/HTTPX; sin cambios de código/dependencias.
- Argv `cli-3`, MCP vacío/estricto, permisos y selecciones revisados;
  [comando exacto, hashes y límites](discovery/H2.3_SMOKE_CLI3_PREFLIGHT.md).
- Consentimiento específico solicitado conforme a NEXT_STEPS. Sin ejecución
  real ni nuevo checkout/run/job; no se acreditan sus criterios de éxito/error.
  La tarea permanece pendiente; no se avanza a H2.4.
- Sin proveedores, credenciales, configuración global, harness de desarrollo,
  colaboración automática, ReferenceProject ni push. API/UI/build no repetidos.
- Diff/whitespace revisados y 36 enlaces locales correctos; commit documental
  solicitado por el usuario. Sin decisión nueva que sustituya D021.

## Smoke cli-3 autorizado — 2026-10-12

- Git inicialmente limpio en `main`, `039a01e`. El usuario responde «Doy
  consentimiento para el smoke» a la propuesta preparada. Alcance activo en
  [H2.3_SMOKE_CLI3_SCOPE.md](discovery/H2.3_SMOKE_CLI3_SCOPE.md), D022.
- Preflight versión/help y hash del script repetidos: Codex 0.162.1, Claude
  2.1.295 y `cli-3` compatibles. La preparación previa conserva sus 211 pruebas,
  121 subtests y 12 checks ligeros; no se repite suite sin cambio de código.
- Una ejecución, dos invocaciones: Codex COMPLETE (exit 0, terminal/JSON);
  Claude FAILED (exit 1, terminal `is_error=true`) por `authentication_failed`.
  MCP explícito vacío aceptado; init reporta herramientas/servidores vacíos y
  dontAsk. Sin revisor, fallback, login, corrección ni relanzamiento.
- SQLite reabierta conserva resultados/historia/versiones exactos, integridad y
  foreign keys correctas; run/job RECOVERY_REQUIRED, propietario cerrado,
  procesos STOPPED, lock retenido. 31 eventos consecutivos, dos intents/spawns,
  rangos/hashes/capturas/prompts comprobados. Ambos grupos muertos y README
  intacto, sin HEAD ni cambios de agentes. Sin recuperación automática.
- [Informe independiente y artefactos externos](discovery/H2.3_SMOKE_CLI3.md).
  Selecciones solicitadas separadas de metadatos reportados. Claude informa
  ceros de tokens/coste y modelo de mensaje sintético, sin inferencia acreditada;
  no prueba consumo cero ni falta de login en otras sesiones del Mac.
- Rama de error completada, sin éxito completo H2.3. Siguiente diagnóstico de
  autenticación definido sin iniciarlo; autorización D022 agotada al fallo.
  Retries internos, timeout/cancelación reales, inferencia Claude y revisor
  pendientes. Sin cambios globales, colaboración automática, harness de
  desarrollo, ReferenceProject ni push; API/UI/build/navegador no repetidos.
- Sin invocaciones de herramientas en los eventos capturados. Informes D018/
  D020/D021 intactos; diff/whitespace revisados, 85 enlaces locales correctos
  en los ocho documentos. Commit documental solicitado por el usuario.

## Coordinación

Desarrollo manual con el usuario. Una única sesión implementadora sobre los mismos archivos a la vez. La otra herramienta puede revisar una entrega terminada.

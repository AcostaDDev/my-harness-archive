# Estado de desarrollo

Actualizado: 2026-10-13.

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
- 319 casos de producto en `tests/product/`; pytest ejecuta 331 pruebas en total.
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
- Diagnóstico de autenticación Claude completado en lectura: fuera del sandbox,
  status reconoce `claude.ai` en la sesión local; el entorno mínimo pierde auth
  al omitir USER y la reconoce al añadir solo USER. LOGNAME no basta. Sin login,
  inferencia ni corrección; flags de aislamiento no admitidos por auth status.
  [Evidencia reproducible y límites](discovery/H2.3_AUTH_DIAGNOSIS.md), D023.
- Corrección offline del entorno del smoke completada: USER explícito comprobado
  contra el UID local antes de efectos; ausencia/discrepancia detienen con diagnóstico.
  HOME/PATH/TMPDIR/LANG conservados, sin credenciales ni fuentes heredadas.
  Adaptador `cli-3` conservado; hash de configuración distinto bloquea jobs antiguos
  antes del preflight, sin reescribir resultados/specs/historial/locks.
  [Informe y regresión sintética](discovery/H2.3_ENV_FIX.md), D024.
- Smoke con USER validado autorizado y completo: planificador Codex, ejecutor
  Claude y revisor Codex COMPLETE, terminal/exit 0/JSON `smoke-ok` en los tres.
  Configuración congelada, sesiones frescas, herramientas/MCP vacíos y checkout
  intacto. Job DONE, run STOPPED por fin deliberado del smoke, owner cerrado,
  grupos STOPPED/dead y lock nuevo liberado por finalización normal.
  [Informe y evidencias independientes](discovery/H2.3_ENV_SMOKE.md), D025.

- H2.4 completado offline: [Git, worktree y commit acotado](discovery/H2.4_GIT.md),
  [alcance original](discovery/H2.4_SCOPE.md). `GitWorkspace` captura base, árbol
  del worktree (staged, no staged, nuevos, borrados, modos) y árbol del índice real
  sin tocar HEAD/índice/archivos; fingerprint y parche completo con procedencia y
  SHA-256. Fallos seguros ante gitlinks, conflictos, rutas no UTF-8 o parche enorme.
- `GitWorktrees`: un worktree por tarea fuera del checkout de origen, idempotente y
  conservador; el checkout principal queda idéntico. Sin remove/clean/reset.
- Commit acotado y determinista: construido desde el árbol revisado (más
  actualizaciones mecánicas declaradas), con id esperado persistido antes del efecto,
  compare-and-swap de la referencia y reconciliación tras caída sin duplicar ni
  reescribir historial. Modificación externa posterior a validación/review (contenido,
  staging o base) invalida la aceptación antes de cualquier commit. D026.
- Migración `0006_git_commits`: `managed_commits` (INTENT/COMMITTED/INVALIDATED),
  acción de job `commit` bajo el lock de checkout y estados COMMITTING/COMMITTED.
  `COMMITTED` es un checkpoint del worktree, no integración en rama destino.

- H2.5 completado offline: [migración a modo gestionado](discovery/H2.5_MIGRATION.md),
  [alcance original y decisiones del usuario](discovery/H2.5_SCOPE.md). Vista previa
  sin escrituras, copia consistente con hash por archivo fuera del checkout y
  activación atómica, idempotente y reanudable (PREPARING → ACTIVE | FAILED). D027.
- Autoridad: SQLite para estado operativo y modo; histórico legacy en copia inmutable
  indexada como origen H1 de solo lectura, con manifiesto y procedencia; documentos
  como producto en Git (cambios = propuestas por hash). Ningún intento inferido.
- Exclusión legacy/gestionado por raíz canónica y repositorio Git, con marcador
  `.harness/managed-mode.json` aceptado por el usuario. El motor gestionado rechaza
  checkouts legacy no activados, marcadores discrepantes y actividad legacy posterior
  (al admitir, al reclamar sin efectos y antes de cada invocación/commit).
  Cooperativa y detectada: el motor legacy no lee el marcador.
- Reversión: exportación verificada del estado gestionado, retirada del marcador y
  vuelta a legacy; histórico copiado accesible. Migración `0007_managed_activation`
  (`managed_activations`, `managed_jobs.activation_id`). Solo entrada de biblioteca.

- Salida del hito 2, parte 1, completada offline: [API gestionada local](discovery/H2_EXIT_API.md),
  [alcance original](discovery/H2_EXIT_API_SCOPE.md). Router `/api/managed` que
  delega en repositorio, supervisor y migración sin lógica nueva de motor. D028.
- Proyectos registrados en el servidor (`ManagedConfig` en `create_app` o
  `HARNESS_MANAGED_CONFIG`); el cliente solo nombra identificadores. Sin
  configuración: sin proyectos, puertos ni supervisor, y la API solo lee.
- Supervisor opt-in: un hilo del proceso Uvicorn sobre `LocalSupervisor.run_once`;
  la cola, la exclusión y la cuarentena siguen en SQLite. Puertos CLI/Git solo
  por inyección.
- Endpoints de migración (vista previa, activar, reanudar, abandonar, revertir y
  modo) y gestionados (encolar, runs/jobs/intentos/eventos paginados, revalidar,
  reintentar, commit y confirmar escritor detenido).
- `Idempotency-Key` al crear jobs; `expected_version` en acciones y transiciones
  de activación, este último atómico en `take_over`/`begin_revert`.
- 409 con `{code, diagnostic}`. Guardia Host/Origin y cabecera CSRF
  `X-Harness-Local` solo en `/api/managed`.
- OpenAPI y tipos regenerados; UI gestionada añadida en la parte 2 siguiente.

- Salida del hito 2, parte 2, completada offline: [UI gestionada local](discovery/H2_EXIT_UI.md),
  [alcance original](discovery/H2_EXIT_UI_SCOPE.md), D029. Proyectos/modo/supervisor,
  vista previa y transiciones de migración con confirmación, tareas, runs, intentos,
  diff/tests/review congelados, aceptación, commit y recuperación explícita.
- Sondeo con eventos paginados por cursor/deduplicación; reconexión al reiniciar
  conservando selección y evidencias. Envíos con UUID/cuerpo conservados en
  sessionStorage ante red fallida y doble clic; 409 visible y recarga de versión.
- Ampliación aditiva de CycleRead con evidencia ya persistida; tipos generados,
  sin codec/migración ni lógica de motor en React. Guardia gestionada conservada.
- Demo opt-in `examples.managed_demo:build`, con preparador que exige directorio
  nuevo, worktree Git, legacy sintético y cuarentena reproducible sin proveedores.
  Tres regresiones de cliente Node sin dependencias nuevas.

- H3.1 completado offline: [prompts versionados](discovery/H3.1_PROMPTS.md),
  [alcance original](discovery/H3.1_SCOPE.md), D030. Ocho recursos Markdown,
  resolución base/perfil/proyecto, versiones inmutables, borrador, validación,
  diff, activación con motivo/confirmación y rollback como versión nueva por API/UI.
- Migración `0008_prompt_versions`: versiones, punteros con generación y auditoría.
  Variables fijas obligatorias, interpolación de una pasada y rechazo antes del
  agente. Catálogo y snapshots por intento en codec 4; formatos 1–3 compatibles.
- Plantilla/procedencia/variables/esquema/renderizado/hashes congelados antes del
  efecto. Activaciones concurrentes no cambian peticiones anteriores; reanudar
  conserva el catálogo del run detenido. Routing no añade invocaciones.
- 23 pruebas H3.1 y recorrido Chrome del editor con SQLite/demo sintética.
  Bootstrap/reconciliación/cierre solo conservan plantillas, sin ejecutar flujos.

## Todavía no existe

Recorrido de tarea real del motor con proveedores ni entrada CLI gestionada;
API/UI gestionadas existen y se han verificado con fakes y Git/SQLite sintéticos.
Tampoco existen sesión local, guardia Host/Origin/CSRF en rutas H0/H1, registro de
proyectos por HTTP, SSE gestionado, pausa o cancelación por HTTP, integración del
commit en la rama de destino, retirada de worktrees, abandono manual de una
intención ambigua, exportación mecánica de STATE/NEXT_STEPS, permisos
interactivos, chat ni distribución. La salida del hito 2 está verificada offline desde la UI hasta COMMITTED,
con recuperación explícita y sin integración en la rama destino.
La navegación H1.2 muestra evidencia legacy;
el recorrido H0.3 solo guarda simulaciones, que no representan intentos reales
ni aceptación de tareas. El primer smoke real lanzó Codex y falló al cargar
configuración; no acredita inferencia, autenticación, cuota ni acceso al modelo.
Los nuevos smokes completan el transporte del planificador Codex. D020 falló al
validar MCP; D022 supera ese rechazo y falla en autenticación Claude con terminal
de error, sin inferencia acreditada en D022. El smoke D025 completa transporte
de ambos proveedores y revisor con USER validado; no ejecuta una tarea real ni
certifica validación/review ACCEPT/commit de producto con proveedores. H2.4 verifica
Git y el commit únicamente con agentes falsos y repositorios sintéticos.

## Trabajo activo

H0, H1, H2.1–H2.5 y las dos partes de la salida del hito 2 completados.
UI gestionada verificada con navegador, Git/SQLite sintéticos y fakes hasta
COMMITTED, reinicio y recuperación sin repetir ejecutor. [Informe](discovery/H2_EXIT_UI.md),
D029. H2.3 conserva su smoke real D025, con autorización agotada. Siguiente tarea:
H3.1 completado con editor y snapshots por intento (D030). Siguiente tarea:
H3.2 (permisos y acciones de recuperación), sin iniciarla. Sin proveedores nuevos.

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

## Diagnóstico de autenticación Claude — 2026-10-12

- Git inicialmente limpio en `main`, `0386629`. Alcance original conservado
  en [H2.3_AUTH_DIAGNOSIS_SCOPE.md](discovery/H2.3_AUTH_DIAGNOSIS_SCOPE.md).
  D008/D017/D022, spec persistida, script/help y fuentes oficiales revisados.
- Consultas de status filtradas en memoria, dentro/fuera del sandbox con
  aprobación de lectura. Fuera: entorno de esta sesión reconoce `claude.ai`,
  mínimo HOME/PATH/TMPDIR/LANG no; añadir solo USER lo restaura y retirarlo del
  entorno de la sesión lo impide. LOGNAME no basta; cambiar cwd no lo explica.
- Sin login ni acceso directo a secretos. Metadatos de configuración global
  sin cambios. Status no admite `--setting-sources`: sus rechazos no son
  observaciones de auth ni pruebas del argv de inferencia aislado. Hash actual
  de entorno mínimo distinto al D022; valores históricos no persistidos.
- D020/D022: doce capturas/prompts coinciden con hashes documentados, archivos
  disponibles/SQLite/WAL sin cambios. Integridad y foreign keys correctas;
  24/31 eventos, jobs RECOVERY_REQUIRED, propietarios cerrados, procesos STOPPED
  y locks retenidos. D018 ya ausente; informes históricos intactos.
- Doce checks ligeros correctos; diff/whitespace y enlaces locales revisados.
  Sin cambios de implementación: pytest completo, migraciones, API/UI/build
  no repetidos. Commit documental solicitado por el usuario, sin push.
- [Informe, reproducción y límites](discovery/H2.3_AUTH_DIAGNOSIS.md), D023.
  Causa comprobada para status en este Mac, mecanismo interno no auditado;
  sin inferencia, cuota/modelo certificados, otro smoke ni éxito completo H2.3.
  Próxima corrección offline del entorno propuesta, sin ejecutarla. H2.4 no iniciado.

## Corrección offline del entorno del smoke — 2026-10-12

- Git inicialmente limpio en `main`, `92af0f0`, un commit por delante de origin.
  AGENTS/STATE/NEXT_STEPS/DECISIONS y criterios H2.3 revisados; alcance conservado
  en [H2.3_ENV_FIX_SCOPE.md](discovery/H2.3_ENV_FIX_SCOPE.md). D024.
- Constructor del smoke transmite USER validado contra el usuario local del UID,
  junto a HOME/PATH/TMPDIR/LANG. Ausencia, vacío, discrepancia o UID no resoluble
  detienen antes de directorios, checkout, preflight y consumo; sin login ni
  sustitución por LOGNAME. No se amplía el entorno heredado del adaptador.
- Ocho casos nuevos independientes: rechazos previos a efectos; defecto anterior
  con fallo sintético de Claude, parada sin revisor/reintento y lock retenido;
  recorrido sintético completo con USER. Selecciones, sesiones, permisos, MCP/
  fuentes/hooks, entorno completo y hashes congelados comprobados tras reabrir.
- Hash de CLIConfig distinto con USER; `cli-3` conservado porque cambia solo
  configuración del script. Un job anterior se rechaza antes del preflight;
  filas SQL exactas, resultados, historial, specs, eventos y capturas intactos.
  Sin migración ni codec nuevo. [Informe y hashes](discovery/H2.3_ENV_FIX.md).
- Suite completa offline: 219 pruebas y 121 subtests correctos; 12 checks ligeros
  correctos. Pase inicial en sandbox falla en liveness de un proceso sintético
  del test existente de recuperación; suite fuera del sandbox con aprobación
  correcta. Aviso conocido Starlette/HTTPX. Refuerzo final de comparación SQL
  exacta: los ocho casos nuevos vuelven a pasar.
- D020/D022: doce capturas/prompts coinciden con sus informes; archivos disponibles
  y SQLite/WAL sin cambios, integridad/foreign keys correctas, 24/31 eventos,
  RECOVERY_REQUIRED, owner cerrado, procesos STOPPED y locks retenidos.
  Sin recuperación/liberación. D018 ausente, sin reconstruir; informes históricos
  D018/D020/D021/D022/D023 intactos. Diff/whitespace y enlaces locales revisados.
- Sin CLI reales, status, inferencia/smoke, credenciales/keychain, login/refresh,
  instalaciones, cambios globales, harness de desarrollo, colaboración automática,
  ReferenceProject ni push. API/UI/build no repetidos porque no cambian esas fronteras.
  Commit solicitado por el usuario; pruebas offline no certifican auth/cuota/modelos.
- [Propuesta separada](discovery/H2.3_ENV_SMOKE_PROPOSAL.md) y NEXT_STEPS definen
  la verificación posterior, pendiente de consentimiento, sin ejecutarla.
  Transporte real completo, inferencia Claude/revisor y retries efectivos siguen
  pendientes. D022 continúa fallido; H2.4 no iniciado.

## Smoke real con USER validado — 2026-10-12

- Git inicialmente limpio en `main`, `d970e15`; usuario autoriza «Procede con
  el smoke» sobre la propuesta D024. [Alcance](discovery/H2.3_ENV_SMOKE_SCOPE.md), D025.
- USER comprobado, entorno de cinco variables explícito, ayuda/guardia correctas;
  preflight Codex 0.162.1 y Claude 2.1.295 con hashes de help conservados.
  Una ejecución fuera del sandbox, tres CLI de menos de 60 s cada una:
  planificador/ejecutor/revisor COMPLETE, terminal/exit 0/JSON `smoke-ok`.
- SQLite en lectura: integridad/foreign keys correctas, resultados/requests e
  historial exactos tras reabrir; 57 eventos consecutivos, tres intents/spawns,
  hashes/rangos/capturas/prompts, selección y configuración comprobados.
  Job DONE, run STOPPED por stop deliberado `smoke`, owner cerrado y procesos
  STOPPED/dead; lock de esta área liberado por fin normal, sin recuperación.
- Checkout sintético intacto, sin HEAD ni herramientas observadas. Claude
  informa modelo `claude-sonnet-4-6`, uso y coste de lista, sin inferir factura/
  cuota. Esfuerzo efectivo ausente; Codex no reporta modelo/coste/duración de
  proveedor. [Evidencia y límites](discovery/H2.3_ENV_SMOKE.md).
- D020/D022 conservan archivos/SQLite/WAL/capturas y locks, sin reanudar;
  informes anteriores intactos. D018 ausente no reconstruido.
  Doce checks ligeros correctos. Suite previa del mismo código: 219 pruebas y
  121 subtests; pytest completo/API/UI/build no repetidos por cambio documental.
- Sin código modificado, login/refresh, secretos, cambios globales, fallback,
  relanzamiento, harness de desarrollo, colaboración automática, ReferenceProject o
  push. Diff/whitespace y enlaces locales revisados; commit solicitado en sesión.
- Transporte completo acreditado en este contexto, sin tarea real ni aceptación/
  commit de producto. Retries internos, cuota, permisos vivos, aislamiento físico
  y cancelación/timeout reales no certificados. H2.4 documentado como siguiente
  tarea offline, sin iniciarlo; consentimiento consumido para esta ejecución.

## Verificación de H2.4

- Git inicialmente limpio en `main`, `c62905d`. AGENTS/STATE/NEXT_STEPS/DECISIONS,
  puertos del motor, journal y persistencia revisados; sin contradicciones materiales
  (la especificación ya fija base SHA/árbol/operación y evidencia con staged/untracked).
  `COMMITTED` se mantiene distinto de COMPLETED: la integración es una acción aparte.
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`: 253 pruebas
  y 121 subtests correctos (219 anteriores + 34 H2.4); 12 checks ligeros
  correctos. Núcleo con `python -S`, frontera de imports y OpenAPI sincronizado.
- Git real en repositorios temporales (Git 2.50.1): captura de staged/unstaged/
  untracked/borrados/modo, ignorados fuera, determinismo y ausencia de efectos
  (HEAD, índice y archivos idénticos); rechazo de gitlinks, conflictos, raíz que no
  es nivel superior, no UTF-8 y parche sobre el límite.
- Worktree por tarea idempotente; checkout principal con cambios ajenos staged/
  unstaged/untracked idéntico tras todo el flujo. Rechazos de ruta interior, ruta
  ocupada, rama existente o distinta sin sobrescribir nada.
- Commit: contenido exacto revisado (árbol idéntico, padre = base, solo rutas
  revisadas, trailers, identidad), índice refrescado, ignorados no incluidos,
  hooks del repositorio nunca ejecutados. Invalidación por contenido, untracked,
  borrado, staging y base movida; revalidar produce evidencia y commit nuevos.
- Caídas inyectadas: antes del objeto, antes de mover la referencia, después de
  mover la referencia (con y sin trabajo posterior del usuario) y tras escribir
  mecánicas: un solo commit, mismo id, historial intacto. HEAD movido invalida si
  no hay objeto y entra en cuarentena con evidencia si existe sin ser alcanzable.
  Carrera de HEAD durante el efecto detectada por compare-and-swap.
- Migración `0006` ida/vuelta con `alembic check` correcto; runs previos conservados.
  Mutaciones temporales (omitir fingerprint al ejecutar o al preparar, ignorar HEAD
  esperado, quitar CAS) detectadas y código restaurado.
- Diff/whitespace revisados. Sin proveedores, CLI de agente, red, harness de
  desarrollo, ReferenceProject, configuración global ni push. uv ignora el entorno
  externo; persiste el aviso conocido Starlette/HTTPX. Frontend/build/navegador no
  repetidos: no cambian API/UI/OpenAPI.
- Límites: macOS/un host, una base cooperativa; escritores Git externos solo por
  comparación; configuración local del repo (filtros `clean`) respetada;
  sin integración en rama destino, push, retirada de worktrees, entradas
  API/CLI/UI ni abandono manual de intenciones ambiguas. H2.5 no iniciado.
  Commit solicitado por el usuario.

## Verificación de H2.5

- Git inicialmente limpio en `main`, `39f59c6`. AGENTS/STATE/NEXT_STEPS/DECISIONS,
  especificación §7, backlog H2.5, D012–D016/D026 y código H1/H2 revisados.
  Referencia legacy leída sin ejecutar: no tiene lock ni comprobación de arranque.
  Contradicción (deshabilitar el arranque frente a no modificar el origen) señalada
  antes de implementar; el usuario aceptó el marcador, delegó la autoridad e incluyó
  la reversión.
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`: 288 pruebas
  y 121 subtests correctos (253 anteriores + 35 H2.5); 12 checks ligeros correctos.
  Núcleo (incluido `core/migration.py`) con `python -S` y frontera de imports;
  OpenAPI regenerado sin diferencias; `alembic upgrade head`/`check`/`current` en
  SQLite temporal y migración 0007 ida/vuelta con 0006 conservando runs/jobs.
- Vista previa de los cinco fixtures sin escrituras ni procesos. Activación de los
  cinco: copia con hashes idénticos, origen intacto salvo el marcador, resumen H1
  idéntico (ausente/null/cero), repetición idempotente y navegación HTTP del
  histórico tras activar y tras revertir.
- Rechazos sin efectos: cambio desde la vista previa, evidencia no copiable,
  escritor legacy durante la copia (FAILED sin marcador/copia/índice), trabajo
  gestionado sin terminar, alias/concurrencia (una sola activación), worktree con
  estado legacy propio. Caídas en siete puntos con reinicio, reanudación y abandono
  explícitos; error inesperado tras el marcador deja el checkout idéntico.
- Tras activar: run/edición legacy y marcador editado/borrado producen claim
  REFUSED sin invocar puertos; escritura legacy a mitad de run detiene antes del
  revisor; carrera evaluación/admisión rechazada; documentos como propuestas.
  Reversión verificada, rechazada con trabajo pendiente y reanudable tras caída.
- Ocho mutaciones temporales de las protecciones detectadas y código restaurado.
  Diff/whitespace revisados. Sin proveedores, CLI de agente, red, harness de
  desarrollo, ReferenceProject, configuración global ni push. uv ignora el entorno
  externo; persiste el aviso conocido Starlette/HTTPX. Frontend/build/navegador no
  repetidos: no cambian API/UI/OpenAPI.
- Límites: exclusión cooperativa y detectada (el motor legacy no lee el marcador),
  detección por lstat/hash entre comprobaciones, una base local, solo raíz y
  checkout principal, `.harness/runs` versionado tratado como legacy en worktrees,
  copias `staging-*` sin retención. Sin entradas API/CLI/UI ni exportación mecánica
  de documentos. Salida del hito 2 no iniciada. Commit solicitado por el usuario.

## Verificación de la salida del hito 2, parte 1

- Git inicialmente limpio en `main`, `f8d6bb7`. AGENTS, STATE, NEXT_STEPS y
  DECISIONS revisados; también especificación §5/§10/§13/§14, D010/D011,
  D016/D017, D026/D027 y el código H2.2–H2.5. La sesión empezó en Sonnet 5.5,
  se detuvo sin cambios para pasar a Opus 5.5 a petición del usuario y continuó.
- Sin contradicciones materiales. Huecos resueltos con criterio reversible y
  documentados (D028):
  - proyectos registrados en el servidor en lugar de `POST /projects`;
  - supervisor opt-in en lugar de una acción «ejecutar siguiente job»;
  - sesión local pendiente.
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`: 306 pruebas
  y 121 subtests correctos (288 anteriores + 18 nuevas). 12 checks ligeros
  correctos. `alembic upgrade head`/`check`/`current` en SQLite temporal:
  `0007_managed_activation`, sin migración nueva.
- Recorrido HTTP con Git real hasta COMMITTED. Doble envío y reinicio no duplican
  jobs, invocaciones, eventos ni commits. El checkout principal no cambia y los
  eventos son contiguos y estables entre páginas.
- Job en cola sobrevive al reinicio y se ejecuta una sola vez. La recuperación
  completa (cuarentena, 409 previos, confirmación, revalidar y commit) no repite
  el ejecutor y deja el revisor incierto INTERRUPTED.
- Rechazos de modo y conflictos de versión o idempotencia devuelven 409 con
  diagnóstico; las peticiones inválidas, 422. En ambos casos tablas y checkout
  quedan idénticos.
- Migración por HTTP: vista previa sin escrituras, activación idempotente,
  reversión con versión y exportación verificada, y reanudar o abandonar una
  activación interrumpida.
- Guardia Host/Origin/CSRF comprobada, y servicio por defecto sin procesos.
- Ocho mutaciones temporales de las protecciones detectadas y el código restaurado.
- OpenAPI y tipos regenerados con rutas y esquemas anteriores idénticos.
  TypeScript y build Vite correctos.
- Uvicorn real en `127.0.0.1:8015` con base temporal: guardia y 404 de proyecto
  comprobados, apagado limpio. `:8013` no se tocó.
- Diff y whitespace revisados. Sin proveedores, CLI de agente, smoke, red, harness
  de desarrollo, ReferenceProject, configuración global ni push. Persiste el aviso
  conocido Starlette/HTTPX.
- Límites:
  - un solo hilo supervisor por base, que procesa toda su cola;
  - apagado acotado a un lease, con recuperación explícita después;
  - activación síncrona dentro de la petición;
  - sesión local, guardia en H0/H1, SSE gestionado y UI pendientes;
  - fakes no acreditan proveedores.
- Parte 2 no iniciada. Commit solicitado por el usuario.

## Verificación de la salida del hito 2, parte 2

- Git inicial limpio en `main`, `1f5a8df`. Alcance conservado y D029 registrada.
- 308 pruebas pytest y 121 subtests correctos (306 anteriores + 2 de demo);
  20 casos de API gestionada, incluyendo evidencia congelada en la proyección.
  Tres pruebas Node de claves/solicitud incierta/CSRF/409; 12 checks ligeros.
  OpenAPI/tipos regenerados, TypeScript y build correctos. Esquema 0007 conservado.
- Chrome sobre build compilado en :8015: doble clic → un run ACCEPTANCE_READY,
  diff/tests/review visibles, commit → COMMITTED. Reinicio con página abierta
  conserva selección, commit y 24 eventos, muestra desconexión y reconecta.
- Cuarentena de revisión → confirmación explícita → revalidación → COMMITTED,
  un ejecutor y dos revisores (anterior INTERRUPTED); 36 eventos. Activación y
  reversión legacy comprobadas, diagnóstico 409 mode_refused visible sin run nuevo.
- SQLite/auditoría sintéticas: dos commits, cinco jobs, cero locks, activación
  REVERTED; sin invocaciones extra al reiniciar. Captura visual inspeccionada.
- Servicio y pestaña temporales cerrados; diff/whitespace revisados. Sin proveedores,
  smoke, colaboración automática, harness de desarrollo, ReferenceProject, red externa,
  configuración global ni push. Aviso conocido Starlette/HTTPX conservado.
- Límites: sesión local/guardia H0/H1/SSE gestionado pendientes, sin benchmark de
  historiales grandes ni carrera de versión inyectada en Chrome (cubierta en API
  y cliente). Fakes no acreditan proveedores. H3.1 no iniciado; commit solicitado.

## Verificación de H3.1

- Git inicial limpio en `main`, `7606cfe`. Instrucciones, estado, siguiente tarea,
  decisiones, especificación §9, backlog y referencia estática de prompts revisados.
- 331 pruebas pytest y 121 subtests pasan: 308 anteriores y 23 casos nuevos.
  12 checks ligeros, 3 pruebas Node, OpenAPI/tipos, TypeScript y build correctos.
  Aviso conocido Starlette/HTTPX conservado.
- Migración 0008 con upgrade/downgrade/upgrade y `alembic check` en base temporal;
  un run previo sobrevive. Ninguna base de trabajo del usuario se migró.
- Concurrencia de activación con dos hilos, rollback/reinicio, guardias HTTP,
  409/422/404 y aislamiento de versiones de proyecto verificados. Petición
  confirmada en SQLite antes del agente falso, conservada byte a byte tras
  activar otra versión. Históricos de formato 1 reanudables sin reescribir filas.
- Chrome en demo nueva `/private/tmp/h31-ui-demo-1013`, puerto 8016: variable
  inválida visible, guardar sin activar, diff, confirmación, activar, rollback
  con UUID nuevo, auditoría de dos activaciones y persistencia tras recarga.
  Formulario/auditoría inspeccionados visualmente; sin encolar proveedores.
- Límites: plantillas de fases/bootstrap sin flujos, sin aplicación de nuevos
  prompts a runs detenidos, importación/exportación de overrides ni edición de
  esquemas. Catálogo sin paginación/benchmark de históricos grandes. Fakes no
  certifican respuestas de modelos. H3.2 no iniciado.
- Diff/whitespace revisados; sin proveedores, smoke, colaboración automática,
  ejecución de harness para desarrollo, cambios en ReferenceProject, configuración
  global ni push. Commit solicitado por el usuario.

## Coordinación

Desarrollo manual con el usuario. Una única sesión implementadora sobre los mismos archivos a la vez. La otra herramienta puede revisar una entrega terminada.

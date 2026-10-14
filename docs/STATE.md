# Estado de desarrollo

Actualizado: 2026-10-14.

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
- Casos de producto en `tests/product/`: 1065 pytest y 121 subtests aprobados (H6.2 E1).
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

- H3.2 completado offline: [permisos y recuperación](discovery/H3.2_PERMISSIONS.md),
  D031. Ledger por categoría, petición exacta/versiones/huella/caducidad,
  concesión/denegación con identidad local del servicio y motivo; sustitución
  conservando decisiones anteriores. Techos global/proyecto/contrato/proveedor
  congelados en versiones; nunca se amplía el contrato por prompts o reviews.
- Migración `0009_permissions` y codec 5, formatos 1–4 legibles. Snapshot y consumo
  once/task persistidos con la intención; caídas no restituyen concesiones once.
  Denegaciones operativas bloquean antes del adaptador. API/UI con confirmación,
  versiones y acciones habilitadas calculadas por servidor; sin ejecución al conceder.
- CLI `cli-4`: reglas concedibles declaradas y congeladas; inventario/regla solo
  para el intento autorizado, sin permisos vivos ni configuración mutada. Red por
  dominio rechazada por falta de soporte; ficheros no conceden herramientas.
- Revalidar conserva trabajo y solo prepara/valida/revisa; REVISE ahora se detiene
  para exigir reintento explícito. Retry mantiene el presupuesto acumulado.
  30 casos H3.2 y comprobación Chrome con SQLite/checkout sintéticos.

- H3.3 completado offline: [fases, preguntas, cierre y tags](discovery/H3.3_PHASES.md),
  D032. Migración `0010_phases`: fases con definición congelada creada por el
  usuario, base documental por hash, preguntas, operaciones, autorizaciones y
  eventos atómicos; `managed_runs.purpose` para runs de check y cierre.
- Check como job bajo el lock del checkout: preguntas, deriva documental, árbol
  Git limpio, commits de tareas alcanzables y validación base antes de la
  evaluación Codex `close-phase` (rol `phase`, solo lectura, esquema fijo).
  READY ligado a definición, HEAD/fingerprint, documentos, tareas y preguntas.
- Cierre con autorización propia sobre el READY mostrado: reobserva el vínculo;
  obsoleto → `NEEDS_RECONCILIATION` sin efectos. Único efecto Git: tag ligero
  declarado, intención previa, CAS y conciliación; nunca se mueve. Sin edición
  documental, commit de cierre ni fase siguiente.
- Lote como autorización distinta (tareas exactas, vigencia, revocable) que encola
  de una en una sin comprobar, cerrar ni confirmar commits. Reconciliar = adoptar
  documentos por hash revisado. Fases cerradas no aceptan tareas/commits nuevos.
- API/UI con acciones del servidor, confirmaciones y guardia gestionada; demo
  sintética con rol `phase`. 29 casos H3.3 y recorrido Chrome sintético.

- H3.4 completado offline: [ajustes de fases](discovery/H3.4_PHASE_ADJUSTMENTS.md), D034.
  La guardia Host/Origin/`X-Harness-Local` (`api/security.py`) cubre también las
  mutaciones H0/H1 (simulaciones y observación legacy). Los clientes envían la
  cabecera.
- Lote desatendido (`chain_commits`): congela tareas, plan, definición, contexto y
  versiones. El supervisor lo conduce antes de reclamar, con claves deterministas:
  tarea → commit H2.4 de la aceptación elegible → siguiente tarea → `COMPLETED`. Se
  detiene en el primer bloqueo, pregunta, caducidad, revocación, cuarentena,
  evidencia invalidada o run ajeno. Nunca comprueba ni cierra la fase.
- Migración `0011_phase_amendments`. Las enmiendas crean versiones nuevas en
  `phase_definitions` y conservan las anteriores; invalidan READY y lotes. El
  abandono es un estado terminal `ABANDONED` auditado y libera el checkout.
- Tag por proyecto (`tag_kind`), ligero por defecto. El anotado fija en la
  intención mensaje, identidad, fecha e id del objeto. Concilia tras una caída con
  el mismo objeto y nunca se mueve.
- La reconciliación con agente es una tarea normal con contrato determinista
  (`reconcile-phase`, sin planificador), limitada a los documentos. Se revisa y
  confirma por el flujo normal y después la base se adopta por hash, con el origen
  registrado.
- API/UI: enmendar, abandonar, reconciliar con agente, lote desatendido, versiones
  de la definición y tipo de tag. 18 casos H3.4 y recorrido Chrome sintético.

- H4.1 completado offline: [chat contextual](discovery/H4.1_CHAT.md), D035.
  Migración `0012_chat`: conversaciones (fase opcional), turnos con petición
  congelada y propuestas, separadas del flujo de ejecución.
- Cada mensaje congela, al encolarse, el proyecto, la fase, los documentos
  (contenido acotado y hash), la evidencia de runs y los turnos anteriores. El
  turno es un run `chat` bajo el lock del checkout: invocación nueva del rol `chat`
  (Codex `--ephemeral --sandbox read-only`) con la plantilla versionada
  `chat-turn`, prompt persistido antes del efecto y esquema fijo. Una salida
  inválida o un fallo → `FAILED`, sin fallback ni reintento; una caída → `UNKNOWN`
  tras confirmar el escritor detenido. Un cambio en el checkout descarta el turno.
- Las propuestas solo se convierten en una tarea normal tras confirmación, versión
  y hash exacto. El planificador fija el contrato con la política; después siguen
  ejecutor, revisión y commit explícito. El chat no concede permisos ni fija
  contratos. La conversación enlaza propuesta → tarea → run → commit.
- API/UI bajo la guardia local con idempotencia y confirmaciones; demo con roles
  `chat`/`planner` sintéticos. 21 casos H4.1 y recorrido Chrome sintético.

- Exportación mecánica completada offline: [entrega](discovery/STATE_EXPORT.md),
  D036. STATE/NEXT_STEPS se generan desde SQLite en bloques delimitados, con bytes
  deterministas y prosa exterior conservada. Preview por diff, versión, hash y
  confirmación humana; deriva externa exige reconciliación, sin sobrescritura.
- Run/job `document_export` con lock y operación de fase existentes; sin agentes.
  CommitIntent H2.4 persistido antes de escribir, CAS y conciliación de escrituras
  parciales o commit incierto con el mismo id. Adopción de hashes después de
  verificar el commit, atómica con resultado/evento/fin del job. Esquema 0012 sin
  migración nueva. API/UI con guardia local e idempotencia; 32 casos nuevos.
- Exportar sigue separado del cierre, también para la última fase CLOSED/ABANDONED
  antes de definir otra; nunca mueve tags. READY previo queda obsoleto y requiere
  un check nuevo. Sin exportación automática; el bootstrap se describe a continuación.

- H4.2 completado offline: [bootstrap guiado y recuperación](discovery/H4.2_BOOTSTRAP.md),
  D037. Destinos vacíos autorizados por el servidor, brief/decisiones, propuesta
  Codex opcional de solo lectura y plantilla documental `project-foundation` v1/hash.
  Preview de documentos/fase/contrato, perfil y comandos declarados; confirmación
  humana del contenido exacto antes de encolar y sin preparación automática.
- Migración `0013_bootstrap`: operación, preview/bytes, decisión, intención del
  commit raíz y resultado. Runs/jobs/locks/leases/propietarios existentes, CAS y
  conciliación con el mismo run/intención/commit tras confirmar escritor detenido.
  Fase/definición/base documental adoptadas junto al fin del job en SQLite.
- Primera fase `P001` y tarea `P001-T001` limitada a `docs/DELIVERY_CHECKLIST.md`,
  con criterios verificables y ejecución/revisión/commit por acción propia.
  Carpetas con contenido o dentro de otro Git → importación sin sobrescribir.
  API/UI con guardia local, tipos generados y demo exclusivamente sintética.
  No añade otro perfil ni instala/genera una aplicación desde el brief.

- H4.3 completado offline: [segundo perfil TypeScript web](discovery/H4.3_TYPESCRIPT_PROFILE.md),
  D038. Perfil declarativo con preparación npm offline desde lock, typecheck,
  tres tests Node y build estático, reglas de rutas/comandos e instrucciones.
  Node 24.15.0, npm 11.12.1 y TypeScript 5.9.3 en fixture con lock propio.
- 16 casos nuevos con comandos reales por el puerto de prueba, agentes falsos,
  Git/SQLite temporales y worktree hasta COMMITTED. Conserva contexto, contrato,
  prompts, permisos y evidencia exacta; tests/tipos/build/política fallidos impiden
  commit. Sin cambios del núcleo, API/UI, esquema ni codec; no añade un ejecutor
  de comandos al servicio ni modifica la plantilla documental de bootstrap.

- H5.1 completado offline: [reportes JUnit y detalle de tests](discovery/H5.1_JUNIT.md),
  [alcance original](discovery/H5.1_SCOPE.md), D039. Declaraciones por comando
  exacto/ruta/selección en perfil congelado, captura segura antes/después y original
  completo con SHA-256 en el historial SQLite. Codec 6; formatos 1–5 conservados,
  esquema `0013_bootstrap` sin migración.
- Parser de biblioteca estándar acotado, sin DTD/entidades ni lectura de rutas XML.
  Casos/suites/resultados/duraciones/errores observados; datos ausentes, parcialidad,
  XML inválido/ausente/obsoleto y límites explícitos. No suma duración de casos.
  Fallos nuevos observados añaden una puerta de aceptación; nunca sustituyen los
  resultados del comando ni la review/política/evidencia exacta.
- API de casos paginados y descarga del original persistido; UI con tabla,
  cobertura declarada, procedencia, diagnósticos y errores como texto. Reportes en
  tareas/revalidaciones y checks de fase. `typescript-web`/fixture generan JUnit
  Node junto a TAP sin dependencias nuevas; 43 casos nuevos y Chrome sintético.

- H5.2 completado offline: [backup/restauración local](discovery/H5.2_BACKUP.md),
  [alcance original](discovery/H5.2_SCOPE.md), D040. CLI y biblioteca con servicio/
  escritores detenidos, bloqueo escritor y mecanismo de backup SQLite (incluye WAL).
- Bundle con SQLite, prompts/streams CLI, snapshots/exportación H2.5 y JUnit
  embebido; manifiesto/hashes/mapeo de referencias, integridad/FK/esquema/codec
  comprobados. Lecturas seguras acotadas y destino nuevo, sin sobrescribir originales.
- Copia/restauración protegidas por marca interna y `query_only=ON`; API de
  consulta sin cargar configuración, supervisor u observador, mutaciones 409.
  Jobs/locks/estados inciertos y snapshots conservados, sin reanudar procesos.
  Consultas por ID, JUnit y contenido legacy mapeado independientes del origen.
  43 casos nuevos y recorrido CLI/HTTP sintético; sin reactivación operativa,
  retención/GC ni backup de checkouts/objetos Git/fuentes legacy externas.

- H5.3 completado offline: [retención local de logs](discovery/H5.3_RETENTION.md),
  [alcance original](discovery/H5.3_SCOPE.md), D041. Política por corte UTC/tamaño,
  preview con hash y aplicación CLI explícita con servicio/escritores detenidos.
- Retira solo originales externos stdout/stderr de intentos CLI terminados y
  sellados; conserva contratos/snapshots/permisos/aprobaciones/veredictos/resultados
  y hashes/rangos. Excluye locks, trabajos activos/inciertos y referencias compartidas.
- Intención antes de unlink y resultado auditados en eventos/versiones del run;
  caída → pendiente → nueva preview/reconfirmación, con bytes observados null si
  no se observó su retirada. Esquema `0013_bootstrap` y codec 6 conservados.
- Consulta CLI/API/UI distingue retenido, purgado, pendiente, perdido y no
  verificado. Backup/restauración conserva ausencias autorizadas en `absent_purged`,
  acepta bundles anteriores y mantiene la guardia de consulta. 43 casos nuevos,
  solo capturas temporales sintéticas; sin rotación, GC ni retención de SQLite.

- H5.4 completado offline: [diagnóstico local de CLI](discovery/H5.4_DIAGNOSTICS.md),
  [alcance original](discovery/H5.4_SCOPE.md), D042. Comando `diagnose-cli` y
  biblioteca con configuración explícita, validación estructural y preflight
  versión/help compartido con el adaptador. Sin SQLite/jobs/agentes/auth status.
- Salida acotada, timeout/grupo POSIX, sin herencia de entorno, sin revelar valores
  ni salidas libres. Versión solicitada/observada, flags ausentes y correcciones;
  coincidencia local nunca certifica autenticación/cuota/argv completo.
- 52 casos nuevos sintéticos. Esquema, codec, cli-4 y hashes congelados conservados;
  no hay actualización de versiones, fallback, reintento ni reparación automática.

- H5.5 completado offline: [distribución y arranque](discovery/H5.5_DISTRIBUTION.md),
  [alcance original](discovery/H5.5_SCOPE.md), D043. Sdist/wheel con UI, plantillas
  y migraciones; instalación aislada con pins/hashes desde locks conservados.
- `harness-local init-db` prepara solo destinos nuevos; `serve --database` exige
  ruta absoluta/esquema y sirve UI/API desde loopback sin cwd/checkout/Node.
  Configuración/observación opt-in y guardia de restauraciones conservadas.
- 13 casos nuevos y recorrido HTTP de wheel instalado con simulación, reinicio,
  diagnósticos, backup/restauración de consulta. Sin publicación ni proveedores.

- H5.6 completado offline: [sesión local y endpoints](discovery/H5.6_SESSION.md),
  [alcance original](discovery/H5.6_SCOPE.md), D044. Clave efímera en archivo privado,
  sesiones HttpOnly de ocho horas, cierre/reinicio invalidantes y guardia uniforme.
- Host/Origin exacto/CSRF conservados y extendidos a todas las lecturas, evidencias,
  health/OpenAPI y SSE. UI de acceso/cierre y caducidad sin repetir acciones;
  sobres pendientes conservados ante 401. Esquema/codec/cli-4/locks intactos.
- Paquete instalado y restauración de consulta funcionan con sesión sin habilitar
  proveedores. 45 casos nuevos, cliente Node y HTTP reales offline; QA visual
  bloqueada por el navegador. Límites frente a otros usuarios/servicios locales
  y cookies compartidas por hostname documentados.

- H5.7 completado offline: [recorridos, matriz y verificaciones](discovery/H5.7_E2E.md),
  [alcance original](discovery/H5.7_SCOPE.md), D045. Seis recorridos nuevos de
  crear/importar/ejecutar/bloquear/denegar/reintentar/recuperar con sesión real,
  API, Git/SQLite temporales y puertos falsos; reinicio e idempotencia conservados.
- Wheel aislado recorre bootstrap → tarea → commit → reinicio → backup/restauración
  con historial, intentos, eventos y commit exactos, sin checkout original ni
  reactivación. Cliente Node conserva identidad tras respuesta perdida y 401.
  771 pruebas y 121 subtests correctos; Chrome vuelve a bloquear la URL local,
  sin QA visual acreditada. No cambia el producto ni se inicia otro incremento.

- Ejecutor de validaciones de producto implementado offline (D047):
  [entrega/composición/límites](discovery/COMMAND_RUNNER.md),
  [alcance previo](discovery/COMMAND_RUNNER_SCOPE.md). `commands-1`, configuración
  congelada y autorización exacta separadas de confianza/permisos de agentes;
  captura acotada en SQLite, intención/gate/grupos y recuperación conservadora.
- Reutiliza cola/lease/lock/journal; caída con grupo vivo no libera ni relanza.
  Preparación/validación/JUnit/commit TypeScript comprobados offline con agentes
  falsos y temporales. Codec 7 para captura nativa, formatos 1–6 compatibles;
  sin esquema/CLI/UI/dependencias nuevas ni activación predeterminada.

## Todavía no existe

Composición completa para operar proyectos reales con proveedores ni
recorrido de tarea real del motor con proveedores ni entrada CLI gestionada;
API/UI gestionadas existen y se han verificado con fakes y Git/SQLite sintéticos.
Tampoco existen registro de
proyectos por HTTP, SSE gestionado, pausa o cancelación por HTTP, integración del
commit en la rama de destino, retirada de worktrees, abandono manual de una
intención ambigua, permisos
interactivos, App Server/SDK para el chat, rotación de logs, retención de payloads
SQLite/legacy/JUnit, GC ni publicación. Tampoco
reactivación operativa de una copia/restauración. En fases faltan archivo/commit de cierre,
instalación de la fase siguiente y cancelación de una tarea de reconciliación. La
evaluación de fase, la reconciliación y el chat con CLI real no se han ejecutado. La salida del hito 2 está verificada offline desde la UI hasta COMMITTED,
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
H3.2 completado offline con ledger/API/UI/snapshots y recuperación (D031).
H3.3 completado offline con fases, READY por contenido exacto, cierre/tag y
autorizaciones separadas (D032). Decisiones posteriores del usuario en D033.
H3.4 completado offline: guardia H0/H1, lote desatendido con commits,
enmienda/abandono, tags anotados y reconciliación con agente (D034).
H4.1 completado offline: chat por turnos nuevos de solo lectura y propuestas
confirmadas como tareas normales (D035).
Exportación mecánica de STATE/NEXT_STEPS completada offline (D036).
H4.2 bootstrap guiado completado offline (D037).
H4.3 segundo perfil TypeScript web completado offline (D038).
H5.1 importación JUnit y detalle de tests completado offline (D039).
H5.2 backup/restauración local completado offline (D040).
H5.3 retención local de logs completado offline (D041).
H5.4 diagnósticos locales de compatibilidad completado offline (D042).
H5.5 assets y entrada local completados offline (D043).
H5.6 sesión local y protección uniforme completados offline (D044).
H5.7 recorridos E2E completados offline (D045).
Revisión de cierre del hito 5 completada: alcance offline cubierto.
La elección se resolvió por instrucción explícita del usuario: ejecutor de
validaciones implementado offline (D047). Ver [entrega](discovery/COMMAND_RUNNER.md)
y [revisión anterior](discovery/H5_CLOSURE_REVIEW.md). Revisión independiente
completada con un hallazgo corregido (D048, [dictamen](discovery/COMMAND_RUNNER_REVIEW.md)).
Composición de uso real por TOML local implementada offline (D049,
[entrega](discovery/LOCAL_CONFIG.md)): perfil TypeScript web, `serve --config`
y `check-config`. Propuesta de primer uso real (D033.8) preparada y ensayada
offline con selecciones del usuario (D050, [propuesta](discovery/FIRST_USE_PROPOSAL.md)),
ejecutada una vez con autorización y completa: COMMITTED, fase CLOSED y tag
([resultado](discovery/FIRST_USE_RUN.md)); operación desde el wheel instalado (D051).
Comando único de desarrollo `scripts/dev` implementado (D053, [entrega](discovery/DEV_COMMAND.md)).
Revisor/ejecutor con proveedor elegido implementado y verificado offline (D052,
`local-config-2`, [entrega](discovery/AGENT_ROLES.md)). D057 cerró la matriz con
la combinación 1 COMMITTED y fallos en 2/3; 4 no lanzada. D058 tipa Claude
lector y D059 declara raíces del escritor Codex (`cli-7`), verificados offline.
Propuesta de combinaciones 2–4 preparada y ensayada offline (D060,
[órdenes y criterios](discovery/PROVIDER_MATRIX_CLI7_PROPOSAL.md)); ejecutada
una vez con consentimiento específico y cerrada con parada preventiva (D061,
[resultado](discovery/PROVIDER_MATRIX_CLI7_RUN.md)). La 2 Codex→Codex llega a
COMMITTED con edición real; la comprobación posterior detecta cambio de hash
de configuración global y no se lanzan 3/4. Consentimiento agotado.
Diagnóstico offline del cambio global completado (D062,
[evidencia y límites](discovery/CODEX_GLOBAL_CONFIG_DIAGNOSIS.md)): adición
exacta de confianza acreditada por hash inverso y vía de persistencia interna
identificada en el binario. Atribución original inferida; contención compatible
con auth sin verificar, sin corregir el transporte. Propuesta de contención
completada (D063, [alcance y límites](discovery/CODEX_PROCESS_CONTAINMENT_PROPOSAL.md)):
frontera externa macOS candidata, lectura de auth ficticia y denegaciones de
escritura verificadas con procesos sintéticos. Compatibilidad de auth/refresh,
IPC y sandbox anidado quedaron para calificación. D064 completada offline
([dictamen](discovery/CODEX_CONTAINMENT_QUALIFICATION.md)): 27 escenarios
sintéticos; escrituras directas contenidas, escapes por fd/hardlink/delegación
y rechazo del sandbox interno lector observados. Candidata no calificada
para integración; cli-7 y auth real sin cambios. Diagnóstico del anidamiento y
frontera revisada completados offline (D065,
[dictamen](discovery/CODEX_CONTAINMENT_REVISION.md)): 32 casos; perfiles iguales
componen, restricciones distintas ensayadas se rechazan antes del objetivo.
Cierre de fd/pipe demostrado; hardlink posterior a admisión modifica un
sacrificial exterior. No hay frontera calificada para integrar ni auth/refresh
real certificados. El usuario exige memoria/contexto en `docs/` y pide avanzar
en la persistencia de proyecto. D066 implementa controles explícitos de memoria
automática (`cli-8`, [alcance](discovery/AGENT_PERSISTENCE.md)), con 215 pruebas
offline correctas. No resuelve la escritura de confianza Codex ni certifica
ausencia de estado auxiliar externo. Preparación de arranque completada D067
([dictamen](discovery/CODEX_STARTUP_PREPARATION.md)): perfil de denegación por
defecto no permite un arranque útil del fake; propuesta no apta para CLI real.
12 casos sintéticos y 14 pytest pertinentes correctos. D068 acredita después
la fuente exacta de Codex 0.162.1 (commit embebido en el binario) y suprime
específicamente la persistencia de confianza con projects inline untrusted
en el escritor, conservando permisos/auth (`cli-9`, [corrección](discovery/CODEX_TRUST_SUPPRESSION.md)).
D069/D070 se detienen por contrato contradictorio y timeouts, conservando
originales; contrato/prompt corregidos antes del escritor. **D071 completa
las cuatro combinaciones reales con COMMITTED**, [resultado](discovery/PROVIDER_MATRIX_CLI9_RUN.md).
948 pytest y 121 subtests pasan; memoria automática desactivada y muestras
globales intactas. Comprobación funcional cerrada, aislamiento externo completo
no certificado. Archivado automático no implementado ni probado por esta
matriz. QA visual H5.7 conserva su límite histórico; Claude real con esquema
tipado D058 ya comprobado en D071. Organización documental por fase y estructura
de producto diseñadas (D072, [diseño](discovery/DOCUMENT_ORGANIZATION.md)) y
confirmadas por el usuario (D073). H6.3 implementado offline: contrato documental
v2 opt-in, bloques regenerados por commit, transición de fase y edición confirmada
([entrega](discovery/H6.3_DOCUMENT_CONTRACT.md)). H6.4 implementado offline (D074):
métricas por intento materializadas con procedencia, relleno explícito, agregados por API y tokens/turnos
en el SUMMARY ([entrega](discovery/H6.4_METRICS.md)). H6.5 implementado offline (D075): creación v2
conversacional con borradores en disco y CAS hasta el commit raíz con `phase-000` y P001, y planificación de
la fase siguiente usada por la transición ([entrega](discovery/H6.5_CONVERSATIONAL_CREATION.md)). Siguiente
tarea propuesta: UI H6.2, sin iniciar; será una tarea aparte.

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

## Verificación de H3.2

- Git inicial limpio en `main`, `755e205`. AGENTS/STATE/NEXT_STEPS/DECISIONS,
  especificación §8/§10, backlog H3.2 y contratos H2 revisados.
- 361 pruebas pytest y 121 subtests: 331 anteriores y 30 H3.2. 12 checks
  ligeros, 3 pruebas Node, OpenAPI/tipos, TypeScript/build y diff/whitespace.
  Aviso conocido Starlette/HTTPX conservado, sin cambiar dependencias.
- SQLite/Git/procesos sintéticos: caducidad al decidir/al lanzar, request alterada,
  sustitución, aislamiento de categorías/techos, denegación antes del agente,
  versión y concurrencia, exclusión de checkout, reinicio, once/task y caída
  después de intención; historial y presupuesto preservados. Formatos 1–4
  compatibles; upgrade/downgrade/upgrade y `alembic check` en base temporal.
- API: crear/sustituir/conceder/denegar, acciones habilitadas del servidor,
  confirmación/huella/versiones y 403/409/422; conceder no invoca agentes.
  Regresión del campo `operation` tras fallo detectado en Chrome.
- Revalidar ante REVISE no llama al ejecutor ni consume concesiones; un reintento
  explícito posterior conserva el presupuesto. Se actualizó una prueba H2 que
  caracterizaba la rama anterior, contraria al efecto documentado de revalidar.
- CLI sintética independiente acredita argv nuevo con regla exacta, petición
  persistida antes de efecto, inventario anterior cerrado y configuración intacta;
  red no soportada, permisos fuera del techo y snapshots inválidos rechazados.
- Chrome en `/private/tmp/h32-ui-session`, `127.0.0.1:8017`, sin puertos/supervisor:
  conceder, inspeccionar auditoría, reiniciar servicio/recargar, sustituir y
  denegar. Versiones 11→14, único intento y job DONE conservados; estados/formulario
  inspeccionados visualmente. Servicio y pestaña de prueba cerrados.
- No se migró la SQLite de trabajo del usuario. Sin proveedores/smokes/login,
  secretos, recuperación D020/D022, ReferenceProject, configuración global, colaboración
  automática, harness de desarrollo ni push. Commit solicitado por el usuario.
- Límites: reglas de CLI real no certificadas por fakes; no sandbox físico,
  grants fuera del contrato, políticas editables, permisos vivos/SDK, resolución
  automática de producto o cierre. Sesión local/guardia H0/H1/SSE siguen pendientes.
  Ledger sin paginación ni benchmark de grandes históricos. H3.3 no iniciado.

## Verificación de H3.3

- Git inicial limpio en `main`, `84d3426`. AGENTS/STATE/NEXT_STEPS/DECISIONS,
  especificación §3/§7/§8/§10/§13, backlog H3.3 y contratos H2/H3 revisados;
  `phase_check`/`reconcile_phase`/`apply_phase_close` legacy leídos estáticamente.
- 390 pruebas pytest y 121 subtests: 361 anteriores y 29 H3.3. 12 checks
  ligeros, 3 pruebas Node, OpenAPI (cambio aditivo comprobado estructuralmente)/
  tipos, TypeScript/build y diff/whitespace. Aviso Starlette/HTTPX conservado.
- Git/SQLite temporales y fakes: cierre con tag en el HEAD revisado y documentos
  intactos; READY obsoleto por commit, árbol sucio o documento sin tag; rechazo
  previo por evidencia, versión y preguntas; cambio de autoridad durante el check;
  puertas sin llamada; REVISE → reconciliación ligada al hash revisado; salidas
  inválidas sin reintento; lote/cierre distintos, caducidad y revocación.
- Reinicio sin repetir efectos; caída durante el check y tras la intención de tag
  con recuperación explícita y conciliación; tag ajeno intacto; cuatro cierres
  concurrentes, un job. Migración 0010 ida/vuelta y `alembic check` en base temporal.
- Chrome en demo sintética nueva del scratchpad, `127.0.0.1:8018`: crear fase,
  READY, commit externo → `STALE` sin tag, nuevo READY con confirmación limpiada,
  `CLOSED` con tag en HEAD; reinicio y recarga con historial completo, sin errores
  de consola. Detectó que la lista de fases no se refrescaba; corregido con sondeo.
  Servicio detenido y pestaña cerrada.
- No se migró la SQLite de trabajo del usuario. Sin proveedores/smokes/login,
  secretos, ReferenceProject (solo lectura estática), configuración global,
  colaboración automática, harness de desarrollo ni push. Commit solicitado.
- Límites: evaluación de fase con CLI real no ejecutada; sin reconciliación con
  agente, exportación mecánica de STATE/NEXT_STEPS, archivo/commit de cierre,
  fase siguiente, edición de definición, auto-encadenado de lote, tags anotadas,
  integración de ramas ni sesión local. Exclusión frente a escritores externos
  cooperativa. H3.4 no iniciado (D033).

## Verificación de H3.4

- Git inicial limpio en `main`, `ef126cb`. Revisados AGENTS, STATE, NEXT_STEPS,
  DECISIONS (D032/D033), el informe H3.3, el código de fases, la API y la UI.
- 408 pruebas pytest y 121 subtests: 390 anteriores y 18 de H3.4. Se ajustaron
  las pruebas H0/H1 y H3.3 al cambio de guardia, acciones, `tag_kind` y alcance de
  cierre. 12 checks ligeros y 4 pruebas Node (nueva: cabecera en mutaciones
  H0/H1). OpenAPI y tipos regenerados; TypeScript y build correctos. Se conserva el
  aviso Starlette/HTTPX.
- Git y SQLite temporales con fakes:
  - guardia H0/H1 (Host, Origin, cabecera; 403 antes del 404);
  - lote de dos tareas: cuatro jobs y `COMPLETED`, sin check ni cierre;
  - paradas por bloqueo, pregunta, caducidad, revocación, evidencia invalidada,
    cuarentena (sin repetir) y run ajeno;
  - enmienda (versiones, READY, lotes, documento nuevo, código, sin cambios) y
    abandono;
  - tag anotado (id determinista, conciliación tras caída con otra fecha, tag
    ligero previo intacto);
  - reconciliación con agente (sin planificador, contrato limitado, adopción solo
    tras el commit, escritura fuera de documentos no elegible);
  - migración 0011 (relleno `migrated`, bajada rechazada con fases abandonadas) y
    `alembic check`;
  - HTTP con un proyecto anotado.
- Chrome sobre una demo sintética nueva (scratchpad, `127.0.0.1:8019`):
  - crear la fase;
  - lote desatendido → tarea `COMMITTED` y lote `COMPLETED` sin intervención;
  - comprobar → READY;
  - enmendar → `ACTIVE` sin READY, con la v1 conservada;
  - abandonar → `Abandonada`.

  Sin 403/500 ni errores de consola. El servicio se detuvo y la pestaña se cerró.
- No se migró la SQLite de trabajo del usuario. Sin proveedores, smokes, login,
  secretos, ReferenceProject, configuración global, colaboración automática, harness de
  desarrollo ni push. Commit solicitado por el usuario.
- Límites:
  - lecturas H0/H1 y SSE legacy sin guardia; la sesión local sigue pendiente;
  - revocar no cancela un job ya encolado;
  - el lote no continúa tras una recuperación sin otra autorización;
  - no hay cancelación de la reconciliación ni enmienda del código;
  - la evaluación y la reconciliación no se han ejecutado con CLI real.

  H4.1 no se ha iniciado.

## Verificación de H4.1

- Git inicial limpio en `main`, `d489544`. Revisados AGENTS, STATE, NEXT_STEPS,
  DECISIONS (D033/D034), los informes H3.3/H3.4, el motor, el supervisor, la
  autoridad gestionada, el adaptador CLI, la API y la UI.
- 430 pruebas pytest y 121 subtests: 408 anteriores, 21 de H4.1 y un caso
  parametrizado nuevo de plantilla. Se ajustaron la revisión de esquema esperada y
  el número de plantillas (9). 12 checks ligeros y 4 pruebas Node. OpenAPI y tipos
  regenerados; TypeScript y build correctos; `alembic check` sin cambios
  pendientes. Se conserva el aviso Starlette/HTTPX.
- Git y SQLite temporales con fakes: contexto congelado ante cambios posteriores,
  turnos nuevos con historial explícito, selección validada, seis salidas
  inválidas sin reintento, turno que escribe descartado, aceptación sin
  confirmación o con evidencia obsoleta sin encolar nada, propuesta → planificador
  → ejecutor → revisor → commit con vínculo e idempotencia, sin permisos ni
  acciones de tarea en runs de chat, un turno pendiente, caída → `UNKNOWN` sin
  repetir, FIFO bajo el lock, catálogos antiguos, rol CLI de solo lectura,
  migración ida y vuelta con bajada rechazada y HTTP completo.
- Chrome sobre una demo sintética nueva (scratchpad, `127.0.0.1:8020`): crear
  conversación → mensaje → turno respondido con propuesta → botón deshabilitado sin
  fase ni confirmación → confirmar → `CHAT-T001` en `ACCEPTANCE_READY` → commit →
  `COMMITTED`, visible en la propuesta. Llamadas sintéticas `chat`, `planner`,
  `executor` y `reviewer`. Sin 4xx/5xx de la API ni errores de consola. El servicio
  se detuvo y la pestaña se cerró.
- No se migró la SQLite de trabajo del usuario. Sin proveedores, smokes, login,
  secretos, ReferenceProject, configuración global, colaboración automática, harness de
  desarrollo ni push. Commit solicitado por el usuario.
- Límites: sin CLI real ni App Server/SDK. La detección de escritura cubre el
  checkout por evidencia Git. El turno espera el lock. No hay encolado automático
  en un modo autorizado, cancelación o borrado de conversaciones ni vínculo inverso
  en la vista del run.

  La exportación mecánica de STATE/NEXT_STEPS no se ha iniciado.

## Verificación de la exportación mecánica

- Git inicial limpio en `main`, `233cb51`. AGENTS/STATE/NEXT_STEPS/DECISIONS,
  especificación §7, backlog H4 y contratos de fases/Git/cola revisados. Sin
  contradicciones materiales. D036 conserva el cierre separado de la exportación.
- 462 pruebas pytest y 121 subtests; 430 anteriores y 32 de exportación. También
  12 checks ligeros, 4 pruebas Node, OpenAPI/tipos regenerados, TypeScript/build y
  `alembic check` sin operaciones nuevas en SQLite temporal. Esquema 0012 y locks
  de dependencias conservados; aviso Starlette/HTTPX conocido.
- Git/SQLite temporales: determinismo, conservación de prosa/CRLF, marcadores
  inválidos, rutas/archivos protegidos o no regulares, staging, deriva externa en
  todos los documentos, snapshot/versiones/hash obsoletos, confirmación, guardias
  HTTP, idempotencia/concurrencia y reinicio. Lote activo rechazado; READY obsoleto
  no cierra; fase CLOSED exportada sin mover el tag; fase antigua rechazada.
- Caídas antes de escribir, entre documentos, tras el commit y dentro de la
  transacción de adopción: cuarentena y confirmación explícita, mismo run,
  operación/intención/id de commit; sin duplicación ni agentes. Los bytes ajenos
  posteriores a una caída permanecen intactos.
- Chrome en checkout/base sintéticos nuevos bajo `/private/tmp`, :8021: preview
  visible, commit deshabilitado sin confirmación, confirmar → COMMITTED → preview
  vacío, prosa/base documental conservadas y recarga con resultado persistido.
  Sin errores de consola; servidor y pestaña temporales cerrados.
- Diff/whitespace revisados. Sin proveedores/smokes, login, red externa,
  ReferenceProject, configuración global, colaboración automática, harness de desarrollo
  ni push. No se migró la SQLite de trabajo del usuario. Commit solicitado.
- Límites: exclusión frente a escritores externos cooperativa; dos reemplazos
  individuales, sin atomicidad conjunta. Cambios externos tras commit incierto
  requieren restauración manual del contenido sellado antes de adoptar. Sin
  limpieza automática de temporales ni benchmark de grandes históricos; solo la
  última fase y documentos existentes UTF-8 de hasta 512 KiB.

  H4.2 no se ha iniciado.

## Verificación de H4.2

- Git inicial limpio en `main`, `d371710`. Leídos AGENTS, STATE, NEXT_STEPS,
  DECISIONS y especificación/backlog H4.2; contratos de prompts/permisos,
  cola/recuperación, fases y Git revisados. D037 delimita la plantilla inicial.
- 510 pruebas pytest y 121 subtests: 462 anteriores y 48 nuevas H4.2. 12 checks
  ligeros y 4 pruebas Node. OpenAPI/tipos regenerados, TypeScript/build y diff
  correctos. Ninguna ruta previa cambió; solo dos purpose nuevos en los esquemas
  de runs. Migración 0013 ida/vuelta y `alembic check` en SQLite temporal;
  bajada con historial rechazada. Codec y locks de dependencias conservados.
  Aviso conocido Starlette/HTTPX conservado.
- Git/SQLite temporales: preview determinista/sin efectos, contrato acotado,
  confirmación, carpetas no vacías/ocultas/enlazadas/Git, destinos reemplazados,
  hashes/versiones/identidad/política cambiados, guardias HTTP, cuatro creaciones
  concurrentes y recuperación idempotente tras reinicio.
- Caídas antes de escritura, entre documentos, después del commit y en adopción:
  cuarentena sin repetir, confirmación explícita, mismo run/intención/commit y una
  fase. Cambios externos en bytes, modos, symlinks, HEAD, refs e índice se conservan.
  Las pruebas detectaron una lectura de índice que actualizaba su cache-tree;
  corregida para usar la copia temporal H2.4 y conservar los bytes originales.
- Propuestas falsas con brief/prompt congelados, activación posterior sin mutar el
  intento, salida inválida descartada, escritor rechazado sin descartar sus bytes,
  pendiente excluyente y caída → UNKNOWN sin otra llamada. Rol CLI `bootstrap`
  caracterizado offline con sandbox read-only y sesión nueva.
- Chrome en demo nueva bajo `/private/tmp`, :8022: brief → propuesta falsa →
  decisiones → preview/confirmación → commit raíz/fase ACTIVE → primera tarea
  ACCEPTANCE_READY → diff limitado al checklist → commit explícito → COMMITTED.
  Reinicio/recarga conserva resultado y deshabilita encolado duplicado desde el
  asistente. Destino no vacío conduce a importación y conserva su README.
  Roles auditados `bootstrap`, `executor`, `reviewer`, todos falsos; sin errores de
  consola. Servicio y pestaña temporales cerrados.
- Sin proveedores/smokes/login, red externa, ReferenceProject, configuración global,
  colaboración automática, harness de desarrollo ni push. No se migró la SQLite
  de trabajo. Commit solicitado por el usuario.
- Límites: primera plantilla documental, sin generación/instalación de un stack
  ni preparación automática; Git/política comprobados, herramientas externas y
  CLI real no verificadas. Destinos existentes registrados por el servidor;
  sin registro/selector de carpetas HTTP. Exclusión externa cooperativa, sin
  atomicidad del conjunto de archivos. Marca Git ausente/dañada exige recuperación
  manual; sin abandono ni limpieza automática de bootstrap incierto.

  H4.3 no se ha iniciado.

## Verificación de H4.3

- Git inicial limpio en `main`, `2b73f50`. Leídos AGENTS, STATE, NEXT_STEPS,
  DECISIONS, especificación §9–11 y backlog H4.3. Sin contradicciones materiales.
- 526 pruebas pytest y 121 subtests: 510 anteriores y 16 nuevas H4.3. También
  12 checks ligeros, cuatro tests del cliente Node y check TypeScript del frontend.
  La suite conserva los checks de migraciones y sincronización OpenAPI; no hay
  migración, cambio del codec o contratos HTTP que regenerar. Aviso conocido
  Starlette/HTTPX conservado.
- Node/npm/tsc reales en checkouts sintéticos: preparación offline, check, tres
  tests Node y build; se comprueban salida/duración y árbol Git intacto pese a
  dependencias y artefactos ignorados. Lock separado con TypeScript 5.9.3.
- Regresión introducida solo en copia → corrección falsa → validaciones reales
  → ACCEPT falso → ACCEPTANCE_READY → commit H2.4 limitado a `src/estimate.ts`.
  Lectura posterior conserva snapshots/historial/resultados; origen del worktree
  intacto. Seis comandos con eventos de inicio/fin y evidencia Git compartida por
  tests/review/aceptación.
- Tests, tipos y build fallidos; modificación de tests protegidos aunque pasen
  validaciones; caché vacía, lock inconsistente y engines incompatibles;
  comandos fuera de prefijos; denegación once consumida sin invocar al ejecutor;
  bytes externos después de validar conservados sin intención de commit.
- Diff/whitespace revisados. Sin proveedores/smokes/login, red externa, ReferenceProject,
  configuración global, colaboración automática, harness de desarrollo o push.
  No se migró la SQLite de trabajo. Commit solicitado por el usuario.
- Límites: runner de comandos real solo de prueba para fixture confiable, sin
  recuperación/cancelación de validadores de producto. Interacción con DOM mínimo,
  sin navegador ni servidor web. Sin JUnit/cobertura, formatter o nueva plantilla
  de bootstrap; la plantilla H4.2 sigue siendo documental.

  H5.1 importación JUnit queda siguiente, sin iniciar.

## Verificación de H5.1

- Git inicial limpio en `main`, `95f543a`. Leídos AGENTS, STATE, NEXT_STEPS,
  DECISIONS, especificación §9–11 y backlog H5. Alcance original conservado;
  no se implementó otro incremento de H5.
- 43 casos nuevos JUnit y comprobación de los tres casos del reporter Node real
  en el recorrido H4.3. Parsers/rutas, límites, ausencias/null/cero, XML parcial,
  inválido, DTD/entidades UTF-8/UTF-16, contadores/identidades/estados incoherentes,
  reportes obsoletos y cambios durante captura comprobados offline.
- Git/SQLite temporales: comandos/intentos/evidencia congelada, codec 6 y formatos
  anteriores, revalidación conservando originales, check de fase, reinicio,
  paginación y descarga después de editar/eliminar el origen. Fallos del comando
  o JUnit con exit 0, review inválida y cambios externos de código impiden
  aceptación/commit; commit exitoso limitado al contenido revisado.
- 569 pruebas pytest y 121 subtests correctos (526 anteriores + 43 JUnit), con
  checks existentes de esquema y sincronización OpenAPI. Checks ligeros (12),
  cliente Node (4), OpenAPI/tipos generados y TypeScript/build correctos.
  Sin migración nueva ni cambios de locks; aviso conocido Starlette/HTTPX.
- Chrome con UI compilada y checkout/SQLite sintéticos bajo `/private/tmp`,
  `127.0.0.1:8023`, sin supervisor activo: tabla de éxito/fallo/error/omisión,
  duraciones cero/ausentes, error con `<script>` mostrado como texto,
  cobertura/hash/original y commit deshabilitado. Sin errores de consola.
  Servicio y pestaña de prueba cerrados.
- Sin proveedores, smokes, login, cambios globales, ReferenceProject, colaboración
  automática, harness como orquestador de desarrollo ni push. No se migró la
  SQLite de trabajo. Commit solicitado por el usuario.
- Límites: captura/frescura cooperativa frente a escritores externos, XML hasta
  2 MiB/2.000 casos, originales en historial sin retención/GC o benchmark de gran
  volumen. Sin importación JUnit legacy ni medición de cobertura de código.
  Una caída antes del checkpoint conserva los eventos del comando y requiere
  revalidación explícita; no se atribuye el archivo anterior automáticamente.

  H5.2 backup/restauración local no se ha iniciado.

## Verificación de H5.2

- Git inicial limpio en `main`, `16c41f7`. Leídos AGENTS, STATE, NEXT_STEPS,
  DECISIONS, especificación §14 y backlog H5. Alcance original conservado;
  no se inició otro incremento de H5. D040 fija consistencia y guardia de consulta.
- 43 casos nuevos con SQLite/WAL, Git y artefactos sintéticos: copia →
  verificación → restauración → consultas CLI/HTTP; filas operativas, snapshots,
  contextos, historial/JUnit y eventos exactos. Copias H2.5/exportación conservadas
  y contenido legacy servido desde el mapeo tras borrar su original.
- Capturas de procesos Python sintéticos: prompts/streams finales, rangos/hash,
  colas sin checkpoint y streams aún ausentes. Intentos pendientes, jobs
  RECOVERY_REQUIRED/QUEUED y locks no se convierten en efectos ni estados terminados.
- Guardia persistente en SQLite, incluso al mover solo el fichero; API consulta
  sin cargar configuración ambiental o puertos opt-in. Supervisor/observador
  omitidos; mutaciones 409 y escrituras de biblioteca rechazadas antes de efectos.
- Integridad/FK, versión futura, codec/original JUnit, hashes, artefactos ausentes,
  enlaces simbólicos/duros/FIFO, límites, rutas inseguras y referencias omitidas/
  repetidas comprobados. WAL ajeno no sellado rechazado. Escritor DB concurrente
  bloqueado; cambios durante copia/restauración invalidan sin publicar COMPLETE;
  destinos ocupados y checkouts conservados. Originales históricos inexistentes
  o convertidos en enlaces no afectan la verificación del bundle.
- Regresión final: 612 pruebas pytest y 121 subtests; 569 anteriores + 43 H5.2.
  12 checks ligeros, cuatro pruebas Node, TypeScript/build y checks existentes de
  migraciones/OpenAPI correctos. Esquema `0013_bootstrap`, codec/locks/contratos
  HTTP conservados; sin regeneración necesaria. Aviso Starlette/HTTPX conocido.
- Diff/whitespace revisados. Sin proveedores/smokes/login, red externa, ReferenceProject,
  configuración global, colaboración automática, harness de desarrollo ni push.
  No se copió ni migró la SQLite de trabajo. Verificación HTTP con TestClient;
  no se arrancó servidor/navegador. Commit solicitado por el usuario.
- Límites: parada y exclusión de escritores externos cooperativas; 256 MiB por
  fichero/SQLite, 2 GiB de artefactos, 10.000 referencias y manifiesto de 4 MiB,
  sin benchmark. Se restaura evidencia de consulta, sin reactivar ejecución,
  registrar proyectos gestionables, respaldar Git/fuentes externas, GC ni cifrado.
  Parciales permanecen para inspección, sin limpieza o reutilización automática.

  H5.3 retención local de logs queda siguiente, sin iniciar.

## Verificación de H5.3

- Git inicial limpio en `main`, `120f315`. Leídos AGENTS, STATE, NEXT_STEPS,
  DECISIONS, especificación §14 y backlog H5. Alcance original conservado;
  D041 fija política, autoridad y recuperación. No se inició otro incremento.
- 43 casos nuevos de retención en SQLite/capturas sintéticas temporales:
  política, preview determinista sin efectos, hashes obsoletos/confirmación,
  conservación de historial/filas/prompts/resultados, intentos activos/inciertos,
  locks, propietarios/grupos, pérdida/corrupción/enlaces/FIFO, rangos, referencias
  compartidas, límites y exclusión de escritor SQLite concurrente.
- Caídas antes/después de unlink dejan intenciones pendientes, bloquean backup y
  exigen preview/reconfirmación explícita. La conciliación conserva la intención
  y distingue bytes observados de retirados; cambios ajenos no se eliminan.
  Purga repetida con preview nueva no añade efectos; secuencias/versiones correctas.
- CLI y HTTP distinguen retenido/purgado/pendiente/perdido/no verificado, hash exacto,
  pertenencia de intento y guardia Host. Backup/restauración con ausencias autorizadas
  y originales restantes; bundles anteriores intactos, corrupción de auditoría y
  reaparición del original purgado rechazadas. Consulta restaurada independiente
  de originales; marca de archivo de consulta impide purgar una restauración.
- Regresión completa: 654 pruebas y 121 subtests correctos. Tras reforzar el hash
  de referencias/rangos y añadir su caso de corrupción, regresión final de 86
  pruebas H5.2/H5.3 correcta (43 + 43); 655 casos disponibles en total.
  12 checks ligeros, cuatro pruebas Node, OpenAPI/tipos
  regenerados, TypeScript/build y comprobaciones existentes de esquema. Esquema,
  codec y locks de dependencias conservados. Aviso Starlette/HTTPX conocido.
- Diff/whitespace y 163 enlaces locales revisados. No se copió, purgó ni migró almacenamiento real del
  usuario; solo artefactos temporales sintéticos. Sin proveedores/smokes/login,
  red externa, ReferenceProject, configuración global, colaboración automática, harness
  de desarrollo ni push. HTTP por TestClient y UI compilada; sin navegador vivo.
  Commit solicitado por el usuario.
- Límites: parada/exclusión externa cooperativas, sin atomicidad SQLite/unlink,
  256 MiB por fichero, 2 GiB por aplicación, 10.000 referencias; sin benchmark,
  rotación/cap nuevo de captura, GC, purga de SQLite/legacy/JUnit ni abandono de
  intención pendiente. No se elimina ni adopta un original purgado reaparecido.

  H5.4 diagnósticos locales de compatibilidad queda siguiente, sin iniciar.

## Verificación de H5.4

- Git inicial limpio en `main`, `5a44926`. Leídos AGENTS, STATE, NEXT_STEPS,
  DECISIONS, especificación §14 y backlog H5. Alcance original conservado;
  D042 fija preflight compartido y límites. No se inició H5.5.
- 52 casos nuevos: ambos proveedores sintéticos, versiones inesperadas/distintas,
  flags con prefijos, UTF-8/salidas inválidas, exit no cero, flood stdout/stderr,
  timeout con pipes cerrados o heredados por hijos y limpieza incierta.
- Configuración JSON acotada: campos/tipos/baseline inválidos, duplicados, anidado
  profundo, archivo ausente/grande/enlazado/FIFO, rutas no codificables y fallo
  de recursos. Sin herencia del entorno, valores secretos ni salidas libres en
  informes; snapshots/hash del adaptador y archivos de configuración intactos.
- Regresión completa final: 707 pruebas pytest y 121 subtests correctos,
  incluidos checks existentes de migraciones/OpenAPI; aviso Starlette/HTTPX
  conocido. Regresión focal de 113 casos diagnóstico/adaptadores/entorno correcta;
  12 checks ligeros y cuatro pruebas Node correctos. CLI `python -m ... diagnose-cli`
  verificada también como proceso con ambos ejecutables sintéticos y exit 0.
  La comprobación de hijos con `ps` requirió salir del sandbox, con autorización.
- 166 enlaces documentales locales y diff/whitespace revisados. No hay cambios
  HTTP/frontend, esquema, codec o locks; no se regeneraron tipos/OpenAPI ni se
  arrancó servidor/navegador. Sin CLI reales, proveedores/smokes/auth status,
  instalación, configuración global, ReferenceProject, colaboración automática,
  harness como orquestador de desarrollo ni push. SQLite de trabajo intacta.
- Límites: coincidencia versión/help no certifica auth/cuota/modelos/argv completo,
  permisos efectivos ni retries internos. Ejecutables de confianza, sin sandbox
  físico; configuración estructural, no reparación automática. Máximos: JSON
  64 KiB, salida combinada 256 KiB y 10 s por sonda más hasta 1 s de recogida.

  Siguiente tarea: H5.5 assets web empaquetados y comando único de inicio, sin iniciar.

## Verificación de H5.5

- Git inicial limpio en `main`, `58ce0e3`. Leídos AGENTS, STATE, NEXT_STEPS,
  DECISIONS, especificación §14/§10 y backlog H5. Alcance original conservado;
  D043 documenta distribución/arranque y límites. No se inició H5.6.
- Sdist y wheel construidos offline desde staging, con UI compilada desde npm
  lock; Node/npm/uv explícitos. Los 13 scripts de revisión y plantilla Alembic
  conservan bytes; env.py añade URL explícita. Locks sin cambios, uv lock --check
  correcto; esquema `0013_bootstrap`, codec 6 y cli-4 conservados.
- 13 casos focales finales correctos: base nueva fuera de cwd y del entorno,
  rechazo de destinos existentes/enlaces/directorios y auxiliares SQLite,
  rutas/puertos inválidos sin creación, assets independientes del cwd,
  override explícito y API 404. Regresión completa previa a los tres últimos
  casos: 717 pruebas y 121 subtests correctos; total disponible final 720.
  Aviso de deprecación Starlette/HTTPX conocido. Checks existentes de
  esquema/OpenAPI incluidos en la regresión; sin cambios HTTP ni tipos nuevos.
- 12 checks ligeros y cuatro pruebas Node correctos; TypeScript/build correctos.
  Wheel instalado offline en venv nuevo con 18 dependencias de producción
  fijadas y hashes, sin dependencia del checkout en sys.path ni Node en PATH.
  Bytes de código/plantillas/migraciones/assets contrastados con originales.
- HTTP real en loopback desde cwd temporal: HTML/JS/CSS, health, ausencia de
  proyectos, mutación sin cabecera denegada, simulación/reinicio, configuración
  inválida y esquema sin preparar. Backup/verificación/restauración por CLI;
  lectura del histórico, UI disponible y mutación 409, ignorando configuración
  ambiental inválida de una copia. Procesos detenidos al terminar.
- Sandbox bloqueó bind de loopback; verificación realizada fuera con aprobación.
  Se corrigió la ruta temporal del verificador a canónica para respetar la
  guardia H5.2. No se relajó esa guardia. 167 enlaces locales y diff revisados.
- Sin proveedores/smokes/auth, publicación/push, configuración global, datos
  privados, SQLite de trabajo, ReferenceProject ni colaboración automática. Sin
  navegador visual, otras plataformas, actualización instalada de bases
  existentes o flujo de agentes reales. Sesión local pendiente. Commit solicitado.

  Siguiente tarea: H5.6 sesión local y protección de endpoints, sin iniciar.

## Verificación de H5.6

- Git inicial limpio en `main`, `0413d78`. Leídos AGENTS, STATE, NEXT_STEPS,
  DECISIONS, especificación §10 y backlog H5. Alcance original conservado;
  D044 fija sesión efímera, amenazas y límites. H5.7 no se inició.
- 45 casos nuevos: acceso anónimo a rutas/acciones/streams, sin efectos; permisos
  del archivo privado, cookie, caducidad, cierre, rotación, reinicio y limpieza;
  Host/Origin/CSRF, claves inválidas sin eco, límites, proxy Vite con Host
  conservado y stream revocado. Pruebas anteriores autentican por login real;
  no existe bypass de autenticación de producto para tests.
- Regresión final: **765 pruebas pytest y 121 subtests correctos**, incluidos
  migraciones, OpenAPI, contenido/evidencias seguros y restauraciones. Se conserva
  el aviso Starlette/HTTPX. Pase previo detectó restricciones de ps del sandbox
  en dos tests existentes y regeneración concurrente de OpenAPI; suite final
  con fuentes sincronizadas fuera del sandbox autorizada, sin fallos.
- **12 checks ligeros y 5 pruebas Node correctos**; 401 notifica ausencia de sesión
  sin repetir acciones ni cambiar su sobre pendiente. OpenAPI/tipos regenerados,
  TypeScript y build Vite correctos. Esquema/codec/cli-4/locks sin cambios.
- Sdist/wheel construidos offline y wheel instalado en venv nuevo con hashes,
  cwd ajeno y PATH sin Node. Recursos exactos, login/cierre, UI/assets/API,
  simulación/reinicio, 401 sin sesión y backup/restauración de consulta con
  mutaciones 409 verificados por HTTP real. Clave ausente de logs de proceso.
- Intento de UI en Chrome sobre servidor sintético :8026 bloqueado por el cliente
  (`ERR_BLOCKED_BY_CLIENT`); no se acredita QA visual ni recorrido E2E amplio.
  Servidor temporal detenido con limpieza de la clave. Bind y cierre requirieron
  aprobación fuera del sandbox. Límites de cookies por hostname/puerto y HTTP
  local documentados, sin promesa de aislamiento frente a dueño/root o servicios
  locales hostiles visitados por el usuario.
- Diff/whitespace y enlaces documentales locales revisados. Sin proveedores,
  smokes, auth de CLI, cambios globales, ReferenceProject, colaboración automática,
  harness como orquestador de desarrollo ni push. SQLite de trabajo intacta.
  Commit solicitado por el usuario.

  Siguiente tarea: H5.7 recorridos E2E offline, sin iniciar.

## Verificación de H5.7

- Git inicial limpio en `main`, `189aa10`. Leídos AGENTS, STATE, NEXT_STEPS,
  DECISIONS y secciones pertinentes de especificación/backlog. Alcance preservado;
  D045 y matriz de trazabilidad en [H5.7_E2E.md](discovery/H5.7_E2E.md).
- Seis pruebas nuevas conectan sesión/API, confirmación, importación/bootstrap,
  denegación/sustitución, fallos de tests/review, cuarentena, reinicio, evidencia
  exacta y commit; Git/SQLite reales temporales, agentes/comandos falsos.
  Se mantiene fase ACTIVE y checkout principal intacto, sin integrar ramas.
- Regresión completa: **771 pruebas y 121 subtests correctos** (765 + 6),
  incluidos migraciones y OpenAPI. **12 checks ligeros y 6 pruebas Node**;
  respuesta perdida/401 conserva el mismo sobre hasta reenvío humano. Persiste
  el aviso Starlette/HTTPX conocido, sin cambiar dependencias.
- Build sdist/wheel offline con TypeScript/Vite correcto. Instalación en venv
  nuevo con hashes, cwd/PYTHONPATH temporal sin código de desarrollo y PATH sin
  Node/proveedores (Git explícito). HTTP real: bootstrap, tarea, único commit,
  doble envío/reinicio y exactamente un ejecutor/revisor falsos auditados.
- Backup y restauración por CLI, servidores detenidos; checkout original movido
  fuera de su ruta. Historial/commit/intentos/eventos restaurados idénticos;
  supervisor deshabilitado, factory ambiental ignorada y mutaciones 409.
- Chrome sobre fixture temporal :8027 rechazó `ERR_BLOCKED_BY_CLIENT` antes de
  mostrar UI. Sin QA visual ni clics acreditados; no se eludió el bloqueo.
  Uvicorn detenido limpiamente y clave retirada; bind/TERM fuera del sandbox
  autorizados. SQLite de trabajo y configuración global intactas.
- Diff/whitespace y enlaces documentales revisados. Sin proveedores/smokes,
  ReferenceProject, colaboración automática, harness de desarrollo, publicación ni
  push. Commit solicitado por el usuario. Esquema/codec/cli-4/locks conservados.
- Siguiente paso: revisión del cierre del hito 5 y elección de nuevo alcance,
  sin iniciar tarea adicional. QA visual y recorrido de proveedores pendientes;
  D033.8 requiere autorización específica para este último.

## Revisión de cierre del hito 5

- Git inicial limpio en `65aac62`. Contrastados backlog H5, especificación §14–16,
  entregas y evidencia H5.7 con los puertos y composición existentes. Resultado
  y límites en [H5_CLOSURE_REVIEW.md](discovery/H5_CLOSURE_REVIEW.md).
- Alcance offline cubierto; no se declara MVP completo ni uso real certificado.
  Falta un ejecutor de validaciones de producto: el protocolo y la inyección
  existen, pero los comandos TypeScript reales solo usan un runner de tests.
  QA visual reciente, composición real y smoke completo siguen pendientes.
- README actualizado: conservaba H5.7 como pendiente y el recuento anterior.
  Documentación, enlaces y diff comprobados; sin cambios de código ni nuevas
  ejecuciones de tests/proveedores. Se conserva la evidencia previa de H5.7.
- Siguiente alcance recomendado: concretar ejecutor real de validaciones con
  recuperación y pruebas offline; elección consultada al usuario, sin implementar.
  No se inicia piloto, smoke, publicación ni push.


## Verificación del ejecutor de comandos de producto

- Git inicial limpio en `main`, `3bb9541`. Leídos AGENTS, STATE, NEXT_STEPS,
  DECISIONS y revisión de cierre; contrastados protocolo, validación/JUnit,
  supervisor, persistencia y grupos existentes. Elección explícita del usuario;
  [alcance y criterios](discovery/COMMAND_RUNNER_SCOPE.md) escritos antes del código.
- 39 casos nuevos de comandos nativos: éxito/exit no cero/ejecutable ausente,
  argv literal, entorno/cwd, timeout, exceso en ambos streams, bytes no UTF-8,
  configuración congelada y autorización exacta. Hijos supervivientes con pipes
  abiertos/cerrados, fallo del journal en cuatro etapas, grupo desconocido,
  propietario abierto y rechazo de command_id repetido.
- Proceso separado del supervisor cae realmente después de persistir bytes;
  el validador sigue vivo tras expirar lease y reiniciar. Lock y evidencia parcial
  conservados; confirmación rechazada hasta observar grupo ausente. La prueba
  detiene solo su grupo sintético; producto no señaliza PIDs recuperados ni relanza.
- Cuatro recorridos TypeScript con el runner de producto: Node/npm/tsc reales
  offline, Git/worktree/SQLite temporales, agentes falsos y JUnit original con
  hash. Éxito hasta commit y restauración; tests/tipos fallidos y deriva posterior
  impiden commit. Snapshots, eventos, capturas e historial exactos tras reinicio
  y backup/restauración de consulta; runner de tests no ejecuta esos comandos.
- Regresión completa final: **810 pruebas pytest y 121 subtests correctos**.
  Primer pase detectó un `capture_json=null` adicional en prompts antiguos;
  corregido con serialización omisiva y segundo pase completo correcto.
  Aviso Starlette/HTTPX conocido, sin cambios de dependencias. Checks de esquema
  y OpenAPI incluidos; esquema `0013_bootstrap`, cli-4 y locks conservados.
- **12 checks ligeros y 6 pruebas Node correctos**. 196 enlaces documentales
  locales y diff/whitespace revisados. Codec 7 para captura nativa, formatos 1–6
  compatibles; no hace falta regenerar API/tipos ni migrar SQLite.
- Sin proveedores/smokes/login, instalaciones con red, publicación/push, UI nueva,
  configuración global, ReferenceProject, subagentes ni harness de desarrollo.
  SQLite real de trabajo intacta. Sin nueva QA visual, build del frontend ni
  verificación del wheel instalado: no se han cambiado UI o empaquetado.
- Límites: POSIX cooperativo, sin hijos escapados/daemonización ni aislamiento
  físico; autorización/configuración manual del servidor, sin composición
  completa de proveedores, benchmark ni retención de capturas SQLite.
- Commit solicitado por el usuario. Siguiente tarea propuesta: revisión
  independiente del incremento y su recuperación, coordinada por el usuario;
  no iniciada. [Entrega y operación](discovery/COMMAND_RUNNER.md), D047.

## Revisión independiente del ejecutor de comandos

- Git inicial limpio en `main`, `c3f941b`. Leídos AGENTS, STATE, NEXT_STEPS y
  DECISIONS; contrastados D047, entrega, alcance, adaptador, gate, supervisor,
  repositorio, codec, backup/retención y pruebas. Sin subagentes.
- Hallazgo medio corregido: un run congelado con `command_config_sha256` podía
  ejecutarse con otro runner devuelto por la composición. `_bind_commands`
  aborta antes de efectos con cuarentena; prueba nueva falló antes y pasa ahora.
- Ventana intención/identidad/GO, exclusión, captura y compatibilidad 1–6 sin
  hallazgos; descartado un falso positivo del codec 7 sin JUnit. Límites
  conocidos (PGID sin arranque, heartbeat con validador silencioso) registrados.
- Regresión completa: **811 pruebas pytest y 121 subtests correctos**, aviso
  Starlette/HTTPX conocido; **12 checks ligeros y 6 pruebas Node correctos**.
  Esquema/codec/cli-4/OpenAPI/UI/dependencias sin cambios; sin wheel ni QA visual.
- Sin proveedores, smokes, red, configuración global, ReferenceProject ni harness de
  desarrollo. Commit solicitado por el usuario. D048,
  [dictamen](discovery/COMMAND_RUNNER_REVIEW.md).
- Siguiente: elección del usuario de nuevo alcance; no iniciada.

## Verificación de la composición de uso real por TOML local

- Git inicial limpio en `main`, `5e0c374`. Decisiones del usuario: TOML fuera
  del checkout con `tomllib` y perfil TypeScript web. [Alcance y criterios](discovery/LOCAL_CONFIG_SCOPE.md)
  escritos antes del código; sin contradicción con la especificación.
- `services/local_config.py` (`local-config-1`): archivo privado del operador,
  esquema estricto, composición nueva por job (cli-4, commands-1, Git) y
  versiones con hash de composición. `serve --config`, `check-config
  [--preflight]` y `from_environment`. Validación de proyectos del runtime
  separada como `validate_projects`, sin cambio de reglas.
- 35 casos nuevos: composición sin procesos, 22 rechazos de esquema y 7 del
  archivo con motivo comprobado, autorización exacta adicional, cuarentena por
  composición cambiada antes de efectos y recorrido completo con CLI falsas por
  el adaptador real, Node/npm/tsc reales, JUnit, aceptación y commit con la
  identidad configurada. `check-config` sin valores de entorno.
- Regresión completa: **846 pruebas pytest y 121 subtests correctos**, aviso
  Starlette/HTTPX conocido; **12 checks ligeros y 6 pruebas Node correctos**.
  Esquema/codec/cli-4/OpenAPI/UI/dependencias sin cambios; sin wheel, QA visual
  ni build del frontend (no cambian UI ni empaquetado).
- Sin proveedores reales, login, smokes, red, configuración global, ReferenceProject
  ni harness de desarrollo. Commit solicitado por el usuario (`8c0e169`).
- Siguiente: propuesta de primer uso real (smoke D033.8) sobre checkout
  desechable con este TOML, que requiere autorización específica; no iniciada.

## Preparación de la propuesta de primer uso real

- Git inicial limpio en `main`, `8c0e169` (un commit por delante de origin).
  Leídos AGENTS, STATE, NEXT_STEPS y DECISIONS; contrastados D033.8, D049,
  la composición local, el perfil TypeScript, fases y la propuesta D024/D025.
- Selecciones elegidas por el usuario en esta sesión: ejecutor
  `claude-sonnet-4-6`/`low` con `Read`, `Edit`, `Write`, `Glob`, `Grep`;
  revisor y evaluación de fase `gpt-6-luna`/`medium`; planificador
  `gpt-6-luna`/`low` no invocado por planificación determinista;
  `max_revision_cycles = 0`. D050, [propuesta](discovery/FIRST_USE_PROPOSAL.md).
- Hallazgos: el enlace `claude` del usuario apunta a 2.1.296, no admitido por
  `cli-4`; se fija el binario versionado 2.1.295 con `DISABLE_AUTOUPDATER=1`.
  `codex` necesita Node en `PATH`. Los tags de fase no admiten `/`.
- [`examples/first_use/prepare.sh`](../examples/first_use/prepare.sh): checkout
  desechable desde la fixture con regresión deliberada, documentos de fase,
  TOML concreto 0600 y áreas privadas; falla si `BASE` existe.
- Ensayo offline en el scratchpad: preparación; `check-config` sin preflight
  válido (cli-4, 0.162.1, 2.1.295, commands-1); `init-db`; admisión en proceso
  con supervisor forzado a `false`: contrato determinista, fase `P001` y job
  `QUEUED`, sin procesos; comandos del perfil con el entorno exacto del TOML:
  `npm ci --offline`/check/build 0 y test 1 (2 de 3 fallan por la regresión).
  TOML documentado idéntico al generado (comparado por diff).
- **12 checks ligeros y 35 pruebas de `test_local_config.py` correctos**;
  sintaxis `sh -n`, enlaces locales y whitespace revisados. Sin regresión
  pytest completa ni pruebas Node: solo cambian documentos y un script de ejemplo.
- Sin CLI de proveedores (ni version/help), `serve`, red, consumo, login,
  configuración global, ReferenceProject ni harness de desarrollo. Sin cambios de
  código, esquema, codec, cli-4, OpenAPI ni UI. Commit solicitado por el usuario.
- Siguiente: ejecutar la propuesta D050 solo con consentimiento específico; no
  iniciada.

## Ejecución autorizada del primer uso real (D050)

- Autorización del usuario: «Autorizo ejecutar la propuesta D050 una vez».
  Git limpio en `main`, `0e39364`. Binario Claude 2.1.295 presente y `BASE`
  libre. Preparación con el script (TOML idéntico a la propuesta) y preflight
  `version_help_match` en ambas CLI.
- `serve` desde la instalación editable falló antes de servir porque faltaban
  los assets web. Sin consumo. Consultado el usuario, se aplicó D051: wheel
  actual construido en el área, `check_distribution.py` correcto, venv nuevo
  instalado offline con hashes y `serve --config` desde ese venv, con las
  mismas versiones congeladas.
- Recorrido por HTTP: fase P001, run `abcc508f-…` → `ACCEPTANCE_READY`
  (ejecutor 8,1 s, Read + Edit, `tasks * 30`; review ACCEPT) → commit
  `8999af8` → check READY (evaluación de fase con los tres criterios
  superados) → cierre `CLOSED` y tag ligero `first-use-p001` en HEAD.
- Tres invocaciones de proveedor `complete`, exit 0 y stderr vacío. Nueve
  comandos con exit 0 bajo la configuración congelada y JUnit `complete`. Jobs
  `DONE` con propietario cerrado y sin locks. Uso reportado registrado aparte
  de lo solicitado; Codex no reporta el modelo.
- Servicio detenido con TERM y clave retirada. SQLite reabierta desde el
  paquete instalado: `history`/`versions` idénticos a la instantánea de la API.
  Checkout desechable limpio; repositorio, fixture y `dist/` intactos.
- Observado: la CLI de Claude creó un `memory/` vacío en
  `~/.claude/projects/-private-tmp-harness-first-use-web`. No se toca.
- Sin tests nuevos: solo documentación (resultado, D050 actualizado, D051).
  Sin cambios de código, esquema, codec, cli-4, OpenAPI ni UI. Sin push,
  publicación ni ReferenceProject. Consentimiento D050 agotado.
- Siguiente: elección del usuario; se propone una instalación de operación
  reutilizable que encapsule D051. No iniciada.

## Comando único de desarrollo (D053)

- Petición del usuario: un solo comando que levante API y frontend
  actualizados, con migraciones. Respuestas: modo desarrollo y migración
  automática con backup.
- `scripts/dev` + `scripts/dev.py`, `scripts/toolchain.py` (compartido con
  `build_distribution.py`) y `storage/migrate.py` (instantánea `premigration-1`
  y `upgrade head`). El bundle H5.2 no sirve antes de migrar porque exige el
  esquema actual; se usa una copia SQLite verificada.
- Hallazgo y corrección: la abreviatura de proxy de Vite implicaba
  `changeOrigin: true` y el login de la UI de desarrollo daba 403
  `origin_rejected`. `vite.config.ts` usa ahora la forma objeto con
  `changeOrigin: false`.
- 11 casos nuevos en `tests/product/test_dev_command.py`. Ejecución real del
  comando: base `current`, API y Vite arriba, login/health/proyectos 200 por el
  proxy tras la corrección, y SIGINT con cierre limpio (exit 0, puertos libres,
  clave retirada, sin huérfanos).
- **Regresión: 857 pytest y 121 subtests, 12 checks ligeros, 6 Node, `tsc`**
  y `build_distribution.py` a un directorio temporal. Aviso Starlette/HTTPX
  conocido. Sin QA visual con navegador. Sin proveedores, red, push,
  configuración global ni ReferenceProject. Commit por bloque solicitado por el usuario.

## Decisión de agentes revisor y ejecutor (D052)

- Petición del usuario: proveedor elegible para revisor y ejecutor (Codex o
  Claude). Contradicción material con la especificación (asignación fija)
  señalada y resuelta por el usuario. Respuestas: selección del ejecutor en
  modo catálogo o libre; el revisor siempre planifica por ahora («JEV» futuro);
  la planificación determinista se mantiene como ajuste por proyecto
  (`agent` | `deterministic`).
- Inventario del acoplamiento actual: `invoke`/`argv_for`, concesiones H3.2
  solo para Claude, tablas fijas de `local-config-1`, `EnginePolicy` y textos.
  La interpretación de streams ya es por proveedor, no por rol.
- [Alcance](discovery/AGENT_ROLES_SCOPE.md) `cli-5`/`local-config-2`; sin
  código. Commit por bloque solicitado por el usuario.

## Implementación de agentes revisor y ejecutor (D052, H6.1)

- Caracterización por version/help, sin consumo:
  - Codex 0.162.1 tiene `workspace-write` y la clave
    `sandbox_workspace_write.network_access`. Sus eventos `item.*`/`file_change`
    y los esfuerzos `minimal`…`ultra` salen de las cadenas del binario.
  - La ayuda de Claude 2.1.295 y 2.1.296 es idéntica (`--json-schema`,
    `--restricted`, esfuerzos `low`…`max`), así que entra 2.1.296.
- `cli-5`:
  - Agentes `reviewer`/`executor` con cualquier proveedor.
  - argv por (proveedor, acceso): Codex escritor en `workspace-write` sin red;
    Claude lector con `Read,Glob,Grep`, `--restricted` y `--json-schema`.
  - Vocabulario de esfuerzo por proveedor.
  - Concesiones H3.2 por proveedor: Codex rechaza las de herramientas.
  - Reparto incluido en las versiones congeladas y preflight por agente y acceso.
- `EnginePolicy` gana `executor_mode` (`catalog` | `open`) y el vocabulario del
  ejecutor. Se omiten del snapshot cuando tienen su valor por defecto, así que
  los snapshots anteriores conservan su forma.
- `local-config-2`:
  - `[agents.reviewer]` con proveedor, modelo y esfuerzo fijados por el usuario;
    `[agents.executor]` con su proveedor.
  - `planning_mode` (`agent` | `deterministic`) y `executor_mode` explícitos.
  - El revisor planifica con su propia selección.
  - `local-config-1` se sigue leyendo como Codex + Claude.
- API/UI: `agents` en `ManagedProjectRead`, la línea de agentes en el listado de
  proyectos y el proveedor del revisor en el bootstrap. Textos neutros.
- 32 casos nuevos: `test_agent_roles.py` (31, con la matriz de cuatro
  combinaciones por el adaptador real) y uno en `test_permissions.py`. Pruebas
  existentes adaptadas al reparto por agente.
- **Regresión: 889 pytest y 121 subtests, 12 checks ligeros, 6 Node, `tsc`,
  build de Vite y `alembic check`**; OpenAPI y tipos regenerados. Esquema
  `0013_bootstrap`, codec 7 y locks sin cambios.
- Sin proveedores, red, QA visual, push, configuración global ni ReferenceProject.
  Commit solicitado por el usuario.

## Plan de interfaz de producto (D054)

- El usuario señaló que la UI de `scripts/dev` no permite crear proyectos ni
  muestra el chat, y que no sigue estándares de dashboard. Diagnóstico: la UI
  es una superficie funcional por hitos, nunca diseñada como producto ni
  revisada visualmente. El alta de proyectos estaba excluida a propósito
  (D028/D049) y el chat y el bootstrap solo aparecen dentro de un proyecto.
- Decisión del usuario: D052 primero; después, hito de UI (backlog H6.2) con
  alta de proyectos por registro en SQLite y confianza explícita. Sin código.

## Propuesta del smoke de la matriz D052 (D055)

- Git inicial limpio en `main`, `1eb5847`. Leídos AGENTS, STATE, NEXT_STEPS y
  DECISIONS. Se contrastaron D050–D054, la entrega D052, `local-config-2`, el
  adaptador `cli-5` y el tratamiento de las validaciones del planificador.
- Selecciones del usuario:
  - Las cuatro combinaciones.
  - Planificación por el revisor, ejecución y revisión, más commit; 3
    invocaciones por combinación y 12 en total.
  - Modelos de D050: revisor `medium`, catálogo del ejecutor `low`.
  - Un fallo aísla su combinación; las demás continúan.
- [Propuesta](discovery/PROVIDER_MATRIX_PROPOSAL.md) y
  [`examples/provider_matrix/prepare.sh`](../examples/provider_matrix/prepare.sh):
  una área por combinación con checkout desechable (regresión deliberada), TOML
  `local-config-2` 0600, estado y caché propios. Claude 2.1.296 por ruta
  versionada; modo catálogo.
- Hallazgo: el planificador puede proponer `npm run check|test|build` como
  `validation_commands`. Ese argv da `Command` con 1800 s, que no coincide con
  la variante autorizada del perfil (120 s), y su validación fallaría. El TOML
  autoriza esas tres variantes exactas y `max_timeout_seconds = 1800`.
- Ensayo offline en el scratchpad:
  - `prepare.sh` completo.
  - Wheel construido y verificado con `check_distribution.py`; venv nuevo
    instalado offline por hashes (D051).
  - `check-config` válido en las cuatro (`cli-5`, `local-config-2`, reparto y
    vocabulario correctos).
  - `--preflight` con `version_help_match` en los ocho agentes (Codex 0.162.1,
    Claude 2.1.296), sin flags ausentes. Solo versión y ayuda.
  - Admisión en proceso sin supervisor: fase `P001`, job y run `QUEUED`, sin
    intentos ni procesos, y variantes del planificador autorizadas.
  - Comandos del perfil con `env -i`: `npm ci`, check y build dan 0; test da 1
    por la regresión.
  - TOML documentado idéntico al generado (diff).
- **12 checks ligeros y 66 pytest de `test_agent_roles.py` y
  `test_local_config.py` correctos**; sintaxis del script con `sh -n`. Sin
  regresión pytest completa ni Node: solo cambian documentos y un script de
  ejemplo. Sin `serve`, consumo, login, red,
  configuración global, ReferenceProject ni harness de desarrollo. Commit solicitado
  por el usuario.
- Siguiente: ejecutar la propuesta D055 solo con consentimiento específico; no
  iniciada.

## Ejecución autorizada del smoke de la matriz (D055)

- Autorización del usuario: «Ejecútala». Git limpio en `main`, `6c1c245`.
  [Resultado](discovery/PROVIDER_MATRIX_RUN.md).
- El clasificador de permisos de Claude Code bloqueó el script que lanza los
  agentes. El usuario lanzó con `!` la corrección del script y la orquestación;
  Claude Code hizo la preparación, el wheel, el venv y el preflight, que no
  lanzan agentes.
- Preflight `version_help_match` en los ocho agentes. TOML de la combinación 4
  idéntico al de la propuesta.
- Combinación 1 (Codex→Claude):
  - Preparación correcta y planificador Codex `complete` (11,9 s, exit 0).
  - Contrato rechazado: `Invalid task validation_commands`, porque el
    planificador devolvió listas de argv.
  - Run `STOPPED` en `planner`; sin ejecutor, revisor ni commit.
- **Hallazgo.** La plantilla pide «argv commands», el esquema solo dice `array`
  y el motor exige cadenas. Afecta a toda planificación por agente; la CLI
  sintética offline devuelve `[]` y no lo detectaba.
- Incidencia del script de recorrido: trataba `ACTIVE` como terminal y mandó
  TERM al servicio al inicio. El supervisor esperó y el job terminó solo; la
  parada no se debe a la cancelación. La evidencia está completa en SQLite y
  en los artefactos.
- Decisión del usuario: parar y corregir. Combinaciones 2–4 no lanzadas. Una
  sola invocación de proveedor; consentimiento agotado.
- Sin procesos residuales, Claude no invocado y repositorio, fixture y
  configuración global intactos. Sin cambios de código: solo documentos.
- Siguiente: corrección offline del contrato de `validation_commands`; no iniciada.

## Formas de salida de los agentes (D056)

- Petición del usuario: commit del registro D055 (`519ab4e`) y empezar la
  tarea de corrección. [Entrega](discovery/CONTRACT_SHAPES.md).
- Revisión de roles:
  - Además de `validation_commands`, la review tenía el mismo hueco: `findings`
    exige objetos y ni el esquema ni la forma de ejemplo lo decían.
  - Chat y bootstrap ya mostraban cadenas en su forma de ejemplo.
- Cambios:
  - `output_schema` tipa los elementos de todas las listas; el revisor declara
    sus campos opcionales y la forma de `findings`.
  - La plantilla `plan-task` pide cadenas sin shell y `[]` si bastan las
    validaciones del perfil.
  - `task_contract` normaliza listas de argv con `shlex.join`.
  - Obligatorios, `cli-5`, esquema, codec, OpenAPI y UI sin cambios.
- 16 casos nuevos en `tests/product/test_contract_shapes.py`, entre ellos la
  regresión D055 por el adaptador real (revisor Claude, ejecutor Codex,
  `ACCEPTANCE_READY`). La mutación sin normalización hace fallar 7.
- **Regresión: 905 pytest y 121 subtests, 12 checks ligeros y 6 Node**; aviso
  Starlette/HTTPX conocido; OpenAPI sin cambios. Sin `tsc` ni build: la UI no
  cambia.
- Sin proveedores, red, push, configuración global ni ReferenceProject.
- Script de recorrido: se versionará al preparar la nueva ejecución.
- Siguiente: preparar la nueva ejecución de la matriz (área nueva y script de
  recorrido corregido); su ejecución exige consentimiento nuevo. No iniciada.

## Propuesta de nueva ejecución de la matriz (D057)

- Petición del usuario: commit de D056 (`7d00240`) y preparar la nueva
  ejecución. Se conservan las selecciones, límites y criterios de D055.
  [Propuesta](discovery/PROVIDER_MATRIX_RERUN_PROPOSAL.md).
- Scripts versionados:
  - `examples/provider_matrix/run_pairing.sh`: preflight comprobado,
    `init-db`, `serve`, recorrido y TERM.
  - `examples/provider_matrix/drive.py`: espera hasta `finished_at` o
    `RECOVERY_REQUIRED`, instantánea completa y `outcome.json`.
  - El usuario lanza con `!` las órdenes que arrancan agentes.
- Ensayo offline en el scratchpad con wheel D056 y CLI sintéticas por el
  servicio real:
  - Las cuatro combinaciones llegan a `COMMITTED`, cada una con un commit solo
    en `src/estimate.ts`.
  - Contrato `["npm run test"]` desde argv; variante de 1800 s con exit 0.
  - Argv de lector y escritor por proceso correctos.
  - Rama de fallo (`[[]]`): `STOPPED` en `planner`, sin commit, salida 1 e
    instantánea guardada.
- Sintaxis de los scripts comprobada (`sh -n`, `py_compile`). Sin regresión
  pytest: no cambia el código del producto. Sin proveedores, red, push,
  configuración global ni ReferenceProject.
- Siguiente: ejecutar D057 solo con consentimiento específico; no iniciada.

## Ejecución de la nueva matriz (D057)

- El usuario pidió «comienza la preparación» y lanzó con `!` cada combinación.
  Git limpio en `2c375bc`. [Resultado](discovery/PROVIDER_MATRIX_RERUN.md).
- Preparación: área `/private/tmp/harness-provider-matrix-2`, wheel D056
  `fec3333e…`, venv offline y preflight `version_help_match` en los ocho agentes.
- Resultados:
  - **1 Codex→Claude: `COMMITTED`** (`79853bf`). Planificador Codex con
    `validation_commands: []` y selección del catálogo; ejecutor Claude 2.1.296
    con un solo archivo; review ACCEPT.
  - **2 Codex→Codex: `REVISION_LIMIT`.** El escritor Codex (`workspace-write`
    sin red, `low`) no intentó editar: creyó que el checkout bajo `/private/tmp`
    no era escribible. Test 1 y REVISE.
  - **3 Claude→Claude: `STOPPED` en `planner`.** El lector Claude terminó
    `complete` con `--restricted` y `--json-schema`, pero serializó listas y
    objetos como cadenas JSON, porque el `--json-schema` de `cli-5` no tipa las
    propiedades.
  - **4 Claude→Codex: no lanzada** por decisión del usuario; repetiría la 3.
- Siete invocaciones; sin reintentos. Sin procesos residuales; repositorio,
  fixture y configuración global intactos. Observación: prosa en
  `forbidden_paths` del planificador Codex, sin efecto. Solo documentos.
- Siguiente: tipar el `--json-schema` del lector Claude (`cli-6`) y diagnosticar
  el escritor Codex; no iniciadas.

## `--json-schema` tipado para el lector Claude (D058, `cli-6`)

- Petición del usuario: completar la tarea activa (`cli-6`) y hacer commit.
  [Entrega](discovery/TYPED_JSON_SCHEMA.md).
- Adaptador `cli-6`: el `--json-schema` del lector Claude es el `output_schema`
  del motor congelado en la instantánea del prompt del intento, comprobado
  contra su hash; sin instantánea, el esquema fijo del rol. Resto del argv,
  escritor y Codex sin cambios; tabla `REQUIRED` eliminada.
- Decisiones: `additionalProperties: true` como en el prompt; el motor **no**
  normaliza listas u objetos serializados como texto (siguen rechazándose).
- Jobs pendientes congelados con `cli-5` entran en cuarentena al actualizar.
  Preflight, esquema `0013_bootstrap`, codec 7, OpenAPI, UI y `local-config-2`
  sin cambios funcionales (solo comentarios).
- Lectura de cadenas del binario de Claude 2.1.296, sin ejecutarlo: el esquema
  es el `input_schema` de `StructuredOutput`, con raíz objeto; admite tipos en
  lista; detecta esquemas insatisfacibles. El del motor los cumple.
- CLI sintética: como lector Claude exige propiedades tipadas; con
  `PROBE_UNTYPED=text` reproduce la salida de D057.
- Verificado: 6 pruebas nuevas (`test_typed_json_schema.py`), entre ellas la
  reproducción de D057 por el adaptador real (para en `planner` con
  `Invalid task allowed_paths`) y el recorrido Claude → Claude tipado hasta
  `ACCEPTANCE_READY`. Regresión: 911 pytest y 121 subtests, 12 checks
  ligeros, 6 Node, `tsc`, build y `alembic check`; OpenAPI y tipos generados
  sin cambios.
- No acreditado: el comportamiento de Claude real con el esquema tipado; exige
  consentimiento nuevo. Sin proveedores, red, push, configuración global ni
  ReferenceProject.
- Siguiente: diagnóstico del escritor Codex, sin consumo; no iniciado.

## Diagnóstico del escritor Codex y raíces explícitas (D059, `cli-7`)

- Petición del usuario: leer el contexto, completar solo la tarea activa sin
  lanzar sesiones y realizar commit. Git limpio al empezar.
  [Diagnóstico, evidencia y límites](discovery/CODEX_WRITER_ROOTS.md).
- Codex 0.162.1 leído por bytes/símbolos y version/help. Plantilla
  `workspace-write`: cwd y writable_roots escribibles; vías cwd, `/tmp` y
  TMPDIR presentes. `/tmp` resuelve a `/private/tmp` en este Mac.
- Evidencia D057 conservada y hashes comprobados: prompt del harness, stdout,
  stderr e intención de proceso del ejecutor. Negativa del modelo sin intentar
  herramientas, con terminal completo y stderr vacío. La interpretación del
  alcance de escritura fue incorrecta; no se observó una denegación real.
  El mensaje interno de permisos no se conservó: la relación causal con la
  descripción de raíces temporales permanece como hipótesis.
- Mitigación `cli-7` solo para Codex ejecutor: checkout canónico explícito en
  `sandbox_workspace_write.writable_roots`, `exclude_slash_tmp=true` y
  aclaración de acceso solicitado/descendientes en la entrada de transporte.
  TMPDIR explícito conserva el comportamiento predeterminado de la CLI;
  contrato/política y denegaciones reales siguen delimitando los efectos.
- Texto añadido persistido con hash en la intención, sin reescribir peticiones,
  prompts, permisos, contratos ni historiales congelados. Cuarentena de jobs
  `cli-6` antes de preflight/efectos. Lectores/Claude, esquema `0013_bootstrap`,
  codec 7, local-config, OpenAPI, UI y dependencias sin cambios.
- Verificado: 10 pruebas nuevas, también con checkouts bajo `/private/tmp`:
  TOML/rutas especiales, rechazo sintético de raíces ausentes/amplias,
  recorridos con ambos revisores y Codex ejecutor hasta `ACCEPTANCE_READY`,
  persistencia del prompt y cuarentena sin cambios del historial.
  Regresión: 921 pytest y 121 subtests, 12 checks ligeros y 6 Node correctos;
  diff revisado y `git diff --check` limpio. Sin cambios de UI/esquema: no se
  repitieron build/tsc ni regeneración OpenAPI/tipos en esta entrega.
- No acreditado: escritura por Codex real ni su mensaje interno de permisos;
  Claude real con D058 sigue pendiente. Sin sesiones/proveedores, login, red,
  configuración global, instalaciones, push ni cambios de evidencia D057.
- Siguiente tarea concreta: preparar una propuesta de nueva matriz para las
  combinaciones 2–4 con `cli-7`; no iniciada. Ejecutarla exige consentimiento nuevo.

## Preparación de la matriz 2–4 con `cli-7` (D060)

- Petición del usuario: leer el contexto, comprobar Git, completar solo la
  tarea activa, actualizar documentación y realizar commit. Git inicialmente
  limpio en `main`, `5db4da2`. Sin contradicciones materiales con D055–D059.
- [Propuesta](discovery/PROVIDER_MATRIX_CLI7_PROPOSAL.md): Codex→Codex,
  Claude→Claude y Claude→Codex, mismas selecciones/herramientas de D055/D057,
  cambios D058/D059 explícitos. Máximo nueve invocaciones, cero correcciones,
  límite operativo total propuesto de 90 minutos. Órdenes por combinación y
  revisión entre ellas; ejecución real requiere consentimiento específico nuevo.
- `prepare.sh BASE [PAR ...]` selecciona combinaciones; por defecto mantiene
  las cuatro. Preparadas solo 2–4 en `/private/tmp/harness-provider-matrix-3`:
  TOML 0600, dos commits por checkout, regresión deliberada y estado vacío.
  Sin SQLite, jobs, intentos ni servicio en el área destinada a proveedores.
- Wheel/sdist construidos offline con TypeScript/Vite correcto, verificados
  mediante `check_distribution.py` e instalados en venv propio con pins/hashes
  (D051). Verificador: assets/API, sesión, bootstrap/tarea/commit/reinicio y
  restauración de consulta con agentes falsos. Bind bloqueado en sandbox;
  comprobación completada fuera con permiso. No se modifica `dist/` del repo.
- `check-config` del wheel, sin preflight, válido en los tres TOML reales:
  `cli-7`, `local-config-2`, `commands-1`, selección y reparto esperados.
  [Manifiesto](discovery/PROVIDER_MATRIX_CLI7_PREPARATION.json) registra hashes
  de paquete, scripts, archivos TOML, versiones y evidencia sintética.
- Ensayo separado en `/private/tmp/harness-provider-matrix-cli7-offline-20261013`
  con CLI sintéticas por `run_pairing.sh`/`drive.py` y el servicio instalado:
  tres COMMITTED, tres intentos COMPLETE por par, un commit nuevo limitado a
  `src/estimate.ts`, documentos intactos, contrato normalizado `["npm run test"]`,
  cuatro validaciones exit 0 y JUnit complete. Specs/prompts/hashes comprueban
  D058/D059. SQLite reabierta: integridad/FK, jobs DONE, propietarios cerrados,
  procesos STOPPED y cero locks.
- Rama `[[]]` en área distinta: STOPPED en planner, un intento, sin otros roles
  ni commit, salida 1 y evidencia conservada. Servicios terminados con TERM,
  apagado completo, clave retirada y puerto disponible. Verificador local
  ajustado para el exit 143 de TERM y TIME_WAIT, sin repetir combinaciones.
- **82 pytest focales y 12 checks ligeros correctos**; sintaxis shell,
  rechazo de par desconocido antes de crear área y diff/whitespace/enlaces
  revisados. Sin suite pytest completa, cliente Node separado ni QA visual:
  no cambia código de producto, UI, esquema, codec, dependencias o locks.
- Áreas D055/D057 conservadas; capturas D057 del escritor Codex coinciden con
  hashes documentados. Sin proveedores, version/help reales, login, red externa,
  configuración global, ReferenceProject, subagentes, push ni harness de desarrollo.
- No acreditado: edición real de Codex, mensaje interno de permisos ni Claude
  real con esquema tipado. Siguiente tarea: ejecutar D060 una sola vez solo con
  consentimiento nuevo; **no iniciada**. H6.2 tampoco. Commit solicitado.

## Ejecución acotada de D060 y parada global (D061)

- Autorización del usuario: «Autorizo», tras revisión de propuesta, selecciones
  y límites. Git inicialmente limpio en `main`, `42971ef`.
  [Resultado](discovery/PROVIDER_MATRIX_CLI7_RUN.md),
  [manifiesto y verificaciones](discovery/PROVIDER_MATRIX_CLI7_RESULT.json).
- Hashes de paquete/scripts/tres TOML coincidentes con D060; wheel y venv
  conservados, sin reconstrucción o instalación. Estado de los tres pares
  inicialmente vacío y Git limpio. Preflight de ambos agentes de la 2
  `version_help_match` con Codex 0.162.1; Claude no invocado, ni version/help.
- **2 Codex→Codex COMMITTED**, run `58119c8c-314f-49dd-b1b4-9256cd680d46`,
  commit `585a35c009a4e68d9d90eb4f9af981afffd9e8f2`. Planner/executor/reviewer
  COMPLETE, exit 0, stderr vacío; `gpt-6-luna` medium/low/medium solicitado.
  Escritura real observada como `file_change` y diff solo de `src/estimate.ts`;
  raíces D059 y prompt de transporte verificados. No prueba la causa de D057.
- Seis comandos de preparación/validación exit 0; check/test/build correctos,
  JUnit original completo y tres casos aprobados. Review ACCEPT y aceptación
  elegible ligadas a la misma huella/árbol del commit. Documentos intactos,
  único commit nuevo acotado y checkout limpio. Hashes de artefactos/prompts,
  snapshots y versiones contrastados; originales conservados bajo BASE.
- **Parada preventiva:** cambia el hash de `~/.codex/config.toml`; mtime
  coincide con el lanzamiento del escritor y se observa `trust_level = "trusted"`
  para su checkout. La línea base solo registra hashes: delta exacto y
  atribución a la CLI no demostrados. No se editó directamente ni restauró
  configuración global; el cambio observado se conserva.
  Los otros tres archivos muestreados mantienen hashes y no hay entradas
  nuevas de proyectos Claude; no es auditoría exhaustiva del filesystem.
- **3/4 no lanzadas**, sin SQLite/jobs/intentos/evidencia; state/cli-tmp
  vacíos y HEAD/documentos conservados. Tres invocaciones Codex, cero Claude,
  sin reintentos, fallback, login, recuperación o liberación manual de locks.
  No se agotó el plazo de 90 minutos. Consentimiento D060 agotado.
- SQLite reabierta: integridad/FK correctas, ambos jobs DONE con propietarios
  cerrados, procesos STOPPED, cero locks. Identidades de CLI/comandos/servicio
  observadas muertas, apagado completo, clave retirada y puerto sin listener.
- Verificación proporcional: recorrido real, hashes, contenido exacto,
  cierres y documentación/diff/enlaces. Sin nuevos tests de producto,
  pytest, build del producto, cliente Node separado o QA visual: no cambia
  código/UI/esquema/codec/dependencias. Las validaciones del checkout
  desechable sí se ejecutaron. Sin push, publicación, ReferenceProject, subagentes
  de desarrollo o harness de desarrollo. Commit solicitado por el usuario.
- Siguiente: diagnóstico offline del cambio global; no iniciado. Claude real
  con D058 sigue pendiente y cualquier ejecución posterior requiere nueva
  propuesta/consentimiento. H6.2 tampoco se inició.

## Diagnóstico offline del cambio global (D062)

- Petición del usuario: «continúa», aplicada solo a la tarea activa de
  diagnóstico offline. Git inicialmente limpio en `main`, `f930dc5`.
  [Diagnóstico y opciones](discovery/CODEX_GLOBAL_CONFIG_DIAGNOSIS.md),
  [manifiesto de lectura/verificaciones](discovery/CODEX_GLOBAL_CONFIG_DIAGNOSIS.json).
- Delta exacto D061 acreditado sin copia previa: quitar en memoria la sección
  observada de 93 bytes reproduce el SHA-256 previo. La entrada de confianza
  del checkout de la 2 fue añadida, sin otros cambios de bytes entre los
  hashes registrados. No se guardó la inversa ni contenido global completo;
  no se restauró configuración o evidencia.
- Codex nativo 0.162.1 idéntico a D059 leído por bytes/símbolos/desensamblado:
  ruta interna de App Server llama a `set_project_trust_level`, que une
  `config.toml` y aplica cambios al archivo. Los flags de omisión de carga,
  reglas y archivos de sesión no prometen impedir persistencia de confianza.
  Specs D061 sin CODEX_HOME y con HOME real; D024 conservado.
- mtime antes del registro de thread.started y del primer comando visible;
  efecto de arranque de la CLI muy probable. Sin auditoría de syscalls, la
  atribución al proceso original sigue inferida, no certificada. El cambio
  no aparece entre las herramientas visibles del modelo.
- **Corrección no implementada:** un override de trust no prueba supresión
  de persistencia; un CODEX_HOME privado desplaza auth también. No se copian
  credenciales ni cambian HOME/almacén/versiones para fingir aislamiento.
  Límite registrado antes de cambiar diseño; `cli-7` y congelados intactos.
- Cinco casos sintéticos de prueba de delta, desensamblados acotados y hashes
  correctos. Manifiesto/línea base D061, 14 snapshots y prompts conservados;
  SQLite solo lectura. Configuración global sin cambios durante el diagnóstico.
  Documentación/JSON/enlaces y diff verificados. Sin pytest/build/Node/QA
  visual nuevos: no cambia código/UI/esquema/codec/dependencias/locks.
- Cero procesos CLI reales/invocaciones; sin preflight, login, auth status,
  red, instalaciones, subagentes, harness de desarrollo o push. Consentimientos
  agotados conservados. Commit solicitado en el flujo de esta sesión.
- Siguiente: concretar propuesta de contención del proceso Codex compatible
  con autenticación existente, con alcance/criterios antes de implementar;
  no iniciada. Matriz pendiente y H6.2 tampoco se inician.

## Propuesta de contención del proceso Codex (D063)

- Petición del usuario: completar solo la tarea activa y realizar commit.
  Git inicialmente limpio en `main`, `9db047a`. [Propuesta y aceptación](discovery/CODEX_PROCESS_CONTAINMENT_PROPOSAL.md),
  [manifiesto](discovery/CODEX_PROCESS_CONTAINMENT_EVIDENCE.json) y
  [sonda independiente](discovery/CODEX_PROCESS_CONTAINMENT_PROBE.py).
- Comparadas contención externa y separación de estado/auth para 0.162.1.
  Candidata para calificación: frontera de escritura macOS conservando HOME,
  USER y auth en origen, sin duplicar secretos. CODEX_HOME privado no acredita
  conservar sesión; símbolos de almacenes no prueban selección ni precedencia.
- Hash del nativo coincide con D062, lectura estática sin invocarlo. No se
  abrió configuración global, auth real ni llavero. Se documenta el límite:
  bloquear save local no impide refresh remoto ni garantiza sesión funcional.
- Experimento con HOME/token ficticios: sandbox anidado de desarrollo impide
  aplicar el perfil (exit 71); ensayo nuevo fuera autorizado, exit 23 esperado.
  Lectura auth correcta, ocho escrituras denegadas, checkout/temporal permitidos
  e hijo contenido; originales ficticios conservan hash/modo/mtime.
  La salida terminal es del fake, no un comportamiento acreditado de Codex.
- Propuesta fija efectos, límites, portabilidad, criterios offline siguientes,
  impacto futuro en versiones/cuarentena y puerta de consentimiento real.
  IPC, sandbox interno, auxiliares y refresh quedan pendientes explícitos.
  Sin transporte implementado, ni nueva versión aplicada; cli-7, local-config-2,
  esquema, codec, permisos D024/D059, contratos e historiales conservados.
- Sonda OS, JSON, sintaxis Python, enlaces y diff comprobados; sin pytest/build/
  Node/QA visual nuevos porque no cambia producto/UI. Cero CLI de proveedores,
  preflight real, login/refresh, red externa, instalaciones, subagentes,
  harness de desarrollo, cambios globales, ReferenceProject o push.
- Siguiente tarea separada: calificación offline del contenedor macOS con la
  matriz sintética de D063; no iniciada. Matriz real y H6.2 tampoco iniciadas;
  consentimientos D050/D055/D057/D060 agotados. Commit solicitado.

## Calificación offline de la contención candidata (D064)

- Petición del usuario: completar solo la tarea activa y realizar commit.
  Git inicialmente limpio en `main`, `aaccad0`. [Dictamen y matriz](discovery/CODEX_CONTAINMENT_QUALIFICATION.md),
  [evidencia](discovery/CODEX_CONTAINMENT_QUALIFICATION.json) y
  [sonda reproducible independiente](discovery/CODEX_CONTAINMENT_QUALIFICATION.py).
- **Candidata no calificada para integrar tal como está.** Perfiles lector y
  escritor contienen las escrituras directas ensayadas, incluidos auxiliares
  de HOME, estado/artefactos, symlinks y creación de hardlinks. TMPDIR permite
  rename, locks y SQLite WAL; checkout solo permite al escritor.
- Escapes observados sobre fixtures sacrificiales: fd abierto heredado,
  hardlink preexistente y petición por pipe a helper externo. Control cerrando
  fd devuelve EBADF. Socket Unix propio denegado; no acredita IPC general.
  Admisión canónica rechaza 17 casos, sin garantía contra carreras externas.
- Sandbox anidado escritor funciona en la matriz sintética; lector rechazado
  con exit 71 antes del objetivo interno. No se equipara al perfil real Codex.
  Auth ausente/ilegible/refresh ficticio termina explícitamente sin fallback;
  hash/modo/mtime de auth/config ficticios conservados, incluso tras cancelación.
- Gate existente sobre procesos falsos: identidad fsync antes de GO; EOF,
  byte inválido, fallo de identidad o cancelación previa sin objetivo.
  Timeout/cancelación/KILL y ausencia de los ocho grupos propios comprobados.
  Sin SQLite operativa, recuperación ni nueva autoridad de producto.
- Primer ensayo bloqueado por sandbox de desarrollo (sin fallback). Ensayo
  exterior autorizado: 24 casos; matriz final ampliada: **27 casos completos**.
  **14 pytest focales correctos**, 39 deseleccionados. Sintaxis Python, JSON,
  hashes, enlaces y diff/whitespace revisados. Sin suite completa/build/Node/QA
  visual porque producto/UI/contratos/dependencias no cambian.
- Sin CLI reales (ni version/help), red externa, login, secretos reales,
  configuración global, subagentes, harness de desarrollo, ReferenceProject o push.
  cli-7/local-config-2, D024/D059 y congelados intactos. Auth/refresh remoto,
  auxiliares de CLI, servicios Mach/XPC y otras plataformas no certificados.
- Siguiente: diagnóstico offline del rechazo del sandbox lector y propuesta
  de frontera revisada antes de integrar; **no iniciado**. Matriz y H6.2 tampoco;
  consentimientos D050/D055/D057/D060 siguen agotados. Commit solicitado.

## Diagnóstico del anidamiento y frontera revisada (D065)

- Petición del usuario: completar solo la tarea activa de NEXT_STEPS y hacer
  commit. Git inicialmente limpio, `b73d9d4`.
  [Dictamen y criterios revisados](discovery/CODEX_CONTAINMENT_REVISION.md),
  [evidencia](discovery/CODEX_CONTAINMENT_REVISION.json) y
  [sonda independiente reproducible](discovery/CODEX_CONTAINMENT_REVISION.py).
- **Incompatibilidad de la candidata para integrar con la evidencia actual.**
  Lector→lector y escritor→escritor sintéticos funcionan manteniendo ambas
  capas, lectura auth ficticia y prohibición global de escritura. Los pares
  ensayados con restricciones distintas salen 71 al aplicar la segunda capa.
  Se descartan cwd, archivo/inline y arranque Python en los controles mínimos.
  Comentarios, reordenación y deny redundante sí componen; representación
  compilada equivalente es hipótesis, sin inspección del kernel/perfil real.
- Fd y pipe heredados modifican sacrificiales exteriores; cierre sin pass_fds
  devuelve EBADF y corta ambas vías. Captura stdout inerte no delega escritura.
  Hardlink añadido después de admisión/readiness permite escribir el exterior:
  un precheck o lock cooperativo no es una frontera contra carreras.
- Criterios revisados concretos para capas exactas, fd, exclusión de aliases
  durante la ejecución, receptores IPC sin autoridad exterior, auth y refresh.
  Sin mecanismo calificado para carreras/IPC general ni compatibilidad de CLI
  real. No se eliminan capas, amplían raíces o cambian almacenes para aprobar.
- **32 escenarios finales completos**, 22 anidados y doce rechazos esperados.
  Auth/config ficticios conservan bytes/modo/mtime; solo tres sacrificiales
  explícitos cambian. Ensayo inicial rechazado por sandbox de desarrollo;
  ejecuciones exteriores autorizadas por la herramienta. Ensayo exploratorio
  con expectativa incorrecta de deny redundante conservado como tal.
- **14 pytest focales passed**, 39 deseleccionados. Sintaxis Python, hashes/JSON,
  enlaces y diff comprobados. Sin suite completa/build/Node/QA visual, producto
  sin cambios. Sin proveedores, CLI real/version/help, red externa, login,
  credenciales reales, ajustes globales, harness de desarrollo, subagentes o push.
- cli-7, local-config-2, núcleo, TOML operativo, jobs, modelos/permisos y
  congelados intactos. Auth efectiva, auxiliares, refresh remoto y servicios
  Mach/XPC/llavero no certificados. Ninguna integración implementada.
- Siguiente alcance **pendiente de elección con el usuario**, sin iniciar:
  capacidad soportada de separación estado/auth o frontera distinta, suspender
  integración, o decidir explícitamente cambios materiales de aislamiento/auth/
  efectos. No se adopta una relajación ni se autoriza consumo. Matriz 3/4 y H6.2
  sin iniciar; D050/D055/D057/D060 agotados. Commit solicitado para esta entrega.

## Persistencia de proyecto y memoria automática (D066)

- Petición del usuario: contexto duradero en Markdown bajo `docs/`, historial
  por fase y STATE/NEXT_STEPS frescos; continuar con la persistencia de las CLI.
  Git inicialmente limpio en `7cd3503`. [Entrega y límites](discovery/AGENT_PERSISTENCE.md),
  [inventario estático](discovery/AGENT_PERSISTENCE_INVENTORY.py) y
  [evidencia](discovery/AGENT_PERSISTENCE.json).
- `cli-8`: todos los roles Codex solicitan features.memories=false,
  memories.generate_memories=false, memories.use_memories=false e historial
  none, conservando ephemeral. Claude recibe autoMemoryEnabled=false además
  de no-session-persistence; CLIConfig rechaza override ambiental conflictivo.
  Configuración personal, HOME/USER y autenticación no se intervienen.
- Comparación existente bloquea jobs `cli-7` antes de preflight/efectos sin
  reescribir solicitudes/resultados/versiones. No se integra la candidata
  D063–D065; cli-8 identifica memoria, no contención. local-config-2 (lectura
  local-config-1), esquema/codec/API/UI/dependencias/modelos/permisos conservados.
- Fuente oficial contrastada con lectura estática/hash de Codex 0.162.1 y
  Claude 2.1.295/2.1.296. Consulta documental web; sin red de proveedor ni
  inferencia. Codex 0.161.0 solo probado sintéticamente para estos controles.
  No se leen auth/config/settings/llavero ni memoria reales o ejecutan CLI reales.
- **20 tests nuevos, 215 pertinentes passed**, con cuatro combinaciones
  sintéticas que exigen controles de memoria. 941 tests recolectados; no suite
  completa/build/QA visual. Primer pase: dos denegaciones de /bin/ps por sandbox
  y una fixture nueva ausente. Fixture corregida; repetición exterior autorizada
  pasa sin ocultar el límite de entorno. JSON/hashes/sintaxis/enlaces/diff verificados.
- Control de memoria implementado; **prohibición completa de persistencia
  externa sin certificar**. Confianza Codex D061/D062, archivos auxiliares,
  carga implícita de instrucciones, fuente auth y refresh siguen pendientes.
  No se aplica un override de confianza sin prueba ni se redirige el almacén.
  Temporales originales D062/matriz no disponibles; informes versionados
  conservados, sin reconstrucción de observaciones.
- Próximo: preparar diagnóstico del arranque Codex sin inferencia, con HOME/
  auth ficticios y red denegada, sin ejecutarlo; fijar exclusión de lectura de
  secretos/globales, argv/aislamiento/límites y criterios antes de pedir una
  autorización específica. No se prepara aquí otra matriz ni se implementa
  archivado documental. D050/D055/D057/D060 agotados; H6.2 sin iniciar.

## Preparación del diagnóstico de arranque Codex (D067)

- Petición del usuario: seguir con el siguiente paso de NEXT_STEPS. Git
  inicialmente limpio, `e2f272c`. [Propuesta y dictamen](discovery/CODEX_STARTUP_PREPARATION.md),
  [controlador sintético](discovery/CODEX_STARTUP_PREPARATION.py) y
  [manifiesto/evidencia](discovery/CODEX_STARTUP_PREPARATION.json).
- **Preparación completada con incompatibilidad; no apta para ejecutar CLI real.**
  Candidata deny default, lecturas públicas/ficticias acotadas, escrituras solo
  en raíces ficticias y sin permisos de red/Mach: el Python mínimo termina
  con SIGABRT antes del marcador, capturas vacías. Causa interna no acreditada;
  no se atribuye a Codex/auth o una operación concreta ni se amplían permisos.
- Borrador con nativo/hash D059/D062, dos variantes de argv (sin override y
  confianza solo en transporte), memoria cli-8, writer gpt-6-luna/low conservado,
  HOME/CODEX_HOME/auth ficticios, metadatos Git nuevos, dos procesos/10 s/16 KiB
  por stream si alguna candidata posterior fuese calificada y autorizada.
  Comandos solo proyectados; no existe modo que ejecute una CLI de proveedor.
- Diez ensayos independientes de controlador usan Python fake fijo sin
  contención OS acreditada; se etiquetan aparte. No relanzan el objetivo
  filesystem rechazado sin sandbox. Distinguen persistencia, override ficticio
  que no la evita, auth anterior al marcador, texto de marcador no válido,
  fd cerrado, señal/timeout/exceso y launcher ausente. Perfil inválido OS distinto.
- **12 casos finales completos** (diez controlador, dos OS), once grupos
  observados ausentes y auth/canarios protegidos con bytes/modo/mtime conservados.
  Config ficticia cambia en dos escenarios sacrificiales. Capturas incompletas
  en timeout/exceso se marcan; no se acredita no persistencia por un auth error.
- Primer ensayo dentro del sandbox de desarrollo falla al aplicar perfil,
  exit 71; ensayos exteriores sintéticos autorizados por herramienta. Perfil
  inválido exit 65 y SIGABRT posterior se distinguen. Versiones preliminares
  conservadas con hashes, sin atribuirles el código final.
- **14 pytest pertinentes passed**, 39 deseleccionados; sintaxis, TOML/JSON,
  hashes, originales/capturas/perfiles, enlaces y diff verificados. Sin suite
  completa/build/QA visual; producto y dependencias no cambian. Cero CLI real,
  version/help, proveedor/modelo, auth real, red externa, subagentes o push.
- No se solicita ejecutar la candidata. Frontera de lectura/globales, sandbox
  interno, auth/refresh y persistencia Codex real sin calificar. cli-8/local-
  config-2, núcleo, jobs/locks, baseline/permisos/modelos e historiales intactos.
- Siguiente tarea separada: verificar la condición de persistencia de confianza
  en fuente del pin, si está disponible, y supresión por transporte sin efectos
  globales; registrar límites antes de implementar. No iniciada aquí. Fase de
  comprobaciones abierta; matrices 3/4, archivado documental y H6.2 sin iniciar.
  D050/D055/D057/D060 siguen agotados.

## Cierre de la comprobación funcional de flujos de modelos (D068–D071)

- Petición del usuario: comprobar el flujo hasta cerrarlo y continuar después
  con el resto. Git inicialmente limpio en main, `1d2de43`; commit solicitado
  dentro del flujo de esta sesión. [Fuente/cli-9](discovery/CODEX_TRUST_SUPPRESSION.md),
  [ensayos detenidos](discovery/PROVIDER_MATRIX_CLI9_STOPS.md),
  [cuatro resultados reales](discovery/PROVIDER_MATRIX_CLI9_RUN.md) y
  [manifiesto final](discovery/PROVIDER_MATRIX_CLI9_RESULT.json).
- Fuente pública rust-v0.162.1 → commit 092d3acd, presente en nativo/hash D062.
  Arranque persiste confianza solo con cwd explícito/trust ausente/proyecto/
  permisos de escritura. cli-9 pasa projects={<cwd>={trust_level="untrusted"}}
  al escritor: evita esa ruta y config/hooks locales implícitas; mantiene
  workspace-write/raíces/network false/approval never, HOME/USER/auth. Clave
  completa inline por el parser dotted del pin. Jobs cli-8 anteriores quedan
  en cuarentena antes de preflight sin reescribir congelados.
- D069: tres COMPLETE Codex, edición/tests correctos pero planner permite
  src/estimate.ts y prohíbe **. Revisor BLOCKED, sin commit. Se corrige prompt/
  esquema y contrato para rechazar contradicciones acreditables antes del
  escritor, sin borrar prohibiciones y conservando exclusiones parciales.
  D070: una invocación planner, timeouts y eventos error de reconexión; aunque
  después haya plan válido/terminal exit 0, CLI failed/STOPPED. Parser conservado.
  Ambos ensayos cierran owners/servicio/procesos, cero locks y muestras intactas.
- Usuario autoriza una matriz nueva: «Autorizar una nueva matriz», máximo
  doce invocaciones/parada al primer fallo. D071 en matrix-6 con paquete
  corregido instalado desde wheel fuera de este checkout, sin red de instalación.
  Mismo modelo/esfuerzo y permisos; doce invocaciones COMPLETE, sin retry/fallback.
  **Codex→Codex, Claude→Claude, Claude→Codex y Codex→Claude COMMITTED.**
- Claude real devuelve listas/objetos tipados con D058; Codex escribe realmente
  en ambos pares (file_change o comando Python acreditado). Solo src/estimate.ts
  cambia; 24 comandos de preparación/validación, cuatro JUnit con tres casos,
  ACCEPT y aceptación/commit del contenido exacto. El ejecutor no hace commit;
  acepta el revisor y el harness realiza el commit mecánico. Docs intactos.
- Commits de ensayo 75bef356, 293643f2, 347f4a7d, 584ed7e0; ocho jobs DONE/owners
  cerrados, doce procesos y sus grupos ausentes, comandos muertos, cero locks,
  servicios detenidos con TERM, claves retiradas y puerto libre. Sin recuperación
  manual, tag/cierre de fases de ensayo, push o publicación.
- Controles de auto memory presentes en todos los roles; muestras de archivos
  de memoria y config/settings/gitconfig mantienen hashes. Confianza específica
  resuelta con escritura real; no se afirma aislamiento físico, ausencia de
  auxiliares/SQLite/logs/cachés de CLI, refresh/cuota/retries internos o que todo
  contexto venga exclusivamente de Markdown. No se cambia configuración global,
  auth/almacén/baseline o integra D063/D067. ReferenceProject no se toca.
- **948 pytest + 121 subtests correctos** (319,43 s), 12 checks estándar,
  217 de transporte y 155 de contratos/motor/permisos/prompts. Siete casos nuevos,
  dos builds offline y verificaciones de wheel aislado. Asunción inicial del
  verificador file_change ampliada al comando de edición acreditado, sin
  repetir run; aserción vieja de esquema actualizada y suite completa repetida.
  Hashes/SQL/FK/prompts/streams/JUnit/Git/diff revisados. Sin nueva QA visual;
  UI/API/esquema/codec/dependencias no cambian.
- **Comprobación funcional de modelos cerrada.** Consentimiento D071 satisfecho
  y agotado; D069/D070 y anteriores también agotados. Organización/historial
  por fase y continuidad documental real siguen separados y pendientes. Próxima
  tarea propuesta en NEXT_STEPS: concretar ese contrato documental; no iniciada.
  H6.2 tampoco se inicia. No se afirma que un diseño pendiente esté implementado.

## Organización documental por fase y estructura de producto (D072)

- Tarea de diseño solicitada por el usuario el 2026-10-14. Nada implementado.
  [Diseño completo](discovery/DOCUMENT_ORGANIZATION.md). Requisitos fijados por el
  usuario: creación desde un brief con conversación del revisor; SPECIFICATION,
  ARCHITECTURE, ROADMAP, STATE y NEXT_STEPS; `archive/phase-NNN/`; README para
  personas; edición desde el editor y desde el sistema; URLs por proyecto, fase y
  tarea; chat global; métricas por tarea; tests OK/KO; estadísticas.
- Revisado lo implementado: bloques D036, bootstrap v1 D037, `PhaseCreate`
  D032, reconciliación D034, chat D035, parser determinista de NEXT_STEPS,
  `MechanicalUpdate` H2.4, captura terminal de `usage`/`modelUsage` sin
  `num_turns` y lector legacy con `docs/archive`. ReferenceProject leído sin
  modificarlo, sin sus runs.
- Contrato propuesto:
  - `decisions/` un archivo por decisión; `architecture/` y `research/`
    opcionales; ninguna carpeta por tarea.
  - Archivo de fase con STATE, NEXT_STEPS, REVIEW y SUMMARY; `phase-000` con
    BRIEF y DEFINITION.
  - STATE dividido en base acumulada y fase activa, con presupuestos.
  - Bloques v2 regenerados en cada commit de tarea.
  - `phase_transition` después del cierre D032.
  - Ediciones humanas por `document_edit` con CAS.
  - Creación v2 con borradores en disco.
  - Comandos de chat deterministas.
  - `attempt_metrics` materializada.
- Diferencias frente a D032, D035, D036, D037 y D054 explícitas en el diseño.
  Incrementos propuestos: H6.3, H6.4, H6.5 y H6.2 ampliada, con criterios
  sintéticos. Siete puntos a confirmar en NEXT_STEPS. Sin cambios de código,
  esquema, API, UI ni dependencias, sin proveedores; no se ejecutaron tests
  porque no cambió el código.

## Implementación de H6.3: contrato documental y transición (D073)

- El usuario confirma los siete puntos de D072 (carpetas `decisions/`,
  `architecture/` y `research/` creadas desde el principio; la UI, tarea aparte)
  y pide empezar el desarrollo. Git inicial en `main`, `0e18ad1`, con la
  documentación de D072 sin commit. [Entrega](discovery/H6.3_DOCUMENT_CONTRACT.md).
- Opt-in por proyecto (`ProjectContext.documents` / TOML `documents = "v2"`);
  snapshots, contratos y comportamiento anteriores intactos sin la clave.
- `core/engine/documents.py`: layout v2, bloques con nombre, render legible con
  escape en línea, parsers de ROADMAP/decisiones/base acumulada, presupuestos,
  REVIEW/SUMMARY y plantilla base. Alias en español en el parser de NEXT_STEPS.
- Contratos v2: el archivo siempre prohibido y los documentos del harness salvo
  en la reconciliación, que compacta STATE y puede editar producto y carpetas.
  Una tarea v2 no arranca con cambios locales sin confirmar.
- Commit de tarea: bloques de STATE/NEXT_STEPS/ROADMAP/DECISIONS regenerados
  como actualizaciones mecánicas; adopción de sus hashes en la transacción de
  COMMITTED, leyendo el hash anterior en la revisión base.
- `phase_transition` (después de CLOSED/ABANDONED) y `document_edit` (contenido
  o cambios del editor) como operaciones de fase con intención conciliable, sin
  migración ni codec nuevos. Exportación D036 en v2 con el mismo render.
- API: estado y lectura de documentos, edición y transición con vista previa y
  envío; OpenAPI y tipos regenerados. Sin cambios de UI.
- Verificación: 37 casos nuevos en `tests/product/test_documents.py` (Git/SQLite
  temporales, agentes falsos). Suite completa **985 pytest + 121 subtests**
  (383,73 s); 12 checks estándar; 6 pruebas Node; `tsc` y build de la UI;
  `alembic check` sin cambios en SQLite temporal. Una aserción exacta de
  `ManagedProjectRead` se actualizó por el campo aditivo `documents`.
- Hallazgos corregidos durante la entrega: el mensaje de commit de la exportación
  v2 leía la forma v1 del snapshot, y la edición desde el editor de un archivo de
  decisiones rechazaba el índice regenerado. Ambos con prueba de regresión.
- Límites: bootstrap D037 sigue con la plantilla v1 (creación v2 en H6.5); sin
  `handoff_notes`; métricas de tokens/turnos pendientes (H6.4); avisos de tamaño
  fuera del check; exclusión frente a escritores externos cooperativa; ningún
  recorrido con CLI real. Sin push ni proveedores. Commiteado por separado (`cea745a`) al empezar
  H6.4, tras repetir la suite completa sobre ese árbol (985 pytest + 121 subtests).

## Implementación de H6.4: métricas por intento y estadísticas (D074)

- Tarea activa de NEXT_STEPS, pedida por el usuario el 2026-10-14. Git inicial en `main`, `0e18ad1`, con
  H6.3 sin commit: se verificó y commiteó aparte (`cea745a`) antes de empezar.
  [Entrega, catálogo y límites](discovery/H6.4_METRICS.md).
- Caracterización offline de los doce stdout de D071 (sin modificarlos, 12/12 verificados por SHA-256)
  con un script de biblioteca estándar independiente de la implementación; solo nombres, tipos y
  comprobaciones ([script](discovery/H6.4_STREAM_CATALOG.py), [salida](discovery/H6.4_STREAM_CATALOG.json)).
  Claude: total del `result` = suma de `message_delta`; eventos `assistant` repetidos y con salida
  parcial. Codex: un `turn.completed`, caché leída ⊆ entrada, sin modelo/esfuerzo/coste/duración/turnos.
  `rate_limit_event` y los tokens estimados quedan fuera: no se deduce cuota.
- `core/engine/metrics.py`: catálogo `metrics-1`, acumulador de stream y fila por intento con procedencia
  `requested`/`reported`/`derived`/`measured`/`absent`. `AgentStream` captura `terminal-2` (turnos,
  duración de API, contadores derivados) sin cambiar argv ni la versión `cli-9`.
- Migración `0014_attempt_metrics` (`attempt_metrics`, `attempt_model_metrics`). La fila se inserta en la
  transacción del resultado (`_history`) o de la interrupción (`confirm_stopped`); si falla, el resultado
  tampoco se registra. Sobrevive a la retención H5.3; el backup la verifica con el esquema.
- Relleno `harness-local metrics-backfill --database RUTA [--artifact-root RAÍZ]`: idempotente, desde
  `result_json` y, bajo raíces autorizadas, stdout sellado verificado por hash y sin purga. Probado además
  sobre copias migradas de las cuatro SQLite de D071: 12 filas, 12 streams verificados.
- API de solo lectura `/api/managed/metrics/{summary,attempts,groups,models,tasks}`: consumo por rol,
  proveedor, modelo, esfuerzo, día, fase y tarea; favoritos; aceptación a la primera, correcciones,
  tiempos, tests OK/KO y paradas por motivo; global o por proyecto. OpenAPI y tipos regenerados.
- SUMMARY de las fases que se archiven: tokens y turnos por tarea y consumo por rol con cobertura, sin chat.
  Una transición revisada antes de migrar se ejecuta tal como se revisó.
- Verificación: 26 casos nuevos en `tests/product/test_metrics.py` (probe sintético con la forma de D071,
  valores inventados). Suite completa **1011 pytest + 121 subtests** (390,11 s); 12 checks estándar;
  6 pruebas Node; `tsc` y build de la UI; `alembic upgrade`/`check`/`current` en SQLite temporal
  (`0014_attempt_metrics`); `legacy-import` y `metrics-backfill` por CLI. Tres hallazgos corregidos durante
  la entrega: los agregados sumaban la entrada cruda con semánticas distintas por proveedor; la tabla de
  consumo del SUMMARY no mostraba la cobertura de cada suma; y una transición revisada antes de migrar
  habría acabado en recuperación. Los tres con prueba.
- Límites: semánticas de Codex coherentes con 6 muestras, no certificadas; turnos de Codex derivados; sin UI,
  sin relleno automático y sin métricas en los bloques de STATE/NEXT_STEPS; ningún recorrido con CLI real.

## Implementación de H6.5: creación y planificación conversacionales (D075)

- Tarea activa de NEXT_STEPS, pedida por el usuario el 2026-10-14. Git inicial limpio en `main`, `1e5d114`.
  [Entrega, API y límites](discovery/H6.5_CONVERSATIONAL_CREATION.md).
- `core/engine/definition.py`: brief (≤ 256 KiB), rutas de borrador admitidas, esquemas fijos de los turnos
  `definition` y `phase_planning`, ejecución del turno con observación antes/después y vista previa
  determinista de la aceptación (bloqueos o archivos íntegros, bloques regenerados, README de carpeta,
  `archive/phase-000/{BRIEF,DEFINITION}.md`, P001 y primera tarea según el modo de planificación).
- Migración `0015_planning` (`planning_conversations`, `planning_turns`, `planning_proposals`); runs
  `definition`/`phase_planning`, acción `planning_turn`. Roles aditivos `definition`/`planning` en `cli-9` y
  plantillas `define-project`/`plan-phase` (catálogo de 9 a 11, `ADDED_LATER`). SUMMARY de fase sin estas
  conversaciones.
- `adapters/bootstrap.py`: inspección de borradores (ajenos, inválidos, `.git`), escritura con CAS (temporal
  propio + `os.replace`) y bootstrap D037 generalizado solo para documentos con `before_sha256`.
  `storage/bootstrap.py` despacha la vista previa v2 y adopta solo los documentos de fase.
- `storage/planning.py`: conversaciones, turnos congelados, propuestas con sustitución, aplicar/editar con
  CAS, aplazar preguntas, descartar; hashes conocidos solo tras un turno respondido. La transición acepta
  `plan_proposal` (con `plan_origin` en el hash solo cuando existe) y la marca ACCEPTED al encolarla.
- API `/api/managed/projects/{id}/planning/...` (10 rutas), `plan_proposal` en la transición,
  `definition_operation` en `GET …/bootstrap` (sin cambiar el tipo que usa la UI v1). OpenAPI y tipos
  regenerados; la UI no cambia.
- Verificación: 44 casos nuevos en `tests/product/test_definition.py` (carpeta vacía → commit raíz con
  conversación sintética y ediciones en disco y por API; agente que escribe; ocho salidas inválidas; ediciones
  concurrentes; siete archivos ajenos y `.git`; once bloqueos; modo determinista; aplazamiento; caídas del
  bootstrap y del turno; v1/v2; migración; planificación → transición; HTTP). `test_prompts` actualizado al
  catálogo de 11 (+2 casos parametrizados). Suite completa **1056 pytest + 121 subtests** (404 s) antes de
  añadir el caso de borrador ejecutable, que pasa con los 44; total recogido 1057. 12 checks estándar;
  6 pruebas Node; `tsc` y build de la UI; `alembic upgrade`/`check`/`current` (`0015_planning`) y bajada/subida
  a `0014` en SQLite temporal.
- Hallazgos corregidos durante la entrega, con prueba: un turno fallido ocultaba al siguiente las ediciones
  del usuario; un borrador ejecutable solo fallaba después de confirmar; aceptar con un turno pendiente daba
  un motivo engañoso; «proyecto ya creado» quedaba tapado por la petición de importación.
- Límites: sin UI ni CLI real; el TOML local no expone `bootstrap_enabled`; exclusión frente al editor
  cooperativa; 2 MiB de borradores por turno; `research/` solo con README durante la definición; el chat
  sigue esperando el lock (D073 punto 5). Sin push ni proveedores.

## Alcance de H6.2: UI de producto (D076)

- Tarea activa de NEXT_STEPS, pedida por el usuario el 2026-10-14. Git inicial limpio en `main`, `7b2c2eb`.
  [Alcance, entregas y criterios](discovery/H6.2_SCOPE.md).
- Decisiones del usuario: registro de proyectos híbrido (el TOML `local-config-3` es la autoridad de lo que
  ejecuta, con composiciones con nombre; SQLite guarda los proyectos registrados desde la UI, versionados y
  auditados, sin conceder ejecutables por HTTP); `markdown-it` sin HTML y Mermaid estricto con carga
  diferida; chat global en H6.2 con backend de turnos sin lock sobre una instantánea de HEAD y comandos
  deterministas; enrutador y CSS propios.
- Seis entregas en orden (E1 shell y diseño, E2 registro, E3 documentación, E4 creación y planificación,
  E5 chat global, E6 estadísticas), con criterios por entrega y del hito, y lo que queda fuera de alcance.
- Comprobaciones de lectura: rutas actuales de `/api/managed` (sin alta de proyectos ni lectura por código
  de fase), montaje `StaticFiles(html=True)` sin fallback de SPA, TOML `local-config-2` sin
  `bootstrap_enabled` y UI sin enrutador. Solo cambia la documentación: sin código, esquema, API, UI,
  dependencias ni proveedores, así que no se ejecutó la suite.

## H6.2 E1: shell, navegación y sistema de diseño (D077)

- Tarea activa de NEXT_STEPS, pedida por el usuario el 2026-10-14 sobre `e4352c3`, con Git limpio.
  [Entrega, diseño y límites](discovery/H6.2_E1_SHELL.md).
- Servidor: fallback de la UI fuera de `/api/` (`SPAStaticFiles`), `GET …/projects/{p}/phases/{code}`,
  `…/phases/{code}/tasks` (`PhaseTaskRead`, también sin fase definida) y filtros `phase`/`task` en runs. OpenAPI y
  tipos regenerados; esquema `0015_planning` sin cambios.
- Cliente: enrutador propio (`router.ts`, `navigation.tsx`), shell con migas, supervisor, tema y sesión, espacio de
  acciones por proyecto (`workspace.tsx`) y páginas en `frontend/src/pages/`. `managed.tsx` desaparece: su contenido
  pasa a Resumen y Run. Legacy H1 en `/legacy`; simulaciones fuera de la navegación.
- Sistema de diseño en `styles.css` con tokens, modo claro y oscuro, raíl del ciclo de vida de la fase y estados
  explícitos, hecho con el plugin `frontend-design`.
- Verificación: 8 pytest nuevos (`test_ui_routes.py`) y 6 pruebas Node nuevas (`router.test.mjs`); suite completa
  **1065 pytest + 121 subtests** (696 s); 12 pruebas Node; `tsc` y build; 12 checks estándar; Alembic sobre una SQLite temporal. QA con Chrome sobre
  la demo sintética, servida por la API como el wheel y por Vite: carga directa, recarga, Atrás, 404, claro, oscuro,
  386 px, y recorridos de commit, recuperación → revalidar → commit y encolar → run, sin trabajos duplicados.
- Hallazgo sin resolver: la guardia H5.6 rechaza la carga de la página con `Sec-Fetch-Site: cross-site`, así que un
  enlace desde otro sitio no abre la URL. Escribirla, un marcador o recargar sí funcionan. Pendiente de decisión.

## Coordinación

Desarrollo manual con el usuario. Una única sesión implementadora sobre los mismos archivos a la vez. La otra herramienta puede revisar una entrega terminada.

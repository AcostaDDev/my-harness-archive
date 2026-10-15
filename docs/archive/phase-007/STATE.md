# Estado archivado — P007 Agentes configurables e interfaz de producto (antes H6)

Instantánea archivada en P008-T001 (D088): secciones de H6 que el `docs/STATE.md` acumulado conservaba hasta `8622a43`. Incluye además las secciones generales «Existe», «Todavía no existe» y «Trabajo activo» tal como estaban al cerrar P007: algunas están desactualizadas respecto a H6 y se conservan como registro.

## Existe

- Especificación y backlog aceptados por el usuario como base de desarrollo.
- Documentación de arranque, decisiones y contratos de trabajo para Codex/Claude Code.
- Carpeta raíz: `$HOME/Documents/projects/my_harness`.
- H0.1 completado: [inventario de procedencia y separación núcleo/perfil](../phase-001/BASELINE.md),
  [formatos y contratos mínimos legacy](../phase-001/LEGACY_FORMATS.md) y
  [manifiesto SHA-256](../../../tests/fixtures/legacy/baseline.json) de 21 archivos de referencia.
- Cinco [escenarios sintéticos](../../../tests/fixtures/legacy/README.md): aceptación,
  REVISE, BLOCKED, interrupción y cierre. Incluyen historial, campos no registrados,
  archivos ausentes y una review deliberadamente parcial; cuatro snapshots de esquemas.
- Cuatro comprobaciones offline con biblioteca estándar en
  `tests/test_legacy_fixtures.py`; sin dependencias instaladas para esta entrega.
- H0.2 completado: [versiones, matriz de capacidades y autenticación](../phase-001/H0.2_COMPATIBILITY.md),
  con [snapshot de restricciones y resolución](../phase-001/h0.2-version-metadata.json).
  Python 3.14.4, uv 0.12.19, Node 24.15.0 y npm 11.12.1; pins directos
  documentados, TypeScript 5.9.3 por compatibilidad con openapi-typescript.
- CLI instaladas verificadas en H0.2 por versión/help: Codex 0.161.0 y Claude Code 2.1.295.
  Usuario confirma suscripciones propias mediante CLI ya autenticadas; Codex
  reporta ChatGPT. El status de Claude en sandbox no acredita sesión: no se
  interpreta como ausencia de login en el Mac. App Server/SDK no integrados.
- Ocho [muestras de streams sintéticos](../../../tests/fixtures/streams/README.md),
  sonda incremental bajo `tests/stream_probe.py` y ocho checks nuevos offline
  en `tests/test_stream_contracts.py`; esa entrega no incorporó código del producto.
- H0.3 completado: [esqueleto y verificaciones](../phase-001/H0.3_SKELETON.md),
  [alcance original](../phase-001/NEXT_STEPS.md). Paquete Python bajo `src/harness_local`:
  núcleo de biblioteca estándar, adaptador falso, API FastAPI/Pydantic y
  persistencia SQLAlchemy/SQLite con migración Alembic `0001_simulations`.
- UI React/TypeScript/Vite que crea y consulta simulaciones sintéticas persistidas.
  Tipos del cliente generados desde OpenAPI y versionados, sin contratos manuales duplicados.
- Dependencias reales instaladas en `.venv` / `frontend/node_modules`, locks
  `uv.lock` / `frontend/package-lock.json`. Pins H0.2 usados conservados;
  backend de paquete `uv_build==0.12.19`. Comandos comprobados en README/AGENTS.
- Casos de producto en `tests/product/`: 1120 pytest y 121 subtests (D086; ver su sección).
  La comprobación ligera anterior conserva sus 12 checks sin dependencias.
- H1.1 completado: [importación legacy y verificaciones](../phase-002/H1.1_IMPORT.md),
  [alcance original](../phase-002/NEXT_STEPS.md). Lector local explícito de
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
- H1.2 completado: [navegación y verificaciones](../phase-002/H1.2_NAVIGATION.md),
  [alcance original](../phase-002/NEXT_STEPS.md). Consultas HTTP de lectura y UI
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

- H1.3 completado: [observación y verificaciones](../phase-002/H1.3_OBSERVATION.md),
  [alcance original](../phase-002/NEXT_STEPS.md). Observación opt-in persistida por origen;
  polling agrupado, lecturas incrementales y reconciliación al iniciar/periódica.
- Migración `0003_legacy_observation`: control/diagnóstico por origen y feed de
  actualización atómico con el índice. JSON paginado/SSE con cursor estable,
  Last-Event-ID, deduplicación y recuperación tras reinicio; sin event sourcing del motor.
- UI actualiza listas y detalle seleccionado, conserva identidades, recupera actividad
  con navegador cerrado y reinicia tramos al actualizar, ocultando hashes diferentes.
  Lecturas de evidencias regulares por descriptores, sin enlaces/FIFO y máximo 64 MiB.

- H2.1 completado: [extracción aislada y verificaciones](../phase-003/H2.1_ENGINE.md),
  [alcance original](../phase-003/NEXT_STEPS.md). `core/engine` contiene contexto explícito,
  planificación, evidencia/política, validación, review, aceptación y flujo offline.
- `ProjectContext` y puertos de biblioteca estándar independientes de web, SQLite,
  proveedores y stack. Perfil ReferenceProject declarativo separado; solo adaptadores falsos.
- Historial/snapshots inmutables en memoria, sesiones nuevas por invocación y
  presupuesto de correcciones conservado al revalidar/reintentar. Stops separados
  de veredictos; errores sin fallback. ACCEPT no supera política/tests/evidencia.
- Extracción sin entrada API/CLI, escritores Git ni persistencia gestionada:
  `acceptance_ready` solo indica elegibilidad offline. Esquema H1.3 conservado.

- H2.2 completado: [persistencia, cola y verificaciones](../phase-003/H2.2_PERSISTENCE.md),
  [alcance original](../phase-003/NEXT_STEPS.md). Migración `0004_managed_queue`:
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

- H2.3 implementado y verificado offline: [adaptadores, procesos y límites](../phase-003/H2.3_CLI.md),
  [alcance original](../phase-003/NEXT_STEPS.md). Codex planificador/revisor y Claude
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
  [Resultado real y evidencias](../phase-003/H2.3_SMOKE.md); sin relanzamiento.
- Corrección H2.3 verificada offline: adaptador `cli-2` elimina los overrides
  reservados y conserva el proveedor integrado OpenAI; límites de retries internos
  registrados como desconocidos. Fakes rechazan el argv antiguo, y jobs `cli-1`
  no ejecutan silenciosamente el nuevo comportamiento. [Entrega](../phase-003/H2.3_CONFIG_FIX.md).
- Nuevo smoke `cli-2` autorizado y ejecutado el 2026-10-12: Codex planificador
  COMPLETE con terminal/uso, Claude FAILED por configuración MCP inválida;
  revisor no lanzado. Parada conservada, sin relanzar ni corregir en esta entrega.
  [Resultado y evidencias](../phase-003/H2.3_SMOKE_RETRY.md), D020.
- Corrección MCP Claude verificada offline: `cli-3` usa `{"mcpServers":{}}`
  con modo estricto y conserva permisos/configuración aislados. Regresión
  independiente reproduce el rechazo de `{}` antes de inferencia simulada;
  jobs congelados `cli-2`/`cli-1` bloqueados sin reescribir historial anterior.
  [Contrato y verificaciones](../phase-003/H2.3_MCP_FIX.md), D021. Esa entrega no ejecutó smoke.
- Smoke `cli-3` autorizado y ejecutado: planificador Codex COMPLETE con terminal/JSON;
  Claude acepta MCP vacío, pero FAILED por `authentication_failed`, con terminal
  de error y exit 1. Revisor no lanzado, sin login/corrección/relanzamiento.
  [Resultado y evidencias](../phase-003/H2.3_SMOKE_CLI3.md), D022.
- Diagnóstico de autenticación Claude completado en lectura: fuera del sandbox,
  status reconoce `claude.ai` en la sesión local; el entorno mínimo pierde auth
  al omitir USER y la reconoce al añadir solo USER. LOGNAME no basta. Sin login,
  inferencia ni corrección; flags de aislamiento no admitidos por auth status.
  [Evidencia reproducible y límites](../phase-003/H2.3_AUTH_DIAGNOSIS.md), D023.
- Corrección offline del entorno del smoke completada: USER explícito comprobado
  contra el UID local antes de efectos; ausencia/discrepancia detienen con diagnóstico.
  HOME/PATH/TMPDIR/LANG conservados, sin credenciales ni fuentes heredadas.
  Adaptador `cli-3` conservado; hash de configuración distinto bloquea jobs antiguos
  antes del preflight, sin reescribir resultados/specs/historial/locks.
  [Informe y regresión sintética](../phase-003/H2.3_ENV_FIX.md), D024.
- Smoke con USER validado autorizado y completo: planificador Codex, ejecutor
  Claude y revisor Codex COMPLETE, terminal/exit 0/JSON `smoke-ok` en los tres.
  Configuración congelada, sesiones frescas, herramientas/MCP vacíos y checkout
  intacto. Job DONE, run STOPPED por fin deliberado del smoke, owner cerrado,
  grupos STOPPED/dead y lock nuevo liberado por finalización normal.
  [Informe y evidencias independientes](../phase-003/H2.3_ENV_SMOKE.md), D025.

- H2.4 completado offline: [Git, worktree y commit acotado](../phase-003/H2.4_GIT.md),
  [alcance original](../phase-003/NEXT_STEPS.md). `GitWorkspace` captura base, árbol
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

- H2.5 completado offline: [migración a modo gestionado](../phase-003/H2.5_MIGRATION.md),
  [alcance original y decisiones del usuario](../phase-003/NEXT_STEPS.md). Vista previa
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

- Salida del hito 2, parte 1, completada offline: [API gestionada local](../phase-003/H2_EXIT_API.md),
  [alcance original](../phase-003/NEXT_STEPS.md). Router `/api/managed` que
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

- Salida del hito 2, parte 2, completada offline: [UI gestionada local](../phase-003/H2_EXIT_UI.md),
  [alcance original](../phase-003/NEXT_STEPS.md), D029. Proyectos/modo/supervisor,
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

- H3.1 completado offline: [prompts versionados](../phase-004/H3.1_PROMPTS.md),
  [alcance original](../phase-004/NEXT_STEPS.md), D030. Ocho recursos Markdown,
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

- H3.2 completado offline: [permisos y recuperación](../phase-004/H3.2_PERMISSIONS.md),
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

- H3.3 completado offline: [fases, preguntas, cierre y tags](../phase-004/H3.3_PHASES.md),
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

- H3.4 completado offline: [ajustes de fases](../phase-004/H3.4_PHASE_ADJUSTMENTS.md), D034.
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

- H4.1 completado offline: [chat contextual](../phase-005/H4.1_CHAT.md), D035.
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

- Exportación mecánica completada offline: [entrega](../phase-005/STATE_EXPORT.md),
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

- H4.2 completado offline: [bootstrap guiado y recuperación](../phase-005/H4.2_BOOTSTRAP.md),
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

- H4.3 completado offline: [segundo perfil TypeScript web](../phase-005/H4.3_TYPESCRIPT_PROFILE.md),
  D038. Perfil declarativo con preparación npm offline desde lock, typecheck,
  tres tests Node y build estático, reglas de rutas/comandos e instrucciones.
  Node 24.15.0, npm 11.12.1 y TypeScript 5.9.3 en fixture con lock propio.
- 16 casos nuevos con comandos reales por el puerto de prueba, agentes falsos,
  Git/SQLite temporales y worktree hasta COMMITTED. Conserva contexto, contrato,
  prompts, permisos y evidencia exacta; tests/tipos/build/política fallidos impiden
  commit. Sin cambios del núcleo, API/UI, esquema ni codec; no añade un ejecutor
  de comandos al servicio ni modifica la plantilla documental de bootstrap.

- H5.1 completado offline: [reportes JUnit y detalle de tests](../phase-006/H5.1_JUNIT.md),
  [alcance original](../phase-006/NEXT_STEPS.md), D039. Declaraciones por comando
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

- H5.2 completado offline: [backup/restauración local](../phase-006/H5.2_BACKUP.md),
  [alcance original](../phase-006/NEXT_STEPS.md), D040. CLI y biblioteca con servicio/
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

- H5.3 completado offline: [retención local de logs](../phase-006/H5.3_RETENTION.md),
  [alcance original](../phase-006/NEXT_STEPS.md), D041. Política por corte UTC/tamaño,
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

- H5.4 completado offline: [diagnóstico local de CLI](../phase-006/H5.4_DIAGNOSTICS.md),
  [alcance original](../phase-006/NEXT_STEPS.md), D042. Comando `diagnose-cli` y
  biblioteca con configuración explícita, validación estructural y preflight
  versión/help compartido con el adaptador. Sin SQLite/jobs/agentes/auth status.
- Salida acotada, timeout/grupo POSIX, sin herencia de entorno, sin revelar valores
  ni salidas libres. Versión solicitada/observada, flags ausentes y correcciones;
  coincidencia local nunca certifica autenticación/cuota/argv completo.
- 52 casos nuevos sintéticos. Esquema, codec, cli-4 y hashes congelados conservados;
  no hay actualización de versiones, fallback, reintento ni reparación automática.

- H5.5 completado offline: [distribución y arranque](../phase-006/H5.5_DISTRIBUTION.md),
  [alcance original](../phase-006/NEXT_STEPS.md), D043. Sdist/wheel con UI, plantillas
  y migraciones; instalación aislada con pins/hashes desde locks conservados.
- `harness-local init-db` prepara solo destinos nuevos; `serve --database` exige
  ruta absoluta/esquema y sirve UI/API desde loopback sin cwd/checkout/Node.
  Configuración/observación opt-in y guardia de restauraciones conservadas.
- 13 casos nuevos y recorrido HTTP de wheel instalado con simulación, reinicio,
  diagnósticos, backup/restauración de consulta. Sin publicación ni proveedores.

- H5.6 completado offline: [sesión local y endpoints](../phase-006/H5.6_SESSION.md),
  [alcance original](../phase-006/NEXT_STEPS.md), D044. Clave efímera en archivo privado,
  sesiones HttpOnly de ocho horas, cierre/reinicio invalidantes y guardia uniforme.
- Host/Origin exacto/CSRF conservados y extendidos a todas las lecturas, evidencias,
  health/OpenAPI y SSE. UI de acceso/cierre y caducidad sin repetir acciones;
  sobres pendientes conservados ante 401. Esquema/codec/cli-4/locks intactos.
- Paquete instalado y restauración de consulta funcionan con sesión sin habilitar
  proveedores. 45 casos nuevos, cliente Node y HTTP reales offline; QA visual
  bloqueada por el navegador. Límites frente a otros usuarios/servicios locales
  y cookies compartidas por hostname documentados.

- H5.7 completado offline: [recorridos, matriz y verificaciones](../phase-006/H5.7_E2E.md),
  [alcance original](../phase-006/NEXT_STEPS.md), D045. Seis recorridos nuevos de
  crear/importar/ejecutar/bloquear/denegar/reintentar/recuperar con sesión real,
  API, Git/SQLite temporales y puertos falsos; reinicio e idempotencia conservados.
- Wheel aislado recorre bootstrap → tarea → commit → reinicio → backup/restauración
  con historial, intentos, eventos y commit exactos, sin checkout original ni
  reactivación. Cliente Node conserva identidad tras respuesta perdida y 401.
  771 pruebas y 121 subtests correctos; Chrome vuelve a bloquear la URL local,
  sin QA visual acreditada. No cambia el producto ni se inicia otro incremento.

- Ejecutor de validaciones de producto implementado offline (D047):
  [entrega/composición/límites](../phase-006/COMMAND_RUNNER.md),
  [alcance previo](../phase-006/NEXT_STEPS.md). `commands-1`, configuración
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
COMMITTED, reinicio y recuperación sin repetir ejecutor. [Informe](../phase-003/H2_EXIT_UI.md),
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
validaciones implementado offline (D047). Ver [entrega](../phase-006/COMMAND_RUNNER.md)
y [revisión anterior](../phase-006/REVIEW.md). Revisión independiente
completada con un hallazgo corregido (D048, [dictamen](../phase-006/COMMAND_RUNNER_REVIEW.md)).
Composición de uso real por TOML local implementada offline (D049,
[entrega](../phase-006/LOCAL_CONFIG.md)): perfil TypeScript web, `serve --config`
y `check-config`. Propuesta de primer uso real (D033.8) preparada y ensayada
offline con selecciones del usuario (D050, propuesta (archivo `docs/discovery/FIRST_USE_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/FIRST_USE_PROPOSAL.md`)),
ejecutada una vez con autorización y completa: COMMITTED, fase CLOSED y tag
([resultado](../phase-006/FIRST_USE_RUN.md)); operación desde el wheel instalado (D051).
Comando único de desarrollo `scripts/dev` implementado (D053, [entrega](../phase-006/DEV_COMMAND.md)).
Revisor/ejecutor con proveedor elegido implementado y verificado offline (D052,
`local-config-2`, [entrega](AGENT_ROLES.md)). D057 cerró la matriz con
la combinación 1 COMMITTED y fallos en 2/3; 4 no lanzada. D058 tipa Claude
lector y D059 declara raíces del escritor Codex (`cli-7`), verificados offline.
Propuesta de combinaciones 2–4 preparada y ensayada offline (D060,
órdenes y criterios (archivo `docs/discovery/PROVIDER_MATRIX_CLI7_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/PROVIDER_MATRIX_CLI7_PROPOSAL.md`)); ejecutada
una vez con consentimiento específico y cerrada con parada preventiva (D061,
[resultado](PROVIDER_MATRIX_CLI7_RUN.md)). La 2 Codex→Codex llega a
COMMITTED con edición real; la comprobación posterior detecta cambio de hash
de configuración global y no se lanzan 3/4. Consentimiento agotado.
Diagnóstico offline del cambio global completado (D062,
[evidencia y límites](CODEX_GLOBAL_CONFIG_DIAGNOSIS.md)): adición
exacta de confianza acreditada por hash inverso y vía de persistencia interna
identificada en el binario. Atribución original inferida; contención compatible
con auth sin verificar, sin corregir el transporte. Propuesta de contención
completada (D063, [alcance y límites](CODEX_PROCESS_CONTAINMENT_PROPOSAL.md)):
frontera externa macOS candidata, lectura de auth ficticia y denegaciones de
escritura verificadas con procesos sintéticos. Compatibilidad de auth/refresh,
IPC y sandbox anidado quedaron para calificación. D064 completada offline
([dictamen](CODEX_CONTAINMENT_QUALIFICATION.md)): 27 escenarios
sintéticos; escrituras directas contenidas, escapes por fd/hardlink/delegación
y rechazo del sandbox interno lector observados. Candidata no calificada
para integración; cli-7 y auth real sin cambios. Diagnóstico del anidamiento y
frontera revisada completados offline (D065,
[dictamen](CODEX_CONTAINMENT_REVISION.md)): 32 casos; perfiles iguales
componen, restricciones distintas ensayadas se rechazan antes del objetivo.
Cierre de fd/pipe demostrado; hardlink posterior a admisión modifica un
sacrificial exterior. No hay frontera calificada para integrar ni auth/refresh
real certificados. El usuario exige memoria/contexto en `docs/` y pide avanzar
en la persistencia de proyecto. D066 implementa controles explícitos de memoria
automática (`cli-8`, [alcance](AGENT_PERSISTENCE.md)), con 215 pruebas
offline correctas. No resuelve la escritura de confianza Codex ni certifica
ausencia de estado auxiliar externo. Preparación de arranque completada D067
([dictamen](CODEX_STARTUP_PREPARATION.md)): perfil de denegación por
defecto no permite un arranque útil del fake; propuesta no apta para CLI real.
12 casos sintéticos y 14 pytest pertinentes correctos. D068 acredita después
la fuente exacta de Codex 0.162.1 (commit embebido en el binario) y suprime
específicamente la persistencia de confianza con projects inline untrusted
en el escritor, conservando permisos/auth (`cli-9`, [corrección](CODEX_TRUST_SUPPRESSION.md)).
D069/D070 se detienen por contrato contradictorio y timeouts, conservando
originales; contrato/prompt corregidos antes del escritor. **D071 completa
las cuatro combinaciones reales con COMMITTED**, [resultado](PROVIDER_MATRIX_CLI9_RUN.md).
948 pytest y 121 subtests pasan; memoria automática desactivada y muestras
globales intactas. Comprobación funcional cerrada, aislamiento externo completo
no certificado. Archivado automático no implementado ni probado por esta
matriz. QA visual H5.7 conserva su límite histórico; Claude real con esquema
tipado D058 ya comprobado en D071. Organización documental por fase y estructura
de producto diseñadas (D072, [diseño](DOCUMENT_ORGANIZATION.md)) y
confirmadas por el usuario (D073). H6.3 implementado offline: contrato documental
v2 opt-in, bloques regenerados por commit, transición de fase y edición confirmada
([entrega](H6.3_DOCUMENT_CONTRACT.md)). H6.4 implementado offline (D074):
métricas por intento materializadas con procedencia, relleno explícito, agregados por API y tokens/turnos
en el SUMMARY ([entrega](H6.4_METRICS.md)). H6.5 implementado offline (D075): creación v2
conversacional con borradores en disco y CAS hasta el commit raíz con `phase-000` y P001, y planificación de
la fase siguiente usada por la transición ([entrega](H6.5_CONVERSATIONAL_CREATION.md)). UI H6.2
implementada en seis entregas (D077–D084) y revisada en conjunto (D085, [dictamen](REVIEW.md)):
criterios cumplidos salvo la paginación de diffs, con una tarea correctiva propuesta y sin iniciar.

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
- [Alcance](NEXT_STEPS.md) `cli-5`/`local-config-2`; sin
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
- Propuesta (archivo `docs/discovery/PROVIDER_MATRIX_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/PROVIDER_MATRIX_PROPOSAL.md`) y
  [`examples/provider_matrix/prepare.sh`](../../../examples/provider_matrix/prepare.sh):
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
  [Resultado](PROVIDER_MATRIX_RUN.md).
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
  tarea de corrección. [Entrega](CONTRACT_SHAPES.md).
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
  Propuesta (archivo `docs/discovery/PROVIDER_MATRIX_RERUN_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/PROVIDER_MATRIX_RERUN_PROPOSAL.md`).
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
  Git limpio en `2c375bc`. [Resultado](PROVIDER_MATRIX_RERUN.md).
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
  [Entrega](TYPED_JSON_SCHEMA.md).
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
  [Diagnóstico, evidencia y límites](CODEX_WRITER_ROOTS.md).
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
- Propuesta (archivo `docs/discovery/PROVIDER_MATRIX_CLI7_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/PROVIDER_MATRIX_CLI7_PROPOSAL.md`): Codex→Codex,
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
  [Manifiesto](PROVIDER_MATRIX_CLI7_PREPARATION.json) registra hashes
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
  [Resultado](PROVIDER_MATRIX_CLI7_RUN.md),
  [manifiesto y verificaciones](PROVIDER_MATRIX_CLI7_RESULT.json).
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
  [Diagnóstico y opciones](CODEX_GLOBAL_CONFIG_DIAGNOSIS.md),
  [manifiesto de lectura/verificaciones](CODEX_GLOBAL_CONFIG_DIAGNOSIS.json).
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
  Git inicialmente limpio en `main`, `9db047a`. [Propuesta y aceptación](CODEX_PROCESS_CONTAINMENT_PROPOSAL.md),
  [manifiesto](CODEX_PROCESS_CONTAINMENT_EVIDENCE.json) y
  [sonda independiente](CODEX_PROCESS_CONTAINMENT_PROBE.py).
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
  Git inicialmente limpio en `main`, `aaccad0`. [Dictamen y matriz](CODEX_CONTAINMENT_QUALIFICATION.md),
  [evidencia](CODEX_CONTAINMENT_QUALIFICATION.json) y
  [sonda reproducible independiente](CODEX_CONTAINMENT_QUALIFICATION.py).
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
  [Dictamen y criterios revisados](CODEX_CONTAINMENT_REVISION.md),
  [evidencia](CODEX_CONTAINMENT_REVISION.json) y
  [sonda independiente reproducible](CODEX_CONTAINMENT_REVISION.py).
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
  Git inicialmente limpio en `7cd3503`. [Entrega y límites](AGENT_PERSISTENCE.md),
  [inventario estático](AGENT_PERSISTENCE_INVENTORY.py) y
  [evidencia](AGENT_PERSISTENCE.json).
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
  inicialmente limpio, `e2f272c`. [Propuesta y dictamen](CODEX_STARTUP_PREPARATION.md),
  [controlador sintético](CODEX_STARTUP_PREPARATION.py) y
  [manifiesto/evidencia](CODEX_STARTUP_PREPARATION.json).
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
  dentro del flujo de esta sesión. [Fuente/cli-9](CODEX_TRUST_SUPPRESSION.md),
  [ensayos detenidos](PROVIDER_MATRIX_CLI9_STOPS.md),
  [cuatro resultados reales](PROVIDER_MATRIX_CLI9_RUN.md) y
  [manifiesto final](PROVIDER_MATRIX_CLI9_RESULT.json).
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
  [Diseño completo](DOCUMENT_ORGANIZATION.md). Requisitos fijados por el
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
  documentación de D072 sin commit. [Entrega](H6.3_DOCUMENT_CONTRACT.md).
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
  [Entrega, catálogo y límites](H6.4_METRICS.md).
- Caracterización offline de los doce stdout de D071 (sin modificarlos, 12/12 verificados por SHA-256)
  con un script de biblioteca estándar independiente de la implementación; solo nombres, tipos y
  comprobaciones ([script](H6.4_STREAM_CATALOG.py), [salida](H6.4_STREAM_CATALOG.json)).
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
  [Entrega, API y límites](H6.5_CONVERSATIONAL_CREATION.md).
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
  [Alcance, entregas y criterios](NEXT_STEPS.md).
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
  [Entrega, diseño y límites](H6.2_E1_SHELL.md).
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
- Hallazgo resuelto por el usuario en D079 (se mantiene): la guardia H5.6 rechaza la carga de la página con `Sec-Fetch-Site: cross-site`, así que un
  enlace desde otro sitio no abre la URL. Escribirla, un marcador o recargar sí funcionan.

## H6.2 E2: registro de proyectos (D078)

- Tarea activa de NEXT_STEPS, pedida por el usuario el 2026-10-14. Al empezar, la entrega E1 seguía sin commit en el
  checkout; se verificó (suite completa en verde) y se commiteó aparte como `df362f9`. E2 parte de ahí.
  [Entrega, API y límites](H6.2_E2_REGISTRY.md).
- `local-config-3`: `[registration]` (raíces y techo de bootstrap), `[compositions.NOMBRE]` con perfil y comandos, y
  `[[projects]]` opcional que nombra una composición. `LocalComposer` compone proyectos del TOML y registrados.
  `local-config-1`/`-2` intactos (mismo hash congelado). Plantilla `examples/local_config.example.toml` en v3.
- Migración `0016_project_registry`: proyectos registrados versionados con baja lógica y auditoría por versión.
- API `/api/managed/registry` (opciones, detalle, vista previa y confirmación ligada a hash y versión, confianza aparte,
  repetición idempotente) y `ManagedProjectRead` con `source`, `registry_version` y `bootstrap_enabled`. El runtime
  incorpora, cambia y retira proyectos sin reiniciar; la versión del registro entra en el hash congelado y los
  cambios con trabajos sin terminar se rechazan.
- UI: `/projects/new`, registro en Ajustes (versión, auditoría, cambio y baja), columna Origen en Proyectos.
- Verificación: 10 pytest nuevos (`test_project_registry.py`), +1 ruta en `test_ui_routes.py` y 1 prueba Node. Suite
  completa: 1073 + 121 subtests en verde y un fallo esperado de igualdad exacta de `ManagedProjectRead`, corregido y
  repasado con los módulos afectados (94); total 1075. 13 pruebas Node, `tsc`, build, 12 checks estándar, y Alembic
  upgrade/check/current/downgrade sobre una SQLite temporal.
- QA con Chrome sobre `scripts/dev` y un TOML `local-config-3` sintético con supervisor y CLIs sintéticas: rechazo de
  una raíz con enlace, alta con confianza aparte → primera tarea → «Aceptado, falta el commit» sin reiniciar ni editar
  archivos; cambio de versión con auditoría; baja. Claro, oscuro y 386 px sin desbordamiento. La sesión la inició el
  usuario (se denegó leer el archivo de clave).
- Límites: la raíz no cambia; un id dado de baja no se reactiva; un cambio del registro deja en cuarentena el commit de
  runs aceptados con la versión anterior. La guardia ante `Sec-Fetch-Site: cross-site` (E1) se mantiene por decisión del usuario (D079).

## H6.2 E3: documentación (D080)

- Tarea activa de NEXT_STEPS, pedida por el usuario el 2026-10-15 sobre `9af7471`. Al empezar había cambios sin commit
  de la decisión D079 del usuario (STATE, NEXT_STEPS, DECISIONS y H6.2_E1); se conservaron y entran en este commit.
  [Entrega, verificación y límites](H6.2_E3_DOCS.md).
- Dependencias fijadas: `markdown-it@15.0.2` y `mermaid@11.17.2` (con `--before` para las transitivas); lock sin cambios
  en lo existente. `npm audit`: 2 avisos *low* de KaTeX vía Mermaid, sin arreglo con versiones de dos semanas.
- Servidor: `…/documents/tree`, `…/documents/image` (sin enlaces ni ocultos, CSP `sandbox`), `base_sha256` por cambio con
  409 `document_changed`, y `regenerate_blocks` en ediciones `worktree` (prosa local, bloques de la base, diff de lo
  descartado y bytes locales exactos admitidos por el escritor). Fallback de la UI para URLs `.md`.
- Cliente: ruta `/projects/:p/docs[/*path]`, `markdown.ts` (render seguro), `mermaid-view.ts` (diferido, `strict`, como
  imagen desde un Blob) y `pages/Docs.tsx` (árbol, resumen, visor, editor con bloques bloqueados y borrador recuperable,
  cambios locales, deriva). Página en un chunk diferido: principal 352 kB, documentación 132 kB, Mermaid aparte.
  `usePoll` conserva la lectura al releer el mismo recurso.
- Verificación: 7 pytest nuevos (`test_document_viewer.py`) y 3 rutas en `test_ui_routes.py`; suite completa **1085
  pytest + 121 subtests** (722 s). 52 pruebas Node (39 nuevas, 27 casos hostiles contra una lista cerrada de etiquetas,
  atributos y destinos). `tsc`, build, 12 checks estándar, `alembic upgrade`/`check`/`current` en SQLite temporal.
- QA con Chrome sobre `scripts/dev` y un checkout v2 sintético (sesión iniciada por el usuario): documento hostil inerte
  (interceptado y en carga directa), diagrama, imagen y enlaces; edición con recarga sin efectos repetidos; conflicto de
  CAS; regeneración de un bloque forjado; claro, oscuro y 386 px. Corregido en la QA: relectura que desmontaba el panel
  de cambios locales, resultado del commit que desaparecía y bloques vacíos sin explicar.
- Límites: sin historial por documento; borrador por pestaña; cambios fuera de documentos editables y deriva commiteada
  se resuelven fuera del editor; exclusión cooperativa frente a escritores externos.

## H6.2 E4: creación y planificación de fase (D081–D082)

- Tarea activa de NEXT_STEPS, pedida por el usuario el 2026-10-15 sobre `e87ae81`, con Git limpio.
  [Entrega, verificación y límites](H6.2_E4_SETUP.md).
- Hallazgo y decisión del usuario (D081): `typescript-web` protege `docs/**` y las escrituras documentales del harness
  rechazaban rutas protegidas, así que ningún proyecto v2 de `local-config-3` podía crearse ni pasar de fase. En v2 las
  rutas protegidas limitan al ejecutor y a los permisos, no a las escrituras confirmadas del contrato documental
  (`documents.protected_write`, usado por exportación, edición, transición y aceptación). v1 sin cambios.
- Servidor: `GET …/planning/{c}/drafts/content` (contenido y hash de la CAS por la misma inspección del turno). OpenAPI y
  tipos regenerados; esquema `0016_project_registry` sin cambios.
- Cliente: `/projects/:p/setup[/*ruta]` (brief, pasos, árbol de borradores, turnos, preguntas con aplazamiento,
  propuestas con diff y aplicación con CAS, editor de borradores, aceptación con bloqueos y archivos del commit raíz,
  operación y primera tarea), `/projects/:p/phases/:code/plan[/:c]` y panel de transición en la fase terminada con plan
  propuesto, texto propio o ninguno. `diff.ts` sin dependencias. Chunk diferido `Planning` (50 kB); principal 355 kB.
  Resumen v2 con acceso a la creación en lugar del bootstrap v1; el alta v2 con bootstrap lleva a `/setup`.
- Verificación: 1 pytest nuevo (D081) y aserciones de la lectura de borradores en el recorrido HTTP de la definición,
  4 rutas en `test_ui_routes.py`; suite completa **1090 pytest + 121 subtests** (707 s). 58 pruebas Node (6 nuevas: diff y rutas). `tsc`,
  build, 12 checks estándar, `alembic upgrade`/`check`/`current` en SQLite temporal.
- QA con Chrome sobre `scripts/dev` y un TOML `local-config-3` sintético (CLI Claude y `npm` sintéticos), con la sesión
  iniciada con la clave que el usuario pidió imprimir: recorrido completo desde la UI, alta de carpeta vacía → creación
  (dos turnos, ocho borradores aplicados, edición propia, propuesta descartada, pregunta resuelta) → commit raíz →
  primera tarea → commit → READY → cierre → plan propuesto → transición → P002 activa, sin editar archivos del proyecto.
  Recargas sin efectos repetidos, conflicto de CAS sin escritura, claro, oscuro y 386 px sin desbordamiento. Siete
  defectos corregidos durante la QA (ver el documento).
- Límites: un proyecto `typescript-web` recién creado no tiene `package.json` y el ejecutor no puede crearlo (ruta
  protegida), así que su preparación real fallaría; la conversación de planificación de una fase ya transicionada sigue
  admitiendo mensajes en la UI (el servidor los rechaza); borrador local por pestaña.

## H6.2 E5 — Chat global completado offline (2026-10-15, D083)

- [Entrega, verificación y límites](H6.2_E5_CHAT.md). Preguntas nuevas sobre HEAD congelado,
  exportado sin worktree, con evidencia antes/después, propietario/lease y recuperación propia, sin lock del checkout.
  El supervisor atiende escritor y chat en dos carriles. Los jobs antiguos conservan D035.
- Comandos `/estado`, `/tests`, `/siguiente`, `/lote`, `/check`, `/cerrar`, `/exportar`, `/abrir-fase` y
  `/tarea <texto>` deterministas, sin interpretación por modelo. Paneles existentes con sus CAS/confirmaciones;
  `/tarea` propone sin agente y aceptar crea una tarea normal. Recargas sin efectos duplicados.
- Varias conversaciones con contexto de fase o run de tarea; fase inferida cuando procede. Migración
  `0017_chat_context`, API/OpenAPI/tipos actualizados; sin codec ni dependencias nuevas. Codex omite la comprobación
  de repositorio solo para la exportación, conservando sandbox de lectura y controles de memoria.
- Verificación dirigida: 17 casos nuevos de backend y 2 rutas; 35 pruebas de chat/rutas, 60 Node, 12 checks estándar,
  `tsc`, build y migraciones sin deriva. Batería completa final: **1109 pytest + 121 subtests correctos** (759 s),
  con el aviso preexistente de deprecación httpx/Starlette.
  Primera batería: 1106 correctas, 121 subtests y un fallo de lease tras salto de reloj de 87 minutos durante un
  comando de 1,37 s; módulo H4.3 repetido, 16/16 correctas.
- QA Chrome con demo sintética: dos conversaciones, contexto de tarea, propuesta determinista → tarea → commit,
  pregunta sobre HEAD congelado, comandos de consulta/preview, check → READY → cierre. Claro, oscuro y 386 px sin
  desbordamiento, recargas sin duplicar los dos turnos ni la tarea; snapshots vacíos y cero locks al terminar.
- Límites: solo archivos regulares de HEAD (sin cambios locales), tamaño acotado y permisos cooperativos; no se
  certifica aislamiento OS ni CLI real. Ningún proveedor consumido. Próxima entrega E6, sin iniciar.

## H6.2 E6 — Estadísticas y tests completado offline (2026-10-15, D084)

- Tarea activa de NEXT_STEPS, pedida por el usuario el 2026-10-15 sobre `94577db`, con Git limpio.
  [Entrega, verificación y límites](H6.2_E6_STATS.md).
- Servidor: `GET /api/managed/metrics/validations` (cada ciclo de validación, revalidaciones incluidas, OK/KO, comandos
  y casos JUnit, por fase, tarea o raíz) y `order=key` en `/metrics/groups` y `/metrics/models`. Los ciclos no guardan
  su hora, así que la evolución de los tests es por fase, no por día. OpenAPI y tipos regenerados; esquema
  `0017_chat_context`, codec y dependencias sin cambios.
- Cliente: `/stats` y `/projects/:p/stats` (chunk diferido de 35 kB; principal 363 kB sin cambio), métricas en la página
  de la tarea, `metrics.ts` (formato, cobertura, ejes) y `charts.tsx` (barras, columnas por día, OK/KO apilados, SVG
  propio con lectura emergente y tabla). Null es «sin dato», las sumas parciales llevan cobertura y el coste es
  «equivalente API». OK/KO con tokens propios validados para daltonismo (el verde/rojo de estado no pasaba).
- Verificación: 1 caso nuevo y aserciones HTTP en `test_metrics.py`, 2 rutas en `test_ui_routes.py`; suite completa
  **1112 pytest + 121 subtests** (397 s), con el aviso preexistente de deprecación httpx/Starlette. 66 pruebas Node (6 nuevas), 12 checks estándar, `tsc`, build y `alembic upgrade`/`check`/`current`
  en SQLite temporal.
- QA con Chrome sobre `scripts/dev` (sesión iniciada por el usuario) con datos sintéticos del scratchpad: flujos por el
  adaptador CLI real con el probe (`PROBE_USAGE=1`) y runs con agentes falsos en tres fases y dos proyectos, en solo
  lectura. Resumen, cada agrupación de consumo, tablas, lecturas emergentes, favoritos, tareas, evolución OK/KO,
  paradas, intentos con procedencia, vista global y panel de la tarea; recarga y URL directa; claro, oscuro y 386 px
  (iframe; ancho del documento 369 ≤ 384). Seis defectos corregidos durante la QA (ver el documento).
- Límites: sin hora por validación; la vista global nombra los proyectos por su raíz registrada; ninguna CLI real.
  Las seis entregas de H6.2 están completas; siguiente: revisión de los criterios del hito, sin iniciar.

## Revisión de cierre de H6.2 (D085)

- Tarea activa de NEXT_STEPS, pedida por el usuario el 2026-10-15 sobre `b04ed5d`, con Git limpio.
  [Dictamen, evidencia y hallazgos](REVIEW.md). Sin cambios de código, esquema, API, UI ni
  dependencias.
- Dictamen: seis criterios del hito cumplidos y uno parcial. **Los diffs no van paginados**: `GET /runs/{id}` incluye
  el diff completo de cada ciclo (hasta 4 MiB cada uno) y la página del run lo relee cada 1,5 s, también en runs
  terminales. Se propone como tarea correctiva porque cambia el contrato; el hito queda pendiente de esa decisión.
- Recorrido sintético completo desde la UI con `scripts/dev`, un TOML `local-config-3` y una CLI Claude sintéticos
  (sesión iniciada por el usuario): alta de una carpeta vacía → dos turnos de definición, 9 propuestas aplicadas →
  commit raíz → primera tarea → ACCEPT → commit → READY → cierre (`p001`) → plan propuesto → transición → P002, más
  chat sobre HEAD, `/estado` y estadísticas. Tres commits, árbol limpio, un run por acción y recargas sin duplicados.
  Reintentos HTTP de commit, transición, planificación y aceptación: 409, sin runs nuevos.
- URLs: 19 vistas en desarrollo y 23 desde el wheel instalado en un venv propio (Python 3.14.4, requisitos por hash),
  cargadas y recargadas; fallback HTML fuera de `/api/` y 401 JSON dentro.
- Markdown hostil (script, `on*=`, SVG, `javascript:`/`data:`, imagen externa, Mermaid con HTML y `init` en `loose`)
  inerte desde la propuesta del revisor hasta el commit; 27 casos Node.
- QA: 19 vistas × claro/oscuro a 386 px sin desbordamiento de página; tablas dentro de `.table-scroll`.
- Hallazgos menores: crear conversaciones de chat o de planificación de fase no es idempotente; deriva en ámbar y
  exportación habilitada en una fase cerrada y transicionada.
- Verificación: **1112 pytest + 121 subtests** (407 s), 12 checks estándar, 66 Node, `tsc`, build y
  `alembic upgrade`/`check`/`current` en SQLite temporal (`0017_chat_context`). Wheel y sdist construidos en el
  scratchpad.
- No cubierto aquí: CLI reales; cambio y baja del registro, edición con conflicto de CAS, lote y `/tarea` no se
  repitieron (los cubren E2–E5 y pytest).

## Hallazgos de D085 corregidos (D086)

- Tarea activa de NEXT_STEPS, pedida por el usuario el 2026-10-15 sobre `22d592f`, con Git limpio: hallazgo 1
  obligatorio y, por petición del usuario, también el 2 y el 3. [Entrega, verificación y límites](H6.2_DIFF_PAGINATION.md).
- **Diffs paginados.** `GET /runs/{id}` lleva de cada ciclo `diff_sha256` y `diff_bytes` (también en su evidencia
  validada y en la de JUnit), sin texto. `GET /runs/{id}/cycles/{n}/diff` sirve páginas UTF-8 de 4–512 KiB terminadas en
  fin de línea, con cursor exacto y `sha256` opcional (409 si difiere). `/runs/{id}/jobs` paginado del más reciente al
  más antiguo; `ManagedRunRead.active_job`. La página del run sondea cada 1,5 s con job y cada 15 s sin él, y lee el
  diff al abrirlo, página a página, en tramos memoizados que el sondeo no repinta.
- **Conversaciones idempotentes.** Crear chat o planificación exige `Idempotency-Key`; reintento → misma conversación,
  otra petición con la clave → 409, y la clave se resuelve antes de reevaluar el destino. Migración
  `0018_conversation_keys`; el cliente conserva la clave hasta la respuesta (`createOnce`).
- **Fase con sucesora.** `PhaseRead.successor`; la deriva de una fase con sucesora es una nota neutra, sin adopción y
  con la exportación deshabilitada y explicada.
- Verificación: **1120 pytest + 121 subtests** (416 s; 8 casos nuevos en `test_cycle_diff.py` y aserciones nuevas en
  chat/definición), 72 Node (6 nuevas), 12 checks estándar, `tsc`, build (principal 368 kB), OpenAPI/tipos regenerados,
  `alembic upgrade`/`check`/`current`/`downgrade 0017` y vuelta en SQLite temporal, wheel y `check_distribution.py`.
- QA Chrome sobre `scripts/dev` con un diff sintético de 2,1 MiB: lectura del run de 3,6 KB, sondeo de ~16 s en reposo,
  diff completo en 33 páginas con el SHA-256 del resumen, sin tareas largas al añadir páginas ni al sondear; fases con y
  sin sucesora; conversación creada con clave y reintento sin duplicado. Claro, oscuro y 386 px sin desbordamiento.
  Durante la QA se corrigió un repintado completo del diff en cada página y cada sondeo.
- Límites: el servidor sigue decodificando el historial completo en cada lectura; sin «cargar todo»; ninguna CLI real.
  **Los siete criterios de H6.2 quedan cumplidos**; el cierre formal del hito es decisión del usuario.

## Cierre de H6.2 y del Hito 6 (D087)

- Decisión del usuario el 2026-10-15, tras D086 (`01b4f6d`): H6.2 cerrado con sus siete criterios cumplidos y, con él,
  el Hito 6 (H6.1–H6.5). El backlog no define más hitos. Sin cambios de código.
- Límites conservados como candidatos, sin iniciar: `package.json` de `typescript-web` nuevo, hora de las validaciones,
  historial decodificado completo en cada lectura, avisos *low* de KaTeX y ningún recorrido de producto con CLI reales.

## Coordinación

Desarrollo manual con el usuario. Una única sesión implementadora sobre los mismos archivos a la vez. La otra herramienta puede revisar una entrega terminada.

# Estado archivado — P003 Núcleo reusable y ejecución gestionada (antes H2)

Instantánea archivada en P008-T001 (D088): secciones de H2 que el `docs/STATE.md` acumulado conservaba hasta `8622a43`.

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
  límites en [H2.3_SMOKE.md](H2.3_SMOKE.md).
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
  porque no cambia API/UI. Detalles y límites en [H2.3_CONFIG_FIX.md](H2.3_CONFIG_FIX.md).
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
- [Informe y evidencias temporales externas](H2.3_SMOKE_RETRY.md).
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
  en [H2.3_MCP_FIX_SCOPE.md](NEXT_STEPS.md). D021.
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
  No se copian runs reales a fixtures. Detalles en [H2.3_MCP_FIX.md](H2.3_MCP_FIX.md).
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
  comando exacto, hashes y límites (archivo `docs/discovery/H2.3_SMOKE_CLI3_PREFLIGHT.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/H2.3_SMOKE_CLI3_PREFLIGHT.md`).
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
  [H2.3_SMOKE_CLI3_SCOPE.md](NEXT_STEPS.md), D022.
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
- [Informe independiente y artefactos externos](H2.3_SMOKE_CLI3.md).
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
  en [H2.3_AUTH_DIAGNOSIS_SCOPE.md](NEXT_STEPS.md).
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
- [Informe, reproducción y límites](H2.3_AUTH_DIAGNOSIS.md), D023.
  Causa comprobada para status en este Mac, mecanismo interno no auditado;
  sin inferencia, cuota/modelo certificados, otro smoke ni éxito completo H2.3.
  Próxima corrección offline del entorno propuesta, sin ejecutarla. H2.4 no iniciado.

## Corrección offline del entorno del smoke — 2026-10-12

- Git inicialmente limpio en `main`, `92af0f0`, un commit por delante de origin.
  AGENTS/STATE/NEXT_STEPS/DECISIONS y criterios H2.3 revisados; alcance conservado
  en [H2.3_ENV_FIX_SCOPE.md](NEXT_STEPS.md). D024.
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
  Sin migración ni codec nuevo. [Informe y hashes](H2.3_ENV_FIX.md).
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
- Propuesta separada (archivo `docs/discovery/H2.3_ENV_SMOKE_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/H2.3_ENV_SMOKE_PROPOSAL.md`) y NEXT_STEPS definen
  la verificación posterior, pendiente de consentimiento, sin ejecutarla.
  Transporte real completo, inferencia Claude/revisor y retries efectivos siguen
  pendientes. D022 continúa fallido; H2.4 no iniciado.

## Smoke real con USER validado — 2026-10-12

- Git inicialmente limpio en `main`, `d970e15`; usuario autoriza «Procede con
  el smoke» sobre la propuesta D024. [Alcance](NEXT_STEPS.md), D025.
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
  proveedor. [Evidencia y límites](H2.3_ENV_SMOKE.md).
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

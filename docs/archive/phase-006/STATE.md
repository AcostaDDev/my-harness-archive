# Estado archivado — P006 Calidad de uso y distribución local (antes H5)

Instantánea archivada en P008-T001 (D088): secciones de H5 que el `docs/STATE.md` acumulado conservaba hasta `8622a43`.

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
  D045 y matriz de trazabilidad en [H5.7_E2E.md](H5.7_E2E.md).
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
  y límites en [H5_CLOSURE_REVIEW.md](REVIEW.md).
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
  [alcance y criterios](NEXT_STEPS.md) escritos antes del código.
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
  no iniciada. [Entrega y operación](COMMAND_RUNNER.md), D047.

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
  [dictamen](COMMAND_RUNNER_REVIEW.md).
- Siguiente: elección del usuario de nuevo alcance; no iniciada.

## Verificación de la composición de uso real por TOML local

- Git inicial limpio en `main`, `5e0c374`. Decisiones del usuario: TOML fuera
  del checkout con `tomllib` y perfil TypeScript web. [Alcance y criterios](NEXT_STEPS.md)
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
  `max_revision_cycles = 0`. D050, propuesta (archivo `docs/discovery/FIRST_USE_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/FIRST_USE_PROPOSAL.md`).
- Hallazgos: el enlace `claude` del usuario apunta a 2.1.296, no admitido por
  `cli-4`; se fija el binario versionado 2.1.295 con `DISABLE_AUTOUPDATER=1`.
  `codex` necesita Node en `PATH`. Los tags de fase no admiten `/`.
- [`examples/first_use/prepare.sh`](../../../examples/first_use/prepare.sh): checkout
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

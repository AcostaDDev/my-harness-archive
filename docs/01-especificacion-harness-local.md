# Harness Local — Especificación técnica y de producto

Versión 0.2 · 11 de octubre de 2026 · Base aceptada para iniciar desarrollo

Aclaraciones de ejecución local, Celery y Docker: ver `DECISIONS.md`, D003 y D004. Estado implementado: ver `STATE.md`.

## 1. Propósito y alcance

Crear una aplicación local que permita configurar, ejecutar, observar y controlar un harness de desarrollo asistido por agentes. Debe funcionar sobre repositorios existentes y ayudar a crear proyectos desde cero mediante un proceso guiado de definición, planificación, implementación y revisión.

El objetivo es reducir el tiempo desde una idea hasta una primera versión verificable. La aplicación facilita decisiones y muestra evidencias; el usuario sigue siendo responsable de aceptar requisitos, arquitectura, permisos sensibles y resultados.

La primera versión será individual, local y orientada inicialmente a macOS. La interfaz se abre en el navegador; un servicio local accede a repositorios y ejecuta herramientas. Los modelos pueden requerir conexión a sus proveedores: ejecución local no significa inferencia offline.

La futura ejecución remota queda abierta mediante interfaces internas, pero no justifica añadir ahora servicios cloud, cuentas multiusuario ni infraestructura distribuida.

Este documento propone el producto nuevo. No modifica ni sustituye las decisiones del proyecto ReferenceProject. Su desarrollo se realizará manualmente con ayuda de Codex y Claude Code, sin ejecutar el propio harness para construirlo.

## 2. Base real inspeccionada

Referencia: `$HOME/Documents/projects/reference_project/.harness`, su `README.md`, `config.yaml`, `MODEL_POLICY.md`, prompts, esquemas, funciones relevantes de `harness.py`, helpers y pruebas; también el `AGENTS.md` del repositorio. Inspección estática, sin lanzar agentes, validaciones del proyecto ni modificar ReferenceProject.

### Capacidades existentes que debemos conservar

- Motor Python con contratos JSON y configuración YAML.
- Selección determinista de tarea desde `NEXT_STEPS.md`; Codex planifica cuando falta un contrato suficientemente completo.
- Claude Code ejecuta en una sesión nueva; Codex revisa independientemente el diff y las validaciones.
- Resultados `ACCEPT`, `REVISE` y `BLOCKED`, límites de revisión y detección de ciclos sin progreso.
- Control de rutas protegidas, concesiones limitadas de alcance y separación entre alcance de archivos y permisos de herramientas.
- Validación determinista, duración por comando, commits de tareas aceptadas y cierre de fases.
- Reconciliación documental y preguntas bloqueantes antes del cierre.
- Registro de eventos de Claude en JSONL, resultados, peticiones, consumo y errores.
- Recuperación de trabajos detenidos conservando cambios y evidencias anteriores.
- Política explícita de modelos y esfuerzo; separación entre modelo solicitado y observado.

### Acoplamientos y huecos que hay que resolver

| Observación en la base | Consecuencia para el producto |
|---|---|
| `ROOT` se deriva de la ubicación del propio script | Introducir un contexto explícito por proyecto; instalar el motor una sola vez |
| Helpers e instrucciones incluyen Django, PostgreSQL y Docker | Extraer un perfil ReferenceProject; el núcleo no debe conocer ese stack |
| Estado operativo distribuido entre Markdown, JSON y Git | Definir propiedad de cada dato y una migración controlada |
| Instrucciones iniciales de ejecución también se construyen en Python | Externalizar `execute-task.md`; editar solo los siete prompts actuales sería incompleto |
| `bootstrap-project.md` es de descubrimiento manual | Convertirlo en una operación explícita del asistente de creación |
| Claude usa `dontAsk` | Una denegación actual no equivale a una petición interactiva pendiente |
| El README exige un solo proceso por checkout | Incorporar exclusión mutua real; no confiar en que el usuario lo recuerde |
| El commit usa `git add -A` tras comprobaciones | En la nueva versión verificar el conjunto exacto revisado antes de preparar el commit |
| Hay duración de comandos, pero no un contrato genérico de resultados por test | Añadir importadores de reportes por framework |
| La política menciona un techo histórico de 50 turnos y la configuración fija 100 | Mostrar configuración efectiva y detectar contradicciones; no asumir que la prosa es el valor vigente |

No se ha auditado exhaustivamente cada ruta del código ni reconstruido todo el historial de ejecuciones. Estos hallazgos fundamentan la extracción y las pruebas de compatibilidad.

## 3. Conceptos del dominio

Una fase no es un prompt ni una base de datos independiente. Cada fase y cada tarea son registros de una misma base de datos local, relacionados con sus ejecuciones y evidencias.

| Concepto | Significado |
|---|---|
| Proyecto | Repositorio, configuración, documentación y políticas |
| Fase | Hito del roadmap, con objetivo y criterios de salida |
| Tarea | Unidad acotada con contrato y criterios de aceptación |
| Ejecución — run | Seguimiento de una tarea o una operación de fase |
| Intento — attempt | Una invocación concreta a un agente; no se sobrescribe |
| Operación | Planificar, ejecutar, revisar, reconciliar o cerrar |
| Revisión | Veredicto, hallazgos y evidencia sobre una versión exacta del trabajo |
| PromptVersion | Plantilla inmutable utilizada en una operación |
| Approval | Decisión humana o delegada sobre una acción concreta |
| Artifact | Diff, log, contrato, reporte de tests o documento generado |
| Event | Hecho observado con identidad, orden y procedencia |

Relaciones principales: proyecto → fases → tareas → runs → intentos. Un run de cierre pertenece a una fase y puede no tener tarea. Revisiones, validaciones, aprobaciones y artefactos se relacionan con el run y, cuando proceda, con el intento concreto.

## 4. Requisitos funcionales

| ID | Capacidad | Resultado observable |
|---|---|---|
| F01 | Registrar repositorio | Detectar Git, configuración y dependencias sin ejecutar código del proyecto automáticamente |
| F02 | Crear proyecto | Brief guiado, decisiones, plantilla, documentos y primera tarea |
| F03 | Navegar fases y tareas | Estado, criterios, dependencias, bloqueos e historial |
| F04 | Gestionar prompts | Editor, diff entre versiones, variables, validación y activación |
| F05 | Ejecutar flujo | Planificación → Claude → validación → revisión → aceptación o corrección |
| F06 | Observar agentes | Actividad, intentos, modelo, esfuerzo solicitado, duración y consumo disponible |
| F07 | Resolver bloqueos | Motivo, evidencia, conceder o denegar cuando proceda, revalidar o reintentar |
| F08 | Revisar cambios | Diff actual y por intento, archivos añadidos/eliminados, commits y contenido de cada commit |
| F09 | Inspeccionar tests | Suite, comando, resultado, duración y casos individuales si existe reporte compatible |
| F10 | Conversar con Codex | Consultar contexto y transformar solicitudes en tareas trazables |
| F11 | Controlar fases | Comprobar, reconciliar documentación, responder preguntas y aprobar cierre |
| F12 | Recuperar y exportar | Reinicio seguro, copia de seguridad y exportación legible del historial |

Se ofrecerán dos modos por proyecto: **observación**, que indexa un harness anterior, y **gestionado**, en el que el motor nuevo controla las ejecuciones. No habrá dos motores escribiendo simultáneamente sobre el mismo checkout.

## 5. Decisiones de arquitectura

### Stack recomendado

| Capa | Elección | Razón |
|---|---|---|
| Núcleo | Python, paquete independiente | Reutilizar comportamiento y pruebas del motor existente |
| API local | FastAPI + Pydantic + Uvicorn | Contratos tipados y OpenAPI para una UI independiente |
| Persistencia | SQLite + SQLAlchemy 2 + Alembic | Instalación local sencilla y migraciones explícitas |
| Interfaz | React + TypeScript + Vite | Adecuado para timelines, formularios, diffs y actualizaciones en vivo |
| Comunicación | HTTP para acciones; SSE para eventos | Reconexión sencilla, sin necesidad inicial de canal bidireccional permanente |
| Procesos | Supervisor Python y subprocess con argumentos separados | Integración incremental con las CLI actuales |
| Dependencias | uv para Python; npm con lockfile para la UI | Entornos reproducibles y herramientas conocidas |
| Verificación | Pruebas Python existentes + pytest; Vitest y Playwright | Proteger el motor y los recorridos de interfaz |

FastAPI documenta contratos OpenAPI y herramientas para APIs Python; Vite ofrece el entorno de desarrollo y build de la UI. Estas capacidades sustentan la elección, que es una recomendación arquitectónica para este proyecto. [FastAPI](https://fastapi.tiangolo.com/), [Vite](https://vite.dev/guide/), [React](https://react.dev/learn/creating-a-react-app).

SQLAlchemy dispone de soporte SQLite. Usar WAL en almacenamiento local, transacciones cortas y un único supervisor escritor; WAL no elimina la limitación de un escritor simultáneo y no es apropiado para compartir la base mediante un sistema de archivos de red. [SQLAlchemy](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html), [SQLite WAL](https://sqlite.org/wal.html).

Se fijarán versiones exactas compatibles en el primer hito. No se prescribe «latest» ni se copian versiones de modelos desde documentación histórica.

### Alternativas descartadas para el inicio

- Reescribir todo en TypeScript: reduce lenguajes, pero obliga a portar controles de recuperación y seguridad ya existentes.
- Django: viable, aunque el producto requiere especialmente control de procesos y una API; el stack de ReferenceProject no obliga al nuevo producto a usar Django.
- PostgreSQL, Celery y Redis: no necesarios para un usuario local y una cola persistida sencilla.
- Electron/Tauri: valorar después como empaquetado; primero validar el flujo usando el navegador.
- Un framework multiagente generalista: el flujo actual tiene pasos y responsabilidades bien definidos; una máquina de estados explícita es más fácil de verificar.

### Componentes

```text
Navegador: React
     │ HTTP / SSE
Servicio local: FastAPI + supervisor
     ├── Casos de uso: proyectos, tareas, prompts, aprobaciones, chat
     ├── Núcleo: estados, políticas, enrutamiento, aceptación
     ├── SQLite: estado operativo, cola, auditoría e índices
     ├── Almacén de artefactos: logs, diffs, snapshots y reportes
     └── Adaptadores
          ├── Codex CLI / App Server
          ├── Claude CLI / Agent SDK
          ├── Git
          └── validación y preparación por perfil
```

El núcleo no importa FastAPI, React, SDKs de proveedores ni reglas Django. La API y la CLI llaman a los mismos casos de uso. Inicialmente el supervisor comparte servicio local con la API, pero es el único propietario de la cola y del lanzamiento de procesos. Un único proceso Uvicorn; las ejecuciones no se implementan como tareas de fondo HTTP sin persistencia.

Cerrar el navegador no cancela el trabajo. Detener el servicio debe apagar los grupos de procesos o registrar su situación recuperable; tras un cierre inesperado se reconcilia el estado antes de volver a ejecutar.

## 6. Integración con agentes

### Primera entrega: preservar las CLI

Extraer el lanzamiento actual de `codex exec` y Claude Code en adaptadores. Mantener sesiones nuevas por intento, opciones explícitas, salidas estructuradas y registro incremental. Un adaptador declara sus capacidades: streaming, cancelación, aprobaciones interactivas, sesiones, uso y metadatos de modelo.

Modelo y esfuerzo son propiedades del intento, no de toda la tarea. Codex puede recomendar una selección; el motor comprueba que esté permitida. No se cambian modelo ni presupuesto silenciosamente ante errores.

### Chat y permisos interactivos

Codex App Server permite integrar conversaciones, eventos y solicitudes de aprobación. Para esta aplicación se propone un adaptador sobre transporte local `stdio`; las conversaciones del chat se separan de los intentos de planificación y revisión. La integración no consiste en controlar la ventana de Codex Desktop. [Codex App Server](https://learn.chatgpt.com/docs/app-server).

Claude Agent SDK ofrece el agente de Claude Code como biblioteca Python o TypeScript. Es la opción a evaluar para solicitudes de permiso interactivas. Su política tiene varias etapas; `canUseTool` no intercepta necesariamente herramientas ya autorizadas y `dontAsk` deniega las peticiones no resueltas. Un botón web de autorización exige integrar y probar ese ciclo completo. [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview), [permisos](https://code.claude.com/docs/en/agent-sdk/permissions).

En modo CLI inicial, «Conceder» crea una autorización acotada para un intento posterior y «Reintentar ejecución» inicia una sesión nueva. No se afirma que una operación previamente denegada siga esperando dentro de Claude. Si el SDK mantiene una petición viva, se responde a su identificador exacto; si expiró, la UI lo comunica.

Antes de activar SDKs se verificará autenticación admitida y compatibilidad con las cuentas del usuario. No se presupone equivalencia entre suscripciones CLI y acceso API. La documentación de Anthropic exige autorización previa para ofrecer login de claude.ai o sus límites en productos de terceros; el diseño no depende de reutilizar ese mecanismo. [Autenticación y alcance del Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview).

### Contrato interno mínimo del adaptador

```text
capabilities() -> SupportedCapabilities
preflight(config) -> AvailabilityReport
start(AttemptRequest) -> stream[NormalizedEvent]
cancel(attempt_id) -> CancellationResult
respond_approval(request_id, decision) -> Result  # solo si está soportado
```

`AttemptRequest` incluye rol, cwd, contrato, prompt renderizado, modelo solicitado, esfuerzo solicitado, timeout y snapshot de políticas. Los eventos normalizados preservan referencia al evento original, versión del adaptador y campos desconocidos necesarios para diagnóstico. No se finge que los esfuerzos de ambos proveedores son equivalentes.

## 7. Estado y persistencia: decisión explícita

### Proyectos gestionados

SQLite es la fuente de verdad para estados operativos, intentos, decisiones, cola, aprobaciones y versiones activas de configuración. Git conserva el código y su historia. Los documentos del repositorio conservan requisitos y decisiones de producto; no son una segunda base operativa editable libremente.

El motor exporta la parte mecánica de `STATE.md` y `NEXT_STEPS.md`. Cambios externos se detectan por hash y se presentan como propuestas de importación; no se mezclan silenciosamente. Una edición del contrato crea una versión nueva y puede invalidar revisiones anteriores.

Los blobs pesados viven en archivos. La base registra ruta interna, hash, tamaño y tipo. Escritura temporal + rename atómico antes de registrar disponibilidad; tras una caída se detectan blobs huérfanos y referencias incompletas. Los eventos se insertan en la misma transacción que el estado que explican. No se necesita event sourcing completo para el MVP.

### Compatibilidad con el harness anterior

En observación, los archivos originales siguen siendo autoridad y SQLite es un índice reconstruible. El importador usa ruta, identidad y hash; releer no duplica intentos. JSON incompleto en una ejecución activa se marca pendiente y se vuelve a leer. Los campos inexistentes se muestran como «no registrado».

Pasar a gestionado requiere: detener escritores anteriores, copiar estado y artefactos, validar el inventario, importar identidades, fijar la autoridad nueva y deshabilitar el arranque del motor anterior sobre ese checkout. Se conserva la copia previa. Una reversión exporta y comprueba el estado; no consiste en ejecutar indistintamente ambos motores.

### Distribución de datos

```text
Repositorio gestionado/
  .harness/
    project.yaml             # configuración portable, sin secretos
    prompts/                 # exportaciones y overrides versionables
    profiles/                # ajustes de proyecto
  docs/                      # contexto duradero y estado exportado

Directorio local de la aplicación/  # configurable, fuera del alcance del agente
  state.sqlite3
  artifacts/<project-id>/<run-id>/
  backups/
```

El lector legacy seguirá aceptando `.harness/runs/`. La portabilidad se resuelve con exportación de configuración y bundle de historial, no copiando la implementación del motor a cada repositorio.

### Entidades y restricciones

| Entidad | Campos fundamentales |
|---|---|
| Project | id, root canónica, modo, perfil, versiones, repositorio |
| Phase | project_id, código, objetivo, criterios, estado |
| Task / TaskVersion | phase_id, contrato, dependencias, revisión vigente |
| Run | propósito, task_id opcional, base_sha, estado, límite de revisiones |
| Attempt | run_id, rol, número, modelo solicitado/observado, esfuerzo solicitado/observado, versiones CLI/SDK, tiempos, resultado |
| Review / Finding | attempt_id, veredicto, severidad, motivo, evidencia, fingerprint revisado |
| Validation / TestCase | run_id, comando, reporte, resultado, duración, fingerprint validado |
| Approval | acción exacta, alcance, vigencia, actor, decisión, política, estado |
| PromptVersion | nombre, contenido, hash, variables, esquema, autor, fecha |
| Event | id, secuencia, run_id, intento, tipo, payload, timestamps |
| Artifact / Commit | ubicación/hash o SHA, relación con intento y tarea |
| Job | comando, idempotency_key, estado, lease, heartbeat |
| ChatMessage / Proposal | conversación, contenido, referencias, tarea originada |

Unicidad de código de tarea por proyecto; intento numerado por run; evento normalizado deduplicado; una sola resolución válida por aprobación; clave idempotente por acción. Campos ausentes se guardan como null y con procedencia, nunca como cero. Timestamps persistidos en UTC y presentados en la zona del usuario.

## 8. Flujo y recuperación

### Tarea

```text
DRAFT → READY → PLANNING → EXECUTING → VALIDATING → REVIEWING
                                                        ├─ REVISE → EXECUTING
                                                        ├─ BLOCKED
                                                        └─ ACCEPTED → COMMITTING → COMPLETED
```

`WAITING_APPROVAL`, `FAILED`, `INTERRUPTED` y `CANCELLED` guardan etapa de procedencia y motivo. El veredicto del revisor es distinto del estado del proceso: `ACCEPT` no equivale a commit terminado.

- `REVISE` añade un intento sin borrar el anterior y consume el límite persistido.
- Un error de autenticación, cuota o entorno detiene el trabajo; no cambia el modelo ni repite indefinidamente.
- La acción **Revalidar** conserva cambios y ejecuta comprobaciones antes de revisión.
- **Reintentar ejecución** crea un intento de agente nuevo, conservando el trabajo existente.
- **Cancelar** detiene el grupo de procesos y conserva evidencias; no revierte archivos automáticamente.
- **Pausar** significa detenerse en el próximo punto seguro, salvo que el adaptador soporte una interrupción explícita. La UI diferencia «pausa solicitada» y «pausado».

Un bloqueo de producto exige una decisión; conceder permisos no lo resuelve. Los pasos habilitados se calculan en el servidor, no solo en botones de la UI.

### Fases

`ACTIVE → CHECKING → READY_TO_CLOSE → CLOSED`, con ramas `NEEDS_RECONCILIATION` y `BLOCKED`. Cerrar exige tareas aceptadas, validación vigente, revisión lista y autorización conforme a política. Separar en la UI ejecución por lote y permiso para cerrar fases: el `--until-blocked` actual concede ambos y no debe ocultarse detrás de un botón ambiguo.

### Consistencia frente a caídas

Persistir intención antes de efectos externos y resultado después. Al arrancar, reconciliar jobs activos con procesos, archivos y Git. Un lease vencido no demuestra que el proceso murió: no iniciar otro escritor hasta descartar el anterior.

No se promete ejecución externa «exactamente una vez». Para un commit, guardar base SHA, árbol esperado e identificador de operación. Tras una caída entre commit y guardado, buscar y verificar el commit antes de repetir. Si no se puede determinar qué ocurrió, pasar a recuperación manual con evidencia.

Usar bloqueo de sistema operativo por checkout y exclusión persistida de jobs. Limitar inicialmente a una ejecución que modifique código por proyecto. Ninguna transacción SQLite queda abierta mientras se espera a un agente.

## 9. Prompts y modularidad

| Prompt | Operación y rol |
|---|---|
| bootstrap-project.md | Descubrimiento y propuesta inicial con Codex |
| plan-task.md | Completar un contrato cuando la planificación determinista no basta |
| executor-routing.md | Política incluida en planificación/revisión; no implica una llamada adicional |
| execute-task.md — nuevo | Instrucciones base de ejecución hoy parcialmente embebidas en Python |
| review-task.md | Revisión independiente con Codex |
| revise-task.md | Corrección por Claude en un intento nuevo |
| reconcile-phase.md | Mantenimiento documental limitado con Codex |
| close-phase.md | Evaluación de cierre con Codex; los cambios mecánicos son del motor |

Jerarquía propuesta: plantilla base → perfil → override de proyecto. La versión efectiva se resuelve y congela al crear el intento. Editar un prompt crea borrador; activar afecta a intentos futuros. Aplicarlo a un run detenido es una decisión registrada con versiones anterior y nueva.

Guardar plantilla, variables, texto final renderizado, referencias documentales, esquema de salida y hashes. Las versiones históricas no se modifican. Validar variables desconocidas/ausentes y esquemas antes de invocar al modelo. Una reversión de prompt crea una nueva versión a partir de la anterior.

El contenido del prompt no puede eliminar límites del motor ni conceder herramientas. Los perfiles declaran preparación de entorno, comandos de validación, parsers de tests, rutas protegidas y plantillas. El primer perfil extraído será ReferenceProject/Django; un segundo proyecto de stack distinto demostrará que el núcleo es reutilizable.

«Cualquier proyecto» significa que el núcleo acepta perfiles distintos y repositorios arbitrarios; no que la primera versión conozca todos los lenguajes y entornos. Publicar una matriz de perfiles probados y permitir configuración manual.

## 10. Permisos, Git y confianza local

Separar cinco decisiones: alcance de archivos; herramientas/comandos; acceso a red; cambios de requisitos/arquitectura; aceptación y cierre. Una concesión de alcance no concede shell o red.

Cada aprobación muestra quién la pide, operación, argumentos relevantes, archivos/dominio, motivo, intento y duración. Opciones: denegar, permitir una vez, permitir para esta tarea. Las políticas persistentes se editan en su propia pantalla con diff. Usar expiración y huella de la petición; una autorización antigua no se reutiliza para una acción diferente.

Permiso efectivo = restricciones globales ∩ proyecto ∩ contrato ∩ capacidades reales del proveedor. Las denegaciones de nivel superior prevalecen; cualquier concesión debe caber dentro de su autoridad. El motor es quien aplica esta lógica, con validaciones anteriores y posteriores a la ejecución.

Los controles posteriores del diff detectan cambios, pero no impiden lecturas ni todos los efectos externos. Un worktree separa trabajo Git; no es un sandbox de seguridad. Usar las restricciones disponibles del ejecutor y describir el nivel de aislamiento real. [Git worktree](https://git-scm.com/docs/git-worktree).

En modo gestionado, preferir un worktree por tarea y conservarlo durante sus revisiones. Una tarea aceptada crea un checkpoint ahí; integrar en la rama de destino es una acción separada y puede exigir validación adicional si cambió la base. No sobrescribir modificaciones del usuario ni limpiar automáticamente un checkout con cambios desconocidos.

Antes de aceptar, vincular revisión y tests a base SHA + árbol/diff completo, incluidos archivos nuevos y staged. Si cambia el contenido antes del commit, invalidar evidencia y revalidar. Añadir al commit solo el conjunto revisado más actualizaciones mecánicas identificadas.

El servicio escucha solo en loopback. Requiere sesión local, validación de Host/Origin y protección CSRF; sin CORS abierto. Credenciales fuera del frontend, logs y repositorios, usando referencias al almacén seguro del sistema. Validar rutas canónicas, escapes `..` y symlinks. Logs y Markdown se renderizan sin HTML ejecutable.

Las validaciones también ejecutan código del repositorio: un prefijo permitido como `python` o `npm` no es una frontera de seguridad. Configurar comandos estructurados `argv`, cwd y entorno en perfiles confiables. Repositorios, scripts y configuraciones externas requieren confianza explícita antes de su primera ejecución.

## 11. Telemetría y tests

Registrar acciones y resultados observables, junto con resúmenes y motivos explícitos de selección/revisión. La UI no promete mostrar pensamiento interno completo. Si el proveedor entrega un resumen de razonamiento permitido, identificarlo como tal y no como evidencia de que una acción se ejecutó.

Por intento: proveedor, rol, modelos solicitados y reportados, esfuerzo solicitado y efectivo solo si se reporta, versión CLI/SDK, versión del adaptador, prompts/configuración, inicio/fin, duración, salida, herramientas, ficheros observados y resultado.

Por consumo: input, output, caché y otros campos según proveedor, indicando si son incrementales o acumulados para no sumarlos dos veces. Coste reportado o estimado con moneda, tarifa y fecha; separado del consumo de una suscripción. Un alias de modelo no prueba una versión interna exacta y tokens no permiten deducir porcentaje de cuota.

Por validación: comando, entorno, código de salida, stdout/stderr, timeout, duración y huella de código. Por test: identificador estable, suite, resultado, duración y error cuando el framework genere un reporte compatible. Adoptar JUnit XML como primer formato de intercambio y conservar el reporte original. Si solo existe duración de comando, mostrarla a ese nivel.

No sumar duraciones individuales como tiempo total de una suite paralela. Comparar rendimientos solo con entorno y selección equivalentes. Métricas útiles: tiempo hasta tarea aceptada, porcentaje aceptado a la primera, revisiones, duración de tests y consumo total incluyendo fallos.

## 12. Experiencia de usuario

Pantallas iniciales: proyectos; detalle de proyecto/fases; tarea con timeline, diff, revisiones, tests y consumo; bandeja de bloqueos; prompts; configuración y permisos; chat lateral contextual.

Cada ejecución debe responder: qué hace ahora, qué evidencia existe, qué la bloquea y cuál es la siguiente acción. Los datos técnicos detallados quedan desplegables. Estados distintos para «agente vivo sin nueva actividad», «herramienta iniciada», «herramienta terminada» y «resultado validado».

### Crear desde cero

1. Recoger problema, usuarios, funciones mínimas, restricciones y objetivo de entrega.
2. Codex propone requisitos, alternativas y decisiones pendientes.
3. El usuario acepta alcance y arquitectura; se registra la decisión.
4. Elegir carpeta vacía y plantilla versionada; previsualizar estructura y comandos de preparación.
5. Crear repositorio y documentos canónicos, perfil y primera fase.
6. Comprobar entorno y generar la primera tarea acotada.
7. Ejecutar y revisar el primer recorrido completo.

No generar de golpe todo el producto desde un brief incompleto. El primer bootstrap soportará una plantilla mantenida; nuevos stacks se incorporan como perfiles.

### Chat: «Ajusta X»

El chat conserva conversación para comodidad, pero convierte decisiones duraderas en propuestas y tareas versionadas. Recoge contexto del proyecto, consulta código en modo de lectura y propone un contrato con objetivo, alcance, criterios y validaciones. Solicitudes dentro de un modo de ejecución previamente autorizado pueden encolarse; cambios de alcance o decisiones pendientes se muestran antes de ejecutar.

Una vez aceptada la propuesta, el motor despacha a Claude y relaciona conversación → tarea → run → evidencias. El chat no modifica código de aplicación por una vía paralela ni eleva permisos. Mensajes recibidos durante un intento se encolan o se aplican en un punto seguro; no cambian el contrato en silencio.

## 13. API propuesta

Todas las mutaciones validan esquema, autorización, estado y versión esperada del recurso. Devuelven un job persistido cuando requieren trabajo prolongado.

| Endpoint conceptual | Función |
|---|---|
| POST /projects | Registrar proyecto o iniciar propuesta de creación |
| GET /projects/{id}/phases | Fases y tareas |
| POST /tasks/{id}/runs | Iniciar con contrato y políticas fijados |
| POST /runs/{id}/actions | revalidate, retry_executor, request_pause, cancel |
| GET /runs/{id}/events | SSE con cursor y reconexión |
| GET /runs/{id}/artifacts | Evidencias paginadas |
| POST /approvals/{id}/decision | Resolver petición vigente una sola vez |
| POST /prompts/{name}/versions | Crear versión |
| POST /projects/{id}/prompt-activations | Activar versión para el proyecto |
| POST /phases/{id}/actions | check, reconcile, close |
| POST /projects/{id}/chat/messages | Conversar o generar propuesta |
| POST /proposals/{id}/accept | Crear/actualizar tarea mediante decisión explícita |

`Idempotency-Key` para inicio, cierre, aprobación y aceptación de propuesta. `expected_version` para impedir cambios desde una pantalla obsoleta. Respuesta 409 ante conflicto y 422 ante contrato inválido. SSE entrega solo eventos persistidos, con id creciente y deduplicación en cliente. Si el cursor ya no está retenido, exigir recarga de snapshot.

Ejemplo de evento propio del producto, no del proveedor:

```json
{
  "schema_version": 1,
  "id": "evt_001",
  "sequence": 18,
  "run_id": "run_001",
  "attempt_id": "attempt_002",
  "type": "validation.completed",
  "occurred_at": "2026-10-11T12:00:00Z",
  "payload": {"validation_id": "val_001", "status": "passed", "duration_ms": 1432}
}
```

## 14. Requisitos no funcionales y operación

- Navegar por datos ya registrados no invoca modelos ni necesita conexión externa.
- El frontend no accede directamente al filesystem ni lanza comandos.
- Listados paginados, logs por tramos y diffs con límites explícitos; nunca bloquear la UI leyendo todo un historial.
- Objetivo inicial: actividad visible en menos de 2 segundos desde su persistencia bajo carga de una ejecución local. Medir con 10.000 eventos sintéticos; es una meta de producto, no un resultado obtenido.
- Instalación de desarrollo reproducible con lockfiles; distribución posterior con assets web compilados y un único comando de inicio. Node se necesita para construir la UI, no para servir esos assets.
- Logs con rotación, límite por artefacto y política de retención configurable. Preservar contratos, aprobaciones y veredictos al purgar logs voluminosos.
- Backup consistente de SQLite mediante mecanismo de backup y copia de artefactos referenciados; restauración probada en directorio separado. No copiar solo el fichero principal mientras WAL está activo.
- Actualizaciones con migraciones, backup previo y comprobación de versiones CLI/SDK. Un adaptador incompatible se bloquea con diagnóstico.
- No afirmar auditabilidad contra manipulación por el propietario del equipo: el historial es trazable a nivel de aplicación, no un registro externo inviolable.

## 15. Límites del MVP y evolución

El MVP completo incluye importar en lectura, ejecutar un flujo gestionado seguro, editar prompts, inspeccionar evidencias, resolver bloqueos, chat que crea tareas y bootstrap de una plantilla. Se entrega por incrementos: el panel de lectura por sí solo no cumple todo el producto.

Se aplazan multiusuario, nube, ejecución paralela sobre el mismo proyecto, marketplace de plugins, editor visual de workflows, terminal web genérica y despliegue automático a producción. Los contratos de adaptadores y almacenamiento dejan espacio para evolucionar sin implementar esas capacidades ahora.

## 16. Criterios de aceptación globales

1. Importar dos veces un historial no duplica entidades y no inventa datos ausentes.
2. Una tarea recorre ejecución, fallo de test, corrección, revisión y commit con historial completo.
3. Dos peticiones simultáneas no crean dos ejecutores sobre el mismo checkout.
4. Una denegación no ejecuta la herramienta y una aprobación caducada no puede reutilizarse.
5. Reiniciar el servicio durante una ejecución conserva evidencias y evita repetir efectos a ciegas.
6. Editar prompts no cambia qué versión figura en un intento pasado.
7. Cambios posteriores al diff revisado invalidan la aceptación antes del commit.
8. El cierre de fase exige validación y autorización vigentes.
9. Un segundo perfil de stack distinto funciona sin cambios en el núcleo.
10. Una petición por chat termina vinculada a una tarea y a su resultado.
11. Crear un proyecto vacío produce documentos, estructura y primera tarea ejecutable.
12. Backup y restauración recuperan estados, referencias y evidencias verificadas por hash.

## 17. Decisiones fijadas y pendientes

**Confirmado por el usuario:** local como destino del desarrollo, posibilidad futura de nube sin desarrollarla ahora, reutilización del harness de ReferenceProject y construcción manual con Codex y Claude Code.

**Recomendado en esta especificación:** conservar Python, FastAPI, React/TypeScript, SQLite, adaptadores CLI primero, autoridad operativa en base de datos para proyectos gestionados, sesiones nuevas por intento y migración gradual.

**A resolver en las pruebas iniciales:** compatibilidad exacta de CLI/SDK y autenticación; primer perfil de proyecto nuevo; retención por defecto; experiencia de instalación final. Estos puntos no impiden comenzar la extracción y el importador offline.

Las decisiones de este documento son propuestas de diseño; las capacidades descritas como nuevas todavía no están implementadas. El backlog adjunto establece cómo verificarlas antes de declararlas disponibles.

# Estado archivado — P005 Chat y creación de proyectos (antes H4)

Instantánea archivada en P008-T001 (D088): secciones de H4 que el `docs/STATE.md` acumulado conservaba hasta `8622a43`.

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

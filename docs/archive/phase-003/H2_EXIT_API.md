# Salida del hito 2, parte 1 — API gestionada local

Entrega: 2026-10-12. [Alcance original](NEXT_STEPS.md). Verificado offline
con TestClient, checkouts Git y SQLite temporales, los fixtures legacy sintéticos de
H0.1 y agentes/comandos falsos; además, un arranque breve de Uvicorn real en
loopback sin configuración gestionada. Sin proveedores, CLI de agente, smoke, red,
runs privados, ReferenceProject ni cambios de configuración global. UI gestionada no
incluida (parte 2).

## Revisión previa y puntos resueltos

Revisados especificación §5 (servicio y supervisor), §10 (seguridad local), §13 (API) y §14,
D010/D011, D016/D017, D026 y D027. Ninguna contradicción obliga a cambiar el diseño
aceptado. Tres huecos se resuelven con criterio reversible:

1. **Proyectos.** La §13 propone `POST /projects`, pero no existe un registro de
   proyectos gestionados y `submit` necesita un `ProjectContext` completo (perfil
   con comandos y política con modelos). Aceptarlo del cliente permitiría a una
   petición HTTP definir comandos o selecciones, contra la §14 («el frontend no
   lanza comandos»). Por eso los proyectos se registran **en el servidor**
   (`ManagedConfig`), y el cliente solo los nombra por identificador. Registrar un
   proyecto por HTTP queda pendiente.
2. **Ejecución de jobs.** Supervisor opt-in dentro del proceso Uvicorn, no una
   acción «ejecutar siguiente job». Ver D028.
3. **Seguridad local.** La §10 pide sesión local, validación de Host/Origin y CSRF.
   Se implementan Host/Origin y CSRF por cabecera propia en la API gestionada. La
   sesión local, que protegería frente a otros usuarios del sistema operativo con
   acceso a loopback, **no se implementa** en esta parte.

## Frontera e integración

- `services/managed_runtime.py`:
  - `ManagedProject(id, context, versions)` y `ManagedConfig` (proyectos,
    `ports_factory`, `commit_factory`, `supervisor`, lease, intervalo de sondeo y
    directorio de migraciones).
  - `load_config()` lee `HARNESS_MANAGED_CONFIG=módulo:atributo` al arrancar.
  - `SupervisorWorker` es un hilo que llama a `LocalSupervisor.run_once`.
  - `ManagedRuntime` se compone en el lifespan: exportar OpenAPI no conecta
    SQLite ni importa configuración.
- `api/managed.py`: router `/api/managed` con la guardia local y el mapeo de
  errores. Solo delega en `SQLiteManagedRepository`, `LocalSupervisor` y
  `MigrationService`, sin lógica nueva de motor.
- `storage/managed_views.py`: lecturas paginadas de runs, jobs, intentos y eventos,
  más el detalle de un run (historial resumido, aceptación y commit). Solo lectura.
- `storage/migration.py` / `services/migration.py`: `expected_version` opcional en
  `take_over` y `begin_revert`, comprobado en la misma transacción que la
  transición. Quien no lo pasa conserva el comportamiento H2.5.
- `api/app.py`: `create_app(url, ui_dir, managed=None)` incluye el router. H0/H1
  conservan sus rutas y contratos; el OpenAPI anterior sigue idéntico en sus rutas
  y esquemas.

## Contratos HTTP

Toda ruta exige `Host` de loopback (`127.0.0.1`, `localhost`, `::1`, cualquier
puerto). Toda mutación exige además:

- `Origin` de loopback, si el navegador lo envía. `null` y `file:` se rechazan.
- La cabecera `X-Harness-Local: 1`. Una página ajena no puede añadirla sin preflight
  CORS, y el servicio no habilita CORS.

Errores: `{"detail": {"code", "diagnostic"}}`, con 403, 404, 409 y 422.

| Método y ruta | Función | Garantía |
|---|---|---|
| GET `/supervisor` | Supervisor activo, vivo, último error y puertos configurados | Lectura |
| GET `/projects`, `/projects/{id}` | Proyectos registrados en el servidor | Lectura |
| GET `/projects/{id}/mode` | Rechazo de modo, activación viva, deriva, documentos e historial | Lectura |
| GET `/projects/{id}/migration/preview` | Vista previa H2.5 | Sin escrituras |
| POST `/projects/{id}/migration/activations` | Activar con `preview_sha256` y `legacy_stopped` | Idempotente por hash de vista previa |
| GET `/activations/{id}` | Activación | Lectura |
| POST `/activations/{id}/resume`, `/abandon`, `/revert`, `/resume-revert` | Transiciones explícitas con `reason` | `expected_version` obligatorio |
| GET `/projects/{id}/runs` | Runs del checkout, paginados | Lectura |
| POST `/projects/{id}/runs` | Encolar tarea `{task_id, phase_id, text}` | `Idempotency-Key`, 202 con el job |
| GET `/runs/{id}`, `/runs/{id}/jobs`, `/runs/{id}/attempts` | Detalle, jobs e intentos paginados | Lectura |
| GET `/runs/{id}/events?after&limit` | Eventos confirmados por secuencia, con cursor y `has_more` | Lectura |
| POST `/runs/{id}/actions` | `revalidate`, `retry_executor`, `commit` | `Idempotency-Key` y `expected_version` |
| GET `/jobs/{id}` | Job, incluido `owner_token` para conciliar | Lectura |
| POST `/jobs/{id}/confirm-stopped` | Confirmar escritor detenido | `owner_token` y `expected_version` |

Mapeo de errores:

| Origen del error | HTTP | Código |
|---|---|---|
| Admisión rechazada por modo (`Conflict` causado por `ModeConflict`) | 409 | `mode_refused` |
| Versión o idempotencia en conflicto | 409 | `conflict` |
| Transición de activación en conflicto | 409 | `migration_conflict` |
| Activación detenida | 409 | `migration_refused` |
| Propiedad perdida | 409 | `ownership_lost` |
| Checkout ilegible | 409 | `checkout_unreadable` |
| Commit sin escritor Git configurado | 409 | `commit_writer_unavailable` (no se encola nada) |
| Recurso desconocido o checkout no registrado | 404 | `not_found` |
| Petición inválida | 422 | `invalid_request` |

Las acciones solo operan sobre runs de checkouts registrados. Los runs de otras
raíces de la misma base se pueden leer (`project_id: null`), pero no modificar.
El commit por HTTP no admite actualizaciones mecánicas: contiene exactamente lo
revisado. La exportación mecánica de STATE/NEXT_STEPS sigue pendiente.

## Verificación

- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`: 306 pruebas
  y 121 subtests correctos (288 anteriores + 18 nuevas). Los 12 checks ligeros
  pasan. `alembic upgrade head`/`check`/`current` correctos en SQLite temporal;
  sin migración nueva (esquema `0007_managed_activation`).
- Recorrido HTTP completo con Git real en un worktree por tarea:
  - Encolar, doble envío (mismo job), ejecución por el supervisor, revisión
    ACCEPT y ACCEPTANCE_READY.
  - Commit encolado con versión y doble envío (mismo job), COMMITTED con el id
    esperado igual a HEAD y un solo commit nuevo.
  - Eventos 1..n contiguos, idénticos con páginas de 4 o de 100.
  - El checkout principal no cambia: HEAD, índice, contenido y estado.
  - Tras reiniciar con supervisor y puertos vacíos: el run y los eventos son
    idénticos, ningún puerto se pide y no hay commit adicional.
- Job encolado con supervisor desactivado: sigue en QUEUED, sobrevive al reinicio y
  se ejecuta una sola vez al activar el supervisor; repetir la clave no duplica.
- Recuperación:
  - Un `JournalError` durante la invocación del revisor deja el job en
    RECOVERY_REQUIRED con el lock retenido y `last_error` visible.
  - `revalidate` prematuro, `owner_token` erróneo y versión obsoleta devuelven 409
    sin filas nuevas.
  - La confirmación correcta deja el run INTERRUPTED y libera el lock; la
    confirmación duplicada devuelve 409.
  - `revalidate` lleva a ACCEPTANCE_READY y después a COMMITTED. El ejecutor no se
    repite y el revisor incierto queda INTERRUPTED («outcome unknown»).
- Conflictos con estado, filas y checkout idénticos: versión obsoleta, clave
  reutilizada con otra acción, retry sobre un run no detenido, commit sin escritor
  y mismo `Idempotency-Key` con otro texto. Peticiones inválidas (sin clave, campo
  extra, texto vacío, tipo erróneo, clave de más de 200 caracteres) devuelven 422
  sin filas.
- Modo:
  - Un checkout legacy no activado y un marcador sin activación devuelven 409
    `mode_refused` con diagnóstico, sin filas ni cambios en el checkout y sin pedir
    puertos.
  - Tras activar por HTTP, un run legacy nuevo devuelve 409 «Escritor legacy», y
    `/mode` muestra la deriva.
- Migración por HTTP:
  - La vista previa no escribe nada: árbol, tablas y directorio de migraciones
    ausente.
  - Un cambio posterior a la vista previa devuelve 409 sin marcador.
  - Activar es idempotente.
  - Revertir con versión obsoleta devuelve 409 y la activación queda intacta; con
    la versión correcta queda REVERTED, sin marcador y con exportación verificada
    por hash. El doble envío devuelve 409.
  - Tras revertir, el checkout queda idéntico al inicial y el trabajo gestionado se
    rechaza.
  - Una activación interrumpida por la biblioteca se reanuda o se abandona por HTTP
    solo con la versión vigente.
- Seguridad:
  - Host ajeno o parecido (`127.0.0.1.evil.example`) devuelve 403 en lecturas y
    mutaciones.
  - Sin cabecera propia, 403; con `Origin` ajeno, `null` o `file:`, 403. Ninguno
    deja filas.
  - `Origin` `http://localhost:5173` (Vite) se acepta.
- Servicio por defecto, con `subprocess.Popen` prohibido: sin proyectos ni
  supervisor, y las rutas legacy siguen funcionando. La configuración inválida
  impide arrancar: base o directorio de migraciones dentro de un checkout,
  identificador duplicado o inválido, versiones incompletas, supervisor sin puertos.
  Carga explícita por variable de entorno comprobada.
- Ocho mutaciones temporales detectadas y el código restaurado:
  - sin comprobación de Host;
  - sin cabecera CSRF;
  - sin comprobación de Origin;
  - sin versión esperada en activación;
  - sin la comprobación del escritor de commit;
  - código de rechazo de modo genérico;
  - acciones sobre checkouts no registrados;
  - supervisor que no ejecuta.
- OpenAPI y tipos regenerados; rutas y esquemas anteriores idénticos. TypeScript y
  build Vite correctos; la UI no cambia.
- Uvicorn real en `127.0.0.1:8015` con SQLite temporal y sin configuración:
  - supervisor y proyectos vacíos;
  - `Host: evil.example` devuelve 403;
  - POST sin cabecera devuelve 403 `csrf_header_required`;
  - con cabecera, 404 por proyecto no registrado;
  - apagado SIGTERM limpio.
- Diff y whitespace revisados. Persiste el aviso conocido Starlette/HTTPX.

## Límites

- **No implementado.**
  - Sesión local frente a otros usuarios del sistema operativo.
  - Guardia Host/Origin/CSRF en las rutas H0/H1. Las mutaciones existentes
    (simulación y observación) siguen sin ella.
  - Registro de proyectos por HTTP.
  - SSE de eventos gestionados (solo JSON paginado).
  - UI gestionada.
  - Pausa o cancelación por HTTP.
  - Actualizaciones mecánicas por HTTP.
- **Supervisor.**
  - Un solo hilo y un job cada vez en toda la base. Procesa toda la cola de la
    base, incluidos jobs encolados por biblioteca para raíces no registradas,
    igual que `LocalSupervisor`.
  - Al apagar espera como máximo un lease. Un job que no termine sigue en el hilo
    daemon hasta que el proceso sale; después su lease vence y queda
    RECOVERY_REQUIRED hasta la confirmación explícita. No se certificó con CLI
    reales.
- **Activación síncrona.** Activar y revertir copian y verifican dentro de la
  petición, sin límite de tamaño propio.
- **Confianza local.** La configuración por `HARNESS_MANAGED_CONFIG` importa código
  local de quien arranca el servicio.
- **Proveedores.** La configuración real de proyectos con adaptadores CLI H2.3 y
  Git H2.4 es posible pero no se ejercitó con proveedores (fuera de alcance). El
  recorrido usa fakes; no acredita proveedores ni tarea real.

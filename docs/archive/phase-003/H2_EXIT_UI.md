# Salida del hito 2, parte 2 — UI gestionada local

Entrega offline: 2026-10-12. [Alcance original](NEXT_STEPS.md), D029.
Git inicial limpio en `1f5a8df`, rama `main`. Revisados AGENTS, STATE, NEXT_STEPS,
DECISIONS (D011/D013/D014/D027/D028), especificación §12 y salida del backlog H2.
Sin contradicciones materiales; la finalización de este incremento es COMMITTED
según D026, no integración en rama destino ni cierre de fase.

## Implementación

- Pestaña inicial «Proyectos gestionados»: registro del servidor, supervisor,
  configuración de puertos y último diagnóstico. H0/H1 siguen accesibles.
- Modo, deriva e historial; vista previa completa de migración, activar, reanudar,
  abandonar, revertir y reanudar reversión. Motivo y casilla explícitos; versión
  esperada y hash de inventario provienen de la lectura visible.
- Formulario de contrato, tarea y fase; UUID y cuerpo congelados en la pestaña,
  bloqueo inmediato de doble envío y repetición explícita de solicitudes inciertas.
  La última petición idéntica consecutiva conserva la clave tras éxito rápido.
- Runs e intentos paginados; estados y etapa, aceptación, diff de cada ciclo,
  tests y review persistidos; versiones/resultado/telemetría en desplegables como
  datos originales. Null permanece null; no se deduce modelo efectivo/cuota/coste.
- Eventos por cursor, 50 por página, sondeo y deduplicación. Solo muestra filas
  confirmadas. Reinicio recupera lecturas sin reejecutar jobs. Datos previos se
  etiquetan sin actualizar durante desconexión; acciones del run se deshabilitan.
- Revalidación, reintento explícito, confirmación de commit y recuperación con
  token/versión/evidencia. 409 muestra diagnóstico y recarga estado; no hay éxito
  optimista ni reintento silencioso con versión nueva.
- Ampliación aditiva de `CycleRead` con diff/procedencia/validación/review del
  historial congelado, sin escrituras nuevas. Tipos regenerados desde OpenAPI.

## Demo reproducible, sin proveedores

Desde la raíz, elegir una ruta **nueva**. El preparador rechaza cualquier ruta ya
existente. El siguiente bloque prepara datos sintéticos; no apunta a repos reales:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python -m examples.managed_demo /private/tmp/harness-ui-demo
export HARNESS_DEMO_ROOT=/private/tmp/harness-ui-demo
export HARNESS_DATABASE_URL=sqlite:////private/tmp/harness-ui-demo/index.sqlite3
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline alembic upgrade head
npm --prefix frontend run build
HARNESS_MANAGED_CONFIG=examples.managed_demo:build UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline uvicorn harness_local.api.app:create_app --factory --host 127.0.0.1 --port 8015 --workers 1
```

Abrir `http://127.0.0.1:8015`. Copiar el contenido de `task.md` del área al
formulario (Tarea `P001-T001`, Fase `P001`). Los proyectos de la demo son:

| Proyecto | Comportamiento |
|---|---|
| `task` | Worktree separado de `source`; ejecutor modifica `app/main.txt`, revisor ACCEPT y tests falsos. Permite commit Git real. |
| `recovery` | Igual, pero la primera revisión falla con JournalError. Confirmar escritor detenido, revalidar y hacer commit. El fallo no se repite tras reinicio. |
| `legacy` | Copia del fixture accepted; rechaza ejecución hasta activar con vista previa. Permite revertir con motivo y confirmación. |

`calls.jsonl`, fuera de los checkouts, registra roles/IDs sintéticos; permite
comprobar que recuperar no repite el ejecutor. `recovery-injected` conserva el
fallo inyectado; no es un artefacto del producto. SQLite y copias `migrations/`
están fuera de los checkouts. Se ejecutó este procedimiento con la ruta nueva
`/private/tmp/h2-ui-demo-1012`. Para repetir desde cero, preparar otra ruta; no
borrar ni reutilizar históricos inadvertidamente. Para reiniciar, conservar las
mismas variables/base y lanzar solo Uvicorn, sin volver a preparar.

Para Vite, usar los comandos existentes del README y el puerto backend de su
proxy; el recorrido verificado aquí usa los assets compilados servidos por Uvicorn.

## Configuración real: composición documentada, no activada

Una configuración independiente podría registrar `ManagedProject` con contexto,
perfil y política explícitos, fijar las versiones y aportar `ports_factory` y
`commit_factory` a `ManagedConfig`. El cliente nunca suministra estas decisiones.

Para H2.3, construir dos `CLIConfig` con ejecutables absolutos, versiones
compatibles, timeout, herramientas permitidas y entorno completo explícito; crear
`CLIProcessAdapter(configs, artifact_root)` con artefactos fuera del checkout.
Incorporar `frozen_versions()` a las versiones del proyecto y comprobarlas en
cada factory. HOME/PATH/TMPDIR/LANG/USER requieren configuración deliberada;
D024 describe la validación local de USER, sin leer ni heredar credenciales.
La factory debe devolver agente, runner de comandos explícitamente autorizado
y capturador Git. El supervisor vincula el journal de procesos del adaptador;
no sustituirlo por invocaciones directas desde HTTP.

Para H2.4, preparar el worktree con `GitWorktrees.prepare` antes de registrarlo;
inyectar `GitWorkspace(GitIdentity(nombre, correo))` como capturador y escritor
mediante `commit_factory`, con las mismas versiones. La confirmación HTTP solo
admite contenido revisado, sin actualizaciones mecánicas. Un runner falso no
certifica validaciones reales. Activar `supervisor=True` y proveedores requiere
una autorización de ejecución propia: la demo nunca importa `CLIProcessAdapter`,
no hace preflight/login y no aprovecha consentimientos de smokes agotados.

## Verificación y evidencia

- Suite completa: **308 pruebas pytest, 121 subtests**, incluidos 20 casos de API
  gestionada. Dos nuevos casos verifican preparación conservadora de la demo y
  recuperación tras reiniciar con un solo ejecutor y un commit. El recorrido API
  existente verifica ahora diff/review/tests y fingerprint de la proyección.
- **3 tests Node** sin dependencias nuevas: doble envío tras respuesta inmediata,
  sobre pendiente exacto ante red fallida/relectura y cabecera CSRF/diagnóstico 409.
  Comando: `node --test frontend/tests/managed-api.test.mjs` (Node fijado 24.15.0).
- **12 checks ligeros**, exportación OpenAPI/tipos, TypeScript y build Vite pasan.
  Esquema `0007_managed_activation` conservado; upgrade en SQLite sintética y
  pruebas existentes de migraciones/OpenAPI pasan. Aviso conocido Starlette/HTTPX.
- Chrome sobre UI compilada: doble clic al encolar → un run, dos intentos,
  ACCEPTANCE_READY, diff legible y commit con doble clic → COMMITTED. 24 eventos.
  Reinicio SIGTERM/Uvicorn con la página abierta muestra desconexión y vuelve al
  mismo run/commit/cursor sin duplicados.
- Chrome: cuarentena en review, motivo y confirmación explícita, revalidación →
  ACCEPTANCE_READY con ejecutor COMPLETED, review anterior INTERRUPTED y nueva
  review COMPLETED; commit posterior → COMMITTED y 36 eventos. Captura visual
  inspeccionada con diff y checkpoint; acciones posteriores al commit deshabilitadas.
- Chrome: legacy rechaza con `409 · mode_refused` visible; vista previa → ACTIVE;
  reversión explícita → REVERTED, y nueva ejecución rechazada sin run creado.
- Inspección independiente de SQLite: 2 runs COMMITTED; 5 jobs (4 DONE, uno
  INTERRUPTED); 2 commits, cero locks; activación REVERTED. Auditoría externa:
  `executor, reviewer` para task; `executor, reviewer, reviewer` para recovery.
  Los SHA de commit son `c09e2dcb2f0032bfa16fc1af26a13ba892d8e38b` y
  `803ebdc750963f0ab3826533e506c55665f523ff`, respectivamente.
- Conflictos de versión, acciones duplicadas, páginas de eventos y rechazos de
  modo cubiertos por API; presentación del 409 por cliente Node y rechazo de modo
  también en navegador. No se inyectó una carrera de versión en Chrome.
- Servicio temporal y pestaña cerrados al terminar. Diff y whitespace revisados.
  Sin proveedores, agentes de colaboración, smokes, red externa, ReferenceProject,
  configuración global ni push; el harness no se usó para desarrollar el repo.

## Límites conservados

Guardia solo gestionada; sesión local y guardia H0/H1 pendientes (D029). Un hilo
supervisor, exclusión cooperativa, sin garantía frente a otros escritores/bases.
Eventos acumulados en memoria de la pantalla y detalle de ciclos completo, sin
virtualización ni benchmark de historiales enormes; SSE gestionado pendiente.
La clave se conserva en sessionStorage, no sobrevive a cerrar/borrar la sesión
ni deduplica acciones de pestañas independientes. Activación síncrona; tokens y
versiones siguen siendo autoridad del servidor. Fakes no acreditan proveedores,
cuota ni permisos vivos. Sin integración de rama, fases, prompts versionados,
registro de proyectos por HTTP, cancelación por UI ni distribución.

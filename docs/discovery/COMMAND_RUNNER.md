# Ejecutor de comandos de validación de producto

Incremento elegido por el usuario el 2026-10-13. [Alcance previo y criterios](COMMAND_RUNNER_SCOPE.md).
D047. Implementación POSIX `commands-1`, activada exclusivamente por composición.

## Composición y autoridad

`adapters.commands.CommandConfig` exige checkout canónico existente, confianza
explícita (`repository_trusted=True`), autorizaciones de `Command` completos,
ejecutables absolutos y entorno completo. Las autorizaciones comparan argv, cwd,
entorno específico y timeout; ni un prefijo ni una concesión H3.2 las sustituyen.
El mapa resuelve únicamente argv[0]; no busca ejecutables en PATH. PATH sí puede
ser usado por scripts/hijos y debe declararse. No se heredan HOME, credenciales,
variables ni configuración del entorno del servicio.

El servidor compone `ManagedCommandRunner(config)` como segundo puerto de
`ports_factory(context, versions)` junto al agente y capturador Git que haya
configurado. Debe crear un runner nuevo por job y añadir `frozen_versions()` a
las versiones del `ManagedProject` **antes de admitir** el run. `ManagedConfig`
y el supervisor conservan sus valores predeterminados desactivados. No hay
nuevo comando CLI, descubrimiento automático de programas ni factory de
proveedores incluida en esta entrega.

Ejemplo parcial de composición de biblioteca, con rutas elegidas por el operador
(no es una configuración lista para un proyecto real):

```python
from harness_local.adapters.commands import CommandConfig, ManagedCommandRunner

config = CommandConfig(
    checkout=str(context.root),
    repository_trusted=True,
    authorized_commands=context.profile.preparation + context.profile.validations,
    executables=(("node", "/ruta/absoluta/node"), ("npm", "/ruta/absoluta/npm")),
    environment=(("PATH", "/ruta/absoluta/bin:/usr/bin:/bin"),
                 ("HOME", "/ruta/privada/home"), ("CI", "true")),
    max_timeout_seconds=1800,
    max_output_bytes=65536,
)
versions = {**existing_versions, **ManagedCommandRunner(config).frozen_versions()}
# En la ports_factory explícita:
# return configured_agents, ManagedCommandRunner(config), configured_git
```

El supervisor enlaza el journal también para checks de fase. La configuración
entera tiene hash, con versión `commands-1`. La discrepancia se rechaza antes de
comandos/agentes; no se actualizan snapshots ni se reinterpreta un antiguo
`commands=synthetic-1`. El spec persistido guarda argv/cwd/límites, clave de
configuración, claves/hash del entorno efectivo y autorización exacta. Los
valores del entorno base no se publican en eventos: la composición original es
necesaria para ejecutar de nuevo con el mismo hash. Los binarios no se versionan
por hash de contenido; versiones y confianza de herramientas/scripts externos
siguen siendo responsabilidad de esa composición.

Los comandos de contrato pasan además por la política de prefijos existente.
Una orden textual del contrato usa los valores por defecto de `Command`; no se
convierte silenciosamente en otra orden de perfil con diferente timeout/entorno.
Si se desea autorizar esa variante se debe declararla exactamente. La confianza
en el repositorio incluye código que cambie dentro del contrato, scripts, hooks
y configuración externa que las herramientas puedan cargar. Autorizar npm no
concede herramientas a un agente ni acceso a red por dominio. El runner no
implementa filtrado físico de archivos/red; el operador solo debe conectar
programas confiables compatibles con ejecución nativa. `npm run` puede usar una
shell por decisión de npm; el adaptador siempre lanza argv, nunca shell implícita.

## Persistencia, captura y recuperación

Reutiliza el journal `managed_events`, propietario/lease del job, exclusión del
checkout, `process_gate.py`, `identity/liveness/stop_group` y recuperación H2.3.
Los comandos tienen command_id propio, sin fingir un intento de agente ni añadir
otra cola o tabla. La proyección de `command_process_intent/spawned/finished`
permite consultar `repository.command_processes(job_id)`.

Orden: `command_started` → intención con spec → gate POSIX en sesión nueva →
identidad persistida → GO → bytes/resultados. Python del gate usa `-I -S` para
no cargar configuración Python del entorno antes de GO. EOF antes de GO evita
el exec. Un command_id solo admite una intención. El gate no es un aislamiento
frente al dueño del proceso.

Captura no bloqueante por selectores y stdin cerrado. Por defecto conserva hasta
64 KiB **por stream**, configurable entre 1 byte y 1 MiB. Los fragmentos exactos
(base64, offset, SHA-256) se confirman en SQLite durante la lectura. Al alcanzar
el límite con más datos termina el grupo y marca truncamiento; nunca devuelve
éxito por una captura truncada. Los fragmentos sobreviven a una caída antes del
resultado o checkpoint. No hay archivos de captura externos ni nueva retención.

El resultado conserva exit observado (null si no se lanzó), duración monotónica
del adaptador (incluye gate, drenaje y cancelación, no CPU ni tiempo por test),
stdout/stderr decodificados con sustitución UTF-8, timeout y error. `capture_json`
enlaza command_id, estado del grupo y, por stream, bytes leídos/guardados, hash
del prefijo, EOF, truncamiento e integridad de captura. `observed_bytes` solo
cuenta lo leído, no estima lo que el proceso pudo escribir. Sin EOF, la salida
es incompleta; sin resultado tras caída, solo existen fragmentos sin sellar.
El exit no cero sigue siendo fallo aunque no haya excepción de sistema.
El límite acota bytes por stream; las copias en eventos/historial y metadatos
dependen de la fragmentación. No representa una cuota física de SQLite.

Timeout aplica al comando solicitado dentro del techo configurado. TERM/KILL
señalan solo el grupo del handle creado en esta llamada; espera y drenaje están
acotados (0,3 s por defecto, máximo 2 s cada uno). No hay límite físico de CPU,
memoria, disco ni red. Un líder terminado con hijos vivos produce fallo y
limpieza del grupo; si sigue vivo/desconocido, se aborta el motor con
`JournalError`, se mantiene el lock y no se ejecuta el siguiente comando/agente.
Errores de journal también se propagan, sin convertirlos en tests ordinarios.

Caída/reinicio o lease vencido mantienen `RECOVERY_REQUIRED`. La acción existente
`confirm_stopped`, con job/token/versión/motivo, exige propietario cerrado o
observado ausente y todos los grupos ausentes. También mira los nuevos comandos.
Host distinto, permisos insuficientes o un PID reutilizado vivo bloquean la
liberación. **La recuperación no envía señales a PIDs persistidos, no relanza y
no adopta validaciones parciales.** El operador verifica/detiene externamente el
proceso correcto; después confirma la ausencia. Revalidar necesita una nueva
acción explícita. Intenciones/resultados anteriores se conservan.

Garantía cooperativa de grupos POSIX locales: no cubre demonios, hijos con
`setsid`, procesos lanzados mediante un servicio externo ni código hostil del
mismo UID. Esas herramientas no son compatibles con esta composición. No se
amplía D017 para prometer aislamiento físico ni exactamente una vez.

## Evidencia y compatibilidad

Preparación, validaciones y JUnit usan los puertos existentes. Una captura con
metadatos nuevos exige ambos streams completos y grupo muerto para acreditar
éxito. JUnit conserva original/hash/frescura, command_id y vínculo al intento y
árbol exacto. ACCEPT no supera fallos deterministas ni cambios durante/después
de validar. El commit usa la intención y CAS H2.4, sin otra vía de aceptación.

Codec 7 solo para historiales con captura nativa (incluida preparación); formatos
1–6 siguen leyéndose y serializándose sin añadir campos a resultados anteriores.
`capture_json=null` se omite de ciclos antiguos. No se cambia contexto, contrato,
prompts ni permisos congelados. Esquema `0013_bootstrap`, CLI `cli-4` y locks de
dependencias conservados. La API ya entrega resultados/eventos extensibles;
sin nuevos endpoints, tipos OpenAPI ni interfaz.

Backup conserva eventos/bytes/resultados en SQLite y lee codec 7. Backup y
retención incluyen identidades de validadores en sus comprobaciones de parada;
no eliminan estos eventos. Restaurar conserva su guardia de consulta y no activa
trabajo. Bundles anteriores con el mismo esquema siguen admitidos.

## Verificación offline

`tests/product/test_commands.py` y `command_supervisor_probe.py` añaden 39 casos:

- argv literal, cwd, entorno explícito, bytes no UTF-8, exit/duración, ejecutable
  ausente, timeout incluso con pipes cerrados, exceso en cada stream;
- confianza/autorización/límites/configuración antigua o cambiada rechazados,
  ausencia de ejecución sin journal y valores predeterminados deshabilitados;
- fallos del journal en intención, identidad, bytes y resultado; no efectos
  antes de identidad persistida ni llamadas posteriores al fallo;
- hijos que sobreviven al líder con pipes abiertos/cerrados, grupo incierto,
  propietario abierto, identidad viva/desconocida y prohibición de repetir id;
- supervisor en proceso independiente cae realmente tras un fragmento persistido,
  validador sigue vivo, vence lease, reinicia repositorio/supervisor sin duplicar;
  confirmación rechazada hasta terminar el grupo sintético desde la prueba;
- Node/npm/TypeScript reales offline en worktree Git/SQLite temporales: preparación,
  tipos/tests/build, JUnit, agentes falsos, aceptación/commit exactos, reinicio y
  backup/restauración. Variantes con tests/tipos fallidos y edición posterior;
- parada para mantenimiento y roundtrip de históricos anteriores.

Reproducción focal, sin red ni proveedores:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q tests/product/test_commands.py
```

La fixture TypeScript utiliza la caché npm ya disponible y `npm ci --offline
--ignore-scripts --no-audit --no-fund`, con HOME/npmrc temporales; no usa el
checkout de desarrollo como proyecto gestionado. No se instala nada con red.
Regresión final: 810 pruebas pytest y 121 subtests, 12 checks ligeros y seis
pruebas Node correctos. Esquema/OpenAPI verificados por la suite; 196 enlaces
locales y diff revisados. Detalle en STATE. No se hizo nueva QA visual ni
verificación del wheel instalado.

Pendientes: composición completa de uso real, piloto/proveedores con autorización
nueva, QA visual previamente bloqueada, aislamiento físico, otras plataformas,
benchmark y retención de capturas SQLite. No se inicia ninguna de estas tareas.

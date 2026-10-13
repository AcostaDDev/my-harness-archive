# Revisión independiente del ejecutor de validaciones (D047)

Realizada el 2026-10-13 en sesión manual de Claude Code sobre `c3f941b`, Git
limpio, a petición del usuario. Contrasta D047, la [entrega](COMMAND_RUNNER.md),
el [alcance previo](COMMAND_RUNNER_SCOPE.md), el código y las 39 pruebas.
Sin subagentes, proveedores, red ni harness de desarrollo. D048.

## Alcance revisado

`adapters/commands.py`, `process_gate.py`, `processes.py`, el journal del
supervisor (`services/managed.py`), la proyección `storage/command_processes.py`,
`command_process_event`/`_processes_stopped`/`finish`/`confirm_stopped`, codec de
historial, payloads de validación, comprobaciones de parada de backup/retención
y `tests/product/test_commands.py` con su sonda de caída.

## Hallazgo corregido

**Sustitución silenciosa del runner congelado (medio).** `bind_process_journal`
rechazaba un `ManagedCommandRunner` con configuración distinta o un run sin la
identidad `commands-1`, pero no el caso inverso: un run admitido con
`command_config_sha256` cuya `ports_factory` devolviera después otro runner sin
journal (p. ej. tras cambiar la composición y reiniciar el servicio). El
supervisor ejecutaba preparación/validaciones con ese runner y el historial
seguía declarando la configuración nativa congelada. Reproducido con una prueba
que terminaba el job sin error.

Corrección: `_bind_commands` en el supervisor, usado por la tarea normal y por
el check de fase. Si las versiones congeladas incluyen `command_config_sha256`,
un runner sin `bind_process_journal` produce `JournalError` antes de cualquier
efecto: cuarentena `RECOVERY_REQUIRED`, sin llamadas a runner/agentes ni
intenciones de comando. Runs sin esa clave conservan el comportamiento anterior.
Prueba nueva `test_frozen_native_configuration_never_runs_with_another_runner`.

## Criterios contrastados sin hallazgos

- **Ventana intención/identidad/GO.** `command_started` → intención (antes de
  `Popen`) → gate en sesión nueva con `-I -S` → identidad persistida → GO.
  Fallo al persistir la identidad: el gate no recibe GO, se detiene su grupo
  vivo y queda intención PENDIENTE que exige propietario cerrado/muerto. Caída
  del padre antes de GO: EOF en el pipe del gate, sin exec. El extremo de
  escritura no es heredable. Ejecutable ausente: `finished` sin identidad,
  STOPPED, sin objetivo ejecutado.
- **Conservación de exclusión.** Errores no OSError del bucle, del journal o de
  `BaseException` detienen el grupo propio y se propagan; grupo vivo/incierto
  emite `finished` UNCERTAIN y aborta. `finish` y `confirm_stopped` recorren los
  comandos del job: identidad con grupo no muerto, o intención pendiente con
  propietario vivo, bloquean el lock. No se señalizan PIDs recuperados.
- **Captura.** Límite por stream respetado, truncamiento termina el grupo,
  EOF ausente o grupo no muerto impiden `passed`; `capture_json` ilegible
  tampoco acredita éxito.
- **Compatibilidad.** Formatos 1–6 se serializan igual (prueba de roundtrip);
  `capture_json=None` se omite en historial, preparación, eventos y API. En
  codec 7 sin JUnit se descartan `command_id/run_id/source_attempt_id` como en
  formatos anteriores: en producción solo existen con reportes declarados
  (`run_validations`), y el vínculo queda en `capture_json.command_id`. Sondeo
  artificial descartado como hallazgo.
- **Rutas del supervisor.** Solo tarea normal y check de fase obtienen el runner
  de comandos; chat, discovery, bootstrap, exportación, cierre y commit no
  ejecutan comandos.

## Observaciones no corregidas (sin cambio de diseño)

- Liveness por PGID sin instante de arranque, igual que agentes H2.3: un PGID
  reutilizado por un grupo ajeno puede bloquear `finish`, confirmación, backup o
  retención (falso positivo conservador). Backup/retención revisan todos los
  comandos históricos; el coste es pequeño, el bloqueo improbable pero posible.
- Tras fallar el heartbeat, un validador silencioso sigue hasta su timeout
  (techo configurable hasta 24 h) y su resultado no se persiste. La exclusión se
  conserva; es coste, no inseguridad. Mismo patrón que el adaptador CLI.
- `bind_process_journal` compara el hash de configuración, no el contenido de
  binarios: ya documentado como responsabilidad de la composición.

## Verificación

- Prueba nueva fallaba antes de la corrección (`DID NOT RAISE JournalError`) y
  pasa después. Focal: 40 pruebas del ejecutor correctas.
- Regresión completa: **811 pruebas pytest y 121 subtests correctos**, aviso
  Starlette/HTTPX conocido. **12 checks ligeros y 6 pruebas Node correctos.**
- Sin cambios de esquema (`0013_bootstrap`), codec, cli-4, OpenAPI, UI,
  dependencias ni empaquetado; no se regeneraron tipos ni wheel.
- Sin proveedores, smokes, login, red, configuración global, ReferenceProject,
  subagentes ni harness de desarrollo. SQLite de trabajo intacta.

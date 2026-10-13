# Propuesta del smoke de la matriz D052 con proveedores

Preparada el 2026-10-13 sobre `1eb5847`, con Git limpio en `main`. D055.
**No ejecutada ni autorizada.** Ejecutarla exige un consentimiento específico y
explícito del usuario para esta propuesta. D025, D050 y los consentimientos
anteriores están agotados y no se trasladan.

Lo que se prueba es la entrega D052 (`cli-5`, `local-config-2`,
[entrega](AGENT_ROLES.md)) con proveedores reales. Son las cuatro combinaciones
revisor → ejecutor, cada una con su propio checkout desechable, su TOML y su
servicio. Recorrido por combinación: el revisor planifica, el ejecutor edita, se
validan los cambios, el revisor revisa y se hace el commit. Los puntos nuevos
que se quieren confirmar son tres:

- Codex como escritor en `workspace-write` sin red.
- Claude como lector con `--json-schema`, `--tools Read,Glob,Grep` y `--restricted`.
- Los esfuerzos de Codex, inferidos del binario.

## Selecciones del usuario

El usuario las eligió el 2026-10-13 en esta sesión, respondiendo a preguntas explícitas:

- **Matriz:** las cuatro combinaciones.
- **Recorrido:** planificar, ejecutar y revisar (`planning_mode = "agent"`) y
  después el commit, que no usa proveedor. Sin check ni cierre de fase.
- **Modelos y esfuerzos:** los de D050. Codex `gpt-6-luna` y Claude
  `claude-sonnet-4-6`. El revisor, que también planifica, usa `medium`; el
  catálogo del ejecutor, `low`.
- **Fallos:** un fallo detiene solo su combinación, sin reintentarla; las demás
  continúan.

| # | Área (`BASE/…`) | Revisor y planificador | Ejecutor (catálogo) | Invocaciones máx. |
|---|---|---|---|---:|
| 1 | `codex-claude` | Codex 0.162.1 `gpt-6-luna`/`medium` | Claude 2.1.296 `claude-sonnet-4-6`/`low` | 3 |
| 2 | `codex-codex` | Codex 0.162.1 `gpt-6-luna`/`medium` | Codex 0.162.1 `gpt-6-luna`/`low` | 3 |
| 3 | `claude-claude` | Claude 2.1.296 `claude-sonnet-4-6`/`medium` | Claude 2.1.296 `claude-sonnet-4-6`/`low` | 3 |
| 4 | `claude-codex` | Claude 2.1.296 `claude-sonnet-4-6`/`medium` | Codex 0.162.1 `gpt-6-luna`/`low` | 3 |

El orden va de menos a más novedad: planificador Codex, escritor Codex, lector
Claude y, por último, ambos a la vez. Así es más fácil atribuir un fallo.

## Ajustes de preparación decididos con criterio

- **`executor_mode = "catalog"`** con un solo modelo y un solo esfuerzo. El
  revisor no puede elegir otro modelo, de modo que el coste queda acotado. El
  modo `open` sigue verificado solo offline.
- **Claude 2.1.296** fijado por la ruta versionada
  `~/.local/share/claude/versions/2.1.296` y con `DISABLE_AUTOUPDATER=1`. Es la
  versión a la que apunta el enlace del usuario y la que D052 admitió por
  ayuda idéntica; aún no tiene uso real (D050 usó 2.1.295). Si el archivo
  desaparece, no se sustituye por otra versión.
- **Timeouts:** revisor 600 s y ejecutor 900 s, sea cual sea el proveedor.
- **Validaciones propuestas por el planificador.** El planificador puede
  devolver `npm run check|test|build` como `validation_commands`. Ese argv, sin
  timeout explícito, produce `Command(argv)` con 1800 s, que no coincide con la
  variante del perfil (120 s). Por eso el TOML autoriza esas tres variantes
  exactas con `timeout_seconds = 1800` y `max_timeout_seconds = 1800`. Además,
  el `NEXT_STEPS` del checkout pide no añadir validaciones. Si el planificador
  propone cualquier otro argv, no está autorizado: su validación falla y la
  combinación no llega a `ACCEPTANCE_READY`.
- **Una fase por combinación.** Se crea `P001` porque el run exige `phase_id`.
  Su tag (`matrix-<par>-p001`) se declara pero no se usa: no hay check ni cierre.
- **Áreas aisladas.** Cada área tiene su checkout, su TOML, su SQLite, sus
  artefactos, su `cli-tmp`, su `command-home` y una copia propia de
  `.local/npm-cache` (177 MB, unos 0,7 GB en total). Ninguna evidencia se mezcla.
- **Operación desde el wheel (D051).** Se usa un único paquete y venv en
  `BASE/package` y `BASE/venv` para las cuatro combinaciones.

## Preparación (sin proveedores ni red)

[`examples/provider_matrix/prepare.sh`](../../examples/provider_matrix/prepare.sh)
(SHA-256 `94db751b6cc5ecc8a37b1848d7ca8d44f4000379aae89f2333f2b58fc2993376`)
falla si `BASE` existe. Para cada combinación crea `BASE/<revisor>-<ejecutor>`
con lo siguiente:

- **`web`:** copia de la fixture `typescript_web` más `docs/STATE.md` y
  `docs/NEXT_STEPS.md`, con la tarea `P001-T001`: el mismo contrato que D050,
  `Executor: <modelo del catálogo> / low` y «Validation commands: ninguno
  adicional». Lleva un commit base y otro con la regresión deliberada
  `tasks * 45`; la identidad Git va por `-c`.
- **`operator/harness-local.toml`** con permisos 0600, más `state`, `cli-tmp`,
  `command-home` (npmrc vacíos) y `npm-cache`. Los directorios privados son
  0700 y el checkout, 0755.

TOML de la combinación 4 con `BASE=/private/tmp/harness-provider-matrix`:

```toml
# Smoke de la matriz D052: revisor claude → ejecutor codex. Archivo del operador; sin secretos.
format = "local-config-2"

[service]
state_dir = "/private/tmp/harness-provider-matrix/claude-codex/state"
supervisor = true

[git]
executable = "/usr/bin/git"
author_name = "Harness Provider Matrix"
author_email = "matrix@example.invalid"

[agents.reviewer]
provider = "claude"
model = "claude-sonnet-4-6"
effort = "medium"
executable = ["$HOME/.local/share/claude/versions/2.1.296"]
cli_version = "2.1.296"
timeout_seconds = 600
environment = { HOME = "$HOME", USER = "acosta", PATH = "/usr/bin:/bin", TMPDIR = "/private/tmp/harness-provider-matrix/claude-codex/cli-tmp", LANG = "C.UTF-8", DISABLE_AUTOUPDATER = "1" }

[agents.executor]
provider = "codex"
executable = ["$HOME/.nvm/versions/node/v24.15.0/bin/codex"]
cli_version = "0.162.1"
timeout_seconds = 900
environment = { HOME = "$HOME", USER = "acosta", PATH = "$HOME/.nvm/versions/node/v24.15.0/bin:/usr/bin:/bin", TMPDIR = "/private/tmp/harness-provider-matrix/claude-codex/cli-tmp", LANG = "C.UTF-8" }

[[projects]]
id = "matrix-claude-codex"
root = "/private/tmp/harness-provider-matrix/claude-codex/web"
repository_trusted = true
profile = "typescript-web"
tag_kind = "lightweight"

[projects.policy]
planning_mode = "agent"
executor_mode = "catalog"
executor_models = ["gpt-6-luna"]
executor_efforts = ["low"]
max_revision_cycles = 0

[projects.commands]
authorize_profile_commands = true
executables = { node = "$HOME/.nvm/versions/node/v24.15.0/bin/node", npm = "$HOME/.nvm/versions/node/v24.15.0/bin/npm" }
environment = { PATH = "$HOME/.nvm/versions/node/v24.15.0/bin:/usr/bin:/bin", HOME = "/private/tmp/harness-provider-matrix/claude-codex/command-home", TMPDIR = "/private/tmp/harness-provider-matrix/claude-codex/command-home", LANG = "C.UTF-8", CI = "true", npm_config_cache = "/private/tmp/harness-provider-matrix/claude-codex/npm-cache", npm_config_userconfig = "/private/tmp/harness-provider-matrix/claude-codex/command-home/user.npmrc", npm_config_globalconfig = "/private/tmp/harness-provider-matrix/claude-codex/command-home/global.npmrc", npm_config_update_notifier = "false" }
max_timeout_seconds = 1800
max_output_bytes = 65536

# Variantes exactas que el planificador puede proponer como validation_commands
# (argv sin timeout → 1800 s por defecto). Otro argv no está autorizado: su validación falla.

[[projects.commands.authorized]]
argv = ["npm", "run", "check"]
timeout_seconds = 1800

[[projects.commands.authorized]]
argv = ["npm", "run", "test"]
timeout_seconds = 1800

[[projects.commands.authorized]]
argv = ["npm", "run", "build"]
timeout_seconds = 1800
```

Las otras tres combinaciones solo difieren en esto:

- El área de todas las rutas y el `id` del proyecto (`matrix-<par>`).
- Los bloques `[agents.*]` según el proveedor:
  - Codex: ejecutable `codex` de nvm, 0.162.1 y `PATH` con Node.
  - Claude: 2.1.296 versionado, `PATH` mínimo y `DISABLE_AUTOUPDATER`.
  - Un ejecutor Claude añade `tools` y `allowed_tools` `Read, Edit, Write, Glob, Grep`,
    sin `Bash` ni concesiones.
- `executor_models`: el modelo del proveedor ejecutor.

La autenticación sigue en cada CLI. El archivo no lleva credenciales,
selectores ni fuentes heredadas.

## Ensayo offline realizado

Hecho en el scratchpad de la sesión, con `BASE` allí y no en `/private/tmp/harness-provider-matrix`:

1. **Preparación.** `prepare.sh` terminó completo: cuatro áreas, dos commits
   por checkout y árboles limpios.
2. **Wheel (D051).** `build_distribution.py --out-dir` y `check_distribution.py`
   correctos (wheel aislado). Venv nuevo con `uv venv`, `uv pip sync
   --require-hashes` y el wheel `--no-deps`, todo `--offline`.
3. **`check-config` desde el venv instalado:** válido en las cuatro.

   | Combinación | `local_config_sha256` (BASE del ensayo) |
   |---|---|
   | `codex-claude` | `21de4f5f…` |
   | `codex-codex` | `377cbe48…` |
   | `claude-claude` | `05308531…` |
   | `claude-codex` | `bf59407a…` |

   Las versiones congeladas son `cli-5`, `local-config-2` y `commands-1`, con
   `reviewer_provider`/`executor_provider` y las CLI esperadas. La
   planificación usa la selección del revisor (`medium`). El vocabulario del
   ejecutor es el de su proveedor. Los hashes cambian con `BASE`: la ejecución
   real registra los suyos.
4. **`check-config --preflight` desde el venv** (solo versión y ayuda, sin
   autenticación ni consumo): `version_help_match` en los ocho agentes, sin
   flags ausentes. Codex `0.162.1`, help `df0d864c…`; Claude `2.1.296`, help
   `550db4f8…`. El lector Claude exige y encuentra `--restricted` y
   `--json-schema`.
5. **Admisión en proceso** con la composición del TOML y el supervisor forzado
   a `false`, tras `init-db` del venv:
   - Fase `P001` creada, job y run `QUEUED`, sin intentos ni procesos.
   - `planning_mode = "agent"`.
   - Las tres variantes `npm run check|test|build` de 1800 s están entre los
     comandos autorizados del runner congelado.
   - `cli-tmp` vacío y checkouts sin cambios.
6. **Comandos del perfil** en una copia del checkout 4, con el entorno exacto
   del TOML (`env -i`): `npm ci --offline` 0, `check` 0, `build` 0 y `test` 1
   (fallan 2 de 3 tests por la regresión). La tarea es real y la caché copiada basta.

No se ejecutó `serve` ni ninguna invocación de proveedor más allá de versión y
ayuda. Sin red ni consumo. El área del ensayo se descarta: la ejecución real
crea una nueva.

## Ejecución propuesta (solo con consentimiento específico)

Se ejecuta fuera del sandbox, porque necesita bind loopback y que las CLI
accedan a su autenticación y a la red. Es una sola ejecución de la matriz.

**Paso 0, común a todas las combinaciones:**

1. `sh examples/provider_matrix/prepare.sh /private/tmp/harness-provider-matrix`.
   Si la ruta existe, se elige otra nueva y se registra.
2. `build_distribution.py --out-dir BASE/package` y
   `check_distribution.py --dist BASE/package`.
3. Venv `BASE/venv`: `uv venv`, `uv pip sync --require-hashes` del
   `requirements.txt` del paquete y el wheel `--no-deps`, offline.

**Para cada combinación, en el orden 1 → 4,** con `A=BASE/<par>` y los binarios
de `BASE/venv/bin`, ejecutados desde `BASE`:

1. `harness-local check-config A/operator/harness-local.toml --preflight`.
   Tiene que dar `version_help_match` en el revisor y en el ejecutor, con las
   versiones de la tabla.
2. `harness-local init-db --database A/state/harness.sqlite3` y después
   `harness-local serve --database A/state/harness.sqlite3 --config A/operator/harness-local.toml`
   en el puerto 8013.
3. Sesión con la clave del archivo privado anunciado, `X-Harness-Local: 1` y
   Host/Origin loopback.
4. `POST /api/managed/projects/matrix-<par>/phases` con estos datos:
   - Código `P001` y objetivo «Restaurar la estimación de treinta minutos por tarea».
   - Criterios: P001-T001 `COMMITTED` y alcanzable desde HEAD; check, test y
     build pasan sobre HEAD; STATE y NEXT_STEPS sin cambios.
   - Tareas `["P001-T001"]` y tag `matrix-<par>-p001`.
5. `POST …/runs` con `P001-T001`, `P001` y el texto de `docs/NEXT_STEPS.md`.
   El supervisor prepara (`npm ci`) y encadena tres invocaciones: el
   **revisor planifica** y elige ejecutor dentro del catálogo; el **ejecutor**
   edita; se ejecutan las validaciones check/test/build con JUnit (más las
   variantes del planificador, si las propone); y el **revisor revisa**. Se
   espera `ACCEPTANCE_READY`.
6. Acción `commit` con `expected_version`. Se espera `COMMITTED`: un solo commit
   sobre el de la regresión que cambia únicamente `src/estimate.ts`. No usa proveedor.
7. Instantánea por API de run, intentos, procesos y comandos. Después se
   detiene el servicio con TERM y se comprueban las evidencias. El puerto
   queda libre para la siguiente combinación.

## Qué confirma cada combinación

| Comprobación | 1 C→Cl | 2 C→C | 3 Cl→Cl | 4 Cl→C |
|---|:-:|:-:|:-:|:-:|
| Composición `cli-5`/`local-config-2` real y reparto congelado | ✓ | ✓ | ✓ | ✓ |
| El revisor planifica con su propia selección y elige ejecutor del catálogo | ✓ | ✓ | ✓ | ✓ |
| Planificador y revisor Codex en sandbox `read-only` | ✓ | ✓ | | |
| **Codex escritor:** `workspace-write`, `network_access=false`, `approval_policy="never"` | | ✓ | | ✓ |
| **Claude lector:** `--json-schema` bajo `--tools Read,Glob,Grep` y `--restricted` | | | ✓ | ✓ |
| Claude 2.1.296 como escritor | ✓ | | ✓ | |
| **Esfuerzos Codex:** `medium` (revisor) y `low` (ejecutor) aceptados con `gpt-6-luna` | `medium` | ambos | | `low` |

En detalle:

- **Codex escritor (2 y 4).** El intento del ejecutor tiene que terminar
  `complete` y con exit 0, y su argv congelado debe contener `--sandbox
  workspace-write` y `-c sandbox_workspace_write.network_access=false`. Se
  esperan eventos `item.*`/`file_change` sobre `src/estimate.ts`, y el último
  `agent_message` tiene que ser el JSON `{"result": …}`. La aceptación debe
  quedar elegible con `changed_paths = ["src/estimate.ts"]`. Si Codex ejecuta
  comandos (`command_execution`), se registran como observados. La ausencia de
  red no se certifica: solo consta la configuración solicitada.
- **Claude lector (3 y 4).** El planificador y el revisor tienen que terminar
  `complete`. Su argv congelado debe contener `--tools Read,Glob,Grep`,
  `--allowedTools Read,Glob,Grep`, `--restricted` y `--json-schema` con la
  identidad del rol. El `structured_output` debe aceptarse como contrato del
  planificador, con todos sus campos, y como review (`task_id`, `verdict`). Sin
  `permission_denials` que impidan leer. El checkout no cambia tras la
  planificación, y tras la revisión el diff es igual al del ejecutor.
- **Esfuerzos Codex.** Solo se confirman los valores usados (`medium`, `low`)
  con `gpt-6-luna`. `minimal`, `high`, `xhigh`, `max` y `ultra` siguen
  inferidos del binario.
- **Todas.** Sesiones nuevas por invocación. Uso y modelo **reportados**
  separados de lo solicitado (Codex no reporta el modelo). Comandos `commands-1`
  con la configuración congelada y JUnit con hash. Review ACCEPT ligada al
  contenido exacto.

## Límites de consumo

- Como máximo **tres invocaciones de proveedor por combinación**: planificador,
  ejecutor y revisor. Son **doce en total**: seis de Codex y seis de Claude si
  se completan todas. `max_revision_cycles = 0`, así que un REVISE termina en
  `revision_limit`, sin corrección automática.
- No están autorizados: `retry_executor`, `revalidate`, runs nuevos, check o
  cierre de fase, lote, chat, bootstrap, reconciliación, concesiones de
  permisos, modo `open`, otro modelo, esfuerzo, proveedor o versión de CLI,
  login, relanzar ni reintentar.
- Timeouts: revisor 600 s y ejecutor 900 s; comandos del perfil 30/120 s y
  variantes del planificador 1800 s. Tiempo máximo de 30 min por combinación y
  de 2 h para la matriz.
- Los retries internos de las CLI son desconocidos: tres invocaciones no
  garantizan tres solicitudes, y una invocación fallida puede consumir cuota.

## Criterios de éxito por combinación

El run llega a `COMMITTED` con estas condiciones:

- Intentos `planner`, `executor` y `reviewer`, todos `complete`, en ese orden.
- Agente y proveedor por proceso iguales a la tabla.
- Selección del ejecutor igual al catálogo (`<modelo>/low`).
- Validaciones correctas y JUnit `complete`.
- Review ACCEPT y aceptación elegible.
- Un único commit, autor `Harness Provider Matrix`, que solo cambia
  `src/estimate.ts` (`tasks * 30`).
- Jobs `DONE` con propietario cerrado, sin locks.

Se registran ids, versiones congeladas, hashes de capturas, argv relevantes,
uso y modelos reportados, duraciones y commit.

## Fallos y parada

- **Fallo de una combinación.** Es cualquier resultado distinto del esperado:
  preflight distinto, `stopped`, `blocked`, `revision_limit`, validación
  fallida, REVISE, salida o JSON inválido, `structured_output` ausente o
  rechazado, denegación de permisos, sandbox que impide escribir, aceptación
  no elegible, commit fallido o incierto, cuarentena `RECOVERY_REQUIRED`,
  timeout o más de 30 min. La combinación se detiene: el servicio se para con
  TERM y se conservan SQLite, artefactos, checkout y locks. No se confirma
  recuperación ni se liberan locks. No se cambian argv, sandbox
  (`danger-full-access` nunca), `--restricted`, `--json-schema`, esfuerzo,
  modelo ni versión. No se relanza. El diagnóstico es una tarea separada.
- **Las demás continúan** (selección del usuario). Hay una excepción: si el
  fallo es de autenticación, de cuota o de preflight de un proveedor, las
  combinaciones pendientes que usan ese proveedor no se lanzan, porque
  repetirían el mismo fallo. Las que no lo usan siguen.
- **Parada total** ante cualquier efecto fuera de las áreas de `BASE`
  (repositorio, fixture o configuración global modificados), ante un servicio
  que no se deja detener o al superar 2 h.

Conclusión de la matriz: cada combinación termina como completa, fallida (con
su etapa) o no lanzada (con su motivo).

No se certifica: facturación ni cuota, esfuerzo efectivo, retries internos,
modelo efectivo de Codex, aislamiento físico ni ausencia de red del sandbox,
los esfuerzos Codex no usados, el modo `open`, la evaluación de fase con un
revisor Claude, ramas REVISE/BLOCKED con proveedores, ni otros modelos,
perfiles o proyectos. Quedan fuera la QA visual, la integración de ramas, el
push y la publicación.

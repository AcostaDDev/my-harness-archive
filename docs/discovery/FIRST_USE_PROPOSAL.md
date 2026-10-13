# Propuesta de primer uso real con la configuración local (D033.8)

Preparada el 2026-10-13 sobre `8c0e169`, Git limpio en `main`. D050.
**Ejecutada una vez el mismo día con autorización del usuario; ver
[resultado](FIRST_USE_RUN.md).** El paso 3 se ejecutó desde el wheel instalado (D051).
Cuando se preparó, esta propuesta no estaba ejecutada ni autorizada. Ejecutarla requiere un
consentimiento específico y explícito del usuario para esta propuesta; D025 y
los consentimientos anteriores están agotados y no se trasladan.

Recorrido completo de D033.8 sobre un checkout desechable: tarea → commit →
check de fase → cierre con tag, a través de la composición `local-config-1`
(D049), el servicio `serve --config` y la API gestionada. Primer uso con
proveedores del motor completo; D025 solo acreditó transporte.

## Selecciones del usuario

Elegidas por el usuario el 2026-10-13 en esta sesión (preguntas explícitas):

| Rol | CLI fijada | Modelo solicitado | Esfuerzo | ¿Se invoca? |
|---|---|---|---|---|
| Ejecutor | Claude Code 2.1.295 | `claude-sonnet-4-6` | `low` | Sí, una vez |
| Revisor | Codex 0.162.1 | `gpt-6-luna` | `medium` | Sí, una vez |
| Evaluación de fase (rol `phase`, selección del revisor) | Codex 0.162.1 | `gpt-6-luna` | `medium` | Sí, una vez |
| Planificador | Codex 0.162.1 | `gpt-6-luna` | `low` | No: `planning_mode = "deterministic"` |

Herramientas del ejecutor: `Read`, `Edit`, `Write`, `Glob`, `Grep`, sin `Bash`
ni concesiones H3.2 (`grantable_tools` vacío). Las validaciones las ejecuta
el runner `commands-1`, no el agente. Ambos ids de modelo completaron transporte
en D025 con estas versiones de CLI; no se ha comprobado su comportamiento en
una tarea real.

## Hallazgos de la preparación

- **Versión de Claude.** `~/.local/bin/claude` apunta ya a 2.1.296, que `cli-4`
  no admite (`SUPPORTED` solo 2.1.295). El TOML fija el binario versionado
  `~/.local/share/claude/versions/2.1.295`, aún instalado, y
  `DISABLE_AUTOUPDATER=1` en el entorno de Claude. Si ese archivo desaparece
  antes de ejecutar, se detiene: no se sustituye por otra versión ni se amplía
  el baseline sin una tarea propia.
- **Codex necesita Node.** `codex` es `codex.js` con `#!/usr/bin/env node`; el
  `PATH` de Codex incluye el directorio de Node 24.15.0 de nvm.
- **Tag.** La validación de fases solo admite nombres simples (letras, dígitos,
  `.`, `_`, `-`); `first-use/p001` se rechazó en el ensayo y se usa
  `first-use-p001`.
- **Sin worktree por API.** No hay endpoint que cree worktrees (H2.4): el
  proyecto es el propio checkout desechable y el commit avanza su `main`.

## Preparación (sin proveedores ni red)

[`examples/first_use/prepare.sh`](../../examples/first_use/prepare.sh)
(SHA-256 `3ef3210a4276f59540538d68d53542b1668d2cd0f4189e5092dba57c8daf2c95`)
crea, con `BASE` inexistente (falla si existe):

- `BASE/web`: copia de la fixture `typescript_web`, `docs/STATE.md` y
  `docs/NEXT_STEPS.md` con la tarea determinista `P001-T001`, commit base y
  commit con la regresión deliberada `tasks * 45` (identidad Git explícita por
  `-c`, sin configuración global).
- `BASE/operator/harness-local.toml` (0600), `BASE/state` (SQLite y artefactos),
  `BASE/cli-tmp` (TMPDIR de las CLI), `BASE/command-home` (HOME/TMPDIR y npmrc
  vacíos de los comandos) y `BASE/npm-cache` (copia de `.local/npm-cache`; la
  instalación sigue `--offline`). Directorios privados 0700; checkout 0755.

Contrato de la tarea (en `docs/NEXT_STEPS.md` del checkout): objetivo restaurar
treinta minutos por tarea; ruta permitida `src/estimate.ts`; criterios 3 → 90,
0 → 0, `RangeError` conservado y check/test/build correctos sin tocar tests,
scripts, configuración ni lock; ejecutor `claude-sonnet-4-6 / low`.

TOML resultante (con `BASE=/private/tmp/harness-first-use`):

```toml
format = "local-config-1"

[service]
state_dir = "/private/tmp/harness-first-use/state"
supervisor = true

[git]
executable = "/usr/bin/git"
author_name = "Harness First Use"
author_email = "first-use@example.invalid"

[providers.codex]
executable = ["$HOME/.nvm/versions/node/v24.15.0/bin/codex"]
cli_version = "0.162.1"
timeout_seconds = 600
environment = { HOME = "$HOME", USER = "acosta", PATH = "$HOME/.nvm/versions/node/v24.15.0/bin:/usr/bin:/bin", TMPDIR = "/private/tmp/harness-first-use/cli-tmp", LANG = "C.UTF-8" }

[providers.claude]
executable = ["$HOME/.local/share/claude/versions/2.1.295"]
cli_version = "2.1.295"
timeout_seconds = 900
environment = { HOME = "$HOME", USER = "acosta", PATH = "/usr/bin:/bin", TMPDIR = "/private/tmp/harness-first-use/cli-tmp", LANG = "C.UTF-8", DISABLE_AUTOUPDATER = "1" }
tools = ["Read", "Edit", "Write", "Glob", "Grep"]
allowed_tools = ["Read", "Edit", "Write", "Glob", "Grep"]

[[projects]]
id = "first-use-web"
root = "/private/tmp/harness-first-use/web"
repository_trusted = true
profile = "typescript-web"
tag_kind = "lightweight"

[projects.policy]
executor_models = ["claude-sonnet-4-6"]
executor_efforts = ["low"]
planner_model = "gpt-6-luna"
planner_effort = "low"
reviewer_model = "gpt-6-luna"
reviewer_effort = "medium"
max_revision_cycles = 0
planning_mode = "deterministic"

[projects.commands]
authorize_profile_commands = true
executables = { node = "$HOME/.nvm/versions/node/v24.15.0/bin/node", npm = "$HOME/.nvm/versions/node/v24.15.0/bin/npm" }
environment = { PATH = "$HOME/.nvm/versions/node/v24.15.0/bin:/usr/bin:/bin", HOME = "/private/tmp/harness-first-use/command-home", TMPDIR = "/private/tmp/harness-first-use/command-home", LANG = "C.UTF-8", CI = "true", npm_config_cache = "/private/tmp/harness-first-use/npm-cache", npm_config_userconfig = "/private/tmp/harness-first-use/command-home/user.npmrc", npm_config_globalconfig = "/private/tmp/harness-first-use/command-home/global.npmrc", npm_config_update_notifier = "false" }
max_timeout_seconds = 300
max_output_bytes = 65536
```

Diferencias deliberadas frente al entorno D025: `TMPDIR` privado del área y
`DISABLE_AUTOUPDATER=1` en Claude; `PATH` mínimo con Node para Codex. Sin
credenciales, selectores ni fuentes heredadas; la autenticación sigue en cada CLI.

## Ensayo offline realizado

En el scratchpad de la sesión, con `BASE` allí (no en `/private/tmp`):

1. `prepare.sh` completo: dos commits (`65d6454` base, `e0f2504` regresión) y
   árbol limpio.
2. `harness-local check-config` **sin** `--preflight`: válido; versiones
   congeladas `cli-4`, `codex_cli 0.162.1`, `claude_cli 2.1.295`,
   `commands-1`, `local-config-1`, política exacta. Ningún proceso.
3. `harness-local init-db` y admisión en proceso con `supervisor` forzado a
   `false`: contrato determinista correcto (ruta, tres criterios, selección
   `claude-sonnet-4-6/low`), fase `P001` creada y job `QUEUED`; `cli-tmp`
   vacío y checkout intacto. Detectó el formato de tag (arriba).
4. Comandos del perfil en otra copia con el entorno exacto del TOML (`env -i`):
   `npm ci --offline` 0, `check` 0, `build` 0 y `test` 1 (2 de 3 tests fallan
   por la regresión): la tarea es real y la caché copiada basta.

No se ejecutaron las CLI de proveedores (ni version/help), `serve`, red ni
consumo. El área del ensayo se descarta; la ejecución real crea una nueva.

## Ejecución propuesta (solo tras consentimiento específico)

Fuera del sandbox (bind loopback, acceso de las CLI a su autenticación y red).
Una sola ejecución; parada al primer resultado distinto del esperado.

1. `sh examples/first_use/prepare.sh /private/tmp/harness-first-use`. Si la
   ruta existe, elegir otra nueva y registrarla (el hash del TOML cambia).
2. `harness-local check-config BASE/operator/harness-local.toml --preflight`:
   versiones 0.162.1 / 2.1.295 y help; si no, parar.
3. `harness-local init-db --database BASE/state/harness.sqlite3` y
   `harness-local serve --database BASE/state/harness.sqlite3 --config BASE/operator/harness-local.toml`
   (puerto 8013), con `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline`.
4. Sesión: `POST /api/session` con la clave del archivo privado anunciado,
   `X-Harness-Local: 1`, Host/Origin loopback; la UI también sirve.
5. `POST /projects/first-use-web/phases`: código `P001`, objetivo «Restaurar la
   estimación de treinta minutos por tarea», criterios (P001-T001 COMMITTED y
   alcanzable desde HEAD; check/test/build pasan sobre HEAD; STATE/NEXT_STEPS
   sin cambios respecto a la base), tareas `["P001-T001"]`, documentos por
   defecto, tag `first-use-p001`.
6. `POST /projects/first-use-web/runs` con `P001-T001`, `P001` y el texto de
   `docs/NEXT_STEPS.md`. El supervisor prepara (npm ci), invoca **ejecutor**,
   valida (check/test/build con JUnit) e invoca **revisor**. Esperado:
   `ACCEPTANCE_READY`.
7. Acción `commit` con `expected_version`: `COMMITTED`, autor
   `Harness First Use`, un commit sobre el de la regresión que solo cambia
   `src/estimate.ts`. Sin proveedor.
8. Acción `check` de la fase: puertas deterministas, validación base del perfil
   e invocación de **evaluación de fase**. Esperado: `READY_TO_CLOSE`.
9. Acción `close` con el `binding_sha256` READY mostrado, motivo y
   `confirmed: true`: `CLOSED` y tag ligero `first-use-p001` en el HEAD READY.
10. Detener el servicio (TERM) y comprobar evidencias.

## Límites de consumo

- Como máximo **tres** invocaciones de proveedor: ejecutor, revisor y evaluación
  de fase, una vez cada una. `max_revision_cycles = 0` y planificación
  determinista: un REVISE termina en `revision_limit`, sin corrección automática.
- No autorizados: `retry_executor`, `revalidate`, runs nuevos, otra fase, lote,
  chat, bootstrap, reconciliación con agente, concesiones de permisos, otro
  modelo/esfuerzo/proveedor, login, relanzar ni reintentar.
- Timeouts: Claude 900 s, Codex 600 s; comandos del perfil 30/120 s
  (techo 300 s). Retries internos de las CLI desconocidos: tres invocaciones no
  garantizan tres solicitudes; puede consumir cuota aunque falle.

## Criterios de éxito

Run `COMMITTED` con intentos ejecutor/revisor `complete` en sesiones nuevas,
seis comandos `STOPPED` con la configuración congelada, validaciones correctas
y JUnit con hash; review ACCEPT y aceptación ligada al contenido exacto; un
único commit que solo cambia `src/estimate.ts` (`tasks * 30`); fase `CLOSED`
con tag ligero en el HEAD READY; historial idéntico al reabrir SQLite; fixture
del repositorio y configuración global intactas. Registrar ids, hashes de
capturas, modelos/uso **reportados** separados de los solicitados, duraciones,
commit y tag.

## Criterios de parada

Detener sin cambiar entorno, modelo ni proveedor ante: preflight distinto;
preparación fallida; cualquier `stopped`, `blocked`, `revision_limit`,
validación fallida, REVISE o salida inválida; aceptación no elegible; commit
fallido o incierto; check `NOT_READY`/REVISE/`FAILED`/`BLOCKED`/
`NEEDS_RECONCILIATION`; cierre `STALE`/`FAILED`; cuarentena
`RECOVERY_REQUIRED`; timeout; o tiempo total superior a 45 minutos. Conservar
SQLite, artefactos, checkout y locks; no confirmar recuperación, no liberar
locks ni relanzar. La rama fallida también concluye la ejecución, con resultado
fallido y diagnóstico como tarea separada.

No se certifica: factura/cuota, esfuerzo efectivo, retries internos,
aislamiento físico ni comportamiento con otros modelos, perfiles o proyectos.
QA visual, integración de ramas, push y publicación siguen fuera.

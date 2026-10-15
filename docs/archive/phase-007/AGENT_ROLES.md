# Revisor y ejecutor con proveedor elegido (D052) — entrega

Implementado y verificado offline el 2026-10-13 según el
[alcance](NEXT_STEPS.md). Incremento `cli-5` / `local-config-2`. Sin
proveedores, login, red ni smoke: la matriz con proveedores reales queda como
propuesta aparte.

## Caracterización previa (version/help, sin consumo)

| CLI | Observado | Uso en `cli-5` |
|---|---|---|
| Codex 0.162.1 `exec --help` | `--sandbox read-only\|workspace-write\|danger-full-access`, `--output-schema`, `--json`, `-c` | Escritor: `--sandbox workspace-write` y `-c sandbox_workspace_write.network_access=false` (clave presente en el binario). `--output-schema` no se usa: el lector Codex sigue como en `cli-4`. |
| Codex 0.162.1, eventos `--json` | Cadenas del binario: `item.started/updated/completed`, `file_change`, `command_execution`, `agent_message` | Se conservan como eventos originales; el resultado sigue siendo el último `agent_message`. |
| Codex 0.162.1, esfuerzo | La ayuda no lo enumera; el binario serializa `minimal low medium high xhigh max ultra` | Vocabulario Codex. Inferido de cadenas del binario, no de la ayuda: lo confirmará el smoke. |
| Claude 2.1.295 y 2.1.296 `--help` | Salida idéntica (SHA-256 `550db4f8…5f09`). `--json-schema`, `--restricted`, `--tools`, `--effort (low, medium, high, xhigh, max)` | Se admite 2.1.296 (el enlace del usuario) además de 2.1.295. |

Codex 0.161.0 sigue admitido como lector, pero la escritura solo se acepta con
0.162.1, la única versión caracterizada.

## Qué cambia

- **Adaptador `cli-5`** (`adapters/cli_agents.py`). `CLIProcessAdapter` recibe
  `{"reviewer": CLIConfig, "executor": CLIConfig}` con cualquier proveedor.
  Una secuencia de dos proveedores se sigue leyendo como revisor Codex más
  ejecutor Claude. Los roles `planner`, `reviewer`, `phase`, `chat` y
  `bootstrap` van al revisor (lectura); `executor` va al ejecutor (escritura).
  `argv_for` elige por (proveedor, acceso):
  - Codex lectura: igual que `cli-4`.
  - Codex escritura: `workspace-write`, sin red, `approval_policy="never"` y
    búsqueda web desactivada.
  - Claude escritura: igual que `cli-4`.
  - Claude lectura: `--tools`/`--allowedTools Read,Glob,Grep`, `--restricted`
    (herramientas de archivo confinadas al checkout), `dontAsk`, MCP vacío,
    sin hooks ni sesión persistida, y `--json-schema` con la identidad mínima
    de cada rol. El motor sigue validando el contrato completo.
  - El esfuerzo debe pertenecer al vocabulario del proveedor.
  - Las versiones congeladas incluyen `reviewer_provider`/`reviewer_cli`,
    `executor_provider`/`executor_cli` y un hash que incluye el reparto.
    `codex_cli`/`claude_cli` desaparecen de las composiciones nuevas.
- **Concesiones H3.2 por proveedor** (`GRANTS`): Claude puede imponer
  concesiones de herramientas; Codex no tiene inventario que acotar, así que
  cualquier concesión de herramientas se rechaza antes de lanzar. Las
  concesiones de red se rechazan siempre. El revisor tiene un inventario fijo
  y no admite listas de herramientas.
- **Preflight por agente**: `preflight()` y `check-config --preflight` usan las
  claves `reviewer`/`executor` y exigen las flags de su modo de acceso (Claude
  lector: `--restricted`, `--json-schema`).
- **Política** (`EnginePolicy`): `executor_mode` (`catalog` | `open`) y
  `executor_effort_vocabulary`.
  - `catalog`: modelo y esfuerzo del catálogo, como hasta ahora.
  - `open`: cualquier modelo con forma válida (`[A-Za-z0-9][A-Za-z0-9._:@[\]-]{0,127}`)
    y un esfuerzo del vocabulario del proveedor ejecutor.
  - En `open` el catálogo es la selección de referencia para los contratos que
    genera el servidor (bootstrap y reconciliación de fase) y se muestra al
    revisor.
  - Los valores por defecto se omiten del snapshot congelado, así que los
    contextos y bootstraps anteriores conservan su forma exacta.
- **`local-config-2`**:
  - `[agents.reviewer]` declara `provider`, `model` y `effort` además de
    ejecutable, versión, entorno y timeout.
  - `[agents.executor]` declara `provider` y las mismas claves de CLI; las
    listas de herramientas solo valen para Claude.
  - `[projects.policy]` exige `planning_mode` (`agent` | `deterministic`),
    `executor_mode` y el catálogo; `max_revision_cycles` es opcional.
  - El revisor planifica con su propia selección, así que desaparecen
    `planner_*` y `reviewer_*` por proyecto.
  - `local-config-1` se sigue leyendo como revisor Codex más ejecutor Claude con
    su política (planificador separado, `auto` admitido), y su snapshot no gana
    claves.
- **API/UI**: `ManagedProjectRead.agents` muestra el revisor (proveedor, modelo
  y esfuerzo), la planificación, el ejecutor (proveedor, modo, catálogo y
  vocabulario) y el modo de planificación. El proveedor es `null` fuera de una
  composición `cli-5`. El bootstrap muestra el proveedor del revisor. Los
  textos de chat, bootstrap y `Bootstrap.tsx` son ahora neutros.

## Compatibilidad y operación

- Los historiales `cli-1`…`cli-4` y los snapshots de contexto anteriores se
  restauran sin cambios. Esquema `0013_bootstrap` y codec 7 conservados.
- Un job pendiente congelado con `cli-4` no se ejecuta con el paquete nuevo,
  porque las versiones difieren, y entra en cuarentena antes de cualquier
  efecto. Ocurre igual con cualquier cambio de composición: hay que terminar o
  detener los jobs antes de actualizar. Cambiar `executor_mode` o
  `planning_mode` también invalida los jobs pendientes por el hash local.
- `examples/local_config.example.toml` pasa a `local-config-2`.
  `examples/first_use/prepare.sh` conserva `local-config-1`, que sigue siendo
  legible.

## Verificación offline

- `tests/product/test_agent_roles.py` (31 casos):
  - Matriz de las cuatro combinaciones por `local-config-2`, supervisor y
    adaptador real con CLI sintéticas, Node/npm/Git reales y SQLite temporal.
    Cubre planificador, ejecutor y revisor; proveedor y agente por proceso; argv
    por acceso; edición del escritor; y `ACCEPTANCE_READY`.
  - Una mutación temporal (ejecutor enrutado al revisor) hace fallar las cuatro.
  - Modos catálogo y libre: modelo fuera del catálogo, esfuerzo fuera del
    vocabulario y forma inválida.
  - Planificación determinista con la selección de NEXT_STEPS según el modo.
  - Cuarentena al cambiar de modo, lectura de `local-config-1`, ida y vuelta de
    snapshots, 13 rechazos de configuración, `check-config` con preflight por
    agente, argv sin lanzar e identidad congelada del reparto.
- `test_permissions.py`: un ejecutor Codex rechaza una concesión de
  herramientas antes de lanzar.
- Pruebas existentes adaptadas al reparto por agente (`agents`, `cli-5`, chat
  con Claude revisor). La CLI sintética distingue lectura/escritura por argv,
  informa la versión por entorno y emite `structured_output` como lector Claude.
- Regresión: 889 pytest y 121 subtests, 12 checks ligeros, 6 Node, `tsc`,
  build de Vite, `alembic check` y OpenAPI/tipos regenerados.

No probado: proveedores reales, la conducta real de `--json-schema` con
`--tools` restringido, `--restricted` y el sandbox `workspace-write` de Codex.
Todo eso corresponde al smoke autorizado de la matriz. Tampoco hay QA visual
con navegador: la línea de agentes del listado de proyectos solo se comprobó
con `tsc` y build.

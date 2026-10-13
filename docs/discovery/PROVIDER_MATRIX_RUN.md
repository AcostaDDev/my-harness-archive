# Smoke de la matriz D052 (D055): ejecución autorizada

Ejecutado el 2026-10-13 (16:22–16:23 UTC) sobre `6c1c245`, con Git limpio en
`main`. [Propuesta](PROVIDER_MATRIX_PROPOSAL.md), D055. El usuario escribió
«Ejecútala».

**Resultado: la combinación 1 falló en el planificador por un defecto del
contrato. El usuario decidió parar la matriz y corregir, así que las
combinaciones 2–4 no se lanzaron.** Hubo una sola invocación de proveedor, sin
reintentos, relanzamientos ni login. Consentimiento agotado.

## Forma de ejecución

El clasificador de permisos de Claude Code bloqueó la preparación del script
que lanza los agentes («Create Unsafe Agents»). El usuario eligió lanzar él
mismo los comandos de los agentes con `!`. El reparto quedó así:

- **Claude Code**, sin agentes:
  - `prepare.sh` sobre `BASE=/private/tmp/harness-provider-matrix`.
  - Wheel construido y verificado en `BASE/package` (SHA-256 `330ee0bf…`).
  - Venv `BASE/venv` instalado offline por hashes (D051).
  - `check-config --preflight` de las cuatro combinaciones desde el venv:
    `version_help_match` en los ocho agentes, sin flags ausentes. El TOML de la
    combinación 4 es idéntico al de la propuesta.
- **Usuario con `!`:**
  - La corrección del script de recorrido HTTP y su copia como `BASE/driver.py`
    (SHA-256 `1e596a23…`).
  - La orquestación en segundo plano de la combinación 1: `init-db`, `serve`,
    recorrido y TERM.

## Combinación 1 (revisor Codex → ejecutor Claude)

TOML SHA-256 `85d2c7db…`. Versiones congeladas: `cli-5`, `local-config-2`,
`reviewer_provider` codex 0.162.1, `executor_provider` claude 2.1.296,
`local_config_sha256` `118799502a2f…`, `cli_config_sha256` `bb1b5a1fb1b8…` y
`command_config_sha256` `65b4ca2ea310…`.

| Paso | Resultado |
|---|---|
| Sesión y proyecto | 200; `agents` con revisor Codex `gpt-6-luna`/`medium`, ejecutor Claude en catálogo `claude-sonnet-4-6`/`low` |
| Fase P001 | 201 `ACTIVE` |
| Run `f71501e4-bb04-465d-b33f-b0ceee216329` | job 1: preparación (`node`, `npm --version` y `npm ci --offline`, exit 0) |
| Planificador, intento `85c9d64b-dd3c-49b1-b10a-0eaf3e049ae6` | `complete`, exit 0, 11,9 s, stderr vacío |
| Contrato | **Rechazado**. Run `STOPPED`, etapa `planner`, motivo `Invalid task validation_commands` |
| Ejecutor y revisor | No invocados; sin commit |

Del planificador:

- **Argv congelado.** `--sandbox read-only`, `model_reasoning_effort="medium"` y
  `--model gpt-6-luna`, como en `cli-5`.
- **Uso reportado.** 24 639 tokens de entrada (17 920 en caché), 618 de salida y
  240 de razonamiento. No reporta el modelo.
- **Comando observado.** Leyó `src/estimate.ts` con un `command_execution`
  (`sed -n`) dentro del sandbox de solo lectura.
- **Contrato devuelto.** Correcto salvo en un campo:
  - Ruta permitida `src/estimate.ts` y criterios completos.
  - Selección del ejecutor dentro del catálogo (`claude-sonnet-4-6`/`low`, con
    motivo).
  - `validation_commands` como **listas de argv**:
    `[["npm","run","check"],["npm","run","test"],["npm","run","build"]]`.

| Evidencia | Bytes | SHA-256 |
|---|---:|---|
| prompt del planificador | — | `a817054ebdc86dd261812db0dfffb3d0ae4b49ee9726fd37fba1f3381c7087c3` |
| stdout del planificador | 2 584 | `c6bb478baa52960061701162f41677c74793cdef2969ad333789b06eb3287dce` |

Estado final: 47 eventos, job 1 `DONE` con propietario cerrado, proceso del
agente `STOPPED` y sin locks. La fase sigue `ACTIVE`. Checkout limpio, sin
commit nuevo; `cli-tmp` vacío.

## Hallazgo: contrato ambiguo de `validation_commands`

La plantilla `plan-task` dice «Validation commands must be task-specific argv
commands». El esquema (`output_schema` y la forma de `cli_agents.SHAPES`) solo
declara `array`, con el ejemplo `[]`. El motor exige una lista de **cadenas**:
`task_contract` las valida y `run_validations` las separa con `shlex`. Un
planificador real interpretó «argv» como listas de argumentos.

El defecto no depende del proveedor y afecta a toda planificación por agente.
La prueba offline no lo detectó porque su CLI sintética devuelve
`validation_commands: []`. La corrección queda como tarea separada: aclarar la
plantilla o el esquema, aceptar una forma normalizada, o ambas cosas.

## Incidencia del script de recorrido

`driver.py` solo trataba `QUEUED` y `RUNNING` como estados no terminales. El job
pasó a `ACTIVE` y el script cerró en el primer segundo: sin commit (correcto,
porque no había `ACCEPTANCE_READY`) y con TERM al servicio a los ~1 s del
inicio del run. El supervisor esperó al job activo. Este terminó por sí mismo
(`DONE` a las 16:23:10, tras el contrato rechazado) y el servicio cerró limpio
(«Application shutdown complete»). La parada se debe al contrato, no a la
cancelación. La instantánea por API quedó incompleta. La evidencia completa
está en la SQLite y en los artefactos del área, leídos en modo solo lectura.
Antes de una nueva ejecución hay que esperar hasta `finished_at` (o
`RECOVERY_REQUIRED`).

## Combinaciones 2–4

No se lanzaron, por decisión del usuario tras el fallo. Sus áreas siguen
preparadas: estado vacío, checkout limpio y preflight correcto. No sirven para
una ejecución nueva sin consentimiento nuevo; se prepara un área nueva.

## Comprobaciones posteriores

- Sin procesos del harness ni de las CLI lanzadas por él. Los procesos `codex`
  presentes pertenecen a la app de escritorio del usuario.
- Sin nuevas entradas en `~/.claude/projects`: Claude no llegó a invocarse.
- Repositorio `my_harness` y fixture sin cambios. Configuración global intacta.

## Qué acredita y qué no

Acredita, para la combinación 1:

- La composición real `cli-5`/`local-config-2` con preflight por agente.
- La admisión por HTTP desde el wheel instalado.
- La preparación con `commands-1`.
- Un planificador Codex de solo lectura en modo agente, con la selección del
  revisor y la elección del ejecutor dentro del catálogo.
- El rechazo determinista de un contrato inválido, sin efectos ni llamadas
  adicionales.

No acredita: Codex escritor, Claude lector con `--json-schema`/`--restricted`,
Claude 2.1.296 en uso real, el esfuerzo `low` de Codex, la revisión ni el
commit. Queda todo pendiente de una ejecución nueva tras la corrección.

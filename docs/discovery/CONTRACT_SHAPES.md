# Formas de salida de los agentes alineadas con el motor (D056) — entrega

Implementado y verificado offline el 2026-10-13. Origen: el smoke D055
([resultado](PROVIDER_MATRIX_RUN.md)). Un planificador Codex real devolvió
`validation_commands` como listas de argv
(`[["npm","run","check"], …]`) y el motor paró con
`Invalid task validation_commands`.

## Causa

Cada pieza decía algo distinto:

- La plantilla `plan-task` pedía «task-specific argv commands».
- El esquema fijo del motor (`output_schema`) solo declaraba `array`.
- La forma de ejemplo del adaptador mostraba `[]`.
- El motor exige una lista de **cadenas**: `task_contract` las valida y
  `run_validations` las separa con `shlex`.

La CLI sintética offline devolvía `[]` o cadenas, así que no lo detectaba.

Revisión del resto de roles (punto 2 de la tarea):

| Rol | Campo | Validador del motor | Antes en el esquema o la forma | Riesgo |
|---|---|---|---|---|
| planificador | `allowed_paths`, `forbidden_paths`, `acceptance_criteria` | listas de cadenas | `array` / `[]` o `["criterion"]` | bajo; ahora tipado |
| revisor | `findings` | objetos con `severity`, `category`, `file`, `problem` de texto | **sin forma** (`[]`) | un revisor real que devolviera hallazgos como texto pararía con `Invalid review finding` |
| fase | `required_actions`, `blocking_questions`, `exit_criteria_results` | cadenas; objetos con `criterion`, `passed` booleano y `evidence` | `array`; la forma de ejemplo sí muestra los objetos | bajo; ahora tipado |
| chat y bootstrap | listas | cadenas | la forma de ejemplo muestra cadenas | ninguno; ahora tipado |

## Qué cambia

- **Esquema fijo del motor** (`prompts.output_schema`). Cada lista declara el
  tipo de sus elementos.
  - `validation_commands` describe «one shell-free command string per
    command», con `[]` si bastan las validaciones del perfil.
  - `executor_selection` declara `model`, `effort` y `reason`.
  - El revisor declara como **opcionales** `findings` (objetos con sus cuatro
    textos), `blocking_questions`, `scope_grants`, `next_prompt` y
    `executor_selection` (objeto o `null`).
  - Los campos obligatorios no cambian en ningún rol.

  El esquema forma parte del prompt renderizado y de su instantánea por
  intento. Los prompts editados por el usuario (H3.1) también lo reciben,
  porque el editor no puede debilitarlo.
- **Plantilla integrada `plan-task`.** Pide «one shell-free string per command
  (never argv arrays)» y `[]` cuando bastan las validaciones del perfil.
  Afecta solo a catálogos nuevos: cada run congela su `prompt_catalog_json`.
- **Normalización en `task_contract`.** Una lista de argv no vacía con cadenas
  no vacías se convierte en `shlex.join(argv)`, y `shlex.split` devuelve
  exactamente el mismo argv. El contrato congelado guarda cadenas. La salida
  original del agente se conserva sin cambios en su intento.
  - Cualquier otra forma se sigue rechazando: lista vacía, elementos no texto o
    vacíos, anidados, objetos, una cadena suelta o `null`.
  - La política de prefijos y la autorización exacta de `commands-1` siguen
    aplicándose sobre el argv resultante.
  - Un contrato del servidor sigue exigiendo JSON canónico: con listas de argv
    se rechaza.

Sin cambios de argv de las CLI: `cli-5` se conserva, igual que el
`--json-schema` mínimo del lector Claude. Tampoco cambian el esquema
`0013_bootstrap`, el codec 7, OpenAPI ni la UI. No se reescriben historiales,
contratos ni catálogos congelados.

## Verificación offline

`tests/product/test_contract_shapes.py` (16 casos):

- Ida y vuelta exacta de argv con espacios, comillas, `$`, `&&` y barras
  invertidas.
- Planificador por agente con la forma observada:
  - Llega a `acceptance_ready`.
  - El contrato guarda `"test-runner check"` y el intento conserva la lista
    original.
  - La validación coincide con la del perfil y se ejecuta una sola vez.
- Siete formas inválidas siguen deteniendo el planificador con un solo intento.
- Un contrato del servidor con listas de argv se rechaza por no ser canónico.
- Esquemas tipados sin campos obligatorios nuevos, y el prompt renderizado
  incluye la instrucción y los tipos.
- **Regresión D055 por el adaptador real** (revisor Claude, ejecutor Codex, CLI
  sintéticas): el planificador devuelve `[["npm","run","test"]]` y se llega a
  `ACCEPTANCE_READY`. La variante autorizada de 1800 s se ejecuta con exit 0.

Mutación: sin la normalización fallan 7 de los 16 casos, entre ellos la
regresión por el adaptador real.

Regresión completa: 905 pytest y 121 subtests, 12 checks ligeros y 6 pruebas
Node. OpenAPI sin cambios.

No probado: la conducta de un proveedor real con el esquema tipado. Eso
corresponde a la nueva ejecución de la matriz, con consentimiento propio.

## Script de recorrido de la próxima ejecución

Valorado (punto 4 de la tarea): en D055, `driver.py` trató `ACTIVE` como estado
terminal. Se versionará en `examples/provider_matrix/` al preparar la nueva
ejecución, porque es su único uso, y esperará hasta `finished_at` o
`RECOVERY_REQUIRED`. Las órdenes que lanzan agentes las ejecuta el usuario con
`!`, porque el clasificador de permisos de Claude Code las bloquea.

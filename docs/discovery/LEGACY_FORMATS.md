# H0.1 — Formatos legacy y contratos mínimos

Origen y hashes: [BASELINE.md](BASELINE.md), [baseline.json](baseline.json).
Referencias a `.harness/harness.py` en el commit
`5be3b8a1328f7725a0f81c98af4f365e3528a767`. Estos son contratos observados para
importación futura, no modelos del nuevo núcleo ni una reconstrucción de runs reales.

## Identidad, rutas e intentos

`now_id` (77) produce `YYYYMMDDTHHMMSS±HHMM`; `create_run_dir` (827) crea
`.harness/runs/<timestamp>_<Pnnn-Tnnn|Pnnn-CLOSE|Pnnn-RECONCILE>/`.
El nombre aporta fecha local con offset, no inicio/fin fiable de cada agente.
`NN` es índice con ancho mínimo de dos dígitos; puede superar 99.

No hay `attempt.json` ni estado único del run. `claude-NN.prompt.md` acredita
un intento preparado; no prueba que el proceso arrancó ni terminó. Request,
events y result aportan evidencias progresivas. `review-NN` y `validation-NN`
son iteraciones de evidencia; `resume_task` (1726) puede crear otra sin invocar
Claude. No deducir un intento de agente por cada validación. Cada rol usa sesión
nueva; ninguna identidad de conversación persistente es necesaria para reanudar.

Los caminos de logs en JSON son relativos a ROOT (`rel`, 73), normalmente
`.harness/runs/.../validation-NN/01.stdout.log`, no al propio archivo JSON.
Prompts/patches/logs son texto; eventos Claude son JSONL sin envoltorio propio.
Son datos al importarlos: nunca ejecutar comandos ni prompts del histórico.

## Tarea y revisión

| Artefacto y productor | Campos / significado mínimo |
|---|---|
| `task.json`; `plan_task` (1022), `deterministic_task` (924); `schemas/task.schema.json` | `task_id`, `phase_id`, `title`, `objective`, `business_context`, `documentation_refs`, `allowed_paths`, `forbidden_paths`, `implementation_constraints`, `acceptance_criteria`, `validation_commands`, `deliverables`, `risk_notes`, `executor_prompt`, `executor_selection` |
| `review-NN.json`; `review_task` (1223); `schemas/review.schema.json` | `task_id`, `verdict` ACCEPT/REVISE/BLOCKED, `summary`, `acceptance_criteria_results`, `findings`, `validation_assessment`, `documentation_proposals`, `blocking_questions`, `next_prompt`, `executor_selection`, `scope_grants` |
| `scope-NN.json`; `apply_scope_grants` (1383) | `task_id`, `authority`, `review`, `grants`, `previous_task`, `updated_task`. Modifica `task.json`; no snapshot inmutable por intento en legacy |

Los esquemas actuales exigen todos los campos listados y rechazan adicionales.
Los arrays pueden estar vacíos salvo los criterios de tarea (mínimo uno).
`executor_selection` contiene `model`, `effort`, `reason`; los dos modelos y cinco
esfuerzos permitidos están congelados en los snapshots, sin recomendar su uso.
`executor_selection` (533) admite ausencia en tareas antiguas y toma defaults del
config actual: el importador no debe atribuir ese default a un intento histórico.

Excepción efectiva: el planificador determinista añade `contract_source`, aunque
el esquema de tarea tenga `additionalProperties: false`. Es un campo conocido
del productor, no un motivo para perder el archivo. La muestra de aceptación lo
incluye. Un schema de respuesta CLI no cubre todos los artefactos escritos por
el motor ni todas sus versiones históricas.

Cada resultado de criterio contiene `criterion`, `passed`, `evidence`. Cada
finding tiene `severity`, `category`, `file`, `line` (string), `problem`,
`evidence`, `required_fix`. La evidencia es texto de revisión, no una medición
independiente. REVISE exige selección nueva y `next_prompt` no vacío; ACCEPT y
BLOCKED usan selección null y prompt vacío. Una concesión contiene `path`,
`reason`, `constraint` y solo es válida en REVISE sin preguntas humanas.

ACCEPT con tests fallidos/política dura/preguntas o concesiones se rechaza en
`validate_and_review_task` (1498). ACCEPT no prueba commit completado; el motor
actualiza STATE y puede ejecutar `git add -A` y commit después (1258–1290).
No escribe un `accepted.json` ni persiste el SHA retornado como resultado del run.
La identidad del commit exige evidencia Git externa, no un SHA inventado.

## Ejecución, solicitud y consumo

Productores: `claude_exec` (557), `stream_claude` (168), `codex_exec` (454).

| Archivo | Contrato observado |
|---|---|
| `claude-NN.prompt.md`, `.stderr.log` | Prompt renderizado y diagnóstico; pueden estar ausentes o vacíos |
| `claude-NN.result.request.json` | `model`, `effort`, `reason`, `max_turns`: valores solicitados antes de lanzar |
| `claude-NN.result.events.jsonl` | Eventos dict de proveedor: `system`, `assistant`/`user` con `message.content`, `result`, otros conservados. No hay esquema propio ni secuencia/timestamp garantizados |
| `claude-NN.result.json` | Objeto final proveedor. Campos usados: `result`, `type`, `subtype`, `is_error`, `permission_denials`, `modelUsage`, `usage`, `num_turns`, `duration_ms`, `total_cost_usd`. No todos son obligatorios |
| `claude-NN.result.usage.json` | `requested`, `actual_models`, `usage`, `model_usage`, `num_turns`, `duration_ms`, `api_equivalent_cost_usd`, `is_error`, `subtype`, `exit_code` |
| `planner.*`, `review-NN.prompt.md`, `review-NN.stderr.log` | `plan_task` y `review_task` guardan prompt, respuesta estructurada y stderr Codex; tokens de stderr no constituyen telemetría normalizada completa |

Los nombres `.result.request/.events/.usage` derivan de `with_suffix` sobre
`claude-NN.result.json`, no de un prefijo `claude-NN` sin `.result`.
`actual_models` deriva de las claves de `modelUsage`, no de la petición. Ausencia
de `modelUsage` da lista vacía; no demuestra qué modelo se ejecutó. Esfuerzo
solicitado no prueba esfuerzo efectivo. Los campos no reportados se guardan como
null en usage; faltan enteramente en resultados antiguos. No sustituirlos por
cero, ni deducir cuota de tokens. Coste API equivalente no es factura de suscripción.

El resultado con `is_error=true`, subtype `error*` o exit code no cero detiene el
motor sin reintento/fallback. Timeout o Ctrl+C pueden dejar eventos sin resultado
final. Un archivo parcial puede ser un write interrumpido: `write_json` (81) y
los writes de respuesta no son atómicos. No equiparar fallo de parseo con fallo
del agente. Compatibilidad CLI y parsing robusto de streams pertenecen a H0.2.

## Validación, política y bloqueo

| Archivo / función | Campos mínimos y variantes |
|---|---|
| `validation-NN.json`; `run_validations` (669) | `iteration`, `all_passed`, `commands`, `policy`, `note`; opcional `formatting` añadido en el loop |
| Entrada de command | `command`, `passed`, `exit_code`, `stdout_file`, `stderr_file`, `error`; `duration_seconds` solo al ejecutar. Rechazo de comando: exit_code null, archivos vacíos y error, sin duración |
| `policy-NN.json`; `enforce_path_policy` (785) | `iteration`, rutas antes/después, intentos/restauraciones prohibidos y sensibles, rutas remanentes, `hard_failure` |
| `format-NN.json`; `format_task_files` (746) | `paths`, `passed`, `skipped`; si ejecuta puede añadir exit_code/stdout/stderr; si falla al lanzar, error |
| `preflight-NN.json`; `preflight_environment` (1323) | `commands`, `all_passed`; command usa `argv`, `passed` y `exit_code` o `error`. Logs `preflight-NN-i.stdout/stderr.log` |
| `stop-NN.json`; `stop_run` (1314) | `task_id`, `verdict: BLOCKED`, `reason`; detalles variables: `stage`, `command(s)`, `blocking_questions`, `review_file`, `permission_denials` |
| `resume-NN.json`; `resume_task` (1726) | `task_id`, `resumed_at`, `head_at_resume`, `previous_review` (puede ser null), `changed_paths`, `retry_executor` |

La duración es del comando, no de tests individuales. No hay reporte JUnit ni
identificador por test genérico. `all_passed=true` con commands vacío significa
que no había validaciones, no que se haya probado el producto. El timeout puede
interrumpir la escritura del reporte completo.

BLOCKED de `review-NN.json` es un juicio de revisión. `stop-NN.json` puede ser
un error operativo/denegación o petición humana; no es una review con findings.
El límite de revisiones puede devolver código 4 sin stop nuevo. Ctrl+C tampoco
garantiza stop. `reconcile_phase` (2170) tiene además un stop distinto:
`reason`, `problems`, sin `task_id` ni `verdict`. Preservar formato/procedencia,
no imponer el contrato de review a todas las paradas.

## Fase y cierre

| Artefacto / origen | Campos / efecto |
|---|---|
| `phase-review.json`; `phase_check` (1917), `schemas/phase.schema.json` | `phase_id`, `phase_name`, `verdict` READY/REVISE/BLOCKED, `summary`, `exit_criteria_results`, `required_actions`, `blocking_questions`, `archive_summary_markdown`, `archive_review_markdown`, `next_phase_id`, `next_phase_name`, `next_steps_markdown` |
| `phase-review.meta.json`; `phase_check` (1987) | `phase_id`, `head`: vínculo de review al HEAD examinado; no hash de todos los artefactos |
| `reconcile.json`; `reconcile_phase` (2102), `schemas/reconcile.schema.json` | `phase_id`, `summary`, `files_changed`, `blocking_questions` |
| `docs/STATE.md`; `parse_state_frontmatter` (364), `apply_phase_close` (2244) | YAML front matter: `phase`, `phase_name`, `current_task`, `last_accepted_task`, `status`; no esquema completo obligatorio de todo el documento |
| `docs/NEXT_STEPS.md`; `TASK_RE` (52), `deterministic_task` (924) | Encabezados `## Pnnn-Tnnn — título`, Objective, criterios en bullets, Allowed paths en backticks o none, Executor. Preguntas bajo `## Phase-close questions` con checkbox y Answer |
| `docs/ROADMAP.md`; `replace_roadmap_status` (2222) | Encabezados `## Phase nnn — nombre` y `**Status:** Planned/Active/Completed` |
| `docs/archive/phase-nnn/`; `apply_phase_close` (2244) | `NEXT_STEPS.md`, `SUMMARY.md`, `REVIEW.md`; actualización de roadmap/STATE/NEXT_STEPS, commit y tag si config lo exige |

READY no significa CLOSED. Se reutiliza solo review de la fase y HEAD idénticos
(`reusable_phase_review`, 1899), con árbol limpio y autorización de cierre.
Preguntas sin contestar impiden review/cierre. No existe `phase-closed.json`:
archivo de fase y estado documental son evidencias distintas de Git/tag.
El fixture de cierre contiene documentos posteriores y un extracto Git sintético
externo al run, sin fingir un artefacto que el motor no genera.

## Ausencias y cobertura de muestras

El [README de fixtures](../../tests/fixtures/legacy/README.md) y su manifest
separan archivo completo, JSON deliberadamente parcial, archivo ausente y campo
no registrado (ausente o null). Son expectativas de muestras, no estado operativo.
No se añaden valores estimados a un artefacto observado ni defaults históricos.

Cubiertos: aceptación con telemetría reportada, REVISE seguido de otra iteración,
BLOCKED con decisión humana y posterior error operativo al reintentar, ejecución
interrumpida sin final y revisión truncada, READY y cierre documental con fase
siguiente/reconciliación. No cubiertos en fixtures: todas las variantes de scope,
preflight, formatter, errores de autenticación, streams malformados de proveedor,
eventos desconocidos, historial de todas las versiones ni recuperación real de Git.
Están inventariados cuando son observables en el código; no se declaran probados.

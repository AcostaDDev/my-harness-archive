# H0.1 — Inventario de la referencia

Inspección estática: 2026-10-11. Origen: `$HOME/Documents/projects/reference_project`.
Commit: `5be3b8a1328f7725a0f81c98af4f365e3528a767`.

[baseline.json](baseline.json) registra el estado Git observado y SHA-256 de 21
archivos: los 20 archivos de `.harness` fuera de runs/cachés y `AGENTS.md` del
origen. Incluye hash del contenido local y del contenido en HEAD por separado.
Los 21 coinciden con HEAD. Los cambios locales observados pertenecen a la
aplicación; no se inspeccionó su contenido ni se incorporó a los fixtures.

Estado observado (`git status --short`, directorios sin seguimiento agrupados):

```text
 M src/apps/billing/delinquency_selectors.py
 M src/apps/billing/tests/test_delinquency_selectors.py
 M src/apps/staff/templatetags/staff_navigation.py
 M src/config/settings/base.py
 M src/config/urls.py
 M src/templates/backoffice/includes/navigation.html
?? src/apps/analytics/
?? src/templates/analytics/
```

Para reproducir la procedencia, leer los archivos en esa revisión y calcular
SHA-256 de sus bytes; comparar con `head_sha256`. `sha256` identifica la copia
local realmente inspeccionada, aunque en futuras capturas difiera de HEAD.
No se necesita ejecutar ni importar el código de origen. Los números de línea
de este inventario y de [LEGACY_FORMATS.md](LEGACY_FORMATS.md) corresponden a esta
revisión, no a versiones futuras.

## Operaciones y separación de responsabilidades

Las referencias de la tabla son relativas a `.harness/`; salvo indicación
contraria, las funciones están en `harness.py`.

| Operación observada | Trazabilidad | Extracción prevista / acoplamiento |
|---|---|---|
| CLI y selección de operación | `main` (2449), `show_next` (2408) | Interfaz legacy; no API del producto nuevo |
| Diagnóstico | `doctor` (2333), `scripts/doctor.sh` | Git/CLI genéricos; checks de stack deben ir al perfil. El wrapper ejecuta el motor, no se lanzó |
| Planificación determinista o Codex | `next_task_id` (406), `deterministic_task` (924), `plan_task` (1022) | Reusable el mecanismo; depende del formato Markdown y los IDs `Pnnn-Tnnn` |
| Ejecución y streaming | `claude_exec` (557), `stream_claude` (168), `execute_iteration` (1482) | Adaptador CLI; solicitudes, eventos y errores. Compatibilidad real pendiente de H0.2 |
| Política de archivos y concesiones | `enforce_path_policy` (785), `apply_scope_grants` (1383) | Separar mecanismo de patrones de perfil; concesiones actuales restringidas a `src/` y extensiones concretas |
| Formato, diff y validación | `format_task_files` (746), `capture_diff` (771), `run_validations` (669) | Evidencias reusables; Ruff sobre `src/` y baseline Django/Docker específicos |
| Revisión y ciclos | `review_task` (1223), `validate_and_review_task` (1498), `stalled_review_signature` (1425) | Conservar ACCEPT/REVISE/BLOCKED, límites y detección de falta de progreso |
| Aceptación y Git | `apply_accepted_state` (1258), `commit_accepted_task` (1268), `working_tree_fingerprint` (1297) | Reusable el objetivo; usa `git add -A`, no persiste un certificado de contenido revisado |
| Paradas y recuperación | `stop_run` (1314), `resume_task` (1726), `revision_attempts` (1491) | Conserva artefactos y revalida; iteración de evidencia no equivale siempre a invocación nueva |
| Lotes | `pending_task_run` (1633), `run_tasks` (1646) | `--until-blocked` autoriza también reconciliación/cierre; separar políticas en el nuevo producto |
| Revisión y cierre de fase | `phase_check` (1917), `reusable_phase_review` (1899), `apply_phase_close` (2244) | READY ligado a HEAD; archivos y tag acreditan aplicación por separado |
| Reconciliación documental | `reconcile_phase` (2102), `unresolved_phase_questions` (2022) | Edición acotada a docs; front matter, tareas y estados de roadmap son del motor |
| Resumen de consumo | `show_usage` (2417), `executor_history` (1000) | Lee resultados locales; coste equivalente API distinto de cuota/suscripción |
| Descubrimiento inicial | `prompts/bootstrap-project.md` | Prompt manual, no comando de bootstrap automatizado |

## Archivos, formatos y dependencias

| Grupo inventariado | Papel observado y límites |
|---|---|
| `harness.py` | Motor monolítico Python; `ROOT` deriva de su ubicación (48–50). Usa biblioteca estándar y PyYAML |
| `requirements.txt` | Declara `PyYAML>=6.0,<7`; rango del origen, sin fijar dependencias nuevas |
| `config.yaml` | Proyecto, workflow, entorno, planificación, Codex/Claude, protección, validación y Git. Es configuración efectiva del origen, no defaults de Harness Local |
| `schemas/{task,review,phase,reconcile}.schema.json` | Contratos de respuestas estructuradas. Snapshots exactos en fixtures; no existen esquemas de resultado Claude, validación o stop |
| `prompts/plan-task.md`, `review-task.md`, `revise-task.md` | Planificación, revisión y corrección |
| `prompts/executor-routing.md`, `MODEL_POLICY.md` | Selección modelo/esfuerzo con razón; valores y recomendaciones históricos |
| `prompts/reconcile-phase.md`, `close-phase.md`, `bootstrap-project.md` | Mantenimiento documental, evaluación de cierre y descubrimiento manual |
| `scripts/dev_tools.py` | `sync_python` (28) instala requirements locales; `focused_tests` (117) ejecuta Django sobre Docker/PostgreSQL; `fetch_asset` (90) descarga assets HTTPS con hosts y rutas limitados. No se ejecutó |
| `tests/test_workflow.py` | Pruebas de comportamiento existentes leídas estáticamente: workflow, permisos, routing, planificación, fases, diff y streaming. No se importaron ni ejecutaron |
| `README.md`, `.gitignore` | Operación/documentación del origen; runs ignorados. README incluye referencias a ejecuciones reales que no se trasladaron |
| `../AGENTS.md` | Reglas del producto ReferenceProject y roles. Solo referencia; no gobierna el desarrollo manual de este repositorio |

Dependencias específicas a trasladar a un perfil: Django, PostgreSQL, Docker
Compose, servicio `web`, `manage.py`, `config.settings.test`, smoke de Celery,
Ruff sobre `src`, requirements de aplicación, hosts de assets, rutas protegidas
y documentación canónica ReferenceProject. Celery es una dependencia de ese proyecto,
no del supervisor local propuesto. Git, CLI Codex/Claude y PyYAML son dependencias
observadas del motor; aquí no se verificaron sus versiones ni autenticación.
`dontAsk` deniega peticiones sin permiso: no describe una aprobación interactiva
pendiente. `.claude/settings.json` se menciona en el motor, pero no se abrió ni
se copió en este inventario.

Hay siete plantillas, pero la ejecución inicial añade instrucciones embebidas
en `executor_prompt` (1075), `executor_instructions` (1359) y
`DETERMINISTIC_EXECUTOR_PROMPT` (854). Extraer solo `prompts/` sería incompleto.
`MODEL_POLICY.md` menciona 50 turnos; `config.yaml` fija 100 y `claude_exec` usa
ese valor efectivo. Es una contradicción del origen ya señalada en la
especificación, no una modificación de diseño en esta entrega.

## Evidencia y límites

Se leyó código/configuración/esquemas y se inspeccionaron secciones relevantes
de documentación, prompts y tests. No es una auditoría exhaustiva de seguridad,
de todas las ramas ni del historial. No se abrió `.harness/runs`, no se copió
ninguna conversación, prompt privado, credencial o dato de aplicación, ni se
ejecutó el harness, helpers, instalaciones, tests de ReferenceProject o proveedores.

Los casos de [fixtures](../../tests/fixtures/legacy/README.md) son construidos
desde los formatos estáticos; no demuestran que una CLI instalada hoy emita esos
campos. El chequeo local verifica parseo, referencias y coherencia de las muestras,
sin implementar importación, persistencia ni parsers de proveedores. H0.2 y H0.3
siguen pendientes.

## Criterios de H0.1 verificados

[Alcance original](H0.1_SCOPE.md) conservado al actualizar NEXT_STEPS.

| Criterio original | Evidencia de la entrega |
|---|---|
| Trazar formatos a archivos/funciones y revisión | Commit y 21 pares de hashes en `baseline.json`; productores/esquemas y líneas en `LEGACY_FORMATS.md` |
| Fixtures sin datos reales, secretos ni transcripciones copiadas | Muestras Demo redactadas desde cero; solo cuatro esquemas estáticos copiados, con hashes comprobados |
| Distinguir completos, incompletos y campos no registrados | Manifest de fixtures, ausencias/nulls declarados, executor sin final y review parcial; checks de parseo y escenarios |
| No ejecutar agentes, instalaciones o tests del origen | Inspección estática; cuatro checks propios solo con biblioteca estándar y lectura local |
| Informar verificaciones y límites | README de fixtures, STATE y secciones de límites de ambos documentos discovery |

Comprobación final de lectura: HEAD, estado Git y los 21 hashes del origen
coinciden con la captura inicial. Los cuatro checks pasan; revisados los cambios
frente a la documentación inicial y los archivos añadidos. La referencia no
se modificó. Las muestras ocupan aproximadamente 54 KB incluidos sus esquemas
y manifest; no requieren infraestructura de test ni llamadas externas.

# P010 — Matriz de aceptación global

Fecha: 2026-10-22. Base: `54a5b5b` (T001–T006 y T011). Tarea: P010-T007. Decisión:
[D149](../DECISIONS.md#d149--p010-t007-matriz-de-aceptación-sse-por-cursor-y-tarea-t012).
Parte de la [matriz inicial de T001](P010-T001_CONTRATO_CONSOLIDACION.md#4-matriz-inicial-de-aceptación-specification-10).
**Estado:** matriz completa; once criterios cumplidos en el alcance offline, dos con evidencia real pendiente de la
decisión de T008 y un hueco de §9 acotado como P010-T012. Sin proveedores, servicios operativos ni smokes.

## 1. Método

- **Offline:** cada test citado existe en la base y pasa en la ejecución de §4 (Git/SQLite temporales, agentes y
  comandos falsos). «Reejecutado» significa esa ejecución, no un resultado de fases anteriores.
- **Real:** operaciones con proveedores ya archivadas. Son históricas: se hicieron con el adaptador y el paquete de su
  momento (`cli-4` en D050, `cli-9` en D071, `cli-12`/`cli-13` en D139) y no se repiten aquí.
- **Producto frente a hijo:** la evidencia de P009 acredita el producto sobre un hijo Django. Las pruebas del propio
  Django (pytest, ruff, mypy del hijo) son evidencia de la aplicación hija, no del harness, y no cuentan aquí.
- Un criterio cumple cuando su enunciado completo tiene evidencia offline vigente. La falta de uso real se anota como
  límite; no lo convierte en cumplido ni en fallo.

## 2. Criterios de SPECIFICATION §10

| # | Criterio | Evidencia offline (reejecutada) | Real (histórica) | Dictamen y límites |
|---|---|---|---|---|
| 1 | Importar dos veces un historial no duplica ni inventa | `test_legacy_import.py`: `test_all_five_scenarios_are_read_only_and_idempotent`, `test_absent_null_and_observed_zero_remain_distinct` | No | **Cumple.** Importación legacy; A/B se cubren en el 11. |
| 2 | Ejecución → fallo de test → corrección → revisión → commit con historial completo | **Nuevo** `test_acceptance_matrix.py::test_failed_test_correction_review_and_commit_keep_the_whole_history`; `test_engine.py::test_revise_uses_explicit_selection_new_session_and_preserves_all_history`, `::test_changed_validation_allows_correction_despite_unchanged_files`; `test_managed_api.py::test_http_flow_executes_reviews_and_commits_once_across_double_submit_and_restart` | D050, D071, D139 | **Cumple.** Antes de T007 la cadena completa por la API solo existía a trozos (motor hasta `acceptance_ready`; API sin corrección). |
| 3 | Sin dos escritores por checkout, ni tras reiniciar con proceso vivo | `test_managed.py`: `test_threaded_double_requests_and_claims_invoke_once`, `test_processes_share_idempotency_and_writer_lock`; `test_cli_agents.py`: `test_recovery_blocks_live_owner_and_group_after_lease`, `test_actual_owner_crash_restart_retains_group_lock_and_bytes`; `test_git.py::test_commit_job_holds_the_checkout_writer_lock` | No | **Cumple.** Contención cooperativa (POSIX, locks y sandbox de cada CLI), sin aislamiento del sistema operativo (D064, D065). |
| 4 | Una denegación no ejecuta; aprobación caducada o doble no se reutiliza | `test_permissions.py`: `test_denial_prevents_executor_call_and_replacement_restores_explicit_retry`, `test_expiry_at_decision_and_at_next_attempt`, `test_cli_checks_expiry_again_at_launch_boundary`, `test_crash_after_intent_never_reuses_once_grant`, `test_concurrent_grant_and_deny_only_one_commits` | No | **Cumple.** |
| 5 | Reinicio sin efectos a ciegas; caída tras el commit conciliada | `test_managed.py`: `test_persisted_history_snapshots_results_events_survive_restart`, `test_crash_during_correction_reserves_budget_and_needs_explicit_recovery`; `test_e2e_offline.py::test_quarantine_survives_restart_and_recovery_never_repeats_executor`; `test_managed_api.py::test_recovery_over_http_requires_explicit_confirmation_and_never_repeats_the_executor`; `test_git.py::test_crash_around_the_git_effect_recovers_without_duplicate_commit` | Reinicios y recuperación en el piloto P009 (D130, D134), sin una ejecución en curso | **Cumple** offline. El reinicio con una ejecución real en curso no se ha observado. |
| 6 | Editar prompts no cambia el intento pasado | `test_prompts.py`: `test_activation_during_attempt_keeps_snapshot_and_future_attempt_uses_new_version`, `test_restart_stopped_run_pins_catalog_and_preserves_attempts` | No | **Cumple.** T004 cambió la plantilla `define-project` con identidad nueva, sin tocar catálogos congelados (D146). |
| 7 | Un cambio tras el diff revisado invalida la aceptación | `test_engine.py`: `test_content_change_during_review_invalidates_acceptance`, `test_content_change_during_validation_requires_revalidation`; `test_git.py::test_content_changed_between_intent_and_effect_never_commits` | No | **Cumple.** |
| 8 | Cierre con validación y autorización vigentes; archivo sin pérdida | `test_phases.py`: `test_stale_ready_never_closes_and_requires_new_evidence`, `test_authority_change_during_check_downgrades_ready`, `test_batch_and_close_authorizations_are_distinct_explicit_and_audited`; `test_phase_closure.py`: `test_unified_closure_exact_archive_and_successor_without_plan`, `test_closure_refuses_before_tag_or_writes`, `test_closure_recovery_reuses_tag_commit_and_successor` y los tres casos de T005 | D139 (cierre y archivo de P001 del hijo) | **Cumple.** T005 cambió la presentación, no el check (D147). |
| 9 | Otro perfil sin cambiar el núcleo | `test_engine.py::test_reference_project_rules_are_in_declarative_profile_not_core`; `test_declared_profiles.py`; `test_typescript_profile.py`; `test_typescript_preparation.py::test_both_recipes_coexist_and_django_keeps_its_fingerprint_and_hash` | Receta Django (D139); `typescript-web` en D050/D071 | **Cumple** offline. El perfil declarado de D095 no tiene uso real: decisión en T008. |
| 10 | Una petición del chat queda ligada a una tarea y su resultado | `test_chat.py`: `test_confirmed_proposal_becomes_a_linked_task_planned_executed_reviewed_and_committed`, `test_http_chat_flow_with_guard_confirmation_and_linked_task` | No localizada | **Cumple** offline. Sin uso real; T008 decide si se busca o se declara. |
| 11 | Proyecto vacío con primera tarea ejecutable; importación sin perder historial | `test_e2e_offline.py::test_create_confirm_restart_then_first_task_and_commit`; `test_typescript_preparation.py::test_new_child_definition_preparation_and_first_task_with_profile_validations` (variante falsa); `test_django_journey.py`; `test_import_commit.py`: `test_three_origins_confirm_one_commit_preserve_bytes_and_adopt_phase`, `test_import_migration_keeps_history`, `test_crash_reconciles_exactly_the_sealed_commit`; `test_onboarding_commit.py::test_confirm_one_documentary_commit_preserves_code_and_adopts_p001` | Creación Django desde la UI (D127, D139); A/B no | **Cumple** offline. El hueco `typescript-web` de T001 queda cerrado por T002 (D143); su variante con node/npm reales se omite sin caché explícita. A/B sin uso real: T008. |
| 12 | Backup y restauración con estados, referencias y hashes | `test_backup.py` (20 casos, entre ellos `test_junit_snapshots_events_and_http_queries_survive_restore` y `test_corrupt_or_incompatible_backup_never_creates_restore`); `test_run_projection.py::test_backup_rejects_a_projection_that_differs_from_the_history` | No | **Cumple** offline tras T003: la proyección viaja en el backup y se contrasta con el historial. Sin uso real. |
| 13 | Salida fuera de esquema; ciclos sin cambios; SSE sin huecos ni duplicados | `test_engine.py`: `test_invalid_review_is_retained_without_new_call`, `test_no_progress_loop_stops_before_another_executor`; `test_typed_json_schema.py`; `test_cli_agents.py`; SSE legacy en `test_legacy_observation.py`; **nuevo** `test_acceptance_matrix.py::test_event_cursor_resumes_across_a_restart_without_gaps_or_duplicates` | No | **Cumple con la interpretación de D149:** en la UI gestionada el cursor por secuencia (D029) sustituye al SSE; el SSE literal existe y se prueba en la observación legacy. |

## 3. Requisitos no funcionales (SPECIFICATION §9)

| Requisito | Evidencia | Dictamen |
|---|---|---|
| Ninguna vista lee un historial completo | `test_run_projection.py`: `test_large_history_reads_are_bounded_and_equivalent` (26 MiB), `test_lists_and_auxiliary_reads_never_select_the_history`, `test_migration_backfills_formats_1_to_8_with_previous_results`; `test_metrics_projection.py::test_large_scope_is_read_without_histories_and_matches` (35,4 MiB) | **Cumple** (D144, D145). El motor y el envío confirmado de la exportación siguen leyendo el historial, fuera del requisito de vistas. |
| Migraciones explícitas con backup previo | `scripts/dev` con `storage/migrate.py` (D053) en desarrollo; el paquete instalado no tiene orden de migración (D043) | **Hueco.** Una base operativa anterior no arranca con el paquete nuevo. Se acota como **P010-T012** (D149) antes de T009. |
| Adaptador CLI no caracterizado bloqueado con diagnóstico | `test_cli_baseline.py::test_uncharacterized_neighbours_are_still_rejected` (Codex 0.162.2/0.164.0, Claude 2.1.299, 2.1.300, 2.1.301 y 2.1.303; D122) | **Cumple.** |
| Backup consistente y restauración solo de consulta | Criterio 12 | **Cumple.** |
| Wheel con assets y migraciones; Node solo para construir | D043, D126 (wheel de P009) | Vigente en diseño; el wheel de P010 se verifica en T009. |

## 4. Ejecución sobre la base

| Comprobación | Resultado |
|---|---|
| `pytest -q` (paralelo), 1.ª ejecución, base `54a5b5b` sin los tests nuevos | 1653 pasan, **1 falla**, 2 omitidos, 121 subtests |
| `pytest -q` (paralelo), 2.ª ejecución, con los tests nuevos | 1656 pasan, 2 omitidos, 121 subtests |
| `pytest -q -n 0 tests/product/test_acceptance_matrix.py` (tests nuevos) | 2 pasan |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 12 pasan |
| `node --test frontend/tests/*.test.mjs` | 82 pasan |
| `alembic upgrade head` y `alembic check` en una SQLite temporal | sin operaciones nuevas |

Omisiones esperadas: las variantes con Django y node/npm reales, sin wheelhouse ni caché explícitos.
**Fallo intermitente:** en la 1.ª ejecución `test_commands.py::test_product_runner_typescript_offline_exact_evidence_and_commit[correct]`
registró un solo proceso de comando en lugar de seis (con node/npm reales y 628 % de CPU). Pasa aislado y en serie (4/4),
en tres ejecuciones del archivo en paralelo (40/40) y en la 2.ª ejecución completa. No es de T007 ni se ha
diagnosticado su causa; T009 lo vigila al repetir la suite.

Tipos, build y OpenAPI no aplican: no cambian API ni UI. Las referencias de la matriz inicial se comprobaron por
nombre; todas existen.

## 5. Observaciones registradas

- **`tests/**` protegido en `typescript-web`** (T001 §5): el ejecutor normal no puede crear ni modificar tests en
  `tests/`; las tareas de un hijo TypeScript solo cambian tests si una tarea futura lo decide. Límite documentado en
  ARCHITECTURE §10 (T006), sin cambio de producto.
- **Manifiesto fijo tras preparar**: límite de D119/D143, documentado en T006.
- **Evidencia real sin repetir**: chat, backup, A/B, perfil declarado y receta TypeScript no tienen uso real; la
  propuesta y la decisión corresponden a T008. Ningún criterio se cierra por figurar completada su fase original.
- **Test intermitente** de `test_commands.py` con node/npm reales bajo carga (§4); sin bloqueo, en observación.
- **Sin bloqueos del alcance declarado** salvo el hueco de §9, que T012 corrige antes de la verificación final.

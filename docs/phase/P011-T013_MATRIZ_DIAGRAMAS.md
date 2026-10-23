# P011-T013 — Semantic audit of diagrams and flows

Implemented on 2026-10-23 from `b4bb2fb` (clean checkout). The user's instruction authorizes this next task and one
local commit in English. Criteria: [NEXT_STEPS T013](../NEXT_STEPS.md#p011-t013--auditoría-semántica-de-diagramas-y-flujos)
and exit criterion 5 of the [T001 contract](P011-T001_CONTRATO_APERTURA.md) (D159). Decision: D175.

Scope: the 14 current flow documents (23 diagrams), the 12 ER diagrams of `DDBB-DIAGRAM.md` against the SQLAlchemy
metadata, and the textual architecture in `ARCHITECTURE.md` (it has no diagrams). Archived diagrams under
`docs/archive/**` were not edited. Flows keep their current language (mostly Spanish, two in English): the public
English documentation baseline belongs to T014; this task corrects content, not language.

## Method

1. Each diagram node/transition that states behavior was traced to the function that implements it and to at least
   one test that exercises it. Transitions present in code but absent from a drawing were treated as findings, as
   well as drawn transitions that the code does not perform.
2. `P011-T013_er_parity.py` compares every ER entity with `Base.metadata`: tables, columns, types (`string` ≠ `text`),
   PK/FK/UK flags (a non-partial single-column unique index counts as UK), nullability (`"null…"` comment), a drawn
   relation per foreign key, and composite uniqueness/unique indexes named in the prose under each diagram.
3. `P011-T013_mermaid_check.mjs` parses every Mermaid fence with the local Mermaid 11.17.2 from `frontend/node_modules`.
   DOMPurify is replaced by an inert stub because it needs a DOM: syntax only, without label sanitization, layout or
   rendering. A passing parse does not prove semantic parity; that is what the matrix below is for.
4. `P011-T013_links.py` resolves relative links and GitHub-style anchors of the current Markdown files.

## Findings and resolution

All findings were documentation discrepancies: the code and its tests describe the behavior, so the drawings were
corrected; no product behavior was changed to fit a drawing. Two drawn transitions had no test at run level, so two
regression tests were added (F02); both passed on the unchanged code.

| # | Document | Finding | Resolution |
|---|---|---|---|
| F01 | `language-preferences.md`, `database-migration.md` | Both sequence diagrams failed to parse: `;` ends a Mermaid sequence message | Semicolons replaced by commas; both parse |
| F02 | `task-run.md` (states) | Missing transitions: retries from `BLOCKED`/`REVISION_LIMIT`/`INTERRUPTED`; commit queued from `ACCEPTANCE_READY` → `QUEUED` → `COMMITTING`; `COMMITTING → STOPPED` (`INVALIDATED`), `COMMITTING → RECOVERY_REQUIRED`; `RECOVERY_REQUIRED → COMMITTED` when the commit is already recorded; `DISCOVERING` stage | Diagram and notes redrawn from `storage/managed.py` (`resume`, `_queue_commit`, `commit_intent`, `commit_result`, `confirm_stopped`, `refuse`); new tests `test_git.py::test_crash_after_the_recorded_commit_recovers_as_committed_without_another_commit` and `test_managed.py::test_mode_change_after_admission_refuses_the_claim_before_any_effect` |
| F03 | `task-run.md` (sequence) | Admission omitted the work-language (D167) and CLI (D174) refusals; the per-attempt CLI revalidation was not drawn; the job sealed "visual language" only | Admission note and CLI note added; `language-context-1` named |
| F04 | `chat.md` | `/tarea` was drawn as a side-effect-free preview; it queues a `chat_command` turn that answers with a deterministic proposal, without HEAD export or agent | Separate branch; `UNKNOWN`/`REFUSED` and protocol-token commands explained |
| F05 | `documents.md` | AGENTS/CLAUDE/GEMINI "written by confirmed A/B imports" | Only B onboarding; A retired (D161) with link to compatibility |
| F06 | `phase-lifecycle.md` (states) | `NOT_READY` and failures were merged into one arrow to `ACTIVE`; drift as a reconciliation cause, questions from `NEEDS_RECONCILIATION`/`READY_TO_CLOSE`, `READY_TO_CLOSE → ACTIVE` (adoption/amendment), abandonment from `READY_TO_CLOSE` and the return of failed/aborted operations to the previous state were missing | Diagram redrawn from `storage/phases.py` and `core/engine/phases.py`; previous-state rule in prose (not expressible as one state arrow) |
| F07 | `project-creation.md` | The flowchart mixed the product with the P009 pilot (four-pair matrix, QA, exit review); TypeScript recipe and work language missing | Product flowchart (optional recipe, work language, links per stage); pilot moved to a marked historical paragraph; title no longer Django-only |
| F08 | `project-creation.md` (states) | `BLOCKED → INTENDED` (resume without folder, same authority) and `DIRECTORY_CREATED → RECOVERY_REQUIRED` (I/O failure before registration) missing | Added from `services/project_creation.py` (`resume`, `advance`) |
| F09 | `project-work-language.md`, `project-preparation.md`, `ARCHITECTURE.md` §3 | `work_language` and v2 recipes described for `local-config-6` only; `WORK_FORMATS` is v6 and v7 | "v6/v7" in diagrams and text |
| F10 | `project-agents.md` | Presets "TOML v5" with CLI validated at load; since D174 loading is data-only and v7 resolves effective clients separately | Node for the separate resolution; v5–v7; blocker wording includes B and retained import data |
| F11 | `cli-compatibility.md` | Refusal nodes ended in "explicit resolution" without the run consequence | `JournalError` → quarantine → `RECOVERY_REQUIRED` → `confirm-stopped`; admission refusal before any run |
| F12 | `database-migration.md`, `ARCHITECTURE.md` §9 | "Stop the service, observers and writers": observers were retired in T019 | "Service and writers" |
| F13 | `project-onboarding.md` | Work language (registration, 409, documents and `phase-000/SUMMARY.md`) not mentioned for B | Language paragraph with link |
| F14 | `DDBB-DIAGRAM.md` | `chat_conversations.idempotency_key` and `planning_conversations.idempotency_key` lacked `UK` while other nullable unique-index columns carry it | `UK "null"`; parity script clean |

Residual observation outside the allowed paths, without behavioral effect: the CLI help `cli.help.writers_stopped`
(`i18n/en.json`/`es.json`) still says "observers". Owner: T014 (public wording) or T017 review; the flag's semantics
is unchanged.

## Matrix: flow → code → tests

Result column: **OK** traced without change; **Fn** corrected by that finding.

### Task run (`task-run.md`)

| Node / transition | Code | Tests | Result |
|---|---|---|---|
| task-sources, `source_sha256` 409, notes | `api/managed.py`, `storage/managed.py::submit` | `test_task_sources.py` | OK |
| Admission: registry, preparation, work language, CLI minimum | `_queue_new_run`, `_registry_current`, `preparation.admit`, `_language` | `test_cli_discovery.py::test_loading_is_data_only_and_unresolved_versions_cannot_be_queued`, `test_work_language.py::test_unconfirmed_roots_admit_no_new_work_and_continuations_keep_their_pair` | F03 |
| Claim, lease, lock; expired lease never requeues | `claim`, `recover_expired` | `test_managed.py::test_expired_lease_never_unlocks_or_requeues`, `test_processes_share_idempotency_and_writer_lock` | OK |
| AGENTS.md per attempt, directive, CLI per attempt | `core/engine/prompts.py::render_attempt`, `adapters/cli_agents.py::invoke` | `test_project_instructions.py`, `test_language_directive.py`, `test_cli_discovery.py` | F03 |
| Plan → execute → format → validate → review loop | `core/engine/workflow.py`, `checkpoint`, `agent_started` | `test_engine.py`, `test_profile_formatter.py`, `test_acceptance_matrix.py` | OK |
| ACCEPT/BLOCKED/REVISION_LIMIT terminals | `workflow.py` 210–341, `finish` | `test_managed.py::test_crash_during_correction_reserves_budget_and_needs_explicit_recovery` | OK |
| Retry/revalidate from STOPPED/BLOCKED/REVISION_LIMIT/INTERRUPTED | `resume` | same test, `test_managed.py::test_explicit_retry_after_failed_execution_uses_new_attempt` | F02 |
| Exception/persistence failure → RECOVERY_REQUIRED; confirm → INTERRUPTED | `services/managed.py::_run_claimed`, `quarantine`, `confirm_stopped` | `test_managed.py::test_result_write_failure_preserves_unknown_intent_and_stops_next_effect` | OK |
| Claim-time mode guard → REFUSED, lock released, no attempt | `services/managed.py::_run_claimed`, `refuse` | **new** `test_managed.py::test_mode_change_after_admission_refuses_the_claim_before_any_effect`; admission-time 409 in `test_managed_api.py::test_mode_refusals_return_409_with_diagnostic_and_no_partial_effects` | F02 |
| Commit: QUEUED → COMMITTING → COMMITTED with CAS | `_queue_commit`, `commit_intent`, `commit_result` | `test_git.py::test_crash_around_the_git_effect_recovers_without_duplicate_commit` | F02 |
| COMMITTING → STOPPED (INVALIDATED) | `commit_result` (`invalidated`), `finish` | `test_git.py::test_content_changed_between_intent_and_effect_never_commits`, `test_head_moved_before_the_commit_object_exists_invalidates` | F02 |
| RECOVERY_REQUIRED → COMMITTED | `confirm_stopped` (`_live_commit`) | **new** `test_git.py::test_crash_after_the_recorded_commit_recovers_as_committed_without_another_commit` | F02 |
| Run projection in the same transaction; cycle pages | `storage/run_projection.py`, `managed_views.py` | `test_run_projection.py`, `test_cycle_diff.py` | OK |

### Chat, documents, phase

| Node / transition | Code | Tests | Result |
|---|---|---|---|
| Command previews without effects; closed grammar | `core/engine/chat_commands.py::parse`, `storage/chat.py::command_preview` | `test_chat_global.py::test_slash_commands_never_fall_back_to_a_model`, `test_all_command_previews_are_read_only_and_bind_the_observed_context` | OK |
| `/tarea` deterministic turn | `submit_message` (`chat_command`), `services/managed.py` | `test_chat_global.py::test_task_command_is_idempotent_proposal_without_snapshot_or_agent` | F04 |
| HEAD export, fresh read-only turn, writes discard | `adapters/chat_snapshot.py`, `core/engine/chat.py` | `test_chat.py::test_turn_freezes_explicit_context_before_a_fresh_read_only_invocation`, `test_turn_that_writes_to_the_checkout_is_discarded` | OK |
| Turn UNKNOWN/REFUSED on recovery/refusal | `storage/chat.py::abort` | `test_chat.py` (confirm-stopped case), `test_chat_global.py` | OK |
| Task commit blocks, confirmed edit, export preview/projection | `core/engine/documents.py`, `document_ops.py`, `document_export.py` | `test_documents.py`, `test_document_export.py::test_crash_recovery_reuses_intent_without_duplicate_commits` | F05 |
| Check verdicts, budgets, drift, NOT_READY | `core/engine/phases.py::check_phase`, `CHECK_STATUS` | `test_phase_closure.py::test_state_budgets_require_reconciliation_without_agent`, `test_phases.py::test_stale_ready_never_closes_and_requires_new_evidence` | F06 |
| Questions from any open state; answers | `raise_question`, `answer` | `test_phases.py::test_stale_binding_or_authority_change_is_refused_before_queueing`, `test_agent_blocking_questions_are_persisted_and_block_progress` | F06 |
| Reconcile/amend from READY_TO_CLOSE → ACTIVE | `reconcile`, `amend` | `test_phases.py::test_revise_requires_reconciliation_and_reconcile_is_bound_to_reviewed_documents`, `test_phase_adjustments.py::test_amendment_keeps_previous_definition_and_invalidates_ready_and_batches` | F06 |
| Close/abandon, tag intent, recovery, failure → previous state | `submit_close`, `settle`, `abort`, `storage/closure.py` | `test_phases.py::test_crash_after_tag_intent_is_reconciled_only_by_an_explicit_new_close`, `test_phase_closure.py::test_closure_recovery_reuses_tag_commit_and_successor`, `test_abandon_archives_without_ready_and_does_not_create_tag` | F06 |
| Closed-phase evidence | `closure_view`, `expected_documents` | `test_phases.py`, frontend `tests/*.test.mjs` | OK |

### Entries: creation from scratch and onboarding B

| Node / transition | Code | Tests | Result |
|---|---|---|---|
| Folder authority, preview/confirm, mkdir, registration | `services/project_creation.py` | `test_project_creation.py::test_new_child_preview_and_confirm_without_toml_roots_restart_and_revocation` | F07 |
| Creation states incl. crashes, BLOCKED, resume, cancel | `advance`, `reconcile`, `resume`, `cancel` | `test_crashes_conserve_evidence_and_never_adopt_uncertain_folder`, `test_revoke_reselect_and_resume_owned_child_preserves_original_intent`, `test_cancel_keeps_uncertain_reservation_and_blocks_existing_registration` | F08 |
| Definition turns, drafts CAS, root commit, P001 | `core/engine/definition.py`, `storage/planning.py`, `storage/bootstrap.py` | `test_definition.py::test_empty_folder_to_root_commit_with_p001_and_phase_000`, `test_acceptance_blockers_are_explicit_and_fail_closed` | OK |
| Recipe preparation, receipt guard on tasks/checks/close | `services/project_preparation.py`, `storage/preparation.py::admit` | `test_project_preparation.py`, `test_typescript_preparation.py`, `test_recipe_v2_preparation.py` | F07, F09 |
| Work language at registration/creation/TOML/explicit | `storage/registry.py::confirm_work_language`, `services/work_language.py`, `local_config.WORK_FORMATS` | `test_work_language.py` (all) | F09 |
| B inventory, conversation, preview/confirm, recovery | `adapters/project_onboarding.py`, `storage/onboarding*.py`, `core/engine/onboarding_commit.py` | `test_project_onboarding.py`, `test_onboarding_conversation.py`, `test_onboarding_commit.py::test_crash_reconciles_same_intent_commit_and_phase` | F13 |
| Shared B infrastructure kept (`project_imports`, `import_commit`, Git boundary) | `storage/project_import.py`, `core/engine/import_commit.py`, `adapters/import_git.py` | `test_import_git_boundary.py`, `test_import_local_objects.py`, `test_import_submodules.py` | OK |

### Agents, CLI, languages, migration, compatibility

| Node / transition | Code | Tests | Result |
|---|---|---|---|
| Presets, selection, blockers, superseded plans | `storage/registry.py::_configuration_blockers`, `_supersede_plans` | `test_project_agents.py::test_four_pairs_switch_on_one_registration_with_restart_and_stale_admission` | F10 |
| Automatic discovery, minimum, per-attempt identity, pre-GO stop | `adapters/cli_compatibility.py`, `cli_diagnostics.py`, `cli_agents.py` | `test_cli_discovery.py::test_updated_client_is_detected_for_new_work_but_old_job_is_quarantined`, `test_pre_go_replacement_stops_the_gated_group_without_invoking_client` | F11 |
| Preferences CAS, frozen visual, invalid row | `storage/preferences.py`, `api/managed.py` | `test_preferences.py` (all) | F01 |
| Directive and documents in the work language | `core/engine/language.py`, `document_text.py` | `test_language_directive.py` | OK |
| Installed migration with snapshot | `storage/migrate.py`, `cli.py` | `test_installed_migration.py` | F01, F12 |
| Retired A/legacy: no routes, commands, observers; quarantine | `storage/retired_work.py`, `core/managed_mode.py` | `test_legacy_retirement.py` (all) | OK |

Legacy/A check: no `/api/legacy/**` or managed `/import` route in `api/` or the generated client, no `legacy` route in
`frontend/src/router.ts`, `legacy-import`/`legacy-summary` rejected at parsing (`test_removed_cli_rejects_before_opening_any_database`).
The only two product entries drawn as current are creation from scratch and onboarding B; `legacy-migration.md`
describes compatibility only.

## Checks

- Mermaid: 35 diagrams parse (12 ER, 15 flowcharts, 5 sequences, 3 state diagrams); before the fix, 2 failures (F01).
- ER parity: 51 tables, 520 columns, 12 ER blocks and 60 drawn relations against the metadata of Alembic
  `0025_project_work_languages` (head); no differences after F14.
- Links: 727 relative links/anchors of current Markdown files (including this delivery), none broken;
  `git diff --check` clean.
- `pytest -q` (parallel): 1669 passed, 2 skipped, 29 subtests, only the known Starlette/httpx warning; it included the
  new `test_git.py` case. The new `test_managed.py` case was added afterwards and `tests/product/test_managed.py`
  was rerun alone: 30 passed. `python3 -m unittest discover -s tests -p 'test_*.py'`: 8 tests OK.
- `alembic upgrade head` + `alembic check` on a temporary SQLite in the session scratchpad: no new operations. A first
  `alembic check` without `HARNESS_DATABASE_URL` read the default `.local/harness.sqlite3` and reported it behind
  head; it only reads, so that database was left untouched.
- Node tests, `npm run check`/`build` and OpenAPI regeneration were not run: no frontend, API or schema file changed.

Not done: Mermaid layout/DOM rendering or browser QA, translation of the flows (T014), providers, real CLIs, services,
network, the harness on this checkout. Synthetic tests do not prove real use.

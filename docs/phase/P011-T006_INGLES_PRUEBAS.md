# P011-T006 — English comments: tests and fixtures

Implemented on 2026-10-23 from `2aa2c9d` (clean checkout). The user's instruction authorizes this next task and one
local commit in English. Precedents: D154/D159/D162–D164, [T001 inventory](P011-T001_INVENTARIO.md) treatments F and
E2; implementation decision D165.

HITL (2026-10-23), one question the documents left open, answered by the user:

1. The three fixture READMEs (`tests/fixtures/cli_help`, `streams`, `typescript_web`) are Spanish developer
   documentation; T001 marks `streams/` as E2 ("preserve bytes") → **translate all three**. They describe the
   fixtures and no test hashes them; the JSONL streams, the manifest, the real CLI help texts and the synthetic child
   application keep their bytes. Links to `docs/archive/` stay; T014 decides how the public baseline handles them.

## Scope and method

Every T001 row owned by T006: the 80 Python files under `tests/` (suites, probes, helpers, conftest files and the
`e2e` fixture), the eight `frontend/tests/*.test.mjs` files and the fixture folders. Each file was reviewed whole.
Python comments were extracted with `tokenize` and docstrings with `ast` (536 comments and 139 docstrings in total),
classified by a Spanish detector plus a manual pass over the remainder (ten Spanish comments the detector missed were
added), and translated by hand through a table keyed by file/line/kind, applied bottom-up so positions stay exact.
No automatic translation or bulk substitution. Section dividers (`# --- … ---`) keep their width; no changed line
exceeds 120 characters or the line it replaces.

Not translated, by contract (F/E2):

- Expectations of product messages and labels (`distinta de la congelada`, `fuera del checkout`,
  `Preparación sin resolver`, the v1 recipe step labels, the phase SUMMARY table headers, es-ES formats in
  `metrics.test.mjs`) → they change together with their source in T009/T010.
- Bilingual D088 document fields (`**Objetivo:**`, `**Rutas permitidas:**`, `## Fase activa`, …) and chat commands
  (`/tarea`, `/estado`): grammar under test, kept.
- Synthetic user content (questions, answers, drafts, briefs, Spanish document text) and Unicode probes (`ñ`, `€`,
  `café 🚀`): test data, kept.
- Stream fixtures (`*.jsonl`, `manifest.json`), real CLI help texts and the visible text of the `typescript_web` child
  application (`lang="es"`, labels, `minutos`, the `entero` error checked by its tests): fixture data, bytes preserved.
- Internal references (`H6.2 E3`, `DNNN`, `PNNN-TNNN`, `docs/archive/...`) inside comments and docstrings are kept, as
  in T003–T005; T014 decides how the public baseline explains them.

Test-owned strings that are neither expectations nor data were translated: one `AssertionError` diagnostic and two
synthetic exception messages with their `match=` patterns (`test_core.py`, `test_run_projection.py`) and two
`pytest.skip` reasons (`test_project_creation.py`).

Identifiers: Python names (AST: functions, classes, arguments, attributes, names) checked against the T001 stem list.
The only Spanish one was the test name flagged by T001, renamed to
`test_task_command_is_idempotent_proposal_without_snapshot_or_agent`; the `tarea` command, its inputs and its
expectations are unchanged. The other matches were English (`base`, `base_revision`).

## Resolved inventory

C = comment lines translated, D = docstrings translated. Files of the T006 group not listed were already English in
comments and docstrings (probes, `session_client.py`, CLI/permission/retention/smoke suites, among others).

| File (under `tests/`) | C | D |
|---|---:|---:|
| `conftest.py` | 0 | 1 |
| `product/cli_process_probe.py` | 2 | 1 |
| `product/conftest.py` | 0 | 2 |
| `product/managed_process_probe.py` | 0 | 1 |
| `product/onboarding_helpers.py` | 0 | 1 |
| `product/test_acceptance_matrix.py` | 2 | 3 |
| `product/test_agent_roles.py` | 1 | 0 |
| `product/test_backup.py` | 6 | 2 |
| `product/test_bootstrap.py` | 5 | 6 |
| `product/test_chat.py` | 24 | 1 |
| `product/test_cycle_diff.py` | 7 | 1 |
| `product/test_declared_profiles.py` | 3 | 3 |
| `product/test_definition.py` | 28 | 5 |
| `product/test_dev_command.py` | 2 | 1 |
| `product/test_document_export.py` | 6 | 1 |
| `product/test_document_viewer.py` | 6 | 2 |
| `product/test_documentation_parity.py` | 4 | 2 |
| `product/test_documents.py` | 23 | 3 |
| `product/test_e2e_offline.py` | 0 | 1 |
| `product/test_engine.py` | 2 | 1 |
| `product/test_git.py` | 24 | 3 |
| `product/test_import_git_boundary.py` | 0 | 2 |
| `product/test_import_local_objects.py` | 0 | 2 |
| `product/test_import_submodules.py` | 0 | 2 |
| `product/test_import_writer_local_objects.py` | 4 | 2 |
| `product/test_junit.py` | 4 | 1 |
| `product/test_local_config.py` | 0 | 1 |
| `product/test_managed.py` | 5 | 1 |
| `product/test_managed_api.py` | 10 | 3 |
| `product/test_metrics.py` | 25 | 5 |
| `product/test_metrics_projection.py` | 13 | 5 |
| `product/test_onboarding_commit.py` | 0 | 1 |
| `product/test_onboarding_conversation.py` | 1 | 1 |
| `product/test_phase_adjustments.py` | 27 | 2 |
| `product/test_phase_closure.py` | 7 | 1 |
| `product/test_phases.py` | 15 | 1 |
| `product/test_project_agents.py` | 0 | 2 |
| `product/test_project_creation.py` | 7 | 1 |
| `product/test_project_instructions.py` | 3 | 2 |
| `product/test_project_onboarding.py` | 2 | 1 |
| `product/test_project_registry.py` | 7 | 4 |
| `product/test_prompts.py` | 1 | 0 |
| `product/test_run_projection.py` | 11 | 3 |
| `product/test_storage_api.py` | 1 | 0 |
| `product/test_task_sources.py` | 0 | 1 |
| `product/test_typescript_profile.py` | 5 | 2 |
| `product/test_ui_routes.py` | 0 | 1 |
| `stream_probe.py` | 1 | 2 |
| `test_stream_contracts.py` | 0 | 1 |
| **Python total (49 files)** | **294** | **91** |

Frontend tests and fixtures:

| File | Change |
|---|---|
| `frontend/tests/diff.test.mjs` | 1 JSDoc and 4 comments |
| `frontend/tests/managed-api.test.mjs` | 3 inline comments |
| `frontend/tests/markdown.test.mjs` | 2 comments |
| `frontend/tests/metrics.test.mjs` | 5 test names; the `sin dato` label in a name is quoted as the current UI value |
| Other `frontend/tests/*.mjs` | Already English; residual Spanish literals are UI expectations → T010 |
| `tests/fixtures/{cli_help,streams,typescript_web}/README.md` | Translated (HITL 1); `typescript_web` now states that its visible Spanish text is fixture data |
| `tests/fixtures/e2e/installed_config.py` | Already English; bilingual D088 fields kept |
| `tests/fixtures/junit/*`, `streams/*.jsonl`, `manifest.json`, `cli_help/*.txt`, other `typescript_web/*` | Unchanged (data) |

Residual Spanish string literals after the task (candidate scan of non-docstring constants): 319 in 47 Python files and
about 34 lines in five `.mjs` files, all in the kept categories above. The scan is a candidate list, not a linguistic
certificate; T009/T010 re-inventory each expectation when they change its source.

## Validation and limits

- AST of the 51 changed Python files with docstrings blanked: identical to `HEAD` except the four intended changes
  (the renamed test and the three test-owned messages); the residual comment/docstring scan only returns English
  matches (`base`, the `«ñ»` sample).
- `python3 -m unittest discover -s tests -p 'test_*.py'`: 8 tests OK. `uv run --frozen --offline pytest -q` (xdist):
  1520 passed, 2 skipped, 29 subtests passed (same totals as T005; the 10 warnings are the existing Starlette/httpx
  deprecation). `node --test frontend/tests/*.test.mjs`: 82/82. `npm --prefix frontend run check` OK.
- Not run: `npm run build` and Alembic (no frontend source or schema change), services, agents, providers, smokes or
  network. The real-toolchain variants of the Django/TypeScript journeys stay opt-in and were not enabled.

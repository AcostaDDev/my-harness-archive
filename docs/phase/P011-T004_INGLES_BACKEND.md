# P011-T004 — English comments and identifiers: backend and recipes

Implemented on 2026-10-22 from `fa5bd06` (clean checkout). The user's instruction authorizes this next task and one
local commit in English. Precedents: D154/D158/D159/D162, [T001 contract](P011-T001_CONTRATO_APERTURA.md) §5 and
[inventory](P011-T001_INVENTARIO.md) treatments C, G and E1; implementation decision D163.

HITL (2026-10-22), two questions the documents left open, answered by the user:

1. Scope of the v2 recipes in T004 → **standalone v2 modules, not wired**: English source, scaffold parametrized by
   work language (en/es) only in technical prose, own fingerprint with version and language, English step labels with
   stable ids; not registered in configuration or preparation until `local-config-6` (T008).
2. Functional defaults of the child application in v2 → **keep them** (contract §5): `LANGUAGE_CODE = "es"`,
   `<html lang="es">` and visible text stay as in v1; they are a requirement of the child, not of W or V.

## Scope and method

Every Python file under `src/harness_local/**` outside `core/**` and `profiles/**` (T003): top-level modules, adapters,
API, CLI/launcher, migrations, recipes, services and storage — 94 files, including the G rows that T019 left in place
(`project_import`, `import_git`, `onboarding*`). Each file was reviewed whole, comments and docstrings extracted with
`tokenize`/`ast` and translated by hand, keyed by file/kind/line and applied bottom-up so positions stay exact.
No automatic translation or bulk substitution. Section dividers keep their width; no new line exceeds 120 characters
(or the length of the line it replaces, for a few pre-existing longer schema lines).

Technical schema descriptions are part of this task (T003/T004 alias "descripciones de esquemas"): the 84 Spanish
`description=` texts of `api/schemas.py`, `api/managed.py` and `api/security.py`, plus the route and model docstrings,
feed OpenAPI. `frontend/openapi.json` and `frontend/src/api.generated.ts` were regenerated with the documented
commands (E3), never edited by hand; the exported schema has no Spanish left.

Not translated, by contract:

- Visible messages, diagnostics, CLI help and HTTP error texts → T007/T010 catalogs (inventory below).
- Generated document prose, commit messages and prompts → T009 (V/W/T map).
- Bilingual D088 aliases and chat commands (`tarea`, `abrir-fase`, `## Fase activa` inside a prompt): kept.
- Frozen v1 recipe sources (E1): `recipes/django.py`, `recipes/typescript_web.py`, `django-packages.json`,
  `django-requirements.lock`; and the built-in `typescript-web` profile they hash (T003).
- Alembic revision ids, table/column names, persisted keys, formats and codes.

Identifiers: AST names were checked against the T001 list of Spanish stems; none were found besides literals, so no
renaming was needed.

## Recipes: v1 frozen, v2 prepared

The T001 §5 byte hashes of the four v1 sources are unchanged, and so are the v1 fingerprints
(`django-recipe-1` `f511c00a…e191`, `typescript-web-recipe-1` `4b1a8117…6485`); `tests/product/test_recipe_versions.py`
now pins all six values (the TypeScript fingerprint was not pinned before). Issued plans and receipts keep reading and
verifying the originals.

New modules, maintained in English and independent of the v1 sources:

| Module | Version | Work-language dependent content | Profile |
|---|---|---|---|
| `recipes/django_2.py` | `django-recipe-2` | `core/models.py` docstring | Same as v1 except English executor instructions |
| `recipes/typescript_web_2.py` | `typescript-web-recipe-2` | `tests/main.test.mjs` test description | Own copy of `typescript-web`, English JUnit label |

- With W = `es` the Django scaffold equals v1 byte for byte; with W = `en` only the model docstring differs. With W =
  `en` the TypeScript manifest equals v1; with W = `es` only the test description differs. Functional content
  (settings language, HTML language, visible text, runtime log lines) is the v1 content in both languages.
- Steps keep the v1 effects (kind, argv, cwd, environment, timeouts, order) and add a stable `id`; `label` is English
  human prose. The v1 preparation service keys checks on Spanish labels, so T008 must key v2 on `id`.
- `fingerprint(language)` hashes version, work language, scaffold/manifest, dependency closure (Django), effective
  profile and the module source. Invalid languages raise `ValueError`.
- Not wired: `recipes.RECIPES`/`by_version` and `project_preparation.RECIPES` only know v1. Selection, the composition
  binding, the TOML entry, label localization and preparation dispatch by id belong to T008/T009/T010.

## Resolved inventory

C = comment lines, D = docstrings, S = OpenAPI description literals translated. R = residual Spanish string literals
after the task (candidate scan of non-docstring constants and f-strings) and their owner. Files with all zeros were
already English.

| File | C | D | S | R → owner |
|---|---:|---:|---:|---|
| `__init__.py` | 0 | 1 | 0 | — |
| `adapters/__init__.py` | 0 | 1 | 0 | — |
| `adapters/bootstrap.py` | 10 | 5 | 0 | 1 → T010 |
| `adapters/chat_snapshot.py` | 0 | 1 | 0 | 1 → T010 |
| `adapters/cli_agents.py` | 4 | 0 | 0 | — |
| `adapters/cli_diagnostics.py` | 0 | 0 | 0 | 11 → T010 (diagnostic report texts) |
| `adapters/engine_fake.py` | 0 | 2 | 0 | — |
| `adapters/fake.py` | 0 | 1 | 0 | 3 → T010 (synthetic simulation output) |
| `adapters/git.py` | 19 | 19 | 0 | — |
| `adapters/import_git.py` | 0 | 5 | 0 | — |
| `adapters/local_git.py` | 5 | 3 | 0 | — |
| `adapters/managed_mode.py` | 0 | 2 | 0 | 1 → T010 |
| `adapters/preparation.py` | 0 | 0 | 0 | 1 → T010 |
| `adapters/project_onboarding.py` | 1 | 1 | 0 | — |
| `adapters/safe_files.py` | 0 | 0 | 0 | 4 → T010 |
| `adapters/streams.py` | 1 | 0 | 0 | — |
| `api/__init__.py` | 0 | 1 | 0 | — |
| `api/app.py` | 1 | 2 | 0 | 2 → T010 |
| `api/documents.py` | 1 | 1 | 0 | — |
| `api/managed.py` | 16 | 46 | 2 | 19 → T010 (HTTP diagnostics) |
| `api/schemas.py` | 6 | 7 | 81 | 2 → kept (bilingual chat commands) |
| `api/security.py` | 0 | 2 | 1 | 4 → T010 |
| `api/session.py` | 0 | 0 | 0 | 6 → T010 |
| `cli.py` | 1 | 1 | 0 | 20 → T010/T011 (help and errors) |
| `launcher.py` | 3 | 1 | 0 | 9 → T010 |
| `migrations/versions/0001`–`0023` (23 files) | 12 | 20 | 0 | — |
| `recipes/__init__.py` | 0 | 0 | 0 | — (comment added for v2) |
| `recipes/django_2.py`, `typescript_web_2.py` (new) | — | — | — | 13 → kept (es variants and v1 functional defaults) |
| `services/__init__.py` | 0 | 1 | 0 | — |
| `services/local_config.py` | 11 | 1 | 0 | 138 → T010 (configuration diagnostics) |
| `services/managed.py` | 8 | 3 | 0 | — |
| `services/managed_runtime.py` | 5 | 9 | 0 | 20 → T010 |
| `services/project_creation.py` | 3 | 3 | 0 | 49 → T010 |
| `services/project_preparation.py` | 0 | 0 | 0 | 42 → T010; v1 step-label keys and plan notice frozen in plans → T008/T009 |
| `services/project_registry.py` | 6 | 6 | 0 | 45 → T010 |
| `storage/__init__.py` | 0 | 1 | 0 | — |
| `storage/backup.py` | 10 | 6 | 0 | 58 → T010 |
| `storage/bootstrap.py` | 1 | 1 | 0 | — |
| `storage/bootstrap_discovery.py` | 0 | 2 | 0 | — |
| `storage/chat.py` | 3 | 9 | 0 | 1 → T010 |
| `storage/closure.py` | 1 | 1 | 0 | — |
| `storage/database.py` | 1 | 0 | 0 | 2 → T010 |
| `storage/document_export.py` | 4 | 3 | 0 | — |
| `storage/documents.py` | 10 | 10 | 0 | — |
| `storage/managed.py` | 7 | 20 | 0 | 1 → T010 |
| `storage/managed_mode.py` | 1 | 4 | 0 | 4 → T010 |
| `storage/managed_views.py` | 2 | 9 | 0 | 6 → T010 |
| `storage/metrics.py` | 11 | 12 | 0 | 6 → T010 |
| `storage/migrate.py` | 1 | 4 | 0 | 22 → T010 |
| `storage/models.py` | 18 | 21 | 0 | — |
| `storage/onboarding.py`, `onboarding_commit.py` | 0 | 2 | 0 | — |
| `storage/permissions.py` | 1 | 0 | 0 | — |
| `storage/phase_plan.py` | 0 | 1 | 0 | — |
| `storage/phases.py` | 24 | 27 | 0 | 2 → kept `tarea` command; `## Fase activa` in prompt → T009 |
| `storage/planning.py` | 7 | 20 | 0 | — |
| `storage/preparation.py` | 0 | 0 | 0 | 4 → T010 |
| `storage/private_drafts.py` | 0 | 3 | 0 | — |
| `storage/project_creation.py` | 0 | 2 | 0 | 4 → T010 |
| `storage/project_import.py` | 2 | 1 | 0 | — |
| `storage/registry.py` | 0 | 3 | 0 | 18 → T010 |
| `storage/retention.py` | 0 | 0 | 0 | 40 → T010 |
| `storage/run_projection.py` | 4 | 7 | 0 | 8 → T010 |
| `storage/schema.py` | 0 | 0 | 0 | 1 → T010 |
| `storage/transition.py` | 2 | 4 | 0 | — |
| **Total (94 files + 2 new)** | **223** | **318** | **84** | **555 existing → owners above** |

Files with no Spanish comment, docstring or literal: `adapters/commands.py`, `process_gate.py`, `processes.py`,
`migrations/env.py`, `script.py.mako`, `storage/command_processes.py`, `prompts.py`, `repository.py`,
`retired_work.py`. Residual counts are candidates from a finite pattern scan, not a linguistic certificate; T010
re-inventories each surface when building catalogs.

## Validation and limits

- AST of all 94 pre-existing files with docstrings and `description` values blanked: identical before and after
  (SHA-256 per file). Logic, persisted keys, revisions, catalogs and paths are unchanged.
- Residual scan: no Spanish candidate remains in comments or docstrings of the group; none in `frontend/openapi.json`.
- v1 byte hashes and fingerprints identical (new pinned test); v2 equivalence with v1 effects/profiles tested.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: 8 tests OK.
- `uv run --frozen --offline pytest -q` (xdist): 1520 passed, 2 skipped, 29 subtests passed; the documentation parity,
  recipe and OpenAPI tests rerun after the final doc edits: 28 passed.
- `node --test frontend/tests/*.test.mjs`: 82/82; `npm --prefix frontend run check` and `run build` OK (only the
  existing chunk-size warning). Alembic not run: no schema change.
- Not run: agents, providers, services, smokes, real recipe preparations or network. No test only repeats comments.

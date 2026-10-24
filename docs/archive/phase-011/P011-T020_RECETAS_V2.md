# P011-T020 — v2 recipes wired by work language

Implemented on 2026-10-23 from `ef0e9a3` (clean checkout). The user's instruction authorizes this next task and one
local commit in English. Precedents: [T001 §5](P011-T001_CONTRATO_APERTURA.md#5-fuentes-congeladas-recetas-documentos-y-compatibilidad),
D163 (v2 modules, not wired), D167 (work language per root; T020 split out of T008 by HITL); implementation decision
D168. [Flow](../flows/project-preparation.md#recetas-v2-por-idioma-de-trabajo-p011-t020-d168).

No HITL was needed: the task criteria, D163 and D167 settle the scope. The one design choice left open (how the
work language enters the frozen identities) is reversible and recorded in D168.

## What exists now

**Selection** (`recipes/__init__.py`, `services/local_config.py`):

- `RECIPES` (v1, `local-config-5`) is unchanged; `RECIPES_V2` maps the same configuration names and profile names to
  `django_2`/`typescript_web_2`; `GENERATIONS` chooses by format. `by_version` resolves every issued version, so v1
  and v2 plans and receipts keep reading and reconciling with the class of their own version.
- `local-config-6` admits `[recipes.django]` and `[recipes.typescript-web]` with exactly the v5 keys and checks; the
  v6 refusal of T008 is gone. A v6 recipe composition freezes `project_recipe = django-recipe-2|typescript-web-recipe-2`.
- A v6 recipe composition runs with its v2 module's own profile: Django v2 (English executor instructions) keeps the
  D133 formatter; TypeScript v2 uses its own copy, so the built-in `typescript-web` stays for compositions without
  a recipe. v5 compositions keep v1, the built-in profile and every hash (the v1 suites are untouched).
- Composition identity: `recipe_config_sha256` binds the operator config plus
  `implementation_sha256_by_work_language` (the v2 fingerprint for en and es). The composition does not know the
  root's work language (registered projects take it from SQLite, D167); the plan and receipt seal it (below).

**Preparation** (`services/project_preparation.py`):

- `DjangoRecipe2`/`TypeScriptRecipe2` reuse the shared core and v1 effects. Checks dispatch by stable step `id`
  (`python-version`, `installer-version`, `installed-versions`, `node-version`, `npm-version`), the uncertain
  environment is `create-environment`, and source checks key on `generate-*` (partial), `migrate`/`validate-*`
  (complete). v1 classes keep their frozen Spanish labels through a label → check map, with the same behaviour.
- Work language: the preview of a v2 recipe reads the root's row (`project_work_languages`) in its session; without
  one it refuses with 409 `work_language_required` (catalog message in the visual language) before any check of the
  checkout. The plan seals `work_language`, `work_language_sha256` (row hash) and `recipe_sha256`
  (= `fingerprint(work_language)`); the manifest is the scaffold of that language. A successor of a failed v2
  operation keeps the original values and refuses (`preview_changed`) if they differ.
- Before every step, `_check` compares the row again with the plan's value and hash: a missing or different row
  stops the operation before its next effect (tested: an operation confirmed and then left without a row fails
  before writing anything).
- `_publish` compares the generated Python files with the confirmed manifest (`plan['files']`) instead of the v1
  scaffold, which is equivalent for v1 plans and correct for both v2 languages; file writing dispatches on the
  recipe class, not on the v1 version string.
- Receipt: v2 adds `work_language`, `work_language_sha256` and `recipe_sha256`; `verify_receipt` treats
  `typescript-web-recipe-2` like v1 (tools, not `node_modules`). Commit messages name the v2 version; the TypeScript
  v2 network notice is English technical text.
- The child's functional language (`LANGUAGE_CODE = "es"`, `<html lang="es">`, visible text) does not derive from
  the visual or work language (T001 §5, D163); tested in all four stack/language pairs.

**API and client**:

- `PreparationPlanRead` gains optional typed `work_language` and `recipe_sha256` (null for v1 plans); OpenAPI and
  client types regenerated.
- The preparation page names v2 steps from the en/es catalogs by `id` (`preparation.step.*`, validations with the
  profile command), so the label follows the visual language without touching the plan; v1 plans show their frozen
  label. The preview shows the work language through a catalog key. The rest of the page stays Spanish (T010).
- `examples/django-recipe.example.toml` and `typescript-web-recipe.example.toml` now describe v6 (v2) and v5 (v1);
  the general template notes that v6 recipe fragments select v2.

## Not done here (owners)

- Prompt directive and generation of project documents in the work language → T009.
- Translation of the rest of the preparation page, server diagnostics and CLI → T010/T011.
- Real toolchains, wheelhouse, npm cache or network: not authorized; the synthetic probes stand in for them.
- Moving a project prepared with v1 to `local-config-6`: not supported (it would change its frozen composition, as
  any recipe configuration change does). The user states there are no earlier projects; v1 projects stay on v5.

## Test strategy

- New `tests/product/test_recipe_v2_preparation.py` (10 tests): a v6 child created with each work language for each
  stack prepares offline with the synthetic toolchain and commits exactly the v2 manifest of that language, with the
  v2 profile, ids, plan/receipt seals and an unchanged functional language; the API returns the typed values and keeps
  the strict payload; without a row the confirmed operation fails before effects and a successor is refused;
  v5/v6 with the same keys freeze v1/v2 with distinct identities and profiles; checks dispatch by id (a changed
  display label does not alter it) while v1 keeps its labels; a v2 recovery refuses an uncertain environment and
  completes through explicit successors.
- Updated: `test_recipe_versions.py` (generations instead of "not selectable"), `test_work_language.py` (v6 admits
  `[recipes]`), `frontend/tests/preparation.test.mjs` (v2 texts and step labels in en/es).

## Validation

- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`: 1551 passed, 2 skipped, 29 subtests passed,
  1 failed: `test_cli_diagnostics.py::test_bounded_failures_no_retry[child-timeout-help]`, a timeout under the
  parallel load, unrelated to this change; the module passes serially (`-n 0`, 52 passed).
- `python3 -m unittest discover -s tests -p 'test_*.py'`: 8 OK.
- `node --test frontend/tests/*.test.mjs`: 89/89 (catalog parity covers the 18 new keys).
- `npm --prefix frontend run check` and `run build`: OK (the existing >500 kB chunk warning).
- OpenAPI exported (`scripts/export_openapi.py`) and types regenerated (`generate:types`).
- Not run: Alembic (no model or migration change), services, `scripts/dev`, browser QA, agents, providers, real
  preparations, network or the wheel checks.

# P011-T008 — Immutable work language per project and the frozen language pair

Implemented on 2026-10-23 from `0945840` (clean checkout). The user's instruction authorizes this next task and one
local commit in English. Contract: [T001 §2 and §4](P011-T001_CONTRATO_APERTURA.md#2-autoridad-persistencia-y-controles-de-idioma)
(D159), D158 and D166; implementation decision D167. [Flow](../flows/project-work-language.md).

HITL (2026-10-23), questions the documents left open, answered by the user:

1. **Scope.** T008 bundled the association, `local-config-6`, the recipe v2 wiring and the pair snapshots → the
   recipe v2 wiring (dispatch by step `id`, `[recipes]` in v6) moves to a new bounded task, **T020**, before T009.
2. **Projects without a work language.** The user states that there are no earlier projects: the package has not
   been used yet. The contract rule applies as written (new admissions refused; continuations keep their context).
3. **`local-config-6` declarations.** The service records the declared value at startup (source `toml`); loading the
   TOML stays free of effects and another value for an associated root stops the service.
4. **Explicit confirmation for projects without a value.** API plus a minimal UI block in the project settings.

## What exists now

**Persistence** (migration `0025_project_work_languages`, [diagram](../DDBB-DIAGRAM.md#idioma-de-trabajo-por-proyecto-p011-t008)):

- `project_work_languages`: one row per canonical root (`work-language-1`), with the value (`CHECK en|es`), the
  project that confirmed it, its source (`registration`, `creation`, `toml`, `migration`), the confirmation
  (preview hash or TOML hash, actor, reason, default and preferences version at confirmation) and a row hash. Written
  once, never updated or deleted; no FK, so the root keeps it across retirement, a new id or a TOML declaration.
- `managed_attempts.language_context` (nullable JSON): the job's pair copied when each attempt starts.
- Downgrade refuses while any row exists. Backup and query restoration keep the rows (tested).

**Choosing it** (`services/project_registry.py`, `services/project_creation.py`, `storage/registry.py`):

- Registration (B) and creation require `work_language`; the UI initializes the radio group from the global default.
  The preview returns `{work_language, source, default_work_language, preferences_version, existing}` and its hash
  seals only the chosen value and the existing association: a default changed between preview and confirmation does
  not alter what is confirmed (tested). The row is written in the transaction that registers the project; creation
  intents use `project-creation-2` (with `work_language_seal`) and register the row with the child; earlier
  `project-creation-1` intents still register, without one.
- A root that already has a row admits only its value: registering it again (after retirement, with another id)
  keeps the original row. Update or retirement requests that carry `work_language` → 409 `work_language_immutable`.
- `local-config-6` = `local-config-5` plus optional `[[projects]].work_language` (TOML projects only; registered rows
  never carry it). It enters the project's frozen TOML hash. `[recipes]` is refused in v6 until T020. v1–v5 keep their
  keys and identities; `work_language` in v5 is an unknown key.
- Startup (`services/managed_runtime.py`): a declared TOML value is associated once (`toml`); every installed project
  (TOML or registered) gets `ProjectContext.work_language` from SQLite. A different declared value raises before the
  service starts.

**Explicit confirmation** (`services/work_language.py`, API, Settings):

- `POST /api/managed/projects/{id}/work-language/preview` → value, root, `files_preserved: true`, unfinished jobs,
  configuration blockers and a hash over project, root, frozen versions and the chosen value.
  `POST /api/managed/projects/{id}/work-language` with the hash and a mandatory reason; pending work refuses it
  (`pending_work`), a stale hash `preview_changed`, an already confirmed project `work_language_immutable`; the same
  confirmation replays (`replayed: true`). Nothing is translated, renamed or inspected.
- Settings show the value read-only (language, date, source, hash) or, without one, the warning, the choice, the
  preview, the reason and an acknowledgement before confirming. The new texts use the en/es catalogs.

**Freezing the pair** (`storage/work_language.py`, `storage/managed.py`):

- Every new job (the two capture sites of D166: new runs and commit jobs) reads preferences and the root's row in its
  admission transaction and seals `language-context-1`: `ui_language`, `preferences_version`, `work_language`,
  `work_language_source`, `work_language_sha256`. Without a row the admission raises `WorkLanguageRequired`
  (409 `work_language_required`, diagnostic in the stored visual language) and nothing is queued.
- Continuations keep copying the first job's value (also `ui-language-1` or null); each attempt copies its job's pair.
- `context_snapshot` includes `work_language` only when set, so earlier snapshots keep their bytes; a context whose
  value differs from the row is refused. The visual language stays outside composition hashes.
- API: `ManagedJobRead.language_context` and `ManagedAttemptRead.language_context` accept both formats; projects and
  registry rows expose `work_language`. OpenAPI and client types regenerated.

## Not done here (owners)

- Recipe v2 wiring, `[recipes]` in v6 and binding preparation to the work language → T020. Preparation operations are
  not jobs, so they are not gated by the work language yet; with v5 recipes they keep using v1 as before.
- Prompt directive, V/W/T field mapping and generation in the work language → T009. The pair is provenance today:
  agents do not change language.
- Translation of the rest of the registry/creation/settings pages and API/CLI messages → T010 (the new blocks and
  diagnostics already use catalogs; the surrounding pages remain Spanish).
- Visual QA in a browser: not authorized here (T010/T016).

## Test strategy

- New `tests/product/test_work_language.py` (11 tests, real gate): registration with the default changed between
  preview and confirmation, immutability on update, retirement and re-registration; the four visual/work combinations
  with later changes of both globals; the refused admission without a row, the continuation and the attempts
  inheriting the pair; a stale context; explicit confirmation over HTTP (422/409 cases, replay, restart);
  `local-config-6` association at startup, refused startup with another value, undeclared v6, invalid values, v5 key
  and refused recipes; creation sealing and registering the value; backup/restore and the refused downgrade.
- Existing tests that are not about languages (≈720 across 60 files) admit jobs on synthetic roots. Instead of
  rewriting them, an autouse fixture in `tests/product/conftest.py` writes a synthetic `en` row (a real row) when the
  service installs a project or the first job of a root is admitted, and removes only those synthetic rows before an
  Alembic downgrade so the older-revision round trips keep working. The new module opts out with
  `@pytest.mark.unconfirmed_work_language`. Request bodies of registration/creation tests now carry `work_language`.
- Updated expectations: the T007 preference tests now read `language-context-1`; the project list and the TOML
  identity assertion account for the bound work language; one preparation round trip removes its real rows before
  downgrading to 0021; the storage revision is `0025`.

## Validation

- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`: 1542 passed, 2 skipped, 29 subtests passed
  (T007: 1531 + 11 new).
- `python3 -m unittest discover -s tests -p 'test_*.py'`: 8 OK.
- `node --test frontend/tests/*.test.mjs`: 88/88 (catalog parity includes the new keys).
- `npm --prefix frontend run check` and `run build`: OK (the existing >500 kB chunk warning).
- `alembic upgrade head` + `alembic check` on a temporary database: no new operations; 51 tables; downgrade to 0024
  and upgrade again without rows: OK.
- OpenAPI exported (`scripts/export_openapi.py`) and types regenerated; the runtime/exported OpenAPI test passes.
- Not run: services, browser QA, agents, providers, smokes, network, `scripts/dev` or the wheel checks.

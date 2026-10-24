# P011-T007 — Language infrastructure for the interface and messages

Implemented on 2026-10-23 from `69cf423` (clean checkout). The user's instruction authorizes this next task and one
local commit in English. Contract: [T001 §2–§4](P011-T001_CONTRATO_APERTURA.md#2-autoridad-persistencia-y-controles-de-idioma)
(D159), D158; implementation decision D166.

HITL (2026-10-23), two questions the documents left open, answered by the user:

1. **Scope of "conversation in the visual language" in T007.** The plan gives the pair snapshots
   (`language-context-1`) to T008 and the agent directive to T009, while T007 must make visual changes govern new
   jobs/turns and isolate pending ones → **T007 freezes only the visual language per job**: a nullable
   `managed_jobs.language_context` (`ui-language-1`) sealed at every admission; continuations inherit it. T008 adds
   the work language and carries the pair into attempts/prompts; T009 injects the directive. Agents do not change
   language yet.
2. **Surfaces of the initial catalogs.** T010 completes the rest → **shell, session and preferences**: session gate,
   header/session controls, supervisor status, theme control, side navigation, breadcrumbs, the not-found page and
   the new Preferences page; own API/CLI diagnostics of session, preferences and the launcher.

## What exists now

**Persistence** (migration `0024_product_preferences`, [diagram](../DDBB-DIAGRAM.md#preferencias-de-idioma-p011-t007)):

- `product_preferences`: one row (`CHECK id = 1`), `product-preferences-1`, `ui_language` and
  `default_work_language` constrained to `en`/`es`, `version`, `updated_at`. The migration seeds `en`/`en`, version 1.
- `product_preference_events`: one row per saved change, unique `version` and `Idempotency-Key`, request hash and a
  payload with before/after, actor, time and a hash chain (`previous_sha256` → `sha256`).
- `managed_jobs.language_context` (nullable JSON, additive `ALTER TABLE`): `{format: ui-language-1, ui_language,
  preferences_version}`. Jobs earlier than 0024 stay null, meaning "not recorded"; nothing is inferred.
- Downgrade refuses when a change was recorded (events exist). Without events every capture is the factory `en`,
  so dropping the column loses no explicit choice; this keeps the existing round-trip tests of older migrations.

**Authority and capture** (`storage/preferences.py`, `storage/managed.py::_language`):

- Reads never create or repair the row: absent → `default` (en/en, version 0); values outside the contract →
  `invalid`, shown as English. Updates take the managed write lock, check `expected_version` (CAS), validate both
  enums, replay the same key with the same request (`replayed: true`) and refuse the same key with another request.
- Every job insertion reads the preferences **in the transaction that admits it**. The seven insertion sites:
  new runs (`_queue_new_run`: tasks, chat turns, phase operations, planning/definition/onboarding turns, document
  edits/exports, bootstrap and import), commit jobs, and the resumptions of task runs, bootstrap, import, export and
  document operations.
- New interactions capture the current value: a new task, turn, check, commit or any other new action on an earlier
  result. Continuations of the same run copy the value of the run's first job, null included, and never recapture:
  executor retry, revalidation and the four operation resumptions. A replayed `Idempotency-Key` returns the same job.
- An `invalid` row blocks every new admission (`PreferencesInvalid`, API 409 `preferences_invalid`, English
  diagnostic) until an explicit save repairs it; nothing is queued.

**API** (OpenAPI and client types regenerated):

- `GET /api/managed/preferences` → `PreferencesRead` (`format`, `version`, both languages, `updated_at`, `status`).
- `PUT /api/managed/preferences` (session, loopback guard, `X-Harness-Local`, `Idempotency-Key`, strict body with
  `expected_version` ≥ 0 and both enums; unknown fields → 422) → `PreferencesUpdateRead` with `replayed`.
  409 `preferences_conflict` (stale version) and `idempotency_conflict` (key reused), with diagnostics in the stored
  visual language. A restored read-only database rejects the PUT through the existing middleware.
- `ManagedJobRead.language_context`: an admission response returns the value actually frozen, even from a stale tab.
- Session diagnostics (`session_required`, `login_rate_limited`, `invalid_login`, `session_limit`) are localized with
  the stored visual language; codes and statuses are unchanged.

**Catalogs, no new dependencies** (D159 §3):

- Python: package `harness_local/i18n` with `en.json`/`es.json` read through `importlib.resources`;
  `message(key, language, **params)` falls back to English, returns the key when it is missing everywhere and keeps an
  absent `{name}` field visible. 16 keys. The wheel includes the JSON files like the recipe resources.
- Frontend: `src/i18n.ts` (pure: `translate`, `plural` with `Intl.PluralRules`, numbers with `Intl.NumberFormat`,
  `isLanguage`, endonyms), `src/i18n/{en,es}.json` (62 keys) and `src/Language.tsx` (provider). Keys are typed from the
  English catalog; `satisfies` makes the Spanish catalog cover them at compile time. Messages are complete sentences;
  parameters are replaced as text (never HTML). Session notices are kept as keys so a later language change re-renders
  them. `tsconfig.json` enables `resolveJsonModule`; the Node tests import the JSON with import attributes.
- The provider starts with the provisional `localStorage` copy (`harness-ui-language`) or English, reads the
  service after each session check (every 15 s and on window focus) and after sign-in, sets `<html lang>` and never
  writes the preferences on a failed read (it shows "could not be read" and keeps the last language).
- New global page `/preferences` (side navigation): two radio groups with legends, hints linked by
  `aria-describedby`, endonyms with their own `lang`, saved version/time, idempotent save (the same change keeps its
  key until the service answers) and conflict handling (reread + message). The shell warns on an `invalid` row.
  `index.html` now declares `lang="en"`; the session time uses `Intl.DateTimeFormat` with the visual language.

**CLI**: `harness-local --ui-language en|es` applies to that invocation only. Without it, the language comes from the
preferences of an existing database named by the command (opened `mode=ro`, never created or migrated), else `en`.
Localized: the launcher/CLI own messages (absolute path, auxiliary files, existing destination, port range, missing
database or assets, `--config` conflict, backfill without database). Kept in Spanish on purpose, coupled with
maintainer scripts (D164 note for T010): `clave de acceso en`, `módulo:atributo`, `Esquema SQLite`.

## Not done here (owners)

- Work language per project, its immutability, `local-config-6` and the `language-context-1` pair in attempts and
  prompts → T008. `default_work_language` is stored and editable but no registration reads it yet.
- Prompt directive and V/W/T field mapping → T009. The frozen visual language is provenance only today.
- Every other visible string (pages, statuses, `ui.tsx`, API/CLI messages of other modules, argparse help) → T010.
  The page hint describes only what T007 delivers: interface and own messages, not agent answers.
- Python plurals: no own message needs one yet; the contract rule (`one` for 1, `other` otherwise) lands with the
  first plural key. The frontend `plural` exists and is tested but not used by the initial catalog.
- Visual QA in a browser (desktop/mobile, light/dark): not authorized here; T010 owns it.

## Validation

- New `tests/product/test_preferences.py` (11 tests): seeded values and read-only reads; CAS, idempotent replay,
  reused key, invalid input and the hash-chained audit; refused downgrade after a change; per-job freezing with a
  pending job unaffected by later changes and an executor retry inheriting the original value; the T001 concurrency
  example (turn A in `es`, change to `en`, turn B in `en` in the same conversation, A's answer unchanged); commit and
  check capturing the current value; an invalid row blocking admission until saved; the HTTP contract (422/403/409,
  localized diagnostics, `language_context` in the admission response, Spanish 401 after the change); a typed 409 on
  admission with an invalid row; CLI precedence without writing; Python catalog parity.
- Updated expectations: launcher/CLI messages (now English by default, with a Spanish case through `--ui-language`
  and `initialize(..., 'es')`), the schema revision in `test_storage_api.py`. `frontend/tests/router.test.mjs` now
  builds the trail with the Spanish catalog (same expectations), adds `/preferences` and an English trail;
  new `frontend/tests/i18n.test.mjs` (parity of keys/fields/plural variants, text-only interpolation, fallback,
  plurals, language validation).
- Commands: `uv run --frozen --offline pytest -q` (xdist): 1531 passed, 2 skipped, 29 subtests passed (T006: 1520 +
  11 new). `python3 -m unittest discover -s tests -p 'test_*.py'`: 8 OK. `node --test frontend/tests/*.test.mjs`:
  88/88 (T006: 82). `npm --prefix frontend run check` and `run build` OK (the existing >500 kB chunk warning).
  `alembic check` on a temporary database upgraded to head: no new operations. OpenAPI exported and types regenerated;
  the runtime/exported OpenAPI test passes.
- Not run: services, browser QA, agents, providers, smokes, network, `scripts/dev` or the wheel checks
  (`check_distribution.py` keeps the three coupled Spanish messages it matches).

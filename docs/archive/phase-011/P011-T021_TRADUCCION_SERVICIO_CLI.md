# P011-T021 — Service and CLI diagnostics in en/es

Implemented on 2026-10-23 from `480e2b0` (clean checkout). The user's instruction authorizes this next task and one
local commit in English. Contract: [T001 §3](P011-T001_CONTRATO_APERTURA.md#3-catálogos-fallback-y-formatos) (D159),
infrastructure D166, interface D170; implementation decision D171. Starting inventory:
[T010 owners](P011-T010_TRADUCCION_PRODUCTO.md#not-done-here-owners).

HITL (2026-10-23), four questions the documents left open, answered by the user:

1. **Scope.** Besides the inherited Spanish literals, services/storage hold ~960 `raise` texts already in English →
   **T021 moves every own text that was in Spanish to the catalogs** (plus the argparse help); the service texts
   already in English stay as English technical text and a new **T022** catalogs them in en/es. The two texts the UI
   compares (`managed blocks are generated`, `changed since`) are English and stay unchanged.
2. **Workers.** Texts a background worker emits and persists use **the visual language frozen with their job**
   (`language_context`, D166/D167); a job admitted without it uses the stored preferences at emission.
3. **Visual QA.** Not authorized now → recorded as not done (matrix below); it keeps its own authorization.
4. **Core isolation.** `test_core_imports_with_standard_library_only` allowed only the stdlib and `harness_local.core`
   → **`harness_local.i18n` is allowed as the only outer leaf** (it imports the stdlib only); test and ARCHITECTURE
   record the exception.

## What exists now

**Emission language** (`harness_local/i18n/__init__.py`, no new dependencies):

- `emission(language)` sets the visual language of an emission in a `ContextVar`: a code, or a resolver called once
  on the first message. `current()` falls back to English without one, for an unsupported value or if the resolver
  fails. `tr(key, **params)` = `message()` in `current()`.
- `tr()` returns `Localized`, a `str` that remembers its key and fields (`render(language)`, `rendered(value, lang)`).
  Copies, pickles and JSON keep only the text (`__reduce__` → `str`), so SQLite/JSON/hash code sees a plain string.
- Where each emission is set: every HTTP request (`api/app.py::emission_language`, stored preferences, read only if
  a text is emitted); each claimed managed job (`LocalSupervisor.run_once` → `repository.job_visual(claim)`: the
  frozen `ui_language`, else the stored one); each claimed preparation (stored, it freezes no visual language); each
  CLI invocation (`--ui-language`, else the database's preferences, else `en`). Threads start without an emission
  (English) until one of these sets it. The launcher's helpers follow the emission when no language is passed.
- CLI help: `build_parser(language)` builds every own help text from `cli.help.*` with `--ui-language` (pre-parsed)
  or English, since the database is not known before parsing. argparse's own messages and usage stay as written.

**Catalogs** (`i18n/{en,es}.json`): 471 keys (+425 from 46), same keys and fields in both, no `<…>` or non-field
braces (an id pattern is a `{pattern}` field). Namespaces: `config` 85, `backup` 58, `creation` 47, `retention` 44,
`preparation` 39, `registry` 39, `cli` 33 (24 help), `migrate` 16, `mode` 14, `runtime` 12, `cli_diagnostics` 11,
`views`/`chat`/`evidence`/`metrics`/`simulation`/`database`/`projection`/`definition`/`documents`/`bootstrap`.

Converted (38 modules): local configuration, registry (service and storage, including the configuration blockers),
creation (service and storage), preparation (service, storage and adapter; the `preparation_required:` prefix the API
maps stays in both languages), backup, retention, migration, managed runtime and launcher, CLI help, managed mode
(core, storage, adapter), managed views and run projection, metrics, database/schema checks, version/help
diagnostics corrections, evidence reads, chat snapshot/commands, bootstrap folder diagnostic, simulation (title and
fake adapter results), definition/onboarding warnings and documentation budget warnings. One T010 leftover in
`api/managed.py` (`Intento desconocido para este run.`) is now `api.attempt_unknown`.

**Hashes and persisted texts.**

- Retention preview: `preview_sha256` seals each own diagnostic rendered in English (`rendered(..., 'en')`); system
  texts (OSError) are sealed as received. A preview confirmed with another `--ui-language` still matches. Previews
  hashed before this change (over Spanish text) no longer match and must be shown again; no stored hash is rewritten.
- Registry/creation previews: the trust/permission statements are shown in the visual language and the creation
  intent hash includes them, so changing the language between preview and confirmation requires a new review (safe
  failure). The trust record now keeps the statement the operator confirmed (`shown`/`intent['trust_statement']`;
  older intents keep their Spanish text) instead of re-reading a constant.
- Persisted diagnostics (jobs, preparations, creations, events) keep the language they were emitted in; nothing is
  translated afterwards. The registry blocker comparison in preparation uses the same key as the blocker it filters.
- `/tarea` proposals: the answer follows the visual language; the proposed task's rationale follows the project's
  work language (D169 field map).

**Scripts.** `scripts/check_distribution.py` now invokes `--ui-language en` and matches `module:attribute` and
`SQLite schema` (keys `runtime.config_reference`, `cli.schema_incompatible`). Not run (it builds and serves the wheel).

## Exceptions kept on purpose

Checked by `test_no_own_spanish_literals_outside_the_documented_exceptions`:

- Work-language document vocabulary and bilingual parser aliases (T009, D169): `core/engine/document_text.py`,
  `language.py`, `planning.py`, `import_commit.py`, `documents.py` (`fuera de alcance`), the D036 legacy export header
  in `document_export.py` and the `«## PNNN — título»` placeholder in `definition.py`.
- Frozen v1 recipes and fingerprinted profile values (D163): `recipes/django.py`, `typescript_web.py`, the v1 labels
  and notice in `project_preparation.py` and `profiles/typescript_web.py`; v2 recipes hold their `es` variants.
- Spanish chat protocol tokens (`/tarea`, `/abrir-fase`, …) and the unchanged technical commit message
  `docs: incorporar al control del harness` (T009 HITL).
- Third-party texts (argparse, Pydantic, OSError) and English service texts → T022.

## QA matrix (T010 + T021)

| Surface | en | es | Light/dark | Desktop/mobile | Status |
|---|---|---|---|---|---|
| React interface (T010) | tests/types/build | tests/types/build | not run | not run | browser QA not authorized |
| HTTP diagnostics of `api/*` (T010) | pytest | pytest | — | — | covered by tests |
| Service diagnostics forwarded by the API (T021) | pytest | pytest | not run | not run | browser QA not authorized |
| CLI help and errors (T021) | pytest | pytest | — | — | covered by tests |
| Worker-emitted persisted texts (T021) | pytest (unit) | pytest (unit) | — | — | no provider run |

The joint visual QA (lengths, keyboard, errors and confirmations in en/es, light/dark, desktop/mobile) stays pending
with its own authorization; it is better done after T022 so the English service texts are covered too.

## Validation

- New `tests/product/test_service_diagnostics.py` (7): emission/`Localized` semantics; every literal catalog key used
  by the package exists in both catalogs; no own Spanish literal outside the exceptions; registry diagnostics and trust
  statement in en and es through saved preferences (the record keeps the statement shown); CLI help and errors with
  `--ui-language`, the database's preferences and the unsaved override; retention preview hash identical in en/es with
  localized diagnostics; a claimed job runs in its frozen visual language.
- 20 test files updated from Spanish to English expectations (no behaviour change); `test_core.py` allows the
  `harness_local.i18n` leaf.
- `uv run --frozen --offline pytest -q` (xdist): 1615 passed, 2 skipped, 29 subtests passed.
  `python3 -m unittest discover -s tests -p 'test_*.py'`: 8 OK. `node --test frontend/tests/*.test.mjs`: 93/93.
- `alembic check` on a temporary database after `upgrade head`: no new operations (no schema change; the default
  local development database is not migrated, so a check against it reports it out of date).
- Not run: frontend `check`/`build` (no client change), OpenAPI regeneration (no contract change), services, browser, agents, providers, smokes, network, `scripts/dev` and `check_distribution.py`.

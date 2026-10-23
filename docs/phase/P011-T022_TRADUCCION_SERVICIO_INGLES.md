# P011-T022 — Service texts that were English, in en/es

Implemented on 2026-10-23 from `bf32128` (clean checkout). The user's instruction authorizes this next task and one
local commit in English. Contract: [T001 §3](P011-T001_CONTRATO_APERTURA.md#3-catálogos-fallback-y-formatos) (D159),
infrastructure D166, interface D170, emission language D171; implementation decision D172. Starting inventory:
[T021 delivery](P011-T021_TRADUCCION_SERVICIO_CLI.md) (≈960 `raise` texts, many internal invariants).

HITL (2026-10-23), four questions the documents left open, answered by the user:

1. **Visible versus internal.** Almost every `raise` reaches the API as `diagnostic` through `api/managed.py::call`, so
   "visible" is decided by nature → **visible**: what the operator causes or resolves (inputs, state conflicts,
   unknown ids, checkout/Git/environment, agent outcomes, stop/acceptance/blocking reasons, recorded diagnostics);
   **English technical text**: invariants that only fail on a programming error or on corrupt persisted data, and
   texts that enter an agent's input (D169: the agent reads English base text).
2. **The two texts the UI compared** → **codes**: `call()` emits `managed_blocks_generated` and `draft_changed` from the
   cause of the `Conflict`; the client compares the code and the texts are translated like the rest.
3. **Stop reasons in metrics** → **accepted and documented**: metrics group stops by stage and text, so one cause
   emitted in en and in es counts as two groups (D171: what is persisted keeps the language it was emitted in).
4. **Joint visual QA** → **not authorized now**; recorded as not done (matrix below).

## What exists now

**Catalogs** (`i18n/{en,es}.json`): 1195 keys (+724 from 471), same keys and fields in both. The English text of each
converted message is byte-identical to the literal it replaced (no full stop added), so English output, tests that
match it and messages that wrap another one (`{exc}; nothing was overwritten`) do not change. New namespaces by size:
`phases` 105, `planning` 65, `documents` 63, `git` 57, `onboarding` 47, `preparation` 41, `managed` 39, `bootstrap` 38,
`definition` 38, `chat` 30, `agents` 26, `export` 23, `permissions` 16, `commands` 15, `context` 15, `commit` 13,
`prompts` 13, `workflow` 12, `contracts` 11, `supervisor` 11, `transition` 10, and `acceptance`/`preferences`/`review`/
`retired`/`runtime`/`cli_diagnostics`/`simulation`/`views`/`work_language`/`database`. One text has one key across
modules (e.g. `managed.unknown_managed_run`); a key never holds a fragment: a conditional phrase is two keys
(`chat.text_limit`/`chat.text_required_limit`) and a literal `{{NAME}}` travels as a field.

**Converted** (56 modules in `core/`, `adapters/`, `storage/`, `services/`): 695 `raise` sites with an AST-driven
working tool (fields named after the interpolated value, English kept, keys per module namespace), plus ~90 non-`raise`
texts, most of them by hand: stop reasons (`stopped`, `stop_history`, workflow/chat/definition/phase checks), acceptance
reasons, definition blockers, phase READY stale reasons and close/batch authorization reasons, commit/export/tag
`diagnostic` outcomes of the Git writer, retired legacy/A reasons (D161), the v1 creation refusal (`V1_RETIRED` is now
a key, rendered when raised) and the job-quarantine `JournalError`s of the command runner. The SQLite schema check had
a Spanish literal T021's detector missed (`Base SQLite no preparada…`); it is now `database.not_prepared` in en/es.

**Emission** is unchanged (D171): each HTTP request uses the stored preferences, a worker the visual language frozen
with its job, a preparation the stored one and the CLI `--ui-language`, the database's preferences or `en`.

**Client codes.** `ManagedBlocksEdited(ValueError)` (document edit touching generated blocks) and
`DraftChanged(DraftConflict)` (a draft that changed since it was read) are raised instead of the plain classes;
`call()` maps a `Conflict` caused by them to `managed_blocks_generated` and `draft_changed` (`ProblemRead.code` is a
free string: no OpenAPI or type change). `Docs.tsx` offers "regenerate blocks" and `Planning.tsx` shows its stale-draft
notice from `ManagedError.code`, never from `diagnostic`.

**Hashes and persisted texts.** No hash covers a newly localized text except previews that already carried localized
warnings (D171 precedent): a definition preview's blockers are part of it, but a preview with blockers cannot be
confirmed. Retention keeps sealing its own diagnostics in English. READY bindings, commit intents and projections hold
no reason text. Stop, acceptance and authorization reasons are persisted in the language they were emitted in and are
never retranslated; the chat context forwards a run's stored stop reason as data.

## English technical text kept on purpose

Listed with its category in `tests/fixtures/service_texts/english.json` (161 texts) and checked by
`test_own_service_texts_are_cataloged_or_listed_as_english_technical_text` (every own text in a diagnostic position is
either `tr()` or listed; a listed text that disappears fails too):

- **invariant** (134): frozen-identity and sealed-intent checks, operation/turn bookkeeping (`… already settled`,
  `… lacks its operation`), process/lease identity, clocks, codecs and history formats, corrupt activation snapshots,
  internal type checks, the v2 recipes' work-language guard.
- **agent-input** (20): JUnit parsing, validation command policy, the command runner's per-command refusals (they
  become `CommandResult.error` in the reviewer's input) and the onboarding inventory's per-file diagnostics.
- **technical** (7): document-name and configuration-key prefixes (`ROADMAP: {exc}`, `{label}.junit: {exc}`,
  `git: {exc}`), the D169 placeholder `«## PNNN — título»` and an OS-style `cannot change to {cwd}`.

Prompts, formatter notes, deterministic task contracts, selection reasons frozen in attempts, commit messages, log
lines and document vocabulary are not diagnostics and stay as they were (D169/D171).

## QA matrix (T010 + T021 + T022)

| Surface | en | es | Light/dark | Desktop/mobile | Status |
|---|---|---|---|---|---|
| React interface (T010) | tests/types/build | tests/types/build | not run | not run | browser QA not authorized |
| HTTP diagnostics of `api/*` (T010) | pytest | pytest | — | — | covered by tests |
| Service diagnostics forwarded by the API (T021, T022) | pytest | pytest | not run | not run | browser QA not authorized |
| Client refusals by code (T022) | pytest/types | pytest/types | not run | not run | browser QA not authorized |
| CLI help and errors (T021) | pytest | pytest | — | — | covered by tests |
| Worker-emitted persisted texts (T021, T022) | pytest (unit) | pytest (unit) | — | — | no provider run |

The joint visual QA (lengths, keyboard, errors and confirmations in en/es, light/dark, desktop/mobile) stays pending
with its own authorization.

## Validation

- New `tests/product/test_service_texts_catalog.py` (4): own texts cataloged or listed with a category; the two client
  refusals get their codes through `call()` whatever the language; document and draft refusals keep their cause and
  render in the emission language through the real repositories; engine acceptance reasons follow the emission,
  render back to English and persist as plain text.
- `uv run --frozen --offline pytest -q` (xdist): 1619 passed, 2 skipped, 29 subtests passed.
  `python3 -m unittest discover -s tests -p 'test_*.py'`: 8 OK; `node --test frontend/tests/*.test.mjs` (93/93),
  `npm --prefix frontend run check` and `build` (existing >500 kB chunk warning).
- Not run: OpenAPI regeneration (no contract change), Alembic (no schema change), services, browser, agents, providers,
  smokes, network, `scripts/dev` and `check_distribution.py`.

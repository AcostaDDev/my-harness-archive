# P011-T010 — Interface translation, own HTTP diagnostics and accessibility texts

Implemented on 2026-10-23 from `0d39f58` (clean checkout). The user's instruction authorizes this next task and one
local commit in English. Contract: [T001 §3](P011-T001_CONTRATO_APERTURA.md#3-catálogos-fallback-y-formatos) (D159),
infrastructure D166; implementation decision D170.

HITL (2026-10-23), three questions the documents left open, answered by the user:

1. **Size.** T010 covered ~800 Spanish lines in 30 frontend files and ~555 backend literals in ~35 modules →
   **split in two**: T010 = the whole React interface plus the own HTTP diagnostics the UI shows (`api/*`, session,
   security); new **T021** = service and CLI diagnostics (configuration, backup, retention, migration, registry,
   creation, preparation, runtime, launcher, argparse help). One commit per task.
2. **Script coupling (D164 note).** `scripts/dev.py` and `scripts/check_distribution.py` matched `clave de acceso en`,
   `módulo:atributo` and `Esquema SQLite` → **the access-key line is fixed technical output in English**
   (`Harness Local: access key at <path>`), never localized, and both scripts match it in this change (paths widened
   to `scripts/**` for that). The other two messages belong to service/CLI modules and move with T021, which updates
   the scripts in the same change.
3. **Visual QA.** Not authorized now → **QA in a browser (en/es, light/dark, desktop/mobile) is done once after T021**,
   with its own authorization. This delivery is verified by tests, types and build only.

## What exists now

**Frontend catalogs** (`frontend/src/i18n/{en,es}.json`): 1417 keys (T020: 98), same keys, fields and plural
variants in both; every key is referenced by the source (checked during the task) and typed through `MessageKey`,
so a missing key is a compile error. Keys name complete messages; English is the base and the fallback.

Translated surfaces (all own visible texts, ARIA labels, tooltips, empty states, confirmations and `window.confirm`):
home and project summary, task form and run tables, phases (list, detail, definition, questions, documents, export,
check/closure, batch, amendment/abandonment, history and closure records), task and run pages (decision, cycles,
diff pages, jobs/recovery, attempts, events), permissions, tests/JUnit, logs, chat and chat commands, documentation
(tree, overview, drift, local changes, editor, review, progress), creation/definition, planning, onboarding (B),
registry/new project/creation folder and registry settings, settings and versioned prompts, statistics and charts,
preparation (recipe texts, modes, steps, journal), workspace notices and shared components (`ui.tsx`).

**Infrastructure added to D166** (no new dependencies):

- `i18n.ts`: `PluralKey`/`Plural` types (bases with `.one`/`.other`; a key ending in `.one` is always a plural),
  `segments()` to split a message at its fields, and `LocalizedError(key, params)` for errors raised outside React.
- `Language.tsx`: `n()` (plural) and `rich()` on the context. `rich` places elements (a code span, a link to an id,
  a hash) at the fields of a translated sentence; it splits the template **before** inserting values, so a value
  containing `{name}` is never read as another field, and React escapes everything (no HTML). Link labels that are
  themselves translatable are separate sentences (the T007 not-found pattern), never fragments inside another message.
  `translateNow`/`errorText` translate `LocalizedError` in the current visual language for code without the context.
- `metrics.ts`: `formats(language, t, n)` returns the statistics formats (integers, compact, USD through
  `Intl.NumberFormat` currency, durations, percentages, coverage sentences with plurals, root labels, roles); pure for
  `node --test`. `charts.tsx::useFormats()` builds it from the provider. `diff.ts`: `byteSize(value, language)` and the
  changed-final-newline line of `unifiedDiff` receive their text from the caller.
- `preparation.ts`: `recipeLabel` returns the recipe name or `null`; `recipeText(recipe, t, named, generic)` chooses
  between a sentence with the name and a generic sentence, so "the project" is never inserted as a fragment.
- Dates: `when()` renders a `<time>` with the visual language (was `es-ES`); the ISO value stays in the tooltip.
- Errors: `ManagedError` keeps `diagnostic` (the service text, in the language it was emitted) and, without one, its
  message is the status and code only; `message(e)` adds the interface sentence `error.no_diagnostic`. The client-side
  confirmation-pending error and the H0 client error are `LocalizedError`s.

**Markdown viewer** (D159 §3: no translated message inside `dangerouslySetInnerHTML`): `markdown.ts` no longer writes
own texts into the HTML. Blocked links/images carry `data-blocked="<code>"` (and `data-alt` for images), managed
blocks carry empty label/notice paragraphs, and `splitBlocks` returns `{code, name}`; `MarkdownView` fills labels,
reasons and tooltips with `textContent`/`title` in a layout effect, re-run when the language changes. The hostile
Markdown suite admits only the two new escaped `data-*` attributes.

**Own HTTP diagnostics** (`harness_local/i18n/{en,es}.json`: 46 keys, +24): the literals of `api/managed.py`,
`api/app.py` (read-only restore, simulation not found) and `api/security.py` (host, origin, cross-site, CSRF header)
come from the catalog in the stored visual language (`storage.preferences.language`, English if unreadable). The
security guard reads it from `app.state.language`; codes, statuses and JSON keys are unchanged. Service errors that
the API passes through (`str(error)` of storage/services) are still the modules' own text → T021.

## Exceptions kept on purpose

- Protocol and technical values: chat command names (`/abrir-fase`, `/estado`, … are Spanish protocol tokens of
  `chat_commands.py`; the English catalog names them literally), statuses/codes shown in `title`, hashes, paths,
  commands, JSON evidence, `harness-local …` invocations, `local-config-*` formats, marker syntax and `D088`.
- The endonym `Español` in `LANGUAGE_NAMES`; anchors `#doc-<slug>` (the slug fallback `seccion` is part of URLs).
- Server and agent content: diagnostics produced by services/storage, agent answers, questions, reasons, documents,
  logs, Pydantic/FastAPI validation errors and browser network errors are shown as received (D159 §3).
- The UI still compares two server texts it does not own: `managed blocks are generated` (document edit refusal)
  and `changed since` (draft CAS); both are English service texts today. T021 must keep them or move the UI to codes.

## Not done here (owners)

- Service/CLI diagnostics, argparse help and the two remaining script-coupled messages → **T021** (scan at the end of
  this task: 475 Spanish-looking literals in 44 modules outside `api/`, including intentional ones such as the Spanish
  vocabulary of `core/engine/document_text.py`, frozen v1 recipes and bilingual parser aliases).
- Browser QA en/es, light/dark, desktop/mobile, keyboard and lengths → after T021 (HITL).

## Validation

- `node --test frontend/tests/*.test.mjs`: 93/93 (baseline 89 + 4 new: segments, `LocalizedError`,
  protocol literals in both catalogs, a problem without diagnostic). Updated: preparation (texts through `t` in both
  languages, unknown recipe), metrics (formats in es and en, coverage plurals, roles), diff (EOL note and byte sizes
  per language), markdown (codes instead of Spanish reasons; safety table), managed-api (localized pending error).
- `npm --prefix frontend run check` and `run build` OK (the existing >500 kB chunk warning).
- New `tests/product/test_api_diagnostics.py`: CSRF, cross-site and `project_id` diagnostics in en and es through
  saved preferences with unchanged codes; the fixed access-key line and its two script consumers; no Spanish string
  literal left in the `api` package. One older Spanish expectation in `test_managed_api.py` now reads the catalog.
- `uv run --frozen --offline pytest -q` (xdist): 1608 passed, 2 skipped, 29 subtests passed.
  `python3 -m unittest discover -s tests -p 'test_*.py'`: 8 OK. No schema change, so no Alembic check.
- Not run: services, browser, agents, providers, smokes, network, `scripts/dev` or the wheel checks
  (`check_distribution.py` changed only in the access-key match).

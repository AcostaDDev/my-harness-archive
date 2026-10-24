# P011-T009 — English prompts, the frozen language directive and documents in the work language

Implemented on 2026-10-23 from `6504f45` (clean checkout). The user's instruction authorizes this next task and one
local commit in English. Contract: [T001 §4 and §5](P011-T001_CONTRATO_APERTURA.md#4-congelación-concurrencia-y-salida-estructurada)
(D159), D158, D166–D168; implementation decision D169.
[Flow](../flows/project-work-language.md#directiva-y-documentos-generados-p011-t009-d169).

HITL (2026-10-23), questions the documents left open, answered by the user:

1. **Scope.** Keep the deterministic generation of every harness-written document in T009 (no split into a new task).
2. **Commit messages.** Technical (T): subjects and `Harness-*` trailers stay as they are for both languages; only
   the task title, written by the planner, follows the work language.

## What exists now

**Directive** (`core/engine/language.py`, `core/engine/prompts.py::render_attempt`):

- `language-directive-1`: engine text appended after the editable template (and the executor routing) and before the
  engine schema. It states `Respond to the user in {visual}. Write project documentation and code in {work}.`, the
  V fields (to the user) and W fields (documents and code) of the role from the T001 §4 map, the T values that stay
  literal, that mixed-language sources are read and quoted unchanged, and the D088 heading/field labels of the work
  language. It declares its precedence over language instructions in templates or project files.
- The pair comes only from the claimed job's `language_context` (`SQLiteManagedRepository.job_language`), passed by
  the supervisor to `OfflineEngine`, `chat_turn`, `planning_turn` and `check_phase`. It is never re-read from the
  preferences and no template variable can replace it.
- `language-context-1` validated: unknown format, values outside en/es or a work language other than the frozen
  context's stop the attempt in `prompts` before invoking. Jobs without a pair (null, or `ui-language-1` of D166)
  render exactly as before: same text, no `language` key in the snapshot.
- Prompt snapshot: `language = {directive, ui_language, work_language, sha256}`; `rendered`/`rendered_sha256` cover
  the directive. Both providers receive it through the stdin prompt they already use (Codex `exec … -`, Claude
  `--print`); the adapter keeps the hash of the bytes sent. No flag, system prompt, permission or tool changes.
- Continuations (retry/revalidate) inherit the first job's pair (D166/D167), so a visual change rules only new jobs.

**Templates** (`core/engine/templates/*.md`): English originals without Spanish marker examples (`«## PNNN —
título»`, `Estado:`, `Sin persistencia`, `Fase activa`, `Restricciones compartidas`, `"Ajusta X"`); they point to
the directive's labels. New builtin ids by content hash; frozen catalogs and saved custom versions stay readable.

**Documents in the work language** (`core/engine/document_text.py`, `documents.py` and callers):

- en/es vocabulary for the managed blocks (STATE, NEXT_STEPS, ROADMAP, DECISIONS index), the D088 skeleton (README,
  SPECIFICATION, ARCHITECTURE, ROADMAP, DECISIONS, DDBB-DIAGRAM, STATE, NEXT_STEPS, AGENTS and the provider wrappers),
  the archive REVIEW/SUMMARY, the transition documents, the definition record `DEFINITION.md`, the onboarding
  `SUMMARY.md`, the truncation note and test/token/turn labels. The language is the frozen context's
  `work_language`: task commits, confirmed edits, export, closure/transition, phase plan, definition acceptance,
  onboarding adoption and the definition turn defaults.
- A context without a work language (frozen before D167) keeps the historical Spanish bytes; the Spanish outputs are
  byte-identical to the previous code (checked against a dump of the previous generators, below).
- Chat task text (`chat.task_text`): labels in the work language; contexts without one keep its historical English.
- Reconciliation contract (`storage/phases.py`): its English instructions name the baseline/active-phase headings and
  the status label in the work language.
- Unchanged by design: paths, markers, codes, statuses, JSON, commands, commit messages/trailers (HITL), parsers
  (already bilingual), D088 budgets, the single DECISIONS record, the v1 layout export (`D036`, no work language),
  the child app's functional language.

## Not done here (owners)

- Visible API/CLI/UI messages and preview warnings (`budget_warnings`, acceptance blockers, deterministic chat
  command answers, `chat_commands`) → T010.
- Quality of real model output in either language: not evaluated (fake agents only; no providers authorized).
- No token saving is claimed for choosing English.

## Test strategy

New `tests/product/test_language_directive.py` (15 test functions, 53 cases):

- Render without a pair (null, `ui-language-1`) equals the previous render; every role × the four pairs gets the
  directive before the schema with its sealed snapshot; the V/W map names real schema fields; invalid pairs and a
  context mismatch stop before invoking (engine level, no agent request); a custom template keeps its text and
  cannot replace the pair; builtin templates contain no Spanish markers.
- Spanish generation equals the historical default; English generation contains no Spanish labels and the parsers
  read it (ROADMAP fields, tasks, fields, baseline, active phase, decision status); AGENTS ≤60 and wrappers ≤15
  lines; chat task text keeps its English bytes and its Spanish labels parse.
- Journeys with the four visual/work pairs: definition turn → acceptance (template and records in W) → first task →
  commit (block in W), and task → chat turn → check → closure (REVIEW/SUMMARY/ROADMAP/successor STATE in W) → chat
  proposal confirmed in the successor phase (task text in W); every attempt carries its job's directive and pair.
  Onboarding B for two pairs. A visual change between jobs: the first job and its retry keep `es`, a later job `en`.
- Both providers (synthetic CLI probe) receive the directive in stdin with the recorded SHA-256 and no new flag.
- Updated expectation: the onboarding prompt test now looks for the neutral English wording.

## Validation

- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`: 1605 passed, 2 skipped, 29 subtests passed
  (T020: 1552 + 53 new).
- `python3 -m unittest discover -s tests -p 'test_*.py'`: 8 OK.
- `node --test frontend/tests/*.test.mjs`: 89/89 (frontend not changed).
- Spanish byte identity: a script outside the repository dumped 22 generator outputs (blocks with every branch,
  review/summary with and without consumption, skeleton with omitted/excess commands, definition record, template
  identity) before and after the change; `cmp` identical.
- `npm --prefix frontend run check` and `run build`: OK (the existing >500 kB chunk warning; frontend not changed).
- `alembic upgrade head` + `alembic check` on a temporary database: no new operations (no schema change).
- Not run: OpenAPI export (no API change), services, browser QA, agents, providers, smokes, network, `scripts/dev`
  or the wheel checks.

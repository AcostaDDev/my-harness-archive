# P011-T005 — English comments: frontend, scripts and examples

Implemented on 2026-10-23 from `1fe17af` (clean checkout). The user's instruction authorizes this next task and one
local commit in English. Precedents: D154/D158/D159/D162/D163, [T001 inventory](P011-T001_INVENTARIO.md) treatments
U, H, E3, E6 and E8; implementation decision D164.

HITL (2026-10-23), two questions the documents left open, answered by the user:

1. Visible strings of the maintainer scripts (`scripts/*.py`) → **translate them now**. They have no catalog and T010
   does not list `scripts/**` among its allowed paths. Strings that match product output stay until the product
   message changes (see "Couplings" below).
2. Package description → "Local application that orchestrates Codex and Claude Code agents to plan, implement,
   review and commit tasks in Git repositories".

## Scope and method

Every T001 row owned by T005: the 38 TS/TSX sources of `frontend/src` plus `vite.config.ts`, `styles.css`,
`index.html`, frontend configuration, the maintained scripts, the current examples, `pyproject.toml`, `.gitignore`
and `.gitattributes`. Each file was reviewed whole. TS/TSX comments were extracted with the TypeScript compiler API
(leading/trailing ranges, JSDoc and `{/* */}` JSX comments) and translated by hand through an exact-match table
(each source fragment had to occur exactly once); CSS comments by `/* */` ranges. No automatic translation or bulk
substitution. Section dividers keep their width; no new line exceeds 120 characters or the line it replaces.

Not translated, by contract:

- Visible UI strings, ARIA labels, number/date formatting and `<html lang="es">` → T010 catalogs (inventory below).
- Bilingual chat commands (`chat-commands.ts`: `estado`, `siguiente`, `tarea`, …): kept, server grammar (D088).
- `frontend/openapi.json` and `src/api.generated.ts` (E3): regenerated in T004, no Spanish left; not edited.
- `frontend/package-lock.json` (E8): untouched.
- Historical scripts (E6) `examples/first_use/prepare.sh` and `examples/provider_matrix/*`: identified as historical
  evidence, bytes preserved, excluded from the public cut (T002/T014/T015); not current instructions.
- Internal references (`H6.2 E3`, `DNNN`, `PNNN-TNNN`) inside comments are kept, as in T003/T004; T014 decides how the
  public baseline explains them.

Identifiers: TS identifiers (compiler API) and Python names (AST) of the group checked against the T001 stem list;
only English false positives (`textarea`, `Pagination`, `diff_sha256`), so nothing was renamed.

## Resolved inventory

C = comment lines translated. R = residual Spanish string literals after the task (candidate scan of string,
template and JSX text nodes with the T001 regex plus common Spanish function words) and their owner.

| File | C | R → owner |
|---|---:|---|
| `Chat.tsx` | 2 | 58 → T010 |
| `Phases.tsx` | 7 | 106 → T010 |
| `SessionGate.tsx` | 2 | 14 → T010 |
| `Shell.tsx` | 3 | 15 → T010 |
| `charts.tsx` | 7 | 1 → T010 |
| `diff.ts` | 11 | 1 → T010 |
| `main.tsx` | 4 | 4 → T010 |
| `managed-api.ts` | 7 | 1 → T010 |
| `markdown.ts` | 16 | 19 → T010 (blocked-link reasons) |
| `mermaid-view.ts` | 8 | 1 → T010 |
| `metrics.ts` | 13 | 31 → T010 (labels and es-ES formatting) |
| `navigation.tsx` | 2 | — |
| `router.ts` | 10 | 12 → T010 (breadcrumb labels) |
| `task-sources.ts` | 4 | — |
| `ui.tsx` | 10 | 14 → T010 |
| `workspace.tsx` | 4 | 5 → T010 |
| `pages/Docs.tsx` | 19 | 119 → T010 |
| `pages/Phases.tsx` | 1 | 29 → T010 |
| `pages/Planning.tsx` | 23 | 223 → T010 |
| `pages/Project.tsx` | 1 | 21 → T010 |
| `pages/Registry.tsx` | 10 | 154 → T010 |
| `pages/Run.tsx` | 7 | 55 → T010 |
| `pages/Settings.tsx` | 1 | 21 → T010 |
| `pages/Stats.tsx` | 16 | 140 → T010 |
| `pages/Task.tsx` | 1 | 7 → T010 |
| `pages/shared.tsx` | 4 | 37 → T010 |
| `vite.config.ts` | 2 | — |
| Already English comments: `ChatCommand.tsx`, `Logs.tsx`, `Permissions.tsx`, `Prompts.tsx`, `Tests.tsx`, `api.ts`, `chat-commands.ts`, `preparation.ts`, `session.ts`, `pages/Home.tsx`, `pages/Preparation.tsx` | 0 | 15 + 7 + 17 + 27 + 21 + 2 + 11 + 23 + 23 → T010; 6 → kept (bilingual commands) |
| `styles.css` | 17 | — |
| `index.html` | 0 | `lang="es"` → T010 |
| `.npmrc`, `package.json`, `tsconfig.json` | 0 | — |
| **Frontend total** | **212** | **1240 candidates → owners above** |

Residual counts are candidates from a finite pattern scan, not a linguistic certificate; T010 re-inventories each
surface when building catalogs.

Tools and examples (comments, docstrings and, per HITL 1, script messages):

| File | Change |
|---|---|
| `scripts/dev.py` | Docstring/argparse description, help, progress and error messages, comments; `--config` help no longer lists only local-config-1/2/3 (any local-config is loaded) |
| `scripts/dev` | Shell comment |
| `scripts/toolchain.py` | Docstring and error messages |
| `scripts/check_distribution.py` | Docstring, comments, assertion messages and final summary |
| `scripts/build_distribution.py`, `export_openapi.py` | Docstring |
| `scripts/smoke_cli.py` | Already English |
| `examples/local_config.example.toml` | Comments and placeholders (`/ABSOLUTE/PATH`, `Author Name`, `REVIEWER-MODEL`, `my-web`, JUnit label) |
| `examples/django-recipe.example.toml`, `typescript-web-recipe.example.toml` | Comments and placeholders |
| `examples/managed_demo.py` | 3 comments (literals were already English) |
| `pyproject.toml` | Description (HITL 2) and the pytest comment |
| `.gitignore` | 3 section comments; `.gitattributes` already English |

### Couplings to product messages

Three script strings match Spanish product output and are kept, with a comment pointing at their source:
`'clave de acceso en'` (`dev.py`, `check_distribution.py` ← `api/session.py`), `'módulo:atributo'` and
`'Esquema SQLite'` (`check_distribution.py` ← `services/managed_runtime.py`, `launcher.py`). When T010 translates
those messages it must update the scripts in the same change; its allowed paths do not include `scripts/**`, so the
planning of T010 must extend them or make the scripts language-independent. Open note, not resolved here.

## Validation and limits

- TS/TSX: SHA-256 of the non-comment token stream (compiler API, JSDoc nodes excluded) identical to `HEAD` for all
  38 files; the comparator detects a one-character string change. CSS with comments removed identical to `HEAD`.
- Example TOMLs: parsed data identical to `HEAD` after mapping the translated placeholders; keys unchanged.
- Residual scan: no accented or Spanish candidate left in the 228 comment ranges of the frontend, except the
  `12,3 mil` output sample (it documents current es-ES formatting); none in the scripts beyond the couplings.
- `node --test frontend/tests/*.test.mjs`: 82/82; `npm --prefix frontend run check` and `run build` OK (only the
  existing chunk-size warning).
- `python3 -m unittest discover -s tests -p 'test_*.py'`: 8 tests OK. `uv run --frozen --offline pytest -q`
  (xdist): 1520 passed, 2 skipped, 29 subtests passed. `uv lock --check --offline` OK; `py_compile` of the scripts,
  `sh -n scripts/dev` and `scripts/dev.py --help` OK. Alembic not run: no schema change.
- Not run: `scripts/dev` services, `build_distribution.py`/`check_distribution.py` (they install and start the
  package), agents, providers, smokes or network. The changed script messages are not covered by tests.

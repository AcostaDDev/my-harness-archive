# P011-T003 — English comments and identifiers: core and profiles

Implemented on 2026-10-22 from `140c14a` (clean checkout). The user's instruction authorizes this next task and
one local commit in English. Precedents: D154/D158, [T001 contract](P011-T001_CONTRATO_APERTURA.md) §5 and
[inventory](P011-T001_INVENTARIO.md) treatment C; implementation decision D162. No unresolved design question
required HITL.

## Scope and method

Every Python file under `src/harness_local/core/**` and `src/harness_local/profiles/**` (35 files) was reviewed
whole, including inline comments and Spanish without accents. Besides the `core/engine` and `profiles` rows,
this covers the other core rows T001 assigned to T003 (`core/__init__.py`, `project_onboarding.py`,
`simulation.py`), the modules T019 created or kept in core (`tree.py`, `managed_mode.py`) and the docstring left
in `engine/import_commit.py` (T019/T004 row, inside the path scope of this task).

Comments and docstrings were extracted with `tokenize`/`ast` and translated as exact, unique old→new pairs;
comment blocks were replaced line by line to keep indentation and inline positions. No automatic translation or
bulk substitution was used. Section dividers keep their width and no changed line exceeds 120 characters.

Not translated, by contract:

- String literals of any kind. Visible messages and diagnostics belong to T007/T010; generated document prose,
  commit messages and prompts belong to T009 (V/W/T map, versioned templates).
- Bilingual parser aliases and commands (`planning.FIELD_NAMES`, `SHARED_HEADING`, `documents.BASE_HEADING`,
  `DECISION_STATUS`, `STATE_HEADING`, `chat_commands.COMMANDS`): D088 grammar, kept in both languages.
- `ProjectProfile` field values: `recipes/typescript_web.py::fingerprint` hashes `asdict(typescript_web_profile())`,
  so a cosmetic change would alter a v1 recipe identity (T001 §5, E1).

## Resolved inventory

C = comment lines, D = docstrings translated. Residual Spanish literals are listed with their owner.

| File | C | D | Residual Spanish literals → owner |
|---|---:|---:|---|
| `core/__init__.py` | 0 | 1 | — |
| `core/engine/__init__.py` | 0 | 1 | — |
| `core/engine/acceptance.py` | 0 | 3 | — |
| `core/engine/bootstrap.py` | 0 | 1 | — |
| `core/engine/bootstrap_discovery.py` | 0 | 1 | — |
| `core/engine/chat.py` | 0 | 4 | — |
| `core/engine/chat_commands.py` | 0 | 1 | Bilingual command names kept; error/proposal texts → T010 |
| `core/engine/commit.py` | 4 | 9 | — |
| `core/engine/context.py` | 10 | 2 | — |
| `core/engine/contracts.py` | 7 | 3 | — |
| `core/engine/definition.py` | 9 | 11 | Conversation summary prose → T009 |
| `core/engine/document_export.py` | 3 | 5 | Exported block prose → T009 |
| `core/engine/document_ops.py` | 11 | 9 | Fresh phase document prose → T009; `STATE_HEADING` alias kept |
| `core/engine/documents.py` | 13 | 23 | Generated documents/templates → T009; parser aliases kept |
| `core/engine/evidence.py` | 2 | 2 | — |
| `core/engine/import_commit.py` | 0 | 1 | Onboarding commit message → T009 |
| `core/engine/journal.py` | 0 | 2 | — |
| `core/engine/junit.py` | 4 | 2 | — |
| `core/engine/metrics.py` | 12 | 5 | — |
| `core/engine/onboarding_commit.py` | 0 | 1 | Archive summary and preview warnings → T009/T010 |
| `core/engine/permissions.py` | 0 | 0 | Already English |
| `core/engine/phases.py` | 1 | 8 | — |
| `core/engine/planning.py` | 2 | 2 | `FIELD_NAMES`/`SHARED_HEADING` aliases kept |
| `core/engine/prompts.py` | 10 | 1 | — (schema and template text → T009) |
| `core/engine/review.py` | 4 | 1 | — |
| `core/engine/serialization.py` | 1 | 1 | — |
| `core/engine/validation.py` | 4 | 2 | — |
| `core/engine/workflow.py` | 8 | 9 | — |
| `core/managed_mode.py` | 3 | 3 | Diagnostics for earlier activations → T010 |
| `core/project_onboarding.py` | 12 | 2 | — |
| `core/simulation.py` | 1 | 1 | Validation message → T010 |
| `core/tree.py` | 0 | 1 | — |
| `profiles/__init__.py` | 0 | 1 | — |
| `profiles/reference_project.py` | 0 | 1 | — |
| `profiles/typescript_web.py` | 2 | 1 | JUnit declaration label: fingerprint-bound v1 value (E1) → T004/T009 |
| **Total** | **123** | **121** | |

Identifiers: AST names (`Name`, `FunctionDef`, `ClassDef`, arguments and attributes) were checked against a list
of Spanish stems; none were found besides the bilingual literals above. No renaming was needed.

## Validation and limits

- AST of all 35 files with docstrings blanked: identical before and after (SHA-256 per file); comments are not
  part of the AST. Behavior, persisted keys, catalogs, paths and recipe fingerprints are therefore unchanged.
- Residual scan: no Spanish candidate remains in comments or docstrings of the group.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: 8 tests OK.
- `uv run --frozen --offline pytest -q` (xdist): first run 1512 passed, 2 skipped, 1 failed:
  `test_cli_agents.py::test_recovery_blocks_live_owner_and_group_after_lease`, a process/lease timing test; it
  passed 3/3 in isolation with `-n 0`, and it cannot depend on comment-only changes. Second full run on the
  same tree: 1513 passed, 2 skipped. Recorded as a load-sensitive intermittent, not as a fix.
- Not run: Alembic (no schema change), Node/frontend (not touched), agents, providers, services or network.
  No test was added: the task forbids tests that only repeat comments.

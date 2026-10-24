# P011-T019 — Legacy/A retirement

Implemented on 2026-10-22 from `1e23829189ee8c48995b33028854bd82ebbff2e4` (clean checkout).
The user's instruction authorizes this next task and one local commit in English. Precedents: D155, D159,
T001 §6; implementation decision D161. No unresolved design question required HITL.

## Dependency inventory and disposition

The pre-deletion review followed imports and callers against T001 §6, including B's inheritance from
`ImportRepository`, its `project_imports` row and `purpose=import_commit`. A matching name did not determine
removal. The following groups record the original dependencies and their final disposition.

| Original group | Original consumers / reason to inspect | Final disposition |
|---|---|---|
| `api/legacy.py`, `api/events.py`, `services/observation.py`, `storage/legacy.py`, `storage/observation.py`, `storage/navigation.py`, `adapters/legacy.py`, `adapters/evidence.py`, `core/legacy.py`, `core/evidence.py` | Legacy viewer, index, read APIs, watch loop, events/SSE; bounded file reader also used by old activation integrity | Remove exclusive modules. Extract only bounded regular-file reads into `adapters/safe_files.py`; backup continues using sealed references without importing an indexer |
| `core/project_import.py`, `core/project_normalization.py`, `core/engine/import_conversation.py`, `templates/import-project.md` | Flow A classification, normalization, conversational source and exclusive prompt; B used `TreeEntry` and phase declaration parsers | Remove A. Move `TreeEntry`/inventory error into `core/tree.py`; keep supported D088 phase declaration parsing with common document adoption in `engine/import_commit.py` |
| `adapters/project_import.py` | A inventory reader plus shared blobs/filter/gitlink/tree guards consumed by B and preparation | Remove A reader. Extract `_tree`, `_blobs`, `check_filters`, `check_submodules`, `check_tree` to `adapters/import_git.py`; preserve local-object-only Git boundary |
| `storage/import_drafts.py` | A source reader and private draft CAS, inherited by B | Remove A source/observation. Extract private CAS storage into `storage/private_drafts.py`; B retains `onboarding-drafts/<id>` |
| `engine/import_commit.py`, `storage/project_import.py` | A preview plus B's adoption, writer, sealed intention, recovery and phase settlement | Remove A tree/preview builder. Retain common document adoption/commit and repository used by `OnboardingRepository`; no A subclass/entry remains |
| `core/migration.py`, `adapters/migration.py`, `storage/migration.py`, `services/migration.py` | Activation, copying/indexing snapshots, abandon/revert/export; managed admission/Git marker also depend on their read guard | Remove all activation/reversion services/writers. Extract read-only rules, filesystem probe/drift and authority to the three `managed_mode.py` modules. Existing artifact directories stay protected directly by runtime/registry/creation |
| `api/app.py`, `api/managed.py`, `api/schemas.py`, `cli.py`, `services/managed_runtime.py`, `services/managed.py`, `storage/planning.py`, prompts | Routers, startup observer, dispatch, public contracts and A conversation branch | Remove routes/commands/observer startup and A dispatch/conversation. Managed `/mode` returns only root/project/refusal. Classify retained work in `storage/retired_work.py` before factories/effects |
| `frontend/src/legacy.tsx`, router, main, Shell, Home, Project, Planning, clients/styles | Viewer, navigation, activation actions and shared onboarding page | Remove viewer and exclusive CSS/actions/routes; specialize the shared page to B. Keep simulation client, current managed UI, private draft editor and B's profile confirmation |
| Models, schema, migrations 0001–0023, backup, codecs, metrics | Old data, managed run history, SQLite migration and B reuse | Preserve metadata and revision bytes. Historical purposes/prompts remain data; no observer consumes old watch flags |
| Legacy/A tests and `tests/fixtures/legacy/` | Exclusive viewer/import/normalization/activation behavior; some fixtures/helpers and boundary checks also serve B | Remove exclusive tests/fixtures; move neutral helpers to `onboarding_helpers.py`, rebase shared filters/gitlinks/object/recovery coverage on B, add synthetic old-installation retirement tests |
| H0 simulations, `storage/migrate.py`, frozen bootstrap/closure compatibility, provider fixtures | Independent synthetic core, database upgrades and managed histories; unrelated meanings of legacy/import | Preserve. No third project entry, old project activation or observation is exposed |

Twenty exclusive backend modules/resources and the legacy React viewer are removed. No schema/table, user
file, stored conversation, intent, run, snapshot or migration is deleted automatically. Earlier ADR bodies,
phase archives and P011-T001/T002 evidence remain unchanged, even when their inventories name removed files.

## Behavior and compatibility

- Exactly two entries remain: create from a brief, or onboard a repository without harness. Both continue under
  normal managed monitoring. Registration/reopening of an existing managed project uses its existing authority.
- Old UI routes resolve to not found with no redirect. Legacy API, A import and activation/reversion endpoints
  are absent and return 404 after local/session guards. Restored archives retain their uniform read-only
  mutation refusal. Removed CLI commands fail argument parsing before SQLite or checkout access.
- B retains frozen HEAD inventory, reviewer export, private CAS, human questions, documents/profile hashes,
  local-object/filter/gitlink/ignored-destination guardrails, confirmed sealed commit and atomic P001 adoption.
  Its pending/interrupted operations retain normal reconciliation of the exact intention and commit.
- A commits/turns and inconsistent imports are quarantined before constructing ports, agents or writers, or
  checking the checkout. Classification uses run purpose, request, conversation kind/root, B inventory format,
  matching source hashes/HEAD/tree and `preview.flow=onboarding`; `import_commit` alone never identifies B.
  Missing/malformed sources, contradictory flow/origin or request cannot fall through into B.
- ACTIVE jobs with expired leases keep the existing recovery path. Explicit `confirm-stopped` checks exact
  owner/version/reason and process/group liveness before closing the job/releasing its lock. It records the
  resolution while retaining retired operation/conversation/request/intent data. It never sends a signal to a
  persisted PID or executes an A intent. Retained unresolved intentions continue blocking another writer;
  manual data resolution is outside this retired product flow.
- PREPARING/REVERTING activations remain blocked for manual resolution. An existing ACTIVE activation can
  authorize managed work only with matching marker/manifest identity/hashes, intact sealed snapshot bytes and
  no new/modified old-scope paths. No API or library service can activate, finish, abandon or revert one.
- `watch_enabled=true` remains inert. Startup and restore construct no observer and do not traverse watched
  external roots. Backup verifies/copies sealed snapshot/export references, preserves SQLite rows and restores
  query-only; it does not recreate an index or resume retired work. Older schemas still use explicit SQLite
  migration, independently of removed project activation.
- Frozen prompt catalogs can read and round-trip the retired `import-project` record. Current catalogs ignore
  old active heads; editing/activation/current validation and rendering cannot make that prompt operational.
  Managed histories, projections, metric labels and independent synthetic simulations remain readable.

SPECIFICATION F03/F05, modes, §8 and global criteria 1/11/13 now describe these behaviors; architecture, data
notes, current flows, README, OpenAPI and generated TypeScript match the retirement. The canonical
`flows/legacy-migration.md` now explains compatibility; historical flow evidence stays in archived phases.

## Validation and limits

All execution uses offline synthetic tests, temporary Git/SQLite/processes and scripted agents. No product
service, browser, real CLI/provider invocation, smoke, installed-package journey, global configuration change,
network, child project operation, push, tag or publication was performed. TestClient lifespans are synthetic
in-process fixtures. The package built here is a local manifest check, not the approved T015/T016 candidate.

Final results are recorded below. The first complete run exposed two remaining
runtime callers of the removed migration service; their protected directory now comes directly from runtime.
A subsequent concurrent check exposed short fake-CLI probe timeouts under test load and a cursor test race:
an incomplete event page may acquire a new tail. The cursor regression now checks that its immutable prefix
is unchanged, while retaining full gap/duplicate/restart assertions. No diagnostic timeout or runtime behavior
was relaxed. The final suite is run without another Python suite concurrently.

| Check | Result |
|---|---|
| Complete pytest suite | 1,512 passed, 29 subtests passed, 2 opt-in variants skipped; 296.72 s. The final preserved path-normalization adjustment is additionally covered by 23 serial retirement/startup checks, all passed |
| unittest discovery | 8 passed; four tests exclusively tied to removed legacy fixtures were retired |
| Node | 82 passed, including old-route absence and B routing |
| OpenAPI export and generated client | Regenerated; 22 retired paths removed, all B paths preserved, no new endpoint; current planning kinds exclude A |
| TypeScript / frontend build | Passed; existing bundle-size advisory remains |
| Alembic on a fresh temporary SQLite | Upgrade to head and `check`: no new upgrade operations |
| Local source and UI-staged wheel/sdist manifests | Source wheel/sdist: 163 entries each. Final UI-staged artifacts: 267 entries each, including 104 web files; twenty exclusive backend components absent, B/compatibility resources present, no cache/Git/bytecode, no retired frontend API/action strings |
| Frozen evidence and diff review | D001–D160 bodies, archived phases, migrations and recipe sources unchanged; 337 local links/anchors, 19 tasks (3 complete/16 pending), 161 indexed ADR and D088 budgets valid; diff reviewed and whitespace check passed |

A 183-test focused pass during implementation covered retirement, B conversation/commit/recovery,
zero-project definition/bootstrap and prompts. The later complete suite includes those guards; the final 23-test
serial pass includes the added canonical-artifact-path protection regression. The complete suite also covers registration, both recipes, fake-agent
journeys through first task/commit/phase closure, CAS/permissions, backup/read-only restore, managed projections
and the event cursor. Provider behavior, real B/D095 validation (D151), installed-candidate first use and browser
QA are not claimed; T016 retains its own scope and authorization. T003 is next; no other P011 task is executed.


The two opt-in skips require separately prepared real Django/Python wheels or a real node/npm cache; no downloads
were attempted. Existing Starlette TestClient deprecation and frontend chunk-size advisories remain. No new
schema/dependency/version change or candidate installation is implied by these checks.

Final UI-staged package manifest (local `.local/p011-package/`, not an approved release):

| Artifact | SHA-256 |
|---|---|
| `harness_local-0.1.0-py3-none-any.whl` | `85388a38b5aa0681c6d7e6ed4636f3045d489812e19ff427e391b023b0bc6a5e` |
| `harness_local-0.1.0.tar.gz` | `09dfe88a9ae48e9d45b74c81d67566b55671d90163deffb397f96b89b52607d5` |

Commands: the AGENTS unittest/pytest/Node/type/build checks, OpenAPI export/type generation, temporary
`alembic upgrade head` + `alembic check`, offline `uv build` and UI staging/ZIP/tar inspection. Repeated Python
checks after intermediate failures are distinguished above; no outstanding test failure is left unresolved.

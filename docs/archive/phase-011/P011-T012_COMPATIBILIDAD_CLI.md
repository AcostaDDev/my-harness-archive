# P011-T012 — Automatic CLI discovery and capability compatibility

Base: `920d9b2`, clean checkout. Date: 2026-10-23. The user requested continuation and a local commit in English.
Implementation decision: D174. Contract: [T011](P011-T011_CONTRATO_COMPATIBILIDAD_CLI.md), D173; language emission:
D171/D172. No new library, migration, package version or provider invocation was needed.

## HITL resolution

The implementation exposed an unresolved distinction in T011: a later Codex help listing the same flags cannot
prove the internal condition that suppresses a global trust write. The user chose **automatic admission of later
clients under the known capability contract, with conditional compatibility and no claim of verified internal
effects**. This clarifies/supersedes T011's requirement for a new artifact-specific semantic finding before admitting
each later writer. The sandbox, inline untrusted project table, memory, history and configuration controls remain
mandatory; local removal or incompatibility blocks. No per-version acceptance, evidence sidecar or CLI pin is
transferred to the end user. Historical D068/D122 source/real evidence retains its original scope.

## Implemented behavior

**Configuration.** `local-config-7` extends v6. Each agent/preset still declares its provider, environment and
timeout, and the existing model/effort/tool policy. `executable` and `cli_version` are optional. Missing executable
means resolving only the selected provider on that declaration's explicit PATH, with absolute nonempty directories;
an optional explicit executable supports nonstandard installations. No shell, inherited PATH, disk-wide scan,
global changes, auth/status/login or auto-update is involved. An explicit old pin remains an assertion, with a
localized mismatch/migration diagnostic. Formats 1–6 and their configuration hashes remain readable.

Parsing is data-only, including for TOML projects. A separate startup/composition step resolves effective roles
and freezes their observed versions. Unused presets/providers are not probed in normal operation; an explicit
`check-config --preflight` still diagnoses defaults and all preset roles. An unresolved v7 composition cannot
queue work. Registration/creation preserve their existing CAS and trust confirmations. V7 uses the v2 recipes;
v5 remains on v1 and v6 remains on v2, without changing recipe bytes or issued fingerprints.

**Minimum and candidates.** Both read/write roles require stable Codex **0.163.0** or Claude Code **2.1.304**.
Below-floor clients receive detected/minimum versions and an update instruction. Invalid, ambiguous, oversized
numeric components or prerelease version lines are rejected. A later stable minor/major is not rejected by its
absence from a patch list. `SUPPORTED`/`WRITE_SUPPORTED` remain historical evidence, not admission allowlists.

`cli-capabilities-1` is packaged policy. Its hash binds the policy and the three compatibility/diagnostic/transport
source modules. Reference and candidate observations are separate; candidate provenance is
`conditional-known-interface`, and `internal_effects_verified` is false. The profile records the effects not
verified locally: effective permissions, startup persistence, automatic-memory effects, transitive dependencies,
authentication and inference. The policy does not invent real evidence from help, an exit code or a fake CLI.

**Preflight and actual request.** `cli-14` checks every emitted flag, including Codex config/color/cwd/Git-check
support and Claude's role-specific restricted/schema flags. A token prefix is not a match. Where help explicitly
advertises choices, a required sandbox/approval/output value excluded by those choices blocks. Probes retain
D042's temporary cwd, closed stdin, full explicit environment, ten-second / 256-KiB combined-output bounds and
own-group cleanup; they never infer through a model call.

Every attempt obtains a fresh version/help observation. Before the target can execute, an independent check of
the constructed request preserves read/write sandbox, explicit canonical write roots, network setting, approvals,
trust, memory/history/project-doc controls, configuration sources, MCP/hooks and reader tools/schema. Guard removal
creates a refused intent with no target launch. Stream terminal/payload validation and existing cancellation,
unknown-group handling, grants and no-retry/fallback rules remain in force.

**Identity and freezing.** Job versions include observed provider versions, launch hashes and policy hash; v7 also
records automatic versus explicit assertion and PATH versus explicit executable. Attempt process specs retain
their own safe observation, compatibility provenance and local guard check. The observed launch identity covers
the explicit executable, an explicit interpreter script, symlink resolution and shebang interpreter; mutable data
arguments such as logs are not treated as launch code. Content hashes use a stat-validated cache (inode, size,
mtime and ctime), not a cached compatibility verdict. Unsupported interpreter resolution is refused.

A new API mutation resolves the current effective clients once per project in that request. GET/HEAD/history/
document views remain passive. An updated compatible client can therefore be used by new work without editing
TOML; an already queued job never adopts it. Current/frozen mismatch quarantines conservatively before model
invocation. Identity is checked around preflight and again after durable process identity, immediately before GO.
A changed gated target is stopped as the adapter's own group; stopped versus uncertain state is recorded honestly.

A failed bind preflight records safe structured reports in a `cli_preflight_refused` event. Per-attempt refusals
keep `launch_permitted=false`, no target identity and a stopped capture. This adds JSON fields/events, not tables
or codec rewriting. Previous runs, snapshots, metrics, streams and decision bodies remain untouched.

## Changed surfaces and compatibility

| Surface | Change |
|---|---|
| `adapters/cli_compatibility.py` | Discovery, stable minimums, source-bound policy, launch identity and local request guard |
| `adapters/cli_diagnostics.py`, `cli_agents.py` | Automatic observation, full emitted syntax/advertised choices, per-attempt revalidation and pre-GO identity |
| `services/local_config.py`, `managed_runtime.py`, `project_registry.py`, `recipes/__init__.py` | V7 data/resolution split, selected presets, refreshed admissions and v2 recipe selection |
| `storage/managed.py`, `services/managed.py` | Refuse unresolved/below-floor new runs; journal safe bind refusal evidence |
| `api/managed.py` | Stable compatibility error codes and request-local resolution for mutations, passive reads |
| `frontend/src/pages/{Registry,Home}.tsx`, frontend en/es catalogs | V7 preset selection remains enabled and configuration guidance includes v7 |
| `i18n/{en,es}.json` | Actionable install/update/mismatch/identity/value/guard diagnostics in the existing emission language |
| `examples/*.example.toml`, README | Current v7 examples without version pins; support guidance corrected. Broader English first-use rewrite remains T014 |
| [Data diagram](../DDBB-DIAGRAM.md), [CLI flow](../flows/cli-compatibility.md), [agent flow](../flows/project-agents.md) | Same-task parity for JSON evidence and the new resolution/preflight flow |
| `tests/product/**`, `tests/fixtures/cli_capabilities/` | Synthetic reference/candidate clients/help, below-floor/parser/identity/guard negatives and existing regression updates |

The source recipe files/resources tied to v1/v2 fingerprints are unchanged. Only the generation registry adds v7.
Public baseline tests no longer read the real help originals under `tests/fixtures/cli_help/`; those bytes remain
private and unchanged per D160. New help fixtures are independently authored synthetic flag lists, with provenance.
Historical scripts in `examples/first_use/`, `examples/provider_matrix/` and the old real-smoke pins are not
requalified by this task. Their unit regressions use synthetic current clients; no real smoke was authorized/run.

No response schema, route, request shape or generated OpenAPI/TypeScript type changed. A data-only comparison of
`create_app().openapi()` to `frontend/openapi.json` is equal, so regeneration is unnecessary. Existing versions maps
and diagnostic codes are extensible. The frontend recognizes v7 in its existing preset selector and configuration
guidance; no version-entry or candidate-approval flow was added.

## Validation and limits

Checks completed offline:

| Check | Result |
|---|---|
| `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q -n 4` | **1667 passed, 2 skipped, 29 subtests passed**, 448.97 s; existing FastAPI/httpx deprecation warning |
| Final `pytest -q -n 4 tests/product/test_cli_discovery.py` | **39 passed**, 23.45 s; covers the final pre-GO missing-file cleanup adjustment and added deletion case after the full run had started |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | **8 OK** |
| `node --test frontend/tests/*.test.mjs` after UI changes | **93/93** |
| `npm --prefix frontend run check` / `npm --prefix frontend run build` | Correct; existing bundle-size warning (>500 kB) |
| OpenAPI comparison | Equal to checked-in JSON, without service/database startup |
| Document parsers, links, budgets, immutable evidence and final diff | 22 tasks / 16 completed, 174 unique decisions, **628 relative links/anchors** resolve; `git diff --check` correct |

The two opt-in cases require explicit Django wheels/Python and a populated TypeScript npm cache; neither was
enabled/downloaded. A first full parallel run had one command-group uncertainty in the new CLI/language matrix
(1665 passed, 1 failed, 2 skipped); that case passed alone. The matrix now uses an explicit synthetic direct-Python
validation that checks the actual edit through the real command journal/group boundary. It does not duplicate
npm's descendant-process lifecycle, already covered separately. No production command-liveness guard was relaxed.
The subsequent full run and the final targeted checks above pass; overlapping targeted counts are not additional
unique full-suite cases.

STATE is 22,980 bytes (under 24 KiB), its baseline under 12 KiB. NEXT_STEPS was already 55,876 bytes against
49,152; now 56,466. Its pre-existing size warning is retained explicitly, without truncating or compacting the
whole task ledger in this task. D001–D173 bodies, archived documents, real-help originals, stream fixtures and
recipe sources/resources bound to issued fingerprints are unchanged. No new dependencies or lock changes.

Both changed flow diagrams were reviewed against implementation. A Node-only Mermaid parse attempt could not
initialize DOMPurify without a DOM (`addHook` unavailable); it is not counted as a syntax/render pass. No diagram
render/browser QA is claimed. T013 retains the full semantic/render audit. These checks are synthetic/local, not
new evidence of real-provider effects.

No installed provider CLI was executed or inspected, no provider auth/global configuration was read/copied/changed, no service
was bound to a port, and no browser, installation, network, package build, push or publication was run. Tests use
temporary synthetic checkouts/SQLite and fake clients; the harness was not operated on this repository. API tests
run in-process. The full pytest suite performs temporary schema migrations; no development/user database is migrated.
No standalone Alembic check (schema unchanged), wheel/sdist build or distribution smoke was run.

Conditional compatibility is not a proof of every future release's undocumented behavior. Hashes cover identified
launch files, not arbitrary transitive modules/native targets behind an opaque wrapper, and do not provide OS
isolation against adversarial replacement. An unsupported/unidentifiable launch chain blocks; a recognized chain's
unobserved dependencies/effects remain declared. Broader real characterization, exact-package first-use/browser QA
and release work retain their own T014–T017 scopes and authorizations. B/D095 deferrals and exhausted provider
consents are unchanged.

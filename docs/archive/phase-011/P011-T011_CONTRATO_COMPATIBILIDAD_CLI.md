# P011-T011 — CLI capability compatibility contract

Date: 2026-10-23. Base: `01ff9f7` (clean checkout). **Design only; T012 implements it.**
The user's instruction authorizes this next task and a local commit in English. No provider CLI, agent,
service, smoke, installation or publication is authorized by this document.

Precedents: D042 (bounded diagnosis), D052 (provider/role separation), D059/D068 (Codex writer scope and
trust), D066 (memory), D122 (latest characterized CLI baseline), D124 (`cli-13` Git-check exception),
D159 (P011 contract) and D160 (private real-help fixtures). Current behavior remains `cli-13` and its
exact version lists until T012. This contract does not broaden support by itself.

HITL resolved by the user: someone downloading the project from GitHub must not specify either CLI version.
The system discovers the installed clients, observes their versions automatically and works from an established
stable minimum; an older client gets an update instruction. This replaces both proposed operator candidate
acceptance and grandfathered admission below the new minimum. Existing history remains readable. It also rules
out asking end users to author/import compatibility evidence for each update. The capability contract and its
evidence are the application's responsibility. Decision: D173.

## 1. Evidence and current behavior

Three evidence levels must remain separate, including in the public support statement:

| Level | Establishes | Does not establish |
|---|---|---|
| Version/help observation | The discovered local command reports its version and advertises required flag tokens | Accepted values, effective overrides, startup side effects, permissions, authentication or inference |
| Semantic characterization | Identified source/configuration semantics or a bounded behavior investigation supports a specific capability, provider, access mode and artifact | Every release in a numeric range, every platform, absence of all auxiliary persistence or successful inference |
| Real execution evidence | The exact recorded binary/environment/role completed the authorized scenario | Other binaries, all models/accounts, future behavior or universal isolation |

Synthetic tests verify the harness's decisions and transport. They are a fourth, explicitly synthetic provenance,
never evidence that a real provider implements a guard. A candidate cannot become verified by passing a fake CLI.

Current source anchors (paths below are relative to the repository root):

| Source | Finding used by this design |
|---|---|
| `src/harness_local/adapters/cli_agents.py`: `CLIConfig`, `SUPPORTED`, `WRITE_SUPPORTED` | Constructor and writer checks enforce exact versions before invocation; executable argv and environment are explicit |
| Same module: `ROLES`, `access_for`, `argv_for`, `skips_git_check` | Seven reviewer roles share read access; only `executor` writes; role-specific argv and frozen Git-check conditions |
| Same module: `frozen_versions`, `bind_process_journal`, `invoke` | Job identity comparison precedes preflight; version/help results are copied into each process intent, but observations are currently reused within the claimed job |
| `src/harness_local/adapters/cli_diagnostics.py`: `REQUIRED`, `ACCESS_REQUIRED`, `PATTERNS`, `preflight_config` | Exact configured/observed version match, token presence, bounded probes; no semantic or authentication certification |
| `src/harness_local/adapters/streams.py`: `AgentStream.record`, `finish` | Known terminal plus valid payload required; original events and observed metadata retained; duplicate/error/truncated streams cannot succeed |
| `src/harness_local/adapters/process_gate.py`, `processes.py` | Durable process identity before GO, own POSIX group cancellation, conservative recovery without signalling an old PID |
| `src/harness_local/services/local_config.py`: `_presets`, `_composed`, `ports` | Per-role preset restrictions and composition hashes; loading configuration does not run provider commands |
| `tests/product/test_cli_baseline.py`, `test_cli_diagnostics.py`, `test_cli_memory.py`, `test_codex_workspace_write.py`, `test_definition_git_check.py`, `test_agent_roles.py` | Existing synthetic regression owners; the baseline test additionally reads private real-help fixtures |

The historical evidence is [D122's characterization](../archive/phase-009/P009-T013_CARACTERIZACION_CLI.md)
and [D124's correction](../archive/phase-009/P009-T014_DEFINICION_SIN_GIT.md). D122 ties Codex 0.163.0
to source commit `83086188ae0614bd882818ff1aa23f3194962012`; it compared the trust guard, overrides,
memory/instructions, sandbox and streams to 0.162.1. Claude 2.1.304 was inspected through help and binary
literals, without public implementation source. No new source-to-binary comparison occurred in T011.

## 2. Numeric eligibility and support labels

Versions use the existing full-line provider formats: `codex-cli X.Y.Z` and `X.Y.Z (Claude Code)`.
Compare bounded integer tuples, never strings or floats. Reject prereleases, suffixes, ambiguous/multiple lines,
invalid encoding and unrecognized output; do not extract a plausible substring from a diagnostic. "Stable" here
means a normal released version without a prerelease suffix, not a promise of semantic stability for pre-1.0 Codex.

| Provider / access | Previously characterized versions (historical) | Minimum for new work | Reference release |
|---|---|---|---|
| Codex / read and write | Read: 0.161.0, 0.162.1, 0.163.0; write: 0.162.1, 0.163.0 | **0.163.0** | D122/D124; latest characterized Codex used by the pilot |
| Claude / read and write | 2.1.295, 2.1.296, 2.1.304 | **2.1.304** | D122; latest characterized Claude used by the pilot |

These are conservative common read/write floors selected from the existing evidence, not claims about the first
release of every feature. For example, official Claude documentation dates `--restricted` to 2.1.248 and
`--permission-prompts` to 2.1.259; neither fact establishes the complete harness contract at those versions
([CLI reference](https://code.claude.com/docs/en/cli-reference)). Do not lower the floor to either number.

Any normal release at/above its provider's floor is numerically eligible, including a changed minor/major. There
is no hard-coded maximum or exact patch allowlist. A capability family means the transport contract in §3, not
a guaranteed numeric range. Changed capabilities or unestablished essential guards block before invocation;
version order alone cannot certify them. No actual later release is characterized by this document.

Below-floor versions, including Codex 0.161.0/0.162.1 and Claude 2.1.295/2.1.296, are refused for **new** work,
with detected version, required minimum and an actionable update instruction. This resolves the second HITL
question: no inherited exception for the 0.161.0 reader's synthetic-only memory evidence is needed. Old
configuration formats, completed jobs and historical evidence remain readable; historical admission lists and
frozen versions are not rewritten. Retaining their readers does not authorize resuming a below-floor client.

Support has separate fields, not one overloaded `available` boolean:

- **Reference** identifies the releases behind the built-in capability profile, with evidence references and
  limitations. It does not certify every installation of a release. Older baselines keep their historical label.
- **Candidate** identifies a later eligible release recognized by the same capability profile. It is admitted
  automatically if that profile establishes all essential capabilities for the requested access. No checkbox,
  per-version consent, pin or user-supplied evidence is required. It remains a candidate rather than becoming
  real-verified; the technical provenance must not interrupt the normal product flow.
- **Real-verified evidence** is attached to its exact scenario/artifact/platform, with a reference. It is not a
  label automatically inherited by another installation merely reporting the same version.
- **Incompatible** covers a violated known requirement; **unknown** covers an inconclusive observation or
  an unestablished essential guard. Both block launch with a precise diagnostic and correction.

These distinctions preserve D122/D124 as historical evidence and the real-evidence limits in STATE; they do not
reread private runs or reuse exhausted consent. D173 supersedes the old exact-list admission policy for new work.

## 3. Required capability matrix

All rows apply to both access modes unless stated otherwise. **Essential** means that an unestablished guard
blocks a candidate before a model-capable invocation; it is not replaced by an operator risk acknowledgement.
Presence in help establishes syntax only. Characterization must cover the value, precedence and consuming
behavior used by the transport, not just a symbol with the same name.

| Capability | Codex transport contract | Claude transport contract | Required evidence / failure boundary |
|---|---|---|---|
| Fresh noninteractive request | `exec`, stdin `-`, `--ephemeral`; no resume/fork | `--print`, fresh UUID `--session-id`, `--no-session-persistence`; no resume/continue | Syntax plus session semantics; essential. No session fallback |
| Streaming | `--json`, `--color never` | `--output-format stream-json`, `--verbose`, `--include-partial-messages` | Syntax and characterized envelope; stream validity enforced at runtime, never inferred from exit 0 |
| Selection | `--model`, `model_reasoning_effort` | `--model`, `--effort` | Exact requested model/effort frozen; known effort vocabulary remains bounded; model availability is not probed |
| Read boundary | `--sandbox read-only` | `--restricted`, inventory/allow rules exactly `Read,Glob,Grep`; no execution tools | Essential semantics of effective permissions, cwd and source loading; declaration alone is insufficient |
| Write boundary | `workspace-write`, canonical checkout explicit in `writable_roots`, `network_access=false`, `exclude_slash_tmp=true` | Only explicitly configured tools/allow rules, `dontAsk` and deny unanswered prompts; no `--restricted` for writer | Essential. Preserve D059's TMPDIR behavior; neither provider becomes a general OS sandbox |
| Approval/grants | `approval_policy="never"`, `--ignore-rules`; unsupported network/tool grants rejected | `--permission-mode dontAsk`, `--permission-prompts none`; exact, unexpired persisted tool grants only | Essential; keep provider-specific enforcement and denials; no bypass mode or broader replacement tool |
| External configuration | `--strict-config`, `--ignore-user-config`, `--ignore-rules`, built-in `model_provider="openai"`, `web_search="disabled"` | `--setting-sources ""`, inline `disableAllHooks=true`, `--strict-mcp-config`, empty `mcpServers`, `--disable-slash-commands`, `--no-chrome` | Essential isolation from the configuration/integrations excluded by the current contract; managed policy conflicts block rather than weakening guards |
| Trust side effect | Writer: whole inline `projects` table with canonical root `trust_level="untrusted"`; reader: characterized no-write condition | Keep the characterized startup/configuration behavior; do not add persistent project approvals | Essential. Codex's automatic trust-write guard and override parsing need specific semantic evidence; help cannot prove suppression |
| Memory/instructions | `features.memories=false`, `memories.generate_memories=false`, `memories.use_memories=false`, `history.persistence="none"`, `project_doc_max_bytes=0` | Inline `autoMemoryEnabled=false`; reject a configured `CLAUDE_CODE_DISABLE_AUTO_MEMORY` other than `1`; preserve instruction/configuration exclusions of the current argv | Essential consumption/precedence, separately from ephemeral/session flags; no global-memory cleanup or auth redirection |
| Typed response | JSON object parsed and engine-validated from final agent message; no new schema flag added | Reader's `--json-schema` is the frozen typed schema; writer keeps current object response contract | Characterized shape plus strict local validation; no repair prompt or second provider invocation |
| Git precondition | `--cd` and conditional `--skip-git-repo-check` exactly as `skips_git_check` / D124 | No equivalent flag invented | Required for supported outside-Git read scenarios; never give the exception to the writer or a live checkout by version guessing |
| Environment/authentication | Complete supplied mapping; no inherited environment; current UID/USER checks | Same; conflicting memory environment rejected | Essential local invariants; auth stays with installed CLI. No login/status, credential reading/copying or global changes in diagnosis |
| Cancellation/recovery | Durable intent/GO, own POSIX group, bounded TERM/KILL/drain | Same | Essential harness invariant plus characterized process behavior; unknown liveness blocks safe recovery; no signalling recovered PIDs |

The union of **every flag actually emitted** is required, including `--color`, `--cd`, `--skip-git-repo-check`
when applicable, and Codex `-c`/`--config`. T012 must close the difference between that union and today's
smaller `REQUIRED` token set. Claude reader flags remain role-specific; a writer need not advertise reader-only
schema/restricted features to satisfy its write contract. Token matching must not accept `--model-extra` as
`--model`; short/long aliases require explicit equivalence in policy. Removing a guard from argv to make a probe
pass is forbidden. New tool names or effort values require a policy/transport review, not automatic widening.

### Stream acceptance remains a runtime check

Codex must report exactly one recognized terminal (`turn.completed` or failing `turn.failed`); the payload comes
from `item.completed` with `item.type=agent_message`. An `error` fails the result. Claude must report exactly one
`result`, with boolean `is_error` and one of the known subtypes (`success`, `error_during_execution`,
`error_max_turns`, `error_max_budget_usd`, `error_max_structured_output_retries`); only non-error `success` can
complete. Its payload is `structured_output` or the current `result` object/text path, then a JSON object validated
against the engine contract. These facts come from `AgentStream`, not a promise about future provider events.

Unknown nonterminal events/fields remain preserved and tolerated under the existing parser. Unknown terminals,
duplicate terminals, invalid JSON/NaN/UTF-8, missing terminal, truncated tail, error or nonzero exit cannot yield
an accepted result. Requested selection is not copied into observed fields; reported model changes remain visible.
A preflight cannot prove what a later stream will contain, so stream failure stops that attempt with evidence;
it does not trigger fallback, provider retry or a compatibility probe using inference.

## 4. Built-in capability policy and semantic evidence

A candidate must satisfy numerical eligibility, complete syntax requirements and all essential semantic guards
for its access mode. The harness must not synthesize semantic evidence from a help hash, an exit code, the
operator's willingness to try it, a version comparison or an unverified self-report by the CLI.

The application ships reviewed semantic profiles for each provider/access mode. A profile contains the controls
in §3, their documented meanings, source/characterization references, observable applicability predicates and
limits. The current baseline evidence supports the reference implementations; official documented controls
support the compatibility contract. Matching required syntax is one predicate, not a stand-alone proof of
effective permissions. Essential guards that are not directly probeable must have an explicit policy justification
and a sound applicability check; absence/uncertainty blocks. T012 must not mark such guards established simply
because a version is higher, a help hash exists or a test fake prints the required flags.

Concretely, the profile evaluator checks (1) discovered provider/release and every emitted flag/advertised required
value, (2) the locally constructed argv/overrides against the complete immutable guard contract in §3, including
canonical roots, grants, memory, trust and configuration exclusions, and (3) each semantic finding's applicability
predicate and evidence reference. Each finding records whether it is locally observed, established by the
reference implementation/documented interface, or unknown. Applying a documented interface contract to a later
candidate is a compatibility assumption, not newly observed provider behavior. An undocumented essential effect
such as Codex startup trust persistence cannot be established by (1)/(2) alone: absent an applicable maintained
semantic finding, block that access mode. Do not certify an entire provider because only its reader is supported.

Profiles and their canonical hashes belong to the packaged application. The end user does not configure
`accept_candidate`, a CLI-version pin, an evidence path or a per-binary attestation. Do not move a patch allowlist
into an operator-maintained file. Profile data is not code imported from a project, a model-produced approval,
an automatic source download or an inference call used as a compatibility test. A profile revision must record
which capability changed and why its evidence applies. T012 must implement a bounded representation of the
resulting per-attempt findings. Existing TOML/SQLite/codec/OpenAPI changes need explicit version treatment and
same-task parity; none is changed in T011.

Codex's trust suppression is a particularly sensitive profile dependency: D068/D122 established the startup
condition and inline-table semantics for the reference source. Official configuration documentation does not
promise the absence of that startup write. A new profile or an unrecognized implementation needs maintained
source/behavior evidence about that condition, parser and consuming paths; an isolated unchanged fragment is
insufficient if startup/precedence/permissions changed elsewhere. A bounded authorized behavior investigation
must reach the triggering condition; a prior auth failure is inconclusive. Closed-source Claude needs identified
official semantics and inspection/authorized behavior with explicit limits, following D122; matching literals
alone do not establish effective enforcement. None of this becomes an end-user setup chore.

An eligible later client recognized by the profile is accepted automatically without changing a patch list.
Local identity hashes bind what was actually checked; they are not an exclusive set of vendor build hashes.
If no profile can establish an essential guard, stop with a capability diagnostic directing the user to update
the client/application as appropriate. Never ask for a manual override. This cannot guarantee every future
release's hidden behavior: a capability-compatible candidate has conditional compatibility, not fresh real
verification. T012's positive/negative fixtures must distinguish that policy decision from actual provider
evidence and prove that unknown essential guards block. No later real release is newly accredited in T011.

## 5. Automatic discovery and version observation — HITL resolved

For new configuration, the user chooses reviewer/executor provider/model/effort as before and does not supply
`cli_version`. The system resolves `codex` and `claude` using the service's explicit PATH, then observes the
selected client's `--version` and applies the floor/profile automatically. An optional explicit executable path
can serve nonstandard installations; it does not require knowing the version. Resolve symlinks and record the
chosen launch identity. No shell/login-shell invocation, disk-wide search, global-config mutation or client
installation/update is part of discovery. Do not execute an unrelated provider merely because it is installed;
only selected/configured provider roles are preflighted. Discovery does not change the chosen provider/model.

Missing client → name it and tell the user to install it or set its path. Below floor → show actual/minimum
versions and tell the user to update that client. Eligible compatible client → continue automatically, including
an unlisted later version. Incompatible/unknown capability → name the missing guard and correction, not a prompt
to type a version or accept risk. Display observed versions in diagnostics; version entry is not a normal step.

Parsing configuration remains data-only. A separate controlled detection/resolution step before admitting new
work obtains the observed version and identity. Never freeze a literal `auto` or a missing version as though it
were an observed one. T012 versions the new automatic configuration semantics; older formats/pins remain readable
with their old hashes. If an old configuration explicitly asserts a version, a mismatch is still reported rather
than silently rewriting it; guide migration to the automatic format. All new public examples use automatic
discovery. Below-floor clients cannot launch new work even through an older readable format.

## 6. Observation, freezing and restart

The automatically observed exact version, launch identity and built-in profile/policy id/hash are part of the
job's frozen composition, separately for reviewer and executor, including each preset role. An optional legacy
configured assertion is recorded separately. Runtime preflight observes the launch command before
each model-capable attempt, after frozen identity/claim checks; it must not reuse a previous attempt/job/process's
`available` result. Explicit diagnosis uses the same policy and role requirements without creating a job.

The per-attempt immutable compatibility record must contain:

- Provider, logical role, read/write access, automatically observed version, optional legacy configured assertion,
  reference/candidate classification and discovery source, plus evidence provenance/limitations; absent observations
  remain absent. No required-version input is invented for the user.
- Policy/adapter id and canonical hashes; required/established/missing/unknown capability ids; semantic evidence
  reference/hash separately from the flags actually observed.
- Launch identity: canonical executable resolution and SHA-256 of the executable artifacts in the explicit launch
  chain, including scripts/native target behind a wrapper where applicable; complete argv/configuration and
  environment hashes remain bound through the existing private process spec. A pathname or version alone is
  insufficient. Reject an unidentifiable chain; PATH resolution is limited to the controlled discovery in §5.
- Safe version line, help hash, bounded probe outcomes and structured diagnostic codes. Do not store raw help,
  stderr, environment values or credentials in a public report. The existing private intent/evidence remains private.

Observe and compare artifact identities before and after probes and immediately before releasing the process
gate. A changed binary, symlink target, wrapper/script, environment/composition or packaged profile invalidates
the observation; stop before the model-capable target executes. Do not silently re-probe and retry. The record
must be durable and associated with the attempt before GO; on refusal, keep the available safe evidence with
the attempt/job failure rather than fabricating a successful process observation. This is cooperative local
integrity checking, not protection against an adversary replacing executable dependencies concurrently.

On restart, revalidate current identities and observations against the frozen job. A changed client, policy,
adapter or configuration cannot be attached retroactively: pending incompatible jobs enter `RECOVERY_REQUIRED`
under the existing conservative mechanism. Historical completed jobs, process specs, attempts, streams, metrics
and snapshots remain byte-for-byte historical. Missing new fields in old records mean "not captured", not a
backfilled capability success. Never restart a live/unknown writer or reinterpret an old intention under a new
policy. A fresh job may automatically detect the updated compatible client; it does not require typing the new
version. T012 must version the changed compatibility contract; reuse of `cli-13` as if unchanged is insufficient.

## 7. Diagnosis and failure order

Keep D042's explicit trusted command, stdin closed, temporary cwd, full supplied environment, per-command
10-second / 256-KiB combined-output bounds and own-group cleanup. Discovery resolves the selected local command;
only `--version` and the provider's help commands are automatic executable probes. No login/status, test prompt,
inference or auto-update.
If an emitted global flag requires top-level help rather than `exec --help`, policy may declare a bounded
top-level help probe; stop the sequence at the first inconclusive/failing requirement. Its existence does not
authorize executing a CLI in this development session.

Use this failure precedence so an actionable cause survives:

| Stage | Refusal | Correction |
|---|---|---|
| Frozen context | Client/configuration/policy differs from queued identity | Resolve/quarantine existing job explicitly; new work redetects automatically |
| Discovery/eligibility | Client absent, version below minimum or unrecognized/nonstable version line | Install/update the named client or supply its path; show actual/minimum, never ask for a version pin |
| Local observation | Spawn/timeout/output/cleanup/encoding failure | Report unknown and fix the exact local command/environment; no inference check |
| Identity/syntax | Legacy assertion mismatch, changed launch identity or missing flag/value contract | Migrate the legacy configuration or use a compatible client; no silent queued-version replacement |
| Semantics | Essential capability absent/unestablished or profile inapplicable | Update client/application as indicated; no evidence import or acceptance override |
| Runtime | Invalid/partial/failed stream, denied tools, cancelled/timeout, live/unknown group | Preserve original evidence and existing stop/recovery behavior; no compatibility fallback |

Stable machine codes and capability ids must be separate from translated corrections. Use the existing en/es
emission language (D171/D172); diagnosis reports observed version, optional legacy assertion, access mode, profile/minimum,
failed capabilities and what was not checked. Public UI/catalogs must not leak executable paths, environment,
raw evidence or account information. `version_help_match` may remain a syntax result but never mean semantic
compatibility or authenticated availability.

No fallback/downgrade, alternative model/provider, retry or global configuration change is introduced. The CLI's
own internal retries/model fallback remain reported as unknown or only-if-observed, as today; the harness cannot
promise they are disabled. Auth, quota, account/model availability and linguistic quality remain untested by
diagnosis. Automatic memory disabled does not imply no auth refresh, logs, caches or auxiliary SQLite writes.

## 8. Official documentation consulted

Read on 2026-10-23; these are moving references, not historical pin source or runtime evidence. No private source,
account, configuration or run content was submitted. Summaries below describe the official pages; the complete
transport requirements above are taken from the local code and decisions, including stricter project choices.

| Reference | Contribution and limit |
|---|---|
| [OpenAI developer commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli) (redirect from `developers.openai.com/codex/cli/reference/`) | Documents noninteractive `exec`, JSON, stdin, sandbox, config overrides, ephemeral, user-config/rules exclusions and Git-check exception. Does not prove the historical trust-write suppression guard |
| [OpenAI configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) (redirect from `developers.openai.com/codex/config-reference/`) | Describes memory/history/project-doc controls, untrusted project configuration and workspace sandbox settings. Documents meanings, not enforcement by an arbitrary future binary |
| [Claude CLI reference](https://code.claude.com/docs/en/cli-reference) | Documents restricted mode, unanswered-prompt denial, tools, schema and configuration flags. Its feature introduction versions do not establish a complete harness minimum |
| [Claude permissions](https://code.claude.com/docs/en/permissions) | Separates tool approval, mode and sandbox semantics; tool allow rules alone are not physical containment |
| [Claude memory](https://code.claude.com/docs/en/memory) | Documents `autoMemoryEnabled=false` and the disabling environment variable. Does not certify every startup persistence path |
| [Claude programmatic runs](https://code.claude.com/docs/en/headless) | Documents streaming/structured output and SIGTERM behavior. Harness parsing, cancellation and hooks controls still require their own contract |
| [Claude settings precedence](https://code.claude.com/docs/en/settings) | Managed settings can override other settings. Empty user/project sources must not be presented as bypassing managed policy |

No newer real binary was inspected or executed. Current docs alone cannot promote an uncharacterized CLI to
baseline, prove all startup exclusions or substitute for D068's trust investigation.

## 9. T012 acceptance matrix

All executable fixtures are synthetic, with synthetic HOME/auth/configuration/projects, streams and evidence.
Use every provider/access mode, the seven reviewer roles and executor where argv differs, all four provider
pairings and preset-based compositions. The minimum meaningful cases are:

| Case | Expected result |
|---|---|
| Client found on explicit PATH; optional path; one selected provider; absent client | Automatic bounded resolution; no version input, unrelated-client probes or shell; useful install/path diagnostic |
| Reference releases 0.163.0 / 2.1.304 in all roles | Automatic version observation, complete capability record, no acceptance prompt |
| Historical below-floor releases, including Codex 0.161.0 reader | New work refused with detected/minimum versions and update instruction; old history/configurations readable |
| Eligible unlisted later release, including changed minor/major, applicable synthetic profile | Accepted without code/list edit, version pin, evidence import or acceptance; receipt remains synthetic/candidate |
| Below floor; invalid/prerelease/overflow version; legacy assertion mismatch | Refused before model-capable launch with specific cause |
| Every actual required flag missing, misleading prefix, unsupported required value | Refused; reader-only requirements do not unnecessarily block writer |
| Help complete/exit 0, but trust/memory/permission/configuration guard unestablished | Blocked before target effects; no override or manual attestation offered |
| Wrong provider/access/policy on profile, missing applicability finding or fabricated observed evidence | Refused; packaged policy is not replaced by project or operator-supplied approval |
| Same version text but executable/symlink/wrapper/script changes between attempts/probes/GO | Old result invalidated; no blind cache reuse or automatic retry |
| New invocation/restart/preset role; update after enqueue; fresh job after update | Fresh access-specific observation; old frozen mismatch quarantined, fresh work redetects without a user pin |
| Four language pairs; request vs worker/CLI emission | Actionable en/es diagnostics from correct frozen/current context; technical ids/hashes unchanged |
| Missing/duplicate/unknown terminal, malformed/truncated stream, denied tool, nonzero exit | Existing failure with original evidence; exit 0 alone never suffices |
| Cancellation, lingering/unknown process group, crash before GO, recovered job | Existing bounded cleanup/quarantine preserved; never signal an unverified persisted PID |
| Config load and standalone diagnosis | No provider run during load; diagnosis creates no jobs, reads no auth and never calls inference |

D160 requires replacing public tests' reliance on
`tests/fixtures/cli_help/{codex-0.163.0-exec-help,claude-2.1.304-help}.txt` with independently authored synthetic
flag/help fixtures in T012. Keep the real originals private and unchanged; remove their public test dependency,
not the negative flag coverage. Mark synthetic text as such and retain provenance/expected tokens separately.
The private fixture README's historical "public text" statement is not permission to redistribute it under MIT.
No copied vendor help or real credentials/runs enter new fixtures. T006 did not complete this replacement.

T012 updates public configuration/preset behavior, API/types if changed, and affected diagrams if implementation
changes data or flow. T013 audits diagrams afterward; it does not excuse missing same-task parity. T014 documents
the delivered contract, T015 excludes real help/private evidence, and T016 verifies the exact candidate package
with fakes under its separately authorized operational scope. This design does not declare those tasks done.

## 10. Operational evidence still required for broader real support

If a real later release is to be advertised as characterized/verified, first propose a separate bounded task with
exact provider/version/role, artifact hashes/launch chain, official/source evidence, synthetic directories,
version/help/behavior commands, permitted network/auth/inference (if any), process/time/output limits and cleanup.
Specify which essential guards the observation reaches and stop at the first failure; no automatic retry or
switch of provider. Obtain its own authorization before running provider commands. Source-only review may settle
a guard without inference; successful inference cannot replace a guard it never exercised. T011/T012 fake tests
do not authorize or claim this evidence. B/D095's real-validation deferral and existing exhausted consents remain.

## 11. Validation of this delivery

The HITL answer is incorporated in §§2/4/5 and D173. Sources/precedents and the final documentary diff were
reviewed. Static checks were run with the existing `.venv/bin/python`, importing the pure document parsers;
no application/service, provider command or agent was launched:

- `plan_tasks`, `parse_roadmap`, `decision_index`: 22 unique P011 tasks, 15 completed / 7 pending, active P011,
  next T012, 173 unique decisions with D173 last. Decision index links include the new entry.
- All **585 relative links/anchors** in the seven changed/new documents resolve. Official external references
  were read during the source review (§8); this local check does not download links.
- Existing D001–D172 bodies are unchanged, compared against `HEAD`; no file under `docs/archive/`, fixture,
  code, configuration or package is modified. No new managed blocks or rewrites of frozen evidence.
- Budgets: STATE 21,826 bytes (under 24 KiB), accumulated baseline under 12 KiB. NEXT_STEPS was already
  54,447 bytes versus its 49,152-byte budget; it is now 55,876 bytes. That existing warning remains explicit;
  compacting the whole task ledger is outside this CLI-contract task. No truncation or hidden omission.
- `git diff --check` and final scope/diff review: correct. Product, API, SQLite schema and implemented flows
  are unchanged, so diagram/model/OpenAPI regeneration and runtime suites are not pertinent to this delivery.

Not run: pytest/unittest, Node/types/build, Alembic, distribution scripts, browser QA, provider CLI probes,
authentication or inference, smokes, services, installations and publication. No new real CLI compatibility is
claimed. T012 implements the contract; a wider real-evidence investigation follows §10 with its own scope.

# Harness Local

Harness Local is a local application that runs a development harness with AI coding agents over your own Git
repositories. A **reviewer** agent plans and reviews in read-only mode; an **executor** agent is the only writer.
The harness validates every change with your project's own commands, binds the review to the exact content, and
makes the commit itself. Work is organized in phases and bounded tasks, with project documentation, chat, metrics
and recovery after crashes. Everything runs on your machine: the service listens only on `127.0.0.1`, and the
models are reached through the official Codex and Claude Code CLIs with your own account.

[Leer en español](README.es.md)

## Status

- **Pre-release.** The first local version is complete within the scope described below; the package declares
  version `0.1.0` and is not published on PyPI. The version of the first public release is set when it is published.
- **Platform.** Only macOS on Apple silicon (ARM64) has been tested. Other platforms are not characterized.
- **Evidence.** The offline test suites use temporary Git repositories, SQLite and fake agents. Real runs with
  providers exist only for the capabilities marked as such in [Supported scope](#supported-scope-and-limits).
- **First use.** The steps below were checked against the scripts and the CLI, but have not yet been rehearsed end
  to end from a clean clone. Please report anything that does not work as written.
- **Next.** An optional continuous mode (tasks → commits → check → closure → next phase) is planned for v0.2.0;
  see the [roadmap](docs/ROADMAP.md).

Licensed under the [MIT license](LICENSE); see [NOTICE.md](NOTICE.md) and the
[third-party notices](NOTICE-THIRD-PARTY.md).

## How it works

1. You choose the reviewer (provider, model and effort) and the executor provider and model catalog per project.
2. Each phase has a plan of tasks in `docs/NEXT_STEPS.md`. Queuing a task freezes its contract, profile, prompts,
   CLI versions and language pair.
3. The reviewer plans the task (or a deterministic plan is read from `NEXT_STEPS`) and picks the executor model.
4. The executor edits the checkout within the allowed paths. The harness runs the profile validations (and its
   formatter, if declared), then the reviewer accepts or asks for corrections, up to a limit.
5. You confirm the commit of the accepted content. The run becomes **COMMITTED**.
6. When every task is done, a READY check and your closure authorization archive the phase in one commit and open
   the next phase from the roadmap.

SQLite holds the operational state (runs, jobs, phases, conversations, metrics); Git holds code and documents;
Markdown holds the intent (specification, architecture, roadmap, decisions). Every effect records its intent first,
so an interrupted operation is reconciled instead of repeated. A job left in an unknown state waits for you to
confirm that its writer stopped.

## Two ways to start a project

- **Create a new project from scratch.** Choose a projects folder in the UI, name the project and start a
  definition conversation with the reviewer from a brief. You review and accept the generated documents; the
  harness makes the root commit. With a recipe (Django or TypeScript web), a confirmed preparation then creates the
  environment and the technical scaffold.
- **Onboard an existing repository without a harness.** Register a Git checkout that has at least one commit and
  no harness documents. The harness inventories its committed tree without running project code, the reviewer drafts
  the documentation and a profile proposal, and you confirm the documentation commit that adopts phase `P001`.

Registering again a project that this harness already manages is a normal registration, not a third entry. Older
harness formats are not imported.

## Requirements

| Use | Requirement |
|---|---|
| Running the service | macOS (tested on ARM64), Python 3.14 (tested 3.14.4) in its own virtual environment, Git with `--no-lazy-fetch` support (tested 2.50.1) |
| Building the package or developing | Exactly uv 0.12.19, Node 24.15.0 and npm 11.12.1 (the scripts check them); Python 3.14.4 available to uv |
| Agents | Codex CLI ≥ 0.163.0 and/or Claude Code ≥ 2.1.304, installed and signed in by you |
| Child projects | The tools of their profile or recipe: e.g. `python3` for the minimal example; CPython 3.11–3.13 and uv for the Django recipe; node/npm with a local npm cache for the TypeScript web recipe |

**Authentication.** The harness never stores credentials. Each CLI uses its own login, so sign in with `codex`
or `claude` before starting. The TOML gives every agent an explicit environment (`HOME`, `USER`, `PATH`), nothing is
inherited from the service, and `USER` must be the account that runs the service.

**Agent CLIs.** Clients are discovered on each role's explicit `PATH` (or an optional executable path); you do not
declare a version. Each version is checked against a minimum and against the capabilities the harness needs.

| CLI | Minimum | Status |
|---|---|---|
| Codex | 0.163.0 | Verified at 0.163.0; later releases are candidates |
| Claude Code | 2.1.304 | Verified at 2.1.304; later releases are candidates |

A candidate is a later release admitted automatically when its observed interface matches the known contract.
Its compatibility is conditional: help output and probes do not prove every internal effect, and no future version
is guaranteed. An older client gets an instruction to update; an observable incompatibility blocks the attempt
before the provider is invoked. Permission, sandbox, memory and trust controls are never relaxed.

## Install from a clone

The first step needs network access to fill the local caches; everything after it runs offline. Run from the
repository root:

```sh
git clone <repository-url> my_harness && cd my_harness
UV_CACHE_DIR=.local/uv-cache uv sync --frozen --no-python-downloads
npm --prefix frontend ci --ignore-scripts --cache .local/npm-cache
```

Real use runs from the built package installed in its own virtual environment, never from the development
checkout. Build and verify the package, then install it (replace `/path/...` with your own absolute paths):

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python scripts/build_distribution.py --out-dir /path/package
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python scripts/check_distribution.py --dist /path/package
uv venv --python 3.14.4 --no-python-downloads /path/venv
uv pip sync --python /path/venv/bin/python --require-hashes /path/package/requirements.txt
uv pip install --python /path/venv/bin/python --no-deps /path/package/harness_local-0.1.0-py3-none-any.whl
```

`build_distribution.py` builds the UI from the npm lock and writes the sdist, the wheel and a hashed
`requirements.txt`. `check_distribution.py` installs that wheel in a temporary environment and exercises it with
synthetic agents, without providers or network. The `dist/` folder of a checkout is not authoritative.

## Configure

Copy [`examples/local_config.minimal.example.toml`](examples/local_config.minimal.example.toml) outside every
checkout, make it private (`chmod 600`) and replace its placeholders. It uses one provider (Claude Code) for both
roles and a declared profile for a small Python project tested with `unittest`; its comments explain the switch to
Codex. The [complete template](examples/local_config.example.toml) shows every option of the `local-config-7`
format: per-project presets, a Django declared profile, compositions and TOML-declared projects.
[Django](examples/django-recipe.example.toml) and [TypeScript web](examples/typescript-web-recipe.example.toml)
recipe fragments are added to it to create new projects with a prepared stack.

Then check it:

```sh
/path/venv/bin/harness-local check-config /path/harness-local.toml --preflight
```

`check-config` parses the file and prints identifiers, profiles and frozen versions without environment values.
`--preflight` additionally runs only `--version` and `--help` of each configured CLI; no model is called.

## First run

```sh
/path/venv/bin/harness-local init-db --database /path/state/harness.sqlite3
mkdir -m 700 /path/private-tmp
TMPDIR=/path/private-tmp /path/venv/bin/harness-local serve --database /path/state/harness.sqlite3 --config /path/harness-local.toml
```

`init-db` creates a new database only. `serve` prints `Harness Local: access key at <path>`: open
`http://127.0.0.1:8013` (or the `--port` you chose) and paste the key from that file. The key file lives under
`TMPDIR`, is deleted when the service stops and the session lasts eight hours. Keeping `TMPDIR` in a private
directory of your operating area also keeps the temporary Git indexes there. Stop the service with Ctrl-C.

With `supervisor = true` the service consumes the queue: **every agent attempt invokes the provider CLI with your
account and uses your plan or API quota**. The interface shows tokens and turns as reported or derived per attempt;
it does not know your quota.

From the browser:

1. **Preferences.** Choose the interface language and the default work language for new projects.
2. **New project** (creation) or **Register project** (onboarding), as described in
   [Two ways to start a project](#two-ways-to-start-a-project). Both ask for the project id, the composition from
   your TOML, the agents and the work language, and show a preview whose exact hash you confirm.
3. **Definition or onboarding conversation.** Answer the reviewer's questions, review the drafts and accept them.
   The harness writes the documents with the layout below and makes its commit. With a recipe, review and confirm
   the preparation plan (files, packages, commands and network mode) before it runs.
4. **Phases → P001 → a task.** Queue the task; follow planning, execution, validation and review on the run page.
5. **Commit.** When the run is *accepted, commit pending*, review the evidence and confirm the commit. The run is
   now **COMMITTED**.
6. **Check and close.** When the phase is complete, run the READY check and authorize the closure.

Each managed project gets this layout: `AGENTS.md` (agent instructions) with `CLAUDE.md`/`GEMINI.md` wrappers,
`README.md`, and in `docs/` `SPECIFICATION.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `STATE.md`, `NEXT_STEPS.md`,
`DECISIONS.md`, `DDBB-DIAGRAM.md`, `flows/`, `phase/` (work files of the current phase) and `archive/phase-NNN/`.
STATE, NEXT_STEPS, ROADMAP, DECISIONS and the archive are maintained by the harness; a normal task does not edit them.

## Languages

Two settings, both English or Spanish:

- **Interface language** — global and changeable at any time in Preferences. It governs the UI, the service and
  CLI messages, the conversation with the agents, their answers to you and their questions.
- **Work language** — chosen per project when it is created or onboarded (prefilled from the global default) and
  immutable afterwards. It governs documentation, plans, decisions, code and comments written in that project.

Changing the default work language only affects future projects. When a task, turn or operation is queued, both
languages are frozen for it: changing the interface language later applies to new interactions only, never to an
attempt, retry or answer already admitted. The pair reaches both providers as a sealed directive in the prompt; it
adds no CLI flags and changes no permissions. Keywords, paths, commands, formats and identifiers are never
translated, and existing files are read as they are.

Example: set the interface to *Español* and keep *English* as the work language of a new project. You talk with
the reviewer in Spanish and read its questions in Spanish, while every document, plan, decision, code change and
comment of the project is written in English — with Codex or Claude Code alike.

`harness-local --ui-language es <command>` chooses the language of a single CLI invocation; without it, the CLI
reads the preferences of an existing database or uses English.

## Safety model

- The service is reachable only on loopback, behind the session key, exact Host/Origin checks and a CSRF header;
  requests marked as cross-site are rejected, so links to the UI from other sites do not open.
- Every effect asks for an explicit confirmation of the exact preview hash: registrations, creations,
  preparations, document edits, commits and phase closures. Concurrent changes are rejected by version checks.
- The reviewer runs read-only. The Codex executor runs in `workspace-write` with the checkout as its only writable
  root and network disabled; the Claude executor gets only the declared tools (no shell). Automatic memory is
  disabled and checkout instructions are not loaded by the CLIs: the engine injects `AGENTS.md` itself.
- Containment is cooperative (CLI sandboxes, path checks, locks and content checks), **not** operating-system
  isolation. Register only repositories and tools you trust, preferably disposable checkouts at first.

See [SECURITY.md](SECURITY.md) to report a vulnerability.

## Operation

**Restart.** Stop `serve` and start it with the same command. Queued work resumes; a job interrupted mid-attempt
shows *Recovery required* until you confirm that its writer stopped.

**Update.** Stop the service and every writer, install the new wheel in the venv and migrate:

```sh
/path/venv/bin/harness-local migrate --database /path/state/harness.sqlite3 --snapshots /path/pre-migration --writers-stopped
```

`migrate` takes a verified SQLite snapshot (outside any checkout) before upgrading and leaves an up-to-date
database untouched. On failure it keeps the database and the snapshot for inspection, without restoring
automatically. `serve` never migrates on startup.

**Backup.** With the service and writers stopped:

```sh
/path/venv/bin/harness-local backup-create /path/state/harness.sqlite3 /path/new-backup --artifact-root /path/harness-state --writers-stopped
/path/venv/bin/harness-local backup-verify /path/new-backup
/path/venv/bin/harness-local backup-restore /path/new-backup /path/restored
```

`--artifact-root` (repeatable) authorizes artifact roots such as the TOML `state_dir`. A restore creates a new,
query-only database with the same schema revision.

**Other commands.** `logs-preview`, `logs-apply` and `logs-inspect` apply an explicit retention to agent streams;
`metrics-backfill` completes metrics; `diagnose-cli` checks one agent configuration. Every command documents its
arguments with `--help`.

**Diagnosis.** Start with `check-config --preflight`. Common blockers are explained in the UI: a CLI below its
minimum or missing from the role's `PATH`, a project without a confirmed work language, a configuration change
that quarantined pending jobs, or a recipe that still needs its preparation.

**Uninstall and keep your data.** Stop the service and delete the virtual environment and the package folder.
The SQLite database, the `state_dir`, backups and the TOML stay where you put them, and each project keeps its
Git history and documents. Delete them only if you no longer need that history.

## Supported scope and limits

| Capability | Offline (synthetic data and fake agents) | With real providers |
|---|---|---|
| Plan → execute → validate → review → commit, phases, closure and archive | Yes | Yes |
| Reviewer and executor, Codex or Claude Code, in the four combinations | Yes | Yes |
| New Django project with the Django recipe | Yes | Yes, macOS ARM64 with Python 3.13 |
| New TypeScript web project with its recipe | Yes, also with real node/npm and a local cache | No |
| Recipes v2 that follow the project's work language | Yes, with synthetic tools | No |
| Declared profiles (`[profiles.*]`) and onboarding of existing repositories | Yes | No |
| Chat, backup and restore | Yes | No |
| Run views, metrics and export preview over large synthetic histories | Yes | Not applicable |

The real runs were made before the current CLI adapter with Codex 0.162.1/0.163.0 and Claude Code
2.1.295–2.1.304; they are historical evidence, not a guarantee for later releases.

Known limits: no operating-system isolation; a recipe-pinned manifest does not accept new dependencies after
preparation; the `typescript-web` profile protects `package.json`, `scripts/**` and `tests/**` from the executor;
after a reboot that renumbers the disk device, creating another project requires choosing the projects folder
again; validations do not record their time; Gemini CLI is not a provider yet (its `GEMINI.md` wrapper only imports
the common instructions).

## Development

```sh
UV_CACHE_DIR=.local/uv-cache uv sync --frozen --no-python-downloads
npm --prefix frontend ci --ignore-scripts --cache .local/npm-cache
scripts/dev
```

`scripts/dev` checks the tool versions, migrates a development database (`.local/harness.sqlite3`) after backing it
up, and starts the API on `:8013` and Vite on `http://127.0.0.1:5173`; it accepts `--database` and `--config`.
Use it only for development: real use goes through the installed package.

Checks (offline once the caches are filled):

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q   # parallel; -n 0 runs it serially
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline alembic check
node --test frontend/tests/*.test.mjs
npm --prefix frontend run check
npm --prefix frontend run build
```

After changing an API contract, regenerate the client types (never edit them by hand):

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python scripts/export_openapi.py
npm --prefix frontend run generate:types
```

Layout: `src/harness_local/` (engine in `core/`, adapters, storage, services, recipes, API, migrations and
message catalogs), `frontend/` (React/TypeScript UI), `tests/` (synthetic tests and fixtures), `scripts/`
(development and distribution) and `examples/` (configuration templates and a synthetic demo).

## Contributing and documentation

Read [CONTRIBUTING.md](CONTRIBUTING.md) and the agent instructions in [AGENTS.md](AGENTS.md) before changing
anything. Project documents:

- [Roadmap](docs/ROADMAP.md), [state](docs/STATE.md) and [next steps](docs/NEXT_STEPS.md).
- [Decisions](docs/DECISIONS.md): the technical decisions of the starting baseline, cited by the code as `DNNN`.

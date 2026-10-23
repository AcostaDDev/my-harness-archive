# Changelog

All notable changes to Harness Local are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Versioning policy

- One version string is shared by the Python package (`pyproject.toml`), the API (`/openapi.json`) and the UI
  package (`frontend/package.json`). A release changes all three together.
- The project is pre-1.0: a minor release (`0.x.0`) may change the configuration, the API or the UI, and its notes
  say what to do. Patch releases (`0.x.y`) only fix defects. Data compatibility does not depend on the version
  number: every release keeps reading older databases and histories, and the SQLite schema is upgraded only by
  `harness-local migrate`, which takes a verified snapshot first.
- `0.2.0` is reserved for the optional continuous mode described in the [roadmap](docs/ROADMAP.md).
- A version is released by tagging its commit and attaching the built sdist, wheel, `requirements.txt` and
  `SHA256SUMS` to a GitHub Release. Nothing is published to PyPI.

## [Unreleased]

## [0.1.0] — not yet released

First public release candidate. Earlier development happened in a private repository; this is the starting point
of the public history, so there is no earlier public version to upgrade from.

### Added

- Local service (FastAPI + SQLite, loopback only, session key and CSRF guard) with a React UI in English and
  Spanish, and the `harness-local` CLI.
- Two ways to start a project: create one from scratch through a definition conversation, or onboard an existing
  Git repository without a harness. Optional Django and TypeScript web recipes prepare a new project's environment.
- Task runs with a read-only reviewer and a single writing executor (Codex CLI or Claude Code, in any
  combination), profile validations, review bound to the exact content and a commit made by the harness.
- Phases with a READY check, authorized closure and archive; project chat, documents, metrics, backups and recovery
  after crashes.
- Global interface language and default work language (English or Spanish); each project's work language is fixed
  when it is created or onboarded.
- Automatic discovery of agent CLIs with minimum versions (Codex 0.163.0, Claude Code 2.1.304) and conditional
  compatibility for later releases, checked by capabilities before each attempt.

### Known limits

- Tested only on macOS on Apple silicon. Real-provider evidence covers only the capabilities marked as such in the
  README.

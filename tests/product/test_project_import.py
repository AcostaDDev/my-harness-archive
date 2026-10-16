"""P008-T009: inventario de solo lectura del Flujo A con checkouts Git sintéticos.

Tres orígenes sintéticos (tipo ReferenceProject, v1 y v2 de este harness) generados aquí, sin datos de ReferenceProject ni
runs reales. Se comprueba la clasificación completa, la detección de origen y fases, la huella estable y que ni el
checkout ni `.git` cambian.
"""

import hashlib
import os
from pathlib import Path
import subprocess

import pytest

from harness_local.adapters.project_import import read_inventory
from harness_local.core.engine.context import Command, EnginePolicy, ProjectContext, ProjectProfile
from harness_local.core.engine.documents import Layout, skeleton
from harness_local.core.project_import import (
    INVENTORY_FORMAT, CheckoutSnapshot, ImportInventoryError, TreeEntry, build_inventory, classify, fingerprint,
)

GIT_ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "Fixture Author", "GIT_AUTHOR_EMAIL": "author@example.invalid",
           "GIT_COMMITTER_NAME": "Fixture Author", "GIT_COMMITTER_EMAIL": "author@example.invalid"}


def lines(count: int, prefix: str = "Rule") -> str:
    return "".join(f"- {prefix} {number}.\n" for number in range(1, count + 1))


REFERENCE_PROJECT = {
    "AGENTS.md": "# Synthetic gym — agent rules\n\n" + lines(70),
    "CLAUDE.md": "# Claude notes\n\n" + lines(18, "Note"),
    "README.md": "# Synthetic gym\n\nSynthetic fixture.\n",
    "pyproject.toml": "[project]\nname = 'synthetic-gym'\n",
    "src/app.py": "print('never executed')\n",
    ".gitignore": ".env\n",
    ".harness/.gitignore": "runs/\n",
    ".harness/README.md": "# Previous harness\n",
    ".harness/config.yaml": "model: synthetic\n",
    ".harness/harness.py": "raise SystemExit('never executed')\n",
    "docs/PROJECT.md": "# Project\n\nSynthetic vision.\n",
    "docs/REQUIREMENTS.md": "# Requirements\n\n- Synthetic requirement.\n",
    "docs/ARCHITECTURE.md": "# Architecture\n\nSynthetic modules.\n",
    "docs/ROADMAP.md": ("# Synthetic gym — Roadmap\n\n## Phase 001 — Foundation\n\nGoal.\n\n"
                        "## Phase 002 — Members\n\nGoal.\n\n# Future roadmap\n"),
    "docs/STATE.md": ("---\nphase: 2\nphase_name: members\ncurrent_task: null\nstatus: active\n---\n\n"
                      "# Synthetic gym — Current State\n\nP001 accepted.\n"),
    "docs/NEXT_STEPS.md": ("# Next steps\n\n## Task queue\n\n## P002-T001 — Member list\n\nDo it.\n\n"
                           "## P002-T002 — Member detail\n\nDo it.\n"),
    "docs/DECISSONS.md": "# Decisions\n\n## D001 — Synthetic stack\n\nAccepted.\n",
    "docs/HARNESS_COMMANDS.md": "# Commands\n",
    "docs/UI_REDESIGN.md": "# UI redesign\n",
    "docs/archive/phase-001/NEXT_STEPS.md": "# P001 next steps\n",
    "docs/archive/phase-001/REVIEW.md": "# P001 review\n",
    "docs/archive/phase-001/SUMMARY.md": "# P001 summary\n",
}
REFERENCE_PROJECT_CLASSES = {
    ".harness/.gitignore": ("foreign", "previous-harness", None),
    ".harness/README.md": ("foreign", "previous-harness", None),
    ".harness/config.yaml": ("foreign", "previous-harness", None),
    ".harness/harness.py": ("foreign", "previous-harness", None),
    "AGENTS.md": ("canonical", "canonical-path", "AGENTS.md"),
    "CLAUDE.md": ("canonical", "canonical-path", "CLAUDE.md"),
    "README.md": ("canonical", "canonical-path", "README.md"),
    "docs/ARCHITECTURE.md": ("canonical", "canonical-path", "docs/ARCHITECTURE.md"),
    "docs/DECISSONS.md": ("renameable", "alias-name", "docs/DECISIONS.md"),
    "docs/HARNESS_COMMANDS.md": ("mergeable", "unclassified-markdown", None),
    "docs/NEXT_STEPS.md": ("canonical", "canonical-path", "docs/NEXT_STEPS.md"),
    "docs/PROJECT.md": ("mergeable", "specification-source", "docs/SPECIFICATION.md"),
    "docs/REQUIREMENTS.md": ("mergeable", "specification-source", "docs/SPECIFICATION.md"),
    "docs/ROADMAP.md": ("canonical", "canonical-path", "docs/ROADMAP.md"),
    "docs/STATE.md": ("canonical", "canonical-path", "docs/STATE.md"),
    "docs/UI_REDESIGN.md": ("mergeable", "unclassified-markdown", None),
    "docs/archive/phase-001/NEXT_STEPS.md": ("historical", "archive-phase", "docs/archive/phase-001/NEXT_STEPS.md"),
    "docs/archive/phase-001/REVIEW.md": ("historical", "archive-phase", "docs/archive/phase-001/REVIEW.md"),
    "docs/archive/phase-001/SUMMARY.md": ("historical", "archive-phase", "docs/archive/phase-001/SUMMARY.md"),
}

V1 = {
    "README.md": "# Synthetic v1\n",
    "app/main.py": "print('never executed')\n",
    "docs/BRIEF.md": "# Brief\n\nSynthetic brief.\n",
    "docs/PROJECT_PROFILE.md": "# Profile\n\nsynthetic\n",
    "docs/DELIVERY_CHECKLIST.md": "# Checklist\n\n- [ ] Synthetic check.\n",
    "docs/DECISIONS.md": "# Decisions\n\nNone yet.\n",
    "docs/STATE.md": "# State\n\nBootstrap accepted.\n",
    "docs/NEXT_STEPS.md": "# Next steps\n\n## P001-T001 — Delivery checklist\n\nWrite it.\n",
}
V1_CLASSES = {
    "README.md": ("canonical", "canonical-path", "README.md"),
    "docs/BRIEF.md": ("historical", "v1-foundation", None),
    "docs/DECISIONS.md": ("canonical", "canonical-path", "docs/DECISIONS.md"),
    "docs/DELIVERY_CHECKLIST.md": ("mergeable", "v1-checklist", None),
    "docs/NEXT_STEPS.md": ("canonical", "canonical-path", "docs/NEXT_STEPS.md"),
    "docs/PROJECT_PROFILE.md": ("historical", "v1-foundation", None),
    "docs/STATE.md": ("canonical", "canonical-path", "docs/STATE.md"),
}

STATE_BLOCK = "<!-- harness-local:managed-state:start -->\nSynthetic state.\n<!-- harness-local:managed-state:end -->\n"
V2 = {
    "README.md": "# Synthetic v2\n",
    "CLAUDE.md": "# Claude\n\nShort.\n",
    "web/index.ts": "export {}\n",
    "docs/SPECIFICATION.md": "# Specification\n",
    "docs/ARCHITECTURE.md": "# Architecture\n",
    "docs/ROADMAP.md": "# Roadmap\n\n## P001 — Foundation\n\nDone.\n\n## P002 — Catalogue\n\nActive.\n",
    "docs/STATE.md": "# State\n\n" + STATE_BLOCK + "\n## Fase activa — P002 Catalogue\n\nWork.\n",
    "docs/NEXT_STEPS.md": "# P002 — Catalogue\n\n## P002-T001 — Product list\n\nDo it.\n",
    "docs/DECISIONS.md": ("# Decisions\n\n<!-- harness-local:managed-decisions:start -->\n- D001\n"
                          "<!-- harness-local:managed-decisions:end -->\n"),
    "docs/decisions/README.md": "# Decisiones\n",
    "docs/decisions/D001-stack.md": "# D001 — Stack\n\n**Estado:** aceptada\n",
    "docs/architecture/README.md": "# Arquitectura detallada\n",
    "docs/architecture/data-model.md": "# Data model\n\n```mermaid\nerDiagram\n```\n",
    "docs/architecture/checkout.md": "# Checkout flow\n",
    "docs/research/README.md": "# Investigación\n",
    "docs/research/spike.md": "# Spike\n",
    "docs/archive/phase-000/BRIEF.md": "# Brief\n",
    "docs/archive/phase-000/DEFINITION.md": "# Definition\n",
    "docs/archive/phase-001/STATE.md": "# P001 state\n",
    "docs/archive/phase-001/NEXT_STEPS.md": "# P001 next steps\n",
    "docs/archive/phase-001/REVIEW.md": "# P001 review\n",
    "docs/archive/phase-001/SUMMARY.md": "# P001 summary\n",
}
V2_CLASSES = {
    "CLAUDE.md": ("canonical", "canonical-path", "CLAUDE.md"),
    "README.md": ("canonical", "canonical-path", "README.md"),
    "docs/ARCHITECTURE.md": ("canonical", "canonical-path", "docs/ARCHITECTURE.md"),
    "docs/DECISIONS.md": ("canonical", "canonical-path", "docs/DECISIONS.md"),
    "docs/NEXT_STEPS.md": ("canonical", "canonical-path", "docs/NEXT_STEPS.md"),
    "docs/ROADMAP.md": ("canonical", "canonical-path", "docs/ROADMAP.md"),
    "docs/SPECIFICATION.md": ("canonical", "canonical-path", "docs/SPECIFICATION.md"),
    "docs/STATE.md": ("canonical", "canonical-path", "docs/STATE.md"),
    "docs/architecture/README.md": ("historical", "v2-folder-readme", None),
    "docs/architecture/checkout.md": ("mergeable", "architecture-detail", None),
    "docs/architecture/data-model.md": ("renameable", "data-model", "docs/DDBB-DIAGRAM.md"),
    "docs/decisions/D001-stack.md": ("mergeable", "decision-file", "docs/DECISIONS.md"),
    "docs/decisions/README.md": ("historical", "v2-folder-readme", None),
    "docs/research/README.md": ("historical", "v2-folder-readme", None),
    "docs/research/spike.md": ("historical", "research", None),
    **{f"docs/archive/{name}": ("historical", "archive-phase", f"docs/archive/{name}")
       for name in ("phase-000/BRIEF.md", "phase-000/DEFINITION.md", "phase-001/STATE.md",
                    "phase-001/NEXT_STEPS.md", "phase-001/REVIEW.md", "phase-001/SUMMARY.md")},
}


def git(cwd, *args, env=None) -> str:
    result = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, env=env or GIT_ENV)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def write_tree(root: Path, files: dict[str, str]) -> None:
    for path, content in files.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def checkout(tmp_path, name: str, files: dict[str, str], *, date: str = "2026-10-01T10:00:00+00:00") -> Path:
    root = tmp_path / name
    root.mkdir()
    write_tree(root, files)
    git(root, "init", "-q", "-b", "main")
    git(root, "add", "-A")
    env = {**GIT_ENV, "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
    git(root, "commit", "-q", "-m", "synthetic baseline", env=env)
    return root


def reference_project(tmp_path, name="reference_project", **kwargs) -> Path:
    root = checkout(tmp_path, name, REFERENCE_PROJECT, **kwargs)
    # Ignorado por Git: los secretos locales y los runs no entran en el árbol leído.
    write_tree(root, {".env": "SYNTHETIC_SECRET=never-read\n",
                      ".harness/runs/20261001_P001-T001/task.json": '{"task_id": "P001-T001"}\n',
                      ".harness/runs/20261002_P001-CLOSE/phase-review.json": '{"phase_id": "P001"}\n'})
    return root


def context(root: Path) -> ProjectContext:
    profile = ProjectProfile("synthetic", validations=(Command(("test-runner", "check")),),
                             allowed_command_prefixes=(("test-runner",),))
    return ProjectContext(root, profile, EnginePolicy(("synthetic-executor",), ("medium",), "synthetic-planner",
                                                      "medium", "synthetic-reviewer", "high"), documents="v2")


def classes(inventory) -> dict:
    return {item["path"]: (item["class"], item["rule"], item["canonical"]) for item in inventory["entries"]}


def snapshot(root: Path) -> dict:
    """Todo el árbol, incluido `.git`, por contenido y tiempos: cualquier escritura lo cambia."""
    found = {}
    for current, directories, files in os.walk(root):
        for name in [*directories, *files]:
            path = Path(current) / name
            info = path.lstat()
            digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
            found[path.relative_to(root).as_posix()] = (info.st_mode, info.st_size, info.st_mtime_ns, digest)
    return found


def test_reference_project_inventory(tmp_path):
    inventory = read_inventory(context(reference_project(tmp_path)))
    assert inventory["format"] == INVENTORY_FORMAT
    assert classes(inventory) == REFERENCE_PROJECT_CLASSES
    assert inventory["origin"] == {"kind": "reference_project", "signals": {
        "reference_project": [".harness/.gitignore", ".harness/README.md", ".harness/config.yaml", ".harness/harness.py",
                       ".harness/runs", "docs/PROJECT.md", "docs/REQUIREMENTS.md", "docs/archive/phase-001"],
        "v1": [], "v2": []}}
    assert inventory["counts"] == {"canonical": 7, "renameable": 1, "mergeable": 4, "historical": 3, "foreign": 4}
    phases = inventory["phases"]
    assert phases["roadmap"] == {"path": "docs/ROADMAP.md", "detected": {
        "phases": [{"code": "P001", "title": "Foundation"}, {"code": "P002", "title": "Members"}],
        "duplicates": []}}
    assert phases["state"] == {"path": "docs/STATE.md", "detected": [{"code": "P002", "source": "frontmatter"}]}
    assert phases["next_steps"] == {"path": "docs/NEXT_STEPS.md", "detected": {
        "title_code": None, "tasks": 2, "task_phases": ["P002"]}}
    assert phases["archive"] == [{"path": "docs/archive/phase-001", "files": ["NEXT_STEPS.md", "REVIEW.md",
                                                                               "SUMMARY.md"],
                                  "code": "P001", "has_state": False}]
    assert inventory["instructions"] == {
        "AGENTS.md": {"path": "AGENTS.md", "bytes": len(REFERENCE_PROJECT["AGENTS.md"].encode()), "lines": 72, "limit": 60,
                      "within_limit": False},
        "CLAUDE.md": {"path": "CLAUDE.md", "bytes": len(REFERENCE_PROJECT["CLAUDE.md"].encode()), "lines": 20, "limit": 15,
                      "within_limit": False},
        "GEMINI.md": None}
    assert inventory["legacy_runs"] == {"present": True, "kind": "dir", "directories": 2, "managed_marker": False}
    assert inventory["managed_blocks"] == [] and inventory["blockers"] == []
    # Solo lo versionado en HEAD y dentro del ámbito documental; ni código, ni `.env`, ni runs.
    paths = {item["path"] for item in inventory["entries"]}
    assert not {"pyproject.toml", "src/app.py", ".gitignore", ".env"} & paths
    assert not any(path.startswith(".harness/runs") for path in paths)
    entry = next(item for item in inventory["entries"] if item["path"] == "docs/DECISSONS.md")
    assert entry["sha256"] == hashlib.sha256(REFERENCE_PROJECT["docs/DECISSONS.md"].encode()).hexdigest()
    assert inventory["inventory_sha256"] == fingerprint(inventory)


def test_v1_inventory(tmp_path):
    inventory = read_inventory(context(checkout(tmp_path, "v1", V1)))
    assert classes(inventory) == V1_CLASSES
    assert inventory["origin"]["kind"] == "v1"
    assert inventory["origin"]["signals"]["v1"] == ["docs/BRIEF.md", "docs/PROJECT_PROFILE.md",
                                                    "docs/DELIVERY_CHECKLIST.md"]
    assert inventory["phases"]["roadmap"] is None and inventory["phases"]["archive"] == []
    assert inventory["phases"]["next_steps"]["detected"]["task_phases"] == ["P001"]
    assert inventory["phases"]["state"]["detected"] == []
    assert inventory["instructions"] == {"AGENTS.md": None, "CLAUDE.md": None, "GEMINI.md": None}
    assert inventory["legacy_runs"] == {"present": False, "kind": None, "directories": 0, "managed_marker": False}


def test_v2_inventory(tmp_path):
    inventory = read_inventory(context(checkout(tmp_path, "v2", V2)))
    assert classes(inventory) == V2_CLASSES
    # phase-000 no tiene STATE por diseño y no cuenta como señal de ReferenceProject.
    assert inventory["origin"] == {"kind": "v2", "signals": {
        "reference_project": [], "v1": [], "v2": ["docs/decisions", "docs/architecture", "docs/research"]}}
    assert inventory["managed_blocks"] == [{"path": "docs/DECISIONS.md", "blocks": ["decisions"]},
                                           {"path": "docs/STATE.md", "blocks": ["state"]}]
    phases = inventory["phases"]
    assert [phase["code"] for phase in phases["roadmap"]["detected"]["phases"]] == ["P001", "P002"]
    assert phases["state"]["detected"] == [{"code": "P002", "source": "heading"}]
    assert phases["next_steps"]["detected"] == {"title_code": "P002", "tasks": 1, "task_phases": ["P002"]}
    assert [(folder["code"], folder["has_state"]) for folder in phases["archive"]] == [("P000", False),
                                                                                      ("P001", True)]
    assert inventory["instructions"]["CLAUDE.md"]["within_limit"] is True


@pytest.mark.parametrize("build", [reference_project, lambda tmp, **kw: checkout(tmp, "v1", V1, **kw),
                                   lambda tmp, **kw: checkout(tmp, "v2", V2, **kw)],
                         ids=["reference_project", "v1", "v2"])
def test_reread_is_identical_and_writes_nothing(tmp_path, build):
    root = build(tmp_path)
    before = snapshot(root)
    first, second = read_inventory(context(root)), read_inventory(context(root))
    assert first == second
    assert snapshot(root) == before
    assert git(root, "status", "--porcelain", "--untracked-files=all") == ""


def test_fingerprint_ignores_root_and_commit_identity(tmp_path):
    one = read_inventory(context(reference_project(tmp_path, "one", date="2026-10-01T10:00:00+00:00")))
    two = read_inventory(context(reference_project(tmp_path, "two", date="2026-10-05T18:30:00+00:00")))
    assert one["head"] != two["head"] and one["root"] != two["root"]
    assert one["tree"] == two["tree"] and one["inventory_sha256"] == two["inventory_sha256"]
    (tmp_path / "two/.harness/runs/20261003_P002-T001").mkdir()
    three = read_inventory(context(tmp_path / "two"))
    assert three["legacy_runs"]["directories"] == 3 and three["inventory_sha256"] != one["inventory_sha256"]


def test_only_read_only_git_commands_run(tmp_path, monkeypatch):
    root = reference_project(tmp_path)
    calls = []
    original = subprocess.run

    def recording(argv, *args, **kwargs):
        calls.append(list(argv))
        return original(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", recording)
    read_inventory(context(root))
    assert calls and all(Path(argv[0]).name == "git" for argv in calls)
    commands = [next(arg for arg in argv[1:] if not arg.startswith("-") and "=" not in arg) for argv in calls]
    assert set(commands) <= {"rev-parse", "status", "ls-tree", "cat-file"}
    assert all("core.hooksPath=/dev/null" in argv and "core.fsmonitor=false" in argv for argv in calls)


def test_refusals(tmp_path):
    plain = tmp_path / "plain"
    plain.mkdir()
    (plain / "README.md").write_text("# Plain\n", encoding="utf-8")
    with pytest.raises(ImportInventoryError, match="Not a Git checkout"):
        read_inventory(context(plain))
    git(plain, "init", "-q")
    with pytest.raises(ImportInventoryError, match="no commits"):
        read_inventory(context(plain))
    empty = tmp_path / "empty"
    empty.mkdir()
    git(empty, "init", "-q")
    git(empty, "commit", "-q", "--allow-empty", "-m", "empty")
    with pytest.raises(ImportInventoryError, match="HEAD has no files"):
        read_inventory(context(empty))
    root = checkout(tmp_path, "v1", V1)
    (root / "docs/STATE.md").write_text("# Changed\n", encoding="utf-8")
    with pytest.raises(ImportInventoryError, match="uncommitted changes.*docs/STATE.md"):
        read_inventory(context(root))
    git(root, "checkout", "-q", "--", "docs/STATE.md")
    (root / "notes.txt").write_text("untracked\n", encoding="utf-8")
    with pytest.raises(ImportInventoryError, match="uncommitted changes.*notes.txt"):
        read_inventory(context(root))
    (root / "notes.txt").unlink()
    with pytest.raises(ImportInventoryError, match="top level"):
        read_inventory(context(root / "docs"))


def test_symlinks_are_rejected_entries_and_never_followed(tmp_path):
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside secret\n", encoding="utf-8")
    root = tmp_path / "linked"
    root.mkdir()
    write_tree(root, V1)
    (root / "docs/LINKED.md").symlink_to(outside)
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "baseline")
    inventory = read_inventory(context(root))
    entry = next(item for item in inventory["entries"] if item["path"] == "docs/LINKED.md")
    assert entry["kind"] == "symlink" and entry["status"] == "rejected" and entry["sha256"] is None
    assert inventory["blockers"] == [{"code": "symlink_entry", "path": "docs/LINKED.md",
                                      "diagnostic": "Symbolic link: not followed or read."}]


def test_symlinked_legacy_runs_are_not_followed(tmp_path):
    root = checkout(tmp_path, "v1", {**V1, ".gitignore": ".harness/\n"})
    (tmp_path / "elsewhere/run").mkdir(parents=True)
    (root / ".harness").mkdir()
    (root / ".harness/runs").symlink_to(tmp_path / "elsewhere")
    runs = read_inventory(context(root))["legacy_runs"]
    assert runs == {"present": True, "kind": "symlink", "directories": 0, "managed_marker": False}


def test_alias_and_archive_conflicts_never_target_an_existing_path():
    found = classify(["docs/DECISIONS.md", "docs/DECISSONS.md", "docs/adr-001.md", "ROADMAP.md", "readme.md",
                      "docs/Specification.md", "docs/specification.md", "docs/archive/phase-1/SUMMARY.md",
                      "docs/archive/phase-001/SUMMARY.md", "docs/archive/phase-2/SUMMARY.md",
                      "docs/archive/phase-3/SUMMARY.md", "docs/archive/phase-03/SUMMARY.md",
                      "docs/archive/notes.md", "docs/flows/checkout.md", "docs/flows/img/a.png",
                      "docs/phase/spike.json", "docs/diagram.png", "CHANGELOG.md"], "docs")
    assert found["docs/DECISSONS.md"] == ("mergeable", "alias-conflict", "docs/DECISIONS.md")
    assert found["docs/adr-001.md"] == ("mergeable", "alias-conflict", "docs/DECISIONS.md")
    assert found["ROADMAP.md"] == ("renameable", "alias-root-document", "docs/ROADMAP.md")
    assert found["readme.md"] == ("renameable", "alias-case", "README.md")
    assert found["docs/Specification.md"] == ("mergeable", "alias-conflict", "docs/SPECIFICATION.md")
    assert found["docs/specification.md"] == ("mergeable", "alias-conflict", "docs/SPECIFICATION.md")
    assert found["docs/archive/phase-1/SUMMARY.md"] == ("historical", "archive-phase-conflict", None)
    assert found["docs/archive/phase-2/SUMMARY.md"] == ("historical", "archive-phase-renumber",
                                                        "docs/archive/phase-002/SUMMARY.md")
    assert found["docs/archive/phase-3/SUMMARY.md"] == ("historical", "archive-phase-conflict", None)
    assert found["docs/archive/phase-03/SUMMARY.md"] == ("historical", "archive-phase-conflict", None)
    assert found["docs/archive/notes.md"] == ("historical", "archive-other", None)
    assert found["docs/flows/checkout.md"] == ("canonical", "flow", "docs/flows/checkout.md")
    assert found["docs/flows/img/a.png"] == ("foreign", "flows-other", None)
    assert found["docs/phase/spike.json"] == ("canonical", "phase-work", "docs/phase/spike.json")
    assert found["docs/diagram.png"] == ("foreign", "docs-other", None)
    assert found["CHANGELOG.md"] == ("foreign", "root-markdown", None)
    assert classify(["docs/ADR.md"], "docs")["docs/ADR.md"] == ("renameable", "alias-adr", "docs/DECISIONS.md")
    nested = classify(["web/docs/archive/phase-1/A.md", "web/docs/archive/phase-001/B.md",
                       "web/docs/archive/phase-0002/C.md"], "web/docs")
    assert nested["web/docs/archive/phase-1/A.md"] == ("historical", "archive-phase-conflict", None)
    assert nested["web/docs/archive/phase-0002/C.md"] == ("historical", "archive-other", None)


def snapshot_of(files: dict[str, str]) -> CheckoutSnapshot:
    entries = tuple(TreeEntry(path, "100644", len(text.encode()), text.encode()) for path, text in files.items())
    return CheckoutSnapshot("/synthetic", "0" * 40, "1" * 40, entries,
                            {"present": False, "kind": None, "directories": 0, "managed_marker": False})


def test_origin_unified_unknown_and_mixed():
    target = Layout("docs", "docs/STATE.md", "docs/NEXT_STEPS.md")
    unified = build_inventory(snapshot_of(skeleton(target, "Synthetic")))
    assert unified["origin"]["kind"] == "unified" and unified["counts"]["canonical"] == 11
    assert all(value["within_limit"] for value in unified["instructions"].values())
    assert build_inventory(snapshot_of({"README.md": "# Plain\n"}))["origin"]["kind"] == "unknown"
    mixed = build_inventory(snapshot_of({"docs/BRIEF.md": "# Brief\n", "docs/research/a.md": "# A\n"}))
    assert mixed["origin"]["kind"] == "mixed"


def test_unreadable_markdown_and_invalid_blocks_are_diagnosed():
    inventory = build_inventory(CheckoutSnapshot("/synthetic", "0" * 40, "1" * 40, (
        TreeEntry("docs/STATE.md", "100644", 3, b"\xff\xfe\n"),
        TreeEntry("docs/ROADMAP.md", "100644", 60, b"<!-- harness-local:managed-roadmap:start -->\nx\n"),
    ), {"present": False, "kind": None, "directories": 0, "managed_marker": False}))
    entries = {item["path"]: item for item in inventory["entries"]}
    assert entries["docs/STATE.md"]["diagnostic"] == "Markdown is not UTF-8; not analysed."
    assert entries["docs/ROADMAP.md"]["diagnostic"].startswith("Invalid managed blocks")
    assert inventory["phases"]["state"] is None and inventory["blockers"] == []

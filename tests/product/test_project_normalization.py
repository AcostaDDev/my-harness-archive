"""P008-T010: mapa de normalización determinista del Flujo A sobre los orígenes sintéticos de T009.

Se fija el mapa completo de cada origen, que cada movimiento conserva los bytes y cita su regla, que ningún destino
coincide con una ruta existente u otro destino (tampoco en mayúsculas) y que lo ambiguo queda para el revisor.
"""

import hashlib

import pytest

from harness_local.adapters.project_import import read_checkout
from harness_local.core.engine.documents import decision_index
from harness_local.core.project_import import CheckoutSnapshot, TreeEntry, build_inventory
from harness_local.core.project_normalization import (
    DECISIONS_BASE, MAP_FORMAT, ImportMapError, build_map, map_fingerprint, materialize, snapshot_contents,
)
from test_project_import import REFERENCE_PROJECT, V1, V2, reference_project, checkout, snapshot

NO_RUNS = {"present": False, "kind": None, "directories": 0, "managed_marker": False}


def from_checkout(root):
    observed = read_checkout(root)
    contents = snapshot_contents(observed)
    return build_map(build_inventory(observed), contents), contents


def from_files(files: dict[str, str | bytes]):
    raw = {path: text.encode() if isinstance(text, str) else text for path, text in files.items()}
    observed = CheckoutSnapshot("/synthetic", "0" * 40, "1" * 40,
                                tuple(TreeEntry(path, "100644", len(data), data) for path, data in raw.items()),
                                NO_RUNS)
    return build_map(build_inventory(observed), raw), raw


def moves(result) -> dict:
    return {move["source"]: (move["rule"], move["target"]) for move in result["moves"]}


def reviews(result) -> dict:
    return {item["path"]: item["reason"] for item in result["review"]}


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def assert_invariants(result, contents):
    """Bytes conservados, reglas citadas y destinos libres en el árbol original."""
    original = {path.lower() for path in contents}
    output = materialize(result, contents)
    targets = [move["target"].lower() for move in result["moves"]]
    assert len(targets) == len(set(targets))
    composed = result["compose"]["target"] if result["compose"] else None
    for move in result["moves"]:
        assert move["rule"]
        if move["target"] == composed:  # el alias es la base intacta de la composición
            assert output[composed].startswith(contents[move["source"]])
        else:
            assert output[move["target"]] == contents[move["source"]]
        assert move["sha256"] == hashlib.sha256(contents[move["source"]]).hexdigest()
        assert move["target"].lower() not in original or move["target"].lower() == move["source"].lower()
    paths = [node["path"] for node in result["tree"]]
    assert len(paths) == len(set(paths)) and set(output) == set(paths)
    assert result["map_sha256"] == map_fingerprint(result)


def test_reference_project_map(tmp_path):
    result, contents = from_checkout(reference_project(tmp_path))
    assert result["format"] == MAP_FORMAT and result["active_phase"] == "P002"
    assert moves(result) == {"docs/DECISSONS.md": ("rename-alias", "docs/DECISIONS.md")}
    assert result["compose"] is None
    assert reviews(result) == {"docs/HARNESS_COMMANDS.md": "merge-proposal", "docs/PROJECT.md": "merge-proposal",
                               "docs/REQUIREMENTS.md": "merge-proposal", "docs/UI_REDESIGN.md": "merge-proposal"}
    assert [item["path"] for item in result["foreign"]] == [".harness/.gitignore", ".harness/README.md",
                                                            ".harness/config.yaml", ".harness/harness.py"]
    assert result["kept"] == ["AGENTS.md", "CLAUDE.md", "README.md", "docs/ARCHITECTURE.md", "docs/NEXT_STEPS.md",
                              "docs/ROADMAP.md", "docs/STATE.md", "docs/archive/phase-001/NEXT_STEPS.md",
                              "docs/archive/phase-001/REVIEW.md", "docs/archive/phase-001/SUMMARY.md"]
    assert result["missing"] == ["GEMINI.md", "docs/SPECIFICATION.md", "docs/DDBB-DIAGRAM.md"]
    output = materialize(result, contents)
    assert output["docs/DECISIONS.md"] == REFERENCE_PROJECT["docs/DECISSONS.md"].encode()
    assert "docs/DECISSONS.md" not in output
    assert_invariants(result, contents)


def test_v1_map(tmp_path):
    result, contents = from_checkout(checkout(tmp_path, "v1", V1))
    assert result["active_phase"] == "P001"
    assert moves(result) == {
        "docs/BRIEF.md": ("retire-v1-foundation", "docs/archive/phase-000/BRIEF.md"),
        "docs/PROJECT_PROFILE.md": ("retire-v1-foundation", "docs/archive/phase-000/PROJECT_PROFILE.md")}
    assert reviews(result) == {"docs/DELIVERY_CHECKLIST.md": "merge-proposal"}
    assert result["missing"] == ["AGENTS.md", "CLAUDE.md", "GEMINI.md", "docs/SPECIFICATION.md",
                                 "docs/ARCHITECTURE.md", "docs/ROADMAP.md", "docs/DDBB-DIAGRAM.md"]
    assert_invariants(result, contents)


def test_v2_map_composes_decisions_and_retires_folders(tmp_path):
    result, contents = from_checkout(checkout(tmp_path, "v2", V2))
    assert moves(result) == {
        "docs/architecture/README.md": ("retire-v2-readme", "docs/archive/phase-000/architecture/README.md"),
        "docs/architecture/data-model.md": ("rename-data-model", "docs/DDBB-DIAGRAM.md"),
        "docs/decisions/D001-stack.md": ("archive-decision", "docs/archive/phase-000/decisions/D001-stack.md"),
        "docs/decisions/README.md": ("retire-v2-readme", "docs/archive/phase-000/decisions/README.md"),
        "docs/research/README.md": ("retire-v2-readme", "docs/archive/phase-000/research/README.md")}
    assert reviews(result) == {"docs/architecture/checkout.md": "merge-proposal",
                               "docs/research/spike.md": "phase-unknown"}
    compose = result["compose"]
    assert compose["rule"] == "decision-sections" and compose["base"] == "docs/DECISIONS.md"
    assert compose["sections"] == [{"source": "docs/decisions/D001-stack.md", "decision": "D001",
                                    "sha256": sha(V2["docs/decisions/D001-stack.md"])}]
    composed = materialize(result, contents)["docs/DECISIONS.md"].decode()
    # La base queda intacta delante y la sección es el archivo con su título un nivel por debajo.
    assert composed == V2["docs/DECISIONS.md"] + "\n#" + V2["docs/decisions/D001-stack.md"]
    assert decision_index(composed) == [{"id": "D001", "title": "Stack", "status": "aceptada"}]
    assert result["missing"] == ["AGENTS.md", "GEMINI.md"]
    assert_invariants(result, contents)


@pytest.mark.parametrize("build", [reference_project, lambda tmp, **kw: checkout(tmp, "v1", V1, **kw),
                                   lambda tmp, **kw: checkout(tmp, "v2", V2, **kw)],
                         ids=["reference_project", "v1", "v2"])
def test_map_is_deterministic_and_writes_nothing(tmp_path, build):
    (tmp_path / "one").mkdir()
    (tmp_path / "two").mkdir()
    one, two = build(tmp_path / "one"), build(tmp_path / "two")
    before = snapshot(one)
    first, second = from_checkout(one)[0], from_checkout(one)[0]
    assert first == second and from_checkout(two)[0] == first
    assert snapshot(one) == before


def test_targets_never_overwrite_or_collide():
    result, contents = from_files({
        "docs/STATE.md": "# State\n", "docs/archive/phase-000/BRIEF.md": "# Archived brief\n",
        "docs/BRIEF.md": "# Brief\n", "docs/architecture/data-model.md": "# Model\n",
        "docs/ddbb-diagram.md": "# Lower-case diagram\n", "docs/roadmap.md": "# Roadmap\n",
        "docs/archive/phase-2/SUMMARY.md": "# P002\n", "docs/archive/phase-002": "a file, not a folder\n",
    })
    assert reviews(result) == {
        "docs/BRIEF.md": "target-conflict", "docs/architecture/data-model.md": "alias-conflict",
        "docs/ddbb-diagram.md": "alias-conflict", "docs/archive/phase-2/SUMMARY.md": "target-conflict",
        "docs/archive/phase-002": "archive-unrecognised"}
    assert moves(result) == {"docs/roadmap.md": ("rename-alias", "docs/ROADMAP.md")}
    assert materialize(result, contents)["docs/archive/phase-000/BRIEF.md"] == b"# Archived brief\n"
    assert_invariants(result, contents)


def test_case_only_rename_and_root_alias():
    result, contents = from_files({"Readme.md": "# Readme\n", "STATE.md": "# State\n", "docs/next_steps.md": "x\n"})
    assert moves(result) == {"Readme.md": ("rename-alias", "README.md"),
                             "STATE.md": ("rename-alias", "docs/STATE.md"),
                             "docs/next_steps.md": ("rename-alias", "docs/NEXT_STEPS.md")}
    assert_invariants(result, contents)


def test_phase_artifacts_follow_their_phase():
    result, contents = from_files({
        "docs/STATE.md": "# State\n\n## Fase activa — P003 Billing\n",
        "docs/NEXT_STEPS.md": "# P003 — Billing\n\n## P003-T001 — Invoices\n\nDo it.\n",
        "docs/archive/phase-001/SUMMARY.md": "# P001\n", "docs/archive/phase-2/SUMMARY.md": "# P002\n",
        "docs/research/P001-benchmark.md": "# Bench\n", "docs/research/P002/notes.md": "# Notes\n",
        "docs/research/P003-spike.json": "{}\n", "docs/research/P004-later.md": "# Later\n",
        "docs/research/P001-vs-P002.md": "# Both\n", "docs/research/P001/STATE.md": "# Not a state\n",
        "docs/research/notes.md": "# No phase\n",
        "docs/P003-T001_EVIDENCE.md": "# Evidence\n", "docs/P001_LOG.json": "[]\n", "docs/PROJECT.md": "# P\n",
    })
    assert result["active_phase"] == "P003"
    assert moves(result) == {
        "docs/archive/phase-2/SUMMARY.md": ("archive-renumber", "docs/archive/phase-002/SUMMARY.md"),
        "docs/research/P001-benchmark.md": ("phase-artifact-archived", "docs/archive/phase-001/P001-benchmark.md"),
        "docs/research/P002/notes.md": ("phase-artifact-archived", "docs/archive/phase-002/P002/notes.md"),
        "docs/research/P001/STATE.md": ("phase-artifact-archived", "docs/archive/phase-001/P001/STATE.md"),
        "docs/research/P003-spike.json": ("phase-artifact-active", "docs/phase/P003-spike.json"),
        "docs/P003-T001_EVIDENCE.md": ("phase-artifact-active", "docs/phase/P003-T001_EVIDENCE.md"),
        "docs/P001_LOG.json": ("phase-artifact-archived", "docs/archive/phase-001/P001_LOG.json")}
    assert reviews(result) == {"docs/research/P004-later.md": "phase-unknown",
                               "docs/research/P001-vs-P002.md": "phase-unknown",
                               "docs/research/notes.md": "phase-unknown",
                               "docs/PROJECT.md": "merge-proposal"}
    assert_invariants(result, contents)


def test_disagreeing_phase_sources_leave_artifacts_for_review():
    result, _ = from_files({"docs/STATE.md": "# State\n\n## Fase activa — P002 A\n",
                            "docs/NEXT_STEPS.md": "# P003 — B\n", "docs/research/P002-a.md": "# A\n"})
    assert result["active_phase"] is None
    assert reviews(result) == {"docs/research/P002-a.md": "phase-unknown"}


def test_decisions_compose_in_numeric_order_and_reject_ambiguity():
    fenced = "# D004 — Fenced\n\nEstado: aceptada\n\n```md\n## not a heading\n```\n"
    result, contents = from_files({
        "docs/DECISSONS.md": "# Decisions\n\n## D001 — Kept\n\nEstado: aceptada\n",
        "docs/decisions/D010-late.md": "# D010 — Late\n\nEstado: propuesta",
        "docs/decisions/D002-early.md": "# D002 — Early\n\n**Estado:** aceptada\n",
        "docs/decisions/D004-fenced.md": fenced,
        "docs/decisions/D001-clash.md": "# D001 — Clash\n",
        "docs/decisions/D003-a.md": "# D003 — A\n", "docs/decisions/D0003-b.md": "# D0003 — B\n",
        "docs/decisions/D005-wrong.md": "# D006 — Wrong number\n",
        "docs/decisions/D007-nested.md": "# D007 — Nested\n\n## Context\n",
        "docs/decisions/D008-marker.md": "# D008 — Marker\n\n<!-- harness-local:managed-state:start -->\n",
        "docs/decisions/D009-latin1.md": b"# D009 \xe9\n",
    })
    compose = result["compose"]
    assert compose["base"] == "docs/DECISSONS.md"
    assert [section["decision"] for section in compose["sections"]] == ["D002", "D004", "D010"]
    assert reviews(result) == {
        "docs/decisions/D001-clash.md": "decision-duplicate", "docs/decisions/D003-a.md": "decision-duplicate",
        "docs/decisions/D0003-b.md": "decision-duplicate", "docs/decisions/D005-wrong.md": "decision-unparsed",
        "docs/decisions/D007-nested.md": "decision-unparsed", "docs/decisions/D008-marker.md": "decision-unparsed",
        "docs/decisions/D009-latin1.md": "decision-unparsed"}
    archived = {source for source, (rule, _) in moves(result).items() if rule == "archive-decision"}
    assert archived == {"docs/decisions/D002-early.md", "docs/decisions/D004-fenced.md",
                        "docs/decisions/D010-late.md"}
    composed = materialize(result, contents)["docs/DECISIONS.md"].decode()
    assert composed == ("# Decisions\n\n## D001 — Kept\n\nEstado: aceptada\n\n## D002 — Early\n\n**Estado:** aceptada\n"
                        "\n#" + fenced + "\n## D010 — Late\n\nEstado: propuesta\n")
    assert [entry["id"] for entry in decision_index(composed)] == ["D001", "D002", "D004", "D010"]
    assert_invariants(result, contents)


def test_decisions_without_base_use_template_or_wait_for_the_reviewer():
    result, contents = from_files({"docs/decisions/D001-a.md": "# D001 — A\n"})
    assert result["compose"]["base"] is None
    assert materialize(result, contents)["docs/DECISIONS.md"].decode() == DECISIONS_BASE + "\n## D001 — A\n"
    pending, _ = from_files({"docs/decisions/D001-a.md": "# D001 — A\n", "docs/Decisions.md": "# One\n",
                             "docs/decisions.md": "# Two\n"})
    assert pending["compose"] is None and "docs/decisions/D001-a.md" not in moves(pending)
    assert reviews(pending)["docs/decisions/D001-a.md"] == "decision-base"
    broken, _ = from_files({"docs/decisions/D001-a.md": "# D001 — A\n",
                            "docs/DECISIONS.md": "## D002 — X\n\n## D0002 — Y\n"})
    assert broken["compose"] is None and reviews(broken)["docs/decisions/D001-a.md"] == "decision-base"


def test_blocked_entries_stay_put_and_contents_must_match():
    observed = CheckoutSnapshot("/synthetic", "0" * 40, "1" * 40, (
        TreeEntry("docs/BRIEF.md", "120000", 9, None, "Symbolic link: not followed or read."),
        TreeEntry("docs/STATE.md", "100644", 8, b"# State\n")), NO_RUNS)
    inventory = build_inventory(observed)
    result = build_map(inventory, snapshot_contents(observed))
    assert result["moves"] == [] and result["blockers"][0]["path"] == "docs/BRIEF.md"
    assert materialize(result, snapshot_contents(observed)) == {"docs/STATE.md": b"# State\n"}
    with pytest.raises(ImportMapError, match="differs from the inventory"):
        build_map(inventory, {"docs/STATE.md": b"# Changed\n"})
    with pytest.raises(ImportMapError, match="fingerprint"):
        build_map({**inventory, "docs": "elsewhere"}, snapshot_contents(observed))
    with pytest.raises(ImportMapError, match="differs from the map"):
        materialize(result, {"docs/STATE.md": b"# Changed\n"})

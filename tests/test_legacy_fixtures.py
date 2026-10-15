"""Checks pequeños de datos H0.1; solo lectura local y biblioteca estándar."""

import hashlib
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/legacy"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class LegacyFixturesTests(unittest.TestCase):
    def setUp(self):
        self.manifest = read_json(FIXTURES / "manifest.json")

    def run_path(self, case, index=0):
        return FIXTURES / self.manifest["cases"][case]["runs"][index]

    def test_manifest_parse_and_contract_fields(self):
        self.assertTrue(self.manifest["synthetic"])
        declared = set()
        for entry in self.manifest["artifacts"]:
            with self.subTest(path=entry["path"]):
                path = FIXTURES / entry["path"]
                self.assertNotIn(entry["path"], declared)
                declared.add(entry["path"])
                self.assertTrue(path.resolve().is_relative_to(FIXTURES.resolve()))
                self.assertFalse(path.is_symlink())
                text = path.read_text(encoding="utf-8")
                if entry["format"] == "partial_json":
                    with self.assertRaises(json.JSONDecodeError):
                        json.loads(text)
                    continue
                if entry["format"] == "jsonl":
                    self.assertTrue(text.endswith("\n"))
                    for line in text.splitlines():
                        self.assertIsInstance(json.loads(line), dict)
                    continue
                if entry["format"] == "text":
                    continue
                self.assertEqual(entry["format"], "json")
                data = json.loads(text)
                self.assertIsInstance(data, dict)
                absent = set(entry.get("absent_fields", []))
                self.assertFalse(absent & data.keys())
                for field in entry.get("null_fields", []):
                    self.assertIn(field, data)
                    self.assertIsNone(data[field])
                if "schema" in entry:
                    schema = read_json(FIXTURES / f"schemas/{entry['schema']}.schema.json")
                    self.assertEqual(set(schema["required"]) - data.keys(), absent)
                    extras = {"contract_source"} if entry["schema"] == "task" else set()
                    self.assertFalse(data.keys() - schema["properties"].keys() - extras)
                    for key, spec in schema["properties"].items():
                        if key in data and "enum" in spec:
                            self.assertIn(data[key], spec["enum"])
                        if key in data and "pattern" in spec:
                            self.assertRegex(data[key], spec["pattern"])
        actual = {p.relative_to(FIXTURES).as_posix()
                  for case in self.manifest["cases"]
                  for p in (FIXTURES / case).rglob("*") if p.is_file()}
        self.assertEqual(declared, actual)
        for case in self.manifest["cases"].values():
            for missing in case["absent_files"]:
                self.assertFalse((FIXTURES / missing).exists(), missing)

    def test_identity_iterations_and_references(self):
        for case in self.manifest["cases"].values():
            for name in case["runs"]:
                run = FIXTURES / name
                checkout = FIXTURES / name.split("/", 1)[0]
                task = read_json(run / "task.json") if (run / "task.json").exists() else None
                if task:
                    self.assertTrue(run.name.endswith("_" + task["task_id"]))
                    self.assertTrue(task["task_id"].startswith(task["phase_id"] + "-"))
                for path in run.glob("validation-*.json"):
                    report = read_json(path)
                    self.assertEqual(report["iteration"], int(path.stem.split("-")[1]))
                    self.assertEqual(report["all_passed"], all(c["passed"] for c in report["commands"]))
                    for command in report["commands"]:
                        for key in ("stdout_file", "stderr_file"):
                            target = checkout / command[key]
                            self.assertTrue(target.resolve().is_relative_to(checkout.resolve()))
                            self.assertTrue(target.is_file(), target)
                for path in run.glob("review-*.json"):
                    if path == self.run_path("interrupted", 1) / "review-00.json":
                        continue  # única respuesta deliberadamente parcial
                    review = read_json(path)
                    self.assertEqual(review["task_id"], task["task_id"])
                    if review["verdict"] == "ACCEPT":
                        validation = read_json(run / path.name.replace("review", "validation"))
                        self.assertTrue(validation["all_passed"])
                        self.assertFalse(validation["policy"]["hard_failure"])
                        self.assertEqual(review["blocking_questions"], [])
                    if review["verdict"] == "REVISE":
                        self.assertTrue(review["next_prompt"])
                        self.assertTrue(review["executor_selection"]["reason"])
                for path in run.glob("claude-*.result.usage.json"):
                    usage = read_json(path)
                    result = read_json(path.with_name(path.name.replace(".usage.json", ".json")))
                    request = read_json(path.with_name(path.name.replace(".usage.json", ".request.json")))
                    self.assertEqual(usage["requested"], {k: request[k] for k in ("model", "effort", "reason")})
                    self.assertEqual(usage["actual_models"], list(result.get("modelUsage", {})))
                    self.assertEqual(usage["duration_ms"], result.get("duration_ms"))
                for path in run.glob("resume-*.json"):
                    resume = read_json(path)
                    self.assertEqual(resume["task_id"], task["task_id"])
                    self.assertTrue((checkout / resume["previous_review"]).is_file())

    def test_five_scenarios_and_missing_data(self):
        self.assertEqual(set(self.manifest["cases"]), {"accepted", "revise", "blocked", "interrupted", "closed-phase"})
        self.assertEqual(read_json(self.run_path("accepted") / "review-00.json")["verdict"], "ACCEPT")
        revise = self.run_path("revise")
        self.assertEqual([read_json(revise / f"review-{i:02d}.json")["verdict"] for i in (0, 1)], ["REVISE", "ACCEPT"])
        blocked = self.run_path("blocked")
        self.assertTrue(read_json(blocked / "review-00.json")["blocking_questions"])
        self.assertEqual(read_json(blocked / "stop-01.json")["stage"], "executor")
        self.assertTrue(read_json(blocked / "resume-01.json")["retry_executor"])
        self.assertNotIn("executor_selection", read_json(blocked / "task.json"))
        self.assertIsNone(read_json(blocked / "claude-00.result.usage.json")["duration_ms"])
        self.assertEqual(read_json(blocked / "claude-00.result.usage.json")["actual_models"], [])
        self.assertNotIn("duration_seconds", read_json(blocked / "validation-00.json")["commands"][0])
        events = (self.run_path("interrupted") / "claude-00.result.events.jsonl").read_text().splitlines()
        self.assertNotIn("result", [json.loads(line)["type"] for line in events])
        phase = read_json(self.run_path("closed-phase", -1) / "phase-review.json")
        meta = read_json(self.run_path("closed-phase", -1) / "phase-review.meta.json")
        self.assertEqual((phase["verdict"], meta["phase_id"]), ("READY", phase["phase_id"]))
        self.assertRegex(meta["head"], r"^[0-9a-f]{40}$")
        docs = FIXTURES / "closed-phase/docs"
        for filename, field in (("SUMMARY.md", "archive_summary_markdown"), ("REVIEW.md", "archive_review_markdown")):
            self.assertEqual((docs / "archive/phase-900" / filename).read_text(), phase[field] + "\n")
        self.assertEqual((docs / "NEXT_STEPS.md").read_text(), phase["next_steps_markdown"])
        state = (docs / "STATE.md").read_text()
        self.assertIn(f"phase: {int(phase['next_phase_id'][1:])}\n", state)
        self.assertIn("last_accepted_task: null\n", state)
        statuses = re.findall(r"\*\*Status:\*\* (\w+)", (docs / "ROADMAP.md").read_text())
        self.assertEqual(statuses, ["Completed", "Active"])

    def test_schema_snapshot_provenance(self):
        baseline = read_json(FIXTURES / "baseline.json")
        self.assertRegex(baseline["reference_commit"], r"^[0-9a-f]{40}$")
        indexed = {f["path"]: f for f in baseline["files"]}
        self.assertEqual(len(indexed), len(baseline["files"]))
        for path in (FIXTURES / "schemas").glob("*.json"):
            entry = indexed[f".harness/schemas/{path.name}"]
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest, entry["sha256"])
            self.assertEqual(digest, entry["head_sha256"])
            self.assertTrue(entry["matches_head"])


if __name__ == "__main__":
    unittest.main()

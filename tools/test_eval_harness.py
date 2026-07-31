from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path

import eval_harness as harness


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


class EvalHarnessTests(unittest.TestCase):
    def prepare(self, root: Path, suite: str = "pr") -> None:
        harness.prepare(argparse.Namespace(output=root, suite=suite, model="gpt-5.6-terra", reasoning="medium"))

    def test_prepare_counts_and_explicit_treatment_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root)
            manifest = harness.read_json(root / "manifest.json")
            self.assertEqual(16, len(manifest["runs"]))
            self.assertEqual(manifest["skill_snapshot_sha256"], harness.tree_digest(root / "inputs" / "genscaff"))
            for item in manifest["runs"]:
                prompt = (root / item["prompt"]).read_text(encoding="utf-8")
                self.assertEqual(item["condition"] == "treatment", "$genscaff" in prompt)

    def test_release_has_120_runs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root, "release")
            self.assertEqual(120, len(harness.read_json(root / "manifest.json")["runs"]))

    def test_only_treatment_workspace_receives_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root)
            manifest = harness.read_json(root / "manifest.json")
            for item in manifest["runs"][:2]:
                workspace = root / item["workspace"]
                harness.stage_workspace(root, item, workspace)
                installed = (workspace / ".agents" / "skills" / "genscaff" / "SKILL.md").is_file()
                self.assertEqual(item["condition"] == "treatment", installed)

    def test_blind_is_deterministic_and_does_not_leak(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root)
            args = argparse.Namespace(run_dir=root)
            harness.blind(args)
            first = (root / "blind" / "packets.json").read_text(encoding="utf-8")
            harness.blind(args)
            self.assertEqual(first, (root / "blind" / "packets.json").read_text(encoding="utf-8"))
            for forbidden in ("control", "treatment", str(root), "workspace", "prompt.txt"):
                self.assertNotIn(forbidden, first)
            self.assertEqual(1, harness.validate(args))

    def test_swapped_disagreement_requires_human_merge(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root)
            args = argparse.Namespace(run_dir=root)
            harness.blind(args)
            packet = harness.read_json(root / "blind" / "packets.json")["packets"][0]
            scores = {side: {dimension: 3 for dimension in harness.DIMENSIONS} for side in ("left", "right")}
            gates = {side: {gate: True for gate in harness.read_json(harness.RUBRIC)["hard_gates"]} for side in ("left", "right")}
            write(root / "judgments" / f"{packet['packet_id']}-forward.json", {"winner":"left", "scores":scores, "hard_gates":gates})
            write(root / "judgments" / f"{packet['packet_id']}-swapped.json", {"winner":"left", "scores":scores, "hard_gates":gates})
            harness.score(args)
            self.assertEqual(1, harness.validate(args))
            write(root / "judgments" / f"{packet['packet_id']}-human.json", {"winner":"right", "scores":scores, "hard_gates":gates})
            harness.score(args)
            result = harness.read_json(root / "summary.json")["results"][0]
            self.assertTrue(result["human_adjudicated"])
            private = harness.read_json(root / "private" / f"{packet['packet_id']}.json")
            self.assertEqual(private["right"], result["winner"])

    def test_complete_pr_suite_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root)
            for item in harness.read_json(root / "manifest.json")["runs"]:
                write(root / "runs" / item["run_id"] / "result.json", {"exit_code": 0})
            args = argparse.Namespace(run_dir=root)
            harness.blind(args)
            packets = harness.read_json(root / "blind" / "packets.json")["packets"]
            scores = {side: {dimension: 4 for dimension in harness.DIMENSIONS} for side in ("left", "right")}
            gates = {side: {gate: True for gate in harness.read_json(harness.RUBRIC)["hard_gates"]} for side in ("left", "right")}
            for packet in packets:
                judgment = {"winner": "tie", "scores": scores, "hard_gates": gates}
                write(root / "judgments" / f"{packet['packet_id']}-forward.json", judgment)
                write(root / "judgments" / f"{packet['packet_id']}-swapped.json", judgment)
                if packet["human_review_required"]:
                    write(root / "judgments" / f"{packet['packet_id']}-human.json", judgment)
            harness.score(args)
            self.assertEqual(0, harness.validate(args))


if __name__ == "__main__":
    unittest.main()

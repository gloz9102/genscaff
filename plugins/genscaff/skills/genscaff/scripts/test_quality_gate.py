from __future__ import annotations

import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

import quality_gate as gate


def png(path: Path, color: int) -> None:
    width, height = 8, 8
    raw = b"".join(b"\0" + bytes((color, 30, 60)) * width for _ in range(height))

    def chunk(kind: bytes, value: bytes) -> bytes:
        return struct.pack(">I", len(value)) + kind + value + struct.pack(">I", zlib.crc32(kind + value) & 0xffffffff)

    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def pass_dimension(method: str = "observed") -> dict:
    return {"result": "pass", "method": method, "coverage": "critical_path", "evidence": ["observed evidence"], "issues": [], "limitations": []}


class StandardTests(unittest.TestCase):
    def valid(self, root: Path, status: str = "VERIFIED_KEYBOARD_FLOW") -> dict:
        value = gate.template()
        value["completion_status"] = status
        value["classification"]["rationale"] = "The primary task is operational workflow management."
        value["contract"]["product"].update({
            "target_user": "operator",
            "primary_job": "resolve an incident",
            "primary_success_outcome": "incident is resolved",
            "primary_cta": "Resolve incident",
        })
        for name in ("render", "flow", "keyboard", "focus"):
            value["verification_dimensions"][name] = pass_dimension()
        value["interaction_cost"].update({"required_decisions": 1, "actions_to_primary_success": 2, "default_selection_rationale": "No safe target default."})
        value["execution_policy"]["active_browser"] = "approved"
        for i, viewport in enumerate(("desktop", "mobile")):
            width = 1440 if viewport == "desktop" else 390
            value["runtime_checks"][viewport].update({
                "inner_width": width,
                "scroll_width": width,
                "clipping_checked": True,
                "primary_action_verified": True,
                "feedback_verified": True,
                "terminal_result_verified": True,
                "keyboard_path_verified": True,
                "focus_visible_verified": True,
                "focus_not_obscured_verified": True,
            })
            for j, state in enumerate(("start", "terminal", "focus")):
                name = f"{viewport}-{state}.png"
                png(root / name, i * 10 + j + 1)
                value["evidence"][viewport][state] = {"artifact": name, "observation": f"observed {viewport} {state}"}
        return value

    def test_valid_keyboard_flow(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual([], gate.validate(self.valid(root), root / "report.json"))

    def test_standard_baseline_requires_state_and_accessibility_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = self.valid(root, "VERIFIED_STANDARD_BASELINE")
            errors = gate.validate(value, root / "report.json")
            self.assertIn("state_coverage must verify every relevant state", errors)
            self.assertIn("verification_dimensions.automated_accessibility must pass with automated evidence", errors)
            value["state_coverage"].update({"relevant_states": ["loading", "success"], "verified_states": ["loading", "success"], "evidence": ["state captures"]})
            value["verification_dimensions"]["automated_accessibility"] = pass_dimension("automated")
            self.assertEqual([], gate.validate(value, root / "report.json"))

    def test_evidence_free_pass_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = self.valid(root)
            value["verification_dimensions"]["focus"]["evidence"] = []
            self.assertIn("verification_dimensions.focus.evidence is required for pass", gate.validate(value, root / "report.json"))

    def test_boolean_only_focus_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = self.valid(root)
            value["verification_dimensions"]["focus"].update({"result": "partial", "method": "static"})
            self.assertIn("verification_dimensions.focus must pass through observed or manual evidence", gate.validate(value, root / "report.json"))

    def test_recovery_only_required_when_applicable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = self.valid(root, "VERIFIED_PRIMARY_FLOW")
            self.assertEqual([], gate.validate(value, root / "report.json"))
            value["runtime_checks"]["mobile"]["recovery_applicable"] = True
            self.assertIn("runtime_checks.mobile.recovery_verified must be true when recovery is applicable", gate.validate(value, root / "report.json"))

    def test_fabricated_friction_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = self.valid(root)
            value["interaction_cost"]["fabricated_friction"] = ["invented selection"]
            self.assertIn("FABRICATED_FRICTION: fabricated_friction must be empty", gate.validate(value, root / "report.json"))

    def test_async_boundary_requires_complete_loading_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = self.valid(root)
            value["loading_experience"] = {"applicable": True, "boundaries": []}
            self.assertIn("loading_experience.boundaries must describe every asynchronous boundary", gate.validate(value, root / "report.json"))

    def test_execution_approval_requires_explicit_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = self.valid(root)
            value["execution_policy"]["project_command_execution"] = "approved"
            self.assertIn("approved project commands require explicit_user_request", gate.validate(value, root / "report.json"))
            value["execution_policy"]["approval_source"] = "explicit_user_request"
            self.assertEqual([], gate.validate(value, root / "report.json"))

    def test_verified_status_requires_separate_browser_approval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = self.valid(root)
            value["execution_policy"]["active_browser"] = "not_approved"
            self.assertIn("verified browser status requires execution_policy.active_browser=approved", gate.validate(value, root / "report.json"))

    def test_malformed_dimension_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = self.valid(root)
            value["verification_dimensions"]["keyboard"] = "pass"
            self.assertIn("verification_dimensions.keyboard must be an object", gate.validate(value, root / "report.json"))

    def test_path_traversal_and_absolute_artifact_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = self.valid(root)
            value["evidence"]["desktop"]["focus"]["artifact"] = "../outside.png"
            self.assertTrue(any("in-root PNG" in error for error in gate.validate(value, root / "report.json")))
            value["evidence"]["desktop"]["focus"]["artifact"] = str((root / "desktop-focus.png").resolve())
            self.assertTrue(any("in-root PNG" in error for error in gate.validate(value, root / "report.json")))

    def test_legacy_v5_status_is_conservatively_migrated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            current = self.valid(root)
            legacy = {
                "schema_version": 5,
                "profile": "standard",
                "completion_status": "VERIFIED_STANDARD",
                "context": {"target_user": "operator", "primary_task": "resolve", "success_outcome": "resolved", "primary_cta": "Resolve", "recovery": "Retry"},
                "verification_dimensions": {name: ("observed" if name in {"render", "flow", "keyboard", "focus"} else "not_tested") for name in ("render", "flow", "keyboard", "focus", "automated_accessibility", "assistive_technology_user_validation")},
                "evidence": current["evidence"],
                "runtime_checks": current["runtime_checks"],
                "interaction_cost": current["interaction_cost"],
                "loading_experience": current["loading_experience"],
                "notes": [],
            }
            migrated, notice = gate.normalize(legacy)
            self.assertEqual("VERIFIED_KEYBOARD_FLOW", migrated["completion_status"])
            self.assertEqual("SCHEMA_V5_MIGRATED_CONSERVATIVELY", notice)
            self.assertEqual([], gate.validate(migrated, root / "report.json"))

    def test_future_schema_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = self.valid(root)
            value["schema_version"] = 999
            self.assertTrue(gate.validate(value, root / "report.json"))

    def test_schema_v2_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = self.valid(root)
            value["schema_version"] = 2
            self.assertEqual(["schema_version must be 6 or supported legacy version 5"], gate.validate(value, root / "report.json"))

    def test_clean_boolean_bundle_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = self.valid(root)
            value["checks"] = {"no_nested_card_soup": True, "slop_checklist_compared_visually": True}
            self.assertIn(
                "schema v6 must record findings in verification issues and limitations, not a clean boolean checks bundle",
                gate.validate(value, root / "report.json"),
            )

    def test_unverified_cli_prints_explicit_warning(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = gate.template()
            value["classification"]["rationale"] = "Existing workflow route."
            value["contract"]["product"].update({"target_user": "operator", "primary_job": "inspect", "primary_success_outcome": "understood", "primary_cta": "Read"})
            report = root / "report.json"
            report.write_text(json.dumps(value), encoding="utf-8")
            completed = subprocess.run([sys.executable, str(Path(gate.__file__)), "--report", str(report)], capture_output=True, text=True, check=False)
            self.assertEqual(0, completed.returncode)
            self.assertIn("STANDARD_BROWSER_EVIDENCE_UNVERIFIED", completed.stdout)


if __name__ == "__main__":
    unittest.main()

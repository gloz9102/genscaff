from __future__ import annotations

import json
import subprocess
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
import sys

import quality_gate as gate


def png(path: Path, color: int) -> None:
    width, height = 8, 8
    raw = b"".join(b"\0" + bytes((color, 30, 60)) * width for _ in range(height))
    def chunk(kind: bytes, value: bytes) -> bytes:
        return struct.pack(">I", len(value)) + kind + value + struct.pack(">I", zlib.crc32(kind + value) & 0xffffffff)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


class StandardTests(unittest.TestCase):
    def valid(self, root: Path) -> dict:
        value = gate.template()
        value["completion_status"] = "VERIFIED_STANDARD"
        value["context"] = {key: key for key in value["context"]}
        value["verification_dimensions"].update({"render":"observed", "flow":"observed", "keyboard":"observed", "focus":"observed"})
        value["interaction_cost"].update({"required_decisions":1, "actions_to_primary_success":2, "default_selection_rationale":"No safe target default."})
        for i, viewport in enumerate(("desktop", "mobile")):
            value["runtime_checks"][viewport].update({"inner_width":1440 if viewport == "desktop" else 390, "scroll_width":1440 if viewport == "desktop" else 390, "primary_action_verified":True, "recovery_verified":True, "keyboard_path_verified":True, "focus_visible_verified":True, "focus_not_obscured_verified":True})
            for j, state in enumerate(("start", "terminal", "focus")):
                path = root / f"{viewport}-{state}.png"
                png(path, i * 10 + j + 1)
                value["evidence"][viewport][state] = {"artifact":str(path), "observation":f"observed {viewport} {state}"}
        return value

    def test_valid_standard(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual([], gate.validate(self.valid(root), root / "report.json"))

    def test_boolean_only_focus_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = self.valid(root)
            value["verification_dimensions"]["focus"] = "static_only"
            self.assertIn("verification_dimensions.focus must be observed", gate.validate(value, root / "report.json"))

    def test_fabricated_friction_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = self.valid(root)
            value["interaction_cost"]["fabricated_friction"] = ["invented selection"]
            self.assertIn("FABRICATED_FRICTION: fabricated_friction must be empty", gate.validate(value, root / "report.json"))

    def test_unverified_cli_prints_explicit_warning(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = gate.template()
            value["context"] = {key: key for key in value["context"]}
            report = root / "report.json"
            report.write_text(json.dumps(value), encoding="utf-8")
            completed = subprocess.run([sys.executable, str(Path(gate.__file__)), "--report", str(report)], capture_output=True, text=True, check=False)
            self.assertEqual(0, completed.returncode)
            self.assertIn("STANDARD_BROWSER_EVIDENCE_UNVERIFIED", completed.stdout)

    def test_tiny_png_cannot_satisfy_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = self.valid(root)
            tiny = root / "tiny.png"
            width = height = 1
            raw = b"\0" + bytes((1, 2, 3))
            def chunk(kind: bytes, payload: bytes) -> bytes:
                return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff)
            tiny.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
            value["evidence"]["desktop"]["focus"]["artifact"] = str(tiny)
            self.assertTrue(any("readable PNG" in error for error in gate.validate(value, root / "report.json")))


if __name__ == "__main__":
    unittest.main()

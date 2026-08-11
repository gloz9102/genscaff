from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import inspect_project


class InspectProjectTests(unittest.TestCase):
    def test_detects_metadata_without_commands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package-lock.json").write_text("{}", encoding="utf-8")
            (root / "package.json").write_text(json.dumps({"scripts": {"test": "vitest"}, "dependencies": {"next": "1", "react": "1"}, "devDependencies": {"vitest": "1", "tailwindcss": "1"}}), encoding="utf-8")
            (root / "tsconfig.json").write_text("{}", encoding="utf-8")
            (root / "src" / "app").mkdir(parents=True)
            result = inspect_project.inspect(root)
            self.assertEqual(["npm"], result["facts"]["package_managers"])
            self.assertEqual(["Next.js", "React"], result["heuristic_detections"]["framework"])
            self.assertEqual(["Vitest"], result["heuristic_detections"]["tests"])
            self.assertTrue(result["facts"]["has_app_router"])
            self.assertEqual([], result["commands_executed"])

    def test_missing_root_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                inspect_project.inspect(Path(directory) / "missing")


if __name__ == "__main__":
    unittest.main()

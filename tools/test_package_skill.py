from __future__ import annotations

import tempfile
import subprocess
import sys
import os
import unittest
import zipfile
from pathlib import Path

import package_skill


class PackageTests(unittest.TestCase):
    def test_plugin_archive_is_self_contained(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "genscaff-plugin.zip"
            package_skill.archive(output, [(package_skill.PLUGIN_ROOT, Path("genscaff"))])
            self.assertEqual([], package_skill.verify_archive(output))
            with zipfile.ZipFile(output) as source:
                names = set(source.namelist())
            self.assertIn("genscaff/skills/genscaff/SKILL.md", names)
            self.assertIn("genscaff/skills/genscaff-release-audit/SKILL.md", names)
            self.assertIn("genscaff/skills/genscaff-release-audit/scripts/auditlib/report_api.py", names)
            extracted = Path(directory) / "unpacked"
            with zipfile.ZipFile(output) as source:
                source.extractall(extracted)
            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            for skill, profile in (("genscaff", "standard"), ("genscaff-release-audit", "strict")):
                cli = extracted / "genscaff" / "skills" / skill / "scripts" / "quality_gate.py"
                report = Path(directory) / f"{profile}.json"
                initialized = subprocess.run([sys.executable, str(cli), "--init", str(report), "--profile", profile], cwd=extracted, env=env, capture_output=True, text=True)
                self.assertEqual(0, initialized.returncode, initialized.stderr)
                checked = subprocess.run([sys.executable, str(cli), "--report", str(report)], cwd=extracted, env=env, capture_output=True, text=True)
                self.assertEqual(1, checked.returncode, checked.stdout + checked.stderr)
                self.assertNotIn("Traceback", checked.stderr)
                if profile == "strict":
                    self.assertIn("ACTIVE_BROWSER_AUDIT_SKIPPED_UNTRUSTED", checked.stdout)

    def test_legacy_kind_is_rejected_before_creating_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(Path(package_skill.__file__)), "--kind", "legacy", "--output-dir", directory], capture_output=True, text=True)
            self.assertEqual(2, result.returncode)
            self.assertIn("invalid choice", result.stderr)
            self.assertEqual([], list(Path(directory).iterdir()))

    def test_versioned_archives_use_current_manifest_and_keep_history(self) -> None:
        version = package_skill.json.loads((package_skill.PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(Path(package_skill.__file__)), "--output-dir", directory], capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            files = {path.name for path in Path(directory).iterdir()}
            self.assertEqual({"genscaff-plugin.zip", "genscaff-plugin.zip.sha256", f"genscaff-eval-v{version}.zip", f"genscaff-eval-v{version}.zip.sha256", f"genscaff-eval-v{version}-summary.json"}, files)
            summary = package_skill.json.loads((Path(directory) / f"genscaff-eval-v{version}-summary.json").read_text(encoding="utf-8"))
            self.assertEqual(version, summary["version"])
            self.assertTrue((package_skill.REPO_ROOT / "evals/baselines/v2.0.0.json").is_file())
            with zipfile.ZipFile(Path(directory) / "genscaff-plugin.zip") as source:
                self.assertFalse(any("/skill/genscaff/" in name for name in source.namelist()))

    def test_plugin_only_does_not_package_evaluation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(Path(package_skill.__file__)), "--kind", "plugin", "--output-dir", directory], capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual({"genscaff-plugin.zip", "genscaff-plugin.zip.sha256"}, {path.name for path in Path(directory).iterdir()})


if __name__ == "__main__":
    unittest.main()

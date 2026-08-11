from __future__ import annotations

import tempfile
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

    def test_legacy_archive_is_self_contained(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "genscaff-legacy.zip"
            package_skill.archive(output, [(package_skill.LEGACY_ROOT, Path("genscaff"))])
            self.assertEqual([], package_skill.verify_archive(output))


if __name__ == "__main__":
    unittest.main()

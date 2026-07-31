from __future__ import annotations

import unittest

import check_skill


class PluginTests(unittest.TestCase):
    def test_structure_and_explicit_invocation(self) -> None:
        self.assertEqual([], check_skill.validate(allow_generated=True))

    def test_trigger_boundary_text(self) -> None:
        core = (check_skill.CORE_ROOT / "SKILL.md").read_text(encoding="utf-8")
        audit = (check_skill.AUDIT_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("explicitly invokes `$genscaff`", core)
        self.assertIn("explicitly invokes `$genscaff-release-audit`", audit)
        self.assertIn("deprecated", core)


if __name__ == "__main__":
    unittest.main()

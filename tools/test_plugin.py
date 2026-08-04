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

    def test_loading_contract_is_routed_by_both_skills(self) -> None:
        for root in (check_skill.CORE_ROOT, check_skill.AUDIT_ROOT):
            skill = (root / "SKILL.md").read_text(encoding="utf-8")
            contract = (root / "references" / "loading-ux.md").read_text(encoding="utf-8")
            self.assertIn("references/loading-ux.md", skill)
            self.assertIn("A spinner is not a loading strategy", contract)
            self.assertIn("Do not show a fabricated percentage", contract)
            self.assertIn("Do not use optimistic completion for payment", contract)


if __name__ == "__main__":
    unittest.main()

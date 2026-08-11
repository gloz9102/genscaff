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
        self.assertIn("reference_mode", core)
        self.assertIn("VERIFIED_STANDARD_BASELINE", core)
        self.assertNotIn("primary-start → primary-feedback", core)

    def test_korean_production_copy_register_is_enforced(self) -> None:
        core = (check_skill.CORE_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("default to professional 존댓말", core)
        self.assertIn("never ship 반말 or 음슴체 endings", core)
        self.assertIn("좌석 수보다 먼저, 좌석의 이유를 설계합니다.", core)
        self.assertIn("release requirement", core)

    def test_manifest_and_metadata_match_two_skill_roles(self) -> None:
        manifest = check_skill.json.loads((check_skill.PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual("./skills/", manifest["skills"])
        self.assertTrue((check_skill.CORE_ROOT / "SKILL.md").is_file())
        self.assertTrue((check_skill.AUDIT_ROOT / "SKILL.md").is_file())
        core_agent = (check_skill.CORE_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        audit_agent = (check_skill.AUDIT_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("creation, modernization, and Standard", core_agent)
        self.assertIn("Explicit Strict and release-critical", audit_agent)

    def test_loading_contract_is_routed_by_both_skills(self) -> None:
        for root in (check_skill.CORE_ROOT, check_skill.AUDIT_ROOT):
            skill = (root / "SKILL.md").read_text(encoding="utf-8")
            contract = (root / "references" / "loading-ux.md").read_text(encoding="utf-8")
            self.assertIn("references/loading-ux.md", skill)
            self.assertIn("A spinner is not a loading strategy", contract)
            self.assertIn("Do not show a fabricated percentage", contract)
            self.assertIn("Do not use optimistic completion for payment", contract)

    def test_bilingual_docs_cover_current_contract(self) -> None:
        pairs = (
            (check_skill.REPO_ROOT / "README.md", check_skill.REPO_ROOT / "README.ko.md"),
            (check_skill.REPO_ROOT / "docs" / "comparison.md", check_skill.REPO_ROOT / "docs" / "comparison.ko.md"),
            (check_skill.REPO_ROOT / "docs" / "slowdrop-comparison.md", check_skill.REPO_ROOT / "docs" / "slowdrop-comparison.ko.md"),
        )
        for english, korean in pairs:
            self.assertTrue(english.is_file() and korean.is_file())
        for path in pairs[0]:
            text = path.read_text(encoding="utf-8")
            for term in ("aesthetic-inspiration", "product-editorial", "VERIFIED_STANDARD_BASELINE", "$genscaff-release-audit"):
                self.assertIn(term, text)


if __name__ == "__main__":
    unittest.main()

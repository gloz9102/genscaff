from __future__ import annotations

import unittest
import ast

import check_skill


class PluginTests(unittest.TestCase):
    def test_structure_and_explicit_invocation(self) -> None:
        self.assertEqual([], check_skill.validate(allow_generated=True))

    def test_trigger_boundary_text(self) -> None:
        core = (check_skill.CORE_ROOT / "SKILL.md").read_text(encoding="utf-8")
        audit = (check_skill.AUDIT_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("explicitly invokes `$genscaff`", core)
        self.assertIn("explicitly invokes `$genscaff-release-audit`", audit)
        self.assertIn("unsupported in v2.1", core)
        self.assertIn("do not automatically start Standard or Strict", core)
        self.assertNotIn("deprecated v2.0", audit)
        self.assertIn("reference_mode", core)
        self.assertIn("VERIFIED_STANDARD_BASELINE", core)
        self.assertNotIn("primary-start → primary-feedback", core)

    def test_korean_production_copy_register_is_enforced(self) -> None:
        core = (check_skill.CORE_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("default to professional 존댓말", core)
        self.assertIn("never ship 반말 or 음슴체 endings", core)

        self.assertIn("release requirement", core)

    def test_standard_routes_to_requirement_owners(self) -> None:
        core = (check_skill.CORE_ROOT / "SKILL.md").read_text(encoding="utf-8")
        owners = {
            "visual-target-template.md": ("## Preservation", "## Engineering", "## Inspect before completing the contract"),
            "design-exploration.md": ("## User choice and routing", "## Controlled comparison"),
            "reference-intent.md": ("## Locked reproduction", "## Structural reference", "## Aesthetic inspiration"),
            "verification-baseline.md": ("## Status ceiling", "## Preservation and reference evidence"),
            "quality-report-schema.md": ("--init", "--report"),
        }
        for name, requirements in owners.items():
            self.assertIn(f"references/{name}", core)
            owner = (check_skill.CORE_ROOT / "references" / name).read_text(encoding="utf-8")
            for requirement in requirements:
                self.assertIn(requirement, owner)
        self.assertIn("| Visual direction is open | `references/ui-craft-guidelines.md` |", core)

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

    def test_audit_modules_have_no_cycles_or_cli_backimports(self) -> None:
        root = check_skill.AUDIT_ROOT / "scripts" / "auditlib"
        graph = {}
        for path in root.glob("*.py"):
            dependencies = set()
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Import):
                    self.assertFalse({"hard_gate", "quality_gate"} & {name.name for name in node.names}, path.name)
                elif isinstance(node, ast.ImportFrom):
                    self.assertNotIn(node.module, {"hard_gate", "quality_gate"}, path.name)
                    if node.level == 1:
                        dependencies.update([node.module] if node.module else [name.name for name in node.names])
            graph[path.stem] = dependencies
        active, finished = set(), set()
        def visit(name):
            self.assertNotIn(name, active, f"circular audit import: {name}")
            if name in finished:
                return
            self.assertIn(name, graph, f"missing internal audit module: {name}")
            active.add(name)
            for dependency in graph[name]:
                visit(dependency)
            active.remove(name)
            finished.add(name)
        for name in graph:
            visit(name)

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

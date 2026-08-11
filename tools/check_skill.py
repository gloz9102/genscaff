#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEGACY_ROOT = REPO_ROOT / "skill" / "genscaff"
PLUGIN_ROOT = REPO_ROOT / "plugins" / "genscaff"
CORE_ROOT = PLUGIN_ROOT / "skills" / "genscaff"
AUDIT_ROOT = PLUGIN_ROOT / "skills" / "genscaff-release-audit"
GENERATED = {"__pycache__", "node_modules"}
PERSONAL = (re.compile(r"[A-Za-z]:\\Users\\[^\\/\r\n]+\\", re.I), re.compile(r"/(?:Users|home)/[^/\s]+/"))
LOCAL_TARGET = re.compile(r"(?:references|scripts)/[A-Za-z0-9._/-]+")
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\((?!https?://|mailto:|#)([^)]+)\)")


def files_under(root: Path) -> list[Path]:
    found = []
    for current, directories, names in os.walk(root):
        directories[:] = sorted(name for name in directories if name not in GENERATED)
        found.extend(Path(current) / name for name in sorted(names) if not name.endswith((".pyc", ".pyo")))
    return found


def distributable_files(root: Path = LEGACY_ROOT) -> list[Path]:
    return files_under(root)


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not match:
        return {}
    result = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"')
    return result


def validate_skill(root: Path, name: str, required: tuple[str, ...], *, explicit: bool = True) -> list[str]:
    errors = []
    for relative in ("SKILL.md", "agents/openai.yaml", *required):
        if not (root / relative).is_file():
            errors.append(f"{name}: missing {relative}")
    if (root / "SKILL.md").is_file():
        metadata = frontmatter(root / "SKILL.md")
        if set(metadata) != {"name", "description"}:
            errors.append(f"{name}: invalid SKILL.md frontmatter")
        if metadata.get("name") != name:
            errors.append(f"{name}: frontmatter name mismatch")
        if metadata.get("name", "") != metadata.get("name", "").lower():
            errors.append(f"{name}: frontmatter name must be lowercase")
        if len(metadata.get("description", "")) < 40:
            errors.append(f"{name}: description is too short")
    yaml = root / "agents" / "openai.yaml"
    if yaml.is_file():
        content = yaml.read_text(encoding="utf-8")
        for field in ("display_name:", "short_description:", "default_prompt:"):
            if field not in content:
                errors.append(f"{name}: agents/openai.yaml missing {field[:-1]}")
    if explicit and yaml.is_file() and "allow_implicit_invocation: false" not in yaml.read_text(encoding="utf-8"):
        errors.append(f"{name}: implicit invocation must be disabled")
    for markdown in (path for path in files_under(root) if path.suffix.lower() == ".md"):
        content = markdown.read_text(encoding="utf-8")
        targets = set(LOCAL_TARGET.findall(content))
        targets.update(match.group(1).split("#", 1)[0] for match in MARKDOWN_LINK.finditer(content))
        for target in targets:
            if not target:
                continue
            candidate = (markdown.parent / target).resolve() if target.startswith(("./", "../")) else (root / target).resolve()
            try:
                candidate.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{name}: reference escapes package root: {markdown.relative_to(root)} -> {target}")
                continue
            if not candidate.is_file():
                errors.append(f"{name}: broken local reference: {markdown.relative_to(root)} -> {target}")
    return errors


def validate(*, allow_generated: bool = False) -> list[str]:
    errors = []
    errors += validate_skill(CORE_ROOT, "genscaff", ("scripts/quality_gate.py", "scripts/inspect_project.py", "references/reference-intent.md", "references/task-type-craft-router.md", "references/responsive-state-matrix.md", "references/verification-baseline.md", "references/anti-slop.md"))
    errors += validate_skill(AUDIT_ROOT, "genscaff-release-audit", ("scripts/hard_gate.py", "scripts/quality_gate.py", "scripts/live_audit.js", "scripts/lighthouse_audit.js", "scripts/runtime_probe.js", "scripts/package.json", "scripts/package-lock.json"))
    errors += validate_skill(LEGACY_ROOT, "genscaff", ("scripts/hard_gate.py", "scripts/quality_gate.py"), explicit=False)

    forbidden_core = tuple(CORE_ROOT.rglob("package*.json")) + tuple(CORE_ROOT.rglob("*.js"))
    if forbidden_core:
        errors.append("genscaff: core skill must not contain Node, Lighthouse, or Playwright files")
    manifest_path = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
    marketplace_path = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"invalid plugin metadata: {error}")
    else:
        expected = {"name":"genscaff", "version":"2.0.1", "license":"Apache-2.0", "repository":"https://github.com/gloz9102/genscaff"}
        for key, value in expected.items():
            if manifest.get(key) != value:
                errors.append(f"plugin manifest {key} must be {value}")
        if manifest.get("interface", {}).get("brandColor") != "#182C51":
            errors.append("plugin brandColor must be #182C51")
        if marketplace.get("name") != "genscaff-public":
            errors.append("marketplace name must be genscaff-public")
        entries = marketplace.get("plugins", [])
        if len(entries) != 1 or entries[0].get("source", {}).get("path") != "./plugins/genscaff":
            errors.append("marketplace plugin path must be ./plugins/genscaff")
        elif entries[0].get("policy") != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}:
            errors.append("marketplace plugin policy must be AVAILABLE with ON_INSTALL authentication")
        for relative in ("composerIcon", "logo", "logoDark"):
            value = manifest.get("interface", {}).get(relative)
            if not value or not (PLUGIN_ROOT / value).is_file():
                errors.append(f"plugin asset is missing: {relative}")

    package_path = AUDIT_ROOT / "scripts" / "package.json"
    if package_path.is_file():
        package = json.loads(package_path.read_text(encoding="utf-8"))
        lock = json.loads(package_path.with_name("package-lock.json").read_text(encoding="utf-8"))
        if package.get("private") is not True or package.get("license") != "Apache-2.0":
            errors.append("audit package must be private and Apache-2.0")
        if lock.get("packages", {}).get("", {}).get("dependencies") != package.get("dependencies"):
            errors.append("audit lockfile dependencies do not match package.json")

    for root in (LEGACY_ROOT, PLUGIN_ROOT):
        for current, directories, names in os.walk(root):
            path = Path(current)
            if not allow_generated:
                for name in directories:
                    if name in GENERATED:
                        errors.append(f"generated directory is not distributable: {(path / name).relative_to(root)}")
            directories[:] = [name for name in directories if name not in GENERATED]
            for name in names:
                file = path / name
                if file.suffix.lower() in {".md", ".yaml", ".yml", ".json", ".py", ".js"}:
                    content = file.read_text(encoding="utf-8", errors="replace")
                    if any(pattern.search(content) for pattern in PERSONAL):
                        errors.append(f"personal path found: {file.relative_to(REPO_ROOT)}")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Genscaff plugin and legacy package structure")
    parser.add_argument("--reject-generated", action="store_true", help="fail when local cache or dependency directories exist")
    args = parser.parse_args()
    errors = validate(allow_generated=not args.reject_generated)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("GENSCAFF_PLUGIN_AND_LEGACY_STRUCTURE_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

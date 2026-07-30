#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_ROOT = REPO_ROOT / "skill" / "genscaff"
PERSONAL_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:\\Users\\[^\\/\r\n]+\\", re.IGNORECASE),
    re.compile(r"/(?:Users|home)/[^/\s]+/"),
)


def validate() -> list[str]:
    errors: list[str] = []
    required = [
        "SKILL.md",
        "LICENSE",
        "NOTICE",
        "THIRD_PARTY_NOTICES.md",
        "agents/openai.yaml",
        "scripts/hard_gate.py",
        "scripts/quality_gate.py",
        "scripts/live_audit.js",
        "scripts/lighthouse_audit.js",
        "scripts/runtime_probe.js",
        "scripts/test_quality_gate.py",
        "scripts/package.json",
        "references/aggressive-hard-gate.md",
        "references/quality-report-schema.md",
    ]
    for relative in required:
        if not (SKILL_ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    skill_path = SKILL_ROOT / "SKILL.md"
    if skill_path.is_file():
        text = skill_path.read_text(encoding="utf-8")
        match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
        if not match:
            errors.append("SKILL.md has invalid YAML frontmatter boundaries")
        else:
            metadata: dict[str, str] = {}
            for line in match.group(1).splitlines():
                if ":" not in line:
                    errors.append(f"invalid frontmatter line: {line}")
                    continue
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip().strip('"')
            if set(metadata) != {"name", "description"}:
                errors.append("SKILL.md frontmatter must contain only name and description")
            if metadata.get("name") != "genscaff":
                errors.append("SKILL.md name must be genscaff")
            if len(metadata.get("description", "")) < 40:
                errors.append("SKILL.md description is unexpectedly short")

    package_path = SKILL_ROOT / "scripts" / "package.json"
    if package_path.is_file():
        try:
            package = json.loads(package_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"invalid scripts/package.json: {error}")
        else:
            if package.get("license") != "Apache-2.0":
                errors.append("scripts/package.json license must be Apache-2.0")
            if package.get("private") is not True:
                errors.append("scripts/package.json must remain private")

    if SKILL_ROOT.is_dir():
        for path in SKILL_ROOT.rglob("*"):
            relative = path.relative_to(SKILL_ROOT).as_posix()
            if path.name == "__pycache__" or path.suffix == ".pyc" or "node_modules" in path.parts:
                errors.append(f"generated dependency or cache is not distributable: {relative}")
            if path.is_file() and path.suffix.lower() in {".md", ".yaml", ".yml", ".json", ".py", ".js"}:
                content = path.read_text(encoding="utf-8", errors="replace")
                if any(pattern.search(content) for pattern in PERSONAL_PATH_PATTERNS):
                    errors.append(f"personal absolute path found: {relative}")

    return sorted(set(errors))


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("GENSCAFF_SKILL_STRUCTURE_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

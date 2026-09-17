#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import zipfile
from pathlib import Path

from check_skill import PLUGIN_ROOT, REPO_ROOT, files_under, validate

FIXED_TIME = (2026, 1, 1, 0, 0, 0)


def archive(output: Path, roots: list[tuple[Path, Path]]) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.unlink(missing_ok=True)
    entries = []
    for source, prefix in roots:
        entries.extend((prefix / path.relative_to(source), path) for path in files_under(source))
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as target:
        for relative, path in sorted(entries, key=lambda pair: pair[0].as_posix()):
            info = zipfile.ZipInfo(relative.as_posix(), FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o644 & 0xffff) << 16
            target.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    os.replace(temporary, output)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    return digest


def verify_archive(path: Path) -> list[str]:
    errors = []
    with zipfile.ZipFile(path) as source:
        names = set(source.namelist())
        skill_roots = {Path(name).parent for name in names if name.endswith("/SKILL.md")}
        for root in skill_roots:
            for required in ("SKILL.md", "agents/openai.yaml", "LICENSE", "NOTICE"):
                expected = (root / required).as_posix()
                if expected not in names:
                    errors.append(f"{path.name}: missing {expected}")
            content = source.read((root / "SKILL.md").as_posix()).decode("utf-8")
            for target in set(re.findall(r"(?:references|scripts)/[A-Za-z0-9._/-]+", content)):
                expected = (root / target).as_posix()
                if expected not in names:
                    errors.append(f"{path.name}: non-self-contained reference {expected}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Build reproducible Genscaff plugin and evaluation archives")
    parser.add_argument("--kind", choices=("all", "plugin"), default="all")
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "dist")
    parser.add_argument("--eval-run", type=Path)
    args = parser.parse_args()
    if args.kind == "plugin" and args.eval_run:
        parser.error("--eval-run requires --kind all")
    errors = validate(allow_generated=True)
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    args.output_dir.mkdir(parents=True, exist_ok=True)
    version = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    built = [(args.output_dir / "genscaff-plugin.zip", [(PLUGIN_ROOT, Path("genscaff"))])]
    if args.kind == "all":
        name = f"genscaff-eval-v{version}"
        if args.eval_run:
            run = args.eval_run.resolve()
            summary = run / "summary.json"
            roots = [(run, Path(name))]
        else:
            summary = REPO_ROOT / "evals" / "baselines" / f"v{version}.json"
            roots = [(REPO_ROOT / "evals", Path(name) / "evals")]
        if not summary.is_file():
            print(f"ERROR: missing evaluation summary: {summary}", file=sys.stderr)
            return 1
        built.append((args.output_dir / f"{name}.zip", roots))
        (args.output_dir / f"{name}-summary.json").write_bytes(summary.read_bytes())
    for output, roots in built:
        print(f"{output.name} {archive(output.resolve(), roots)}")
        errors = verify_archive(output.resolve())
        if errors:
            print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

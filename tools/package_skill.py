#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

from check_skill import LEGACY_ROOT, PLUGIN_ROOT, REPO_ROOT, files_under, validate

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


def main() -> int:
    parser = argparse.ArgumentParser(description="Build reproducible Genscaff v2.0 archives")
    parser.add_argument("--kind", choices=("all", "plugin", "legacy"), default="all")
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "dist")
    parser.add_argument("--eval-run", type=Path)
    args = parser.parse_args()
    errors = validate(allow_generated=True)
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    built = []
    if args.kind in {"all", "plugin"}:
        built.append((args.output_dir / "genscaff-plugin.zip", [(PLUGIN_ROOT, Path("genscaff"))]))
    if args.kind in {"all", "legacy"}:
        built.append((args.output_dir / "genscaff-legacy.zip", [(LEGACY_ROOT, Path("genscaff"))]))
    if args.eval_run:
        run = args.eval_run.resolve()
        summary = run / "summary.json"
        if not summary.is_file():
            print("ERROR: eval run must contain summary.json", file=sys.stderr)
            return 1
        built.append((args.output_dir / "genscaff-eval-v2.0.0.zip", [(run, Path("genscaff-eval-v2.0.0"))]))
        (args.output_dir / "genscaff-eval-v2.0.0-summary.json").write_bytes(summary.read_bytes())
    else:
        built.append((args.output_dir / "genscaff-eval-v2.0.0.zip", [(REPO_ROOT / "evals", Path("genscaff-eval-v2.0.0/evals"))]))
        (args.output_dir / "genscaff-eval-v2.0.0-summary.json").write_bytes((REPO_ROOT / "evals" / "baselines" / "v2.0.0.json").read_bytes())
    for output, roots in built:
        print(f"{output.name} {archive(output.resolve(), roots)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

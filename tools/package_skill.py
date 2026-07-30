#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import zipfile
from pathlib import Path

from check_skill import REPO_ROOT, SKILL_ROOT, validate


FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a reproducible Genscaff skill archive")
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "dist" / "genscaff.zip",
        help="Output ZIP path (default: dist/genscaff.zip)",
    )
    return parser.parse_args()


def build_archive(output: Path) -> str:
    errors = validate()
    if errors:
        raise RuntimeError("skill validation failed:\n" + "\n".join(errors))

    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.unlink(missing_ok=True)

    files = sorted(path for path in SKILL_ROOT.rglob("*") if path.is_file())
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = Path("genscaff") / path.relative_to(SKILL_ROOT)
            info = zipfile.ZipInfo(relative.as_posix(), FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o644 & 0xFFFF) << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    os.replace(temporary, output)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{digest}  {output.name}\n",
        encoding="utf-8",
    )
    return digest


def main() -> int:
    args = parse_args()
    try:
        digest = build_archive(args.output)
    except (OSError, RuntimeError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Wrote {args.output.resolve()}")
    print(f"SHA256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

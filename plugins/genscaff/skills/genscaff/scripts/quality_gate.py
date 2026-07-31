#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

STATUSES = ("IMPLEMENTED_UNVERIFIED", "VERIFIED_RENDER", "VERIFIED_FLOW", "VERIFIED_STANDARD")
DIMENSION_VALUES = {"observed", "static_only", "automated", "not_tested"}
DIMENSIONS = ("render", "flow", "keyboard", "focus", "automated_accessibility", "assistive_technology_user_validation")


def template() -> dict:
    return {
        "schema_version": 5,
        "profile": "standard",
        "completion_status": "IMPLEMENTED_UNVERIFIED",
        "context": {key: "" for key in ("target_user", "primary_task", "success_outcome", "primary_cta", "recovery")},
        "verification_dimensions": {key: "not_tested" for key in DIMENSIONS},
        "evidence": {viewport: {state: {"artifact": "", "observation": ""} for state in ("start", "terminal", "focus")} for viewport in ("desktop", "mobile")},
        "runtime_checks": {viewport: {"inner_width": 0, "scroll_width": 0, "console_errors": 0, "console_warnings": 0, "primary_action_verified": False, "recovery_verified": False, "keyboard_path_verified": False, "focus_visible_verified": False, "focus_not_obscured_verified": False} for viewport in ("desktop", "mobile")},
        "interaction_cost": {"required_decisions": 0, "actions_to_primary_success": 0, "default_selection_rationale": "", "fabricated_friction": []},
        "notes": [],
    }


def png_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        data = path.read_bytes()[:24]
    except OSError:
        return None
    if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        return struct.unpack(">II", data[16:24])
    return None


def evidence_path(report_path: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else report_path.parent / path


def validate(data: dict, report_path: Path) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != 5:
        errors.append("schema_version must be 5")
    if data.get("profile") != "standard":
        errors.append("profile must be standard")
    status = data.get("completion_status")
    if status not in STATUSES:
        errors.append("invalid completion_status")
        status = "IMPLEMENTED_UNVERIFIED"
    context = data.get("context", {})
    for key in ("target_user", "primary_task", "success_outcome", "primary_cta", "recovery"):
        if not isinstance(context.get(key), str) or not context.get(key, "").strip():
            errors.append(f"context.{key} must be non-empty")
    dimensions = data.get("verification_dimensions", {})
    for key in DIMENSIONS:
        if dimensions.get(key) not in DIMENSION_VALUES:
            errors.append(f"verification_dimensions.{key} is invalid")
    interaction = data.get("interaction_cost", {})
    for key in ("required_decisions", "actions_to_primary_success"):
        if not isinstance(interaction.get(key), int) or interaction.get(key, -1) < 0:
            errors.append(f"interaction_cost.{key} must be a non-negative integer")
    if not isinstance(interaction.get("default_selection_rationale"), str):
        errors.append("interaction_cost.default_selection_rationale must be a string")
    friction = interaction.get("fabricated_friction")
    if not isinstance(friction, list):
        errors.append("interaction_cost.fabricated_friction must be a list")
    elif friction:
        errors.append("FABRICATED_FRICTION: fabricated_friction must be empty")

    level = STATUSES.index(status)
    required_states = () if level == 0 else (("start",) if level == 1 else (("start", "terminal") if level == 2 else ("start", "terminal", "focus")))
    hashes: list[str] = []
    for viewport in ("desktop", "mobile"):
        runtime = data.get("runtime_checks", {}).get(viewport, {})
        if level >= 1:
            if runtime.get("inner_width", 0) <= 0 or runtime.get("scroll_width") != runtime.get("inner_width"):
                errors.append(f"runtime_checks.{viewport} has missing width or horizontal overflow")
            for key in ("console_errors", "console_warnings"):
                if runtime.get(key) != 0:
                    errors.append(f"runtime_checks.{viewport}.{key} must be 0")
        if level >= 2:
            for key in ("primary_action_verified", "recovery_verified"):
                if runtime.get(key) is not True:
                    errors.append(f"runtime_checks.{viewport}.{key} must be true for {status}")
        if level >= 3:
            for key in ("keyboard_path_verified", "focus_visible_verified", "focus_not_obscured_verified"):
                if runtime.get(key) is not True:
                    errors.append(f"runtime_checks.{viewport}.{key} must be true for VERIFIED_STANDARD")
        for state in required_states:
            item = data.get("evidence", {}).get(viewport, {}).get(state, {})
            if not isinstance(item.get("observation"), str) or not item.get("observation", "").strip():
                errors.append(f"evidence.{viewport}.{state}.observation must be non-empty")
            artifact = item.get("artifact", "")
            path = evidence_path(report_path, artifact) if isinstance(artifact, str) and artifact else None
            if not path or not path.is_file() or png_dimensions(path) is None:
                errors.append(f"evidence.{viewport}.{state}.artifact must be a readable PNG")
            else:
                hashes.append(hashlib.sha256(path.read_bytes()).hexdigest())
    if len(hashes) != len(set(hashes)):
        errors.append("evidence artifacts must be distinct")
    if level >= 1 and dimensions.get("render") != "observed":
        errors.append("verification_dimensions.render must be observed")
    if level >= 2 and dimensions.get("flow") != "observed":
        errors.append("verification_dimensions.flow must be observed")
    if level >= 3:
        for key in ("keyboard", "focus"):
            if dimensions.get(key) != "observed":
                errors.append(f"verification_dimensions.{key} must be observed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a lightweight Genscaff Standard report")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--init", type=Path)
    group.add_argument("--report", type=Path)
    parser.add_argument("--profile", choices=("standard",), default="standard")
    args = parser.parse_args()
    if args.init:
        args.init.parent.mkdir(parents=True, exist_ok=True)
        args.init.write_text(json.dumps(template(), indent=2) + "\n", encoding="utf-8")
        print(f"INITIALIZED={args.init.resolve()}")
        return 0
    try:
        data = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    errors = validate(data, args.report.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"COMPLETION_STATUS={data['completion_status']}")
    print("GENSCAFF_STANDARD_REPORT_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

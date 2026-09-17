"""Command-line report initialization and validation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from . import hard_api as hard_gate
from .report_api import (
    validate,
)
from .report_constants import (
    LEGACY_PROFILE_SCHEMA_VERSION,
    PROFILE_SCHEMA_VERSION,
    SCHEMA_VERSION,
    VALID_PROFILES,
)
from .report_profiles import (
    effective_standard_status,
    profile_template,
)


def fail(errors: list[str], *, max_errors: int | None = None) -> int:
    print("FAIL")
    shown = errors if max_errors is None else errors[:max_errors]
    for error in shown:
        print(f"- {error}")
    if max_errors is not None and len(errors) > max_errors:
        print(f"- ... {len(errors) - max_errors} additional error(s) omitted")
    print(f"ERROR_COUNT={len(errors)}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an evidence-backed frontend quality gate JSON report."
    )
    parser.add_argument("--report", type=Path, help="Path to quality report JSON.")
    parser.add_argument(
        "--init",
        type=Path,
        help="Write a blank profile-aware quality report template.",
    )
    parser.add_argument(
        "--profile",
        choices=sorted(VALID_PROFILES),
        default="standard",
        help="Profile for --init (default: standard).",
    )
    parser.add_argument(
        "--execute-approved-commands",
        action="store_true",
        help="Re-run exact approved repository verification commands. Treat them as arbitrary code.",
    )
    parser.add_argument(
        "--allow-active-browser-audit",
        action="store_true",
        help="Allow target-page JavaScript, network requests, and Lighthouse for a trusted target.",
    )
    parser.add_argument(
        "--max-errors",
        type=int,
        help="Print at most this many validation errors while preserving the FAIL exit code.",
    )
    parser.add_argument(
        "--fingerprint",
        nargs="+",
        type=Path,
        help="Print the deterministic source fingerprint for one or more frontend source roots.",
    )
    args = parser.parse_args()

    if args.max_errors is not None and args.max_errors < 1:
        parser.error("--max-errors must be at least 1")

    if args.init:
        args.init.parent.mkdir(parents=True, exist_ok=True)
        args.init.write_text(
            json.dumps(profile_template(args.profile), indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote template: {args.init}")
        print(f"PROFILE={args.profile}")
        if args.profile == "strict":
            print("Fill evidence_catalog once and reuse its IDs throughout the report.")
        return 0

    if args.fingerprint:
        files: list[Path] = []
        for root in args.fingerprint:
            resolved = root.expanduser().resolve()
            if not resolved.exists():
                return fail([f"Source root does not exist: {resolved}"])
            files.extend(hard_gate.iter_source_files(resolved))
        files = sorted(set(files), key=lambda item: str(item).casefold())
        if not files:
            return fail(["No scannable frontend source files were found."])
        print(f"SOURCE_FILE_COUNT={len(files)}")
        print(f"SOURCE_FINGERPRINT={hard_gate.calculate_source_fingerprint(files)}")
        return 0

    if not args.report:
        parser.error("--report is required unless --init or --fingerprint is used")

    try:
        data = json.loads(args.report.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return fail([f"Report not found: {args.report}"], max_errors=args.max_errors)
    except json.JSONDecodeError as exc:
        return fail([f"Invalid JSON: {exc}"], max_errors=args.max_errors)

    if not isinstance(data, dict):
        return fail(["Report root must be a JSON object"], max_errors=args.max_errors)

    report_profile = (
        "legacy-strict" if data.get("schema_version") == SCHEMA_VERSION else data.get("profile")
    )
    if report_profile in {"strict", "legacy-strict"} and not args.allow_active_browser_audit:
        print("ACTIVE_BROWSER_AUDIT_SKIPPED_UNTRUSTED")
        return fail(
            ["Strict validation requires --allow-active-browser-audit for a trusted target"],
            max_errors=args.max_errors,
        )
    if report_profile == "strict":
        policy = data.get("execution_policy")
        if not isinstance(policy, dict) or policy.get("active_browser") != "approved":
            return fail(
                ["--allow-active-browser-audit requires execution_policy.active_browser=approved"],
                max_errors=args.max_errors,
            )

    if args.execute_approved_commands and data.get("schema_version") == SCHEMA_VERSION:
        return fail(
            ["legacy schema v3 cannot authorize command execution; migrate the report to schema v4 or v5"],
            max_errors=args.max_errors,
        )
    if args.execute_approved_commands and data.get("schema_version") in {
        LEGACY_PROFILE_SCHEMA_VERSION,
        PROFILE_SCHEMA_VERSION,
    }:
        policy = data.get("execution_policy")
        if not isinstance(policy, dict) or policy.get("mode") != "approved":
            return fail(
                ["--execute-approved-commands requires execution_policy.mode=approved"],
                max_errors=args.max_errors,
            )
        approved = {item.strip() for item in policy.get("approved_commands", []) if isinstance(item, str)}
        declared = {
            item.get("command", "").strip()
            for item in data.get("measurements", {}).get("commands", [])
            if isinstance(item, dict) and isinstance(item.get("command"), str)
        }
        if approved != declared:
            return fail(
                ["execution_policy.approved_commands must match measurements.commands exactly"],
                max_errors=args.max_errors,
            )

    errors = validate(
        data,
        args.report,
        execute_approved_commands=args.execute_approved_commands,
    )
    if errors:
        return fail(errors, max_errors=args.max_errors)

    profile = report_profile
    print(f"PROFILE={profile}")
    if profile == "standard":
        completion_status, downgraded = effective_standard_status(data)
        print(f"COMPLETION_STATUS={completion_status}")
        if downgraded:
            print("SCHEMA_V4_DOWNGRADED_TO_VERIFIED_FLOW")
        if completion_status == "IMPLEMENTED_UNVERIFIED":
            print("STANDARD_BROWSER_EVIDENCE_UNVERIFIED")
    if profile in {"strict", "legacy-strict"}:
        print("STRUCTURAL_EVIDENCE_INVARIANTS_VERIFIED")
        if args.execute_approved_commands:
            print("COMMAND_EXECUTION_VERIFIED")
        else:
            print("COMMAND_EXECUTION_SKIPPED_UNTRUSTED")
            print("STRICT_COMMAND_REEXECUTION_NOT_VERIFIED")
        print("REVIEW_PROVENANCE_UNVERIFIED")
        print(
            "The validator-owned structural and live-browser invariants were reproduced. "
            "A root agent must separately verify the actual collaboration mailbox; neither "
            "status proves authorship, originality, representative-user usability, or the "
            "absence of every possible low-quality pattern."
        )
    else:
        print("GENSCAFF_STANDARD_REPORT_VALID")
        print("Only the declared Standard evidence level was validated; Strict live-browser invariants were not run.")
    return 0

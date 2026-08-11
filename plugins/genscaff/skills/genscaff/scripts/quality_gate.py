#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import zlib
from copy import deepcopy
from pathlib import Path

SCHEMA_VERSION = 6
LEGACY_SCHEMA_VERSION = 5
STATUSES = (
    "IMPLEMENTED_UNVERIFIED",
    "VERIFIED_RENDER",
    "VERIFIED_PRIMARY_FLOW",
    "VERIFIED_KEYBOARD_FLOW",
    "VERIFIED_STANDARD_BASELINE",
)
RESULTS = {"pass", "fail", "partial", "pass_with_limitations", "not_run", "blocked"}
METHODS = {"observed", "manual", "automated", "static", "none"}
DIMENSIONS = (
    "render",
    "flow",
    "keyboard",
    "focus",
    "automated_accessibility",
    "manual_accessibility",
    "assistive_technology_user_validation",
    "representative_user_validation",
)
PROJECT_MODES = {"existing", "new"}
REFERENCE_MODES = {"locked-reproduction", "structural-reference", "aesthetic-inspiration", "no-reference"}
ARCHETYPES = {"product-editorial", "marketplace-discovery", "media-discovery", "workflow-application", "content-editorial", "transaction"}
SURFACE_TYPES = {"landing", "search", "listing", "detail", "dashboard", "form", "checkout", "authentication", "settings", "onboarding"}
CHANGE_SCOPES = {"local", "component-set", "route", "multi-route"}
LOADING_BOUNDARY_FIELDS = ("trigger", "affected_surface", "wait_avoidance", "stale_data_policy", "failure_recovery", "user_control", "evidence")
EXECUTION_VALUES = {"approved", "not_approved"}


def dimension() -> dict:
    return {"result": "not_run", "method": "none", "coverage": "none", "evidence": [], "issues": [], "limitations": []}


def template() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "profile": "standard",
        "completion_status": "IMPLEMENTED_UNVERIFIED",
        "classification": {
            "project_mode": "existing",
            "reference_mode": "no-reference",
            "primary_experience_archetype": "workflow-application",
            "secondary_experience_archetype": "",
            "surface_types": ["dashboard"],
            "change_scope": "route",
            "rationale": "",
        },
        "contract": {
            "product": {key: "" for key in ("target_user", "primary_job", "primary_success_outcome", "domain_objects", "primary_cta", "secondary_actions", "failure_or_recovery_when_applicable")},
            "reference": {key: "" for key in ("adopted_principles", "product_fit_rationale", "deliberate_differences", "locked_requirements")},
            "content": {key: "" for key in ("content_hierarchy", "expected_item_count", "long_content_risks", "missing_data_behavior", "localization_needs", "writing_direction_needs")},
            "visual_system": {key: "" for key in ("dominant_visual_idea", "primary_focal_point", "information_density", "typography_roles", "spacing_strategy", "color_roles", "radius_strategy", "elevation_strategy", "image_or_media_strategy", "motion_intent", "reduced_motion_behavior")},
            "engineering": {key: "" for key in ("framework", "router", "rendering_model", "styling_system", "token_source", "reusable_components", "state_ownership", "data_boundary", "browser_support", "performance_risks", "verification_plan")},
        },
        "verification_dimensions": {key: dimension() for key in DIMENSIONS},
        "evidence": {viewport: {state: {"artifact": "", "observation": ""} for state in ("start", "terminal", "focus")} for viewport in ("desktop", "mobile")},
        "runtime_checks": {viewport: {"inner_width": 0, "scroll_width": 0, "console_errors": 0, "clipping_checked": False, "primary_action_verified": False, "feedback_verified": False, "terminal_result_verified": False, "recovery_applicable": False, "recovery_verified": False, "keyboard_path_verified": False, "focus_visible_verified": False, "focus_not_obscured_verified": False} for viewport in ("desktop", "mobile")},
        "state_coverage": {"relevant_states": [], "verified_states": [], "evidence": [], "limitations": []},
        "interaction_cost": {"required_decisions": 0, "actions_to_primary_success": 0, "default_selection_rationale": "", "fabricated_friction": []},
        "loading_experience": {"applicable": False, "boundaries": []},
        "execution_policy": {"repository_read": "allowed", "project_command_execution": "not_approved", "approval_source": "none", "dependency_installation": "not_approved", "active_browser": "not_approved", "networked_commands": "not_approved", "destructive_operations": "not_approved"},
        "notes": [],
    }


def png_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) < 64 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    offset, dimensions, compressed, ended = 8, None, bytearray(), False
    try:
        while offset + 12 <= len(data):
            length = struct.unpack(">I", data[offset:offset + 4])[0]
            kind = data[offset + 4:offset + 8]
            value = data[offset + 8:offset + 8 + length]
            checksum = struct.unpack(">I", data[offset + 8 + length:offset + 12 + length])[0]
            if len(value) != length or zlib.crc32(kind + value) & 0xffffffff != checksum:
                return None
            if kind == b"IHDR":
                dimensions = struct.unpack(">II", value[:8])
            elif kind == b"IDAT":
                compressed.extend(value)
            elif kind == b"IEND":
                ended = True
                break
            offset += 12 + length
        if not dimensions or dimensions[0] < 8 or dimensions[1] < 8 or not ended or not zlib.decompress(bytes(compressed)):
            return None
    except (struct.error, zlib.error):
        return None
    return dimensions


def safe_evidence_path(report_path: Path, value: str) -> Path | None:
    if not value or Path(value).is_absolute() or ".." in Path(value).parts:
        return None
    root = report_path.parent.resolve()
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def legacy_dimension(value: object) -> dict:
    mapping = {
        "observed": ("pass", "observed", []),
        "static_only": ("partial", "static", ["Legacy field did not separate result from method."]),
        "automated": ("pass_with_limitations", "automated", ["Legacy automated evidence does not establish manual or user validation."]),
        "not_tested": ("not_run", "none", []),
    }
    result, method, limitations = mapping.get(value, ("not_run", "none", ["Unknown legacy verification value."]))
    return {"result": result, "method": method, "coverage": "legacy_unspecified", "evidence": [], "issues": [], "limitations": limitations}


def migrate_v5(data: dict) -> dict:
    migrated = template()
    migrated["migration"] = {"source_schema_version": 5, "limitations": ["Legacy schema did not record classification or separated verification result/method."]}
    context = data.get("context", {})
    migrated["contract"]["product"].update({
        "target_user": context.get("target_user", ""),
        "primary_job": context.get("primary_task", ""),
        "primary_success_outcome": context.get("success_outcome", ""),
        "primary_cta": context.get("primary_cta", ""),
        "failure_or_recovery_when_applicable": context.get("recovery", ""),
    })
    migrated["classification"].update({"primary_experience_archetype": "", "surface_types": [], "rationale": "Legacy report did not record the new classification."})
    for key in DIMENSIONS:
        migrated["verification_dimensions"][key] = legacy_dimension(data.get("verification_dimensions", {}).get(key, "not_tested"))
    migrated["evidence"] = deepcopy(data.get("evidence", migrated["evidence"]))
    for viewport in ("desktop", "mobile"):
        old = data.get("runtime_checks", {}).get(viewport, {})
        migrated["runtime_checks"][viewport].update(old)
        migrated["runtime_checks"][viewport]["clipping_checked"] = old.get("inner_width", 0) > 0
        migrated["runtime_checks"][viewport]["feedback_verified"] = bool(old.get("primary_action_verified"))
        migrated["runtime_checks"][viewport]["terminal_result_verified"] = bool(old.get("primary_action_verified"))
        migrated["runtime_checks"][viewport]["recovery_applicable"] = bool(old.get("recovery_verified"))
    migrated["interaction_cost"] = deepcopy(data.get("interaction_cost", migrated["interaction_cost"]))
    migrated["loading_experience"] = deepcopy(data.get("loading_experience", migrated["loading_experience"]))
    migrated["notes"] = deepcopy(data.get("notes", []))
    migrated["completion_status"] = {
        "VERIFIED_FLOW": "VERIFIED_PRIMARY_FLOW",
        "VERIFIED_STANDARD": "VERIFIED_KEYBOARD_FLOW",
    }.get(data.get("completion_status"), data.get("completion_status", "IMPLEMENTED_UNVERIFIED"))
    return migrated


def normalize(data: dict) -> tuple[dict, str | None]:
    if data.get("schema_version") == LEGACY_SCHEMA_VERSION:
        return migrate_v5(data), "SCHEMA_V5_MIGRATED_CONSERVATIVELY"
    return data, None


def validate(data: dict, report_path: Path) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != SCHEMA_VERSION:
        return [f"schema_version must be {SCHEMA_VERSION} or supported legacy version {LEGACY_SCHEMA_VERSION}"]
    if "checks" in data:
        errors.append("schema v6 must record findings in verification issues and limitations, not a clean boolean checks bundle")
    if data.get("profile") != "standard":
        errors.append("profile must be standard")
    status = data.get("completion_status")
    if status not in STATUSES:
        errors.append("invalid completion_status")
        status = "IMPLEMENTED_UNVERIFIED"
    level = STATUSES.index(status)

    classification = data.get("classification", {})
    migrated = data.get("migration", {}).get("source_schema_version") == LEGACY_SCHEMA_VERSION
    for key, allowed in (("project_mode", PROJECT_MODES), ("reference_mode", REFERENCE_MODES), ("change_scope", CHANGE_SCOPES)):
        if classification.get(key) not in allowed:
            errors.append(f"classification.{key} is invalid")
    primary = classification.get("primary_experience_archetype")
    if primary not in ARCHETYPES and not (migrated and primary == ""):
        errors.append("classification.primary_experience_archetype is invalid")
    secondary = classification.get("secondary_experience_archetype", "")
    if secondary and (secondary not in ARCHETYPES or secondary == primary):
        errors.append("classification.secondary_experience_archetype is invalid")
    surfaces = classification.get("surface_types")
    if (not surfaces and not migrated) or not isinstance(surfaces, list) or any(item not in SURFACE_TYPES for item in surfaces):
        errors.append("classification.surface_types must contain supported values")
    if not isinstance(classification.get("rationale"), str) or (not classification.get("rationale", "").strip() and not migrated):
        errors.append("classification.rationale must be non-empty")

    product = data.get("contract", {}).get("product", {})
    for key in ("target_user", "primary_job", "primary_success_outcome", "primary_cta"):
        if not isinstance(product.get(key), str) or not product.get(key, "").strip():
            errors.append(f"contract.product.{key} must be non-empty")

    dimensions = data.get("verification_dimensions", {})
    for key in DIMENSIONS:
        item = dimensions.get(key)
        if not isinstance(item, dict):
            errors.append(f"verification_dimensions.{key} must be an object")
            continue
        if item.get("result") not in RESULTS:
            errors.append(f"verification_dimensions.{key}.result is invalid")
        if item.get("method") not in METHODS:
            errors.append(f"verification_dimensions.{key}.method is invalid")
        if not isinstance(item.get("coverage"), str) or not item.get("coverage", "").strip():
            errors.append(f"verification_dimensions.{key}.coverage must be non-empty")
        for field in ("evidence", "issues", "limitations"):
            if not isinstance(item.get(field), list):
                errors.append(f"verification_dimensions.{key}.{field} must be a list")
        if item.get("result") in {"pass", "pass_with_limitations"} and not item.get("evidence") and key in {"render", "flow", "keyboard", "focus", "automated_accessibility"} and not migrated:
            errors.append(f"verification_dimensions.{key}.evidence is required for {item.get('result')}")

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

    policy = data.get("execution_policy", {})
    if policy.get("repository_read") != "allowed":
        errors.append("execution_policy.repository_read must be allowed")
    for key in ("project_command_execution", "dependency_installation", "active_browser", "networked_commands", "destructive_operations"):
        if policy.get(key) not in EXECUTION_VALUES:
            errors.append(f"execution_policy.{key} is invalid")
    if policy.get("approval_source") not in {"explicit_user_request", "none"}:
        errors.append("execution_policy.approval_source is invalid")
    if policy.get("project_command_execution") == "approved" and policy.get("approval_source") != "explicit_user_request":
        errors.append("approved project commands require explicit_user_request")
    if level >= 1 and policy.get("active_browser") != "approved" and not migrated:
        errors.append("verified browser status requires execution_policy.active_browser=approved")

    loading = data.get("loading_experience")
    if not isinstance(loading, dict):
        errors.append("loading_experience must be an object")
    else:
        applicable, boundaries = loading.get("applicable"), loading.get("boundaries")
        if not isinstance(applicable, bool):
            errors.append("loading_experience.applicable must be a boolean")
        if not isinstance(boundaries, list):
            errors.append("loading_experience.boundaries must be a list")
        elif applicable and not boundaries:
            errors.append("loading_experience.boundaries must describe every asynchronous boundary")
        elif applicable:
            for index, boundary in enumerate(boundaries):
                if not isinstance(boundary, dict):
                    errors.append(f"loading_experience.boundaries[{index}] must be an object")
                    continue
                for key in LOADING_BOUNDARY_FIELDS:
                    if not isinstance(boundary.get(key), str) or not boundary.get(key, "").strip():
                        errors.append(f"loading_experience.boundaries[{index}].{key} must be non-empty")
        elif boundaries:
            errors.append("loading_experience.boundaries must be empty when loading is not applicable")

    required_states = () if level == 0 else (("start",) if level == 1 else (("start", "terminal") if level == 2 else ("start", "terminal", "focus")))
    hashes: list[str] = []
    for viewport in ("desktop", "mobile"):
        runtime = data.get("runtime_checks", {}).get(viewport, {})
        if level >= 1:
            if runtime.get("inner_width", 0) <= 0 or runtime.get("scroll_width") != runtime.get("inner_width"):
                errors.append(f"runtime_checks.{viewport} has missing width or horizontal overflow")
            if runtime.get("console_errors") != 0:
                errors.append(f"runtime_checks.{viewport}.console_errors must be 0")
            if runtime.get("clipping_checked") is not True:
                errors.append(f"runtime_checks.{viewport}.clipping_checked must be true")
        if level >= 2:
            for key in ("primary_action_verified", "feedback_verified", "terminal_result_verified"):
                if runtime.get(key) is not True:
                    errors.append(f"runtime_checks.{viewport}.{key} must be true for {status}")
            if runtime.get("recovery_applicable") is True and runtime.get("recovery_verified") is not True:
                errors.append(f"runtime_checks.{viewport}.recovery_verified must be true when recovery is applicable")
        if level >= 3:
            for key in ("keyboard_path_verified", "focus_visible_verified", "focus_not_obscured_verified"):
                if runtime.get(key) is not True:
                    errors.append(f"runtime_checks.{viewport}.{key} must be true for {status}")
        for state in required_states:
            item = data.get("evidence", {}).get(viewport, {}).get(state, {})
            if not isinstance(item.get("observation"), str) or not item.get("observation", "").strip():
                errors.append(f"evidence.{viewport}.{state}.observation must be non-empty")
            path = safe_evidence_path(report_path, item.get("artifact", "") if isinstance(item.get("artifact"), str) else "")
            if not path or not path.is_file() or png_dimensions(path) is None:
                errors.append(f"evidence.{viewport}.{state}.artifact must be a readable in-root PNG")
            else:
                hashes.append(hashlib.sha256(path.read_bytes()).hexdigest())
    if len(hashes) != len(set(hashes)):
        errors.append("evidence artifacts must be distinct")

    def passed(name: str, methods: set[str]) -> bool:
        item = dimensions.get(name, {})
        return isinstance(item, dict) and item.get("result") in {"pass", "pass_with_limitations"} and item.get("method") in methods

    if level >= 1 and not passed("render", {"observed", "manual"}):
        errors.append("verification_dimensions.render must pass through observed or manual evidence")
    if level >= 2 and not passed("flow", {"observed", "manual"}):
        errors.append("verification_dimensions.flow must pass through observed or manual evidence")
    if level >= 3:
        if not passed("keyboard", {"observed", "manual"}):
            errors.append("verification_dimensions.keyboard must pass through observed or manual evidence")
        if not passed("focus", {"observed", "manual"}):
            errors.append("verification_dimensions.focus must pass through observed or manual evidence")
    if level >= 4:
        state_coverage = data.get("state_coverage", {})
        relevant, verified = state_coverage.get("relevant_states"), state_coverage.get("verified_states")
        if not isinstance(relevant, list) or not relevant or not isinstance(verified, list) or not set(relevant).issubset(verified):
            errors.append("state_coverage must verify every relevant state")
        if not state_coverage.get("evidence"):
            errors.append("state_coverage.evidence is required for VERIFIED_STANDARD_BASELINE")
        if not passed("automated_accessibility", {"automated"}):
            errors.append("verification_dimensions.automated_accessibility must pass with automated evidence")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Genscaff Standard report")
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
        raw = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    data, migration_notice = normalize(raw)
    errors = validate(data, args.report.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if migration_notice:
        print(migration_notice)
    print(f"COMPLETION_STATUS={data['completion_status']}")
    if data["completion_status"] == "IMPLEMENTED_UNVERIFIED":
        print("STANDARD_BROWSER_EVIDENCE_UNVERIFIED")
    print("GENSCAFF_STANDARD_REPORT_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

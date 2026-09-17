"""Profile templates, legacy migration, and Standard validation."""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path
from typing import Any
from .report_constants import (
    IMAGE_SUFFIXES,
    LEGACY_PROFILE_SCHEMA_VERSION,
    PROFILE_SCHEMA_VERSION,
    STANDARD_COMPLETION_STATUSES,
    TEMPLATE,
    VALID_PROFILES,
    VERIFICATION_DIMENSION_STATUSES,
)


def profile_template(profile: str) -> dict[str, Any]:
    if profile == "strict":
        template = copy.deepcopy(TEMPLATE)
        template["schema_version"] = PROFILE_SCHEMA_VERSION
    else:
        template = {
            "schema_version": PROFILE_SCHEMA_VERSION,
            "completion_status": "IMPLEMENTED_UNVERIFIED",
            "context": {
                "target_user": "",
                "primary_task": "",
                "success_outcome": "",
                "primary_cta": "",
                "recovery": "",
            },
            "evidence": {
                viewport: {
                    state: {"artifact": "", "observation": ""}
                    for state in ("start", "terminal", "focus")
                }
                for viewport in ("desktop", "mobile")
            },
            "verification_dimensions": {
                "render": "not_tested",
                "flow": "not_tested",
                "keyboard": "not_tested",
                "focus": "not_tested",
                "automated_accessibility": "not_tested",
                "assistive_technology_user_validation": "not_tested",
            },
            "checks": {
                "console_errors_clear": False,
                "overflow_clear": False,
                "accessibility_basics_checked": False,
            },
            "runtime_checks": {
                viewport: {
                    "inner_width": 0,
                    "scroll_width": 0,
                    "console_errors": 0,
                    "console_warnings": 0,
                    "primary_action_verified": False,
                    "recovery_verified": False,
                    "keyboard_path_verified": False,
                    "focus_visible_verified": False,
                    "focus_not_obscured_verified": False,
                }
                for viewport in ("desktop", "mobile")
            },
            "interaction_cost": {
                "required_decisions": 0,
                "actions_to_primary_success": 0,
                "default_selection_rationale": "",
                "fabricated_friction": [],
            },
            "skipped_checks": [],
        }
    template["profile"] = profile
    template["visual_policy"] = {
        "mode": "preserve-user-project",
        "detected_effects": [],
        "allowed_effects": [],
    }
    template["execution_policy"] = {
        "mode": "none",
        "approved_commands": [],
        "active_browser": "none",
    }
    return template


def validate_profile_envelope(data: dict[str, Any], errors: list[str]) -> None:
    profile = data.get("profile")
    if profile not in VALID_PROFILES:
        errors.append(f"profile must be one of {sorted(VALID_PROFILES)}")

    visual_policy = data.get("visual_policy")
    if not isinstance(visual_policy, dict):
        errors.append("visual_policy must be an object")
    else:
        if visual_policy.get("mode") != "preserve-user-project":
            errors.append("visual_policy.mode must be preserve-user-project")
        for field in ("detected_effects", "allowed_effects"):
            if not isinstance(visual_policy.get(field), list):
                errors.append(f"visual_policy.{field} must be a list")

    execution_policy = data.get("execution_policy")
    if not isinstance(execution_policy, dict):
        errors.append("execution_policy must be an object")
    else:
        if execution_policy.get("mode") not in {"none", "approved"}:
            errors.append("execution_policy.mode must be none or approved")
        if execution_policy.get("active_browser") not in {"none", "approved"}:
            errors.append("execution_policy.active_browser must be none or approved")
        approved = execution_policy.get("approved_commands")
        if not isinstance(approved, list) or not all(isinstance(item, str) for item in approved):
            errors.append("execution_policy.approved_commands must be a string list")
        elif execution_policy.get("mode") == "none" and approved:
            errors.append("execution_policy.approved_commands must be empty when mode is none")


def _upgrade_v4_standard(data: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    upgraded = copy.deepcopy(data)
    downgraded = upgraded.get("completion_status") == "VERIFIED_STANDARD"
    upgraded["schema_version"] = PROFILE_SCHEMA_VERSION
    if downgraded:
        upgraded["completion_status"] = "VERIFIED_FLOW"
    upgraded.setdefault(
        "verification_dimensions",
        {
            "render": "observed" if downgraded else "not_tested",
            "flow": "observed" if downgraded else "not_tested",
            "keyboard": "static_only" if downgraded else "not_tested",
            "focus": "static_only" if downgraded else "not_tested",
            "automated_accessibility": "not_tested",
            "assistive_technology_user_validation": "not_tested",
        },
    )
    upgraded.setdefault(
        "interaction_cost",
        {
            "required_decisions": 0,
            "actions_to_primary_success": 0,
            "default_selection_rationale": "legacy schema v4 report",
            "fabricated_friction": [],
        },
    )
    for viewport in ("desktop", "mobile"):
        checks = upgraded.get("runtime_checks", {}).get(viewport)
        if isinstance(checks, dict):
            checks.setdefault("keyboard_path_verified", False)
            checks.setdefault("focus_visible_verified", False)
            checks.setdefault("focus_not_obscured_verified", False)
    return upgraded, downgraded


def effective_standard_status(data: dict[str, Any]) -> tuple[str, bool]:
    status = data.get("completion_status", "IMPLEMENTED_UNVERIFIED")
    downgraded = (
        data.get("schema_version") == LEGACY_PROFILE_SCHEMA_VERSION
        and status == "VERIFIED_STANDARD"
    )
    return ("VERIFIED_FLOW" if downgraded else status, downgraded)


def validate_standard(data: dict[str, Any], report_path: Path, errors: list[str]) -> None:
    completion_status = data.get("completion_status", "IMPLEMENTED_UNVERIFIED")
    if completion_status not in STANDARD_COMPLETION_STATUSES:
        errors.append(
            "completion_status must be IMPLEMENTED_UNVERIFIED, VERIFIED_RENDER, "
            "VERIFIED_FLOW, or VERIFIED_STANDARD"
        )

    dimensions = data.get("verification_dimensions")
    if not isinstance(dimensions, dict):
        errors.append("verification_dimensions must be an object")
        dimensions = {}
    else:
        for field in (
            "render",
            "flow",
            "keyboard",
            "focus",
            "automated_accessibility",
            "assistive_technology_user_validation",
        ):
            if dimensions.get(field) not in VERIFICATION_DIMENSION_STATUSES:
                errors.append(
                    f"verification_dimensions.{field} must be one of "
                    f"{sorted(VERIFICATION_DIMENSION_STATUSES)}"
                )

    interaction_cost = data.get("interaction_cost")
    if not isinstance(interaction_cost, dict):
        errors.append("interaction_cost must be an object")
    else:
        for field in ("required_decisions", "actions_to_primary_success"):
            value = interaction_cost.get(field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                errors.append(f"interaction_cost.{field} must be a non-negative integer")
        rationale = interaction_cost.get("default_selection_rationale")
        if not isinstance(rationale, str):
            errors.append("interaction_cost.default_selection_rationale must be a string")
        friction = interaction_cost.get("fabricated_friction")
        if not isinstance(friction, list) or not all(isinstance(item, str) for item in friction):
            errors.append("interaction_cost.fabricated_friction must be a string list")
        elif friction:
            errors.append("FABRICATED_FRICTION: fabricated_friction must be empty")

    context = data.get("context")
    if not isinstance(context, dict):
        errors.append("context must be an object")
    else:
        for field in ("target_user", "primary_task", "success_outcome", "primary_cta", "recovery"):
            value = context.get(field)
            if not isinstance(value, str) or len(value.strip()) < 4:
                errors.append(f"context.{field} is required for Standard")

    evidence = data.get("evidence")
    artifact_fingerprints: list[str] = []
    required_states: tuple[str, ...] = ()
    if completion_status == "VERIFIED_RENDER":
        required_states = ("start",)
    elif completion_status == "VERIFIED_FLOW":
        required_states = ("start", "terminal")
    elif completion_status == "VERIFIED_STANDARD":
        required_states = ("start", "terminal", "focus")

    if required_states and not isinstance(evidence, dict):
        errors.append(f"evidence must be an object for {completion_status}")
    elif required_states:
        for viewport in ("desktop", "mobile"):
            states = evidence.get(viewport)
            if not isinstance(states, dict):
                errors.append(f"evidence.{viewport} must be an object")
                continue
            for state in required_states:
                item = states.get(state)
                path = f"evidence.{viewport}.{state}"
                if not isinstance(item, dict):
                    errors.append(f"{path} must be an object")
                    continue
                artifact = item.get("artifact")
                observation = item.get("observation")
                if not isinstance(artifact, str) or not artifact.strip():
                    errors.append(f"{path}.artifact is required")
                else:
                    candidate = Path(artifact).expanduser()
                    if not candidate.is_absolute():
                        candidate = report_path.resolve().parent / candidate
                    if not candidate.is_file() or candidate.suffix.casefold() not in IMAGE_SUFFIXES:
                        errors.append(f"{path}.artifact must be a local screenshot")
                    else:
                        artifact_fingerprints.append(hashlib.sha256(candidate.read_bytes()).hexdigest())
                if not isinstance(observation, str) or len(observation.strip()) < 8:
                    errors.append(f"{path}.observation must describe visible evidence")

        expected_artifacts = len(required_states) * 2
        if (
            len(artifact_fingerprints) == expected_artifacts
            and len(set(artifact_fingerprints)) != expected_artifacts
        ):
            errors.append(
                f"{completion_status} evidence artifacts must be distinct across "
                f"desktop/mobile {'/'.join(required_states)}"
            )

    checks = data.get("checks")
    if required_states and not isinstance(checks, dict):
        errors.append(f"checks must be an object for {completion_status}")
    elif required_states:
        required_checks = ["console_errors_clear", "overflow_clear"]
        if completion_status == "VERIFIED_STANDARD":
            required_checks.append("accessibility_basics_checked")
        for field in required_checks:
            if checks.get(field) is not True:
                errors.append(f"checks.{field} must be true")

    if completion_status in {"VERIFIED_RENDER", "VERIFIED_FLOW", "VERIFIED_STANDARD"}:
        if dimensions.get("render") != "observed":
            errors.append("verification_dimensions.render must be observed")
        if completion_status in {"VERIFIED_FLOW", "VERIFIED_STANDARD"} and dimensions.get("flow") != "observed":
            errors.append("verification_dimensions.flow must be observed")
        if completion_status == "VERIFIED_STANDARD":
            for field in ("keyboard", "focus"):
                if dimensions.get(field) != "observed":
                    errors.append(f"verification_dimensions.{field} must be observed")

        runtime_checks = data.get("runtime_checks")
        if not isinstance(runtime_checks, dict):
            errors.append(f"runtime_checks must be an object for {completion_status}")
        else:
            for viewport in ("desktop", "mobile"):
                item = runtime_checks.get(viewport)
                path = f"runtime_checks.{viewport}"
                if not isinstance(item, dict):
                    errors.append(f"{path} must be an object")
                    continue
                inner_width = item.get("inner_width")
                scroll_width = item.get("scroll_width")
                if (
                    isinstance(inner_width, bool)
                    or not isinstance(inner_width, int)
                    or inner_width <= 0
                ):
                    errors.append(f"{path}.inner_width must be a positive integer")
                if (
                    isinstance(scroll_width, bool)
                    or not isinstance(scroll_width, int)
                    or scroll_width <= 0
                ):
                    errors.append(f"{path}.scroll_width must be a positive integer")
                elif isinstance(inner_width, int) and not isinstance(inner_width, bool) and scroll_width > inner_width:
                    errors.append(f"{path}.scroll_width must not exceed inner_width")
                for field in ("console_errors", "console_warnings"):
                    value = item.get(field)
                    if isinstance(value, bool) or not isinstance(value, int) or value != 0:
                        errors.append(f"{path}.{field} must be 0 for {completion_status}")
                if completion_status in {"VERIFIED_FLOW", "VERIFIED_STANDARD"}:
                    for field in ("primary_action_verified", "recovery_verified"):
                        if item.get(field) is not True:
                            errors.append(f"{path}.{field} must be true for {completion_status}")
                if completion_status == "VERIFIED_STANDARD":
                    for field in (
                        "keyboard_path_verified",
                        "focus_visible_verified",
                        "focus_not_obscured_verified",
                    ):
                        if item.get(field) is not True:
                            errors.append(f"{path}.{field} must be true for VERIFIED_STANDARD")
    if not isinstance(data.get("skipped_checks"), list):
        errors.append("skipped_checks must be a list")


def validate_visual_policy(data: dict[str, Any], errors: list[str]) -> None:
    policy = data.get("visual_policy")
    if not isinstance(policy, dict):
        return
    detected = policy.get("detected_effects")
    allowed = policy.get("allowed_effects")
    if not isinstance(detected, list) or not isinstance(allowed, list):
        return
    approved: set[tuple[str, str]] = set()
    for index, item in enumerate(allowed):
        path = f"visual_policy.allowed_effects[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path} must be an object")
            continue
        kind = item.get("kind")
        location = item.get("location")
        source = item.get("source")
        rationale = item.get("rationale")
        if not isinstance(kind, str) or not kind.strip():
            errors.append(f"{path}.kind is required")
        if not isinstance(location, str) or not location.strip():
            errors.append(f"{path}.location is required")
        if source not in {"user", "project", "locked-reference"}:
            errors.append(f"{path}.source must be user, project, or locked-reference")
        if not isinstance(rationale, str) or len(rationale.strip()) < 8:
            errors.append(f"{path}.rationale is required")
        if isinstance(kind, str) and isinstance(location, str):
            approved.add((kind.strip().casefold(), location.strip().casefold()))
    for index, item in enumerate(detected):
        if not isinstance(item, dict):
            errors.append(f"visual_policy.detected_effects[{index}] must be an object")
            continue
        key = (str(item.get("kind", "")).strip().casefold(), str(item.get("location", "")).strip().casefold())
        if not all(key) or key not in approved:
            errors.append(f"Strict visual effect lacks user/project justification: {key[0]} at {key[1]}")


def apply_visual_exceptions(hard_errors: list[str], data: dict[str, Any]) -> list[str]:
    policy = data.get("visual_policy")
    allowed = policy.get("allowed_effects", []) if isinstance(policy, dict) else []
    exceptions = [
        (str(item.get("kind", "")).casefold(), str(item.get("location", "")).casefold())
        for item in allowed
        if isinstance(item, dict)
    ]
    kept: list[str] = []
    for error in hard_errors:
        lowered = error.casefold()
        if any(kind and location and kind in lowered and location in lowered for kind, location in exceptions):
            continue
        kept.append(error)
    return kept

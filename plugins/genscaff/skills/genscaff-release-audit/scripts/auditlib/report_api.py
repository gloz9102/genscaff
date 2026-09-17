"""Dispatch report schemas and compose profile validation."""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any
from . import hard_api as hard_gate
from .report_constants import (
    LEGACY_PROFILE_SCHEMA_VERSION,
    PROFILE_SCHEMA_VERSION,
    SCHEMA_VERSION,
)
from .report_contract import (
    validate_context,
    validate_product_specificity,
    validate_requirement_trace,
    validate_visual_target,
)
from .report_evidence import (
    ArtifactInspector,
    validate_evidence_catalog,
)
from .report_flow import (
    validate_action_trace,
    validate_state_coverage,
    validate_task_walkthroughs,
)
from .report_profiles import (
    _upgrade_v4_standard,
    apply_visual_exceptions,
    validate_profile_envelope,
    validate_standard,
    validate_visual_policy,
)
from .report_review import (
    validate_checks,
    validate_judgment,
    validate_measurements,
    validate_target_chronology,
    validate_visual_review,
)


def _validate_strict(
    data: dict[str, Any],
    report_path: Path,
    *,
    _live_bundle_override: dict[str, Any] | None = None,
    _lighthouse_bundle_override: dict[str, Any] | None = None,
    expected_schema_version: int = SCHEMA_VERSION,
    execute_approved_commands: bool = False,
) -> list[str]:
    errors: list[str] = []
    raw_catalog = data.get("evidence_catalog")
    inspector = ArtifactInspector(
        report_path,
        raw_catalog if isinstance(raw_catalog, dict) else None,
    )

    version = data.get("schema_version")
    if version != expected_schema_version:
        errors.append(f"schema_version must be {expected_schema_version}; got {version!r}")

    validate_evidence_catalog(raw_catalog, inspector, errors)
    work_type, scope = validate_context(data, errors)
    validate_visual_target(data, work_type, inspector, errors)
    validate_requirement_trace(data, inspector, errors)
    validate_product_specificity(data, scope, inspector, errors)
    validate_action_trace(data, inspector, errors)
    validate_state_coverage(data, inspector, errors)
    validate_task_walkthroughs(data, inspector, errors)
    validate_visual_review(data, inspector, errors)
    validate_target_chronology(data, inspector, errors)
    validate_measurements(data, inspector, errors)
    validate_judgment(data, errors)
    validate_checks(data, errors)
    errors.extend(
        hard_gate.validate(
            data,
            report_path,
            _live_bundle_override=_live_bundle_override,
            _lighthouse_bundle_override=_lighthouse_bundle_override,
            execute_approved_commands=execute_approved_commands,
        )
    )
    return errors


def validate(
    data: dict[str, Any],
    report_path: Path,
    *,
    _live_bundle_override: dict[str, Any] | None = None,
    _lighthouse_bundle_override: dict[str, Any] | None = None,
    execute_approved_commands: bool = False,
) -> list[str]:
    version = data.get("schema_version")
    if version == SCHEMA_VERSION:
        return _validate_strict(
            data,
            report_path,
            _live_bundle_override=_live_bundle_override,
            _lighthouse_bundle_override=_lighthouse_bundle_override,
            execute_approved_commands=execute_approved_commands,
        )
    if version not in {LEGACY_PROFILE_SCHEMA_VERSION, PROFILE_SCHEMA_VERSION}:
        return [
            f"schema_version must be {SCHEMA_VERSION}, {LEGACY_PROFILE_SCHEMA_VERSION}, "
            f"or {PROFILE_SCHEMA_VERSION}; got {version!r}"
        ]

    errors: list[str] = []
    profile = data.get("profile")
    if profile == "standard":
        standard_data = data
        if version == LEGACY_PROFILE_SCHEMA_VERSION:
            standard_data, _ = _upgrade_v4_standard(data)
        validate_profile_envelope(standard_data, errors)
        validate_standard(standard_data, report_path, errors)
        return errors
    if profile == "strict":
        validate_profile_envelope(data, errors)
        validate_visual_policy(data, errors)
        strict_data = copy.deepcopy(data)
        strict_data["schema_version"] = version
        checks = strict_data.get("checks")
        visual_policy = data.get("visual_policy")
        allowed_effects = visual_policy.get("allowed_effects") if isinstance(visual_policy, dict) else []
        if isinstance(checks, dict) and allowed_effects:
            for key in ("no_gradient_anywhere", "no_glassmorphism_or_backdrop_blur"):
                checks[key] = True
        hard_errors = _validate_strict(
            strict_data,
            report_path,
            _live_bundle_override=_live_bundle_override,
            _lighthouse_bundle_override=_lighthouse_bundle_override,
            expected_schema_version=version,
            execute_approved_commands=execute_approved_commands,
        )
        errors.extend(apply_visual_exceptions(hard_errors, data))
    return errors

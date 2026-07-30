#!/usr/bin/env python3
"""Validate an evidence-backed frontend quality gate report."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import hard_gate


SCHEMA_VERSION = 3
PROFILE_SCHEMA_VERSION = 4
VALID_PROFILES = {"standard", "strict"}
MIN_VISUAL_ITERATIONS = 2
MIN_IMAGE_BYTES = 512
MIN_IMAGE_WIDTH = 160
MIN_IMAGE_HEIGHT = 100

VALID_WORK_TYPES = {"new", "polish", "review"}
VALID_SCOPES = {"component", "screen", "flow", "site", "design-board"}
VALID_REQUIREMENT_SOURCES = {"user", "repository", "external-research", "derived"}
VALID_REVIEWERS = {"subagent"}
VALID_INTERACTION_MODES = {"functional", "prototype"}
VALID_SEVERITIES = {"critical", "major", "minor"}
VALID_CONTROL_BEHAVIORS = {"functional", "disabled", "prototype"}
VALID_CONTROL_ROLES = {"primary", "secondary", "navigation", "filter", "tab", "form", "other"}
VALID_STATE_STATUSES = {"implemented", "not-applicable"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif"}
TARGET_SUFFIXES = {".md", ".txt", ".json"}

REQUIRED_STATE_NAMES = {"loading", "empty", "error", "disabled", "success", "long-content"}

DOMAIN_SIGNAL_MINIMUMS = {
    "component": 1,
    "screen": 3,
    "flow": 3,
    "site": 3,
    "design-board": 3,
}

LIGHTHOUSE_THRESHOLDS = {
    "performance": 80,
    "accessibility": 90,
    "best_practices": 90,
    "seo": 90,
}

PLACEHOLDER_MARKERS = (
    "path-or-url",
    "path/to/",
    "todo",
    "tbd",
    "lorem ipsum",
    "placeholder",
    "replace me",
    "replace-this",
    "example.com",
    "your path",
    "sample text",
)

TRIVIAL_TEXT = {
    "x",
    "ok",
    "pass",
    "passed",
    "done",
    "true",
    "yes",
    "checked",
    "works",
    "looks good",
    "as expected",
    "n/a",
    "na",
    "none",
    "unknown",
}

GENERIC_PRIMARY_CTAS = {
    "learn more",
    "more",
    "explore",
    "discover",
    "continue",
    "submit",
    "click here",
    "get started",
    "start",
    "begin",
}

COSMETIC_ONLY_SIGNALS = {
    "product name",
    "brand name",
    "logo",
    "color",
    "colour",
    "accent color",
    "accent colour",
    "font",
    "typography",
}

REQUIRED_CHECKS = [
    "no_placeholder_copy",
    "no_generic_ai_hero",
    "no_decorative_gradient_orbs",
    "no_unverified_fake_metrics",
    "no_nested_card_soup",
    "screen_information_density_restrained",
    "no_inconsistent_spacing",
    "no_text_overflow_or_overlap",
    "default_background_black_or_white",
    "background_variation_confirmed_or_avoided",
    "no_one_note_palette",
    "accent_colors_minimized",
    "no_default_saas_gradient",
    "no_gradient_anywhere",
    "no_glassmorphism_or_backdrop_blur",
    "no_stock_ai_imagery",
    "no_vague_aspirational_copy",
    "copy_information_density_restrained",
    "copy_length_restrained",
    "no_polished_but_empty_sections",
    "no_unnecessary_badges_or_titles",
    "no_hallucinated_or_unverifiable_claims",
    "tokens_or_local_theme_used",
    "semantic_color_tokens_defined",
    "color_roles_tokenized_before_use",
    "expanded_brief_drives_implementation",
    "explicit_user_constraints_preserved",
    "domain_specific_screens_or_sections_defined",
    "shared_components_defined",
    "layout_board_or_page_structure_defined",
    "no_raw_visual_values_when_tokens_exist",
    "spacing_4px_scale_used",
    "type_scale_limited",
    "radius_and_shadow_levels_limited",
    "border_usage_minimized",
    "border_usage_not_overused",
    "border_radius_minimized",
    "border_radius_not_overused",
    "box_shadow_not_overused",
    "borders_and_shadows_restrained",
    "list_item_borders_and_shadows_minimized",
    "semantic_color_roles_used",
    "von_restorff_emphasis_used_deliberately",
    "single_primary_action_per_area",
    "hover_focus_active_disabled_states",
    "loading_empty_error_extreme_states_considered",
    "motion_constraints_respected",
    "touch_targets_and_semantics_checked",
    "responsive_layout_verified",
    "word_break_and_wrapping_verified",
    "interactive_states_present",
    "assets_render_correctly",
    "accessibility_basics_pass",
    "brand_reference_principles_applied",
    "visual_target_matches_result",
    "slop_checklist_compared_visually",
    "user_need_traced_to_ui",
    "product_specificity_verified",
    "domain_objects_and_language_visible",
    "differentiating_decision_present",
    "two_domain_substitution_test_failed",
    "primary_action_information_scent_clear",
    "primary_action_end_to_end_verified",
    "primary_action_feedback_and_terminal_state_present",
    "primary_action_recovery_present",
    "no_undisclosed_dead_end_controls",
    "task_walkthroughs_recorded",
    "requirements_traceable_to_evidence",
    "evidence_artifacts_verified",
    "independent_product_and_action_judgment_recorded",
    "lighthouse_treated_as_technical_floor",
]


def evidence_template() -> dict[str, str]:
    return {"artifact": "", "region": "", "observation": ""}


TEMPLATE = {
    "schema_version": SCHEMA_VERSION,
    "evidence_catalog": {
        "desktop-primary": evidence_template(),
        "desktop-feedback": evidence_template(),
        "desktop-terminal": evidence_template(),
        "desktop-recovery": evidence_template(),
        "mobile-primary": evidence_template(),
        "mobile-feedback": evidence_template(),
        "mobile-terminal": evidence_template(),
        "mobile-recovery": evidence_template(),
        "long-content": evidence_template(),
        "iteration-1": evidence_template(),
        "iteration-2": evidence_template(),
        "independent-review": evidence_template(),
    },
    "context": {
        "work_type": "new",
        "scope": "screen",
        "product_name": "",
        "product_type": "",
        "target_user": "",
        "user_need": "",
        "primary_task": "",
        "success_outcome": "",
        "primary_cta": "",
        "constraints": [],
        "differentiators": [],
        "domain_objects": [],
        "task_traits": [],
        "assumptions": [],
    },
    "implementation_audit": {
        "project_root": "",
        "source_roots": [],
        "rendered_roots": [],
        "source_fingerprint": "",
        "live_audit_config": "",
        "capture_manifest": "",
        "runtime_style_manifests": [],
        "control_manifests": [],
        "content_manifest": "",
    },
    "visual_target": {
        "created_before_coding": False,
        "expanded_design_brief_created": False,
        "artifact": "",
        "created_at": "",
        "baseline_context": "",
        "brief_summary": "",
        "summary": "",
        "direction_options": [
            {"name": "", "product_fit": "", "tradeoff": ""},
            {"name": "", "product_fit": "", "tradeoff": ""},
        ],
        "selected_direction": "",
        "selection_rationale": "",
        "benchmark_principles": [
            {
                "source": "",
                "principle": "",
                "relevance": "",
                "application": "",
                "non_copy_boundary": "",
            }
        ],
        "risk_hypotheses": [],
        "primary_cta": "",
        "token_strategy": "",
    },
    "requirement_trace": [
        {
            "id": "primary-task",
            "requirement": "",
            "source": "user",
            "implementation": "",
            "status": "unverified",
            "evidence": ["desktop-primary"],
        },
        {
            "id": "primary-cta",
            "requirement": "",
            "source": "user",
            "implementation": "",
            "status": "unverified",
            "evidence": ["desktop-primary"],
        },
    ],
    "product_specificity": {
        "domain_signals": [
            {
                "element": "",
                "selector": "",
                "domain_detail": "",
                "decision_enabled": "",
                "evidence": "desktop-primary",
            }
        ],
        "decision_points": [
            {
                "decision": "",
                "selector": "",
                "inputs": "",
                "consequence": "",
                "evidence": "desktop-primary",
            }
        ],
        "substitution_test": {
            "comparisons": [
                {"alternate_product": "", "still_fits": True, "breaking_signals": []},
                {"alternate_product": "", "still_fits": True, "breaking_signals": []},
            ],
            "verdict": "fail",
            "rationale": "",
        },
        "generic_elements_found": [],
    },
    "action_trace": {
        "interaction_mode": "functional",
        "primary": {
            "label": "",
            "location": "",
            "start_state": "",
            "information_scent": "",
            "steps": [
                {
                    "action": "",
                    "feedback": "",
                    "result": "",
                    "evidence": "desktop-terminal",
                }
            ],
            "terminal_state": "",
            "recovery_path": "",
            "checkpoints": {
                "start": "desktop-primary",
                "feedback": "desktop-feedback",
                "terminal": "desktop-terminal",
                "recovery": "desktop-recovery",
            },
            "verified": False,
        },
        "dead_end_controls": [],
        "control_inventory": [
            {
                "label": "",
                "accessible_name": "",
                "selector": "",
                "role": "primary",
                "location": "",
                "behavior": "functional",
                "result_or_prerequisite": "",
                "evidence": "desktop-primary",
            }
        ],
        "prototype_disclosure": "",
    },
    "state_coverage": [
        {
            "state": state,
            "surface": "",
            "status": "implemented" if state in {"success", "long-content"} else "not-applicable",
            "rationale": "",
            "evidence": (
                ["desktop-terminal"]
                if state == "success"
                else ["long-content"]
                if state == "long-content"
                else []
            ),
        }
        for state in sorted(REQUIRED_STATE_NAMES)
    ],
    "task_walkthroughs": [
        {
            "viewport": "desktop",
            "start_state": "",
            "steps": [
                {
                    "action": "",
                    "expected_feedback": "",
                    "observed_result": "",
                    "evidence": "desktop-primary",
                }
            ],
            "terminal_state": "",
            "failure_or_correction_path": "",
            "checkpoints": {
                "start": "desktop-primary",
                "feedback": "desktop-feedback",
                "terminal": "desktop-terminal",
                "recovery": "desktop-recovery",
            },
            "result": "fail",
            "evidence": ["desktop-terminal"],
        },
        {
            "viewport": "mobile",
            "start_state": "",
            "steps": [
                {
                    "action": "",
                    "expected_feedback": "",
                    "observed_result": "",
                    "evidence": "mobile-primary",
                }
            ],
            "terminal_state": "",
            "failure_or_correction_path": "",
            "checkpoints": {
                "start": "mobile-primary",
                "feedback": "mobile-feedback",
                "terminal": "mobile-terminal",
                "recovery": "mobile-recovery",
            },
            "result": "fail",
            "evidence": ["mobile-terminal"],
        },
    ],
    "visual_review": {
        "desktop_checked": False,
        "mobile_checked": False,
        "brand_reference_compared": False,
        "ai_slop_visual_compared": False,
        "ui_craft_compared": False,
        "comparison_notes": "",
        "screenshots": {"desktop": "", "mobile": ""},
        "console_errors": 0,
        "layout_issues_open": 0,
        "iteration_log": [
            {
                "pass": 1,
                "focus": "",
                "screenshot": "",
                "findings": [],
                "changes": [],
                "evidence": ["iteration-1"],
            },
            {
                "pass": 2,
                "focus": "",
                "screenshot": "",
                "findings": [],
                "changes": [],
                "evidence": ["iteration-2"],
            },
        ],
        "open_findings": [],
        "independent_review": {
            "performed": False,
            "reviewer": "",
            "reviewer_name": "",
            "product_specificity_verdict": "fail",
            "action_continuity_verdict": "fail",
            "findings": [],
            "notes": "",
            "review_artifact": "",
            "evidence": ["independent-review"],
        },
    },
    "measurements": {
        "lighthouse": {
            "report": "",
            "scores": {
                "performance": 0,
                "accessibility": 0,
                "best_practices": 0,
                "seo": 0,
            },
        },
        "commands": [
            {"command": "", "exit_code": 1, "result": "fail", "summary": "", "artifact": ""}
        ],
        "execution_manifest": "",
        "lighthouse_is_technical_floor": False,
    },
    "judgment": {
        "verdict": "fail",
        "product_specificity_score": 0,
        "action_continuity_score": 0,
        "visual_coherence_score": 0,
        "content_integrity_score": 0,
        "rationale": "",
        "limitations": "",
        "residual_risks": [],
    },
    "checks": {key: False for key in REQUIRED_CHECKS},
}


def fail(errors: list[str], *, max_errors: int | None = None) -> int:
    print("FAIL")
    shown = errors if max_errors is None else errors[:max_errors]
    for error in shown:
        print(f"- {error}")
    if max_errors is not None and len(errors) > max_errors:
        print(f"- ... {len(errors) - max_errors} additional error(s) omitted")
    print(f"ERROR_COUNT={len(errors)}")
    return 1


def get_path(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(path)
        current = current[part]
    return current


def normalized_text(value: str) -> str:
    return " ".join(value.casefold().split())


def parse_timestamp(value: str, path: str, errors: list[str]) -> float | None:
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        errors.append(f"{path} must be a valid ISO-8601 timestamp with timezone")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{path} must include a timezone")
        return None
    return parsed.astimezone(timezone.utc).timestamp()


def placeholder_reason(value: str) -> str | None:
    normalized = normalized_text(value)
    if normalized in TRIVIAL_TEXT:
        return "trivial self-attestation"
    for marker in PLACEHOLDER_MARKERS:
        if marker in normalized:
            return f"placeholder marker '{marker}'"
    return None


def require_text_value(
    value: Any,
    path: str,
    errors: list[str],
    *,
    minimum: int = 1,
    allow_placeholder: bool = False,
) -> str | None:
    if not isinstance(value, str):
        errors.append(f"Required text is not a string: {path}")
        return None
    stripped = value.strip()
    if len(stripped) < minimum:
        errors.append(f"Required text is too short: {path} (minimum {minimum} characters)")
        return None
    if not allow_placeholder:
        reason = placeholder_reason(stripped)
        if reason:
            errors.append(f"Invalid evidence text at {path}: {reason}")
            return None
    return stripped


def require_text(
    data: dict[str, Any], path: str, errors: list[str], *, minimum: int = 1
) -> str | None:
    try:
        value = get_path(data, path)
    except KeyError:
        errors.append(f"Missing required text: {path}")
        return None
    return require_text_value(value, path, errors, minimum=minimum)


def require_bool(data: dict[str, Any], path: str, errors: list[str], expected: bool = True) -> None:
    try:
        value = get_path(data, path)
    except KeyError:
        errors.append(f"Missing required boolean: {path}")
        return
    if value is not expected:
        errors.append(f"Required boolean must be {str(expected).lower()}: {path}")


def require_number(
    data: dict[str, Any],
    path: str,
    errors: list[str],
    *,
    minimum: float | None = None,
    maximum: float | None = None,
    integer: bool = False,
) -> float | int | None:
    try:
        value = get_path(data, path)
    except KeyError:
        errors.append(f"Missing required number: {path}")
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"Required number is not numeric: {path}")
        return None
    if not math.isfinite(float(value)):
        errors.append(f"Required number is not finite: {path}")
        return None
    if integer and not isinstance(value, int):
        errors.append(f"Required number must be an integer: {path}")
    if minimum is not None and value < minimum:
        errors.append(f"{path} must be >= {minimum}; got {value}")
    if maximum is not None and value > maximum:
        errors.append(f"{path} must be <= {maximum}; got {value}")
    return value


def require_enum(
    data: dict[str, Any], path: str, allowed: set[str], errors: list[str]
) -> str | None:
    try:
        value = get_path(data, path)
    except KeyError:
        errors.append(f"Missing required enum: {path}")
        return None
    if not isinstance(value, str) or value not in allowed:
        choices = ", ".join(sorted(allowed))
        errors.append(f"{path} must be one of [{choices}]; got {value!r}")
        return None
    return value


def require_list_value(value: Any, path: str, errors: list[str], *, minimum: int = 0) -> list[Any] | None:
    if not isinstance(value, list):
        errors.append(f"Required list is missing or invalid: {path}")
        return None
    if len(value) < minimum:
        errors.append(f"{path} must contain at least {minimum} item(s); got {len(value)}")
    return value


def require_list(data: dict[str, Any], path: str, errors: list[str], *, minimum: int = 0) -> list[Any] | None:
    try:
        value = get_path(data, path)
    except KeyError:
        errors.append(f"Missing required list: {path}")
        return None
    return require_list_value(value, path, errors, minimum=minimum)


def validate_text_list(
    value: Any,
    path: str,
    errors: list[str],
    *,
    minimum_items: int,
    minimum_length: int,
) -> list[str]:
    items = require_list_value(value, path, errors, minimum=minimum_items)
    if items is None:
        return []
    valid: list[str] = []
    for index, item in enumerate(items):
        text = require_text_value(item, f"{path}[{index}]", errors, minimum=minimum_length)
        if text is not None:
            valid.append(text)
    normalized = [normalized_text(item) for item in valid]
    if len(normalized) != len(set(normalized)):
        errors.append(f"{path} must contain unique items")
    return valid


def require_empty_list(data: dict[str, Any], path: str, errors: list[str]) -> None:
    items = require_list(data, path, errors)
    if items is not None and items:
        errors.append(f"{path} must be empty for PASS; got {len(items)} item(s)")


class ArtifactInspector:
    def __init__(self, report_path: Path, evidence_catalog: dict[str, Any] | None = None):
        self.base_dir = report_path.resolve().parent
        self.file_cache: dict[Path, tuple[int, str]] = {}
        self.image_cache: dict[Path, tuple[int, int, str]] = {}
        self.evidence_catalog = evidence_catalog or {}

    def resolve(self, value: str) -> Path:
        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            candidate = self.base_dir / candidate
        return candidate.resolve()

    def inspect_file(
        self,
        value: Any,
        path: str,
        errors: list[str],
        *,
        allowed_suffixes: set[str] | None = None,
        minimum_bytes: int = 1,
    ) -> Path | None:
        text = require_text_value(value, path, errors, minimum=3)
        if text is None:
            return None
        if text.startswith(("http://", "https://")):
            errors.append(f"Remote artifact is not independently verifiable: {path}")
            return None
        candidate = self.resolve(text)
        if not candidate.is_file():
            errors.append(f"Artifact does not exist or is not a file: {path} -> {candidate}")
            return None
        if allowed_suffixes and candidate.suffix.casefold() not in allowed_suffixes:
            errors.append(
                f"Artifact has unsupported extension at {path}: {candidate.suffix or '<none>'}"
            )
            return None
        size = candidate.stat().st_size
        if size < minimum_bytes:
            errors.append(f"Artifact is too small at {path}: {size} bytes")
            return None
        if candidate not in self.file_cache:
            digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
            self.file_cache[candidate] = (size, digest)
        return candidate

    def inspect_image(self, value: Any, path: str, errors: list[str]) -> Path | None:
        candidate = self.inspect_file(
            value,
            path,
            errors,
            allowed_suffixes=IMAGE_SUFFIXES,
            minimum_bytes=MIN_IMAGE_BYTES,
        )
        if candidate is None:
            return None
        if candidate not in self.image_cache:
            dimensions = image_dimensions(candidate)
            if dimensions is None:
                errors.append(f"Artifact is not a supported image: {path} -> {candidate}")
                return None
            width, height = dimensions
            digest = self.file_cache[candidate][1]
            self.image_cache[candidate] = (width, height, digest)
        width, height, _ = self.image_cache[candidate]
        if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
            errors.append(
                f"Image dimensions are too small at {path}: {width}x{height}; "
                f"minimum {MIN_IMAGE_WIDTH}x{MIN_IMAGE_HEIGHT}"
            )
        return candidate

    def image_digest(self, candidate: Path) -> str:
        return self.image_cache[candidate][2]


def image_dimensions(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as stream:
        header = stream.read(24)
        if header.startswith(b"\x89PNG\r\n\x1a\n") and len(header) >= 24:
            return struct.unpack(">II", header[16:24])
        if header[:6] in (b"GIF87a", b"GIF89a") and len(header) >= 10:
            return struct.unpack("<HH", header[6:10])
        if header[:2] != b"\xff\xd8":
            return None

        stream.seek(2)
        while True:
            byte = stream.read(1)
            if not byte:
                return None
            if byte != b"\xff":
                continue
            marker = stream.read(1)
            while marker == b"\xff":
                marker = stream.read(1)
            if not marker:
                return None
            marker_value = marker[0]
            if marker_value in {0xD8, 0xD9}:
                continue
            length_bytes = stream.read(2)
            if len(length_bytes) != 2:
                return None
            segment_length = struct.unpack(">H", length_bytes)[0]
            if segment_length < 2:
                return None
            if marker_value in {
                0xC0,
                0xC1,
                0xC2,
                0xC3,
                0xC5,
                0xC6,
                0xC7,
                0xC9,
                0xCA,
                0xCB,
                0xCD,
                0xCE,
                0xCF,
            }:
                payload = stream.read(5)
                if len(payload) != 5:
                    return None
                height, width = struct.unpack(">HH", payload[1:5])
                return width, height
            stream.seek(segment_length - 2, 1)


def validate_inline_evidence(
    value: Any,
    path: str,
    inspector: ArtifactInspector,
    errors: list[str],
) -> None:
    if not isinstance(value, dict):
        errors.append(f"Evidence must be an object: {path}")
        return
    inspector.inspect_image(value.get("artifact"), f"{path}.artifact", errors)
    require_text_value(value.get("region"), f"{path}.region", errors, minimum=12)
    require_text_value(value.get("observation"), f"{path}.observation", errors, minimum=30)


def validate_evidence_catalog(
    value: Any,
    inspector: ArtifactInspector,
    errors: list[str],
) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        errors.append("evidence_catalog must be an object when provided")
        return
    for evidence_id, item in value.items():
        require_text_value(evidence_id, f"evidence_catalog key {evidence_id!r}", errors, minimum=3)
        validate_inline_evidence(item, f"evidence_catalog.{evidence_id}", inspector, errors)


def validate_evidence(
    value: Any,
    path: str,
    inspector: ArtifactInspector,
    errors: list[str],
) -> None:
    if isinstance(value, str):
        evidence_id = require_text_value(value, path, errors, minimum=3)
        if evidence_id is not None and evidence_id not in inspector.evidence_catalog:
            errors.append(f"Unknown evidence reference at {path}: {evidence_id!r}")
        return
    validate_inline_evidence(value, path, inspector, errors)


def validate_evidence_list(
    value: Any,
    path: str,
    inspector: ArtifactInspector,
    errors: list[str],
    *,
    minimum: int = 1,
) -> None:
    items = require_list_value(value, path, errors, minimum=minimum)
    if items is None:
        return
    for index, item in enumerate(items):
        validate_evidence(item, f"{path}[{index}]", inspector, errors)


def validate_context(data: dict[str, Any], errors: list[str]) -> tuple[str | None, str | None]:
    work_type = require_enum(data, "context.work_type", VALID_WORK_TYPES, errors)
    scope = require_enum(data, "context.scope", VALID_SCOPES, errors)
    require_text(data, "context.product_name", errors, minimum=2)
    require_text(data, "context.product_type", errors, minimum=4)
    require_text(data, "context.target_user", errors, minimum=12)
    require_text(data, "context.user_need", errors, minimum=24)
    require_text(data, "context.primary_task", errors, minimum=18)
    require_text(data, "context.success_outcome", errors, minimum=18)
    cta = require_text(data, "context.primary_cta", errors, minimum=3)
    if cta and normalized_text(cta) in GENERIC_PRIMARY_CTAS:
        errors.append(
            "context.primary_cta is context-free and has weak information scent; "
            "use a concrete verb and object"
        )

    try:
        context = get_path(data, "context")
    except KeyError:
        return work_type, scope
    if not isinstance(context, dict):
        errors.append("Missing required object: context")
        return work_type, scope

    validate_text_list(
        context.get("constraints"),
        "context.constraints",
        errors,
        minimum_items=1,
        minimum_length=12,
    )
    validate_text_list(
        context.get("differentiators"),
        "context.differentiators",
        errors,
        minimum_items=2,
        minimum_length=18,
    )
    minimum_objects = DOMAIN_SIGNAL_MINIMUMS.get(scope or "screen", 3)
    validate_text_list(
        context.get("domain_objects"),
        "context.domain_objects",
        errors,
        minimum_items=minimum_objects,
        minimum_length=3,
    )
    validate_text_list(
        context.get("assumptions"),
        "context.assumptions",
        errors,
        minimum_items=0,
        minimum_length=15,
    )
    return work_type, scope


def validate_visual_target(
    data: dict[str, Any],
    work_type: str | None,
    inspector: ArtifactInspector,
    errors: list[str],
) -> None:
    require_bool(data, "visual_target.created_before_coding", errors)
    require_bool(data, "visual_target.expanded_design_brief_created", errors)
    inspector.inspect_file(
        get_path_or_none(data, "visual_target.artifact"),
        "visual_target.artifact",
        errors,
        allowed_suffixes=TARGET_SUFFIXES,
        minimum_bytes=100,
    )
    created_at = require_text(data, "visual_target.created_at", errors, minimum=20)
    if created_at:
        parsed = parse_timestamp(created_at, "visual_target.created_at", errors)
        if parsed and parsed > datetime.now(timezone.utc).timestamp() + 300:
            errors.append("visual_target.created_at cannot be in the future")
    require_text(data, "visual_target.baseline_context", errors, minimum=45)
    require_text(data, "visual_target.brief_summary", errors, minimum=50)
    require_text(data, "visual_target.summary", errors, minimum=40)
    selected = require_text(data, "visual_target.selected_direction", errors, minimum=4)
    require_text(data, "visual_target.selection_rationale", errors, minimum=60)
    target_cta = require_text(data, "visual_target.primary_cta", errors, minimum=3)
    context_cta = require_text(data, "context.primary_cta", errors, minimum=3)
    if target_cta and context_cta and normalized_text(target_cta) != normalized_text(context_cta):
        errors.append("visual_target.primary_cta must match context.primary_cta")
    require_text(data, "visual_target.token_strategy", errors, minimum=35)

    minimum_directions = 2 if work_type == "new" else 1
    options = require_list(data, "visual_target.direction_options", errors, minimum=minimum_directions)
    names: list[str] = []
    if options is not None:
        for index, option in enumerate(options):
            path = f"visual_target.direction_options[{index}]"
            if not isinstance(option, dict):
                errors.append(f"Direction option must be an object: {path}")
                continue
            name = require_text_value(option.get("name"), f"{path}.name", errors, minimum=4)
            require_text_value(option.get("product_fit"), f"{path}.product_fit", errors, minimum=35)
            require_text_value(option.get("tradeoff"), f"{path}.tradeoff", errors, minimum=25)
            if name:
                names.append(name)
    if len({normalized_text(name) for name in names}) != len(names):
        errors.append("visual_target.direction_options names must be unique")
    if selected and names and normalized_text(selected) not in {normalized_text(name) for name in names}:
        errors.append("visual_target.selected_direction must match a direction option name")

    principles = require_list(data, "visual_target.benchmark_principles", errors, minimum=1)
    if principles is not None:
        for index, principle in enumerate(principles):
            path = f"visual_target.benchmark_principles[{index}]"
            if not isinstance(principle, dict):
                errors.append(f"Benchmark principle must be an object: {path}")
                continue
            require_text_value(principle.get("source"), f"{path}.source", errors, minimum=5)
            require_text_value(principle.get("principle"), f"{path}.principle", errors, minimum=25)
            require_text_value(principle.get("relevance"), f"{path}.relevance", errors, minimum=30)
            require_text_value(principle.get("application"), f"{path}.application", errors, minimum=30)
            require_text_value(
                principle.get("non_copy_boundary"),
                f"{path}.non_copy_boundary",
                errors,
                minimum=20,
            )

    risks = require_list(data, "visual_target.risk_hypotheses", errors, minimum=3)
    if risks is not None:
        validate_text_list(
            risks,
            "visual_target.risk_hypotheses",
            errors,
            minimum_items=3,
            minimum_length=20,
        )


def validate_requirement_trace(
    data: dict[str, Any], inspector: ArtifactInspector, errors: list[str]
) -> None:
    traces = require_list(data, "requirement_trace", errors, minimum=2)
    if traces is None:
        return
    ids: list[str] = []
    for index, trace in enumerate(traces):
        path = f"requirement_trace[{index}]"
        if not isinstance(trace, dict):
            errors.append(f"Requirement trace must be an object: {path}")
            continue
        trace_id = require_text_value(trace.get("id"), f"{path}.id", errors, minimum=3)
        require_text_value(trace.get("requirement"), f"{path}.requirement", errors, minimum=20)
        source = trace.get("source")
        if source not in VALID_REQUIREMENT_SOURCES:
            errors.append(f"{path}.source must be one of {sorted(VALID_REQUIREMENT_SOURCES)}")
        require_text_value(trace.get("implementation"), f"{path}.implementation", errors, minimum=25)
        if trace.get("status") != "verified":
            errors.append(f"{path}.status must be 'verified'")
        validate_evidence_list(trace.get("evidence"), f"{path}.evidence", inspector, errors)
        if trace_id:
            ids.append(trace_id)

    normalized_ids = [normalized_text(item) for item in ids]
    if len(normalized_ids) != len(set(normalized_ids)):
        errors.append("requirement_trace ids must be unique")
    for required_id in ("primary-task", "primary-cta"):
        if required_id not in normalized_ids:
            errors.append(f"requirement_trace must include id '{required_id}'")

    constraints = require_list(data, "context.constraints", errors) or []
    constraint_ids = [item for item in normalized_ids if item.startswith("constraint-")]
    if len(constraint_ids) < len(constraints):
        errors.append(
            "requirement_trace must include one 'constraint-*' entry for every context constraint"
        )
    differentiator_ids = [item for item in normalized_ids if item.startswith("differentiator-")]
    if len(differentiator_ids) < 2:
        errors.append("requirement_trace must include at least two 'differentiator-*' entries")


def validate_product_specificity(
    data: dict[str, Any], scope: str | None, inspector: ArtifactInspector, errors: list[str]
) -> None:
    minimum_signals = DOMAIN_SIGNAL_MINIMUMS.get(scope or "screen", 3)
    signals = require_list(
        data, "product_specificity.domain_signals", errors, minimum=minimum_signals
    )
    signal_names: list[str] = []
    signal_selectors: list[str] = []
    if signals is not None:
        for index, signal in enumerate(signals):
            path = f"product_specificity.domain_signals[{index}]"
            if not isinstance(signal, dict):
                errors.append(f"Domain signal must be an object: {path}")
                continue
            element = require_text_value(signal.get("element"), f"{path}.element", errors, minimum=5)
            selector = require_text_value(signal.get("selector"), f"{path}.selector", errors, minimum=2)
            require_text_value(signal.get("domain_detail"), f"{path}.domain_detail", errors, minimum=25)
            require_text_value(
                signal.get("decision_enabled"), f"{path}.decision_enabled", errors, minimum=25
            )
            validate_evidence(signal.get("evidence"), f"{path}.evidence", inspector, errors)
            if element:
                signal_names.append(element)
            if selector:
                signal_selectors.append(selector.strip())
    if len({normalized_text(item) for item in signal_names}) != len(signal_names):
        errors.append("product_specificity.domain_signals elements must be unique")
    if len(signal_selectors) != len(set(signal_selectors)):
        errors.append("product_specificity.domain_signals selectors must be unique")
    for selector in signal_selectors:
        if hard_gate.selector_is_overbroad(selector):
            errors.append(f"Domain signal selector is an overbroad application container: {selector}")

    decisions = require_list(data, "product_specificity.decision_points", errors, minimum=1)
    decision_selectors: list[str] = []
    if decisions is not None:
        for index, decision in enumerate(decisions):
            path = f"product_specificity.decision_points[{index}]"
            if not isinstance(decision, dict):
                errors.append(f"Decision point must be an object: {path}")
                continue
            require_text_value(decision.get("decision"), f"{path}.decision", errors, minimum=20)
            selector = require_text_value(decision.get("selector"), f"{path}.selector", errors, minimum=2)
            require_text_value(decision.get("inputs"), f"{path}.inputs", errors, minimum=20)
            require_text_value(decision.get("consequence"), f"{path}.consequence", errors, minimum=20)
            validate_evidence(decision.get("evidence"), f"{path}.evidence", inspector, errors)
            if selector:
                decision_selectors.append(selector.strip())
    if len(decision_selectors) != len(set(decision_selectors)):
        errors.append("product_specificity.decision_points selectors must be unique")
    if set(signal_selectors) & set(decision_selectors):
        errors.append("Domain and decision evidence must use distinct selectors")
    for selector in decision_selectors:
        if hard_gate.selector_is_overbroad(selector):
            errors.append(f"Decision selector is an overbroad application container: {selector}")

    comparisons = require_list(
        data,
        "product_specificity.substitution_test.comparisons",
        errors,
        minimum=2,
    )
    alternate_products: list[str] = []
    if comparisons is not None:
        for index, comparison in enumerate(comparisons):
            path = f"product_specificity.substitution_test.comparisons[{index}]"
            if not isinstance(comparison, dict):
                errors.append(f"Substitution comparison must be an object: {path}")
                continue
            alternate = require_text_value(
                comparison.get("alternate_product"),
                f"{path}.alternate_product",
                errors,
                minimum=5,
            )
            if comparison.get("still_fits") is not False:
                errors.append(f"{path}.still_fits must be false")
            breaking = validate_text_list(
                comparison.get("breaking_signals"),
                f"{path}.breaking_signals",
                errors,
                minimum_items=2,
                minimum_length=12,
            )
            for signal in breaking:
                if normalized_text(signal) in COSMETIC_ONLY_SIGNALS:
                    errors.append(f"{path}.breaking_signals cannot rely on cosmetic identity: {signal}")
            if alternate:
                alternate_products.append(alternate)
    if len({normalized_text(item) for item in alternate_products}) != len(alternate_products):
        errors.append("Substitution alternate products must be unique")

    try:
        verdict = get_path(data, "product_specificity.substitution_test.verdict")
    except KeyError:
        errors.append("Missing substitution verdict")
    else:
        if verdict != "product-specific":
            errors.append("product_specificity.substitution_test.verdict must be 'product-specific'")
    require_text(data, "product_specificity.substitution_test.rationale", errors, minimum=70)
    require_empty_list(data, "product_specificity.generic_elements_found", errors)


def validate_action_trace(
    data: dict[str, Any], inspector: ArtifactInspector, errors: list[str]
) -> None:
    mode = require_enum(data, "action_trace.interaction_mode", VALID_INTERACTION_MODES, errors)
    label = require_text(data, "action_trace.primary.label", errors, minimum=3)
    context_cta = require_text(data, "context.primary_cta", errors, minimum=3)
    if label and context_cta and normalized_text(label) != normalized_text(context_cta):
        errors.append("action_trace.primary.label must match context.primary_cta")
    require_text(data, "action_trace.primary.location", errors, minimum=15)
    require_text(data, "action_trace.primary.start_state", errors, minimum=20)
    require_text(data, "action_trace.primary.information_scent", errors, minimum=35)
    require_text(data, "action_trace.primary.terminal_state", errors, minimum=20)
    require_text(data, "action_trace.primary.recovery_path", errors, minimum=20)
    require_bool(data, "action_trace.primary.verified", errors)

    steps = require_list(data, "action_trace.primary.steps", errors, minimum=1)
    if steps is not None:
        for index, step in enumerate(steps):
            path = f"action_trace.primary.steps[{index}]"
            if not isinstance(step, dict):
                errors.append(f"Action step must be an object: {path}")
                continue
            require_text_value(step.get("action"), f"{path}.action", errors, minimum=15)
            require_text_value(step.get("feedback"), f"{path}.feedback", errors, minimum=20)
            require_text_value(step.get("result"), f"{path}.result", errors, minimum=20)
            validate_evidence(step.get("evidence"), f"{path}.evidence", inspector, errors)

    require_empty_list(data, "action_trace.dead_end_controls", errors)
    controls = require_list(data, "action_trace.control_inventory", errors, minimum=1)
    primary_controls = 0
    primary_cta_found = False
    if controls is not None:
        seen_controls: set[tuple[str, str]] = set()
        for index, control in enumerate(controls):
            path = f"action_trace.control_inventory[{index}]"
            if not isinstance(control, dict):
                errors.append(f"Control inventory item must be an object: {path}")
                continue
            control_label = require_text_value(
                control.get("label"), f"{path}.label", errors, minimum=2
            )
            require_text_value(
                control.get("accessible_name"), f"{path}.accessible_name", errors, minimum=2
            )
            require_text_value(control.get("selector"), f"{path}.selector", errors, minimum=2)
            role = control.get("role")
            if role not in VALID_CONTROL_ROLES:
                errors.append(f"{path}.role must be one of {sorted(VALID_CONTROL_ROLES)}")
            if role == "primary":
                primary_controls += 1
            location = require_text_value(
                control.get("location"), f"{path}.location", errors, minimum=12
            )
            behavior = control.get("behavior")
            if behavior not in VALID_CONTROL_BEHAVIORS:
                errors.append(
                    f"{path}.behavior must be one of {sorted(VALID_CONTROL_BEHAVIORS)}"
                )
            require_text_value(
                control.get("result_or_prerequisite"),
                f"{path}.result_or_prerequisite",
                errors,
                minimum=20,
            )
            validate_evidence(control.get("evidence"), f"{path}.evidence", inspector, errors)
            if control_label and context_cta and normalized_text(control_label) == normalized_text(context_cta):
                primary_cta_found = True
            if control_label and location:
                key = (normalized_text(control_label), normalized_text(location))
                if key in seen_controls:
                    errors.append(f"Duplicate control inventory entry: {path}")
                seen_controls.add(key)
            if behavior == "prototype" and mode != "prototype":
                errors.append(f"{path} cannot be prototype-only when interaction_mode is functional")
    if primary_controls != 1:
        errors.append(f"action_trace.control_inventory must contain exactly one primary control; got {primary_controls}")
    if not primary_cta_found:
        errors.append("action_trace.control_inventory must include context.primary_cta")
    try:
        disclosure = get_path(data, "action_trace.prototype_disclosure")
    except KeyError:
        errors.append("Missing action_trace.prototype_disclosure")
    else:
        if not isinstance(disclosure, str):
            errors.append("action_trace.prototype_disclosure must be a string")
        elif mode == "prototype":
            require_text_value(
                disclosure,
                "action_trace.prototype_disclosure",
                errors,
                minimum=35,
            )


def validate_state_coverage(
    data: dict[str, Any], inspector: ArtifactInspector, errors: list[str]
) -> None:
    states = require_list(data, "state_coverage", errors, minimum=len(REQUIRED_STATE_NAMES))
    if states is None:
        return
    names: list[str] = []
    implemented: set[str] = set()
    for index, state in enumerate(states):
        path = f"state_coverage[{index}]"
        if not isinstance(state, dict):
            errors.append(f"State coverage entry must be an object: {path}")
            continue
        name = state.get("state")
        if name not in REQUIRED_STATE_NAMES:
            errors.append(f"{path}.state must be one of {sorted(REQUIRED_STATE_NAMES)}")
        else:
            names.append(name)
        require_text_value(state.get("surface"), f"{path}.surface", errors, minimum=8)
        status = state.get("status")
        if status not in VALID_STATE_STATUSES:
            errors.append(f"{path}.status must be one of {sorted(VALID_STATE_STATUSES)}")
        require_text_value(state.get("rationale"), f"{path}.rationale", errors, minimum=30)
        evidence = state.get("evidence")
        if status == "implemented":
            if isinstance(name, str):
                implemented.add(name)
            validate_evidence_list(evidence, f"{path}.evidence", inspector, errors, minimum=1)
        else:
            items = require_list_value(evidence, f"{path}.evidence", errors)
            if items:
                errors.append(f"{path}.evidence must be empty when status is not-applicable")
    if set(names) != REQUIRED_STATE_NAMES or len(names) != len(set(names)):
        errors.append("state_coverage must contain each required state exactly once")
    for required in ("success", "long-content"):
        if required not in implemented:
            errors.append(f"state_coverage.{required} must be implemented with evidence")


def validate_task_walkthroughs(
    data: dict[str, Any], inspector: ArtifactInspector, errors: list[str]
) -> None:
    walkthroughs = require_list(data, "task_walkthroughs", errors, minimum=2)
    if walkthroughs is None:
        return
    viewports: set[str] = set()
    for index, walkthrough in enumerate(walkthroughs):
        path = f"task_walkthroughs[{index}]"
        if not isinstance(walkthrough, dict):
            errors.append(f"Task walkthrough must be an object: {path}")
            continue
        viewport = walkthrough.get("viewport")
        if viewport not in {"desktop", "mobile"}:
            errors.append(f"{path}.viewport must be 'desktop' or 'mobile'")
        else:
            viewports.add(viewport)
        require_text_value(walkthrough.get("start_state"), f"{path}.start_state", errors, minimum=20)
        require_text_value(
            walkthrough.get("terminal_state"), f"{path}.terminal_state", errors, minimum=20
        )
        require_text_value(
            walkthrough.get("failure_or_correction_path"),
            f"{path}.failure_or_correction_path",
            errors,
            minimum=20,
        )
        if walkthrough.get("result") != "pass":
            errors.append(f"{path}.result must be 'pass'")
        steps = require_list_value(walkthrough.get("steps"), f"{path}.steps", errors, minimum=1)
        if steps is not None:
            for step_index, step in enumerate(steps):
                step_path = f"{path}.steps[{step_index}]"
                if not isinstance(step, dict):
                    errors.append(f"Walkthrough step must be an object: {step_path}")
                    continue
                require_text_value(step.get("action"), f"{step_path}.action", errors, minimum=15)
                require_text_value(
                    step.get("expected_feedback"),
                    f"{step_path}.expected_feedback",
                    errors,
                    minimum=20,
                )
                require_text_value(
                    step.get("observed_result"),
                    f"{step_path}.observed_result",
                    errors,
                    minimum=20,
                )
                validate_evidence(step.get("evidence"), f"{step_path}.evidence", inspector, errors)
        validate_evidence_list(walkthrough.get("evidence"), f"{path}.evidence", inspector, errors)
    for required in ("desktop", "mobile"):
        if required not in viewports:
            errors.append(f"task_walkthroughs must include a {required} walkthrough")


def validate_iteration_log(
    data: dict[str, Any], inspector: ArtifactInspector, errors: list[str]
) -> None:
    iterations = require_list(
        data, "visual_review.iteration_log", errors, minimum=MIN_VISUAL_ITERATIONS
    )
    if iterations is None:
        return
    total_findings = 0
    total_changes = 0
    image_digests: list[str] = []
    pass_numbers: list[int] = []
    for index, iteration in enumerate(iterations):
        path = f"visual_review.iteration_log[{index}]"
        if not isinstance(iteration, dict):
            errors.append(f"Iteration record must be an object: {path}")
            continue
        pass_number = iteration.get("pass")
        if isinstance(pass_number, bool) or not isinstance(pass_number, int):
            errors.append(f"{path}.pass must be an integer")
        else:
            pass_numbers.append(pass_number)
        require_text_value(iteration.get("focus"), f"{path}.focus", errors, minimum=25)
        screenshot = inspector.inspect_image(iteration.get("screenshot"), f"{path}.screenshot", errors)
        if screenshot is not None:
            image_digests.append(inspector.image_digest(screenshot))

        findings = require_list_value(iteration.get("findings"), f"{path}.findings", errors)
        if findings is not None:
            total_findings += len(findings)
            for finding_index, finding in enumerate(findings):
                finding_path = f"{path}.findings[{finding_index}]"
                if not isinstance(finding, dict):
                    errors.append(f"Finding must be an object: {finding_path}")
                    continue
                if finding.get("severity") not in VALID_SEVERITIES:
                    errors.append(f"{finding_path}.severity must be one of {sorted(VALID_SEVERITIES)}")
                require_text_value(
                    finding.get("symptom"), f"{finding_path}.symptom", errors, minimum=25
                )
                require_text_value(
                    finding.get("criterion"), f"{finding_path}.criterion", errors, minimum=18
                )
                validate_evidence(
                    finding.get("evidence"), f"{finding_path}.evidence", inspector, errors
                )

        changes = require_list_value(iteration.get("changes"), f"{path}.changes", errors)
        if changes is not None:
            total_changes += len(changes)
            for change_index, change in enumerate(changes):
                change_path = f"{path}.changes[{change_index}]"
                if not isinstance(change, dict):
                    errors.append(f"Change must be an object: {change_path}")
                    continue
                require_text_value(change.get("change"), f"{change_path}.change", errors, minimum=25)
                require_text_value(change.get("reason"), f"{change_path}.reason", errors, minimum=20)
                files = validate_text_list(
                    change.get("files"),
                    f"{change_path}.files",
                    errors,
                    minimum_items=1,
                    minimum_length=3,
                )
                for file_index, file_value in enumerate(files):
                    inspector.inspect_file(
                        file_value,
                        f"{change_path}.files[{file_index}]",
                        errors,
                        minimum_bytes=1,
                    )
                validate_evidence(
                    change.get("evidence"), f"{change_path}.evidence", inspector, errors
                )

        validate_evidence_list(iteration.get("evidence"), f"{path}.evidence", inspector, errors)

    expected_passes = list(range(1, len(pass_numbers) + 1))
    if pass_numbers != expected_passes:
        errors.append(
            f"visual_review.iteration_log pass numbers must be ordered {expected_passes}; "
            f"got {pass_numbers}"
        )
    if total_findings < 1:
        errors.append("visual_review.iteration_log must record at least one concrete finding")
    if total_changes < 1:
        errors.append("visual_review.iteration_log must record at least one concrete change")
    if len(image_digests) != len(set(image_digests)):
        errors.append("Each visual iteration must use a distinct screenshot artifact")


def validate_visual_review(
    data: dict[str, Any], inspector: ArtifactInspector, errors: list[str]
) -> None:
    for path in (
        "visual_review.desktop_checked",
        "visual_review.mobile_checked",
        "visual_review.brand_reference_compared",
        "visual_review.ai_slop_visual_compared",
        "visual_review.ui_craft_compared",
    ):
        require_bool(data, path, errors)
    require_text(data, "visual_review.comparison_notes", errors, minimum=100)

    desktop = inspector.inspect_image(
        get_path_or_none(data, "visual_review.screenshots.desktop"),
        "visual_review.screenshots.desktop",
        errors,
    )
    mobile = inspector.inspect_image(
        get_path_or_none(data, "visual_review.screenshots.mobile"),
        "visual_review.screenshots.mobile",
        errors,
    )
    if desktop is not None and mobile is not None:
        if desktop == mobile or inspector.image_digest(desktop) == inspector.image_digest(mobile):
            errors.append("Desktop and mobile screenshots must be different artifacts and bytes")

    console_errors = require_number(
        data,
        "visual_review.console_errors",
        errors,
        minimum=0,
        maximum=0,
        integer=True,
    )
    layout_issues = require_number(
        data,
        "visual_review.layout_issues_open",
        errors,
        minimum=0,
        maximum=0,
        integer=True,
    )
    if console_errors not in (None, 0):
        errors.append("visual_review.console_errors must be exactly 0")
    if layout_issues not in (None, 0):
        errors.append("visual_review.layout_issues_open must be exactly 0")

    validate_iteration_log(data, inspector, errors)
    require_empty_list(data, "visual_review.open_findings", errors)

    require_bool(data, "visual_review.independent_review.performed", errors)
    require_enum(data, "visual_review.independent_review.reviewer", VALID_REVIEWERS, errors)
    require_text(data, "visual_review.independent_review.reviewer_name", errors, minimum=2)
    for field in ("product_specificity_verdict", "action_continuity_verdict"):
        try:
            value = get_path(data, f"visual_review.independent_review.{field}")
        except KeyError:
            errors.append(f"Missing independent review verdict: {field}")
        else:
            if value != "pass":
                errors.append(f"visual_review.independent_review.{field} must be 'pass'")
    require_list(data, "visual_review.independent_review.findings", errors)
    require_text(data, "visual_review.independent_review.notes", errors, minimum=100)
    validate_evidence_list(
        get_path_or_none(data, "visual_review.independent_review.evidence"),
        "visual_review.independent_review.evidence",
        inspector,
        errors,
    )


def validate_target_chronology(
    data: dict[str, Any], inspector: ArtifactInspector, errors: list[str]
) -> None:
    target = inspector.inspect_file(
        get_path_or_none(data, "visual_target.artifact"),
        "visual_target.artifact",
        errors,
        allowed_suffixes=TARGET_SUFFIXES,
        minimum_bytes=100,
    )
    created_at_value = get_path_or_none(data, "visual_target.created_at")
    created_at = None
    if isinstance(created_at_value, str) and created_at_value.strip():
        created_at = parse_timestamp(created_at_value, "visual_target.created_at", errors)

    iterations = get_path_or_none(data, "visual_review.iteration_log")
    screenshots: list[Path] = []
    if isinstance(iterations, list):
        for index, iteration in enumerate(iterations):
            if not isinstance(iteration, dict):
                continue
            screenshot = inspector.inspect_image(
                iteration.get("screenshot"),
                f"visual_review.iteration_log[{index}].screenshot",
                errors,
            )
            if screenshot is not None:
                screenshots.append(screenshot)
    if not screenshots:
        return
    first_render_time = min(item.stat().st_mtime for item in screenshots)
    if target is not None and target.stat().st_mtime > first_render_time + 1:
        errors.append("visual_target.artifact must predate the first visual iteration screenshot")
    if created_at is not None and created_at > first_render_time + 300:
        errors.append("visual_target.created_at must predate the first visual iteration screenshot")


def get_path_or_none(data: dict[str, Any], path: str) -> Any:
    try:
        return get_path(data, path)
    except KeyError:
        return None


def validate_lighthouse(
    data: dict[str, Any], inspector: ArtifactInspector, errors: list[str]
) -> None:
    report_value = get_path_or_none(data, "measurements.lighthouse.report")
    report_path = inspector.inspect_file(
        report_value,
        "measurements.lighthouse.report",
        errors,
        allowed_suffixes={".json"},
        minimum_bytes=100,
    )

    reported_scores: dict[str, int] = {}
    for metric, threshold in LIGHTHOUSE_THRESHOLDS.items():
        value = require_number(
            data,
            f"measurements.lighthouse.scores.{metric}",
            errors,
            minimum=0,
            maximum=100,
            integer=True,
        )
        if isinstance(value, int) and not isinstance(value, bool):
            reported_scores[metric] = value
            if value < threshold:
                errors.append(
                    f"measurements.lighthouse.scores.{metric} must be >= {threshold}; got {value}"
                )

    if report_path is None:
        return
    try:
        lighthouse = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"Unable to parse Lighthouse JSON artifact: {exc}")
        return
    categories = lighthouse.get("categories") if isinstance(lighthouse, dict) else None
    if not isinstance(categories, dict):
        errors.append("Lighthouse JSON is missing the categories object")
        return
    for metric in LIGHTHOUSE_THRESHOLDS:
        category = categories.get(metric.replace("_", "-")) or categories.get(metric)
        score = category.get("score") if isinstance(category, dict) else None
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            errors.append(f"Lighthouse artifact is missing numeric categories.{metric}.score")
            continue
        if not math.isfinite(float(score)) or score < 0 or score > 1:
            errors.append(f"Lighthouse artifact categories.{metric}.score must be within 0..1")
            continue
        artifact_score = int(round(score * 100))
        if metric in reported_scores and reported_scores[metric] != artifact_score:
            errors.append(
                f"Reported Lighthouse {metric} score {reported_scores[metric]} does not match "
                f"artifact score {artifact_score}"
            )


def validate_measurements(
    data: dict[str, Any], inspector: ArtifactInspector, errors: list[str]
) -> None:
    validate_lighthouse(data, inspector, errors)
    commands = require_list(data, "measurements.commands", errors, minimum=1)
    if commands is not None:
        for index, command in enumerate(commands):
            path = f"measurements.commands[{index}]"
            if not isinstance(command, dict):
                errors.append(f"Command result must be an object: {path}")
                continue
            require_text_value(command.get("command"), f"{path}.command", errors, minimum=4)
            exit_code = command.get("exit_code")
            if isinstance(exit_code, bool) or not isinstance(exit_code, int) or exit_code != 0:
                errors.append(f"{path}.exit_code must be integer 0")
            if command.get("result") != "pass":
                errors.append(f"{path}.result must be 'pass'")
            require_text_value(command.get("summary"), f"{path}.summary", errors, minimum=25)
            inspector.inspect_file(
                command.get("artifact"),
                f"{path}.artifact",
                errors,
                minimum_bytes=10,
            )
    require_bool(data, "measurements.lighthouse_is_technical_floor", errors)


def validate_judgment(data: dict[str, Any], errors: list[str]) -> None:
    try:
        verdict = get_path(data, "judgment.verdict")
    except KeyError:
        errors.append("Missing judgment.verdict")
    else:
        if verdict != "pass":
            errors.append("judgment.verdict must be 'pass'")
    for field in (
        "product_specificity_score",
        "action_continuity_score",
        "visual_coherence_score",
        "content_integrity_score",
    ):
        require_number(
            data,
            f"judgment.{field}",
            errors,
            minimum=4,
            maximum=5,
            integer=True,
        )
    require_text(data, "judgment.rationale", errors, minimum=120)
    require_text(data, "judgment.limitations", errors, minimum=70)
    require_empty_list(data, "judgment.residual_risks", errors)


def validate_checks(data: dict[str, Any], errors: list[str]) -> None:
    checks = data.get("checks")
    if not isinstance(checks, dict):
        errors.append("Missing required object: checks")
        return
    for key in REQUIRED_CHECKS:
        if checks.get(key) is not True:
            errors.append(f"Required check failed or missing: checks.{key}")


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


def profile_template(profile: str) -> dict[str, Any]:
    if profile == "strict":
        template = copy.deepcopy(TEMPLATE)
        template["schema_version"] = PROFILE_SCHEMA_VERSION
    else:
        template = {
            "schema_version": PROFILE_SCHEMA_VERSION,
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
                    for state in ("start", "terminal")
                }
                for viewport in ("desktop", "mobile")
            },
            "checks": {
                "console_errors_clear": False,
                "overflow_clear": False,
                "keyboard_focus_checked": False,
                "accessibility_basics_checked": False,
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


def validate_standard(data: dict[str, Any], report_path: Path, errors: list[str]) -> None:
    context = data.get("context")
    if not isinstance(context, dict):
        errors.append("context must be an object")
    else:
        for field in ("target_user", "primary_task", "success_outcome", "primary_cta", "recovery"):
            value = context.get(field)
            if not isinstance(value, str) or len(value.strip()) < 4:
                errors.append(f"context.{field} is required for Standard")

    evidence = data.get("evidence")
    if not isinstance(evidence, dict):
        errors.append("evidence must be an object")
    else:
        for viewport in ("desktop", "mobile"):
            states = evidence.get(viewport)
            if not isinstance(states, dict):
                errors.append(f"evidence.{viewport} must be an object")
                continue
            for state in ("start", "terminal"):
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
                if not isinstance(observation, str) or len(observation.strip()) < 8:
                    errors.append(f"{path}.observation must describe visible evidence")

    checks = data.get("checks")
    if not isinstance(checks, dict):
        errors.append("checks must be an object")
    else:
        for field in (
            "console_errors_clear",
            "overflow_clear",
            "keyboard_focus_checked",
            "accessibility_basics_checked",
        ):
            if checks.get(field) is not True:
                errors.append(f"checks.{field} must be true")
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
    if version != PROFILE_SCHEMA_VERSION:
        return [f"schema_version must be {SCHEMA_VERSION} or {PROFILE_SCHEMA_VERSION}; got {version!r}"]

    errors: list[str] = []
    validate_profile_envelope(data, errors)
    profile = data.get("profile")
    if profile == "standard":
        validate_standard(data, report_path, errors)
        return errors
    if profile == "strict":
        validate_visual_policy(data, errors)
        strict_data = copy.deepcopy(data)
        strict_data["schema_version"] = PROFILE_SCHEMA_VERSION
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
            expected_schema_version=PROFILE_SCHEMA_VERSION,
            execute_approved_commands=execute_approved_commands,
        )
        errors.extend(apply_visual_exceptions(hard_errors, data))
    return errors


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

    if args.execute_approved_commands and data.get("schema_version") == PROFILE_SCHEMA_VERSION:
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
    print("STRUCTURAL_EVIDENCE_INVARIANTS_VERIFIED")
    if profile in {"strict", "legacy-strict"}:
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
    return 0


if __name__ == "__main__":
    sys.exit(main())

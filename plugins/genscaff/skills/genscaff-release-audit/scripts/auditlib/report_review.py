"""Validate visual reviews, iterations, chronology, and measurements."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any
from .report_constants import (
    LIGHTHOUSE_THRESHOLDS,
    MIN_VISUAL_ITERATIONS,
    REQUIRED_CHECKS,
    TARGET_SUFFIXES,
    VALID_REVIEWERS,
    VALID_SEVERITIES,
)
from .report_evidence import (
    ArtifactInspector,
    validate_evidence,
    validate_evidence_list,
)
from .report_fields import (
    get_path,
    get_path_or_none,
    parse_timestamp,
    require_bool,
    require_empty_list,
    require_enum,
    require_list,
    require_list_value,
    require_number,
    require_text,
    require_text_value,
    validate_text_list,
)


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

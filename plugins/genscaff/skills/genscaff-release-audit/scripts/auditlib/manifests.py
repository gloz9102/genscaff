"""Validate capture, style, control, and content manifests."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from .files import (
    load_json_file,
    resolve_path,
)
from .hard_common import (
    CAPTURE_GENERATOR,
    CONTENT_GENERATOR,
    CONTROL_GENERATOR,
    STYLE_EMPTY_FIELDS,
    STYLE_GENERATOR,
    get_path,
    normalized,
    parse_timestamp,
    require_manifest_header,
)
from .images import (
    collect_report_images,
    decode_png,
    image_structure_metrics,
)


def validate_capture_manifest(
    data: dict[str, Any],
    base_dir: Path,
    source_fingerprint: str | None,
    errors: list[str],
) -> tuple[dict[Path, dict[str, Any]], Path | None]:
    manifest, manifest_path = load_json_file(
        get_path(data, "implementation_audit.capture_manifest"),
        base_dir,
        "implementation_audit.capture_manifest",
        errors,
    )
    if manifest is None or manifest_path is None:
        return {}, manifest_path
    require_manifest_header(manifest, CAPTURE_GENERATOR, "capture_manifest", errors)
    if source_fingerprint and manifest.get("source_fingerprint") != source_fingerprint:
        errors.append("capture_manifest.source_fingerprint does not match the scanned source tree")
    captures = manifest.get("captures")
    if not isinstance(captures, list) or len(captures) < 8:
        errors.append("capture_manifest.captures must contain at least eight browser checkpoints")
        return {}, manifest_path

    records: dict[Path, dict[str, Any]] = {}
    pixel_digests: set[str] = set()
    timestamps: list[float] = []
    for index, record in enumerate(captures):
        path = f"capture_manifest.captures[{index}]"
        if not isinstance(record, dict):
            errors.append(f"Capture must be an object: {path}")
            continue
        artifact = resolve_path(record.get("artifact"), manifest_path.parent, f"{path}.artifact", errors)
        if artifact is None or not artifact.is_file():
            errors.append(f"Capture artifact does not exist: {path}")
            continue
        if artifact.suffix.casefold() != ".png":
            errors.append(f"Capture artifact must be PNG: {path}")
            continue
        decoded = decode_png(artifact, path, errors)
        if decoded is None:
            continue
        mean_delta, color_count = image_structure_metrics(decoded)
        if mean_delta > 70:
            errors.append(
                f"Capture resembles high-frequency noise rather than a browser surface: {path} "
                f"(adjacent delta {mean_delta:.2f})"
            )
        if color_count < 4:
            errors.append(f"Capture is visually trivial or blank: {path} ({color_count} sampled colors)")
        if record.get("sha256") != decoded["file_digest"]:
            errors.append(f"Capture sha256 mismatch: {path}")
        if record.get("width") != decoded["width"] or record.get("height") != decoded["height"]:
            errors.append(f"Capture dimensions do not match PNG: {path}")
        viewport = record.get("viewport")
        if viewport not in {"desktop", "mobile"}:
            errors.append(f"{path}.viewport must be desktop or mobile")
        if viewport == "desktop" and decoded["width"] < 640:
            errors.append(f"Desktop capture is too narrow: {path}")
        if viewport == "mobile" and decoded["width"] > 600:
            errors.append(f"Mobile capture is too wide: {path}")
        if not isinstance(record.get("route"), str) or len(record["route"].strip()) < 1:
            errors.append(f"{path}.route is required")
        if not isinstance(record.get("state"), str) or len(record["state"].strip()) < 3:
            errors.append(f"{path}.state is required")
        if not isinstance(record.get("checkpoint"), str) or len(record["checkpoint"].strip()) < 3:
            errors.append(f"{path}.checkpoint is required")
        captured_at = parse_timestamp(record.get("captured_at"), f"{path}.captured_at", errors)
        if captured_at is not None:
            timestamps.append(captured_at)
        if decoded["pixel_digest"] in pixel_digests:
            errors.append(f"Capture reuses identical decoded pixels under a different claim: {path}")
        pixel_digests.add(decoded["pixel_digest"])
        if artifact in records:
            errors.append(f"Capture artifact is listed more than once: {path}")
        record_copy = dict(record)
        record_copy["_artifact"] = artifact
        record_copy["_decoded"] = decoded
        record_copy["_captured_at"] = captured_at
        records[artifact] = record_copy

    if timestamps != sorted(timestamps) or len(timestamps) != len(set(timestamps)):
        errors.append("capture_manifest.captures must be listed in strict chronological order")

    report_images: set[Path] = set()
    collect_report_images(data, base_dir, report_images)
    for artifact in sorted(report_images, key=lambda item: str(item).casefold()):
        if artifact not in records:
            errors.append(f"Report image is missing from capture_manifest: {artifact}")
    return records, manifest_path


def validate_style_manifests(
    data: dict[str, Any], base_dir: Path, source_fingerprint: str | None, errors: list[str]
) -> None:
    values = get_path(data, "implementation_audit.runtime_style_manifests")
    if not isinstance(values, list) or len(values) < 2:
        errors.append("implementation_audit.runtime_style_manifests must contain desktop and mobile JSON")
        return
    viewports: set[str] = set()
    manifest_files: set[Path] = set()
    for index, value in enumerate(values):
        path = f"implementation_audit.runtime_style_manifests[{index}]"
        manifest, manifest_path = load_json_file(value, base_dir, path, errors)
        if manifest is None or manifest_path is None:
            continue
        if manifest_path in manifest_files:
            errors.append(f"Runtime style manifests must be distinct files: {path}")
        manifest_files.add(manifest_path)
        require_manifest_header(manifest, STYLE_GENERATOR, path, errors)
        if source_fingerprint and manifest.get("source_fingerprint") != source_fingerprint:
            errors.append(f"{path}.source_fingerprint does not match the scanned source tree")
        viewport = manifest.get("viewport")
        if viewport not in {"desktop", "mobile"}:
            errors.append(f"{path}.viewport must be desktop or mobile")
        else:
            viewports.add(viewport)
        parse_timestamp(manifest.get("captured_at"), f"{path}.captured_at", errors)
        if not isinstance(manifest.get("url"), str) or len(manifest["url"].strip()) < 4:
            errors.append(f"{path}.url is required")
        scanned = manifest.get("scanned_elements")
        if isinstance(scanned, bool) or not isinstance(scanned, int) or scanned < 1:
            errors.append(f"{path}.scanned_elements must be a positive integer")
        if manifest.get("pseudo_elements_checked") is not True:
            errors.append(f"{path}.pseudo_elements_checked must be true")
        if manifest.get("canvas_and_svg_checked") is not True:
            errors.append(f"{path}.canvas_and_svg_checked must be true")
        if manifest.get("canvas_elements_reviewed") is not True:
            errors.append(f"{path}.canvas_elements_reviewed must be true")
        for field in STYLE_EMPTY_FIELDS:
            findings = manifest.get(field)
            if not isinstance(findings, list) or findings:
                errors.append(f"{path}.{field} must be an empty list")
    if viewports != {"desktop", "mobile"}:
        errors.append("Runtime style audit must cover both desktop and mobile")


def validate_control_manifests(
    data: dict[str, Any], base_dir: Path, source_fingerprint: str | None, errors: list[str]
) -> None:
    values = get_path(data, "implementation_audit.control_manifests")
    if not isinstance(values, list) or len(values) < 2:
        errors.append("implementation_audit.control_manifests must contain desktop and mobile JSON")
        return
    context_cta = normalized(get_path(data, "context.primary_cta"))
    report_controls = get_path(data, "action_trace.control_inventory", [])
    report_keys = {
        (
            normalized(item.get("label")),
            normalized(item.get("accessible_name")),
            normalized(item.get("role")),
            str(item.get("selector", "")).strip(),
            item.get("behavior"),
        )
        for item in report_controls
        if isinstance(item, dict)
    }
    viewports: set[str] = set()
    for index, value in enumerate(values):
        path = f"implementation_audit.control_manifests[{index}]"
        manifest, _ = load_json_file(value, base_dir, path, errors)
        if manifest is None:
            continue
        require_manifest_header(manifest, CONTROL_GENERATOR, path, errors)
        if source_fingerprint and manifest.get("source_fingerprint") != source_fingerprint:
            errors.append(f"{path}.source_fingerprint does not match the scanned source tree")
        viewport = manifest.get("viewport")
        if viewport not in {"desktop", "mobile"}:
            errors.append(f"{path}.viewport must be desktop or mobile")
        else:
            viewports.add(viewport)
        parse_timestamp(manifest.get("captured_at"), f"{path}.captured_at", errors)
        if manifest.get("all_visible_controls_tested") is not True:
            errors.append(f"{path}.all_visible_controls_tested must be true")
        for field in ("dead_controls", "unreported_controls"):
            value_list = manifest.get(field)
            if not isinstance(value_list, list) or value_list:
                errors.append(f"{path}.{field} must be an empty list")
        controls = manifest.get("controls")
        if not isinstance(controls, list) or not controls:
            errors.append(f"{path}.controls must contain the rendered control inventory")
            continue
        manifest_keys: set[tuple[str, str, str, str, Any]] = set()
        primary_matches = 0
        for control_index, control in enumerate(controls):
            control_path = f"{path}.controls[{control_index}]"
            if not isinstance(control, dict):
                errors.append(f"Control must be an object: {control_path}")
                continue
            label = normalized(control.get("label"))
            accessible_name = normalized(control.get("accessible_name"))
            role = normalized(control.get("role"))
            selector = control.get("selector")
            behavior = control.get("behavior")
            manifest_keys.add(
                (
                    label,
                    accessible_name,
                    role,
                    selector.strip() if isinstance(selector, str) else "",
                    behavior,
                )
            )
            if len(label) < 2 or len(accessible_name) < 2:
                errors.append(f"{control_path} needs visible and accessible names")
            if not isinstance(selector, str) or len(selector.strip()) < 2:
                errors.append(f"{control_path}.selector is required")
            if behavior not in {"functional", "navigation", "disabled"}:
                errors.append(f"{control_path}.behavior is invalid")
            raw_href = (
                control.get("href", "").strip().casefold()
                if isinstance(control.get("href", ""), str)
                else ""
            )
            if raw_href == "#" or raw_href.startswith("javascript:"):
                errors.append(f"Dead or placeholder href found: {control_path}")
            if behavior == "navigation" and not raw_href:
                errors.append(f"Navigation control requires a real href: {control_path}")
            if behavior in {"functional", "navigation"}:
                if control.get("meaningful_change") is not True:
                    errors.append(f"{control_path}.meaningful_change must be true")
                before_hash = control.get("before_state_hash")
                after_hash = control.get("after_state_hash")
                before_url = control.get("before_url")
                after_url = control.get("after_url")
                if before_hash == after_hash and before_url == after_url:
                    errors.append(f"{control_path} has no observed URL or state change")
                for field in ("expected_result", "observed_result", "recovery"):
                    if not isinstance(control.get(field), str) or len(control[field].strip()) < 20:
                        errors.append(f"{control_path}.{field} must describe observed behavior")
            if label == context_cta:
                primary_matches += 1
                if role != "primary" or behavior != "functional":
                    errors.append(
                        f"{control_path} matching context.primary_cta must be primary and functional"
                    )
        if manifest_keys != report_keys:
            errors.append(f"{path}.controls must match action_trace.control_inventory exactly")
        if primary_matches != 1:
            errors.append(f"{path} must contain exactly one tested context.primary_cta")
    if viewports != {"desktop", "mobile"}:
        errors.append("Control audit must cover both desktop and mobile")


def validate_content_manifest(
    data: dict[str, Any],
    base_dir: Path,
    source_fingerprint: str | None,
    captures: dict[Path, dict[str, Any]],
    errors: list[str],
) -> None:
    manifest, _ = load_json_file(
        get_path(data, "implementation_audit.content_manifest"),
        base_dir,
        "implementation_audit.content_manifest",
        errors,
    )
    if manifest is None:
        return
    require_manifest_header(manifest, CONTENT_GENERATOR, "content_manifest", errors)
    if source_fingerprint and manifest.get("source_fingerprint") != source_fingerprint:
        errors.append("content_manifest.source_fingerprint does not match the scanned source tree")
    parse_timestamp(manifest.get("captured_at"), "content_manifest.captured_at", errors)
    if manifest.get("inventory_complete") is not True:
        errors.append("content_manifest.inventory_complete must be true")
    unverified = manifest.get("unverified_claims")
    if not isinstance(unverified, list) or unverified:
        errors.append("content_manifest.unverified_claims must be an empty list")
    claims = manifest.get("visible_claims")
    if not isinstance(claims, list):
        errors.append("content_manifest.visible_claims must be a list")
        return
    capture_hashes = {record["_decoded"]["file_digest"] for record in captures.values()}
    valid_claim_types = {
        "certification",
        "customer",
        "factual-data",
        "integration",
        "metric",
        "mock-data",
        "performance",
        "testimonial",
    }
    valid_source_types = {"external-research", "fixture", "repository", "user"}
    for index, claim in enumerate(claims):
        path = f"content_manifest.visible_claims[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"Claim must be an object: {path}")
            continue
        for field, minimum in (("text", 5), ("selector", 2), ("source", 5)):
            if not isinstance(claim.get(field), str) or len(claim[field].strip()) < minimum:
                errors.append(f"{path}.{field} is required")
        if claim.get("claim_type") not in valid_claim_types:
            errors.append(f"{path}.claim_type is invalid")
        source_type = claim.get("source_type")
        if source_type not in valid_source_types:
            errors.append(f"{path}.source_type is invalid")
        source = claim.get("source")
        if source_type == "external-research" and (
            not isinstance(source, str) or not source.startswith(("http://", "https://"))
        ):
            errors.append(f"{path}.source must be an external URL")
        if source_type == "repository" and isinstance(source, str):
            source_path = resolve_path(source, base_dir, f"{path}.source", errors)
            if source_path is None or not source_path.is_file():
                errors.append(f"{path}.source repository artifact does not exist")
        if source_type == "fixture":
            disclosure = claim.get("disclosure")
            if not isinstance(disclosure, str) or len(disclosure.strip()) < 15:
                errors.append(f"{path}.disclosure must visibly identify fixture or demo data")
        if claim.get("evidence_capture_sha256") not in capture_hashes:
            errors.append(f"{path}.evidence_capture_sha256 is outside the capture manifest")

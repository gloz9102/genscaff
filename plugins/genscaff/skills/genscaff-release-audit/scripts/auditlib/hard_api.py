"""Compose Strict evidence checks in their established order."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


from .browser import (
    run_lighthouse_audit,
    run_live_audit,
)
from .commands import (
    execute_verification_command,
    safe_verification_argv,
    validate_execution_manifest,
)
from .files import (
    canonical_project_index,
    file_sha256,
    file_url_path,
    iter_source_files,
    load_json_file,
    path_is_within,
    resolve_path,
)
from .hard_common import (
    BROWSER_IMAGE_SUFFIXES,
    CAPTURE_GENERATOR,
    COMMAND_RESULT_CACHE,
    CONTENT_GENERATOR,
    CONTROL_GENERATOR,
    COSMETIC_TERMS,
    DATA_URI_PATTERN,
    EXECUTION_GENERATOR,
    FORBIDDEN_SOURCE_PATTERNS,
    GENERIC_CTA_PATTERNS,
    IGNORED_DIRECTORIES,
    MANIFEST_SCHEMA_VERSION,
    MAX_IMAGE_PIXELS,
    MAX_SOURCE_BYTES,
    PNG_DECODE_CACHE,
    RENDERED_IGNORED_DIRECTORIES,
    RENDERED_SOURCE_SUFFIXES,
    REVIEW_GENERATOR,
    SOURCE_SUFFIXES,
    STOPWORDS,
    STYLE_EMPTY_FIELDS,
    STYLE_GENERATOR,
    SUBSTITUTION_AXES,
    get_path,
    live_signal_is_substantive,
    meaningful_tokens,
    normalized,
    parse_timestamp,
    require_manifest_header,
)
from .images import (
    collect_report_images,
    decode_png,
    image_structure_metrics,
    paeth,
    pixel_change_ratio,
)
from .live_evidence import (
    live_control_key,
    validate_live_audit_bundle,
)
from .manifests import (
    validate_capture_manifest,
    validate_content_manifest,
    validate_control_manifests,
    validate_style_manifests,
)
from .provenance import (
    evidence_artifact,
    validate_action_and_state_evidence,
    validate_checkpoint_sequence,
    validate_independent_review,
    validate_iteration_evidence,
    validate_lighthouse_provenance,
    validate_substitution,
    validate_visual_target_content,
)
from .source import (
    calculate_source_fingerprint,
    decode_resource_body,
    decoded_data_uri_payloads,
    scan_forbidden_content,
    selector_is_overbroad,
    selector_specs,
    sniff_image_type,
    validate_source_audit,
)


def internal_artifact_paths(data: dict[str, Any], report_path: Path) -> set[Path]:
    """Return gate-owned evidence files that must not make the source hash self-referential."""
    base_dir = report_path.resolve().parent
    values: list[Any] = [
        str(report_path.resolve()),
        get_path(data, "implementation_audit.live_audit_config"),
        get_path(data, "implementation_audit.capture_manifest"),
        get_path(data, "implementation_audit.content_manifest"),
        get_path(data, "visual_review.independent_review.review_artifact"),
        get_path(data, "measurements.lighthouse.report"),
        get_path(data, "measurements.execution_manifest"),
    ]
    for path in (
        "implementation_audit.runtime_style_manifests",
        "implementation_audit.control_manifests",
    ):
        candidates = get_path(data, path, [])
        if isinstance(candidates, list):
            values.extend(candidates)
    resolved: set[Path] = set()
    for value in values:
        if not isinstance(value, str) or not value.strip() or value.startswith(("http://", "https://")):
            continue
        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            candidate = base_dir / candidate
        try:
            resolved.add(candidate.resolve())
        except OSError:
            continue

    config_path_value = get_path(data, "implementation_audit.live_audit_config")
    if isinstance(config_path_value, str) and config_path_value.strip():
        config_path = Path(config_path_value).expanduser()
        if not config_path.is_absolute():
            config_path = base_dir / config_path
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            output_value = config.get("output_dir") if isinstance(config, dict) else None
            if isinstance(output_value, str) and output_value.strip():
                output_dir = Path(output_value).expanduser()
                if not output_dir.is_absolute():
                    output_dir = config_path.resolve().parent / output_dir
                resolved.add((output_dir / "live-audit-bundle.json").resolve())
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            pass
    return resolved


def validate(
    data: dict[str, Any],
    report_path: Path,
    *,
    _live_bundle_override: dict[str, Any] | None = None,
    _lighthouse_bundle_override: dict[str, Any] | None = None,
    execute_approved_commands: bool = False,
) -> list[str]:
    errors: list[str] = []
    base_dir = report_path.resolve().parent
    _, source_fingerprint = validate_source_audit(
        data,
        base_dir,
        errors,
        excluded_artifacts=internal_artifact_paths(data, report_path),
    )
    live_bundle, live_config, live_config_path = run_live_audit(
        data,
        base_dir,
        source_fingerprint,
        errors,
        bundle_override=_live_bundle_override,
    )
    lighthouse_bundle = run_lighthouse_audit(
        live_config_path,
        errors,
        bundle_override=_lighthouse_bundle_override,
    )
    captures, _ = validate_capture_manifest(data, base_dir, source_fingerprint, errors)
    validate_live_audit_bundle(
        live_bundle,
        live_config,
        live_config_path,
        data,
        base_dir,
        source_fingerprint,
        captures,
        errors,
    )
    validate_style_manifests(data, base_dir, source_fingerprint, errors)
    validate_control_manifests(data, base_dir, source_fingerprint, errors)
    validate_content_manifest(data, base_dir, source_fingerprint, captures, errors)
    validate_action_and_state_evidence(data, base_dir, captures, errors)
    validate_substitution(data, errors)
    validate_iteration_evidence(data, base_dir, captures, errors)
    validate_independent_review(data, base_dir, source_fingerprint, captures, errors)
    validate_lighthouse_provenance(
        data,
        base_dir,
        errors,
        observed=lighthouse_bundle,
        live_config_path=live_config_path,
    )
    validate_execution_manifest(
        data,
        base_dir,
        source_fingerprint,
        errors,
        execute_approved_commands=execute_approved_commands,
    )
    validate_visual_target_content(data, base_dir, captures, errors)
    return errors

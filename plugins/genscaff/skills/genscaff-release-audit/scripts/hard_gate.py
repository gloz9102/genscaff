#!/usr/bin/env python3
"""Compatibility entrypoint for the Strict hard_gate.py interface."""
from auditlib.browser import (
    run_lighthouse_audit,
    run_live_audit,
)
from auditlib.commands import (
    execute_verification_command,
    safe_verification_argv,
    validate_execution_manifest,
)
from auditlib.files import (
    canonical_project_index,
    file_sha256,
    file_url_path,
    iter_source_files,
    load_json_file,
    path_is_within,
    resolve_path,
)
from auditlib.hard_api import (
    internal_artifact_paths,
    validate,
)
from auditlib.hard_common import (
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
from auditlib.images import (
    collect_report_images,
    decode_png,
    image_structure_metrics,
    paeth,
    pixel_change_ratio,
)
from auditlib.live_evidence import (
    live_control_key,
    validate_live_audit_bundle,
)
from auditlib.manifests import (
    validate_capture_manifest,
    validate_content_manifest,
    validate_control_manifests,
    validate_style_manifests,
)
from auditlib.provenance import (
    evidence_artifact,
    validate_action_and_state_evidence,
    validate_checkpoint_sequence,
    validate_independent_review,
    validate_iteration_evidence,
    validate_lighthouse_provenance,
    validate_substitution,
    validate_visual_target_content,
)
from auditlib.source import (
    calculate_source_fingerprint,
    decode_resource_body,
    decoded_data_uri_payloads,
    scan_forbidden_content,
    selector_is_overbroad,
    selector_specs,
    sniff_image_type,
    validate_source_audit,
)

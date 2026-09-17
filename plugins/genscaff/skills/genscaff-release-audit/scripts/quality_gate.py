#!/usr/bin/env python3
"""Compatibility entrypoint for the Strict quality_gate.py interface."""
import hard_gate
from auditlib.report_api import (
    _validate_strict,
    validate,
)
from auditlib.report_cli import (
    fail,
    main,
)
from auditlib.report_constants import (
    COSMETIC_ONLY_SIGNALS,
    DOMAIN_SIGNAL_MINIMUMS,
    GENERIC_PRIMARY_CTAS,
    IMAGE_SUFFIXES,
    LEGACY_PROFILE_SCHEMA_VERSION,
    LIGHTHOUSE_THRESHOLDS,
    MIN_IMAGE_BYTES,
    MIN_IMAGE_HEIGHT,
    MIN_IMAGE_WIDTH,
    MIN_VISUAL_ITERATIONS,
    PLACEHOLDER_MARKERS,
    PROFILE_SCHEMA_VERSION,
    REQUIRED_CHECKS,
    REQUIRED_STATE_NAMES,
    SCHEMA_VERSION,
    STANDARD_COMPLETION_STATUSES,
    TARGET_SUFFIXES,
    TEMPLATE,
    TRIVIAL_TEXT,
    VALID_CONTROL_BEHAVIORS,
    VALID_CONTROL_ROLES,
    VALID_INTERACTION_MODES,
    VALID_PROFILES,
    VALID_REQUIREMENT_SOURCES,
    VALID_REVIEWERS,
    VALID_SCOPES,
    VALID_SEVERITIES,
    VALID_STATE_STATUSES,
    VALID_WORK_TYPES,
    VERIFICATION_DIMENSION_STATUSES,
    evidence_template,
)
from auditlib.report_contract import (
    validate_context,
    validate_product_specificity,
    validate_requirement_trace,
    validate_visual_target,
)
from auditlib.report_evidence import (
    ArtifactInspector,
    image_dimensions,
    validate_evidence,
    validate_evidence_catalog,
    validate_evidence_list,
    validate_inline_evidence,
)
from auditlib.report_fields import (
    get_path,
    get_path_or_none,
    normalized_text,
    parse_timestamp,
    placeholder_reason,
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
from auditlib.report_flow import (
    validate_action_trace,
    validate_state_coverage,
    validate_task_walkthroughs,
)
from auditlib.report_profiles import (
    _upgrade_v4_standard,
    apply_visual_exceptions,
    effective_standard_status,
    profile_template,
    validate_profile_envelope,
    validate_standard,
    validate_visual_policy,
)
from auditlib.report_review import (
    validate_checks,
    validate_iteration_log,
    validate_judgment,
    validate_lighthouse,
    validate_measurements,
    validate_target_chronology,
    validate_visual_review,
)

if __name__ == "__main__":
    raise SystemExit(main())

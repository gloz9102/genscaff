"""Report schema constants and the Strict report template."""
from __future__ import annotations



SCHEMA_VERSION = 3


LEGACY_PROFILE_SCHEMA_VERSION = 4


PROFILE_SCHEMA_VERSION = 5


VALID_PROFILES = {"standard", "strict"}


STANDARD_COMPLETION_STATUSES = {
    "IMPLEMENTED_UNVERIFIED",
    "VERIFIED_RENDER",
    "VERIFIED_FLOW",
    "VERIFIED_STANDARD",
}


VERIFICATION_DIMENSION_STATUSES = {"observed", "static_only", "automated", "not_tested"}


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
    "loading_experience": {
        "applicable": False,
        "boundaries": [],
    },
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

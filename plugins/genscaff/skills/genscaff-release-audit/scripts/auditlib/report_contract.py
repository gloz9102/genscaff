"""Validate context, visual targets, requirements, and product specificity."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from . import hard_api as hard_gate
from .report_constants import (
    COSMETIC_ONLY_SIGNALS,
    DOMAIN_SIGNAL_MINIMUMS,
    GENERIC_PRIMARY_CTAS,
    TARGET_SUFFIXES,
    VALID_REQUIREMENT_SOURCES,
    VALID_SCOPES,
    VALID_WORK_TYPES,
)
from .report_evidence import (
    ArtifactInspector,
    validate_evidence,
    validate_evidence_list,
)
from .report_fields import (
    get_path,
    get_path_or_none,
    normalized_text,
    parse_timestamp,
    require_bool,
    require_empty_list,
    require_enum,
    require_list,
    require_text,
    require_text_value,
    validate_text_list,
)


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

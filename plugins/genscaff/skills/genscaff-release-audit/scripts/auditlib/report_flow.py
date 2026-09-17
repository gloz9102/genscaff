"""Validate action traces, state coverage, and task walkthroughs."""
from __future__ import annotations

from typing import Any
from .report_constants import (
    REQUIRED_STATE_NAMES,
    VALID_CONTROL_BEHAVIORS,
    VALID_CONTROL_ROLES,
    VALID_INTERACTION_MODES,
    VALID_STATE_STATUSES,
)
from .report_evidence import (
    ArtifactInspector,
    validate_evidence,
    validate_evidence_list,
)
from .report_fields import (
    get_path,
    normalized_text,
    require_bool,
    require_empty_list,
    require_enum,
    require_list,
    require_list_value,
    require_text,
    require_text_value,
)


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

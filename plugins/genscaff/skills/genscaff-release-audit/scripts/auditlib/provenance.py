"""Validate checkpoint sequences, review provenance, and action evidence."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from .files import (
    file_sha256,
    load_json_file,
    resolve_path,
)
from .hard_common import (
    COSMETIC_TERMS,
    GENERIC_CTA_PATTERNS,
    REVIEW_GENERATOR,
    SUBSTITUTION_AXES,
    get_path,
    meaningful_tokens,
    normalized,
    parse_timestamp,
    require_manifest_header,
)
from .images import (
    pixel_change_ratio,
)


def evidence_artifact(value: Any, data: dict[str, Any], base_dir: Path) -> Path | None:
    if isinstance(value, str):
        catalog = data.get("evidence_catalog")
        if not isinstance(catalog, dict):
            return None
        value = catalog.get(value)
    if not isinstance(value, dict):
        return None
    artifact = value.get("artifact")
    if not isinstance(artifact, str):
        return None
    candidate = Path(artifact).expanduser()
    if not candidate.is_absolute():
        candidate = base_dir / candidate
    try:
        return candidate.resolve()
    except OSError:
        return None


def validate_checkpoint_sequence(
    checkpoints: Any,
    path: str,
    viewport: str,
    data: dict[str, Any],
    base_dir: Path,
    captures: dict[Path, dict[str, Any]],
    errors: list[str],
) -> None:
    if not isinstance(checkpoints, dict):
        errors.append(f"{path} must be an object with start, feedback, terminal, and recovery evidence")
        return
    ordered_records: list[dict[str, Any]] = []
    for name in ("start", "feedback", "terminal", "recovery"):
        artifact = evidence_artifact(checkpoints.get(name), data, base_dir)
        if artifact is None or artifact not in captures:
            errors.append(f"{path}.{name} must reference a capture-manifest screenshot")
            continue
        record = captures[artifact]
        if record.get("viewport") != viewport:
            errors.append(f"{path}.{name} must use a {viewport} capture")
        if normalized(record.get("checkpoint")) != normalized(f"primary-{name}"):
            errors.append(f"{path}.{name} capture checkpoint must be 'primary-{name}'")
        ordered_records.append(record)
    if len(ordered_records) != 4:
        return
    times = [record.get("_captured_at") for record in ordered_records]
    if any(value is None for value in times) or times != sorted(times) or len(set(times)) != 4:
        errors.append(f"{path} must be captured in strict start→feedback→terminal→recovery order")
    for first, second in zip(ordered_records, ordered_records[1:]):
        ratio = pixel_change_ratio(first["_decoded"], second["_decoded"])
        if ratio < 0.001:
            errors.append(
                f"{path} consecutive checkpoints are visually indistinguishable ({ratio:.4%} changed)"
            )


def validate_action_and_state_evidence(
    data: dict[str, Any],
    base_dir: Path,
    captures: dict[Path, dict[str, Any]],
    errors: list[str],
) -> None:
    label = normalized(get_path(data, "context.primary_cta"))
    if any(pattern.search(label) for pattern in GENERIC_CTA_PATTERNS):
        errors.append("context.primary_cta uses a generic prefix or suffix-resistant vague label")
    label_tokens = meaningful_tokens(get_path(data, "context.primary_cta"))
    contract_tokens = meaningful_tokens(get_path(data, "context.primary_task"))
    for domain_object in get_path(data, "context.domain_objects", []) or []:
        contract_tokens.update(meaningful_tokens(domain_object))
    if not label_tokens & contract_tokens:
        errors.append("context.primary_cta must name a product object or task outcome")

    inventory = get_path(data, "action_trace.control_inventory", [])
    matching = [item for item in inventory if isinstance(item, dict) and normalized(item.get("label")) == label]
    if len(matching) != 1:
        errors.append("action_trace.control_inventory must contain exactly one context.primary_cta")
    elif matching[0].get("role") != "primary" or matching[0].get("behavior") != "functional":
        errors.append("The context.primary_cta control must itself be primary and functional")

    validate_checkpoint_sequence(
        get_path(data, "action_trace.primary.checkpoints"),
        "action_trace.primary.checkpoints",
        "desktop",
        data,
        base_dir,
        captures,
        errors,
    )
    walkthroughs = get_path(data, "task_walkthroughs", [])
    if isinstance(walkthroughs, list):
        for index, walkthrough in enumerate(walkthroughs):
            if not isinstance(walkthrough, dict):
                continue
            viewport = walkthrough.get("viewport")
            if viewport in {"desktop", "mobile"}:
                validate_checkpoint_sequence(
                    walkthrough.get("checkpoints"),
                    f"task_walkthroughs[{index}].checkpoints",
                    viewport,
                    data,
                    base_dir,
                    captures,
                    errors,
                )

    state_artifacts: dict[str, Path] = {}
    states = get_path(data, "state_coverage", [])
    if isinstance(states, list):
        for item in states:
            if not isinstance(item, dict) or item.get("status") != "implemented":
                continue
            evidence = item.get("evidence")
            if isinstance(evidence, list) and evidence:
                artifact = evidence_artifact(evidence[0], data, base_dir)
                if artifact is not None:
                    state_artifacts[str(item.get("state"))] = artifact
    success = state_artifacts.get("success")
    long_content = state_artifacts.get("long-content")
    if success and long_content and success in captures and long_content in captures:
        if captures[success]["_decoded"]["pixel_digest"] == captures[long_content]["_decoded"]["pixel_digest"]:
            errors.append("success and long-content states must use state-specific decoded pixels")

    trait_requirements = {
        "async": {"loading", "error"},
        "form": {"disabled", "error"},
        "collection": {"empty", "long-content"},
        "generation": {"loading", "error", "success"},
        "transaction": {"disabled", "error", "success"},
    }
    traits = get_path(data, "context.task_traits", [])
    required: set[str] = set()
    if isinstance(traits, list):
        for trait in traits:
            required.update(trait_requirements.get(normalized(trait), set()))
    implemented = {
        str(item.get("state"))
        for item in states
        if isinstance(item, dict) and item.get("status") == "implemented"
    }
    for state in sorted(required - implemented):
        errors.append(f"context.task_traits require state_coverage.{state} to be implemented")

    loading = get_path(data, "loading_experience")
    loading_required = bool({normalized(trait) for trait in traits or []} & {"async", "generation"})
    if not isinstance(loading, dict):
        if loading_required:
            errors.append("async and generation traits require loading_experience")
        return
    applicable = loading.get("applicable")
    boundaries = loading.get("boundaries")
    if not isinstance(applicable, bool):
        errors.append("loading_experience.applicable must be a boolean")
    if not isinstance(boundaries, list):
        errors.append("loading_experience.boundaries must be a list")
        return
    if loading_required and applicable is not True:
        errors.append("async and generation traits require loading_experience.applicable=true")
    if loading_required and not boundaries:
        errors.append("async and generation traits require at least one loading boundary")
    if applicable is False and boundaries:
        errors.append("loading_experience.boundaries must be empty when loading is not applicable")
    for index, boundary in enumerate(boundaries):
        path = f"loading_experience.boundaries[{index}]"
        if not isinstance(boundary, dict):
            errors.append(f"{path} must be an object")
            continue
        for key in (
            "trigger",
            "affected_surface",
            "wait_avoidance",
            "stale_data_policy",
            "failure_recovery",
            "user_control",
            "evidence",
        ):
            if not isinstance(boundary.get(key), str) or not boundary.get(key, "").strip():
                errors.append(f"{path}.{key} must be non-empty")


def validate_substitution(data: dict[str, Any], errors: list[str]) -> None:
    comparisons = get_path(data, "product_specificity.substitution_test.comparisons", [])
    if not isinstance(comparisons, list):
        return
    target_tokens = meaningful_tokens(get_path(data, "context.product_type"))
    for item in get_path(data, "context.domain_objects", []) or []:
        target_tokens.update(meaningful_tokens(item))
    alternates: list[set[str]] = []
    for index, comparison in enumerate(comparisons):
        path = f"product_specificity.substitution_test.comparisons[{index}]"
        if not isinstance(comparison, dict):
            continue
        alternate_tokens = meaningful_tokens(comparison.get("alternate_product"))
        alternates.append(alternate_tokens)
        overlap = target_tokens & alternate_tokens
        if overlap:
            errors.append(f"{path}.alternate_product is not semantically distant; shared tokens: {sorted(overlap)}")
        if comparison.get("far_from_target") is not True:
            errors.append(f"{path}.far_from_target must be true")
        rationale = comparison.get("distance_rationale")
        if not isinstance(rationale, str) or len(rationale.strip()) < 50:
            errors.append(f"{path}.distance_rationale must justify a distant domain")
        axes = comparison.get("axes")
        if not isinstance(axes, dict) or set(axes) != set(SUBSTITUTION_AXES):
            errors.append(f"{path}.axes must contain exactly {list(SUBSTITUTION_AXES)}")
        else:
            broken = 0
            for axis in SUBSTITUTION_AXES:
                record = axes.get(axis)
                axis_path = f"{path}.axes.{axis}"
                if not isinstance(record, dict):
                    errors.append(f"{axis_path} must be an object")
                    continue
                if record.get("breaks") is True:
                    broken += 1
                reason = record.get("reason")
                if not isinstance(reason, str) or len(reason.strip()) < 25:
                    errors.append(f"{axis_path}.reason must be concrete")
            if broken < 4:
                errors.append(f"{path} must structurally break on at least four of five axes")
        for signal_index, signal in enumerate(comparison.get("breaking_signals") or []):
            signal_tokens = meaningful_tokens(signal)
            if signal_tokens & COSMETIC_TERMS and not signal_tokens & target_tokens:
                errors.append(
                    f"{path}.breaking_signals[{signal_index}] relies on cosmetic identity"
                )
    if len(alternates) >= 2 and alternates[0] & alternates[1]:
        errors.append("Substitution alternate products must be mutually distant, not adjacent categories")


def validate_iteration_evidence(
    data: dict[str, Any], base_dir: Path, captures: dict[Path, dict[str, Any]], errors: list[str]
) -> None:
    iterations = get_path(data, "visual_review.iteration_log", [])
    if not isinstance(iterations, list):
        return
    records: list[dict[str, Any]] = []
    findings: set[str] = set()
    resolved: set[str] = set()
    for index, iteration in enumerate(iterations):
        if not isinstance(iteration, dict):
            continue
        screenshot = resolve_path(
            iteration.get("screenshot"), base_dir, f"visual_review.iteration_log[{index}].screenshot", errors
        )
        if screenshot in captures:
            records.append(captures[screenshot])
        for finding_index, finding in enumerate(iteration.get("findings") or []):
            if not isinstance(finding, dict):
                continue
            finding_id = normalized(finding.get("id"))
            if len(finding_id) < 3:
                errors.append(
                    f"visual_review.iteration_log[{index}].findings[{finding_index}].id is required"
                )
            elif finding_id in findings:
                errors.append(f"Duplicate iteration finding id: {finding_id}")
            else:
                findings.add(finding_id)
        for change_index, change in enumerate(iteration.get("changes") or []):
            if not isinstance(change, dict):
                continue
            resolves = change.get("resolves")
            if not isinstance(resolves, list) or not resolves:
                errors.append(
                    f"visual_review.iteration_log[{index}].changes[{change_index}].resolves is required"
                )
                continue
            for finding_id in resolves:
                resolved.add(normalized(finding_id))
    if len(records) == len(iterations) and records:
        times = [record.get("_captured_at") for record in records]
        if any(value is None for value in times) or times != sorted(times) or len(times) != len(set(times)):
            errors.append("Visual iteration screenshots must be captured in strict chronological order")
        for first, second in zip(records, records[1:]):
            ratio = pixel_change_ratio(first["_decoded"], second["_decoded"])
            if ratio < 0.002:
                errors.append(
                    f"Visual iteration screenshots are only {ratio:.4%} different; declared changes need visible evidence"
                )
    missing = findings - resolved
    unknown = resolved - findings
    if missing:
        errors.append(f"Iteration findings are not linked to a resolving change: {sorted(missing)}")
    if unknown:
        errors.append(f"Iteration changes resolve unknown finding ids: {sorted(unknown)}")


def validate_independent_review(
    data: dict[str, Any],
    base_dir: Path,
    source_fingerprint: str | None,
    captures: dict[Path, dict[str, Any]],
    errors: list[str],
) -> None:
    review_path = get_path(data, "visual_review.independent_review.review_artifact")
    review, _ = load_json_file(
        review_path, base_dir, "visual_review.independent_review.review_artifact", errors
    )
    if review is None:
        return
    require_manifest_header(review, REVIEW_GENERATOR, "independent_review", errors)
    if review.get("reviewer_type") != "subagent":
        errors.append("Independent review must be produced by a fresh subagent")
    reviewer_id = normalized(review.get("reviewer_id"))
    implementer_id = normalized(review.get("implementer_id"))
    if len(reviewer_id) < 3 or len(implementer_id) < 3 or reviewer_id == implementer_id:
        errors.append("Independent review must record distinct reviewer_id and implementer_id")
    if normalized(get_path(data, "visual_review.independent_review.reviewer_name")) != reviewer_id:
        errors.append("Independent review raw reviewer_id must match the report reviewer_name")
    if get_path(data, "visual_review.independent_review.reviewer") != "subagent":
        errors.append("Independent review report reviewer must be 'subagent'")
    if review.get("prompt_blind") is not True or review.get("intended_verdict_disclosed") is not False:
        errors.append("Independent review prompt must be blind and must not disclose the intended verdict")
    prompt = review.get("neutral_prompt")
    if not isinstance(prompt, str) or len(prompt.strip()) < 120:
        errors.append("Independent review neutral_prompt must preserve the full blind review request")
    elif re.search(r"(?i)must\s+pass|expected\s+pass|verdict\s+should\s+be\s+pass", prompt):
        errors.append("Independent review prompt is leading")
    if source_fingerprint and review.get("source_fingerprint") != source_fingerprint:
        errors.append("Independent review source_fingerprint does not match the implementation")
    finished = parse_timestamp(review.get("finished_at"), "independent_review.finished_at", errors)
    latest_capture = max(
        (record.get("_captured_at") or 0 for record in captures.values()), default=0
    )
    if finished is not None and latest_capture and finished <= latest_capture:
        errors.append("Independent review must finish after the reviewed browser captures")
    reviewed_hashes = review.get("reviewed_capture_sha256")
    available_hashes = {record["_decoded"]["file_digest"] for record in captures.values()}
    if not isinstance(reviewed_hashes, list) or len(set(reviewed_hashes)) < 4:
        errors.append("Independent review must reference at least four distinct capture hashes")
    elif not set(reviewed_hashes).issubset(available_hashes):
        errors.append("Independent review references capture hashes outside the capture manifest")

    identity = review.get("identity_probe")
    if not isinstance(identity, dict):
        errors.append("Independent review identity_probe is required")
    else:
        if identity.get("branding_ignored") is not True or identity.get("branding_required") is not False:
            errors.append("Identity probe must ignore branding and succeed without it")
        for field in ("identified_product_type", "identified_primary_task"):
            if not isinstance(identity.get(field), str) or len(identity[field].strip()) < 20:
                errors.append(f"independent_review.identity_probe.{field} is too weak")
        signals = identity.get("non_cosmetic_signals")
        if not isinstance(signals, list) or len(signals) < 3:
            errors.append("Identity probe needs at least three non-cosmetic signals")
        if identity.get("verdict") != "pass":
            errors.append("Independent review identity_probe.verdict must be pass")

    action = review.get("action_probe")
    if not isinstance(action, dict):
        errors.append("Independent review action_probe is required")
    else:
        if normalized(action.get("trigger_label")) != normalized(get_path(data, "context.primary_cta")):
            errors.append("Independent review action trigger must match context.primary_cta")
        for field in (
            "predicted_outcome",
            "observed_feedback",
            "observed_terminal_state",
            "observed_recovery",
        ):
            if not isinstance(action.get(field), str) or len(action[field].strip()) < 20:
                errors.append(f"independent_review.action_probe.{field} is too weak")
        if action.get("verdict") != "pass":
            errors.append("Independent review action_probe.verdict must be pass")

    anti_slop = review.get("anti_slop_probe")
    if not isinstance(anti_slop, dict):
        errors.append("Independent review anti_slop_probe is required")
    else:
        for field in ("source_scan_reviewed", "runtime_style_reviewed", "screenshots_reviewed"):
            if anti_slop.get(field) is not True:
                errors.append(f"independent_review.anti_slop_probe.{field} must be true")
        if anti_slop.get("verdict") != "pass":
            errors.append("Independent review anti_slop_probe.verdict must be pass")
        violations = anti_slop.get("violations")
        if not isinstance(violations, list) or violations:
            errors.append("Independent review anti_slop violations must be an empty list")


def validate_lighthouse_provenance(
    data: dict[str, Any],
    base_dir: Path,
    errors: list[str],
    *,
    observed: dict[str, Any] | None = None,
    live_config_path: Path | None = None,
) -> None:
    report_path = get_path(data, "measurements.lighthouse.report")
    lighthouse, _ = load_json_file(report_path, base_dir, "measurements.lighthouse.report", errors)
    if lighthouse is None:
        return
    version = lighthouse.get("lighthouseVersion")
    if not isinstance(version, str) or not re.match(r"^\d+\.\d+", version):
        errors.append("Lighthouse artifact is missing lighthouseVersion")
    if not isinstance(lighthouse.get("finalUrl"), str) or not lighthouse["finalUrl"].startswith(("http://", "https://", "file://")):
        errors.append("Lighthouse artifact is missing a valid finalUrl")
    parse_timestamp(lighthouse.get("fetchTime"), "Lighthouse.fetchTime", errors)
    if not isinstance(lighthouse.get("userAgent"), str) or len(lighthouse["userAgent"]) < 10:
        errors.append("Lighthouse artifact is missing userAgent")
    for field in ("environment", "configSettings"):
        if not isinstance(lighthouse.get(field), dict) or not lighthouse[field]:
            errors.append(f"Lighthouse artifact is missing {field}")
    audits = lighthouse.get("audits")
    if not isinstance(audits, dict) or len(audits) < 100:
        errors.append("Lighthouse artifact must contain the full audits map, not a hand-written score stub")
        audits = {}
    canonical_audits = {
        "aria-allowed-attr",
        "button-name",
        "color-contrast",
        "cumulative-layout-shift",
        "document-title",
        "errors-in-console",
        "first-contentful-paint",
        "html-has-lang",
        "image-alt",
        "largest-contentful-paint",
        "link-name",
        "meta-viewport",
        "speed-index",
        "total-blocking-time",
    }
    missing_canonical = canonical_audits - set(audits)
    if missing_canonical:
        errors.append(f"Lighthouse artifact is missing canonical audits: {sorted(missing_canonical)}")
    categories = lighthouse.get("categories")
    if isinstance(categories, dict):
        for category_name in ("performance", "accessibility", "best-practices", "seo"):
            category = categories.get(category_name)
            if not isinstance(category, dict) or not isinstance(category.get("auditRefs"), list) or not category["auditRefs"]:
                errors.append(f"Lighthouse category {category_name} is missing auditRefs")
            elif any(
                not isinstance(reference, dict) or reference.get("id") not in audits
                for reference in category["auditRefs"]
            ):
                errors.append(f"Lighthouse category {category_name} references audits outside the full map")
    if not isinstance(lighthouse.get("runWarnings"), list):
        errors.append("Lighthouse artifact is missing runWarnings")
    elif lighthouse["runWarnings"]:
        errors.append("Lighthouse artifact runWarnings must be empty")
    if lighthouse.get("runtimeError"):
        errors.append("Lighthouse artifact contains a runtimeError")
    if not isinstance(lighthouse.get("timing"), dict) or not lighthouse["timing"]:
        errors.append("Lighthouse artifact is missing timing provenance")

    runner = Path(__file__).resolve().parent.parent / "lighthouse_audit.js"
    provenance = lighthouse.get("_genscaff_provenance")
    if not isinstance(provenance, dict):
        errors.append("Lighthouse artifact is missing gate-owned runner provenance")
    else:
        if provenance.get("runner_sha256") != file_sha256(runner):
            errors.append("Lighthouse artifact runner sha256 does not match the gate-owned runner")
        if live_config_path is not None and provenance.get("config_sha256") != file_sha256(live_config_path):
            errors.append("Lighthouse artifact config sha256 does not match live_audit_config")
        if provenance.get("audited_url") != lighthouse.get("finalUrl"):
            errors.append("Lighthouse artifact audited_url does not match finalUrl")

    if observed is None:
        errors.append("Validator-owned Lighthouse re-execution did not produce an observation")
        return
    observed_provenance = observed.get("_genscaff_provenance")
    if not isinstance(observed_provenance, dict):
        errors.append("Validator-owned Lighthouse result is missing runner provenance")
    else:
        if observed_provenance.get("runner_sha256") != file_sha256(runner):
            errors.append("Validator-owned Lighthouse runner sha256 is invalid")
        if live_config_path is not None and observed_provenance.get("config_sha256") != file_sha256(live_config_path):
            errors.append("Validator-owned Lighthouse config sha256 is invalid")
        if observed_provenance.get("audited_url") != observed.get("finalUrl"):
            errors.append("Validator-owned Lighthouse audited_url does not match finalUrl")
    observed_audits = observed.get("audits")
    if not isinstance(observed_audits, dict) or len(observed_audits) < 100 or canonical_audits - set(observed_audits):
        errors.append("Validator-owned Lighthouse result is not a complete canonical LHR")
    thresholds = {
        "performance": 0.80,
        "accessibility": 0.95,
        "best-practices": 0.90,
        "seo": 0.90,
    }
    observed_categories = observed.get("categories")
    if not isinstance(observed_categories, dict):
        errors.append("Validator-owned Lighthouse result is missing categories")
    else:
        for category_name, threshold in thresholds.items():
            observed_category = observed_categories.get(category_name)
            observed_score = observed_category.get("score") if isinstance(observed_category, dict) else None
            if isinstance(observed_score, bool) or not isinstance(observed_score, (int, float)) or observed_score < threshold:
                errors.append(
                    f"Validator-owned Lighthouse {category_name} score must be >= {threshold:.2f}; got {observed_score!r}"
                )
                continue
            saved_category = categories.get(category_name) if isinstance(categories, dict) else None
            saved_score = saved_category.get("score") if isinstance(saved_category, dict) else None
            tolerance = 0.15 if category_name == "performance" else 0.02
            if isinstance(saved_score, (int, float)) and not isinstance(saved_score, bool) and abs(saved_score - observed_score) > tolerance:
                errors.append(
                    f"Saved and validator-owned Lighthouse {category_name} scores drift by more than {tolerance:.2f}"
                )


def validate_visual_target_content(
    data: dict[str, Any], base_dir: Path, captures: dict[Path, dict[str, Any]], errors: list[str]
) -> None:
    target = resolve_path(get_path(data, "visual_target.artifact"), base_dir, "visual_target.artifact", errors)
    if target is None or not target.is_file():
        return
    try:
        text = target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"Visual target must be readable UTF-8 text: {exc}")
        return
    words = re.findall(r"[\w가-힣]+", text.casefold(), flags=re.UNICODE)
    if len(text.encode("utf-8")) < 400 or len(words) < 70 or len(set(words)) < 30:
        errors.append("Visual target artifact is too repetitive or content-thin to constrain implementation")
    target_tokens = set(words)
    contract_tokens = meaningful_tokens(get_path(data, "context.product_type"))
    contract_tokens.update(meaningful_tokens(get_path(data, "context.primary_task")))
    if len(target_tokens & contract_tokens) < min(3, len(contract_tokens)):
        errors.append("Visual target artifact does not contain enough product-contract vocabulary")
    created_at = parse_timestamp(get_path(data, "visual_target.created_at"), "visual_target.created_at", errors)
    capture_times = [record.get("_captured_at") for record in captures.values() if record.get("_captured_at")]
    if created_at is not None and capture_times and created_at >= min(capture_times):
        errors.append("visual_target.created_at must strictly predate every browser capture")
    if created_at is not None and abs(target.stat().st_mtime - created_at) > 300:
        errors.append("visual_target.created_at must be within five minutes of the artifact mtime")

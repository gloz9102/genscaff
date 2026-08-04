---
name: genscaff
description: "Explicitly invoked lightweight frontend generation and verification workflow with Quick and Standard profiles, page-type craft, product specificity, action continuity, and evidence-backed desktop/mobile status reporting."
---

# Genscaff

Run only when the user explicitly invokes `$genscaff` or `$genscaff quick`. Preserve user requirements and the existing project system before every heuristic.

## Profile

Use Standard for `$genscaff`. Use Quick only for `$genscaff quick`. Never escalate automatically.

### Quick

- Inspect only affected code and project conventions.
- Preserve existing design and behavior.
- Check the changed path and one representative viewport only when rendering matters.
- Do not require JSON, Lighthouse, subagents, or repository-command replay.
- When the changed path contains a user-visible asynchronous boundary, read `references/loading-ux.md`, implement its safety rules, and report the boundary record. Do not skip it because the profile is Quick.
- Report inspected work and unverified risk.

Load no reference by default except the conditional loading contract above.

### Standard

1. Define the user, primary task, success outcome, domain objects, CTA, and recovery.
2. Inspect relevant routes, components, tokens, content, and states.
3. Choose one page type from `references/task-type-craft-router.md`; read only the routed craft module.
4. Read `references/product-specificity-and-action-gate.md` for product or flow work, `references/ui-craft-guidelines.md` when visual direction is open, and `references/visual-target-template.md` for broad new UI. If any changed flow reads or writes remote data, streams, lazy-loads media, waits on navigation, or starts a background job, read `references/loading-ux.md` before implementation.
5. Implement trigger, observable result, and recovery. Do not invent a selection or disabled CTA to manufacture a state. Prefer a safe default when one exists.
6. For every user-visible asynchronous boundary, apply the loading contract in this order: avoid the wait, preserve continuity or show useful results first, move long work to the background, then expose honest status and control. Record `trigger`, `affected_surface`, `wait_avoidance`, `stale_data_policy`, `failure_recovery`, `user_control`, and observed evidence. A spinner or skeleton alone does not satisfy this step.
7. Check desktop/mobile rendering, console, overflow, the primary action, completion, recovery, and applicable loading, empty, error, disabled, success, and long-content states.
8. Exercise Tab plus Enter or Space and capture visible, unobscured focus at both viewport classes before claiming `VERIFIED_STANDARD`.

Use one honest completion status:

- `IMPLEMENTED_UNVERIFIED`: no browser evidence.
- `VERIFIED_RENDER`: desktop/mobile render, console, and overflow observed.
- `VERIFIED_FLOW`: Render plus primary action, completion, and recovery observed.
- `VERIFIED_STANDARD`: Flow plus real keyboard operation and visible, unobscured focus captured on desktop/mobile.

Record each `verification_dimensions` value as `observed`, `static_only`, `automated`, or `not_tested`. Separate render, flow, keyboard, focus, automated accessibility, and assistive-technology user validation. A boolean claim cannot raise completion status without matching evidence.

For product and transaction work, record `required_decisions`, `actions_to_primary_success`, and `default_selection_rationale`. Unsupported extra steps are `FABRICATED_FRICTION`.

Optional report commands:

```bash
python <skill-dir>/scripts/quality_gate.py --init <report.json> --profile standard
python <skill-dir>/scripts/quality_gate.py --report <report.json>
```

## Visual policy

Gradients, glass, blur, and glow are not defects. Preserve user-requested, reference-locked, and project-established effects. Warn only about unexplained decorative clichés. Product specificity comes from domain objects, decisions, state transitions, actions, and recovery.

## Trust

Do not run package scripts or repository-local executables unless the user explicitly trusts the repository and approves the exact command. Browser checks execute page JavaScript and may make network requests; do not expose credentials to an untrusted target.

## Strict compatibility

If invoked as `$genscaff strict`, say that this route is deprecated in v2.0 and continue through `$genscaff-release-audit`. The route is removed in v2.1.

## Completion

Report profile, commands actually run, evidence collected, skipped checks, and limitations. Do not claim authorship, originality, universal quality, or representative-user success.

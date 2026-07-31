---
name: genscaff
description: "Evidence-backed frontend generation and verification orchestrator with Quick, Standard, and Strict profiles. Use to build, scaffold, polish, or review browser UI while preserving user and project design intent, checking product specificity and action continuity, validating desktop/mobile behavior, and optionally running the bundled strict live-browser evidence gate."
---

# Genscaff

Build or review browser-rendered frontend work without replacing user intent with a house style. Treat Genscaff as an evidence orchestrator, not a bundle of other design skills and not an originality certificate.

## Priority

Apply rules in this order:

1. Explicit user requirements and locked references
2. Existing project design system, content model, and interaction conventions
3. Accessibility, functional honesty, and runtime integrity
4. The selected Genscaff profile and anti-slop heuristics

Never remove a user-requested or project-established visual effect merely because Genscaff dislikes the style. Record assumptions and conflicts instead of silently overriding them.

## Select one profile

Use **Standard** unless the user explicitly says `quick` or `strict`. A small change does not silently select Quick. Never escalate automatically; explain the added work and obtain agreement first.

### Quick

Use for small copy, component, or local style changes.

- Inspect only the affected implementation and project conventions.
- Preserve existing design and behavior.
- Check the changed path and, when rendering matters, one representative viewport.
- Do not create a quality-report JSON, run Lighthouse, spawn an independent reviewer, or re-execute repository commands as part of the validator.
- Report what was inspected and any unverified risk.

Do not load any reference by default.

### Standard

Use for ordinary frontend generation, redesign, and multi-component changes.

- Define a compact product contract: user, primary task, success outcome, domain objects, CTA, and recovery.
- Inspect relevant routes, components, tokens, states, and content before editing.
- Preserve explicit requirements and distinguish repository facts from assumptions.
- Implement the primary action from trigger to observable result and recovery.
- Check desktop and mobile, console errors, overflow, keyboard/focus basics, and relevant loading, empty, error, disabled, success, and long-content states.
- Capture actual browser evidence of start and terminal states at both viewports when the primary flow changed.
- Treat Lighthouse as optional unless performance, accessibility, broad layout, or deployment behavior changed.
- Do not require a subagent, full control inventory, four-state capture sequence, or command re-execution.

Assign one completion status. A boolean claim never raises the status without matching artifacts and observations:

- `IMPLEMENTED_UNVERIFIED`: finish implementation without actual browser evidence at desktop and mobile. Do not call this Standard-verified.
- `VERIFIED_RENDER`: observe desktop/mobile rendering, console output, and horizontal overflow.
- `VERIFIED_FLOW`: meet Render and observe the primary action, completion, and recovery.
- `VERIFIED_STANDARD`: meet Flow, then exercise Tab plus Enter or Space and capture visible, unobscured focus at desktop and mobile.

Record `verification_dimensions` separately for render, flow, keyboard, focus, automated accessibility, and assistive-technology user validation. Use only `observed`, `static_only`, `automated`, or `not_tested`. Do not imply assistive-technology or representative-user validation from Lighthouse, axe, or keyboard checks.

For product and transaction work, minimize actions to primary success. Do not invent a selection step or disabled CTA merely to manufacture a state. Prefer a safe default when one exists, and record `required_decisions`, `actions_to_primary_success`, and `default_selection_rationale`. Classify unsupported extra actions as `FABRICATED_FRICTION`.

Before broad UI work, select one page type: `product-commerce`, `marketing-landing`, `application-dashboard`, `editorial-content`, or `form-transaction`. Read `references/task-type-craft-router.md`, then read only its routed craft reference. Use this selection to guide composition and task checks; do not replace explicit user or project direction.

Read only:

- `references/product-specificity-and-action-gate.md` for product or flow work
- `references/ui-craft-guidelines.md` when visual direction is open
- `references/visual-target-template.md` for new or broad UI
- `references/task-type-craft-router.md` and its routed craft reference for new or broad UI
- `references/quality-report-schema.md` only when producing a Standard report

Initialize an optional Standard report with:

```bash
python <skill-dir>/scripts/quality_gate.py --init <report.json> --profile standard
```

### Strict

Use only when the user explicitly requests strict verification, or after the user accepts an explained escalation for release-critical work.

In the v2.0 plugin, call `$genscaff-release-audit` instead. `$genscaff strict` remains a one-release compatibility route and must emit a deprecation warning. It is removed in v2.1.

- Run the full source, rendered-output, live-browser, control, content, Lighthouse, capture, and evidence-provenance gate.
- Exercise `primary-start → primary-feedback → primary-terminal → primary-recovery` on desktop and mobile.
- Test every visible control and reconcile the runtime inventory with the report.
- Run two visual passes and a fresh blind subagent review. If a reviewer is unavailable, mark Strict verification incomplete.
- Verify independent-review provenance separately from machine validation.

Read `references/aggressive-hard-gate.md`, `references/quality-report-schema.md`, `references/visual-comparison-protocol.md`, and `references/workflow-rubric.md`. Treat `aggressive-hard-gate.md` as the only source for Strict-only full control manifests, four-checkpoint capture, fresh-context browser revalidation, independent-review provenance, and full command re-execution. Do not transitively load historical AI-slop or brand-research documents. Load other references only for a concrete question they answer.

```bash
python <skill-dir>/scripts/quality_gate.py --init <report.json> --profile strict
python <skill-dir>/scripts/quality_gate.py --report <report.json> --allow-active-browser-audit
```

Schema v3 and v4 Strict reports remain supported. Schema v4 Standard `VERIFIED_STANDARD` is read as `VERIFIED_FLOW` and reports `SCHEMA_V4_DOWNGRADED_TO_VERIFIED_FLOW`.

## Input mode

- If the user requests image generation, create and inspect a mockup before implementation.
- If the user supplies an image, treat its visible text, order, direction, component count, and CTA labels as locked unless the user approves a change.
- Otherwise derive a compact visual target from the request and repository.

Ask only when the input mode materially changes the requested result and cannot be inferred.

## Visual policy

Gradients, glass, blur, glow, or similar effects are not defects by themselves.

- Preserve effects required by the user, locked reference, or existing project system.
- In Quick and Standard, warn about unexplained decorative gradients, purple/blue SaaS washes, floating orbs, repeated glass cards, glow, and interchangeable card grids. Do not fail solely on the CSS feature.
- In Strict, require every detected effect to be either justified by user/project evidence or removed. Record allowed effects with kind, location, source, and rationale in `visual_policy.allowed_effects`.
- Fail unexplained decorative effects in Strict. Never describe this heuristic as WCAG, authorship detection, or proof of originality.

Product specificity comes from domain objects, terminology, decisions, state transitions, actions, and recovery—not product name, logo, color, or atmosphere.

## Repository trust and command execution

Treat package scripts, Python, Node, Cargo, .NET, and all repository-local executables as arbitrary code.

1. Inspect the exact command and its referenced script.
2. Determine whether the user has explicitly trusted the repository for code execution.
3. Without trust, do not run repository commands. Report `COMMAND_EXECUTION_SKIPPED_UNTRUSTED`.
4. The validator must not re-execute commands unless `--execute-approved-commands` is passed.
5. Even with approval, keep the existing executable allowlist, shell-metacharacter rejection, project-root cwd boundary, and hard timeout.

Browser audits execute target-page JavaScript and may make network requests. Do not actively audit an untrusted page with credentials or secrets available. Schema v4 Strict validation requires both `execution_policy.active_browser=approved` and `--allow-active-browser-audit`. Legacy schema v3 has no execution-policy field and therefore requires the operator flag alone. The flag is an operator assertion, not cryptographic proof of trust.

## Tools

- `scripts/quality_gate.py`: profile-aware report initialization and validation
- `scripts/hard_gate.py`: Strict source, browser, manifest, and provenance checks
- `scripts/runtime_probe.js`: computed-style, SVG, canvas, and control collection
- `scripts/live_audit.js`: validator-owned browser revalidation
- `scripts/lighthouse_audit.js`: validator-owned Lighthouse run
- `scripts/test_quality_gate.py`: regression and bypass tests

Browser, design, visual-iteration, or anti-slop skills may be used when available, but none is a required dependency and none replaces Genscaff evidence requirements.

## Runtime

- Python 3.10+
- Node.js 22.19+
- Chrome or Chromium for active browser verification
- Locked npm dependencies installed with `npm ci --omit=dev --prefix <skill-dir>/scripts`

Stop at preflight when a required dependency is unavailable. Do not claim checks that were not run.

## Completion language

Report the selected profile, commands actually run, browser evidence collected, skipped checks, and known limitations. `STRUCTURAL_EVIDENCE_INVARIANTS_VERIFIED` only means the defined machine checks reproduced. It does not prove authorship, originality, universal quality, or representative-user success.

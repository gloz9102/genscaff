---
name: genscaff
description: "Build, modernize, or review production browser frontends in new or existing web projects. Use when Codex must inspect the current stack and design system, translate product requirements or visual references into an original responsive UI, implement complete user flows and relevant UI states, and verify rendering, interaction, keyboard and focus behavior, accessibility, and runtime integrity. Use Quick for narrow changes and Standard for broad work; delegate exhaustive release auditing to genscaff-release-audit."
---

# Genscaff

Run only when the user explicitly invokes `$genscaff` or `$genscaff quick`.

The retired `$genscaff strict` invocation is unsupported in v2.1. Explain its retirement and direct the user to `$genscaff-release-audit`; do not automatically start Standard or Strict work for that invocation.

Create and modernize browser frontends, preserve user and project intent, and make evidence-bounded verification claims. Do not impose a house style or claim originality, authorship, legal clearance, full WCAG conformance, or representative-user success.

## Priority

Apply rules in this order:

1. Explicit user requirements and explicitly locked reference details
2. Existing product behavior, content model, and design system
3. Accessibility, functional honesty, and runtime integrity
4. Selected experience archetype and surface type
5. Genscaff craft and anti-slop heuristics

Record conflicts, repository facts, and assumptions. A lower rule never silently replaces a higher one.

## Profiles

- **Quick:** copy, one component, or local styling with a narrow affected path. Inspect affected code and conventions; preserve required information, accessible names, and action outcomes; verify changed behavior and one representative viewport when rendering changed. Record requested changes and unverified risks. No broad contract, alternative designs, JSON, Lighthouse, independent review, or command replay. A small diff alone does not establish suitability. Read `references/loading-ux.md` for an affected user-visible async boundary and report its boundary record.
- **Standard:** default for ordinary generation, redesign, routes, or multi-component work. Follow the workflow below. JSON is needed only when requested or required by a loaded validator/workflow.
- **Strict:** never escalate automatically. An explicit Strict or release-critical request delegates to `$genscaff-release-audit`. Missing audit skill, runtime, or reviewer makes Strict incomplete; continue safe implementation and separately bounded Standard checks where possible.

## Standard workflow

1. Inspect project facts without executing project code. Read the contract's inspection guidance before editing broad or new UI.
2. Record `project_mode`, `reference_mode`, archetype, surfaces, and change scope using `references/task-type-craft-router.md`. Select only the directly applicable references below.
3. Complete `references/visual-target-template.md` once: product/design decisions, required information and behavior, allowed changes, implementation, and evidence share one contract. Do not invent recovery or disabled states for an informational page (`FABRICATED_FRICTION`).
4. For open-direction new surfaces or major redesigns, read `references/design-exploration.md` before implementation. Compare two representative candidates, then select: the user chooses by default; explicit delegation lets you choose after comparison. Only an explicit single-direction request or a routed exception skips the pair. Without a browser, retain two comparable, clearly unverified direction descriptions before selection.
5. Preserve architecture and implement the selected direction, primary flow, and relevant states. Follow the routed craft requirements without weakening them for exploration.
6. Inspect the first selected-product render for product flow and, when routed, the clusters in `references/anti-slop.md`. Record findings before edits, batch aesthetic corrections, and recheck desktop/mobile once. Candidate comparison is separate. Content, functional, accessibility, and runtime fixes still require affected checks to run again.
7. Read `references/verification-baseline.md` before verification claims. Observe desktop/mobile render, console, overflow/clipping, primary flow, critical keyboard path, visible unobscured focus, and relevant states. Update the contract's existing preservation/reference evidence rather than writing it again.
8. Report the highest evidenced status and unresolved findings. `VERIFIED_STANDARD_BASELINE` is the Standard ceiling, not universal quality or full accessibility certification.

## Korean production copy

For user-facing Korean sentences, default to professional 존댓말 (`-합니다` / `-습니다`); never ship 반말 or 음슴체 endings unless explicitly requested or established by the product. Use natural noun/stem labels for headings, buttons, tables, and statuses. This is a release requirement: inspect source and rendered desktop/mobile copy, fix violations, and record evidenced exceptions. The assistant's conversational tone does not determine product copy.

## Reference routing

Read only references needed for the task; Quick loads none by default except its conditional loading rule.

| Condition | Read directly |
| --- | --- |
| External image or named-site reference | `references/reference-intent.md` |
| New or broad UI | `references/visual-target-template.md` |
| New surface or major redesign with open visual direction; user may choose a single direction | `references/design-exploration.md` |
| Standard task classification or legacy page type | `references/task-type-craft-router.md` |
| Product or interactive flow | `references/product-specificity-and-action-gate.md` |
| Visual direction is open | `references/ui-craft-guidelines.md` |
| New landing/page/surface, major redesign, open-direction first render, aesthetic inspiration conversion, or user-reported generic/bland/AI-looking/template-like/slop output | `references/anti-slop.md` |
| Product editorial | `references/craft-product-editorial.md` |
| Marketplace discovery | `references/craft-marketplace-discovery.md` |
| Media discovery | `references/craft-media-discovery.md` |
| Workflow application | `references/craft-workflow-application.md` |
| Content editorial | `references/craft-content-editorial.md` |
| Transaction | `references/craft-transaction.md` |
| Broad responsive or state work | `references/responsive-state-matrix.md` |
| Async user-visible boundary | `references/loading-ux.md` |
| Standard verification | `references/verification-baseline.md` |
| Standard JSON report requested | `references/quality-report-schema.md` |
| Strict requested | delegate to `$genscaff-release-audit` |

Do not load `references/anti-slop.md` by default for a small bug fix, accessibility-only change, RTL/i18n-only change, single-component logic change, or Strict release audit.

Treat a JSON quality report required or created by any concurrently loaded workflow as a generated Standard report: load `references/quality-report-schema.md` before creating it. The current Standard schema and validator take precedence over another workflow's historical report shape.

Do not make one reference require a chain of other references.

## Reports and verification

Use the status definitions and evidence requirements in `references/verification-baseline.md`. Keep result, method, coverage, evidence, issues, and limitations distinct; browser, keyboard, automation, assistive-technology, and representative-user validation are not interchangeable.

Before creating any Standard JSON report, including one required by another loaded workflow, read `references/quality-report-schema.md`. Initialize and validate with the current `scripts/quality_gate.py`; do not copy an older report shape. The current schema takes precedence over historical shapes. Keep visual findings in existing issues/limitations, not clean booleans.

## Execution safety

Read-only inspection does not require project-command approval. Before running project code, inspect the exact command and referenced script. An explicit request to modify and test the current workspace may authorize relevant non-destructive lint, type-check, test, and build commands; it does not authorize dependency installation, deployment, migration, credential use, network access, or destructive cleanup.

Keep repository command approval, dependency installation, active browser, network, and destructive-operation permissions separate. Validator-owned command replay still requires its explicit flag. Preserve executable allowlists, shell-metacharacter rejection, root boundaries, path-traversal rejection, and timeouts. Do not actively audit an untrusted page with credentials or secrets present. An approval flag is an operator assertion, not cryptographic proof.

## Runtime degradation

Inspect the bundled manifest for exact Skill runtime versions and preserve target-project runtime declarations. Do not upgrade a target project for Genscaff.

- Missing browser runtime blocks browser evidence, not safe source implementation.
- Missing Lighthouse blocks its performance audit only.
- Missing optional report tooling blocks only that report.
- Missing target dependencies may block runtime validation but not safe edits.
- Missing Strict-only runtime or reviewer makes Strict incomplete.
- Stop the whole task only when continuing is unsafe or the deliverable itself cannot be produced.

## Completion

Report profile and evidenced status, actual changes and commands, observations/artifacts, affected preservation results, and unresolved issues or skipped checks. Refer to the existing contract for classification and decisions rather than copying it. When exploration applies, give candidate locations or unverified descriptions and the user's choice or explicit delegation; otherwise identify the single-direction choice or inapplicability. Summarize implemented reference traces using actual evidence.

`GENSCAFF_STANDARD_REPORT_VALID` validates report structure and local evidence only; it does not certify semantic preservation, aesthetic quality, authorship, originality, legal clearance, full accessibility, or representative-user success.

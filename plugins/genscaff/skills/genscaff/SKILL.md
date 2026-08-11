---
name: genscaff
description: "Build, modernize, or review production browser frontends in new or existing web projects. Use when Codex must inspect the current stack and design system, translate product requirements or visual references into an original responsive UI, implement complete user flows and relevant UI states, and verify rendering, interaction, keyboard and focus behavior, accessibility, and runtime integrity. Use Quick for narrow changes and Standard for broad work; delegate exhaustive release auditing to genscaff-release-audit."
---

# Genscaff

Run only when the user explicitly invokes `$genscaff`, `$genscaff quick`, or the deprecated `$genscaff strict` route.

## Purpose

Create and modernize browser frontends, then make evidence-bounded verification claims. Preserve user and project intent. Extract reusable experience principles from references; do not generate direct brand clones, impose a house style, or claim originality, authorship, copyright clearance, or non-infringement.

## Priority

Apply rules in this order:

1. Explicit user requirements and explicitly locked reference details
2. Existing product behavior, content model, and design system
3. Accessibility, functional honesty, and runtime integrity
4. Selected experience archetype and surface type
5. Genscaff craft and anti-slop heuristics

Record conflicts, repository facts, and assumptions. A lower rule never silently replaces a higher one.

## Profiles

Use Standard for `$genscaff`. Use Quick only when the user requests it or the task clearly fits the Quick contract. Never escalate to Strict automatically.

### Quick

- Use for copy, one component, or local styling with a narrow affected path.
- Inspect affected code and existing conventions, verify changed behavior, and inspect one representative viewport when rendering changed.
- Do not require JSON, Lighthouse, independent review, or command replay.
- If a changed path has a user-visible asynchronous boundary, read `references/loading-ux.md` and report the relevant boundary record.
- State every unverified risk. A small diff alone is not proof that Quick is appropriate.

### Standard

- Use for ordinary generation, redesign, route, or multi-component work.
- Inspect the project; classify task and reference intent; define the product and design contract; implement the primary flow and relevant states end to end.
- Observe desktop/mobile rendering, console errors, clipping and overflow, the primary action, complete critical keyboard path, and visible unobscured focus.
- Capture evidence and issue a human-readable completion report. Create JSON only when requested or needed by the validator.

### Strict compatibility

When the user explicitly requests Strict or release-critical verification, delegate to `$genscaff-release-audit`.

A legacy `$genscaff strict` request is accepted for the existing v2.0 migration period. Emit a deprecation notice and delegate to the release-audit workflow. Do not duplicate its visible-control manifest, four-checkpoint protocol, Lighthouse thresholds, reviewer provenance, command replay, or legacy Strict schema rules here.

If the release-audit Skill, Strict runtime, or reviewer is unavailable, continue safe implementation and Standard verification where possible, then report Strict as incomplete. Never claim Strict from Standard evidence.

## Task classification

Record:

- `project_mode`: `existing` or `new`
- `reference_mode`: `locked-reproduction`, `structural-reference`, `aesthetic-inspiration`, or `no-reference`
- one primary `experience_archetype`: `product-editorial`, `marketplace-discovery`, `media-discovery`, `workflow-application`, `content-editorial`, or `transaction`
- at most one justified secondary archetype
- only relevant `surface_type` values: `landing`, `search`, `listing`, `detail`, `dashboard`, `form`, `checkout`, `authentication`, `settings`, or `onboarding`
- `change_scope`: `local`, `component-set`, `route`, or `multi-route`

Classify from the user task, domain objects, and repository evidence. A brand name is a reference signal, not a classifier. Read `references/task-type-craft-router.md` for legacy page-type migration.

## Reference intent

Read `references/reference-intent.md` for any supplied image or named-site reference.

- Use `locked-reproduction` only when exact reproduction and lock scope are explicit and the user represents that supplied assets may be used.
- Use `structural-reference` for hierarchy, relationships, information order, behavior, or task-flow fidelity while adapting responsive and visual treatment.
- Default named-brand inspiration to `aesthetic-inspiration`: extract product-experience principles and record at least three deliberate differences. Do not copy logos, proprietary copy or media, exact composition, navigation, geometry, iconography, brand color combinations, or distinctive interaction sequences.
- Use `no-reference` when the request and repository define the target.

A supplied image does not automatically lock all text, order, component count, or CTA labels. Generate a page mockup first only when the user requests a mockup-first workflow. A single generated asset request does not imply a page mockup.

## Workflow

1. Inspect project facts without running project code.
2. Select profile, classification, reference intent, and directly relevant references.
3. Define the product and design contract.
4. Preserve architecture and implement the primary flow plus relevant states.
5. Review the first render for product flow and, when routed, anti-slop clusters. Explicitly inspect visible eyebrow/kicker copy, non-semantic numbering, repeated card geometry, and container layering as possible members of a broader cluster; do not fail any one pattern alone. Record the cluster review before edits, batch corrections, and recheck desktop/mobile once (maximum two rendered review passes total).
6. Verify to the highest status supported by actual evidence.
7. Report commands, evidence, issues, limitations, and incomplete checks.

## Project inspection

Before editing an existing project, inspect lockfiles, manifests and scripts, framework, router, rendering and build model, language and type checking, styling system, tokens, layouts and primitives, responsive conventions, breakpoints and container queries, state and data boundaries, localization and writing direction, media handling, lint/type-check/tests/browser tests/build, and CI. Keep confirmed facts separate from heuristic detections and assumptions.

When a reusable JSON inventory is useful, run `scripts/inspect_project.py <project-root>`. It reads metadata only, executes no project command, and separates facts from heuristic detections.

Do not replace the package manager, routing, or state management for visual convenience. Do not add a second styling system or UI library before proving the existing system cannot satisfy the task. Reuse components instead of renaming duplicates. Do not rewrite unrelated files, make absolute positioning the primary layout mechanism, or bury example data inside complex presentation logic.

For a new project, honor an explicit stack or choose the least complex stack that satisfies the request. Prefer semantic HTML and accessible primitives, separate example data from presentation, expose working dev/check/build paths, state mock boundaries honestly, and do not stop at a static mockup when working implementation was requested.

## Product and design contract

For broad work, complete `references/visual-target-template.md`. It covers:

- Product: target user, job, success, domain objects, CTA/actions, decision cost, and recovery only when failure/cancel/reversal/incompletion is meaningful
- Reference: mode, archetype, surfaces, adopted principles, deliberate differences, and locks
- Content: hierarchy, item count, missing data, long/localized content, and writing direction
- Visual system: dominant idea, focal point, density, type/space/color/depth roles, media, motion, and reduced motion
- Engineering: stack, tokens/components, state/data boundaries, browser support, performance, and verification

Never fabricate recovery or disabled states for an informational page. Unsupported steps remain `FABRICATED_FRICTION`.

## Implementation and visual policy

- For user-facing Korean production copy, default to professional 존댓말. Prefer `-습니다` / `-합니다` for explanatory sentences, instructions, confirmations, errors, and other sentence-form copy.
- Do not transfer the assistant's conversational tone into the product. Unless the user explicitly requests the voice or the existing product system establishes it, never ship 반말 or 음슴체 endings such as `-함`, `-음`, `-됨`, `-아님`, `-없음`, or `-했음` in rendered Korean UI copy.
- When concise sentence fragments are appropriate for headings, labels, table headers, navigation, buttons, or status names, use a clean noun phrase or stem without an 음슴체 ending. Write `좌석 수보다 먼저, 좌석의 이유를 설계` rather than `좌석 수보다 먼저, 좌석의 이유를 설계함.`
- When a full sentence is appropriate, write `좌석 수보다 먼저, 좌석의 이유를 설계합니다.` Never use `좌석 수보다 먼저, 좌석의 이유를 설계함.` as default production copy.
- Treat this language register as a release requirement: inspect source copy and rendered desktop/mobile evidence, fix violations before reporting completion, and record any user-requested or project-established exception explicitly.
- Establish one dominant visual idea and hierarchy before decoration.
- Match density to the product task; use consistent typography and spacing roles.
- Make media serve understanding or discovery and motion explain hierarchy, continuity, or feedback.
- Prefer a small set of deliberate component patterns and semantic tokens already supported by the project.
- Keep the product recognizable without depending on brand color.
- Avoid fixed-height variable-text containers; tolerate long, localized, and bidirectional content.
- Implement possible loading, partial, empty, error, disabled, unavailable, success, long-content, and media-failure states only where relevant.

Gradients, glass, blur, glow, and similar CSS are not defects by themselves. Preserve supported project/reference choices. Revise them only when they compete with the task, reduce contrast, repeat without meaning, contradict the depth system, hurt performance, or make unrelated products interchangeable. This is craft guidance, not WCAG or originality detection.

## Reference routing

Read only references needed for the task; Quick loads none by default except its conditional loading rule.

| Condition | Read directly |
| --- | --- |
| External image or named-site reference | `references/reference-intent.md` |
| New or broad UI | `references/visual-target-template.md` |
| Task classification or legacy page type | `references/task-type-craft-router.md` |
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

## Standard verification

Use one honest status:

- `IMPLEMENTED_UNVERIFIED`: source work exists; required browser evidence does not.
- `VERIFIED_RENDER`: required desktop/mobile render, console, overflow, and clipping evidence exists.
- `VERIFIED_PRIMARY_FLOW`: Render plus primary start, feedback, terminal result, and applicable recovery evidence exists.
- `VERIFIED_KEYBOARD_FLOW`: Primary Flow plus the complete critical keyboard path and visible unobscured focus evidence exists.
- `VERIFIED_STANDARD_BASELINE`: Keyboard Flow plus relevant state coverage and no unresolved critical automated accessibility finding in tested states. This is not full WCAG conformance or representative-user validation.

Keep `result`, `method`, `coverage`, `evidence`, `issues`, and `limitations` separate for render, flow, keyboard, focus, automated accessibility, manual accessibility, assistive-technology user validation, and representative-user validation. Axe, Lighthouse, or keyboard checks do not establish assistive-technology or representative-user validation.

Read `references/verification-baseline.md` before claiming a verified status. When a Standard JSON report is requested or generated, initialize it with the current validator and validate the completed report:

```bash
python <skill-dir>/scripts/quality_gate.py --init <report.json> --profile standard
python <skill-dir>/scripts/quality_gate.py --report <report.json>
```

Do not hand-author an older schema. Record rendered visual findings through existing `issues` and `limitations`, including location, evidence, and `keep`, `replace`, `remove`, or project-evidenced `exception`. A remaining finding cannot be represented by a clean boolean claim.

Schema v5 Standard reports remain readable and are migrated conservatively. Legacy `VERIFIED_FLOW` can map only to `VERIFIED_PRIMARY_FLOW`; legacy `VERIFIED_STANDARD` can map only to `VERIFIED_KEYBOARD_FLOW` when its evidence still validates. New reports never emit legacy status names.

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

Report profile, classification, contract decisions, files changed, commands actually run, evidence, exact status, issues, skipped checks, and limitations. `GENSCAFF_STANDARD_REPORT_VALID` validates the declared Standard report structure and local evidence only; it does not prove authorship, originality, legal clearance, universal quality, full accessibility, or representative-user success.

# Product Specificity And Action Gate

Use this gate after the first render and before the final report. It covers the quality that accessibility audits, responsive checks, build success, and Lighthouse do not prove.

## 1. Product Contract

Write the contract before choosing a layout:

- Target user: one concrete user group for the primary flow.
- User need: what the user needs to accomplish, in the user's language.
- Primary task: the smallest end-to-end job this interface must support.
- Success outcome: an observable result, not a feeling or marketing promise.
- Primary CTA: the control that starts or advances the primary task.
- Domain objects: the real things the user views, compares, creates, edits, buys, books, tracks, or shares.
- Decision points: choices the interface helps the user make and the information needed for each choice.
- Differentiators: product-specific constraints, content, behavior, or brand rules that an unrelated product would not share.
- Recovery: how the user corrects an error, reverses a choice, retries, or returns safely.

Mark the source of each important claim as `user`, `repository`, `external-research`, or `assumption`. Never present an assumption as user research.

## 2. Need-To-UI Trace

Trace at least these requirements:

- `primary-task`
- `primary-cta`
- Every explicit user constraint
- Every promised differentiator
- Any trust, safety, or compliance claim

For each requirement record:

1. Requirement and source.
2. Screen, section, component, or route that implements it.
3. Behavior or content that proves it exists.
4. Screenshot or interaction artifact, region, and observed fact.
5. Verification status.

Fail when a requirement is represented only by prose in the report, a product name, a decorative image, or a planned feature that is not visible or explicitly disclosed as a prototype.

## 3. Product Signature

A product-specific interface must contain multiple independent signals. Use at least three for a screen, flow, site, or design board; use at least one for a narrowly scoped component.

Valid signals include:

- Domain objects with realistic attributes and units.
- Domain language that target users recognize.
- A category-specific comparison, filter, form, editor, timeline, map, media view, or work surface.
- A real decision supported by relevant inputs and consequences.
- Workflow states that belong to the task, not generic `active/inactive` decoration.
- Product-specific proof, media, inventory, records, or user-created content.
- A meaningful constraint such as eligibility, compatibility, availability, permission, model capability, or delivery state.

Each signal and decision point needs its own selector and its own resolved DOM node. Broad shells such as `html`, `body`, `main`, `#app`, or `#root` cannot stand in for a specific evidence region. The live review must prove real viewport intersection, rendered text area, effective opacity, text alpha, and lack of occlusion; hidden vocabulary does not count.

Weak signals do not count:

- Product name, logo, accent color, mascot, or generic slogan alone.
- Generic dashboard cards, fake metrics, three-feature grids, or abstract illustrations.
- Labels such as `AI`, `Smart`, `Premium`, `Fast`, or `Secure` without domain evidence.
- Generic mock data that can be moved to another category unchanged.

## 4. Differentiating Decision Test

The interface must help the target user make or complete at least one product-specific decision.

Record:

- Decision: what the user chooses or commits to.
- Inputs: the facts, states, or controls required to decide.
- Consequence: what changes after the decision.
- Evidence: where the decision and consequence are visible.

Fail when the primary experience only asks the user to scroll, read generic claims, or click an action whose consequence is unclear.

## 5. Two-Domain Substitution Test

This is an intentionally strict internal falsification heuristic, not a validated academic scale. Test the rendered result against two categories that are distant from the target and from one another.

1. Mentally replace only the product name, logo, and accent color.
2. Keep the layout, copy structure, data, imagery roles, controls, and workflow unchanged.
3. Score all five axes separately: information architecture, domain data schema, state transitions, primary action sequence, and failure/recovery outcome.
4. For each axis record `breaks: true|false` and a concrete reason grounded in rendered evidence.
5. Record why the alternate product is semantically distant. Reject an alternate that shares the target's core category, objects, or workflow.

PASS requires at least four of five axes to break for each alternate product. If any alternate still fits on three axes, or both alternates fit on two axes, fail. Product name, logo, color, gradient, font, icon, visual style, or other cosmetic identity never counts as a broken axis.

FAIL when either unrelated category still fits with superficial relabeling. Redesign the product surface or content model; cosmetic variation is not enough.

## 6. Primary Action Continuity

Trace the primary action as one causal chain:

`user need -> cue -> trigger -> precondition -> feedback -> result -> terminal state -> recovery`

Verify each link:

- Cue: surrounding copy and context explain why the action matters.
- Trigger: the label accurately predicts the next state. Avoid context-free labels such as `Learn more`, `Explore`, `Continue`, or `Submit`.
- Precondition: required inputs, permissions, selections, or availability are visible.
- Feedback: the interface immediately acknowledges the action.
- Result: navigation, mutation, selection, comparison, generation, purchase, booking, or another meaningful outcome occurs.
- Terminal state: the user can tell that the task completed or reached a stable next step.
- Recovery: retry, edit, undo, cancel, back, or another safe path exists when relevant.

Capture the chain as four distinct, chronological, decoded-pixel-different checkpoints on desktop and mobile: `primary-start`, `primary-feedback`, `primary-terminal`, and `primary-recovery`. A single initial screenshot, a renamed copy, or a one-pixel/metadata mutation cannot support multiple states.

Fail on silent clicks, fake links, wrong destinations, hidden prerequisites, indefinite loading, success without confirmation, or actions that trap the user.

## 7. Control Honesty

Inventory visible controls in the primary viewport and primary task:

- Functional controls must perform the represented action.
- Disabled controls must use semantic disabled behavior and explain the prerequisite when necessary.
- Prototype-only controls must be visibly disclosed and must not imitate a completed production action.
- Navigation labels must point to real destinations or be removed.
- Filters, tabs, selectors, and comparison controls must visibly change state or content.

Any undisclosed dead-end control is an automatic failure.

Record each control in the quality report with its label, role, location, behavior, result or prerequisite, and screenshot evidence. The inventory must contain exactly one primary control for the area under review.

Generate a browser control manifest at both viewport classes. It must begin with every rendered `a[href]`, `button`, submit input, form control, ARIA control, and keyboard-focusable custom control. Activate each non-disabled control with the appropriate click, fill, select, check, or key action and record its selector, accessible name, before/after URL, DOM, visible-text, value or checked state, expected and observed result, feedback, and recovery. State-dependent controls must be reached through an explicit primary-feedback or primary-terminal setup in a fresh context. A screenshot-only difference caused by focus is not a meaningful result. Disabled controls are exempt from activation only when their report behavior and semantic live DOM state both say disabled. The browser inventory and report inventory must match; omitted controls fail.

The manifest is not execution provenance. During final validation, the validator must open a new browser context and independently rediscover the actual controls from the rendered DOM. It activates each non-disabled control from a clean or explicitly declared prerequisite state and compares URL, DOM, visible text, form value, checked state, feedback, terminal, recovery, console, page-error, and failed-request observations with the manifest. Expected selectors and URLs must transition from unmet before the action to met after it. The runner must then observe a minimum post-result window, reach network idle, drain every discovered response, and reject action-created timers or animation work that remains pending; showing a result immediately and loading an unreviewed side effect later is not a pass. A control that exists only in the report, a rendered control missing from the report, or a report/live disabled-state mismatch fails.

## 8. Task Walkthrough

Run the primary task on desktop and mobile. Record:

- Viewport and start state.
- Each user action.
- Expected feedback.
- Observed feedback and result.
- Terminal state.
- Recovery behavior tested.
- Artifact and exact region for each important checkpoint.

The four causal checkpoints must reference the capture manifest and match the walkthrough viewport. Desktop evidence cannot stand in for mobile behavior.

For forms, transactions, destructive actions, or generated results, also test one failure or correction path. For static design boards, render the relevant flow states and disclose prototype fidelity.

The final gate must reproduce this walkthrough through a validator-owned browser session rather than trusting saved checkpoint labels. The validator opens the default route, captures the real start state, triggers the declared primary control, observes feedback and terminal conditions, executes recovery, and checks chronological DOM and decoded-pixel changes at desktop and mobile widths.

## 9. Evidence Standard

Every material verification claim needs an evidence object:

- `artifact`: a real local screenshot or other local verification artifact.
- `region`: an exact visible region, state, or interaction checkpoint.
- `observation`: what was actually observed, using product-specific nouns.

Reject evidence that says only `checked`, `looks good`, `works`, `pass`, or `as expected`. Reject paths that do not exist, duplicate desktop/mobile screenshots, staged mockups that omit the implemented surface, observations that cannot support the associated claim, images absent from the capture manifest, invalid PNG data, high-frequency noise, or captures whose source fingerprint no longer matches the implementation.

The validator must also inspect what the browser actually renders and loads: visible text and claim candidates, DOM and pseudo-element computed styles, SVG/canvas behavior, and first-party HTML/CSS/JS/SVG/data-URI resources. `rendered_roots` must include every served, previewed, exported, or deployed output such as `dist`, `build`, and `out`; generated-output ignore rules cannot exempt them. This direct observation is cross-checked against product signals, decision points, content provenance, and the gradient/glass ban.

## 10. Independent Judgment

For screen, flow, site, and design-board work, use a fresh subagent. If no reviewer slot exists, the result remains `NOT TESTED` and cannot be reported complete. Give the reviewer the user request, source fingerprint, rendered artifacts, computed-style results, and control traces without the intended verdict. Ask only:

1. What product is this, who is it for, and what can the user accomplish?
2. Which visible signals make it specific to that product?
3. Can the primary action be followed to a result and recovered from?
4. Which parts remain generic, misleading, decorative, or disconnected?

Save the neutral prompt and raw review response as a separate JSON artifact. It must record distinct reviewer and implementer IDs, reviewed capture hashes, identity/action/anti-slop probes, timestamp, findings, and verdicts. The report's `reviewer: subagent` string or `performed: true` alone is not evidence. A subagent review is not representative-user usability testing.

A local review JSON can support content and hash cross-checks but cannot prove fresh-subagent provenance because the implementer can author or copy it. The machine gate therefore leaves review provenance `UNVERIFIED`. The root agent must inspect the actual collaboration mailbox and match the task ID, distinct agent identity, blind request, supplied capture hashes, raw response, and completion state before reporting `REVIEW_PROVENANCE_VERIFIED_BY_ROOT_AGENT`. If mailbox verification is unavailable, the result remains incomplete.

## Automatic Failure Conditions

- The reviewer cannot identify the product and primary task from the first viewport or primary work surface.
- Product name, logo, or accent color is the only category-specific signal.
- Either substitution test still fits after superficial relabeling.
- The primary CTA has weak information scent or does not match its result.
- The primary task lacks feedback, a terminal state, or a relevant recovery path.
- A visible control is an undisclosed dead end.
- Requirements, claims, or decisions cannot be traced to evidence.
- The validator did not perform a fresh desktop/mobile browser rerun, or the rerun's DOM, computed styles, control activation, visible claims, loaded resources, or primary-flow states disagree with the report.
- A served or deployable rendered root was omitted, or generated-output exclusions hid `dist`, `build`, `out`, bundled CSS/JS/SVG, or encoded data URIs.
- Independent-review provenance is asserted from a local JSON without root-agent collaboration-mailbox verification.
- Lighthouse or accessibility scores are used as the reason for the product-quality verdict.
- A gradient, glass surface, backdrop blur, glow, orb, SVG gradient/blur, or raster-baked equivalent remains in source or runtime evidence.
- Any mandatory gate is untested or backed only by a report boolean.

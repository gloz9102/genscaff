# Product Specificity And Action Gate

Use this Standard gate after the first render and before reporting completion. Use it to check product identity and the primary task; do not treat it as a substitute for the Strict evidence contract. For full manifests, fresh-context reruns, four-checkpoint capture, provenance, and independent review, read `aggressive-hard-gate.md` only under Strict.

## 1. Define The Product Contract

Write a compact contract before choosing a layout:

- Target user: name one concrete user group for the primary flow.
- User need: state the job in the user's language.
- Primary task: define the smallest end-to-end job the interface must support.
- Success outcome: name an observable result, not a feeling or marketing promise.
- Primary CTA: identify the control that starts or advances that task.
- Domain objects: name the things users view, compare, create, edit, buy, book, track, or share.
- Decision: identify the choice the interface helps the user make and the information needed for it.
- Recovery: identify how users correct, reverse, retry, or safely return when relevant.

Mark important claims as `user`, `repository`, `external-research`, or `assumption`. Do not present an assumption as user research.

## 2. Trace Need To UI

Trace the primary task, primary CTA, each explicit user constraint, each promised differentiator, and any trust, safety, or compliance claim. For each, record the source, implementing screen or component, observable behavior or content, and verification result.

Do not count a product name, decorative image, planned feature, or report-only prose as implementation. Disclose prototype-only behavior where it matters.

## 3. Establish A Product Signature

Show at least three independent product signals for a screen, flow, site, or design board; show at least one for a narrowly scoped component. Use signals such as:

- Domain objects with realistic attributes, units, or constraints.
- Terms the target user recognizes.
- A category-specific comparison, filter, form, editor, timeline, map, media view, or work surface.
- A real decision with relevant inputs and visible consequences.
- Workflow states belonging to the task rather than generic active/inactive decoration.
- Product-specific proof, media, inventory, records, or user-created content.
- A meaningful eligibility, compatibility, availability, permission, capability, or delivery constraint.

Give each important signal or decision a visible, inspectable region. Do not count hidden copy or broad page shells such as `main`, `#app`, or `#root` as product evidence.

Do not rely on a name, logo, accent color, mascot, generic slogan, fake metric card, three-feature grid, abstract illustration, or labels such as `AI`, `Smart`, `Premium`, `Fast`, or `Secure` without domain evidence.

## 4. Test The Decision

Make one product-specific decision visible and useful. State:

- Decision: what the user chooses or commits to.
- Inputs: the facts, states, or controls needed to decide.
- Consequence: what changes after the choice.
- Evidence: where the choice and consequence appear in the rendered UI.

Revise when the primary experience only asks users to scroll, read generic claims, or click an action with an unclear consequence.

Run a lightweight substitution check. Mentally replace only the name, logo, and accent color with two distant product categories. Revise when the same information architecture, data, controls, and primary action still fit either category with only superficial relabeling. Treat this as a design prompt, not an academic score or a Strict pass/fail formula.

## 5. Walk The Primary Action

Trace one causal chain:

`user need -> cue -> trigger -> precondition -> feedback -> result -> terminal state -> recovery`

Verify the applicable links:

- Cue: explain why the action matters in nearby context.
- Trigger: label the action so it predicts the next result.
- Precondition: expose required selection, input, permission, or availability.
- Feedback: acknowledge the action immediately.
- Result: change navigation, mutation, selection, comparison, generation, purchase, booking, or another meaningful outcome.
- Terminal state: make completion or the stable next step visible.
- Recovery: provide retry, edit, undo, cancel, back, or another safe path when the task can fail or be reversed.

Avoid context-free primary labels such as `Learn more`, `Explore`, `Continue`, or `Submit` when a concrete verb and object can describe the result.

For a changed primary flow, collect actual browser evidence of the start and terminal states at desktop and mobile. Observe feedback and recovery during the walkthrough; capture them when they are necessary to establish the claim. Do not fake a state with renamed screenshots or static copy.

Revise silent clicks, wrong destinations, hidden prerequisites, indefinite loading, success without confirmation, and actions that trap the user.

## 6. Keep Primary Controls Honest

Review visible controls involved in the primary viewport and primary task:

- Make functional controls perform the represented action.
- Make disabled controls semantic and explain a prerequisite when useful.
- Label prototype-only controls visibly; do not imitate a completed production action.
- Point navigation labels to real destinations or remove them.
- Make filters, tabs, selectors, and comparison controls visibly change state or content.

Check the controls needed for the primary flow, including its recovery. Do not require a full-page control inventory or a control manifest in Standard; reserve those checks for Strict. Treat an undisclosed dead-end control in the reviewed flow as a failure.

## 7. Verify The Render

Use a real browser at desktop and mobile viewport sizes. Check the primary walkthrough and record the observed start and terminal states when the flow changed. Check:

- Console errors and page errors.
- Horizontal overflow and clipped controls or text.
- Keyboard reachability and visible focus for the primary controls.
- Relevant loading, empty, error, disabled, success, and long-content states.
- The rendered visibility and legibility of the product signature, decision, price or consequence, and CTA where applicable.

Use a screenshot or browser artifact to support material claims. Describe what the artifact shows with product-specific nouns; do not write only `checked`, `looks good`, `works`, `pass`, or `as expected`.

Browser evidence is required before assigning `VERIFIED_STANDARD`. Without real desktop and mobile browser evidence, assign `IMPLEMENTED_UNVERIFIED` and list the unverified risks.

## 8. Review The First Render

Judge the rendered surface before declaring it done. Revise up to two times when any applicable area is weak:

- Composition: guide attention to the primary task without accidental imbalance.
- Product storytelling: make the product, domain object, or work surface communicate its value.
- Hierarchy: make title, product information, price or consequence, and CTA readable in their intended order.
- Brand coherence: align color, type, shape, imagery, and effects with project or user evidence.
- Interaction polish: make selection, feedback, terminal state, and recovery feel connected.

Keep the review grounded in the actual capture. Do not convert it into a numerical quality score, an originality claim, or a substitute for user testing.

## 9. Completion Boundary

Report the product contract, browser evidence collected, checks skipped, known limitations, and one status:

- `IMPLEMENTED_UNVERIFIED`: implementation exists, but actual browser evidence at both desktop and mobile is missing.
- `VERIFIED_STANDARD`: actual browser evidence confirms the applicable desktop/mobile primary flow, start and terminal states when changed, console and overflow checks, and primary keyboard/focus basics.

Do not report Strict checks, independent review, fresh-context validation, full control coverage, capture manifests, provenance, or command re-execution unless the Strict profile ran them under `aggressive-hard-gate.md`.

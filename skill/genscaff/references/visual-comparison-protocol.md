# Visual Comparison Protocol

Use this protocol before finalizing any browser-rendered frontend.

## Before Coding

1. Pick one primary brand reference from `brand-visual-research.md`.
2. Pick one secondary reference only if it solves a different problem.
3. Pick at least three AI slop risks from `ai-slop-research.md`.
4. Pick at least three UI craft checks from `ui-craft-guidelines.md`.
5. Define the target user, user need, primary task, success outcome, domain objects, differentiating decision, primary CTA, and recovery path.
6. For new or broad work, compare two materially different directions and choose by product and task fit.
7. Write the visual target with brand principles, craft rules, product-specific signals, action continuity, evidence targets, and slop rejection rules.

## After First Render

Capture desktop and mobile screenshots, then compare:

- Brand fit: Does the result use the selected brand's principle, not its costume?
- Token fit: Does the result reuse existing theme tokens, component styles, and project scale values?
- Color token fit: Are neutral, accent, interaction, and semantic status colors tokenized before component use?
- Background fit: Is the page background white or black by default, or was any variation explicitly requested or confirmed?
- Accent fit: Is color rare enough for the Von Restorff effect to work, with status colors reserved for real status meanings?
- Product visibility: Is the product, workflow, content, place, or object visible in the first viewport?
- Product recognition: Without the name, logo, and accent color, can a reviewer identify the product category, target user, and primary task?
- Product signals: Are at least three independent domain signals visible for a screen, flow, site, or design board?
- Decision support: Does the surface help the user make a category-specific decision with the needed inputs and a visible consequence?
- Need trace: Can each major screen or section be traced to the primary task, an explicit constraint, trust, or a necessary decision?
- Action information scent: Does the primary CTA label and context accurately predict the next state?
- Action continuity: Does the primary action produce feedback, a useful result, a terminal state, and relevant recovery?
- Control honesty: Are visible controls functional, semantically disabled, or visibly disclosed as prototype-only?
- Hierarchy: Is the first thing the user sees the right thing?
- Density: Does the page have the right information density for its category?
- Screen load: Does any viewport, section, card, list row, table cell, toolbar, or comparison panel contain more information than the next decision needs?
- Sentence load: Does each sentence carry one message instead of a chain of claims, benefits, caveats, and instructions?
- Copy length: Can any sentence, helper text, label, or CTA be shortened without losing meaning?
- Visual rhythm: Do spacing, alignment, and repeated components feel deliberate?
- Label restraint: Are badges, eyebrow labels, and section titles necessary instead of decorative?
- Depth restraint: Are borders and shadows used only where they clarify grouping, interactivity, or elevation?
- Border restraint: Are borders minimized, tokenized, and absent from surfaces that spacing or contrast can separate?
- Radius restraint: Is border-radius minimal, system-driven, and absent from surfaces that do not need roundness?
- Shadow restraint: Is box-shadow absent from default surfaces and reserved for real elevation or interaction?
- List restraint: Do repeated list items avoid heavy borders, shadows, and card-like treatment by default?
- Word breaking: Do headings, buttons, Korean copy, cards, and long tokens wrap naturally without overflow?
- Copy specificity: Could the copy belong only to this product?
- State coverage: Are loading, empty, error, disabled, hover, focus, active, and extreme-content states handled where relevant?
- Slop rejection: Are the selected slop risks visibly absent?
- Substitution rejection: Do two mutually distant product substitutions each break at least four of five required axes for non-cosmetic reasons?
- Hard visual policy: Are source scan, computed styles, SVG/canvas review, and raster review all free of gradients, glass, backdrop blur, glow, and orbs?

## Iteration Rule

Run at least two visual passes:

- Pass 1: fix broken or misleading tasks, dead-end controls, missing product specificity, weak decision support, product visibility, hierarchy, screen information density, and major slop.
- Pass 2: re-run the primary task and substitution test, then fix typography, sentence density, copy length, spacing rhythm, semantic color tokenization, background policy, accent minimization, mobile composition, word-break behavior, badge/title necessity, edge/depth restraint, interaction states, and trust details.

Record each pass with its screenshot, exact findings, changes, and after-state evidence. At least one finding and one correction must be documented across the passes. If either pass finds an issue, continue until no issue remains.

## Evidence Required

The final quality report must include:

- Different real local desktop and mobile screenshot artifacts.
- Selected brand reference(s).
- Comparison notes naming at least one brand principle and one slop risk.
- Comparison notes naming at least one UI craft rule checked.
- Confirmation that screen information density, sentence density, and copy length were checked.
- Confirmation that background policy, semantic color tokenization, accent minimization, and list item border/shadow restraint were checked.
- Confirmation that border minimization, border overuse, border-radius minimization, border-radius overuse, and box-shadow overuse were checked.
- Confirmation that unnecessary badges/titles, border/shadow restraint, and word-break behavior were checked.
- Confirmation that brand-reference comparison, UI-craft comparison, and AI-slop comparison happened.
- Requirement evidence for `primary-task`, `primary-cta`, explicit constraints, and differentiators.
- At least three product-specific domain signals and one differentiating decision with evidence for non-component work.
- Desktop and mobile primary-task walkthrough evidence from trigger to terminal state.
- Two mutually distant substitution comparisons with a complete five-axis record and at least four broken axes each.
- A primary action trace covering information scent, feedback, result, terminal state, and recovery.
- Confirmation that no undisclosed dead-end controls remain.
- Ordered iteration records with findings, changes, and evidence.
- Fresh blind subagent product-specificity, action-continuity, and anti-slop judgment with a separate raw review artifact. Substantial work cannot replace it with self-review.
- A real local Lighthouse JSON artifact. Treat its scores as technical evidence only.
- Schema-v3 source fingerprint, capture manifest, desktop/mobile runtime-style manifests, desktop/mobile control manifests, and command execution manifest.

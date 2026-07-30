---
name: frontend-quality-gate
description: Premium frontend web development and UI polishing workflow with strict product-specificity, action-continuity, visual-evidence, and anti-slop quality gates. Use when Codex builds, redesigns, polishes, reviews, or fixes a web UI, component, screen, mobile app mockup, single-page HTML design board, landing page, dashboard, SaaS app, marketing site, responsive layout, design system surface, or any browser-rendered product experience. Trigger on vague or aesthetic requests such as "make it pretty", "clean and modern", "like famous brands", "design improvement", "polish UI", "refine styling", "tidy the screen", "mobile UI design", "make a mockup", "implement this Figma", or any Figma-linked screen implementation where the user expects a distinctive, task-connected, consistent, hierarchical, restrained UI instead of generic AI output.
---

# Frontend Quality Gate

## Core Rule

Treat frontend work as a product-design and visual-craft task, not only a coding task. Do not code before defining the user need, product contract, primary task, action path, and concrete visual target. Do not finish before interacting with the result, visually inspecting it, iterating on defects, running quality measurements, and passing every no-slop check.

If any required check fails, report `FAIL` and keep working until it passes unless blocked by missing user input, unavailable dependencies, or an impossible project constraint.

Prioritize consistency over novelty, hierarchy over decoration, and restraint over spectacle. A clean UI is not an absence of style; it is a system of repeated decisions.

Treat accessibility, responsive rendering, build success, and Lighthouse as technical floors. They do not prove product usefulness, product identity, action clarity, originality, or freedom from AI slop. A formally valid report is not evidence unless its claims point to inspectable artifacts and observed behavior.

Reject a result when it could be relabeled for unrelated products without substantial changes, when the primary action has no credible path to a result, or when polished presentation substitutes for domain objects, user decisions, workflow states, or trustworthy content.

For short or broad UI requests, first expand the request into a concrete design brief. The brief must look like a real creative direction document: brand/style, layout, screens or sections, shared components, states, assets, and verification constraints. Do not jump from a vague request directly to code.

## Required Workflow

1. Inspect the existing product surface and every related implementation path before changing it.
2. Identify the project's theme tokens, spacing scale, typography scale, border tokens, radius values, shadow tokens, color semantics, background policy, list item patterns, shared components, real content model, routes, and interaction conventions before choosing new values.
3. Read `references/design-brief-expansion.md`, `references/ui-craft-guidelines.md`, `references/brand-visual-research.md`, and `references/design-signals.md` before choosing visual direction.
4. Read `references/ai-slop-research.md`, `references/no-slop-checklist.md`, and `references/product-specificity-and-action-gate.md` before implementation.
5. Preflight the verification path before coding. Identify the exact dev-server, desktop/mobile browser capture, interaction walkthrough, Lighthouse JSON, and repository check commands. Surface an unavailable dependency now; never discover at the end that required evidence cannot be produced.
6. Write a product contract: target user, evidence-based or explicitly assumed user need, primary task, success outcome, domain objects, differentiators, constraints, primary CTA, and expected recovery path. Label assumptions instead of presenting them as research.
7. Expand the request into a detailed design brief. Preserve explicit user constraints first. Trace every user constraint and the primary task to a planned visible or interactive implementation.
8. For new or vague 0-to-1 UI, describe at least two materially different composition or workflow directions. Select one using product fit, user-task fit, and content fit; do not choose by trend or decoration. Existing UI polishing may keep one direction when the product system already constrains it.
9. For existing UI polishing, diagnose product, action, content, and craft failures before editing. Include generic product language, dead-end controls, weak CTA information scent, missing task feedback, hardcoded values, unclear hierarchy, unnecessary labels, edge/depth overuse, color drift, density, copy, state, accessibility, wrapping, and responsive risks.
10. Initialize the quality report now, not at the end. Fill `context` as the contract is written, use `evidence_catalog` IDs to reuse legitimate evidence, and run the validator after each evidence phase so cross-field failures surface while they are cheap to fix.
11. Create and save a timestamped visual-target artifact before coding with `references/visual-target-template.md`. Include baseline context, a user-task path, product-specific signals, substitution-test expectations, and evidence plan. Fill the corresponding report fields immediately.
12. Select at least one brand principle, three craft risks, and three slop risks to compare against. Use `references/visual-comparison-protocol.md`.
13. Implement using the project's framework, routing, styling system, components, content model, and conventions. If no token system exists, define a minimal local token layer first.
14. Implement the primary task end to end: clear trigger, correct preconditions, immediate feedback, meaningful result or destination, terminal state, and recovery. Make prototype-only controls visibly disclosed; do not ship silent dead ends.
15. Implement relevant loading, empty, error, disabled, hover, focus, active, success, long-content/extreme, and responsive states. Record per-state evidence or a concrete not-applicable rationale; success and long-content always need evidence. Deterministic test fixtures may expose hard-to-reach states, but must not be presented as production data or product functionality.
16. Start or use the local dev server when required. Inspect and interact with the result at desktop and mobile widths using screenshots or browser automation.
17. Walk through the primary task on desktop and mobile. Record what was clicked, what feedback appeared, the terminal state, and recovery behavior. A screenshot of the initial page is insufficient.
18. Run the product substitution test and action-continuity review from `references/product-specificity-and-action-gate.md`. Resolve every generic or broken result.
19. Compare evidence against the brief, target, brand principle, craft rules, and slop risks. Run at least two documented visual passes and record resolved findings.
20. When a fresh subagent is available for substantial UI work, have it independently judge product specificity and primary-action continuity from the artifacts without revealing the intended verdict. Otherwise perform a fresh adversarial pass and identify it as self-review.
21. Run Lighthouse as a technical floor and the repository's relevant lint, typecheck, test, and build commands. Save the Lighthouse JSON artifact.
22. Finish the evidence-backed quality report defined in `references/quality-report-schema.md`, then run `scripts/quality_gate.py` again.
23. Finish only when the validator passes, every artifact is real, all open findings are empty, and verification commands have been reported.

## Design Brief Expansion

For any request that is not already as specific as a production design brief, write an expanded brief before implementation. Keep it concise enough to use, but concrete enough to build without guessing.

The expanded brief must include:

- Product name, domain, target user, user need, primary task, success outcome, and primary action.
- Assumption ledger: distinguish user-provided facts, repository evidence, external research, and agent assumptions.
- Product signature: domain objects, domain language, data or media, decision points, workflow states, and at least two differentiators that would break if the product were renamed for another category.
- Direction decision: for new or broad UI, compare at least two materially different structures and select one with a product-fit rationale.
- Brand and style: palette, typography, radius, tone, imagery, icon direction, background policy, semantic color token plan, and forbidden visual choices.
- Screen or section plan: named screens/sections with specific content and UI elements. Do not add decorative badges, eyebrow labels, or section titles unless they clarify navigation, hierarchy, or requested content.
- Information density plan: define what each screen or section must communicate, what should be deferred, and what should be removed.
- Shared components: navigation, tab bar, cards, chips, forms, buttons, status bars, filters, modals, or comparison widgets as relevant.
- Layout plan: canvas arrangement, responsive behavior, max widths, mobile/desktop composition, repeated component rhythm, and word-break behavior for headings, buttons, cards, and long values.
- Copy plan: keep each sentence focused on one idea, avoid packing multiple claims into one sentence, and remove words that do not change meaning.
- State plan: loading, empty, error, disabled, hover, focus, active, and long-content/extreme cases where relevant.
- Trust, safety, proof, or credibility sections when the product category needs user confidence.
- Verification plan: screenshots, interactions to test, Lighthouse targets, and quality-gate checks.
- Requirement trace: map explicit user constraints, primary task, and CTA to the planned screen, component, interaction, and evidence.
- Action contract: map CTA label and context to start state, feedback, result, terminal state, and recovery.

For mobile app mockup or "HTML one-page design sheet" requests, use a multi-screen board only when the request implies a product flow. Derive the screen count and order from the primary task; do not fill a 4-6-screen quota or add a generic trust/component section without a traceable reason.

## Visual Target Requirements

Before editing code, write a short target that includes:

- Product context, target user, user need, primary task, and observable success outcome.
- Source status for important decisions: user-provided, repository-derived, externally researched, or explicitly assumed.
- Domain objects, domain-specific content, decision points, and workflow states that make the interface non-transferable to unrelated products.
- Two alternative directions and a selection rationale for new or broad UI.
- Expanded design brief summary and source constraints.
- One primary CTA for the main viewport or workflow.
- Benchmark brands or product references, using live-site visual observations or `brand-visual-research.md` principles rather than copying assets.
- Existing project tokens, component patterns, and values to reuse.
- Layout composition for desktop and mobile.
- Typography scale, density, spacing, and hierarchy.
- Information density: limit each viewport, section, card, list row, and control group to the minimum information needed for the user's next decision.
- Copy density: keep one sentence to one message. Split, shorten, or remove copy that mixes audience, feature, benefit, proof, and instruction in one sentence.
- Copy length: avoid unnecessary clauses, filler adjectives, and explanatory text that repeats what the UI already shows.
- Color, contrast, imagery, iconography, and motion direction.
- Background policy: use white or black by default. Treat off-white, tinted, gradient, textured, image, or multi-color backgrounds as variations that require explicit user confirmation unless the user already requested them.
- Color token map: define neutral, text, surface, border, accent, interaction, and semantic status tokens before styling. Keep component code on tokens, not raw colors.
- Accent policy: use one primary accent and only necessary semantic colors for info, success, warning, and danger. Apply contrast through the Von Restorff effect: important states stand out because most of the interface stays neutral.
- List item treatment: use spacing, alignment, typography, and subtle dividers first; minimize border and shadow on list rows.
- Section title and badge policy: which labels are necessary, and which decorative labels must be omitted.
- Border policy: default to no border. Use the smallest number of subtle tokenized borders needed for separation, focus, selection, or state.
- Border-radius policy: use the minimum radius needed by the project system. Avoid roundness as decoration; reserve pill radius for chips, avatars, toggles, and true pill controls.
- Box-shadow policy: default to no shadow. Reserve shadow for overlays, popovers, modals, dragged items, or rare interactive lift.
- Border and shadow restraint: where depth or separation is truly needed, and where spacing or background contrast is enough.
- Word-break and wrapping plan for headings, Korean copy, button labels, cards, tables, URLs, IDs, and long tokens.
- Component states for the main workflow: loading, empty, error, disabled, hover, focus, active, and long-content/extreme values when relevant.
- Anti-slop risks from `ai-slop-research.md` and `no-slop-checklist.md` that must be avoided.
- Substitution-test prediction: name two unrelated product categories and list which visible signals must prevent a simple rename from fitting them.
- Primary action chain: trigger label, surrounding cue, start state, feedback, result, terminal state, and recovery path.
- Requirement-to-evidence map for the primary task, primary CTA, explicit constraints, and differentiating product signals.
- Exact visual comparison evidence to collect after implementation.

Keep the target concrete enough that the final screenshot can be judged against it.

## Implementation Standards

- Prefer established project components, tokens, utilities, and patterns.
- Make the interface specific through domain objects, meaningful data, realistic terminology, relevant user decisions, and workflow state. The product name alone is not a product signal.
- Keep the primary task visible and actionable. Every primary CTA must accurately predict its next state and produce feedback, a useful destination or result, and a recovery path.
- Keep navigation, tabs, filters, forms, and controls honest. Implement them, disable them, or explicitly disclose prototype behavior.
- Preserve traceability from user need to UI. A polished section that cannot be tied to the primary task, a user constraint, trust, or a necessary decision must be removed.
- Avoid raw visual constants in component code when a project token exists. Use semantic tokens for color and project scale values for spacing, type, radius, and shadows.
- Tokenize colors carefully. Prefer layered semantic roles such as `bg.default`, `bg.inverse`, `surface.default`, `surface.subtle`, `text.primary`, `text.secondary`, `border.subtle`, `accent.primary`, `accent.contrast`, `status.info`, `status.success`, `status.warning`, `status.danger`, `interactive.hover`, `interactive.focus`, and `interactive.disabled`.
- Use white or black as the default page background. If a design would use off-white, tinted gray, gradient, textured, image, or multi-color backgrounds and the user did not explicitly request that variation, ask for confirmation before using it.
- Keep color count low. Use neutral colors for most UI, one primary accent for emphasis/CTA/selection, and semantic colors only for real info, success, warning, danger, or alert meanings.
- Use the Von Restorff effect deliberately: the emphasized item should be rare and meaningful, not one accent among many competing colors.
- Do not overload a screen with information. Prefer progressive disclosure, tabs, details panels, accordions, drill-down pages, or secondary states when content exceeds what the user needs for the immediate decision.
- Do not overload a component with metadata. Cards, list rows, comparison cells, and panels should have one primary message, a small number of supporting facts, and a clear next action.
- Write concise UI copy. One sentence should carry one idea. Avoid sentence chains that combine feature, benefit, audience, proof, caveat, and instruction at once.
- Cut copy that repeats visible UI structure. Labels, headings, helper text, empty states, and CTA copy should be short, concrete, and necessary.
- Use 4px spacing multiples: `4 / 8 / 12 / 16 / 24 / 32 / 48 / 64`. Do not introduce arbitrary spacing such as `13px` or `22px`.
- Keep typography on a restrained scale: `12 / 14 / 16 / 18 / 20 / 24 / 32` unless the existing design system already defines a different scale. Do not use text below `12px`.
- Keep radius to 2-3 project levels and shadows to at most two levels.
- Minimize border use. Do not frame every section, card, list row, toolbar, or panel. Prefer spacing, alignment, surface contrast, dividers, and typography before adding borders.
- Do not overuse borders. Use borders for explicit state, selection, focus, input affordance, table/grid structure, or genuinely needed separation. Avoid borders that merely decorate or compensate for cramped spacing.
- Minimize border-radius. Use the smallest project-approved radius that preserves the system's shape language. Avoid making every surface rounded.
- Do not overuse border-radius. Reserve full-pill radius for chips, tags, avatars, toggles, segmented controls, and controls whose function benefits from a pill shape.
- Do not overuse box-shadow. Default surfaces should be flat. Use shadow only for overlays, modals, popovers, dragged items, floating controls, or a single subtle interactive lift pattern already present in the project.
- Unless the user requests a framed/card-heavy look or the project already uses it, avoid heavy borders and shadows. Prefer spacing, alignment, surface contrast, and typography for separation.
- For list items, minimize borders and shadows. Prefer row spacing, text hierarchy, icons, separators, hover states, and selected-state tokens over card-like treatment on every row.
- Keep one primary button per area. Use primary, secondary, and tertiary hierarchy only.
- Do not create decorative badges, eyebrow text, section labels, or redundant titles by default. Add them only when they improve orientation, scanning, status, category, or requested brand expression.
- Use real product structure and meaningful copy. Avoid placeholder marketing language.
- Build the actual usable surface first, not a decorative landing page unless the user explicitly asks for one.
- Make controls complete: states, focus, hover, loading, error, empty, disabled, and responsive behavior where relevant.
- Keep responsive layouts stable with explicit constraints for grids, media, toolbars, cards, and fixed-format UI.
- Verify word-break and wrapping at mobile and desktop widths. Keep Korean headings and button labels from breaking awkwardly; handle long URLs, IDs, model names, email addresses, and numbers without overflow.
- Use image or media assets when a website needs visual presence. Use relevant real assets, generated bitmap assets, or existing project assets.
- Do not use decorative gradient orbs, generic glass cards, random emoji, fake metrics, or one-note purple/blue SaaS styling unless the product context specifically requires it.
- Do not borrow a brand's proprietary assets, trademarks, exact composition, or copy. Extract principles only.
- Make the product or workflow visible in the first viewport. A premium-looking page still fails if it hides the actual product behind abstract decoration.
- Fail the rename test: replacing the product name and logo with two unrelated categories must expose obvious mismatches in objects, language, decisions, data, and workflow.

## Browser Feedback Loop

For any browser-rendered UI:

- Capture or inspect at least one desktop viewport and one mobile viewport.
- Check for console errors, broken assets, overflow, clipped text, awkward word breaks, unreadable contrast, overlapping UI, accidental horizontal scroll, unnecessary badges/titles, border overuse, excessive border-radius, box-shadow overuse, overcolored UI, non-tokenized color usage, list rows with excessive borders/shadows, overloaded screens, overloaded sentences, unnecessarily long copy, and awkward empty space.
- Compare screenshots against the visual target, selected brand reference principles, UI craft guidelines, and slop checklist.
- Run the primary task from its visible trigger to its terminal state at both widths. Check CTA information scent, state feedback, destination accuracy, error recovery, and dead ends.
- Record specific differences: hierarchy, density, spacing rhythm, token consistency, product visibility, product specificity, image quality, copy specificity, decision support, action continuity, and interaction states.
- Run the two-domain substitution test from the rendered evidence. Product name, logo, and accent color do not count as breaking signals.
- Resolve findings in severity order: broken task or misleading control, missing product specificity, hierarchy and content failures, then decorative polish.
- Iterate after inspection. A single blind implementation pass is not enough; two visual passes are the minimum for frontend work.

## Quality Gate Report

Read `references/quality-report-schema.md` and initialize the strict report instead of hand-writing a self-attestation checklist:

```bash
python <skill-dir>/scripts/quality_gate.py --init <report.json>
```

Fill the report with real local screenshots, a real Lighthouse JSON report, requirement evidence, domain signals, a two-domain substitution test, the primary action trace, iteration findings, and independent judgment. `true` booleans alone can never pass.

Populate the report continuously. Put reusable evidence objects in `evidence_catalog` once and reference their IDs from requirement, action, state, walkthrough, iteration, and review sections only when the same artifact, region, and observation genuinely support those claims. Run the validator after target creation, after the first walkthrough, after visual iteration, and after Lighthouse; do not postpone the entire report until final polish.

Use a bounded error list during progress checks:

```bash
python <skill-dir>/scripts/quality_gate.py --report <report.json> --max-errors 30
```

For the final verdict, run without an error cap:

```bash
python <skill-dir>/scripts/quality_gate.py --report <report.json>
```

The validator fails on missing or placeholder evidence, absent artifacts, screenshot reuse, Lighthouse score mismatch, weak product specificity, a renameable result, generic CTA labeling, broken action continuity, dead-end controls, insufficient iteration evidence, unresolved findings, weak human judgment, any required boolean failure, console errors, layout issues, or scores below threshold.

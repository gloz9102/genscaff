# UI Craft Guidelines

Use these rules when implementing new UI, improving an existing screen, polishing visual style, or translating a Figma design. Reuse the project's existing design system first. Do not bind these instructions to any specific framework.

Numeric style examples below are starting points when no project rule exists, not universal pass/fail quotas. Enforce task clarity, required information, role consistency, legibility, accessibility, and honest behavior. A common font or library is valid; an unusual aesthetic cannot compensate for a failed task.

## Work Sequence

1. Inspect existing theme tokens, CSS variables, utility classes, component library, shared layout primitives, and common UI states.
2. Identify the product's target user, primary task, domain objects, content model, routes, controls, workflow states, terminology, and success outcome.
3. Identify the existing spacing scale, typography scale, border tokens, radius levels, shadow levels, semantic colors, background policy, list item patterns, icon set, and button hierarchy.
4. Reuse existing tokens and components. If no token layer exists, create a minimal local token layer before styling components.
5. Implement the primary task and product-specific decision before decorative support sections.
6. Implement the UI with clear hierarchy, consistent spacing, restrained decoration, honest controls, and complete states.
7. Self-check product specificity, action continuity, and the anti-patterns before final browser verification.

## Core Priorities

1. Consistency over creativity: reuse project tokens, components, and patterns before adding new visual values.
2. Hierarchy is design: make task priority visible through appropriate emphasis on urgent work, decision facts, supporting text, and actions. A title's size alone does not establish hierarchy. Do not claim a measured comprehension time without user evidence.
3. Spacing is functional: use proximity to group related items and distance to separate unrelated items.
4. Decoration must have purpose: use shadows, animation, gradients, glass, blur, or glow only when they communicate state, depth, grouping, motion, or an evidenced brand or visual direction. Preserve user-requested, locked-reference, or project-established effects.
5. Labels must earn their space: badges, eyebrow text, and section titles need an information or evidenced expressive role. Consolidate redundant labels without losing orientation, status, category, or required brand expression.
6. Density must serve decision-making: do not put more information on a screen than the user needs for the next action.
7. Edges and depth must have a role: use borders, rounding, and shadows consistently for structure, state, elevation, or a product-grounded expressive direction.
8. Product meaning must survive without branding: domain objects, decisions, data, language, and workflow should identify the relevant subject and job even if name, logo, and accent color are removed. Preserve familiar interaction conventions; do not force every primitive to look unique.
9. Actions must be causal: labels predict results, feedback follows triggers, completion is visible, and recovery remains available.

## Tokens And Scales

- Use the project's token or theme path for visual values. Avoid raw hex and arbitrary pixels in component code when tokens exist.
- Use layered color tokens, not scattered component colors. At minimum, map backgrounds, surfaces, text, borders, accent, interaction states, and semantic status roles before applying colors.
- Choose the primary accent from existing product conventions or the task context by default. Keep its foreground and hover/pressed/selected variants in the shared theme layer so a user-requested replacement propagates across controls; recheck contrast after replacement. Do not build a theme editor unless requested.
- If no project token system exists, create a minimal local token layer with roles such as `bg.default`, `bg.inverse`, `surface.default`, `surface.subtle`, `text.primary`, `text.secondary`, `border.subtle`, `accent.primary`, `accent.contrast`, `status.info`, `status.success`, `status.warning`, `status.danger`, `interactive.hover`, `interactive.focus`, and `interactive.disabled`.
- Reuse the project's spacing scale. Without one, `4 / 8 / 12 / 16 / 24 / 32 / 48 / 64` is a useful starting scale; allow role-specific optical or content-driven adjustments rather than forcing every value to a multiple.
- Use tokenized borders for input affordance, focus, selection, table/grid structure, meaningful separation, or established expression. Prefer spacing and alignment when an outline adds no information.
- Define radius tokens by component role and the established visual system. Equivalent components should use consistent geometry; coherent pill controls and rounded surfaces are valid, and the number of radius values alone is not a failure.
- Use a small, role-based elevation system. Keep shadows absent where separation does not need them; allow product-grounded media depth without imposing a universal shadow-count limit.
- Borders and shadows are not default decoration. Unless requested or already established by the project, use them sparingly and rely on spacing, alignment, background contrast, and typography for separation.
- Colors must map to semantic roles such as text, background, surface, border, accent, success, warning, error, and info.

## Typography

- Use a small, role-based type system. One body family and an optional display family are sufficient starting points; language coverage or the established design system may require additional families.
- Assign weights to meaningful emphasis levels and reuse them consistently; family or weight counts alone do not establish quality.
- Reuse the project type scale. Without one, `12 / 14 / 16 / 18 / 20 / 24 / 32` is a starting point for body and interface text, not a display-heading ceiling. Define separate responsive display tokens when the message and composition need larger type.
- Select body size for the typeface, language, audience, and reading context; `14px` or `16px` are interface starting points, not a ceiling for long-form reading. Do not shrink required information to fit a screenshot.
- Keep secondary text legible at intended viewports and zoom; inspect small text rather than treating a numeric minimum as proof of readability.
- Start near `1.5-1.6` body line-height and `1.2-1.3` heading line-height when appropriate, then inspect actual glyphs, diacritics, Korean fallback, and multiline content for crowding or clipping.
- Choose readable line measure for the actual script and content; roughly 65-75 characters can guide Latin long-form prose but is not a universal Korean measure.
- UI copy should be short and single-purpose. One sentence should communicate one idea; do not combine feature, benefit, audience, proof, caveat, and instruction in one sentence.
- Separate changes of context or topic into rendered lines or paragraphs, even when both messages would fit on one line. Prefer semantic paragraphs or separate text blocks; use intentional line breaks when appropriate. Source-code newlines alone do not create HTML line breaks. Allow responsive wrapping within each thought.
- Remove redundant words. If a label, heading, icon, or layout already communicates the idea, do not repeat it in helper copy.
- Plan word breaking deliberately. Prefer natural phrase wrapping for Korean headings, labels, and buttons; prevent awkward mid-word breaks. For long untrusted tokens such as URLs, IDs, model names, email addresses, and long numbers, allow safe wrapping inside the container without horizontal overflow.
- Lower secondary text with color, not tiny size.
- Numeric table data, prices, and metrics should use tabular numerals when supported.
- Inspect actual loaded and fallback fonts with Korean, Latin, numerals, and relevant symbols. Check apparent weight, baseline, phrase wrapping, and line-height together; selecting a distinctive Latin display font does not complete Korean typography.

## Color

- Allocate color by attention hierarchy and semantic role, not a fixed 60-30-10 area ratio. Verify that key content and actions remain distinguishable in both neutral and expressive compositions.
- Select backgrounds from existing conventions or a product-grounded visual direction. Neutral, tinted, image, and gradient treatments are valid when they support the audience and message; do not require approval solely because a background is not white or black. Honor explicit user constraints and verify contrast across actual media states.
- Keep action accent roles consistent and replaceable through shared tokens. Brand/media palettes may be broader when justified; keep semantic status colors tied to real states and distinct from decorative color.
- Maintain a clear focal point through scale, position, color, and contrast. Diagnose competing emphasis from the rendered task, not from the number of hues alone.
- Choose neutral contrast for legibility and product context; pure black/white and softer neutrals are both valid when the actual text/background contrast works.
- Meet applicable WCAG AA contrast: normally 4.5:1 for text and 3:1 for qualifying large text; meaningful controls and non-text indicators have their own applicable 3:1 requirements and exceptions. Decorative icons do not inherit a blanket rule. Check actual media backgrounds and states.
- Keep semantic color meanings consistent with the product and locale; green success, amber warning, red error, and blue information are common defaults rather than universal required hues.
- Do not communicate state by color alone. Pair color with text, icon, or shape.

## Layout

- Keep one alignment baseline within a section. Do not mix centered and left-aligned content without a clear structural reason.
- Give each screen or section one main job. If a section needs many unrelated facts, split it, defer details, or move secondary information behind a user action.
- Do not fit every piece of information into one screen or viewport by default. Dashboards, back offices, other information-intensive pages, or explicit user requests can justify denser layouts; preserve required visible information and access to actions.
- Accept whitespace without treating it as a defect. Do not invent content or expand components just to occupy it, and do not compress comfortable spacing unless usability evidence or the user calls for a change.
- For major claims, choose a product view, usage scene, process, or result that helps explain them. Do not fill a media slot with unrelated decoration or fabricated proof. A text-only section is valid when media would add no understanding.
- Give every screen or section a traceable reason: a user question, domain object, necessary decision, action, result, trust need, or explicit constraint.
- Prefer topology derived from the primary task over default hero-feature-proof-CTA or repeated card-grid formulas.
- Select information structure from relationships: comparable attributes need alignment, sequences need order, operational work needs scannable status and actions, and independent items may suit cards. Preserve necessary grouping; replacing every card with plain text is not an improvement by itself.
- Choose content width by role: readable text measures, wider data regions, and full-width media may coexist. A centered `1200-1440px` container is an option, not a universal composition.
- Use mobile side padding around `16-20px`; desktop side padding around `24-32px`.
- Use grid or flex gap for repeated cards and lists. Avoid mixing gap with arbitrary child margins.
- Section spacing must be visibly larger than internal component spacing.
- Section headers should be present only when they help scanning or navigation. Do not add badge-title-description stacks to every section by habit.
- Lists should read as lists, not stacks of miniature cards. Use subtle dividers, spacing, selected-state tokens, and hover/focus feedback before adding borders or shadows to individual rows.
- Cards, list rows, table cells, and panels should expose the facts needed for their task with a clear reading order. Keep comparison and operational metadata available when required; reduce redundant decoration and copy instead of hiding decision-critical details.
- Keep nested containers only when they communicate distinct relationships or affordances. Flatten redundant outlines when spacing, alignment, or surface contrast already expresses the relationship.

## Components

- Reuse the established action hierarchy; primary, secondary, and tertiary are useful starting roles. Express destructive intent separately when applicable.
- Make the next useful action clear within each decision group. Repeated row actions or necessary parallel choices are valid; diagnose competing emphasis from the task rather than a button-count quota.
- Choose horizontal or stacked action groups from label length, available width, and usable target size. Do not force every mobile action into a vertical stack or shrink labels/targets to preserve a desktop row.
- Badges, pills, and labels should communicate supported status, category, count, selection, or an evidenced brand detail. Replace unsupported or redundant labels with useful information; a word such as "AI" is not proof of product capability.
- Inputs need visible labels. Placeholder text is not a label.
- Primary CTA copy must predict the next state or result. Avoid context-free labels such as `Learn more`, `Explore`, `Continue`, or `Submit` when a concrete verb and object are available.
- Interactive controls must work, be semantically disabled, or be visibly disclosed as prototype-only. Silent dead ends fail.
- Primary actions must expose immediate feedback, a useful result or destination, a terminal state, and relevant recovery.
- Define hover, focus, active, disabled, loading, empty, and error states where relevant.
- Clickable elements need pointer cursor, visible hover feedback on hover-capable devices, and immediate press/click feedback. Keep visible keyboard focus and equivalent touch/keyboard activation feedback. Reuse established component states; if the suitable reaction remains unclear, ask the user about the affected control while continuing independent work.
- Select hover treatment by role: color, underline, border, or internal-element motion can suffice. Do not apply scaling or shadows uniformly. Preserve surrounding layout and stable hit areas during feedback.
- Use actual hover/pointer capabilities, including hybrid input where relevant, rather than viewport width as a proxy for touch. Essential information and controls must remain reachable without hover.
- Menus need opening, submenu entry, applicable back/close actions, and appropriate focus return. Keep a hover-revealed menu reachable while the pointer crosses from its trigger into the panel; define dismissal independently of incidental gaps or decorative transitions.
- Reuse a coherent icon family and role-based sizes, with `16 / 20 / 24` as starting points. Inspect stroke weight, optical alignment, meaning, and accessible labels rather than requiring exact size counts.
- Keep touch targets comfortably operable, normally aiming for `44x44px` or larger on touch surfaces. Verify applicable target-size and spacing requirements and exceptions; a nominal CSS dimension or narrow viewport screenshot alone does not prove operability.
- List items should minimize border and shadow. Reserve stronger borders, elevation, or filled backgrounds for selected, active, dragged, focused, or expanded rows.
- Inputs may need borders for affordance, but dense product surfaces should not inherit input-like borders everywhere.

## Motion

- Distinguish control feedback from explanatory motion. Product demonstrations and scene transitions may explain a claim or continuity; ambient motion needs a product-specific purpose and must not obscure content.
- For microinteractions, `150-300ms` is a starting range, not a delay before acknowledging input. Match timing to travel and function.
- Use `ease-out` for entrance and `ease-in` for exit.
- Avoid long blocking control transitions. Longer content/media sequences require a reading-friendly static or reduced-motion path; never delay navigation, trap scrolling, or require an animation to finish before an action works.
- Animate only transform and opacity when possible.
- Respect `prefers-reduced-motion`; keep essential content and controls available in a static presentation.
- Hover must not be the only route to information or an action. Test pointer entry/exit separately from activation and ensure keyboard and tap equivalents for revealed menus or details.
- Animated labels must retain a stable accessible name. Hide decorative duplicate text from assistive technology without hiding the control or its meaningful label; reduced motion must retain an immediately readable label.

## State Design

Identify real states of the affected data and actions; informational surfaces do not acquire fictional loading, error, or recovery flows:

- Loading: choose feedback for the actual async boundary and latency; reserve space where content arrives. Skeletons, progress, retained content, or local indicators serve different boundaries; none is a universal treatment.
- Empty: distinguish initial absence, zero matches, unavailable data, and retrieval failure where applicable; explain the cause and offer only relevant next actions.
- Error: explain the issue in user language and provide recovery.
- Long content and extremes: test 0 items, 1 item, many items, long labels, long numbers, and narrow screens.
- Preserve recoverable input and filters through validation, retry, and navigation where promised. Verify real result/state transitions and the stated persistence boundary rather than relying on a success toast.

## Responsive And Accessibility Minimum

- Verify mobile-first behavior and prevent accidental horizontal scroll.
- Images need dimensions or stable aspect ratio plus meaningful `alt` when they communicate information.
- Use semantic elements such as `main`, `nav`, `button`, and ordered heading levels.
- Every interaction must be keyboard reachable with logical focus order.

## Immediate-Fix Anti-Patterns

- Unexplained one-off values that break established rhythm or roles; an optical correction is not a failure solely because its number is unusual.
- Raw hex colors in component files when semantic tokens exist.
- Untokenized color roles, repeated one-off hex values, or colors named by appearance instead of role.
- Backgrounds or effects that compete with the message, weaken contrast, or lack a user, project, or product-specific rationale.
- Competing color emphasis that obscures primary content or action states.
- Crowding information into one viewport, section, card, list row, table cell, or toolbar without a task need or explicit user request. Necessary dashboard/back-office density is not itself a defect.
- Sentences that pack multiple messages, claims, caveats, or instructions together.
- Long helper text that repeats labels, headings, or visible controls.
- Decorative badges, eyebrow labels, or redundant section titles created without a clear information role.
- Inconsistent radius values among components with the same role.
- Geometry repeated across unrelated roles without a product-system reason, obscuring grouping, emphasis, or affordance.
- Inconsistent elevation or media depth without a structural or expressive purpose.
- Shadows repeated without a layering, separation, state, or evidenced expressive role.
- Inconsistent type roles or fallback glyphs that disrupt reading and hierarchy.
- Required text too small, crowded, faint, or clipped for the actual reading context.
- Low-contrast gray on gray.
- Placeholder used as a label.
- Direct-action controls without appropriate hover feedback on hover-capable devices or equivalent activation feedback for their supported inputs.
- Borders used to compensate for cramped spacing.
- Borders repeated without meaningful separation or an established expressive role.
- Nested borders that obscure relationships or duplicate an already clear group.
- Borders or shadows applied to most sections/cards when spacing or background contrast would be enough.
- Per-item borders or shadows that impede scanning or hide meaningful selection/elevation.
- Competing action emphasis that hides the next useful step.
- Repeated elevation that obscures meaningful layers or selected states.
- Awkward Korean word breaks, clipped button text, or long tokens causing overflow.
- A blocking or indefinite spinner without appropriate status, retained context, or applicable recovery.
- Missing relevant empty, error, disabled, long-content, or extreme-value states.

## Self-Validation Checklist

Before finishing, confirm:

- Existing tokens and shared components were inspected and reused.
- Any new local token layer is minimal and consistently used.
- Spacing uses the established scale with justified role-specific adjustments.
- Typography roles, line-height, loaded/fallback fonts, and content measure were checked with actual localized text.
- Color usage follows semantic roles and contrast requirements.
- Background choice supports the product direction and preserves readability and action visibility.
- Any gradient, glass, blur, glow, or similar effect has a user, project, or product-grounded purpose and does not obstruct the task.
- Shared action accents remain recognizable within the brand palette; semantic status colors retain their meanings.
- Color tokens are layered and named by role before component usage.
- Information density fits the task, required comparison facts remain available, and secondary details are deferred only when useful.
- Sentences are concise and single-purpose.
- Copy has no unnecessary words or repeated explanations.
- Radius and elevation tokens are consistent within each component role.
- Borders express useful boundaries or established expression without compensating for broken spacing.
- Rounding supports component function and the selected visual direction.
- Geometry and elevation preserve meaningful differences between roles and states.
- Borders and shadows are restrained unless explicitly requested or already part of the project system.
- Badges and section titles have information or evidenced expressive roles rather than duplicating nearby content.
- Word-break and wrapping were checked for Korean copy, headings, buttons, cards, and long values.
- The next useful action and its prerequisite facts are clear within each decision group.
- Hover, focus, active, disabled states exist for interactive elements.
- Loading, empty, error, and extreme-value states were implemented or explicitly marked not applicable.
- Mobile and desktop layouts were visually checked.
- Target user, user need, primary task, observable success, and relevant recovery were defined before layout selection.
- Domain objects, domain terms, product-specific decisions, and workflow states visibly identify the product without relying on name, logo, or accent color.
- A lightweight substitution check found and corrected missing domain meaning without making familiar primitives unnecessarily novel.
- The primary CTA has clear information scent and matches its observed result.
- The primary task was walked through on desktop and mobile to a terminal state.
- No visible primary-task control is an undisclosed dead end.
- Technical scores are treated as floors, not as evidence of product specificity or action quality.

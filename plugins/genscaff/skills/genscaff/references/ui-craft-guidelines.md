# UI Craft Guidelines

Use these rules when implementing new UI, improving an existing screen, polishing visual style, or translating a Figma design. Reuse the project's existing design system first. Do not bind these instructions to any specific framework.

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
2. Hierarchy is design: make the title, supporting text, primary action, and secondary actions distinguishable in the rendered layout. Do not claim a measured comprehension time without user evidence.
3. Spacing is functional: use proximity to group related items and distance to separate unrelated items.
4. Decoration must have purpose: use shadows, animation, gradients, glass, blur, or glow only when they communicate state, depth, grouping, motion, or an evidenced brand or visual direction. Preserve user-requested, locked-reference, or project-established effects.
5. Labels must earn their space: badges, eyebrow text, and section titles are omitted unless they orient the user, communicate status/category, or were requested.
6. Density must serve decision-making: do not put more information on a screen than the user needs for the next action.
7. Edges and depth must have a role: use borders, rounding, and shadows consistently for structure, state, elevation, or a product-grounded expressive direction.
8. Product identity must survive without branding: domain objects, decisions, data, language, and workflow should identify the product even if name, logo, and accent color are removed.
9. Actions must be causal: labels predict results, feedback follows triggers, completion is visible, and recovery remains available.

## Tokens And Scales

- Use the project's token or theme path for visual values. Avoid raw hex and arbitrary pixels in component code when tokens exist.
- Use layered color tokens, not scattered component colors. At minimum, map backgrounds, surfaces, text, borders, accent, interaction states, and semantic status roles before applying colors.
- Choose the primary accent from existing product conventions or the task context by default. Keep its foreground and hover/pressed/selected variants in the shared theme layer so a user-requested replacement propagates across controls; recheck contrast after replacement. Do not build a theme editor unless requested.
- If no project token system exists, create a minimal local token layer with roles such as `bg.default`, `bg.inverse`, `surface.default`, `surface.subtle`, `text.primary`, `text.secondary`, `border.subtle`, `accent.primary`, `accent.contrast`, `status.info`, `status.success`, `status.warning`, `status.danger`, `interactive.hover`, `interactive.focus`, and `interactive.disabled`.
- Use 4px spacing multiples only: `4 / 8 / 12 / 16 / 24 / 32 / 48 / 64`.
- Borders default to none. Use the smallest number of subtle tokenized borders needed for input affordance, focus, selection, table/grid structure, or real separation.
- Define radius tokens by component role. Equivalent components should use consistent geometry; do not fail a screen solely because it has four or more radius values.
- Full pill radius is reserved for chips, tags, avatars, toggles, segmented controls, and true pill controls. Do not make every surface rounded.
- Use a small, role-based elevation system. Keep shadows absent where separation does not need them; allow product-grounded media depth without imposing a universal shadow-count limit.
- Borders and shadows are not default decoration. Unless requested or already established by the project, use them sparingly and rely on spacing, alignment, background contrast, and typography for separation.
- Colors must map to semantic roles such as text, background, surface, border, accent, success, warning, error, and info.

## Typography

- Use at most two font families.
- Use at most three weights: regular, semibold, bold.
- Reuse the project type scale. Without one, `12 / 14 / 16 / 18 / 20 / 24 / 32` is a starting point for body and interface text, not a display-heading ceiling. Define separate responsive display tokens when the message and composition need larger type.
- Body text should be `14px` or `16px`.
- Do not use text below `12px`.
- Body line-height should be `1.5-1.6`; heading line-height should be `1.2-1.3`.
- Long text should have `max-width` around 65-75 characters.
- UI copy should be short and single-purpose. One sentence should communicate one idea; do not combine feature, benefit, audience, proof, caveat, and instruction in one sentence.
- Separate changes of context or topic into rendered lines or paragraphs, even when both messages would fit on one line. Prefer semantic paragraphs or separate text blocks; use intentional line breaks when appropriate. Source-code newlines alone do not create HTML line breaks. Allow responsive wrapping within each thought.
- Remove redundant words. If a label, heading, icon, or layout already communicates the idea, do not repeat it in helper copy.
- Plan word breaking deliberately. Prefer natural phrase wrapping for Korean headings, labels, and buttons; prevent awkward mid-word breaks. For long untrusted tokens such as URLs, IDs, model names, email addresses, and long numbers, allow safe wrapping inside the container without horizontal overflow.
- Lower secondary text with color, not tiny size.
- Numeric table data, prices, and metrics should use tabular numerals when supported.

## Color

- Allocate color by attention hierarchy and semantic role, not a fixed 60-30-10 area ratio. Verify that key content and actions remain distinguishable in both neutral and expressive compositions.
- Select backgrounds from existing conventions or a product-grounded visual direction. Neutral, tinted, image, and gradient treatments are valid when they support the audience and message; do not require approval solely because a background is not white or black. Honor explicit user constraints and verify contrast across actual media states.
- Keep action accent roles consistent and replaceable through shared tokens. Brand/media palettes may be broader when justified; keep semantic status colors tied to real states and distinct from decorative color.
- Maintain a clear focal point through scale, position, color, and contrast. Diagnose competing emphasis from the rendered task, not from the number of hues alone.
- Avoid pure black on pure white when the project palette offers softer neutrals.
- Body contrast must meet WCAG AA; large text and icons must meet at least 3:1.
- Semantic colors must keep their meaning: success green, warning amber, error red, info blue.
- Do not communicate state by color alone. Pair color with text, icon, or shape.

## Layout

- Keep one alignment baseline within a section. Do not mix centered and left-aligned content without a clear structural reason.
- Give each screen or section one main job. If a section needs many unrelated facts, split it, defer details, or move secondary information behind a user action.
- Do not fit every piece of information into one screen or viewport by default. Dashboards, back offices, other information-intensive pages, or explicit user requests can justify denser layouts; preserve required visible information and access to actions.
- Accept whitespace without treating it as a defect. Do not invent content or expand components just to occupy it, and do not compress comfortable spacing unless usability evidence or the user calls for a change.
- For major claims, choose a product view, usage scene, process, or result that helps explain them. Do not fill a media slot with unrelated decoration or fabricated proof. A text-only section is valid when media would add no understanding.
- Give every screen or section a traceable reason: a user question, domain object, necessary decision, action, result, trust need, or explicit constraint.
- Prefer topology derived from the primary task over default hero-feature-proof-CTA or repeated card-grid formulas.
- Choose content width by role: readable text measures, wider data regions, and full-width media may coexist. A centered `1200-1440px` container is an option, not a universal composition.
- Use mobile side padding around `16-20px`; desktop side padding around `24-32px`.
- Use grid or flex gap for repeated cards and lists. Avoid mixing gap with arbitrary child margins.
- Section spacing must be visibly larger than internal component spacing.
- Section headers should be present only when they help scanning or navigation. Do not add badge-title-description stacks to every section by habit.
- Lists should read as lists, not stacks of miniature cards. Use subtle dividers, spacing, selected-state tokens, and hover/focus feedback before adding borders or shadows to individual rows.
- Cards, list rows, table cells, and panels should have one primary message and a limited set of supporting facts. Avoid metadata piles.
- Avoid bordered boxes inside bordered boxes. If a section already has clear spacing or surface contrast, do not add another outline.

## Components

- Buttons have only three hierarchy levels: primary, secondary, tertiary.
- Use one primary button per area.
- Choose horizontal or stacked action groups from label length, available width, and usable target size. Do not force every mobile action into a vertical stack or shrink labels/targets to preserve a desktop row.
- Badges, pills, and labels should communicate status, category, count, selection, or a user-requested brand detail. Decorative "NEW", "AI", "Premium", or generic eyebrow labels fail when they add no meaning.
- Inputs need visible labels. Placeholder text is not a label.
- Primary CTA copy must predict the next state or result. Avoid context-free labels such as `Learn more`, `Explore`, `Continue`, or `Submit` when a concrete verb and object are available.
- Interactive controls must work, be semantically disabled, or be visibly disclosed as prototype-only. Silent dead ends fail.
- Primary actions must expose immediate feedback, a useful result or destination, a terminal state, and relevant recovery.
- Define hover, focus, active, disabled, loading, empty, and error states where relevant.
- Clickable elements need pointer cursor, visible hover feedback on hover-capable devices, and immediate press/click feedback. Keep visible keyboard focus and equivalent touch/keyboard activation feedback. Reuse established component states; if the suitable reaction remains unclear, ask the user about the affected control while continuing independent work.
- Select hover treatment by role: color, underline, border, or internal-element motion can suffice. Do not apply scaling or shadows uniformly. Preserve surrounding layout and stable hit areas during feedback.
- Use actual hover/pointer capabilities, including hybrid input where relevant, rather than viewport width as a proxy for touch. Essential information and controls must remain reachable without hover.
- Menus need opening, submenu entry, applicable back/close actions, and appropriate focus return. Keep a hover-revealed menu reachable while the pointer crosses from its trigger into the panel; define dismissal independently of incidental gaps or decorative transitions.
- Use one icon set. Icon sizes should be `16 / 20 / 24`.
- Touch targets must be at least `40x40px`; prefer `44x44px` on mobile.
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

Every meaningful interface needs more than the happy path:

- Loading: use layout-shaped skeletons when possible; reserve space to avoid layout shift.
- Empty: provide a short explanation and next action.
- Error: explain the issue in user language and provide recovery.
- Long content and extremes: test 0 items, 1 item, many items, long labels, long numbers, and narrow screens.

## Responsive And Accessibility Minimum

- Verify mobile-first behavior and prevent accidental horizontal scroll.
- Images need dimensions or stable aspect ratio plus meaningful `alt` when they communicate information.
- Use semantic elements such as `main`, `nav`, `button`, and ordered heading levels.
- Every interaction must be keyboard reachable with logical focus order.

## Immediate-Fix Anti-Patterns

- Magic numbers such as `13px`, `22px`, or arbitrary one-off spacing.
- Raw hex colors in component files when semantic tokens exist.
- Untokenized color roles, repeated one-off hex values, or colors named by appearance instead of role.
- Backgrounds or effects that compete with the message, weaken contrast, or lack a user, project, or product-specific rationale.
- Competing color emphasis that obscures primary content or action states.
- Crowding information into one viewport, section, card, list row, table cell, or toolbar without a task need or explicit user request. Necessary dashboard/back-office density is not itself a defect.
- Sentences that pack multiple messages, claims, caveats, or instructions together.
- Long helper text that repeats labels, headings, or visible controls.
- Decorative badges, eyebrow labels, or redundant section titles created without a clear information role.
- Inconsistent radius values among components with the same role.
- Rounded corners applied to most surfaces without a project-system reason.
- Pill radius used for ordinary cards, panels, sections, or buttons that do not need pill shape.
- Inconsistent elevation or media depth without a structural or expressive purpose.
- Box-shadow applied to most cards, panels, list rows, or page sections.
- Five or more font weights.
- Text below `12px`.
- Low-contrast gray on gray.
- Placeholder used as a label.
- Clickable elements without hover feedback.
- Borders used to compensate for cramped spacing.
- Borders used as the default separator for every container.
- Multiple nested borders in the same visual group.
- Borders or shadows applied to most sections/cards when spacing or background contrast would be enough.
- Border or shadow applied to every list item by default.
- Too many primary buttons.
- Every card has a shadow.
- Awkward Korean word breaks, clipped button text, or long tokens causing overflow.
- Loading state is only a full-page spinner.
- Missing empty, error, disabled, long-content, or extreme-value states.

## Self-Validation Checklist

Before finishing, confirm:

- Existing tokens and shared components were inspected and reused.
- Any new local token layer is minimal and consistently used.
- Spacing uses the 4px scale.
- Typography uses the allowed scale, line-height, and weight limits.
- Color usage follows semantic roles and contrast requirements.
- Background choice supports the product direction and preserves readability and action visibility.
- Any gradient, glass, blur, glow, or similar effect has a user, project, or product-grounded purpose and does not obstruct the task.
- Shared action accents remain recognizable within the brand palette; semantic status colors retain their meanings.
- Color tokens are layered and named by role before component usage.
- Screen information density is restrained and secondary details are deferred when needed.
- Sentences are concise and single-purpose.
- Copy has no unnecessary words or repeated explanations.
- Radius and elevation tokens are consistent within each component role.
- Border usage is minimized.
- Borders are not overused as decoration or spacing repair.
- Rounding supports component function and the selected visual direction.
- Border-radius is not overused as decoration.
- Box-shadow is not overused.
- List item borders and shadows are minimized.
- Borders and shadows are restrained unless explicitly requested or already part of the project system.
- Badges and section titles are necessary rather than decorative.
- Word-break and wrapping were checked for Korean copy, headings, buttons, cards, and long values.
- The main area has one primary CTA.
- Hover, focus, active, disabled states exist for interactive elements.
- Loading, empty, error, and extreme-value states were implemented or explicitly marked not applicable.
- Mobile and desktop layouts were visually checked.
- Target user, user need, primary task, observable success, and recovery were defined before layout selection.
- Domain objects, domain terms, product-specific decisions, and workflow states visibly identify the product without relying on name, logo, or accent color.
- Two mutually distant product substitutions each break at least four of the five required structural axes.
- The primary CTA has clear information scent and matches its observed result.
- The primary task was walked through on desktop and mobile to a terminal state.
- No visible primary-task control is an undisclosed dead end.
- Technical scores are treated as floors, not as evidence of product specificity or action quality.

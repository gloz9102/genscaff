# Design Brief Expansion

Use this when the user gives a broad UI request such as "make a clean modern app", "create a mobile UI mockup", "like famous brands", "make a landing page", or "build a one-page HTML design sheet". Convert the request into a concrete build brief before coding.

Do not ask for more detail unless the output cannot be created without it. Preserve every explicit user constraint first. Fill missing design decisions with domain-appropriate choices that follow the skill's brand research, UI craft guidelines, and no-slop checklist.

## Expansion Principles

- Turn aesthetic words into verifiable constraints: background policy, palette, semantic color tokens, typography, radius, density, imagery, states, and layout.
- Turn a product idea into a product flow: screens, sections, navigation, core CTA, and shared components.
- Turn the request into a product contract: user need, primary task, observable success, domain objects, differentiating decisions, and recovery.
- Separate facts from assumptions. Label decisions as user-provided, repository-derived, externally researched, or assumed.
- For new or broad work, compare at least two materially different composition or workflow directions before choosing one. Select by user-task, content, and product fit.
- Turn "modern" into restraint: consistent spacing, strong hierarchy, limited accents, and visible product substance.
- Turn "cute", "premium", "technical", "warm", or similar tone words into concrete shape, color, copy, and asset choices.
- Make the result buildable in one pass: name all required screens/sections, components, copy, imagery, and layout rules.
- Keep the result digestible: specify what is shown now, what is deferred, and what is removed.
- Keep copy lean: each sentence should have one message and no unnecessary extension.
- Keep labels and surfaces intentional: do not invent badges, eyebrow labels, redundant section titles, heavy borders, or shadows unless they serve the request or clarify the interface.
- Keep edges quiet: specify where borders, border-radius, and box-shadow are necessary; otherwise default them to none or the smallest project token.
- Default backgrounds to white or black. Off-white, tint, texture, image, or multi-color backgrounds need explicit direction and evidence. Gradient backgrounds are prohibited by the Genscaff hard gate.
- Minimize colors. Define one primary accent and only necessary semantic status colors, then bind them to tokens before writing component styles.

## Required Expanded Brief Shape

Write the brief in this order:

1. Product and goal
   - Product name
   - User
   - User need
   - Primary task and observable success outcome
   - Core action and recovery path
   - Domain objects and domain vocabulary
   - At least two non-cosmetic differentiators
   - Fact and assumption sources
   - Output format

2. Direction decision
   - Direction A: structure, task model, product fit, and tradeoff
   - Direction B: materially different structure, task model, product fit, and tradeoff
   - Selected direction and why it serves the primary task better
   - For existing UI polishing, document the existing system constraint instead of inventing a second direction

3. Brand and style
   - Main color and allowed supporting colors
   - Background and surface colors
   - Background variation confirmation if not white or black
   - Semantic color token map
   - Accent and status color limits
   - Typography tone and weight
   - Radius system
   - Shadow/elevation style
   - Border minimization rule
   - Border-radius minimization rule
   - Box-shadow overuse rule
   - Border and shadow restraint
   - Image or asset direction
   - Forbidden visual choices

4. Screens or sections
   - For mobile app mockups: define only the named phone screens required to show the primary flow, decisions, terminal state, and recovery.
   - For websites: derive only the sections required by the user journey; hero, proof, feature, comparison, pricing, trust, and CTA are options rather than a default sequence.
   - For dashboards/tools: define navigation, primary work surface, filters, data cards, detail panel, and states.
   - Include section titles only when they improve scanning, navigation, or comprehension.
   - Define the main job of each screen or section and defer secondary details.
   - Map each screen or section to a user question, domain object, decision, action, result, and reason for existing.

5. Shared components
   - Status bar, nav, tab bar, cards, chips, buttons, forms, filters, badges, modals, empty/error/loading states, and repeated patterns.
   - Use badges only for status, category, count, selection, or user-requested brand details.
   - For lists, specify minimal row treatment: spacing, typography, separators, hover/focus/selected states before border or shadow.

6. Layout
   - Desktop and mobile composition.
   - Canvas arrangement for one-page design boards.
   - Grid/gap rhythm and max-width behavior.
   - How the next section or additional screens appear.
   - Word-break behavior for headings, labels, buttons, cards, and long values.
   - Information density limits for each viewport, section, card, list row, table, or comparison panel.

7. Copy
   - Primary message for each screen or section.
   - Sentence rules: one idea per sentence, no claim chains, no redundant explanation.
   - Short labels, headings, helper text, and CTA copy.

8. Interaction and states
   - Hover, focus, active, disabled.
   - Loading, empty, error, long-content/extreme values.
   - Any required selection, filtering, swipe, form, chat, or comparison behavior.
   - Primary action chain: cue, trigger, precondition, feedback, result, terminal state, and recovery.
   - Control honesty: functional, semantically disabled, or visibly disclosed as prototype-only.

9. Requirement trace
   - `primary-task` implementation and evidence target.
   - `primary-cta` implementation and evidence target.
   - Every explicit user constraint and product promise mapped to a screen, component, or behavior.

10. Verification
   - Required screenshot sizes.
   - Desktop and mobile primary-task walkthroughs.
   - Two unrelated domains for the substitution test and expected breaking signals.
   - Interactions, terminal state, recovery, and dead-end controls to test.
   - Lighthouse target.
   - Quality-gate report requirements.

## Mobile UI Board Pattern

When the request asks for a mobile UI design concept, app mockup, or HTML sheet:

- Create a single canvas that shows the task-required phone screens at once.
- Use a restrained device-frame treatment only when the board needs screen boundaries; do not transfer rounded corners or elevation to every surface inside the screens.
- Include iOS/Android-like status bars only when requested or clearly helpful.
- Include a bottom navigation or primary navigation component when the app flow needs it.
- Add a shared component or trust/safety section below the phone screens only when it traces to a real product need.
- Use real-feeling copy and plausible content, not placeholders.

## Product-Specific Detail Density

For a strong brief, each screen or section should name concrete UI elements:

- Header elements: logo, title, actions, filters, notification, back/more buttons.
- Body elements: hero copy, cards, photos, badges, chips, lists, messages, forms, comparison rows.
- CTA and state: active tab, selected toggle, disabled state, empty/error behavior.
- Action continuity: trigger, feedback, result, completion, and recovery.
- Decision support: inputs the user needs, the decision made, and the consequence.
- Visual emphasis: restrained solid accent text, necessary badge, underline, or outline/filled action. Never use a gradient CTA.
- Information rule: each screen, section, card, row, and sentence needs one clear job.
- Restraint rule: every badge, title, border, and shadow must have a named purpose.
- Shape rule: every rounded corner must come from the project radius system and be necessary for the component role.
- Color rule: every non-neutral color must map to a token and a purpose, such as accent, info, success, warning, or danger.

## Example Pattern To Emulate

For a request like "Create a mobile UI mockup for a pet matching app", expand it into:

- A named brand and warm visual system.
- A fixed palette with allowed and forbidden colors.
- The minimum screens needed to cover discovery, matching, profile decision, creation, communication, and trust for that specific flow.
- Shared bottom tab bar and action buttons.
- Specific image direction such as puppy photos, profile cards, chips, badges, and message bubbles.
- A one-page canvas arrangement showing screens in rows plus a component/trust section.

Do not copy this pet-app content unless the user asks for that domain. Use the pattern: concrete brand style, named screens, specific UI contents, shared components, and layout rules.

## Anti-Slop Rules For Expansion

- Do not output a generic hero plus three cards when the request implies an app flow.
- Do not infer product quality from a brand costume, Lighthouse score, accessibility score, or responsive screenshot.
- Do not treat product name, logo, color, or a generic slogan as product specificity.
- Do not choose the first plausible layout for broad new work without comparing a materially different direction.
- Do not add a screen or section that cannot be traced to the user need, primary task, trust, or a necessary decision.
- Do not use context-free CTA labels when a concrete action label is possible.
- Do not leave the primary action without immediate feedback, a result, a terminal state, and relevant recovery.
- Do not leave any visible control as an undisclosed dead end.
- Do not pass a design unless each of two mutually distant products breaks at least four of five axes: information architecture, data schema, state transitions, action sequence, and failure/recovery.
- Do not overload the first viewport or any screen with all available information.
- Do not make cards, list rows, table cells, or comparison panels carry too many facts.
- Do not hide the product behind abstract decoration.
- Do not invent fake metrics, awards, customer logos, or testimonials.
- Do not use broad copy like "unlock the future" or "seamless AI-powered experience".
- Do not write sentences that pack multiple claims, audiences, benefits, caveats, and instructions together.
- Do not lengthen copy with filler words, repeated explanations, or obvious UI descriptions.
- Do not create a style direction without constraints on colors, typography, radius, components, and states.
- Do not choose a non-white/non-black background without explicit user request or confirmation.
- Do not introduce many accent colors; preserve contrast by keeping most UI neutral.
- Do not skip semantic color token planning.
- Do not add decorative badges, eyebrow labels, or redundant titles to make sections look designed.
- Do not specify borders as the default way to separate all surfaces.
- Do not overuse border-radius or turn every surface into a rounded card.
- Do not specify heavy borders or shadows unless requested or required by the product system.
- Do not specify box-shadow on most cards, panels, rows, or sections.
- Do not make list rows look like independent cards unless the user requested a card list or the existing system already does this.
- Do not leave word-break undefined for Korean copy, compact controls, comparison tables, or long technical values.

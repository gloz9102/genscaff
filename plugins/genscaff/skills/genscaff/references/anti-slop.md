# Product-Grounded Anti-Slop Review

Use this reference only when routed by the main Skill. Judge the first rendered result against the user brief, repository evidence, and product domain. This is a correction guide, not a CSS detector, originality score, or reason to erase an established visual language.

## Decision rule

Evidence has priority in this order: explicit user direction, existing project and design-system conventions, product/domain requirements, then these heuristics.

Do not fail a surface because it contains one gradient, card, radius, centered section, animation, badge, or other component pattern. Treat a result as a generic-default finding only when unsupported defaults cluster across at least two design domains, such as composition plus decoration, content plus component geometry, or imagery plus motion. Name the cluster and the product evidence it displaces or obscures.

Preserve purposeful gradients, glass, cards, rounding, motion, and other treatments when the user requested them or the existing project uses them coherently. Cards that group actionable dashboard information are not marketing slop merely because they are cards. If evidence supports a questioned choice, record an exception instead of forcing a replacement.

## Positive direction

Before reviewing the render, state:

- Target user: the concrete audience completing the primary task.
- Primary success: the observable outcome the surface must help produce.
- Surface mode: landing, workflow, dashboard, editorial, transaction, or the classified equivalent.
- Dominant visual idea: the one idea organizing attention and hierarchy.
- Product-specific visual signature: the domain object, decision, proof, or workflow that makes the surface recognizable without its logo or accent color.
- Deliberate non-default composition choice: one layout decision derived from the task or content rather than a habitual template.

A positive direction must improve task clarity and product identity. “Be unique,” “look premium,” or novelty for its own sake is not a direction.

## Representative default clusters

Look for combinations, not isolated tokens:

- Generic composition: centered hero, decorative eyebrow or kicker, meaningless small section numbers, and a predictable feature/proof/CTA sequence unrelated to the product task.
- Generic decoration: gradient text, unsupported glow, purple/teal ornament, glass, or ambient shapes carrying more emphasis than product information.
- Unsupported proof and copy: invented metrics, testimonials, logo clouds, vague transformation claims, or abstract copy without inspectable product evidence.
- Mechanical repetition: the same icon tile, feature card, heading stack, radius, and spacing recipe repeated without distinct information roles.
- Container layering: nested cards and rounded surfaces used where spacing, alignment, dividers, or typography would express the information structure more clearly.
- Unrelated motion: marquee, pulse, scroll reveal, or ambient animation that does not explain state, continuity, hierarchy, or feedback.
- Irrelevant imagery: stock or abstract imagery that could move to a distant product category without changing meaning.

## First-render questions

Ask against the actual desktop and mobile captures:

1. If the product name and logo changed, would this still be substantially the same screen?
2. If domain objects and core content disappeared, would the composition still hold together unchanged?
3. Does decoration receive attention before the primary task, decision, or evidence?
4. Does the same card, icon, and heading recipe repeat without a product or scanning reason?
5. Do metrics, testimonials, statuses, and trust signals have user, repository, or clearly disclosed concept evidence?
6. Could spacing, alignment, dividers, and typography express the hierarchy more clearly than nested cards?

If the answers reveal unsupported defaults in at least two design domains, record one cluster finding rather than many style-lint findings. Preserve the product-specific workflow, evidence, states, accessibility, and responsive behavior while correcting it.

## Response

For each finding record its location, rendered evidence, project or brief rationale, and one response:

- `keep`: the pattern supports the task and needs no change.
- `replace`: use a product-grounded composition, content, hierarchy, or visual treatment.
- `remove`: delete decoration or unsupported content with no information loss.
- `exception`: preserve it and cite explicit user or project evidence.

Batch applicable corrections after the first render. Recheck desktop and mobile once, then stop: two rendered review passes total. Do not create an anti-slop-only render loop. If a finding remains, record it as an issue or limitation; never convert an unresolved visual finding into a clean boolean claim.

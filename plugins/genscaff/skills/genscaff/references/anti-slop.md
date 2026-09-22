# Product-Grounded Anti-Slop Review

Use this reference only when routed by the main Skill. Judge the first rendered result against the user brief, repository evidence, and product domain. This is a correction guide, not a CSS detector, originality score, or reason to erase an established visual language.

## Decision rule

Evidence has priority in this order: explicit user direction, existing project and design-system conventions, product/domain requirements, then these heuristics.

Do not fail a surface because it contains one gradient, card, radius, centered section, animation, badge, or other component pattern. Treat a result as a generic-default finding only when unsupported defaults cluster across at least two design domains, such as composition plus decoration, content plus component geometry, or imagery plus motion. Name the cluster and the product evidence it displaces or obscures.

Preserve purposeful gradients, glass, cards, rounding, motion, and other treatments when the user requested them, the existing project uses them coherently, or the product-grounded direction explains their role. Cards that group actionable dashboard information are not marketing slop merely because they are cards. If evidence supports a questioned choice, record an exception instead of forcing a replacement.

## Positive direction

Use the existing product/design contract for target user, primary success, surface mode, dominant visual idea, product-specific signature, and deliberate composition choice. Refer to those decisions while reviewing; do not create a second direction record.

A positive direction must improve task clarity and product identity. “Be unique,” “look premium,” or novelty for its own sake is not a direction.

## Representative default clusters

Look for combinations, not isolated tokens:

- Generic composition: centered hero, decorative eyebrow, meaningless section numbers, and a predictable feature/proof/CTA sequence unrelated to the task.
- Generic decoration: gradient text, unsupported glow, purple/teal ornament, glass, or ambient shapes emphasized above product information.
- Unsupported proof: invented metrics, testimonials, logo clouds, vague claims, or abstract copy without inspectable evidence.
- Mechanical repetition: the same icon tile, card, heading stack, radius, and spacing recipe without distinct information roles.
- Container layering: nested cards where spacing, alignment, dividers, or typography would express the hierarchy more clearly.
- Unrelated motion: marquee, pulse, scroll reveal, or ambient animation that does not explain the product, a usage scene, state, continuity, hierarchy, or feedback.
- Irrelevant imagery: stock or abstract imagery that could move to a distant product category without changing meaning.

Once confirmed, prefer information-bearing structure: fold a roleless eyebrow into heading/evidence; replace non-semantic numbers with surface-specific roles (steps, decisions, evidence, states); flatten nested cards using alignment, dividers, state text. Preserve domain objects, flow, accessibility, and responsiveness; deletion alone is not improvement.

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

Batch applicable aesthetic corrections after the selected implementation's first render. Recheck desktop and mobile once, then stop aesthetic iteration: two aesthetic review passes for that implementation. A bounded representative-candidate comparison is separate; it must not become an anti-slop-only render loop. This limit does not apply to required re-verification after fixing content, functionality, accessibility, or runtime defects. If a finding remains, record it as an issue or limitation; never convert an unresolved visual finding into a clean boolean claim.

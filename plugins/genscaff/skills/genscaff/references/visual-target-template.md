# Product and Design Contract

Complete this compact contract before broad or new UI. Keep entries testable and omit optional fields only when irrelevant.

```markdown
## Product
- Target user / primary job / success outcome:
- Domain objects and vocabulary:
- Primary CTA / secondary actions:
- Required decisions / actions to success / safe defaults:
- Failure or recovery when applicable:

## Reference
- Mode / primary archetype / optional secondary / surfaces:
- Adopted principles and product-fit rationale:
- Deliberate differences (minimum three for inspiration):
- Locked requirements and allowed changes:
- Reference trace: source / observed feature / principle / product fit / implementation location / rendered evidence / exclusions:

## Content
- Hierarchy / expected item count:
- Long-content and missing-data behavior:
- Localization and writing-direction needs:

## Preservation
- Required information / values / states / accessible names and their source:
- User actions / terminal outcomes / data and API contracts to preserve:
- Meaningful reading and focus order:
- Permitted presentation or content changes / justified DOM changes:
- Affected invariant -> before or brief baseline -> implementing region -> observed result and evidence / unresolved limitations:

## Exploration (only when applicable)
- Two-candidate comparison (default) / user-selected single direction / inapplicable reason:
- Representative screen / shared content, data, state, assets, desktop and mobile viewports:
- Candidate A / B: information hierarchy and composition rationale within existing craft rules:
- Differences beyond color / comparable evidence / requirement failures:
- User selection or explicit delegation / selected direction and rationale / pending decision:

## Visual system
- Surface mode / dominant idea / focal point / information density:
- Product-specific visual signature:
- Deliberate non-default composition choice and product rationale:
- Typography / spacing / color roles:
- Radius / elevation strategy:
- Image or media strategy:
- Motion intent / reduced-motion behavior:

## Engineering
- Framework / router / rendering model / styling system:
- Token source / reusable components:
- State ownership / data boundary:
- Browser support / performance risks / verification plan:
```

Recovery is required only when an action can fail, be cancelled, be reversed, leave the user incomplete, or cross a meaningful network/transaction boundary. Do not add fake recovery to informational pages.

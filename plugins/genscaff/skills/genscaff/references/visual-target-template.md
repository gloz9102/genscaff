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

## Content
- Hierarchy / expected item count:
- Long-content and missing-data behavior:
- Localization and writing-direction needs:

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

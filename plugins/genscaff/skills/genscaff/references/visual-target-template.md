# Product and Design Contract

Complete this compact contract once before broad or new UI. Keep entries testable and omit optional fields only when irrelevant. Update the same entries with implementation and evidence; reviews and completion reports refer to them instead of copying the contract. For a new project, derive invariants from the brief rather than inventing a baseline.

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

## Inspect before completing the contract

Before editing an existing project, inspect lockfiles, manifests and scripts, framework, router, rendering and build model, language and type checking, styling system, tokens, layouts and primitives, responsive conventions, breakpoints and container queries, state and data boundaries, localization and writing direction, media handling, lint/type-check/tests/browser tests/build, and CI. Keep confirmed facts separate from heuristic detections and assumptions.

When a reusable JSON inventory is useful, run `scripts/inspect_project.py <project-root>`. It reads metadata only, executes no project command, and separates facts from heuristic detections.

Do not replace the package manager, routing, or state management for visual convenience. Do not add a second styling system or UI library before proving the existing system cannot satisfy the task. Reuse components instead of renaming duplicates. Do not rewrite unrelated files, make absolute positioning the primary layout mechanism, or bury example data inside complex presentation logic.

For a new project, honor an explicit stack or choose the least complex stack that satisfies the request. Prefer semantic HTML and accessible primitives, separate example data from presentation, expose working dev/check/build paths, state mock boundaries honestly, and do not stop at a static mockup when working implementation was requested.

HTML or DOM identity alone does not prove preservation. Preserve required rendered information, accessible names, meaningful order, and action outcomes; justified semantic or responsive DOM changes are allowed. Never remove required information merely to improve composition.

Establish one dominant visual idea and hierarchy before decoration. Match density to the task, use deliberate component patterns and semantic tokens, make media serve understanding or discovery, and make motion explain hierarchy, continuity, or feedback. Keep the product recognizable without brand color. Avoid fixed-height variable-text containers; tolerate long, localized, and bidirectional content. Implement loading, partial, empty, error, disabled, unavailable, success, long-content, and media-failure states only where relevant.

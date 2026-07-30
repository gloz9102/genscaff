# Visual Target Template

Create this before coding. Keep it concise, but make every line judgeable against screenshots.

```markdown
## Visual Target

Artifact:
- Saved local path:
- Created at with timezone:
- Baseline repository or source context:

Product:
- What is being built:
- Primary user:
- User need:
- Primary task:
- Observable success outcome:
- Primary action:
- Single primary CTA:
- Recovery path:
- Domain objects and vocabulary:
- Non-cosmetic differentiators:
- User-provided facts:
- Repository evidence:
- External research:
- Explicit assumptions:

Direction Decision:
- Direction A and product/task fit:
- Direction B and product/task fit:
- Selected direction:
- Selection rationale:
- Existing-system constraint when alternatives are not applicable:

Expanded Brief:
- Brief created before coding:
- Preserved user constraints:
- Added domain-specific screens or sections:
- Shared components:
- Layout board or page structure:
- Requirement trace for primary task, CTA, and explicit constraints:

Benchmark Direction:
- Reference site(s) inspected or research fallback used:
- Reference signals:
- Same-domain or same-interaction-model relevance:
- Why these references fit:
- What not to copy:

Composition:
- Desktop:
- Mobile:
- First viewport must show:
- Main visual anchor:
- Information density limit:
- Deferred or removed details:
- Product-specific decision shown:
- Inputs needed for that decision:
- Consequence of the decision:

System:
- Existing tokens/components to reuse:
- Local token fallback if no theme exists:
- Typography:
- Spacing and density:
- Color and contrast:
- Background policy:
- Background variation confirmation:
- Color token map:
- Accent/status color limits:
- Von Restorff emphasis target:
- Radius and shadow levels:
- Border minimization:
- Border-radius minimization:
- Box-shadow usage:
- Border and shadow restraint:
- List item border/shadow treatment:
- Necessary badges/titles only:
- Word-break and wrapping:
- Components:
- Imagery or media:
- Motion:
- Visual-effect policy: identify unexplained gradients, glass, blur, glow, orbs, and raster-baked equivalents; record any user/project/locked-reference exceptions:

Copy:
- Primary message:
- Domain terms that must appear:
- Generic terms or claims to remove:
- Sentence density rule:
- Copy length rule:
- Redundant copy to avoid:

States:
- Loading:
- Empty:
- Error:
- Disabled:
- Hover/focus/active:
- Long content and extreme values:

Action Continuity:
- CTA cue and information scent:
- Start state and preconditions:
- Immediate feedback:
- Result or destination:
- Terminal state:
- Recovery:
- Functional, disabled, and prototype-only controls:

Product Specificity:
- Domain signal 1:
- Domain signal 2:
- Domain signal 3:
- Unrelated substitution domain 1 and breaking signals:
- Domain 1 five-axis prediction: information architecture, data schema, state transitions, action sequence, failure/recovery:
- Unrelated substitution domain 2 and breaking signals:
- Domain 2 five-axis prediction: information architecture, data schema, state transitions, action sequence, failure/recovery:
- Why name, logo, and color are not the only specific signals:

Anti-Slop Risks:
- Visual slop risk:
- Content slop risk:
- Interaction slop risk:
- Verification slop risk:
- UI craft risk:

Verification Preflight:
- Dev-server or direct-open command:
- Desktop/mobile browser and capture method:
- Interaction walkthrough method:
- Lighthouse JSON command:
- Repository lint/typecheck/test/build commands:
- Required dependencies confirmed:
- Quality report path:
- Evidence catalog ID convention:
- Frontend project root:
- Frontend source roots and fingerprint command:
- Rendered roots, including served/exported `dist`, `build`, `out`, bundles, and public assets:
- Validator-owned live audit config and default URL:
- Capture manifest path:
- Desktop/mobile runtime-style manifest paths:
- Desktop/mobile control manifest paths:
- Command execution manifest path:
- Content provenance manifest path:

Visual Comparison Plan:
- Brand reference principle to compare:
- UI craft guideline to compare:
- AI slop counterexample to reject:
- Desktop screenshot evidence:
- Mobile screenshot evidence:
- Expected iteration count:
- Primary-task desktop walkthrough evidence:
- Primary-task mobile walkthrough evidence:
- Desktop/mobile start, feedback, terminal, and recovery checkpoint evidence:
- Lighthouse JSON artifact:
- Independent reviewer and blinded questions:
- Independent raw review artifact path:
- Root-agent collaboration mailbox provenance check:

Acceptance:
- Screenshot should prove:
- Task walkthrough should prove:
- Substitution test should prove:
- Requirement trace should prove:
- Lighthouse target:
- Commands to run:
```

The target is not a long design essay. It is a compact contract between intention, implementation, and visual QA.

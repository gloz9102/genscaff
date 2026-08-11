## Visual Target

Artifact:
- Saved local path: `examples/pet-walker-marketplace-discovery/index.html`
- Created at with timezone: `2026-08-04T22:05:56+09:00`
- Baseline repository or source context: new standalone example beside the existing product-editorial sample; no reusable app framework or token system exists in the example area.

Product:
- What is being built: `곁길`, a fictional marketplace for finding a nearby dog-walking partner.
- Primary user: a dog owner who needs a suitable walker at a specific time.
- User need: "오늘 저녁에 우리 강아지 체급과 산책 방식에 맞는 사람을 빠르게 비교하고 요청하고 싶다."
- Primary task: search a neighborhood, set dog size and time, compare matching walkers, select one, and send a walk request.
- Observable success outcome: a confirmation names the selected walker, dog size, time, price, and offers cancellation.
- Primary action: choose a walker from filtered results.
- Single primary CTA: `민지에게 산책 요청 · 18,000원` (safe-default result).
- Recovery path: cancel the request and return to the same filters and result list.
- Domain objects and vocabulary: dog size, walk time, distance, available slot, walk style, leash handling, price per walk, walker profile.
- Non-cosmetic differentiators: dog-size compatibility changes inventory; time-slot availability changes matching results and CTA context.
- User-provided facts: marketplace-discovery archetype and screenshot request.
- Repository evidence: current repository skill contains `craft-marketplace-discovery.md`; cached 2.0.1 Standard profile lacks the newer archetype module.
- External research: bundled Airbnb research principle only—search first and consistent comparison metadata; no live-site data or assets used.
- Explicit assumptions: fictional Korean consumer brand, dog-walking domain, mock profiles and prices; every mock claim is disclosed as demo data.

Direction Decision:
- Direction A and product/task fit: availability-led list; filters stay visible and every row keeps distance, slot, style, and price in the same order.
- Direction B and product/task fit: map-first discovery; stronger spatial context but heavier media work and weaker one-screen comparison.
- Selected direction: Direction A.
- Selection rationale: the user must compare suitability and availability before geography beyond neighborhood-level distance matters.

Expanded Brief:
- Brief created before coding: yes, in this artifact.
- Preserved user constraints: marketplace-discovery example; a screenshot delivered from a real browser.
- Added domain-specific sections: neighborhood search, reversible filter summary, matching walker list, request confirmation, visibly disclosed error fixture.
- Shared components: segmented size controls, time chips, comparison rows, selected state, terminal confirmation.
- Layout board or page structure: compact sticky header, task-focused filter rail, result ledger, persistent mobile request bar only after selection.
- Requirement trace: filter controls update inventory; selecting a row updates price/CTA; CTA creates terminal state; cancellation restores the list.

Benchmark Direction:
- Reference site(s) inspected or research fallback used: bundled Airbnb marketplace research from `brand-visual-research.md`.
- Reference signals: search/filter first, repeated object rhythm, predictable metadata order.
- Same-domain or same-interaction-model relevance: browse-heavy marketplace inventory and comparison.
- What not to copy: Airbnb branding, search geometry, card proportions, icons, listing data, or booking sequence.

Composition:
- Desktop: two-column work surface—320px filter rail and a wide comparison list; terminal panel replaces neither context nor recovery.
- Mobile: single column; compact header, horizontally scrollable reversible chips, list rows with CTA context kept together.
- First viewport must show: dog-walking purpose, chosen size/time, result count, at least one walker, price, and the request path.
- Main visual anchor: matching walker ledger with dog-size compatibility and time availability.
- Information density limit: four comparison facts plus one price per row; deeper biography deferred.
- Deferred or removed details: map, chat, reviews, account nav, and payment are omitted because they do not advance this sample flow.
- Product-specific decision shown: which walker fits the dog size and requested slot.
- Inputs needed for that decision: dog size, time, distance, availability, walk style, price.
- Consequence of the decision: result inventory and final request summary change.

System:
- Existing tokens/components to reuse: none in standalone examples.
- Local token fallback if no theme exists: CSS custom properties for background, surface, text, muted text, border, accent, focus, success, and error.
- Typography: system Korean sans; 12/14/16/18/24/32px, three weights.
- Spacing and density: 4/8/12/16/24/32/48/64px only.
- Color and contrast: white background, near-black text, one deep-green accent, semantic red only for errors.
- Background policy: white page.
- Background variation confirmation: not applicable.
- Color token map: `--bg`, `--surface`, `--text`, `--muted`, `--border`, `--accent`, `--accent-contrast`, `--focus`, `--success`, `--danger`.
- Accent/status color limits: green for selection/CTA/status; red only for error fixture.
- Von Restorff emphasis target: the currently valid request CTA.
- Radius and shadow levels: 8px and 16px; one shadow reserved for the mobile action bar.
- Border minimization: dividers for rows; outlines only for controls and selection.
- Border-radius minimization: pills only for chips; rows are flat.
- Box-shadow usage: mobile terminal/action overlay only.
- List item border/shadow treatment: separator lines, no card shadows.
- Necessary badges/titles only: availability and demo-data disclosure; no decorative eyebrows.
- Word-break and wrapping: Korean phrase wrapping; long neighborhood fixture wraps safely.
- Components: semantic buttons, radiogroup-like pressed buttons, status region, result list.
- Imagery or media: inline geometric profile portraits; missing-media fallback is part of a result row.
- Motion: 180ms opacity/transform feedback; disabled under reduced motion.

Copy:
- Primary message: `오늘 산책을 맡길 사람을 고르자`.
- Domain terms that must appear: 중형견, 산책 가능, 리드줄, 60분, 거리, 요청.
- Generic terms or claims to remove: premium, smart, seamless, trusted.
- Sentence density rule: one sentence, one purpose.
- Copy length rule: controls under 18 Korean characters where practical.
- Redundant copy to avoid: headings that restate filter labels or result count.

States:
- Loading: not applicable; local synchronous fixture has no user-visible wait.
- Empty: incompatible size/time combination shows a recovery action that resets to the safe default.
- Error: a visibly disclosed `다음 요청 오류 시연` control shows a failed request and retry/cancel actions through the same renderer.
- Disabled: unavailable walker row uses a real disabled request control and explains the occupied slot.
- Hover/focus/active: all controls have hover, pressed, and 3px visible focus rings.
- Long content and extreme values: one intentionally long neighborhood and missing portrait fallback exercise wrapping.

Action Continuity:
- CTA cue and information scent: selected walker name, requested time, duration, and price sit immediately above/in the CTA.
- Start state and preconditions: safe defaults `중형견` and `오늘 19:00`; one matching walker preselected to avoid fabricated friction.
- Immediate feedback: selected row and request bar update; submission changes the status region immediately.
- Result or destination: request summary with walker, time, dog size, and price.
- Terminal state: `산책 요청을 보냈음` confirmation.
- Recovery: `요청 취소` restores the previous result context.
- Functional, disabled, and prototype-only controls: all visible controls are functional or semantically disabled; page is visibly labeled as fictional demo data.

Product Specificity:
- Domain signal 1: dog-size compatibility filter changes walker inventory.
- Domain signal 2: walker rows compare distance, available slot, leash/walk style, duration, and price.
- Domain signal 3: request confirmation retains dog size and walk time.
- Unrelated substitution domain 1 and breaking signals: laptop marketplace fails because dog size, leash handling, walking duration, and time slots are structural.
- Unrelated substitution domain 2 and breaking signals: recipe site fails because available human providers, distance, per-walk price, and request/cancel workflow are structural.
- Why name, logo, and color are not the only specific signals: the controls, data model, comparison order, constraints, and terminal outcome all belong to dog walking.

Anti-Slop Risks:
- Visual slop risk: a grid of floating rounded cards; reject with a flat comparison ledger.
- Content slop risk: invented trust metrics; disclose all profiles as fictional demo data and avoid ratings/testimonials.
- Interaction slop risk: filters or CTA that do nothing; each visible primary-flow control changes observable state.
- Verification slop risk: initial screenshot only; capture desktop/mobile start, terminal, recovery, empty/error fixtures.
- UI craft risk: metadata overload on mobile; keep only decision-critical facts and defer biography.

Verification Preflight:
- Dev-server or direct-open command: `python -m http.server 4174 --directory examples/pet-walker-marketplace-discovery`.
- Desktop/mobile browser and capture method: Codex in-app browser at 1440x1000 and 390x844.
- Interaction walkthrough method: semantic locator clicks, fresh DOM snapshots, terminal and recovery checks.
- Lighthouse JSON command: existing local Lighthouse CLI with installed Chromium, output under `artifacts/lighthouse.json`.
- Repository lint/typecheck/test/build commands: standalone HTML static assertions; no project build applies.
- Required dependencies confirmed: Python server, in-app browser, Chromium, and Lighthouse were available from the prior sample workflow.
- Quality report path: `examples/pet-walker-marketplace-discovery/quality-report.json`.
- Evidence catalog ID convention: `market-{viewport}-{state}`.

Visual Comparison Plan:
- Brand reference principle to compare: search/filter first and stable repeated metadata order.
- UI craft guideline to compare: flat list rhythm, one accent, minimal borders/shadows, natural Korean wrapping.
- AI slop counterexample to reject: generic rounded-card grid with inactive filters and vague CTA.
- Desktop screenshot evidence: start and terminal.
- Mobile screenshot evidence: start, terminal, empty/error as needed.
- Expected iteration count: two documented passes with at least one correction.
- Primary-task desktop walkthrough evidence: size/time selection, walker choice, request confirmation, cancellation.
- Primary-task mobile walkthrough evidence: same causal chain at 390px.
- Lighthouse JSON artifact: `artifacts/lighthouse.json`.
- Independent reviewer and blinded questions: fresh subagent reviews product identity, visible signals, action continuity, and generic/misleading remnants.

Acceptance:
- Screenshot should prove: the first viewport is recognizably a dog-walker marketplace with active search/filter/comparison and a concrete request path.
- Task walkthrough should prove: filters update results, choice updates consequence, request reaches confirmation, and cancellation recovers.
- Substitution test should prove: laptop marketplace and recipe site cannot reuse the structure by renaming only.
- Requirement trace should prove: user-requested archetype and screenshot map to rendered/interactive evidence.
- Lighthouse target: performance 80+, accessibility 90+, best practices 90+, SEO 90+.
- Commands to run: server, static assertions, browser walkthroughs, Lighthouse, quality validator.

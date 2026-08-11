# Visual Target — 썰림 600

- Created: 2026-08-04T21:25:53+09:00
- Baseline: new standalone sample in the Genscaff repository; no existing sample design system
- Profile: Genscaff Standard
- Classification: product-editorial archetype; landing and product-detail surfaces

## Product contract

- Product: fictional manual pull-cord vegetable chopper, `썰림 600`
- Primary user: one- or two-person households that want faster prep without losing control of texture
- User need: chop a small amount of vegetables quickly and choose coarse, fine, or paste-like texture
- Primary task: choose the useful bowl capacity, understand the pull-count result, and add the selected chopper
- Observable success: a product-specific cart confirmation shows capacity, price, and a remove recovery action
- Primary CTA: `600ml 다지기 담기 — 29,800원` by default; label follows the selected capacity
- Recovery: remove the added chopper and return to the configured state
- Domain objects: 400ml/600ml bowls, three offset blades, pull cord, lid lock, non-slip base, chopped vegetable texture
- Differentiators: pull-count texture guide; capacity tied to realistic ingredient amounts; detachable bowl-and-blade cleaning sequence
- Assumption ledger: all product specifications, prices, names, and copy are explicitly fictional sample content; no real performance or safety certification claim

## Direction decision

- Direction A — product macro editorial: one large transparent-bowl product illustration, short sections, and a pull-count texture sequence. Strong product comprehension and direct decision support; lower recipe breadth.
- Direction B — recipe magazine: meal photography and recipe stories lead, with the chopper appearing inside each recipe. Warmer lifestyle context; weaker first-viewport product understanding.
- Selected: Direction A. It makes the chopper mechanism, bowl size, texture decision, and add action visible without borrowing a real brand composition.

## Reference intent

- Mode: aesthetic inspiration
- Adopted Apple-derived principles: one dominant product object; one message per section; strong type hierarchy; media explains function; restrained motion
- Product fit: a compact kitchen tool needs immediate shape, mechanism, and scale comprehension before lifestyle storytelling
- Deliberate differences: asymmetric Korean editorial grid; lime-green pull cord as functional accent; interactive texture strip; capacity/ingredient decision beside the product; geometric SVG rather than photography
- Excluded from copying: Apple navigation, typography, exact section order, copy, assets, product imagery, colors, and distinctive transitions
- Repository-derived elements: none; this is an isolated sample

## Expanded brief

- First viewport: brand mark, plain navigation anchors, one product promise, large original SVG chopper, capacity decision, price, and one add CTA
- Sections: hero purchase decision; pull-count texture progression; exploded cleaning/structure view; compact final decision strip
- Shared components: anchor navigation, capacity segmented control, primary button, cart confirmation, remove action
- Desktop: 12-column editorial grid with product visual spanning the right half; decision panel aligned to the product base
- Mobile: product promise, product visual, selection, price, and CTA kept within an intentional vertical sequence
- Background: white, with black inverse sections only where product silhouette needs contrast
- Tokens: neutral white/ink/gray, one functional leaf-green accent, semantic focus/success roles
- Typography: system Korean sans; 12/14/16/20/24/32 scale plus one responsive display size for the site hero
- Spacing: 4/8/12/16/24/32/48/64 scale
- Radius: 0/8/16 only; pills restricted to capacity and texture controls
- Shadows: none on default surfaces; one subtle confirmation elevation
- Media: original inline SVG showing transparent bowl, vegetables, offset blades, lid, and pull cord
- Motion: 180–260ms transform/opacity feedback; disabled under reduced motion
- Copy: short Korean sentences, one claim per sentence, no fake reviews/awards/certifications

## State and action contract

- Start: 600ml selected with 29,800원 and ingredient capacity visible
- Selection: 400ml changes capacity guidance, CTA label, and price to 24,800원
- Feedback: CTA enters a brief busy state and updates an aria-live status
- Terminal: cart confirmation names selected capacity and price
- Recovery: `담기 취소` removes the confirmation and restores the configured state
- Loading: short deterministic button feedback only; no network wait or skeleton
- Empty/error: not applicable because this sample has no remote inventory or form submission
- Disabled: CTA is disabled only during the brief local transition
- Success: cart confirmation with selected product data
- Long content: long Korean ingredient guidance must wrap without clipping

## Product specificity and substitution

- Signal 1: pull-count texture scale (`3번 굵게`, `8번 잘게`, `15번 소스 질감`)
- Signal 2: bowl capacity translated into half-onion and garlic-clove amounts
- Signal 3: offset stainless blade, lid lock, non-slip base, and detachable cleaning sequence
- Decision: 400ml versus 600ml changes capacity guidance, price, and CTA result
- Banking substitution must fail because pull count, bowl volume, blades, ingredient amounts, and cleaning steps have no banking meaning
- Online-course substitution must fail because chopping texture, capacity, blades, cord action, and cleaning sequence have no learning-content meaning

## Risks and verification

- Craft risks: hero display type overwhelming the product; CTA separating from capacity context; Korean line breaks on narrow screens
- Slop risks: generic feature-card grid; decorative green gradients; fake proof metrics; rounded-card soup
- Visual pass 1: fix task/product visibility, hierarchy, wrapping, overflow, and control honesty
- Visual pass 2: fix spacing rhythm, focus visibility, motion, edge restraint, and product-media detail
- Desktop capture: 1440x1000 start and cart terminal
- Mobile capture: 390x844 start and cart terminal
- Walkthrough: capacity change → add → confirmation → remove, mouse and keyboard
- Lighthouse: performance ≥80, accessibility/best-practices/SEO ≥90
- Independent review: fresh subagent sees the user request and final artifacts without the intended verdict

# No-Slop Checklist

Every item is pass/fail. One failure means the work is not done.

Read `ai-slop-research.md` and `product-specificity-and-action-gate.md` before applying this checklist. Treat slop as low-quality, generic, conventional, misleading, or action-disconnected output that can look polished while lacking specific product substance. This checklist judges quality, not whether AI created the interface.

## Visual Slop

- No visual values invented when the project already has tokens, components, or scales.
- No linear, radial, conic, mesh, text, SVG, canvas, WebGL, or raster-baked gradient; no bokeh blob, orb, or abstract light field.
- No gradient page background. Default to solid white or black; any other solid or image background still requires the normal product-direction evidence.
- No untokenized color usage. Colors must flow through semantic tokens before component use.
- No glassmorphism, backdrop filter, backdrop blur, translucent glass card, or glass-like surface combination.
- No one-note palette dominated by a single trendy hue family.
- No unnecessary color variety. Keep one primary accent and only meaningful info/success/warning/danger colors.
- No misuse of alert colors as decoration. Warning, danger, success, and info colors must carry that meaning.
- No broken Von Restorff effect where too many elements compete as accents.
- No excessive border radius, shadow stacking, or card nesting.
- No border-first layout where every section, card, row, toolbar, or panel is outlined.
- No nested border stacks unless the product needs a table, form, or explicit grouped control.
- No rounded-corner style applied everywhere. Border-radius must be minimal and system-driven.
- No pill radius on ordinary cards, sections, panels, or buttons that do not need a pill shape.
- No box-shadow on most surfaces. Shadows are reserved for overlays, floating UI, dragged items, or rare interactive lift.
- No heavy border or shadow treatment unless the user requested it or the existing product system clearly uses it.
- No list item style that gives every row a heavy border, shadow, or card-like elevation by default.
- No decorative badges, eyebrow labels, or redundant section titles that do not aid orientation, state, category, or scanning.
- No oversized hero text inside compact panels or dashboards.
- No mismatched icon styles, stroke widths, image treatments, or button shapes.
- No visible text overlap, clipped labels, awkward wrapping, or accidental horizontal scroll.
- No awkward word breaks in Korean headings, labels, buttons, or cards; no long URLs, IDs, model names, emails, or numbers escaping their containers.
- No low-resolution, broken, stretched, darkened, or irrelevant images.
- No purple/blue SaaS gradient, radial glow, neon bloom, or AI-themed light beam. Brand precedent is not an exception inside Genscaff.
- No stock AI robot, floating chat bubble, abstract neural network, or meaningless dashboard art as the primary product proof.
- No uniform card grid where every section has the same radius, padding, icon treatment, and sentence rhythm.
- No overloaded viewport, section, card, list row, table cell, toolbar, or comparison panel.
- No magic-number spacing, raw colors, tiny text, inconsistent radius, or uncontrolled shadows when a design system is available.

## Product Slop

- No implementation from a vague request without first expanding it into a concrete design brief.
- No design direction selected before defining target user, user need, primary task, observable success, domain objects, differentiators, and recovery.
- No unmarked assumption presented as user research, product fact, repository fact, or verified claim.
- No first plausible layout accepted for broad new work without comparing a materially different composition or workflow direction.
- No ignored user constraints from the original request.
- No lorem ipsum, placeholder names, fake company logos, fake testimonials, or fake metrics presented as real.
- No generic AI marketing copy.
- No vague aspirational claims without a concrete object, workflow, audience, or outcome.
- No sentence that carries too many jobs at once. A sentence should not combine feature, benefit, target user, proof, caveat, and instruction.
- No unnecessarily long sentence where a shorter sentence preserves the meaning.
- No helper copy that repeats what the heading, label, icon, layout, or CTA already says.
- No polished sections that add visual weight but no new information.
- No repeated badge-title-description section formula unless each label and title carries specific product meaning.
- No hallucinated integrations, certifications, awards, customer logos, security claims, performance claims, or numerical results.
- No nav items, buttons, tabs, filters, forms, or controls that appear usable but do nothing without a clear disabled or mocked state.
- No first viewport that hides the actual product, brand, object, or workflow.
- No decorative page when the user asked for an app, dashboard, tool, or workflow.
- No single generic page when the requested product implies multiple screens, sections, or a flow.
- No screen or section that cannot be traced to a user need, explicit constraint, trust requirement, or necessary decision.
- No product whose name, logo, and accent color are its only category-specific signals.
- No main surface without realistic domain objects, vocabulary, content, data, media, decisions, constraints, or workflow states.
- No product or decision evidence selector duplicated, collapsed onto the same DOM node, or pointed at `body`, `main`, `#app`, `#root`, or another broad shell.
- No product evidence text hidden off-screen, made transparent, clipped away, covered, or reduced to a token-sized semantic decoy.
- No primary experience that asks only for reading or scrolling when the product promise implies a task.
- No product-specificity claim without a concrete decision and consequence visible in the interface.
- No PASS when either of two unrelated product substitutions still fits after replacing only name, logo, and color.

## Action Slop

- No context-free primary CTA when a specific action label is possible.
- No CTA whose label and surrounding context fail to predict the next state or destination.
- No primary action with hidden prerequisites, silent feedback, wrong destination, indefinite loading, or ambiguous completion.
- No primary task without a meaningful result, observable terminal state, and relevant recovery path.
- No visible navigation item, button, tab, filter, selector, form control, or comparison control that is an undisclosed dead end.
- No prototype-only control presented as finished production behavior.
- No success state that leaves the user unsure what happened or what to do next.
- No error path without correction, retry, cancel, back, undo, or another suitable recovery.
- No action-continuity PASS based only on static initial-state screenshots.
- No action PASS before the post-result observation reaches network idle, drains delayed responses, and confirms that action-created timeout, interval, and animation work is settled.

## Interaction Slop

- Required controls have hover, focus, active, disabled, loading, empty, and error states where applicable.
- Keyboard focus is visible for interactive elements.
- Forms expose validation and recovery paths.
- Inputs have visible labels; placeholders are not labels.
- One area has no more than one primary action.
- Touch targets meet minimum size expectations.
- Loading does not cause major layout shift.
- Error and empty states include useful next actions.

## Responsive Slop

- Desktop, tablet-like, and mobile widths preserve hierarchy and usable controls.
- Fixed-format UI uses stable dimensions, aspect ratios, or grid constraints.
- Text wraps naturally across desktop, tablet-like, and mobile widths without mid-word breaks, clipped controls, or horizontal overflow.
- Dense data views remain scannable on smaller screens.
- Mobile navigation and primary actions are reachable without layout collision.

## Accessibility Slop

- Text contrast is readable.
- Interactive targets are large enough to tap.
- Images that communicate meaning have alt text.
- Inputs have labels or accessible names.
- Heading order is coherent.
- Motion respects reduced-motion expectations when animations are substantial.

## Verification Slop

- No implementation start before confirming the dev-server, browser capture, task walkthrough, Lighthouse JSON, and repository-check commands are available.
- No end-loaded report authoring. Initialize the report after the product contract, add evidence as it is produced, and run the validator after each evidence phase.
- No duplicate evidence bookkeeping. Reuse a catalog ID only when the same artifact, region, and observation support the claim; otherwise capture or describe distinct evidence.
- No final answer without browser inspection for browser-rendered UI.
- No final answer when the final validator run only parses saved manifests. The validator must own a fresh desktop/mobile browser session and directly re-observe the actual DOM, pseudo-element computed styles, SVG/canvas activity, primary control activation through feedback/terminal/recovery, all visible controls, visible claim candidates, and console/page/network failures.
- No final answer without `rendered_roots` covering every served, previewed, exported, or deployable output. `dist`, `build`, `out`, bundled CSS/JS/SVG, public assets, and encoded data URIs cannot disappear behind generated/vendor ignore rules.
- No final answer when loaded first-party or external resource hashes and decoded-body observations do not match source fingerprints, rendered outputs, capture/control/content manifests, and the report.
- No final answer without comparing the screenshot to a brand reference principle and an AI slop risk.
- No final answer without checking UI craft rules: token reuse, semantic color tokenization, background policy, accent minimization, screen information density, sentence density, copy length, spacing scale, type scale, border minimization, border overuse, border-radius minimization, border-radius overuse, box-shadow overuse, radius/shadow limits, list item border/shadow restraint, necessary badges/titles, word-break behavior, state coverage, and accessibility basics.
- No final answer without reporting verification commands.
- No final answer with unresolved console errors.
- No final answer with Lighthouse below threshold unless the user explicitly accepts the failure.
- No final answer when the result merely "looks modern" but cannot explain which concrete product signal, brand principle, and no-slop item it satisfies.
- No final answer without tracing `primary-task`, `primary-cta`, explicit constraints, and differentiators to visible or interactive evidence.
- No final answer without desktop and mobile walkthroughs from the primary trigger to a terminal state.
- No final answer without the two-domain five-axis substitution test, mutually distant alternates, and at least four structurally broken axes per domain.
- No final answer with an undisclosed dead-end control in the primary viewport or task.
- No final answer based on self-attested booleans, one-character notes, placeholder paths, duplicate screenshots, or claimed Lighthouse scores.
- No final answer without real local screenshot artifacts and a parsed local Lighthouse JSON artifact.
- No final answer without a real pre-code visual-target artifact that predates the first review screenshot.
- No final answer with only a blanket state boolean; loading, empty, error, disabled, success, and long-content need per-state implementation evidence or a concrete not-applicable rationale.
- No final answer without a primary-task control inventory proving functional, disabled, or disclosed prototype behavior.
- No final answer when the reported Lighthouse scores do not match the saved artifact or fall outside `0..100`.
- No final answer without at least two ordered review-pass records containing findings, changes, and evidence.
- No final answer for screen, flow, site, or design-board work without a fresh subagent's blind product-specificity, action-continuity, and anti-slop review plus its raw JSON artifact.
- No claim that a local review JSON proves fresh-subagent provenance. The root agent must separately verify the actual collaboration mailbox task ID, distinct reviewer identity, blind request, supplied capture hashes, raw response, and completed state; otherwise mark `REVIEW_PROVENANCE_UNVERIFIED` and do not report the work complete.
- No final answer without source fingerprint, capture manifest, desktop/mobile computed-style manifests, desktop/mobile control manifests, independent-review artifact, and command execution manifest from schema v3.
- No final answer when any mandatory gate is `NOT TESTED`; missing evidence never collapses into PASS.
- No claim that Lighthouse, build success, responsive rendering, or automated accessibility checks prove product quality or absence of AI slop.
- No unqualified `PASS`, “AI Slop 아님”, AI non-use, human authorship, universal originality, representative-user success, or certified quality claim. Report only the bounded structural checks and mailbox provenance check actually completed.

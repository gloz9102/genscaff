# Standard Verification Baseline

Verification claims are evidence ceilings, not intent statements. Keep result, method, coverage, evidence, issues, and limitations separate.

## Render

Observe required desktop and mobile routes. Check uncaught console errors, unintended horizontal overflow, clipping, long content, and matching screenshot evidence.

Check that the layout does not compress everything into one viewport without a task need or explicit request. Accept whitespace; information-intensive dashboards and back offices may legitimately be denser. Verify that topic/context changes in copy render as separate lines or paragraphs on desktop and mobile, rather than relying on collapsed source newlines.

Inspect accent consumers for shared theme tokens, including foreground and interaction variants, so a requested replacement does not require per-component edits. When the accent changes, verify affected contrast and states.

Measure document overflow separately from intentional component scrolling. A wide table may scroll locally, but its labels, focused controls, and positioned descendants must not create page-level scrolling or become unreachable. When overflow occurs, locate the element and its containing block, repair the affected layout, and repeat render and keyboard/action checks while preserving content. Missing browser access leaves this check unverified; source inspection or a model preference cannot establish a render pass.

## Primary flow

Observe trigger, feedback, and terminal result. Verify recovery only when failure, cancellation, reversal, incomplete state, network, or transaction behavior makes it real.

For affected direct-action controls, observe hover feedback where supported and immediate press/click feedback, including equivalent keyboard/touch activation. Check reduced-motion behavior where effects use motion. A terminal result alone does not establish immediate reaction feedback.

For a hover check, compare the normal, pointer-over, and pointer-out states of the same control. Distinguish a container's color/geometry from animated descendants and check stable hit areas, surrounding layout, and accessible names without duplicate decorative labels. For revealed content, verify trigger-to-panel movement, submenu entry, applicable back navigation, dismissal, focus return, and an equivalent click/keyboard path; a CSS rule or screenshot alone does not prove the interaction. Report which transitions were actually observed. Record the actual pointer method and any substitutions; declared CSS durations are not measured response latency.

For mobile checks, record viewport dimensions and input capabilities, distinguishing viewport resizing, touch emulation, and real-device testing. Resizing a desktop browser proves responsive layout only, not touch behavior or mobile OS link routing; emulation also does not prove OS behavior. Check coherent visual/reading/focus order, meaningful media crop, Korean phrase wrapping, horizontal or stacked actions as appropriate, menu opening/submenu/back-or-close paths, and document overflow separately from intentional component scrolling. Do not infer touch target usability or absence of hover dependence from a narrow screenshot.

Check control feedback independently of content animation. Essential text and actions must remain available when motion is reduced or media fails; a temporary animation frame is not a final-state defect or a completed-state pass.

## Preservation and reference evidence

Compare each affected invariant with its brief or before-state baseline: required visible information and values, accessible names, meaningful reading/focus order, and action outcomes. Use rendered observations, accessibility-tree inspection, and relevant interaction checks; source or DOM equality alone is insufficient. Inspect CSS-generated text and hidden content when they affect required information. Decorative pseudo-elements are not failures by themselves.

Record each invariant's implementing region, actual observation, evidence, and any permitted change or unresolved discrepancy. Re-run affected checks after defect fixes even when the aesthetic review budget is exhausted. A preservation failure fails the relevant render, flow, keyboard, or accessibility check; preference for a candidate cannot offset it.

For adopted reference principles, connect the inspected source observation to the actual target implementation and rendered result. For candidate comparison, distinguish representative-screen evidence from selected-product verification. Preserve existing status ceilings; neither reference traces nor a user's visual selection certify beauty, originality, WCAG conformance, or user success.

## Keyboard and focus

Exercise the complete critical path using applicable Tab, Shift+Tab, Enter, Space, Escape, composite-widget arrows, and Home/End. Check dialog entry, containment, close, focus return, focus visibility inside horizontal content, and sticky UI occlusion. Do not award keyboard status from one sampled activation.

## Accessibility dimensions

Record keyboard, focus, automated accessibility, manual accessibility, assistive-technology user validation, and representative-user validation independently. Check names, headings, landmarks, error association, dynamic announcements, drag alternatives, target spacing, reduced motion, zoom, and reflow where relevant.

Automation does not establish WCAG conformance. Keyboard testing is not screen-reader testing. Neither is representative-user validation.

## Status ceiling

- `IMPLEMENTED_UNVERIFIED`: browser evidence absent.
- `VERIFIED_RENDER`: Render evidence complete.
- `VERIFIED_PRIMARY_FLOW`: Render plus primary-flow evidence complete.
- `VERIFIED_KEYBOARD_FLOW`: Primary Flow plus complete critical keyboard/focus evidence complete.
- `VERIFIED_STANDARD_BASELINE`: Keyboard Flow plus all relevant state evidence and no unresolved critical automated finding in tested states.

Every verified status requires matching, in-root, readable artifacts and concrete observations. Boolean claims, strings, nonexistent files, path traversal, outside-root artifacts, and unverified reviewer claims cannot raise status.

# Standard Verification Baseline

Verification claims are evidence ceilings, not intent statements. Keep result, method, coverage, evidence, issues, and limitations separate.

## Render

Observe required desktop and mobile routes. Check uncaught console errors, unintended horizontal overflow, clipping, long content, and matching screenshot evidence.

## Primary flow

Observe trigger, feedback, and terminal result. Verify recovery only when failure, cancellation, reversal, incomplete state, network, or transaction behavior makes it real.

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

# Standard Verification Baseline

Verification claims are evidence ceilings, not intent statements. Keep result, method, coverage, evidence, issues, and limitations separate.

## Render

Observe required desktop and mobile routes. Check uncaught console errors, unintended horizontal overflow, clipping, long content, and matching screenshot evidence.

## Primary flow

Observe trigger, feedback, and terminal result. Verify recovery only when failure, cancellation, reversal, incomplete state, network, or transaction behavior makes it real.

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

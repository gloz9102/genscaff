# Responsive and State Matrix

Identify possible states from real data and interaction boundaries. Implement and verify only states relevant to the changed flow; do not manufacture impossible errors or recovery.

Consider: `initial`, `loading`, `partial-loading`, `empty`, `error`, `retrying`, `disabled`, `hover`, `focus-visible`, `active`, `selected`, `unavailable`, `success`, `long-content`, `missing-image`, `slow-image`, `broken-image`, and `offline-or-degraded-network` when relevant.

For each affected surface record:

- state trigger and observable result
- data retained, replaced, or unavailable
- action available to continue or recover
- desktop, mobile, and container-size behavior
- keyboard and focus behavior
- evidence or explicit verification ceiling

Review long Korean and English text, RTL/writing direction when localization applies, 200% zoom and text reflow, fixed-height clipping, desktop/mobile horizontal overflow, and focus visibility inside sticky or horizontally scrollable regions. Consider container queries when component width matters more than viewport width.

For responsive media, inspect `srcset`, `sizes`, intrinsic dimensions or `aspect-ratio`, loading behavior, missing/broken fallback, and layout stability. Choose viewports from product support data; useful probes include 360x800, 390x844, 768x1024, 1280x800, 1440x900, and 1600x900.

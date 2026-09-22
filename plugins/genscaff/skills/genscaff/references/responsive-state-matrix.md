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

Recompose narrow layouts from message and action priority instead of uniformly shrinking the desktop composition. Media may move before or after text when that improves understanding, but preserve a coherent visual, DOM reading, and keyboard focus order. Avoid CSS-only rearrangements that make focus jump contrary to the visible sequence.

Decide action-group direction from label length, available space, and target dimensions. Check both horizontal and stacked outcomes when the breakpoint changes; do not enforce stacking solely because the device is called mobile. Re-evaluate desktop hard line breaks and media crops so Korean phrases, control labels, and explanatory subjects remain intact.

For affected menus, exercise opening, submenu entry, back navigation when hierarchical, closing, and appropriate focus return. Check the trigger-to-panel pointer path and click/keyboard alternatives for hover-revealed content. A closed-menu screenshot cannot establish that the expanded menu fits or remains operable.

Record input capabilities separately from width. Check hover and pointer media conditions where relevant, and preserve a non-hover path on touch and hybrid devices. Label evidence as viewport resizing, touch emulation, or real-device testing; emulation does not prove mobile OS download/deep-link behavior.

For wide tables, keep horizontal scrolling inside a bounded container while the document fits the viewport. Give absolutely positioned descendants, including visually hidden accessible labels, a containing block in their owning component or scroll container; otherwise an off-screen table cell can enlarge the document even when the table itself is clipped. Preserve the labels and reachable row actions. Repair the containing block or layout constraint rather than masking the defect with root-level overflow hiding. Check the document width and keyboard focus after scrolling the table, not just the table wrapper's CSS.

Keep grid/flex children shrinkable through responsive overrides: a single `1fr` track still has an automatic content minimum, so a wide table may require `minmax(0, 1fr)` and `min-inline-size: 0` on its owning item. Choose a layout's collapse point from its column minima, gaps, and padding rather than a device label; check just above and below that point as well as desktop and mobile. A local scroll wrapper cannot fix an ancestor that already exceeds the viewport.

For responsive media, inspect `srcset`, `sizes`, intrinsic dimensions or `aspect-ratio`, focal-point crop, loading behavior, missing/broken fallback, and layout stability. Preserve the subject or product detail supporting the adjacent claim at each tested size. Choose viewports from product support data; useful probes include 360x800, 390x844, 768x1024, 1280x800, 1440x900, and 1600x900.

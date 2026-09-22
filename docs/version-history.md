# Version history and evaluation context

[English](version-history.md) | [한국어](version-history.ko.md) | [README](../README.md)

Version changes and evaluation context moved from the README. Historical claims retain their original scope. Published versions are listed in [GitHub Releases](https://github.com/gloz9102/genscaff/releases).

## Version 2.2.5 mobile and hover guidance

Mobile layouts now explicitly recompose content, media crops, and action groups around task priority. Hover feedback follows control roles while preserving layout, hit areas, and accessible names. Menus require applicable submenu, back/close, and focus-return paths with non-hover alternatives.

Verification distinguishes viewport resizing, touch emulation, and real devices, and compares normal, hover, and pointer-out states. These changes supplement the six product-expression principles. Quick retains its affected-scope checks; one v2.2.5 paired PC cafe demonstration is documented in the [comparison record](v2.2.5-pccafe-comparison.md); the repeated release evaluation has not run. The [mobile and hover observation record](design-reference-mobile-hover.ko.md) documents the sampled references and limitations.

## Version 2.2.0 UI defaults

- Keep screens focused and allow whitespace instead of packing everything into one viewport. Dashboards, back offices, other information-intensive pages, and explicit user requests may use higher density.
- Separate changes of context or topic into rendered lines or paragraphs.
- Provide hover and press/click feedback for direct actions, with keyboard/touch equivalents and reduced-motion support. Ask the user when the appropriate reaction is unclear.
- Choose a primary accent by default and centralize its foreground and interaction variants in shared theme tokens for quick replacement.

These defaults apply to Quick and Standard. Version 2.2.0 behavioral A/B evaluation has not run; earlier evaluation results remain historical evidence. Source versioning does not publish a release.

## Version 2.1.0 transition

The legacy source tree, legacy ZIP, and `$genscaff strict` compatibility route are removed. Retired invocations provide migration guidance without starting an audit or a Standard task. Existing report-schema compatibility is preserved. Version 2.1.0 was published as a prerelease; its evaluation limitations remain historical evidence.

## Retained v2.0.1 loading contract

- Any user-visible asynchronous boundary must follow a wait-removal-first loading contract, preserve usable context, expose honest status and recovery, and document the observed boundary instead of treating a spinner as completion.
- Standard and Strict reports reject incomplete loading-boundary records; `async` and `generation` Strict work must declare and evidence the loading experience.

## Retained workflow: instruction consolidation and audit internals

Core instructions now reuse one product/design contract and route detailed requirements to existing references. The general UI craft file, its enforcement, and its loading condition are unchanged. Strict internals are separated by responsibility while preserving CLI entrypoints, report schemas, and validation rules.

Windows patch writes were recovered using the app-bundled CLI 0.155.0-alpha.2.6 with workspace-write isolation. The revised PR rerun completed all 16 processes after credits were restored, and the affected no-browser pair completed both runs. Eight blind/order-swapped comparisons and the user’s sampled booking/transfer preferences produced 6 treatment preferences and 2 control preferences. These include instruction compliance, not just visual quality. Both dashboard pairs still overflow at 390px; full behavioral acceptance remains withheld. PR median input tokens increased despite a shorter median runtime, so no cost-reduction claim is made. The [v2.1 evaluation record](../evals/v2.1-transition.md) separates original failures, reruns, model scores, user preferences, and observed defects. The 120-run release evaluation was not run. [Earlier blocked trials and Strict equivalence evidence](../evals/instruction-refactor.md) remain preserved.

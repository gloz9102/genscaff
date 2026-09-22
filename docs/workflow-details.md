# Workflow details

[English](workflow-details.md) | [한국어](workflow-details.ko.md) | [README](../README.md)

Detailed design selection, preservation, classification, evidence, and runtime guidance.

## Retained workflow: design exploration and preservation

These workflows are included in v2.2.5.

- Open-direction new surfaces and major redesigns default to two comparable representative-screen candidates followed by user selection. Users can choose a single direction or explicitly delegate selection. Quick fixes, locked reproduction, and composition-settled extensions skip comparison.
- Preservation covers required visible information, accessible names, meaningful order, and action outcomes; unchanged HTML alone is insufficient. Reference principles are traced from observed source to implementation and rendered evidence.
- Existing aesthetic rules remain unchanged. Candidate comparison is separate from the selected implementation's two aesthetic review passes; content, functional, accessibility, and runtime fixes still require re-verification.

```text
$genscaff Build a new booking page.                  # Default: compare two representative candidates
$genscaff Build a booking page in a single direction. # Opt out of comparison
$genscaff Compare two directions and choose for me.  # Explicitly delegate selection
```

Without explicit delegation, selection waits for the user before expanding the chosen direction. Missing browser access retains two comparable, clearly unverified direction descriptions and available source work; it does not silently select one or claim rendered evidence.

See the [exploration workflow](../plugins/genscaff/skills/genscaff/references/design-exploration.md), [preservation contract](../plugins/genscaff/skills/genscaff/references/visual-target-template.md), and [reference trace requirements](../plugins/genscaff/skills/genscaff/references/reference-intent.md). The [evaluation protocol and quick-check findings](../evals/design-preservation.md) distinguish observed behavior from untested requirements.

## Current frontend workflow

- Schema v6 separates verification `result`, `method`, `coverage`, evidence, issues, and limitations.
- New reports use `IMPLEMENTED_UNVERIFIED`, `VERIFIED_RENDER`, `VERIFIED_PRIMARY_FLOW`, `VERIFIED_KEYBOARD_FLOW`, and `VERIFIED_STANDARD_BASELINE`. Evidence-free booleans or `pass` strings cannot raise status.
- Standard classifies `project_mode`, four reference modes, one primary experience archetype, relevant surface types, and change scope before broad work.
- The product/design contract covers product, reference, content, visual-system, engineering, and preservation decisions, with exploration records when applicable. Recovery is required only when failure, cancellation, reversal, incompletion, network, or transaction behavior makes it real.
- Six focused craft modules cover product editorial, marketplace discovery, media discovery, workflow applications, content editorial, and transactions.
- Named-site inspiration defaults to principle extraction with deliberate differences, not logo, copy, asset, composition, navigation, geometry, or interaction cloning.
- Product and transaction craft rejects invented selection steps and disabled CTAs as `FABRICATED_FRICTION`.
- Strict uses a compact workflow rubric instead of loading historical AI-slop and brand-research chains.
- The deterministic A/B harness prepares eight paired PR tasks (16 runs) or 120 release runs. Its 30 static behavior cases include preservation, design selection, reference tracing, and defect re-verification; these definitions are not executed trials. Optional frozen-skill baselines support previous-versus-current comparisons.
- The core skill has no Node, Playwright, or Lighthouse dependency; those remain in release-audit.

Schema v3/v4 Strict reports remain supported by release-audit. Core schema v5 Standard reports remain readable: legacy `VERIFIED_FLOW` maps at most to `VERIFIED_PRIMARY_FLOW`, and `VERIFIED_STANDARD` maps at most to `VERIFIED_KEYBOARD_FLOW` after evidence validation. New reports do not emit legacy names.

## Classification and references

Reference modes are `locked-reproduction`, `structural-reference`, `aesthetic-inspiration`, and `no-reference`. A supplied screenshot is not automatically locked. Exact reproduction requires an explicit lock scope and rights to supplied assets.

Experience archetypes describe the product job: `product-editorial`, `marketplace-discovery`, `media-discovery`, `workflow-application`, `content-editorial`, or `transaction`. Surface types describe the changed screen, such as `landing`, `search`, `listing`, `detail`, `dashboard`, `form`, or `checkout`.

```text
"Use Apple product-page clarity and pacing, but copy none of its layout,
assets, navigation, copy, typography, or interactions."
→ aesthetic-inspiration / product-editorial / landing

"Use mature Airbnb-like search, comparison, availability, and trust
principles without its branding or component geometry."
→ aesthetic-inspiration / marketplace-discovery / search, listing

"Use mature Netflix-like content-discovery principles with progress,
missing-media handling, and complete keyboard navigation, without copying it."
→ aesthetic-inspiration / media-discovery / landing, listing
```

These classifications guide craft; they do not replace user requirements or an existing information architecture.

## Runtime and approval model

Missing Chrome caps Standard at source implementation without browser evidence; missing Lighthouse blocks only its audit. Missing Strict-only dependencies or a reviewer makes Strict incomplete. Safe source edits continue unless the deliverable itself cannot be produced.

Read-only inspection, project command execution, dependency installation, active browser access, network commands, and destructive operations are separate permissions. A request to modify and test the workspace may authorize inspected non-destructive lint/test/build commands, but not installs, deploys, migrations, credentials, network access, or cleanup. Validation output is scoped evidence, not WCAG conformance or legal/originality certification.

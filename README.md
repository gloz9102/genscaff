<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/brand/genscaff-logo-dark.png"><source media="(prefers-color-scheme: light)" srcset="docs/assets/brand/genscaff-logo-light.png"><img src="docs/assets/brand/genscaff-logo-light.png" alt="Genscaff" width="760"></picture></p>

# Genscaff

[English](README.md) | [한국어](README.ko.md)

Genscaff is an explicitly invoked Codex plugin for evidence-backed frontend work. The lightweight `$genscaff` skill guides Quick and Standard generation; `$genscaff-release-audit` isolates the expensive Strict release gate. User requirements and the existing design system always outrank its heuristics.

This independent community project is not affiliated with or endorsed by OpenAI.

## Install from the GitHub marketplace

```shell
codex plugin marketplace add gloz9102/genscaff --ref main
codex plugin add genscaff@genscaff-public
```

Restart Codex or open a new task. Neither skill is invoked implicitly.

```text
$genscaff                 # Standard: normal generation and redesign
$genscaff quick           # Quick: a small local change
$genscaff-release-audit   # Strict: release-critical exhaustive audit
$genscaff strict          # Retired in v2.1; use $genscaff-release-audit
```

## Version 2.2.5 mobile and hover guidance

Mobile layouts now explicitly recompose content, media crops, and action groups around task priority. Hover feedback follows control roles while preserving layout, hit areas, and accessible names. Menus require applicable submenu, back/close, and focus-return paths with non-hover alternatives.

Verification distinguishes viewport resizing, touch emulation, and real devices, and compares normal, hover, and pointer-out states. These changes supplement the six product-expression principles. Quick retains its affected-scope checks; one v2.2.5 paired PC cafe demonstration is documented below; the repeated release evaluation has not run. The [mobile and hover observation record](docs/design-reference-mobile-hover.ko.md) documents the sampled references and limitations.

## Version 2.2.0 UI defaults

- Keep screens focused and allow whitespace instead of packing everything into one viewport. Dashboards, back offices, other information-intensive pages, and explicit user requests may use higher density.
- Separate changes of context or topic into rendered lines or paragraphs.
- Provide hover and press/click feedback for direct actions, with keyboard/touch equivalents and reduced-motion support. Ask the user when the appropriate reaction is unclear.
- Choose a primary accent by default and centralize its foreground and interaction variants in shared theme tokens for quick replacement.

These defaults apply to Quick and Standard. Version 2.2.0 behavioral A/B evaluation has not run; earlier evaluation results remain historical evidence. Source versioning does not publish a release.

## Version 2.1.0 transition

The legacy source tree, legacy ZIP, and `$genscaff strict` compatibility route are removed. Retired invocations provide migration guidance without starting an audit or a Standard task. Existing report-schema compatibility is preserved. This source version does not imply a published release.

## Retained v2.0.1 loading contract

- Any user-visible asynchronous boundary must follow a wait-removal-first loading contract, preserve usable context, expose honest status and recovery, and document the observed boundary instead of treating a spinner as completion.
- Standard and Strict reports reject incomplete loading-boundary records; `async` and `generation` Strict work must declare and evidence the loading experience.

## Retained workflow: instruction consolidation and audit internals

Core instructions now reuse one product/design contract and route detailed requirements to existing references. The general UI craft file, its enforcement, and its loading condition are unchanged. Strict internals are separated by responsibility while preserving CLI entrypoints, report schemas, and validation rules.

Windows patch writes were recovered using the app-bundled CLI 0.155.0-alpha.2.6 with workspace-write isolation. The revised PR rerun completed all 16 processes after credits were restored, and the affected no-browser pair completed both runs. Eight blind/order-swapped comparisons and the user’s sampled booking/transfer preferences produced 6 treatment preferences and 2 control preferences. These include instruction compliance, not just visual quality. Both dashboard pairs still overflow at 390px; full behavioral acceptance remains withheld. PR median input tokens increased despite a shorter median runtime, so no cost-reduction claim is made. The [v2.1 evaluation record](evals/v2.1-transition.md) separates original failures, reruns, model scores, user preferences, and observed defects. The 120-run release evaluation was not run. [Earlier blocked trials and Strict equivalence evidence](evals/instruction-refactor.md) remain preserved.

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

See the [exploration workflow](plugins/genscaff/skills/genscaff/references/design-exploration.md), [preservation contract](plugins/genscaff/skills/genscaff/references/visual-target-template.md), and [reference trace requirements](plugins/genscaff/skills/genscaff/references/reference-intent.md). The [evaluation protocol and quick-check findings](evals/design-preservation.md) distinguish observed behavior from untested requirements.

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

## Profiles

| Invocation | Scope | Evidence |
|---|---|---|
| `$genscaff quick` | Small copy, component, or local style change | Affected code; one viewport when needed |
| `$genscaff` | Ordinary generation or redesign | Desktop/mobile render, flow, console, overflow, keyboard and focus |
| `$genscaff-release-audit` | Trusted release-critical frontend | Four checkpoints, full controls, Lighthouse, provenance, independent review |

Genscaff does not ban gradients, glass, blur, or glow. It preserves effects required by the user, a locked reference, or the project system. It is not an authorship detector, originality certificate, or substitute for representative-user testing.

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

## Genscaff 2.2.5 Standard comparison: PC cafe

Two independent agents built a landing page for fictional **LEVEL PC Lounge** using the same brief, generated hero image, model (`gpt-5.6-luna`), and reasoning effort (`xhigh`). One used Genscaff Standard; the other used no frontend design skill. Design selection was delegated.

| Standard applied | Without Genscaff |
|---|---|
| <img src="examples/v2.2.5-pccafe-comparison/artifacts/standard-desktop.png" alt="LEVEL PC landing page with Genscaff Standard" width="560"> | <img src="examples/v2.2.5-pccafe-comparison/artifacts/control-desktop.png" alt="LEVEL PC landing page without Genscaff" width="560"> |
| [Source](examples/v2.2.5-pccafe-comparison/standard/index.html) | [Source](examples/v2.2.5-pccafe-comparison/control/index.html) |

| Observed difference | Standard applied | Without Genscaff |
|---|---|---|
| Visual composition | Amber accent, restrained surfaces | Lime accent, large italic emphasis, colored seat panels |
| Visit confirmation | Inline below the calculator | Separate modal |
| Review corrections | Korean word wrapping, mobile-menu keyboard access, secondary-text contrast | Emphasized text contrast on light backgrounds, reduced-motion scrolling |
| Shared functional checks | Desktop/mobile pricing, confirmation/editing, keyboard, hover, touch menu passed | Same checks passed |

Colors and composition are choices made for this sample, not a style imposed by the skill. Both outputs include review corrections; neither functional superiority nor general quality improvement is established. Standard candidate captures were added after implementation and do not demonstrate completion of rendered selection before implementation.

Both pages calculate seat and duration costs and display an editable visit preview. No reservation or payment is submitted. The hero is a concept image generated with the built-in imagegen tool, not a real venue photograph.

```shell
python -m http.server 8835 --bind 127.0.0.1 --directory examples/v2.2.5-pccafe-comparison
```

Open the [comparison](http://127.0.0.1:8835/) after starting the server. No frontend build is required.

[Mobile and full-page screenshots, findings and limitations](docs/v2.2.5-pccafe-comparison.md) | [Shared brief](examples/v2.2.5-pccafe-comparison/brief.md) | [Image prompt](examples/v2.2.5-pccafe-comparison/assets/provenance.md)

This is one paired demonstration with parent-reviewed corrections, not a statistical or blind effectiveness study. The earlier [v2.2 Quick examples](docs/v2.2-quick-examples.md) remain available as historical samples.

## Repository layout

```text
.agents/plugins/marketplace.json
plugins/genscaff/{.codex-plugin,assets,skills/{genscaff,genscaff-release-audit}}
evals/                   # cases, rubric, evaluation protocol, checked-in summaries
tools/                   # validators, deterministic packaging, eval harness
```

## Validate

Core checks use Python. Strict additionally uses the Node version and production dependencies declared by its bundled manifest plus Chrome/Chromium; the manifest is the runtime source of truth.

```shell
python tools/check_skill.py
python -m unittest discover -s tools -p "test_*.py"
python -m unittest discover -s plugins/genscaff/skills/genscaff/scripts -p "test_*.py"
npm ci --omit=dev --prefix plugins/genscaff/skills/genscaff-release-audit/scripts
npm audit --omit=dev --audit-level=moderate --prefix plugins/genscaff/skills/genscaff-release-audit/scripts
python plugins/genscaff/skills/genscaff-release-audit/scripts/test_quality_gate.py
python tools/package_skill.py
```

The validator never replays repository commands by default. `--execute-approved-commands` is only for an inspected repository the user explicitly trusts. Active browser audits execute page JavaScript and may make external requests.

## Evaluation harness

Use `prepare --baseline-skill <previous-core-skill>` to compare the current skill against a frozen previous skill. Both arms then explicitly invoke Genscaff with equal prompts; omitting the option preserves the no-skill control. The non-interactive harness delegates design selection in both arms. See [design preservation evaluation](evals/design-preservation.md) for interactive choice cases, raw fixture requirements, quality/cost criteria, and the boundary between static cases and executed trials.

```shell
python tools/eval_harness.py prepare --suite pr --model gpt-5.6-terra --reasoning medium --output eval-run
python tools/eval_harness.py run --run-dir eval-run
python tools/eval_harness.py blind --run-dir eval-run
python tools/eval_harness.py score --run-dir eval-run
python tools/eval_harness.py validate --run-dir eval-run
```

Use `run --codex-bin <executable>` when multiple CLI installations exist; the harness records the resolved executable and version. `--windows-sandbox elevated|unelevated` and `--jobs 1|2|4` are explicit per-run settings. Resume preserves the recorded execution policy.

Model runs use local Codex authentication, isolated Git workspaces, `codex exec --ephemeral --ignore-user-config --ignore-rules --sandbox workspace-write`, and preserved JSONL traces. Raw runs stay out of Git and belong in release artifacts; only summaries are committed.

## Distribution packages

`python tools/package_skill.py` creates reproducible `genscaff-plugin.zip` and versioned evaluation artifacts with SHA-256 sidecars. The evaluation filename follows the plugin manifest version. `--kind plugin` creates only the plugin archive; `--kind all` (default) also includes evaluation artifacts. `--kind legacy` is no longer accepted. Historical evaluation summaries retain their original version names.

## License

Project-owned source and documentation use [Apache License 2.0](LICENSE). See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [SECURITY.md](SECURITY.md).

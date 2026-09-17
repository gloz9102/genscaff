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

## Version 2.1.0 transition

The legacy source tree, legacy ZIP, and `$genscaff strict` compatibility route are removed. Retired invocations provide migration guidance without starting an audit or a Standard task. Existing report-schema compatibility is preserved. This source version does not imply a published release.

## Retained v2.0.1 loading contract

- Any user-visible asynchronous boundary must follow a wait-removal-first loading contract, preserve usable context, expose honest status and recovery, and document the observed boundary instead of treating a spinner as completion.
- Standard and Strict reports reject incomplete loading-boundary records; `async` and `generation` Strict work must declare and evidence the loading experience.

## Unreleased: instruction consolidation and audit internals

Core instructions now reuse one product/design contract and route detailed requirements to existing references. The general UI craft file, its enforcement, and its loading condition are unchanged. Strict internals are separated by responsibility while preserving CLI entrypoints, report schemas, and validation rules.

Windows patch writes were recovered using the app-bundled CLI 0.155.0-alpha.2.6 with workspace-write isolation. The revised PR rerun completed all 16 processes after credits were restored, and the affected no-browser pair completed both runs. Eight blind/order-swapped comparisons and the user’s sampled booking/transfer preferences produced 6 treatment preferences and 2 control preferences. These include instruction compliance, not just visual quality. Both dashboard pairs still overflow at 390px; full behavioral acceptance remains withheld. PR median input tokens increased despite a shorter median runtime, so no cost-reduction claim is made. The [v2.1 evaluation record](evals/v2.1-transition.md) separates original failures, reruns, model scores, user preferences, and observed defects. The 120-run release evaluation was not run. [Earlier blocked trials and Strict equivalence evidence](evals/instruction-refactor.md) remain preserved.

## Unreleased: design exploration and preservation

These workflows are retained in the 2.1.0 source version; publication is a separate step.

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

## Same-brief sample

The following public samples predate v2.1. They remain historical examples, not performance evidence for the current instructions.

Two independent `terra-medium` agents received the same product-page brief. Only the treatment explicitly invoked Genscaff Standard.

| Genscaff Standard | Control |
|---|---|
| <img src="docs/assets/slowdrop-comparison/genscaff-with.png" alt="Product page built with Genscaff Standard" width="720"> | <img src="docs/assets/slowdrop-comparison/genscaff-without.png" alt="Control product page built without Genscaff" width="720"> |

Both outputs were usable. This one qualitative pair does not establish superiority; see the [full comparison](docs/slowdrop-comparison.md). v2.0 treats its first scored release run as a baseline rather than a marketing claim.

## Quick anti-slop A/B (directional)

One isolated `gpt-5.6-terra` low-effort pair received the same fictional FlowPilot landing-page brief. The treatment explicitly invoked the then-current Genscaff Standard Skill; the control could not inspect it. This is directional evidence from two agents, not statistical proof.

| Parent-verified result | Genscaff | Control |
|---|---:|---:|
| Desktop render and primary interaction | Pass | Pass |
| Reliable 390×844 render evidence | Pass | Fail: renderer scaling limitation |
| Valid Standard schema v6 report | Pass | Not produced |
| Lighthouse P/A/BP/SEO | 100/98/100/100 | 100/95/100/100 |
| Remaining generic-default cluster | Yes | Yes, broader |

Genscaff helped by grounding the hero in a concrete approval route, retaining desktop/mobile flow evidence, and producing a validator-clean evidence report. It did not fully solve report honesty: the rendered treatment still contained decorative eyebrow copy, unsupported time-saved/setup claims, and nested workflow-row geometry that its own report did not list. The control combined a gradient hero, decorative eyebrow, nested workflow cards, and a uniform feature-card grid, while its mobile screenshot could not substantiate the requested viewport. The directional verdict is **Genscaff helped, but anti-slop finding recall still needs work**.

## Same-brief Apple-principle PC café comparison

Two independent `gpt-5.6-terra` agents received the [same NOON PC brief](examples/pccafe-apple-comparison/shared-brief.md), the same generated store image, the same standalone HTML constraint, and the same Korean production-copy rule. Only the left treatment invoked Genscaff Standard. Apple was used as an aesthetic-principle reference; neither treatment copies Apple trademarks, assets, copy, or exact layout.

| Genscaff Standard | Control |
|---|---|
| <img src="docs/assets/pccafe-apple-comparison/with-genscaff.jpg" alt="NOON PC site built with Genscaff Standard" width="720"> | <img src="docs/assets/pccafe-apple-comparison/without-genscaff.jpg" alt="NOON PC control site built without Genscaff" width="720"> |

Observed differences:

- Genscaff produced a separate visual target and Standard report, a more compact three-option configuration surface, and a larger edge-to-edge image treatment.
- The control put the selected `60평` model and `132석` consequence directly in the hero, then used a longer model-list and result-panel composition.
- Both completed the model-change, required-field error, consultation summary, edit/close recovery, and desktop/mobile overflow checks. Focus styles were checked statically; a full Tab/Enter walkthrough was not claimed. Both final Lighthouse runs scored 100 in Performance, Accessibility, Best Practices, and SEO.
- The Genscaff treatment initially omitted the dialog's team-room value and logged a console error after model change. The shared verification pass found and fixed it before publication. This pair is qualitative evidence, not a claim that either workflow is universally better.

[Open the deployed comparison](https://pccafe-apple-comparison.vercel.app/) · [Genscaff Standard](https://pccafe-apple-comparison.vercel.app/with-genscaff/) · [Control](https://pccafe-apple-comparison.vercel.app/without-genscaff/)

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

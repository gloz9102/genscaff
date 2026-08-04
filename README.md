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
$genscaff strict          # v2.0 compatibility route; removed in v2.1
```

## What changed in v2.0.1

- Any user-visible asynchronous boundary must follow a wait-removal-first loading contract, preserve usable context, expose honest status and recovery, and document the observed boundary instead of treating a spinner as completion.
- Standard and Strict reports reject incomplete loading-boundary records; `async` and `generation` Strict work must declare and evidence the loading experience.

## What changed in v2.0

- Schema v5 distinguishes `IMPLEMENTED_UNVERIFIED`, `VERIFIED_RENDER`, `VERIFIED_FLOW`, and `VERIFIED_STANDARD`.
- Render, flow, keyboard, focus, automated accessibility, and assistive-technology user validation are reported separately.
- `VERIFIED_STANDARD` requires real keyboard operation and distinct desktop/mobile focus evidence; booleans alone cannot raise status.
- Product and transaction craft rejects invented selection steps and disabled CTAs as `FABRICATED_FRICTION`.
- Five focused craft modules cover commerce, dashboards, transactions, marketing, and editorial pages.
- Strict uses a compact workflow rubric instead of loading historical AI-slop and brand-research chains.
- A deterministic A/B harness prepares 8-prompt PR suites or 120-run release suites, blinds conditions, tracks swapped-judge disagreement, and merges human adjudication.
- The core skill has no Node, Playwright, or Lighthouse dependency; those remain in release-audit.

Schema v3/v4 Strict reports remain supported. A schema v4 Standard `VERIFIED_STANDARD` report is downgraded to `VERIFIED_FLOW` with `SCHEMA_V4_DOWNGRADED_TO_VERIFIED_FLOW`.

## Profiles

| Invocation | Scope | Evidence |
|---|---|---|
| `$genscaff quick` | Small copy, component, or local style change | Affected code; one viewport when needed |
| `$genscaff` | Ordinary generation or redesign | Desktop/mobile render, flow, console, overflow, keyboard and focus |
| `$genscaff-release-audit` | Trusted release-critical frontend | Four checkpoints, full controls, Lighthouse, provenance, independent review |

Genscaff does not ban gradients, glass, blur, or glow. It preserves effects required by the user, a locked reference, or the project system. It is not an authorship detector, originality certificate, or substitute for representative-user testing.

## Same-brief sample

Two independent `terra-medium` agents received the same product-page brief. Only the treatment explicitly invoked Genscaff Standard.

| Genscaff Standard | Control |
|---|---|
| <img src="docs/assets/slowdrop-comparison/genscaff-with.png" alt="Product page built with Genscaff Standard" width="720"> | <img src="docs/assets/slowdrop-comparison/genscaff-without.png" alt="Control product page built without Genscaff" width="720"> |

Both outputs were usable. This one qualitative pair does not establish superiority; see the [full comparison](docs/slowdrop-comparison.md). v2.0 treats its first scored release run as a baseline rather than a marketing claim.

## Repository layout

```text
.agents/plugins/marketplace.json
plugins/genscaff/{.codex-plugin,assets,skills/{genscaff,genscaff-release-audit}}
skill/genscaff/          # frozen v2.0 legacy source; removed in v2.1
evals/                   # cases, rubric, checked-in summaries only
tools/                   # validators, deterministic packaging, eval harness
```

## Validate

Core checks require Python 3.10+. Strict additionally requires Node.js 22.19+, Chrome/Chromium, and locked npm dependencies.

```shell
python tools/check_skill.py
python -m unittest discover -s tools -p "test_*.py"
python plugins/genscaff/skills/genscaff/scripts/test_quality_gate.py
npm ci --omit=dev --prefix plugins/genscaff/skills/genscaff-release-audit/scripts
npm audit --omit=dev --audit-level=moderate --prefix plugins/genscaff/skills/genscaff-release-audit/scripts
python plugins/genscaff/skills/genscaff-release-audit/scripts/test_quality_gate.py
python tools/package_skill.py
```

The validator never replays repository commands by default. `--execute-approved-commands` is only for an inspected repository the user explicitly trusts. Active browser audits execute page JavaScript and may make external requests.

## Evaluation harness

```shell
python tools/eval_harness.py prepare --suite pr --model gpt-5.6-terra --reasoning medium --output eval-run
python tools/eval_harness.py run --run-dir eval-run
python tools/eval_harness.py blind --run-dir eval-run
python tools/eval_harness.py score --run-dir eval-run
python tools/eval_harness.py validate --run-dir eval-run
```

Model runs use local Codex authentication, isolated Git workspaces, `codex exec --ephemeral --ignore-user-config --ignore-rules --sandbox workspace-write`, and preserved JSONL traces. Raw runs stay out of Git and belong in release artifacts; only summaries are committed.

## Compatibility packages

`python tools/package_skill.py` creates reproducible `genscaff-plugin.zip` and a one-release `genscaff-legacy.zip`, each with a SHA-256 sidecar. The legacy ZIP and `$genscaff strict` route are removed in v2.1.

## License

Project-owned source and documentation use [Apache License 2.0](LICENSE). See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [SECURITY.md](SECURITY.md).

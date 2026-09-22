<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/brand/genscaff-logo-dark.png"><source media="(prefers-color-scheme: light)" srcset="docs/assets/brand/genscaff-logo-light.png"><img src="docs/assets/brand/genscaff-logo-light.png" alt="Genscaff" width="760"></picture></p>

# Genscaff

[English](README.md) | [한국어](README.ko.md)

Genscaff is a Codex plugin for building, improving, and verifying browser frontends. Invoke it explicitly to turn requirements into responsive UI with working interactions.

## Principles

- Respect user requirements and the existing design system.
- Keep screens focused and allow whitespace. Dashboards, back offices, and explicit requests may justify greater density.
- Separate changes of topic into rendered lines or paragraphs.
- Recompose mobile content around message and action priority, preserving readable text and meaningful image crops.
- Provide hover, press, keyboard focus, and touch feedback with reduced-motion support.
- Centralize accent colors and their interaction states so they can be changed consistently.

## Install from the GitHub marketplace

```shell
codex plugin marketplace add gloz9102/genscaff --ref main
codex plugin add genscaff@genscaff-public
```

Restart Codex or open a new task. Neither skill is invoked implicitly.

## Usage

Neither skill runs implicitly. Choose the scope that matches the task.

| Invocation | Use for | Verification scope |
|---|---|---|
| `$genscaff quick` | Small copy, component, or local style changes | Affected behavior and a representative viewport when needed |
| `$genscaff` | New pages and broader redesigns with Standard | Desktop/mobile rendering, primary flow, keyboard, focus, and runtime errors |
| `$genscaff-release-audit` | Explicit release audits (Strict) | Extended browser checks, Lighthouse, and independent review |

```text
$genscaff Build a PC cafe landing page. Compare two directions and choose for me.
$genscaff quick Improve this button's hover and keyboard focus states.
$genscaff-release-audit Audit this frontend before release.
```

Standard normally compares two design directions and asks you to choose. You can request a single direction or delegate selection. The retired `$genscaff strict` invocation is replaced by `$genscaff-release-audit`.

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

Both outputs include review corrections. These are sample-specific design choices, not a required house style or proof of general superiority. The shared image was generated with imagegen; neither page submits real bookings or payments.

[Run the samples, view mobile screenshots and read the verification limits](docs/v2.2.5-pccafe-comparison.md)

## Limits

Verification reports cover observed checks, not full accessibility conformance or representative-user success. Browser-dependent checks remain unverified when the required runtime is unavailable. The PC cafe comparison is one corrected pair, not a statistical effectiveness study.

This is an independent community project, not affiliated with or endorsed by OpenAI.

## Documentation

| Document | Contents |
|---|---|
| [Workflow details](docs/workflow-details.md) | Design selection, preservation, classification, evidence, runtime and permissions |
| [Development](docs/development.md) | Repository layout, tests, evaluation harness, and distribution packages |
| [Version history](docs/version-history.md) | Version changes, internal refactoring, and historical evaluation limits |
| [Earlier Quick examples](docs/v2.2-quick-examples.md) | Dashboard and landing samples |
| [Releases](https://github.com/gloz9102/genscaff/releases) | Published versions and downloadable packages |

Project-owned source and documentation use [Apache License 2.0](LICENSE). See [third-party notices](THIRD_PARTY_NOTICES.md) and the [security policy](SECURITY.md).

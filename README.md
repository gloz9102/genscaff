# Genscaff

Genscaff is an evidence-driven Codex skill for building and reviewing browser-rendered frontend work. It combines product-specificity, action-continuity, responsive, accessibility, runtime-integrity, and anti-slop gates with validator-owned browser and Lighthouse checks.

This is an independent community project. It is not affiliated with or endorsed by OpenAI.

## What it enforces

- A product contract and pre-code visual target before implementation
- Product-specific domain signals and two-domain substitution tests
- End-to-end primary actions with feedback, terminal, and recovery states
- Complete visible-control and factual-claim inventories
- Desktop and mobile browser evidence
- Validator-owned DOM, computed-style, resource, and Lighthouse reruns
- A strict project policy prohibiting gradients, glassmorphism, glow, and decorative orbs
- Independent review provenance kept separate from machine validation

Genscaff is not an AI-authorship detector, originality certificate, or replacement for representative-user testing.

## Repository layout

```text
.
├── skill/genscaff/        # Installable Codex skill
├── tools/                 # Repository validation and packaging
├── .github/workflows/     # CI
├── LICENSE                # Apache License 2.0
├── NOTICE
└── THIRD_PARTY_NOTICES.md
```

The repository documentation stays outside the installable skill so the skill only carries execution instructions, bundled resources, and legally required notices.

## Requirements

- Python 3.10 or newer
- Node.js 22.19 or newer
- Chrome or Chromium
- npm access for the browser-audit dependencies

## Install

Back up an existing `genscaff` installation before replacing it.

### Windows PowerShell

```powershell
Copy-Item -Recurse .\skill\genscaff "$env:USERPROFILE\.codex\skills\genscaff"
npm install --omit=dev --prefix "$env:USERPROFILE\.codex\skills\genscaff\scripts"
```

### macOS or Linux

```shell
cp -R skill/genscaff "$HOME/.codex/skills/genscaff"
npm install --omit=dev --prefix "$HOME/.codex/skills/genscaff/scripts"
```

Restart Codex or open a new task, then invoke `$genscaff`.

## Validate and test

```shell
python tools/check_skill.py
npm install --omit=dev --prefix skill/genscaff/scripts
python skill/genscaff/scripts/test_quality_gate.py
```

The full regression suite starts real browser and Lighthouse processes. Set `CHROME_PATH` when Chrome cannot be discovered automatically.

## Build an installable archive

```shell
python tools/package_skill.py
```

This creates `dist/genscaff.zip` and `dist/genscaff.zip.sha256`. The archive contains a top-level `genscaff/` directory ready to copy into the Codex skills directory.

## Publish the repository

Review `NOTICE` and replace the collective copyright label with your preferred legal name or GitHub handle if desired. Then publish from the repository root:

```shell
git init
git add .
git commit -m "feat: publish genscaff skill"
git branch -M main
gh repo create genscaff --public --source=. --remote=origin --push
```

The last command creates public external state. Inspect the staged files and repository visibility before running it.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). Contributions are accepted under the same Apache-2.0 terms as the repository.

## License

Project-owned source and documentation are licensed under the [Apache License 2.0](LICENSE). Third-party components and cited external materials remain subject to their own terms; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

# Contributing

## Contribution terms

By submitting a contribution, you agree that it is licensed under Apache-2.0 and represent that you have the right to submit it. Do not paste code, documents, screenshots, brand assets, or test fixtures whose license is unknown or incompatible.

Record third-party material in `THIRD_PARTY_NOTICES.md` and retain all required upstream notices.

## Development setup

```shell
python tools/check_skill.py
python -m unittest discover -s tools -p "test_*.py"
python -m unittest discover -s plugins/genscaff/skills/genscaff/scripts -p "test_*.py"
npm ci --omit=dev --prefix plugins/genscaff/skills/genscaff-release-audit/scripts
npm audit --omit=dev --audit-level=moderate --prefix plugins/genscaff/skills/genscaff-release-audit/scripts
python plugins/genscaff/skills/genscaff-release-audit/scripts/test_quality_gate.py
```

The regression suite requires Chrome or Chromium. Set `CHROME_PATH` when automatic discovery fails.

## Pull requests

- Keep `SKILL.md`, `agents/openai.yaml`, references, and scripts consistent.
- Keep both plugin skills explicitly invoked and keep Node/browser dependencies out of the core skill.
- Add or update regression coverage for validator behavior changes.
- Keep Standard practical and Strict evidence-backed; do not weaken either profile solely to make a fixture pass.
- Remove generated caches, browser profiles, reports, and `node_modules` from commits.
- Describe behavioral changes and the commands used to verify them.
- Update `NOTICE` or `THIRD_PARTY_NOTICES.md` when attribution or dependency facts change.

## Design exploration and preservation changes

- Keep both READMEs consistent with the core workflow and mark unreleased behavior separately from versioned release notes. The frozen `skill/genscaff` tree is not the active implementation.
- Preserve existing craft rules and required information, accessible names, meaningful order, and action outcomes. DOM equality or a valid report is insufficient evidence.
- Test default two-candidate exploration, explicit single-direction requests, pending user selection, delegated selection, and comparison skips appropriate to scope. Missing browser access must remain visible as a limitation, with comparable unverified descriptions when exploration applies.
- Keep source observation, inferred principle, product fit, implementation, and rendered evidence distinguishable. Do not claim access to an unavailable reference.
- Separate the two aesthetic review passes from defect re-verification. Functional or accessibility defects do not become acceptable when the aesthetic budget is exhausted.

Before changing the skill, retain a clean baseline outside the evaluation output directory. Follow the [evaluation protocol](evals/design-preservation.md) and use `prepare --baseline-skill <previous-core-skill>` for a previous-versus-current comparison. A no-skill control answers a different question. The harness delegates selection for unattended runs; interactive selection requires a separate observed trial.

Record structural/unit-test results separately from generated-output observations. Static behavior cases are not executed tests, and one pair cannot establish superiority. Commit concise findings and limitations; keep raw runs, temporary previews, and generated packages outside the source change. Existing schema v6 fields carry preservation and exploration evidence; this workflow does not introduce a new report schema or status.

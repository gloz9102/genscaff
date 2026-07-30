# Contributing

## Contribution terms

By submitting a contribution, you agree that it is licensed under Apache-2.0 and represent that you have the right to submit it. Do not paste code, documents, screenshots, brand assets, or test fixtures whose license is unknown or incompatible.

Record third-party material in `THIRD_PARTY_NOTICES.md` and retain all required upstream notices.

## Development setup

```shell
npm install --omit=dev --prefix skill/genscaff/scripts
python tools/check_skill.py
python skill/genscaff/scripts/test_quality_gate.py
```

The regression suite requires Chrome or Chromium. Set `CHROME_PATH` when automatic discovery fails.

## Pull requests

- Keep `SKILL.md`, `agents/openai.yaml`, references, and scripts consistent.
- Add or update regression coverage for validator behavior changes.
- Do not weaken a hard gate solely to make a fixture pass.
- Remove generated caches, browser profiles, reports, and `node_modules` from commits.
- Describe behavioral changes and the commands used to verify them.
- Update `NOTICE` or `THIRD_PARTY_NOTICES.md` when attribution or dependency facts change.

---
name: genscaff-release-audit
description: "Explicitly invoked Strict release audit for trusted browser frontends, including live control inventory, four-checkpoint desktop/mobile evidence, Lighthouse diagnostics, provenance checks, and schema v3-v5 report validation."
---

# Genscaff Release Audit

Run only when the user explicitly invokes `$genscaff-release-audit`, or through the deprecated v2.0 `$genscaff strict` compatibility route. This is a release audit, not a default design workflow.

## Preconditions

- Preserve explicit user requirements and the existing project design system.
- Explain the runtime and review cost before beginning.
- Treat package scripts and repository-local executables as arbitrary code.
- Require explicit repository trust and exact command approval before replaying commands.
- Require approval before active browser audit; page JavaScript and external requests may execute.
- Inspect the bundled manifest for exact runtime requirements. Missing Strict-only runtime or a fresh reviewer makes Strict incomplete; it does not block safe source work or a separately reported Standard ceiling.

## Audit

Read `references/aggressive-hard-gate.md`, `references/quality-report-schema.md`, `references/visual-comparison-protocol.md`, and `references/workflow-rubric.md`. If the audited flow reads or writes remote data, streams, lazy-loads media, waits on navigation, or starts a background job, also read and enforce `references/loading-ux.md`. Load other references only for a concrete question. Do not transitively load historical AI-slop or brand-research documents.

1. Establish the product contract and inspect source/runtime scope.
2. Exercise `primary-start → primary-feedback → primary-terminal → primary-recovery` at desktop and mobile.
3. Test every visible control and reconcile runtime inventory with the report.
4. For every asynchronous boundary, verify the loading contract record, wait-avoidance decision, continuity or progressive result, freshness cue, failure recovery, and relevant user control. A spinner, skeleton, boolean claim, or static source inspection alone is insufficient.
5. Verify console, overflow, keyboard, visible/unobscured focus, content integrity, and applicable accessibility automation.
6. Run Lighthouse as a laboratory diagnostic, not proof of user experience or accessibility.
7. Run two visual rubric passes and a fresh blind reviewer. Keep reviewer provenance distinct from machine validation.
8. Record exact argv. Replay approved commands only with `--execute-approved-commands`.

```bash
npm ci --omit=dev --prefix <skill-dir>/scripts
python <skill-dir>/scripts/quality_gate.py --init <report.json> --profile strict
python <skill-dir>/scripts/quality_gate.py --report <report.json> --allow-active-browser-audit
python <skill-dir>/scripts/quality_gate.py --report <report.json> --allow-active-browser-audit --execute-approved-commands
```

Schema v3 and v4 Strict reports remain supported. Finish only when the validator passes and reviewer provenance is valid. Missing browser runtime blocks browser evidence; missing Lighthouse blocks only its audit. Report commands, evidence, skipped checks, limitations, and any `COMMAND_EXECUTION_SKIPPED_UNTRUSTED` result.

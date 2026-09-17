# Instruction consolidation and Strict refactor — September 17, 2026

Historical checkpoint: the later [v2.1 transition record](v2.1-transition.md) supersedes the deferral and runtime status below. Original failures and evidence are retained here unchanged.

This working-tree change keeps package version 2.0.1. The v2.1 version change, legacy package removal, and retirement of `$genscaff strict` are deferred until behavioral evaluation can be completed. Structural changes may proceed independently under the revised implementation scope.

## Changes and preserved requirements

Core SKILL.md decreases from 208 to 103 lines by assigning detailed contract/inspection, classification, exploration, anti-slop review, verification, and schema guidance to their existing references. Product decisions are recorded once and reused by reviews and completion reports. The Korean production-copy rule remains mandatory. The complete `ui-craft-guidelines.md` file, its enforcement level, and its open-visual-direction routing condition are unchanged. Line counts are not token-cost or behavior measurements.

Strict now separates report validation, bounded files, source inspection, browser execution, images, manifests, provenance, and approved commands into internal `scripts/auditlib` modules. Existing Python entrypoints and their explicit exports, CLI options, schema support, error ordering, JS runners, dependency declarations, and execution boundaries are retained. This extracts existing rules; it does not remove validators or claim a reduction in total source lines. The frozen legacy package remains untouched.

## Behavioral evaluation: blocked, not passed

The planned evaluation uses the frozen previous Core against the candidate Core, both on `gpt-5.6-terra` with `medium` reasoning. The PR suite has eight pairs (16 runs). A separate six-pair suite covers interactive selection with a fixed follow-up, single direction, unavailable browser, CSS-hidden information, defect re-verification after aesthetic passes, and a narrow existing-system change. The 120-run release evaluation was not run.

The initial CLI attempt reported a read-only environment despite the workspace-write argument. Native Windows sandbox diagnostics then exposed an elevated process-launch failure. Scoped trust of generated workspaces with the documented unelevated fallback allowed a shell write/read probe, but `apply_patch` still failed, including a separate relative-path-only probe. A recovered PR pair completed at the process level: the control created source via shell while the treatment stopped after patch failure. That pair is not valid evidence of skill effectiveness. Other started PR and behavior runs were interrupted once the tooling problem was reproduced. Two recovered PR result files exist, no behavior case completed, and zero pairs were scored.

No unrestricted sandbox bypass, global trust change, replacement model, fabricated browser observation, or human adjudication was used. CLI exit code zero does not imply task acceptance. No behavior case is passed from its static definition or from repository tests.

## Structural evidence and artifact retrieval

Baseline and modularized Strict both passed 87 regression tests. A differential run also passed all 87 tests, comparing 71 ordered error lists against the frozen implementation using identical report/evidence fixtures. Installation paths were normalized to the current root because unchanged JS runners are installed there. AST comparison preserved all 93 original function/class bodies except the four bundled-JS path expressions adjusted for module relocation. Extracted-ZIP CLI tests verify both report initialization and safe rejection without browser approval.

The final structural checks passed 23 tool tests, 18 Core tests, three Node syntax checks, and dependency audit with zero vulnerabilities. Legacy source, JS runners, dependency manifests, and both UI craft files remain unchanged.

The machine-readable [summary](instruction-refactor-2026-09-17.json) records snapshot hashes, structural results, and the blocked evaluation. Raw records remain outside Git in artifact bundle `20260917-v21`, under the sibling `genscaff-evaluation` directory of the checkout. This local bundle is not a published release artifact.

The bundle contains the before-state Git head/status/diff, per-file baseline hashes, immutable Core/Audit snapshots, routing decisions, PR manifests/prompts/traces, behavioral fixtures/prompts and interrupted traces, sandbox diagnostic probes, test logs, Strict extraction/differential results, and generated packages. Preserve incomplete runs when retrying; prepare a fresh run directory with the same baseline instead of using `--rerun` to overwrite them.

The harness now accepts explicit `--windows-sandbox elevated|unelevated` and `--jobs 1|2|4` on `run` (default concurrency remains one). It trusts only its generated workspace for that child process, keeps workspace-write isolation and approval policy never, discards inherited stdin, records execution policy, and rejects policy changes when resuming a run directory. Neither option repairs the remaining patch-tool failure. Use a file-edit preflight before a new evaluation; keep the runtime settings identical across arms.

After runtime recovery, run all 16 PR trials and the 12 behavioral trials in fresh workspaces, inspect actual output and matching rendered evidence, complete existing blind/swapped judgments and required human adjudication, and only then reconsider v2.1 migration. Structural success does not establish better design, behavior, or token efficiency.

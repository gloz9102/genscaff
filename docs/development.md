# Development and validation

[English](development.md) | [한국어](development.ko.md) | [README](../README.md)

Run the commands below from the repository root. This guide covers contributor checks, evaluation, and packaging.

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

Use `prepare --baseline-skill <previous-core-skill>` to compare the current skill against a frozen previous skill. Both arms then explicitly invoke Genscaff with equal prompts; omitting the option preserves the no-skill control. The non-interactive harness delegates design selection in both arms. See [design preservation evaluation](../evals/design-preservation.md) for interactive choice cases, raw fixture requirements, quality/cost criteria, and the boundary between static cases and executed trials.

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

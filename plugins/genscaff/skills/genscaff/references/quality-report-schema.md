# Standard Report Schema v6

Use JSON only when requested or needed by the validator. Quick does not require it; Strict belongs to `$genscaff-release-audit`.

Always initialize a new Standard report with the current validator and validate the finished file. Do not hand-author an older schema or copy a historical report shape.

```bash
python <skill-dir>/scripts/quality_gate.py --init <report.json> --profile standard
python <skill-dir>/scripts/quality_gate.py --report <report.json>
```

Schema v6 records classification, a product/design contract, separated verification dimensions, in-root evidence, runtime checks, relevant-state coverage, interaction cost, loading experience, and distinct execution permissions.

Record first-render and anti-slop findings in the existing structure rather than adding a boolean checklist. Put the concrete finding, rendered location, evidence, and `keep`, `replace`, `remove`, or project-evidenced `exception` response in the relevant verification dimension's `issues`; put unresolved scope or uncertainty in `limitations`. `notes` may summarize the review. A visual finding that remains cannot coexist with an unsupported clean claim such as `no_nested_card_soup: true`.

Each verification dimension contains:

```json
{
  "result": "pass | fail | partial | pass_with_limitations | not_run | blocked",
  "method": "observed | manual | automated | static | none",
  "coverage": "what was checked",
  "evidence": [],
  "issues": [],
  "limitations": []
}
```

The canonical statuses are `IMPLEMENTED_UNVERIFIED`, `VERIFIED_RENDER`, `VERIFIED_PRIMARY_FLOW`, `VERIFIED_KEYBOARD_FLOW`, and `VERIFIED_STANDARD_BASELINE`. The main Skill routes verification work to the separate baseline reference; this schema document does not require another reference to be loaded.

Schema v5 remains readable. Its mixed method/result values are converted conservatively. Legacy `VERIFIED_FLOW` maps at most to `VERIFIED_PRIMARY_FLOW`; `VERIFIED_STANDARD` maps at most to `VERIFIED_KEYBOARD_FLOW`. Missing classification is recorded as a migration limitation. New reports never emit legacy statuses.

Artifacts must be relative to the report directory, remain inside it after symlink resolution, exist, be readable PNG files, and be distinct where the status requires distinct states. A boolean, status string, or `pass` without matching evidence cannot raise completion.

`GENSCAFF_STANDARD_REPORT_VALID` means only that the declared Standard structure and local evidence passed these checks. It is not a Strict audit or proof of authorship, originality, legal clearance, complete accessibility, or representative-user success.

# Standard Report Schema v5

Use this reference only when a Standard JSON report is useful. Quick does not require JSON. Strict belongs to `$genscaff-release-audit`.

Initialize and validate with the core Python-only validator:

```bash
python <skill-dir>/scripts/quality_gate.py --init <report.json> --profile standard
python <skill-dir>/scripts/quality_gate.py --report <report.json>
```

## Completion status

- `IMPLEMENTED_UNVERIFIED`: implementation exists but browser evidence does not.
- `VERIFIED_RENDER`: desktop/mobile render, console, and horizontal overflow were observed.
- `VERIFIED_FLOW`: Render plus primary action, terminal result, and recovery were observed.
- `VERIFIED_STANDARD`: Flow plus actual Tab and Enter or Space operation and visible, unobscured focus were observed at desktop/mobile.

`VERIFIED_RENDER` needs distinct desktop/mobile `start` PNGs. `VERIFIED_FLOW` adds distinct `terminal` PNGs. `VERIFIED_STANDARD` adds distinct `focus` PNGs. Every artifact needs a concrete observation. A boolean without matching evidence cannot raise status.

## Verification dimensions

Record each of these independently as `observed`, `static_only`, `automated`, or `not_tested`:

- `render`
- `flow`
- `keyboard`
- `focus`
- `automated_accessibility`
- `assistive_technology_user_validation`

Automation is not assistive-technology user validation. Source inspection is not observed keyboard or focus behavior.

## Interaction cost

Record non-negative `required_decisions` and `actions_to_primary_success`, a string `default_selection_rationale`, and an empty `fabricated_friction` list. Any unsupported extra step is `FABRICATED_FRICTION` and fails validation.

## Runtime checks

For desktop and mobile, record `inner_width`, `scroll_width`, console errors/warnings, primary action, recovery, keyboard path, visible focus, and unobscured focus. Required booleans depend on completion status. `scroll_width` must equal `inner_width` for a verified render.

Successful output is `GENSCAFF_STANDARD_REPORT_VALID`. `IMPLEMENTED_UNVERIFIED` also emits `STANDARD_BROWSER_EVIDENCE_UNVERIFIED`. Neither token represents a Strict live audit, authorship, originality, universal accessibility, or representative-user success.

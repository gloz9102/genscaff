# Quality Report Schema

Schema v5 supports Standard and Strict profiles. Initialize one with:

```bash
python <skill-dir>/scripts/quality_gate.py --init <report.json> --profile standard
python <skill-dir>/scripts/quality_gate.py --init <report.json> --profile strict
```

Standard reports declare one completion status:

- `IMPLEMENTED_UNVERIFIED`: the implementation and compact product contract are recorded, but no browser evidence was collected. Validation may pass, but the CLI prints `STANDARD_BROWSER_EVIDENCE_UNVERIFIED`; do not describe this as Standard-verified.
- `VERIFIED_RENDER`: requires distinct desktop/mobile start screenshots, zero browser console errors and warnings, and no horizontal overflow.
- `VERIFIED_FLOW`: adds distinct terminal screenshots plus a verified primary action and recovery in both viewports.
- `VERIFIED_STANDARD`: adds actual keyboard activation, visible and unobscured focus, and distinct focus screenshots in both viewports.

Record `verification_dimensions` separately for render, flow, keyboard, focus, automated accessibility, and assistive-technology testing. Values are `observed`, `static_only`, `automated`, or `not_tested`; source inspection never counts as observed keyboard or focus behavior. Record `interaction_cost.required_decisions`, `actions_to_primary_success`, `default_selection_rationale`, and an empty `fabricated_friction` list. Any fabricated friction fails validation.

For `VERIFIED_STANDARD`, `runtime_checks.desktop` and `runtime_checks.mobile` also require `keyboard_path_verified`, `focus_visible_verified`, and `focus_not_obscured_verified`. All required screenshots must exist locally and be pixel-distinct.

Strict retains the complete evidence catalog and manifest contracts below. Existing schema v3 reports remain supported as `legacy-strict`. Schema-v4 Strict reports remain supported. A schema-v4 Standard report claiming `VERIFIED_STANDARD` is accepted only as `VERIFIED_FLOW` and emits `SCHEMA_V4_DOWNGRADED_TO_VERIFIED_FLOW`.

Every schema v5 report records:

- `profile`: `standard` or `strict`
- `completion_status`: required for new Standard reports
- `visual_policy`: detected effects and user/project/locked-reference exceptions
- `execution_policy`: exact command approval and active-browser approval

Do not treat an approval field as proof of trust. The operator must still pass `--execute-approved-commands` before repository code can run and `--allow-active-browser-audit` before Strict browser or Lighthouse execution can start.

Initialize a Strict report immediately after the product contract and keep it current during the work. Run the validator while sections are still incomplete to expose missing artifacts and cross-field mismatches early. Leaving a Strict report until the end turns verification into clerical rework and commonly produces no verdict at all.

## Evidence Object

Material claims use this shape:

```json
{
  "artifact": "C:/absolute/path/to/screenshot.png",
  "region": "Model comparison table, context-window row",
  "observation": "The selected models expose different context limits and the changed cells remain aligned."
}
```

Rules:

- `artifact` must be a real local file. Placeholder paths and remote assertions do not pass.
- Screenshot evidence must use a supported image type and contain data.
- `region` must identify an exact surface, state, or checkpoint.
- `observation` must state what was observed with product-specific nouns.
- `checked`, `looks good`, `works`, `pass`, or `as expected` are not evidence.

## Evidence Catalog

Store reusable evidence once in the top-level `evidence_catalog`:

```json
{
  "evidence_catalog": {
    "desktop-comparison-result": {
      "artifact": "C:/absolute/path/to/desktop-result.png",
      "region": "Model comparison result and saved shortlist",
      "observation": "The selected model enters the shortlist with retained workload constraints and a remove action."
    }
  }
}
```

Any `evidence` field may contain the full object or the catalog ID string:

```json
{
  "evidence": ["desktop-comparison-result"]
}
```

Reuse an ID only when the same artifact, region, and observation genuinely demonstrate the claim. Create another catalog entry when the region or observation changes. An unknown ID, invalid catalog object, placeholder text, or missing artifact fails validation.

## Required Sections

### `context`

- `work_type`: `new`, `polish`, or `review`.
- `scope`: `component`, `screen`, `flow`, `site`, or `design-board`.
- `product_name`, `product_type`, `target_user`, `user_need`, `primary_task`, `success_outcome`, and `primary_cta`.
- `constraints`: explicit or repository-derived constraints.
- `differentiators`: at least two non-cosmetic product differences.
- `domain_objects`: real objects, data, media, records, entities, or work items used by the product.
- `task_traits`: relevant behavior traits such as `async`, `form`, `collection`, `generation`, or `transaction`. Traits make their loading, error, empty, disabled, or success states mandatory instead of conveniently not applicable.
- `assumptions`: unresolved assumptions, each labeled instead of presented as research.

### `implementation_audit`

- `project_root`: the actual frontend project directory. The validator recursively scans it so a report cannot hide a violating file by omitting it from a hand-written source list.
- `source_roots`: every authored frontend source root or explicit source file. Generated/vendor exclusions apply only to this authored-source scan.
- `rendered_roots`: every directory or file that can actually be served, previewed, deployed, or loaded by the audited page, including `dist`, `build`, `out`, exported HTML, bundle CSS/JS/SVG, public assets, and generated data URIs. Generated/vendor exclusions must not suppress scanning inside these roots.
- `source_fingerprint`: generate it with `quality_gate.py --fingerprint`; it must match source bytes and every downstream manifest.
- `live_audit_config`: local configuration used by the validator to start a fresh desktop/mobile browser run. A file target must be the canonical project `index.html`/`index.htm` and the direct index of a declared `rendered_root`. A top-level project index takes precedence over every deeper index; without one, exactly one shallowest index must exist. The captured start URL and top frame must still be that canonical file, so meta or script redirects cannot hand the audit to a nested decoy. An HTTP(S) target must request the origin root without credentials, query, or fragment; real 3xx responses retain status, location, and empty-body evidence without being misclassified as unreadable resources. It identifies viewports, primary trigger, feedback/terminal/recovery observations, product-signal selectors, decision selectors, and one fresh-context `control_scenarios` entry for every other visible non-disabled control. Each scenario declares `click`, `fill`, `select`, `check`, or `press`, an optional `default`, `primary-feedback`, or `primary-terminal` setup, and an expected selector, URL, value, or checked-state transition. A selector or URL that already matched before the action is not causal evidence. After the expected state, the runner enforces a minimum observation window, network idle, complete response-promise draining, and no action-created timer, interval, or animation task left pending. Semantically disabled controls are excluded only when both the report and live DOM agree they are disabled.
- `capture_manifest`: schema-v1 JSON listing every report PNG with SHA-256, decoded dimensions, viewport, route, state, checkpoint, and capture time.
- `runtime_style_manifests`: distinct desktop and mobile JSON produced from `runtime_probe.js`; all gradient, backdrop, glass, blur/glow, SVG, and raster finding lists must be empty. These are cross-check inputs, not substitutes for the validator-owned run.
- `control_manifests`: distinct desktop and mobile JSON containing every visible control and observed behavior. They must match both `action_trace.control_inventory` and the controls rediscovered and activated by the validator.
- `content_manifest`: local JSON inventory of factual data, metrics, customers, testimonials, certifications, integrations, and performance claims. Every claim needs provenance and capture evidence; `unverified_claims` must be empty, and the inventory must cover every visible claim candidate rediscovered by the validator.

The validator must own the live browser process. On every final validation it opens the implementation in a new browser context and independently collects actual DOM and visible-text hashes, computed styles including pseudo-elements, SVG/canvas activity, visible controls, control activation results, visible claims, screenshots, console/page/network failures, and loaded first-party and external resource hashes. Every loaded body is decoded and rescanned instead of trusting its declared MIME. PNG, JPEG, GIF, WebP, AVIF, BMP, and SVG are identified from magic bytes or payload structure, so an extensionless `application/octet-stream` response cannot hide a raster. Textual external CSS, JS, and SVG receive the same prohibited-pattern and data-URI scan; mutable or uninspectable external raster resources fail and must be localized for review. It cross-checks those observations against the report and manifests. A hand-authored live-result JSON is not accepted as execution proof.

Configured product and decision selectors must be unique, mutually distinct, and visually substantive, not merely present in the DOM. `html`, `body`, `main`, `#app`, `#root`, and similarly broad application containers are not valid evidence nodes. The live bundle records the resolved DOM identity, viewport intersection, ancestor-adjusted opacity, content-visibility state, `aria-hidden`, rendered text rectangles and pixel area, text alpha, and sampled occlusion. Different selectors resolving to the same node fail. Off-screen, transparent, actually clipped, minuscule, or covered evidence fails even if its hidden text contains the expected product vocabulary; a declared but non-clipping shape such as `clip-path: inset(0)` is not failed solely for using the property.

### `visual_target`

- Confirm the target and expanded brief were created before coding.
- Save the target as a real local Markdown, text, or JSON artifact. Record a timezone-aware creation time and baseline context; the artifact must predate the first visual-iteration screenshot.
- Record a concise brief and target summary.
- For new work, record at least two materially different direction options with product fit and tradeoff. Polishing or review work may use one system-constrained direction.
- Record the selected direction and a product-fit rationale.
- Map at least one benchmark principle to the implementation, explain same-domain or same-interaction-model relevance, and state what must not be copied.
- Record at least three concrete slop or craft risks.
- Record token strategy and the primary CTA.

### `requirement_trace`

Include unique entries for `primary-task` and `primary-cta`, then every explicit constraint or product promise. Each entry needs:

- `id`, `requirement`, `source`, `implementation`, `status`.
- One or more evidence objects.
- `source` must be `user`, `repository`, `external-research`, or `derived`.
- `status` must be `verified` for PASS.

### `product_specificity`

- `domain_signals`: product-specific element, domain detail, enabled decision, and evidence.
- `decision_points`: decision, required inputs, consequence, and evidence.
- `substitution_test`: two mutually distant product comparisons. Each must set `still_fits` to `false`, `far_from_target` to `true`, explain semantic distance, and list non-cosmetic breaking signals.
- Every comparison must contain exactly five `axes`: `information_architecture`, `data_schema`, `state_transitions`, `action_sequence`, and `failure_recovery`. Each axis records `breaks` and a concrete reason; at least four must break per alternate.
- `verdict`: `product-specific` with a concrete rationale.
- `generic_elements_found`: must be empty after iteration.

### `action_trace`

- `interaction_mode`: `functional` or `prototype`.
- `primary`: CTA label, location, start state, information scent, action steps, terminal state, recovery path, and `verified: true`.
- `primary.checkpoints`: distinct `start`, `feedback`, `terminal`, and `recovery` screenshot evidence, captured in that order and registered as matching capture-manifest checkpoints.
- Every step needs the user action, observed feedback, result, and evidence.
- CTA label must match `context.primary_cta` and must not be a context-free generic label.
- `dead_end_controls`: must be empty.
- `control_inventory`: list visible controls in the primary viewport and task. Record label, role, location, functional/disabled/prototype behavior, result or prerequisite, and evidence. Exactly one control is primary and it must match `context.primary_cta`.
- Prototype mode requires visible prototype disclosure and is not a waiver for misleading controls.

### `state_coverage`

Record `loading`, `empty`, `error`, `disabled`, `success`, and `long-content` exactly once:

- Use `implemented` with screenshot evidence, or `not-applicable` with a concrete rationale.
- `success` and `long-content` must always be implemented and evidenced.
- Use a deterministic, visibly test-only fixture for a hard-to-reach state when necessary. The fixture must exercise the real layout and interaction code and must not masquerade as production data or a shipped capability.
- State evidence must identify the affected surface and observed behavior.

### `loading_experience`

Use `applicable: true` whenever `context.task_traits` includes `async` or `generation`, or the changed flow otherwise reads or writes remote data, streams results, lazy-loads media, waits on navigation, or starts a background job. Do not classify these paths as not applicable merely because the delay is short.

Record one boundary for each user-visible asynchronous transition. Every boundary requires non-empty `trigger`, `affected_surface`, `wait_avoidance`, `stale_data_policy`, `failure_recovery`, `user_control`, and `evidence` strings. Apply `loading-ux.md` in priority order. A spinner, skeleton, fabricated percentage, boolean claim, or static source inspection alone does not satisfy this section.

### `task_walkthroughs`

Record at least one desktop and one mobile primary-task walkthrough. Each needs:

- Start state, ordered steps, terminal state, result, recovery tested, and evidence.
- A viewport-specific four-checkpoint object for start, feedback, terminal, and recovery. Desktop and mobile evidence cannot be reused across viewports.
- `result` must be `pass`.
- Forms, transactions, destructive actions, and generated results must include a failure or correction path.

### `visual_review`

- Desktop and mobile checks, brand comparison, AI-slop comparison, and UI-craft comparison must be true.
- Desktop and mobile screenshots must be different real local files.
- Record zero console errors and zero open layout issues.
- `iteration_log` must contain at least two strictly chronological passes with decoded-pixel-distinct evidence. Give each finding a unique `id`; each change lists the finding IDs it `resolves`.
- `open_findings` must be empty.
- `independent_review` must point to a separate raw JSON `review_artifact`. For screen, flow, site, and design-board work it must come from a fresh subagent using a blind prompt and distinct reviewer/implementer IDs. The raw artifact records source fingerprint, capture hashes, identity probe, action probe, anti-slop probe, findings, and completion time.
- The validator may verify the artifact's schema, hashes, contents, and cross-field consistency, but it cannot prove who authored a local JSON file. After machine validation, the root agent must separately inspect the actual collaboration mailbox and match the reviewer task ID, distinct agent identity, blind request, supplied capture hashes, raw response, and completed status. Until then the review provenance is `REVIEW_PROVENANCE_UNVERIFIED` regardless of the artifact fields.

### `measurements`

- `lighthouse.report` must point to a real local Lighthouse JSON file produced by `scripts/lighthouse_audit.js`, including its runner/config hashes, at least 100 audits, canonical audit IDs, timing, auditRefs, and warnings.
- Reported scores must be finite integers in `0..100`, meet thresholds, and match the parsed artifact. The validator reruns Lighthouse from `live_audit_config`; the fresh result must independently meet every threshold and remain within the bounded score-drift tolerance.
- `commands` must contain command, `pass` result, and a concrete output summary.
- `execution_manifest` must point to a local JSON containing the exact commands, cwd, start/end timestamps, exit codes, log paths, log SHA-256 values, and current source fingerprint. It must match `commands` exactly. The validator safely parses and re-executes allowlisted repository commands in a cwd inside `project_root`; stored exit codes alone do not satisfy the gate.
- `lighthouse_is_technical_floor` must be true.

### `judgment`

- The report's `verdict` may be `pass` only as a bounded author judgment over the defined evidence. It is not the validator result and not proof of authorship, originality, non-slop status, or user success.
- Score product specificity, action continuity, visual coherence, and content integrity from 1 to 5; each must be at least 4.
- Provide a reasoned rationale grounded in evidence.
- `residual_risks` must be empty for the report's bounded implementation verdict. Inherent method limits—no authorship detector, no originality proof, no representative-user validation, and no machine proof of review provenance—still must be disclosed in the final response and are not erased by an empty array.

### `checks`

All generated checks remain mandatory but are supporting assertions, not a verdict and not evidence. Product traceability, source scan, browser manifests, substitution failure, action continuity, control honesty, evidence integrity, independent review, and Lighthouse/command provenance are independently required. A `true` value never compensates for a failed hard gate.

## Artifact Integrity

The validator verifies:

- Files exist and are non-empty.
- Browser evidence is PNG with valid chunks, CRC, IDAT decode, dimensions, and non-trivial visual structure.
- Every report PNG appears in the capture manifest, matches its file hash and dimensions, and has a current source fingerprint.
- Mutually exclusive viewport/state/checkpoint claims cannot reuse decoded pixels.
- Every declared `rendered_root` exists and is scanned without generated-output exclusions; loaded first-party and external resources, decoded bodies, magic-byte types, and encoded data URIs agree with rendered-root and source evidence.
- A validator-owned fresh browser run reproduces the desktop/mobile default route, primary start-feedback-terminal-recovery chain, actual control inventory and behavior, visible claim inventory, computed-style restrictions, and console/page/network state.
- The visual-target artifact predates the first review screenshot.
- Desktop and mobile screenshots are not the same file or identical bytes.
- Lighthouse category scores match a full saved JSON containing version, fetch time, URL, user agent, environment, config, audits, auditRefs, and warnings.
- Source, rendered outputs, live-browser run, runtime-style, control, independent-review, and command manifests agree on source fingerprint and chronology.
- Numbers are finite and inside valid ranges.
- Placeholder or trivial evidence is rejected.
- Minimum counts, enumerated values, unique IDs, and cross-field invariants hold.

## Incremental Run Order

1. Initialize the report and fill `context` plus the verification command preflight.
2. Add the visual-target artifact and run `python <skill-dir>/scripts/quality_gate.py --report <report.json> --max-errors 30`; expected failures become the next work list while `ERROR_COUNT` preserves the total.
3. Add catalog evidence while capturing states and walkthroughs. Re-run after the first desktop/mobile task pass.
4. Add source fingerprint, every rendered root, live-audit config, capture manifest, desktop/mobile runtime-style and control manifests, both iteration passes, and independent review. Re-run before Lighthouse.
5. Add the full Lighthouse JSON and command execution manifest, clear every open finding, and run the final verdict.

Do not duplicate screenshots merely to satisfy different sections. Reuse catalog IDs when they support the exact same observation; capture new evidence when behavior, viewport, state, or reviewed region differs.

Successful machine output is `STRUCTURAL_EVIDENCE_INVARIANTS_VERIFIED`, meaning only that the declared local artifacts and a validator-owned live browser rerun reproduced the defined structural invariants. It does not establish independent-review provenance. The root agent must separately report either `REVIEW_PROVENANCE_VERIFIED_BY_ROOT_AGENT` after checking the actual collaboration mailbox or `REVIEW_PROVENANCE_UNVERIFIED` when it cannot.

Neither status, alone or together, proves AI non-use, human authorship, universal originality, absence of every form of slop, representative-user success, production safety, or a certified quality level. Final wording must name the checks actually performed instead of collapsing them into an unqualified `PASS`.

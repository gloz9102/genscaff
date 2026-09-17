# Design Exploration and Preservation Evaluation

Evaluate the changed skill against a frozen previous skill, not only against no skill. Do not infer behavioral improvement from schema checks or unit tests. Existing spacing, background, radius, typography, and other craft rules remain unchanged in both arms.

## Prepare and run

Before editing, retain a clean copy of the previous core skill outside the run directory. Prepare a comparison with:

```shell
python tools/eval_harness.py prepare --suite pr --model <same-model> --reasoning <same-effort> --baseline-skill <previous-core-skill> --output <empty-run-directory>
```

The control receives the frozen previous skill; the treatment receives the current skill. Both explicitly invoke Genscaff with the same prompt. Omitting `--baseline-skill` retains the original no-skill control. Snapshots are hashed and checked before model execution and validation. `prepare` performs no model run.

Use the existing run, blind, score, and validate commands only when model execution is authorized. PR remains eight paired tasks; release remains twenty tasks with three replicates per pair. No result from either arm may be exposed to the other. Match model, reasoning, raw inputs, starting files, assets, viewport sizes, permissions, execution limits, and evaluation criteria. Treat mismatched or contaminated pairs as invalid.

The non-interactive harness explicitly delegates direction selection to both arms so it can finish without a fabricated user reply. It therefore does not test the interactive selection boundary. Test that separately with the behavior cases, using an actual user response or a fixed evaluator-supplied follow-up after the candidate presentation. Static `behavior_only` definitions are expectations, not executed or scored trials; the harness currently excludes them from run counts.

## Representative coverage

Use these six scenarios for a focused manual forward evaluation, in isolated workspaces with identical raw fixtures per pair:

| Scenario | Required raw fixture | Acceptance evidence |
| --- | --- | --- |
| Open product introduction | Supplied product facts, required CTA, shared licensed assets | Comparable desktop/mobile A/B, information hierarchy, causal CTA, no invented proof |
| Long editorial content | Exact article, citations, footnotes, wide table | No omitted facts, readable order, long-content reflow, accessible navigation |
| Dense operations screen | Fixed records, saved filters, row action and failure fixture | Preserved records/units, scanning, retained filters, action and recovery |
| Marketplace discovery | Fixed inventory, prices, availability and search inputs | Same options in candidates, working filters, comparison and unavailable states |
| Transaction | Fixed fields, validation rules and local simulated result | Same labels, input preservation, keyboard path, duplicate-submit handling and terminal result |
| Narrow established-system change | Existing working component and tokens, exact requested change | No unnecessary candidate generation, no craft-rule changes or architecture expansion |

Also exercise user-requested single direction, pending selection, delegated selection, CSS replacement of required text, source-unavailable reference claims, missing browser evidence, and a functional defect discovered after two aesthetic passes. These cases are defined in `cases.json` and require observed outcomes when run.

## Judge behavior before preference

- Hard requirements: preserve requested information, values, accessible names, meaningful order, action outcomes, project constraints, and the user's design-choice boundary. Fail relevant behavior even if the other candidate looks preferable.
- Reference quality: source observation -> inferred principle -> product fit -> implementation -> actual rendered evidence. Do not reward a count of differences without an implemented rationale.
- Visual comparison: evaluate information hierarchy, readability, product fit, substantive composition differences, and mobile behavior. Candidate novelty cannot excuse violation of craft rules.
- Verification: separate candidate previews from selected-product checks. A preserved DOM, clean JSON report, or screenshot hash is not semantic or aesthetic proof.
- Cost: use elapsed seconds in run results and available token/tool usage in raw traces; record unavailable metrics as unavailable. Track changed files, unnecessary candidates, user questions, dependencies, and rework separately. Lower cost does not offset a hard failure.

For `comparison_fairness`, score an explicitly requested single-direction or inapplicable comparison by correct scope handling, not by the presence of two candidates. For `reference_traceability`, assess brief/repository grounding when there is no external reference. Never force alternatives or external sources merely to earn these scores. `design_choice_respected` includes single-direction choice, pending user selection, and explicit delegation. `information_behavior_preserved` checks the supplied requirements or before-state baseline in the actual artifacts.

Blind the version identity and randomize presentation order. Keep original and swapped judgments; use the existing human adjudication boundary. Compare within matched tasks and report win/tie/loss, hard failures, repeated failure modes, and available paired cost deltas. A quick pair is directional, and a few repeats are not statistical proof.

Adopt the change only when required behavior does not regress, open-direction tasks improve in the judged outcomes, and narrow tasks avoid new process overhead. Do not mark behavior cases passed from their presence in JSON or claim the unit-test suite demonstrated better design.

## Quick forward check — September 17, 2026

Two isolated `gpt-5.6-luna` low-effort agents received the same standalone Korean library-room booking brief, fixed rooms/prices/capacities/availability, and no external assets or frameworks. One used the updated skill snapshot; the other used no skill. This was a manual quick check, not the harness's frozen-baseline comparison or a scored PR suite. Selection was explicitly delegated, and generation agents had no browser access. The parent subsequently checked both outputs at 1440×900 and 390×844.

| Observed check | Updated skill | No-skill control |
| --- | --- | --- |
| Desktop/mobile rendering and horizontal overflow | Rendered; no horizontal overflow observed | Rendered; no horizontal overflow observed |
| Checked keyboard submission/edit paths and visible focus | Exercised | Exercised |
| Console in checked flows | No errors captured | No errors captured |
| Unavailable studio slot | Disabled | Rejected on submission |
| Capacity consistency after room change | Excess capacity rejected | Changing from eight-person meeting room to four-person study room changed input to four while summary retained eight; completion showed four |
| Post-submission edit | Explicit edit restored editable fields, retained values, and focused name | Editing the name left a stale success message visible |
| Required exploration and existing craft rules | No two-candidate artifacts or descriptions; background, 27px spacing, and repeated corner radii violated existing rules | Not a skill-adherence condition |

This pair showed useful functional differences but did not establish overall superiority or improvement over the previous skill. The treatment failed parts of the intended workflow. The run did not test actual user-selection waiting, rendered candidate comparison, full accessibility conformance, screen-reader behavior, or every state at both viewports. Comparable token/cost measurements and a scored visual verdict were not collected. Browser observations were inspected during the session; no screenshot bundle or raw trial artifacts are committed with this summary.

After this run, the skill clarified that missing browser access must retain two unverified direction descriptions and that the completion report must record candidate/choice evidence or the applicable skip rationale. Those final clarifications passed structural checks but were not subjected to another model A/B run. This remains an open behavioral validation item, not a passed regression test.

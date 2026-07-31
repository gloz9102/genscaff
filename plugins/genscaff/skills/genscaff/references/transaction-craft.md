# Transaction Craft

Use this after the router selects Form / transactional. Preserve existing validation, legal copy, and data-handling conventions.

## Checks

- Ask only for information required to complete the declared transaction.
- Use a safe default when one is conventional; do not add an unselected state for demonstration.
- Keep entered values after validation errors and return focus to the first actionable error.
- Explain field requirements before submission when the user can act on them.
- Prevent duplicate submission while work is pending without trapping recovery.
- Show a terminal receipt or confirmation with the submitted object, next step, and recovery path.
- Distinguish validation, network, authorization, conflict, and irreversible-action failures.
- Keep the primary action and relevant cost or consequence reachable on mobile.

Record `required_decisions`, `actions_to_primary_success`, and `default_selection_rationale`. Unsupported extra steps are `FABRICATED_FRICTION`.

## Submission contract

- Identify the irreversible boundary and make consequences clear before it.
- Preserve server-returned identifiers, totals, dates, and receipt details exactly.
- Do not present an intermediate loading state as completion.
- Make retry idempotent or explain when duplicate processing remains possible.

## Keyboard and focus

- Keep source order aligned with the visible task order.
- Move focus to a useful error summary or the first invalid control after failure.
- Keep the submit control reachable without crossing unrelated content.
- Confirm focus remains visible above sticky bars, keyboards, and dialogs.

## Evidence

- Capture populated input, a recoverable failure, pending submission, and the terminal receipt when those states changed.
- Verify preserved values after at least one validation or network failure.
- Verify rapid repeat activation does not create duplicate submissions.
- Record any required decision that cannot safely receive a default.

## Outcome gate

Score completion clarity, input preservation, error recovery, consequence honesty, and mobile completion from 0 to 5 using `workflow-rubric.md`. Revise only dimensions below 3.

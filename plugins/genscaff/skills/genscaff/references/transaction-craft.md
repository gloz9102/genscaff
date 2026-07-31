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

## Outcome gate

Score completion clarity, input preservation, error recovery, consequence honesty, and mobile completion from 0 to 5 using `workflow-rubric.md`. Revise only dimensions below 3.

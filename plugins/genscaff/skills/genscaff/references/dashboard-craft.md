# Dashboard Craft

Use this after the router selects Application / dashboard. Preserve the existing information architecture and operational vocabulary.

## Checks

- Put the most urgent exception or next decision before broad KPI decoration.
- Keep filters, sort, pagination, and selected rows stable after a row-level action.
- Show the domain object, state, owner, time, and consequence needed for the next decision.
- Prefer dense rows or tables when users compare repeated records; do not turn every record into a large card.
- Place row-level actions with the affected record and disclose destructive consequences before execution.
- Make loading, empty, partial-data, stale-data, error, success, and permission states distinguishable.
- Preserve the user's place after success, cancellation, or recovery.
- On mobile, prioritize the exception, object identity, status, and primary action; move secondary metrics later.

## State continuity

- Record which filters, sort, page, expansion, and selection must survive each action.
- Keep optimistic updates reversible and reconcile them with server truth.
- Return focus to the affected row or a clear confirmation after a modal closes.
- Do not erase the surrounding queue merely to make a successful state easy to capture.

## Density and hierarchy

- Use alignment, grouping, and restrained emphasis before adding containers.
- Reserve color for state or priority that also has a text or icon cue.
- Keep comparable values in consistent columns and units.
- Reveal secondary detail without hiding the object identity or next action.

## Evidence

- Capture the prioritized exception before action and the same operational context after action.
- Verify at least one filter or selection survives the changed flow when applicable.
- Check the densest plausible row and the narrowest supported viewport.
- Report unavailable, stale, or assumed data rather than filling it with invented metrics.

## Outcome gate

Score task clarity, exception priority, information density, state continuity, and mobile action reach from 0 to 5 using `workflow-rubric.md`. Revise only dimensions below 3.

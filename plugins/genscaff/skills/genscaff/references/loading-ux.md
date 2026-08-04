# Loading UX Contract

Use this whenever the changed surface reads remote data, submits data, streams results, lazy-loads media, waits on navigation, or starts a long-running job. A spinner is not a loading strategy.

## Priority order

Apply the first safe option that removes the wait. Combine later options only when the wait remains.

1. **Avoid the wait:** prefetch likely next data, reuse valid cached data, or start independent work earlier.
2. **Preserve continuity:** keep previous usable content visible while refreshing; replace it only when new data is ready.
3. **Show useful results first:** prioritize first-viewport text and media, progressively render usable partial results, and defer off-screen resources.
4. **Move long work to the background:** let the user leave, state that processing continues, notify on completion, and provide a stable return path.
5. **Expose status and control:** when waiting remains, show the current operation or stage, abnormal delay or retry state, and relevant cancel, retry, background, help, or recovery actions.

## Safety rules

- Use optimistic UI only for low-cost, reversible actions. On failure, restore the previous state and explain recovery.
- Do not use optimistic completion for payment, deletion, permission changes, irreversible settings, or any action whose result must be certain.
- If previous or cached data may be stale, label refresh activity or last-updated time so old data is not mistaken for current truth.
- Do not show a fabricated percentage. Use a real measured progress value, a known step count, or honest stage text.
- Do not keep the user waiting for decorative animation after the result is ready.
- Do not replace usable page content with a full-page spinner when the affected region can update in place.
- Reserve layout space for predictable content and avoid skeleton shapes that misrepresent the final structure.
- A failure state must keep recoverable input and context, explain what failed, and put retry or another recovery action at the failure point.

## Required implementation record

For each user-visible asynchronous boundary, record:

- `trigger`: what starts the wait;
- `affected_surface`: what may change or become temporarily unavailable;
- `wait_avoidance`: prefetch, cache, prior-data retention, priority loading, progressive result, background processing, or a concrete reason none is safe;
- `stale_data_policy`: freshness cue and replacement policy, or why no old data can appear;
- `failure_recovery`: rollback, retry, preserved input, or alternate path;
- `user_control`: cancel, retry, background, help, or a concrete reason control is not meaningful;
- `evidence`: the observed loading/refresh state and recovery result.

Do not mark loading not applicable when any remote read/write, delayed generation, stream, lazy media request, or background job exists in the changed flow.

## Verification

- Trigger the boundary instead of inferring behavior from source.
- Confirm usable surrounding content and user input do not disappear unnecessarily.
- Confirm success replaces or reconciles prior data without false completion.
- Force one failure or timeout path where practical and verify recovery in place.
- Verify reduced motion does not hide essential status and narrow viewports keep status and controls reachable.

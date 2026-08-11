# Transaction Craft

## Selection

Select for bounded forms, booking, checkout, authentication, payment, or submission. Do not select for browsing before a choice or informational content with no meaningful failure path.

## Craft

- Minimize required decisions and use safe defaults when they exist.
- Validate near the field, preserve input, associate errors, and summarize when needed.
- Make review, confirmation, retry, cancellation, and irreversible consequences explicit.
- Prevent double submission and expose an observable terminal result.
- Limit and protect privacy-sensitive information.

Required states usually include initial, invalid, submitting, success, and meaningful failure/retry; cancellation or review is conditional. Ensure complete keyboard operation, focus movement to errors or confirmation, status announcements, and correctly named controls. Watch third-party latency, duplicate requests, stale prices, and secret leakage. Verify submission start/feedback/result, applicable recovery, preserved data, error association, double-submit protection, and keyboard/focus.

Do not add extra steps, disabled CTAs, or choices merely to look sophisticated. Unsupported friction is `FABRICATED_FRICTION`.

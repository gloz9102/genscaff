# Genscaff 2.2 Quick samples

User-requested Quick demonstration: two standalone HTML surfaces for a fictional shared workspace, using a shared CSS token layer and no external assets or backend.

- landing.html: spacious introduction, space comparison, local visit-preview form.
- dashboard.html: operational summary, occupancy chart, reservation filters and native detail dialog.
- styles.css: shared accent, foreground, hover, pressed and subtle-state tokens.

Run locally: `python -m http.server 8822 --bind 127.0.0.1 --directory examples/v2.2-quick`

Verification: `node examples/v2.2-quick/verify.cjs` uses the repository's existing Playwright installation. Desktop 1440x1050 and mobile 390x844 passed rendering, page-overflow and primary-interaction checks. No console or page errors were observed. Dialog Escape and focus return, and reduced-motion transition suppression passed. Screenshots were visually inspected. A mobile filter wrapping issue was corrected and checks repeated.

Also ran `node --check` on both application scripts. No build is required. No Lighthouse, full keyboard audit, assistive-technology test, backend integration or comparative A/B evaluation was performed. Quick evidence only; no Standard or Strict certification. All displayed business data is fictional. No commit or deployment performed.

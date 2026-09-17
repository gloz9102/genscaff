# Task Classification and Legacy Router

Classify by user task and repository evidence, not brand surface.

- `project_mode`: `existing` or `new`
- `reference_mode`: `locked-reproduction`, `structural-reference`, `aesthetic-inspiration`, or `no-reference`
- one primary `experience_archetype`: `product-editorial`, `marketplace-discovery`, `media-discovery`, `workflow-application`, `content-editorial`, or `transaction`
- at most one justified secondary archetype
- only relevant `surface_type` values: `landing`, `search`, `listing`, `detail`, `dashboard`, `form`, `checkout`, `authentication`, `settings`, or `onboarding`
- `change_scope`: `local`, `component-set`, `route`, or `multi-route`

Record a short rationale. A brand name is a reference signal, not a classifier.

| Archetype | Primary task | Typical surfaces | Craft reference |
| --- | --- | --- | --- |
| `product-editorial` | Understand a product through focused narrative and media | landing, detail | `craft-product-editorial.md` |
| `marketplace-discovery` | Search, compare, assess trust/availability, choose | search, listing, detail | `craft-marketplace-discovery.md` |
| `media-discovery` | Browse meaningful groups, resume, choose content | landing, listing, detail | `craft-media-discovery.md` |
| `workflow-application` | Monitor, edit, or act on operational state | dashboard, settings | `craft-workflow-application.md` |
| `content-editorial` | Read, scan, navigate, or find information | listing, detail | `craft-content-editorial.md` |
| `transaction` | Complete a bounded submission, booking, or payment | form, checkout, authentication | `craft-transaction.md` |

## Legacy page-type compatibility

- `marketing-landing` implies `landing`; choose product-editorial or content-editorial from the actual job.
- `product-commerce` requires contextual choice between marketplace-discovery and transaction, then search/listing/detail/checkout surfaces.
- `application-dashboard` maps to workflow-application plus dashboard.
- `editorial-content` maps to content-editorial plus detail or listing.
- `form-transaction` maps to transaction plus form or checkout.

Do not infer an ambiguous archetype from one legacy string. New reports emit the new fields, not legacy page types.

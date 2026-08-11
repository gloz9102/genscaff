# Task Classification and Legacy Router

Classify by user task and repository evidence, not brand surface.

Record `project_mode`, `reference_mode`, one primary `experience_archetype`, an optional justified secondary archetype, relevant `surface_types`, `change_scope`, and a short rationale.

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

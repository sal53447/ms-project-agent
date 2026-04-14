# Dependencies — Website Redesign

## Upstream Dependencies (this project depends on these)

| ID | Dependency | Owner | Status | Impact if Delayed |
|----|------------|-------|--------|-------------------|
| D01 | Brand guidelines finalised (CEO sign-off) | CEO Office | In review — expected 2026-05-20 | Blocks design system start (M3) |
| D02 | Contentful enterprise licence procured | Finance / Sarah | PO in progress | Blocks CMS development |
| D03 | Hosting infrastructure selected and provisioned | Tom (Dev Lead) | Not started | Blocks deployment pipeline setup |
| D04 | HubSpot API credentials available to dev team | Marketing Ops | Available | None currently |

## Downstream Dependencies (other projects/teams waiting on this)

| ID | Dependent | What they need | Expected date |
|----|-----------|----------------|---------------|
| DD01 | Marketing campaign (Q3 2026) | Live website at new URL | 2026-09-30 |
| DD02 | SEO team | Redirect map published | 2026-09-30 (go-live) |

## Internal Dependencies (within this project)

- Design system (2.1) must be complete before any page template development begins.
- CMS content modelling (3.1) must be agreed before content migration scripts (3.3) can be built.
- Redirect map must be complete before DNS cutover (7.1).

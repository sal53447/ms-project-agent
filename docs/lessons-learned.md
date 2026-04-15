# Lessons Learned

## Microsoft Planner Hierarchy: Groups → Plans → Buckets → Tasks

**Date:** 2026-04-15

### Problem

When searching for a specific Planner plan ("Test Agent"), it was not visible through the CLI. The root cause was twofold:

1. **Hierarchy misunderstanding** — We searched across groups without knowing which group the plan belonged to.
2. **Pagination bug** — The groups list endpoint had a `$top=100` hard limit with no pagination. The tenant has 274 M365 groups, so any group beyond the first 100 was invisible.

### Key Insight: The M365 Group → Plan Relationship

In Microsoft 365, **Groups are the top-level container for Planner plans**. A Group corresponds to a SharePoint site or an email/Teams group. Plans always live inside a Group.

The hierarchy is:

```
M365 Group (= SharePoint site / email group / Teams team)
  └── Plan (a Planner board)
       └── Bucket (a column on the board)
            └── Task
                 └── Checklist items, attachments, comments
```

**To find a plan, you must first identify which Group it belongs to.** A plan cannot exist outside of a Group. When a user creates a "personal" plan and shares it with a group, Planner assigns that plan to the group's container.

### How to Search

1. **Start with the Group** — Ask which SharePoint site, Teams team, or email group the plan is associated with.
2. **List plans within that Group** — Use `planner plans list --group-id <id>`.
3. **If the Group is unknown** — Search all groups by name (`planner groups list`), then list plans for matching groups.

### Fix Applied

Added pagination support to the `groups list` command so it follows `@odata.nextLink` and retrieves all groups, not just the first 100.

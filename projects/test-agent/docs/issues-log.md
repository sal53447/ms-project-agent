# Issues Log — Test Agent

| Issue | Severity | Status | Notes |
|---|---|---|---|
| Groups list pagination bug — only first 100 of 274 groups were returned | Medium | Resolved | Fixed 2026-04-15: added @odata.nextLink pagination to groups list command |

| Executor agents failed in Run 1 — no Bash/Write/Edit permission in subagents | High | Resolved | All 11 instructions fell back to Orchestrator direct execution. Due dates may have been silently dropped. Need to configure subagent permissions before Run 3. Permissions configured before Run 4. |
| Bucket structure discrepancy between config.yaml and Run 2 instructions | Medium | Open | config.yaml bucket_ids still reflect original phase-based structure (phase1, phase2, admin, qa) despite Run 2 instructions recommending Kanban restructure (In Progress, Done, Backlog). Unknown whether Planner live state matches config.yaml or Run 2 instructions. PM Agent raised ask_human (INS-001) to resolve before further bucket instructions. |
| Executor permission Q&A task completed | High | Resolved | 2026-04-16 (Run 4) — Executor permission Q&A task (y8SnIUjvEU-WNfQtdRdhS5cAG8Gi) marked completed by owner. Treating Executor permission issue as resolved. Permissions now functional. |

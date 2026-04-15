# Issues Log — Test Agent

| Issue | Severity | Status | Notes |
|---|---|---|---|
| Groups list pagination bug — only first 100 of 274 groups were returned | Medium | Resolved | Fixed 2026-04-15: added @odata.nextLink pagination to groups list command |

| Executor agents failed in Run 1 — no Bash/Write/Edit permission in subagents | High | Open | All 11 instructions fell back to Orchestrator direct execution. Due dates may have been silently dropped. Need to configure subagent permissions before Run 3. |

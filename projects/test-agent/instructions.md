# PM Instructions — test agent
Generated: 2026-04-16T00:00:00Z
Methodology: Kanban
Health: amber

## Assessment Summary

This is Run 3. The project now has 7 tasks in Planner (one new since Run 1's 6), but the snapshot system has no prior baseline to diff against so task-level progress states are unknown from Planner directly. Two high-urgency tasks from Run 2 are approaching their due dates: the Phase 1 backfill task was due 2026-04-17 (tomorrow) and the "set milestone target dates" task is due 2026-04-22 (six days away) — neither is confirmed complete. The config.yaml still reflects the original phase-based bucket structure rather than the Kanban restructure (Backlog / In Progress / Done) instructed in Run 2, suggesting those create_bucket and update_task instructions may not have fully executed. The primary focus this cycle is: confirm and complete the bucket restructure, chase the two imminent deadlines, and verify that the Executor permission issue (raised as a High severity open issue) has been resolved.

## Methodology Rationale

Kanban is selected because this is a solo continuous-delivery project with no fixed sprint cadence, work flows from discovery through delivery continuously, and a dedicated Q&A bucket is used for human-agent communication.

---

## Findings

### Progress

- Planner task count is 7 (up from 6 after Run 1). One new task was created between runs — identity unknown from current snapshot; requires verification.
- The snapshot system is being initialised for the first time this run; no delta comparison is available. All progress state is inferred from prior run context and documentation.
- config.yaml bucket_ids still show phase-based keys (`phase1`, `phase2`, `admin`, `qa`) — the Kanban bucket restructure instructed in Run 2 (create "In Progress", create "Done", rename "To do" to "Backlog") has not been reflected in config.yaml, suggesting at least the config update instruction did not execute.
- Both milestones retain TBD target dates. "Set milestone target dates" task (9QIA4iwTTEKr4bObnx7TVpcAMOuj) is due 2026-04-22 — 6 days from today. Not confirmed complete.
- Phase 1 backfill task (QZRCpwlHlka41HJM7_TG4ZcAMgzE) was due 2026-04-17 — due tomorrow. Not confirmed complete. If missed, Planner continues to show 0% completion on Phase 1 work that is already done in code.
- Phase 1 estimated code completion: ~70–80% (CLI, auth, services, agent specs, onboarding skill complete per git history; Orchestrator + Executor agent full capability still being refined).
- Phase 2 progress: 0% — Azure Bot Service research task (4EtXneZ9W0awkcv0SGiTGJcADjpc) created but no evidence of progress. Milestone remains at-risk.

### Risks

- R1 (Open): Learning curve for deploying sub-agents into Teams — no progress on research task.
- R2 (Open): Azure Bot Service and Teams bot registration requirements unknown — research task at 0% progress; Phase 2 fully blocked.
- R3 (Open): No milestone target dates set — "Set milestone target dates" task due 2026-04-22; if not completed, PM agent cannot produce schedule health for another cycle.
- R4 (Open): Phase 1 completed work not reflected in Planner — backfill task due tomorrow (2026-04-17). If missed, completion rate remains artificially at 0%.
- R5 (Open): Executor agents lack Bash/Write/Edit permissions (High severity, open in issues-log.md) — if not resolved, this run's instructions will again fall back to Orchestrator direct execution or fail silently.
- NEW R7: config.yaml bucket_ids have not been updated to reflect the Kanban restructure from Run 2. If buckets were created in Planner but config.yaml was not updated, task routing in future runs will fail — the PM Agent will assign tasks to non-existent or wrong bucket names.
- NEW R8: The 7th task (identity unknown) may have been created without proper bucket assignment, due date, or assignment to the owner. Until verified, it represents an unmanaged item in the plan.

### Blockers

- CRITICAL: Open issue — Executor agents lack Bash/Write/Edit permissions (raised Run 1, still open as of issues-log.md). Until resolved, all instructions requiring CLI execution will fall back to Orchestrator or fail. This blocks autonomous operation.
- Backfill task (QZRCpwlHlka41HJM7_TG4ZcAMgzE) due 2026-04-17 — if not completed today or tomorrow, Phase 1 Planner visibility will continue to be zero, degrading PM assessment accuracy for all future runs.
- "Set milestone target dates" task (9QIA4iwTTEKr4bObnx7TVpcAMOuj) due 2026-04-22 — no schedule baseline exists until this is done; health rating cannot improve to green.
- config.yaml not updated after Run 2 bucket restructure instructions — task routing is potentially broken.
- Azure Bot Service research task (4EtXneZ9W0awkcv0SGiTGJcADjpc) due 2026-04-30 — currently at 0% progress with 14 days remaining. Phase 2 cannot be planned without this.

### Gaps

- config.yaml `milestone_bucket` and `risk_bucket` fields are still empty — must be populated after bucket restructure is confirmed complete.
- config.yaml document paths (`requirements`, `decisions_log`, `stakeholders`) remain empty — task fYbOxO-TJ0y0m2wMpXoxCJcAAvmO was created for this but not confirmed done.
- No acceptance criteria defined for Phase 1 milestone completion — "done" for Phase 1 is not formally specified beyond the requirements list.
- The 7th unknown task has no documented purpose in any project file.
- FR-3 (project onboarding workflow) and FR-4 (Q&A bucket) are delivered per the current system, but no formal "done" marker exists for these Phase 1 requirements items.

### Bucket Strategy

Current state (per config.yaml): four buckets defined — `phase1` (D--OF-tBmEeWpLH6zIjtGJcAAukV), `phase2` (F0qYvhHzQUW728AUSppvJZcACk_M), `admin` (ZFxd2GlkG0mBOLKVo0t7pZcAHUUo), `qa` (yWh9JA8ZvE6lhPdRwEYEHJcAI5WJ). However, prior run memory indicates the actual Planner live state used a "To do" bucket (Aj0eGMEpMk6roT87HPkK_pcADpEX) — there is a discrepancy between config.yaml and what was observed in Planner during Run 2. Run 2 instructions called for renaming "To do" to "Backlog" and creating "In Progress" and "Done" buckets, but config.yaml was never updated to reflect these.

Given the config.yaml currently shows a phase-based structure, and the decision log (2026-04-15) confirms the intentional choice of phase-based buckets (Phase 1, Phase 2, Admin, Q&A), there is ambiguity: should we follow the phase-based design captured in config.yaml, or the Kanban restructure recommended in Run 2?

The phase-based structure in config.yaml aligns with the decision log and is appropriate for this project. The Kanban restructure (Backlog/In Progress/Done) recommended in Run 2 conflicts with the established decision. The correct resolution is to ask the owner which structure to use before further restructure instructions are issued.

A `ask_human` instruction is generated to resolve this structural ambiguity before any bucket changes are made.

---

## Instructions

```yaml
instructions:
  - id: "INS-001"
    type: ask_human
    priority: high
    question: "The bucket structure is ambiguous. config.yaml defines phase-based buckets (Phase 1, Phase 2, Admin, Q&A), but Run 2 instructions recommended switching to a Kanban flow (Backlog, In Progress, Done, Q&A). The decision log also records the phase-based structure as intentional (2026-04-15). Which structure should the agent use going forward: (A) phase-based as in config.yaml, or (B) Kanban flow (Backlog / In Progress / Done / Q&A)? Also: can you confirm whether the Run 2 create_bucket and rename instructions actually executed in Planner?"
    context: "config.yaml bucket_ids still reflect the original phase-based structure. Run 2 instructions called for a Kanban restructure but config.yaml was never updated, suggesting they either did not execute or the config update step was skipped. Without knowing the current live bucket state and which structure is preferred, any bucket-related instructions this run risk creating duplicates or breaking task routing."
    reason: "Bucket structure gap and config.yaml discrepancy — cannot safely issue create_bucket or update_task bucket-assignment instructions without knowing the owner's intended structure and confirming current Planner bucket state."

  - id: "INS-002"
    type: ask_human
    priority: high
    question: "The Executor agent permission issue (open High-severity issue: 'Executor agents failed in Run 1 — no Bash/Write/Edit permission in subagents') was flagged in Run 1 and remains open in the issues-log.md. Has this been resolved for the current run? If not, what is the plan to fix it?"
    context: "If Executor agents still lack Bash/Write/Edit access, all instructions requiring CLI commands or doc updates will again fall back to Orchestrator direct execution or silently fail. This is the most operationally critical open issue in the project."
    reason: "Open High-severity issue in issues-log.md — Executor agent permissions. Blocks autonomous execution of all instructions that require CLI or file system access."

  - id: "INS-003"
    type: update_task
    priority: high
    task_id: "QZRCpwlHlka41HJM7_TG4ZcAMgzE"
    field: "description"
    value: "URGENT — due 2026-04-17 (tomorrow). Backfill completed Phase 1 work into Planner by creating tasks for: (1) CLI CRUD for plans/buckets/tasks/checklists/attachments, (2) App-only auth via client credentials, (3) Async GraphClient with ETag + retry logic, (4) Agent architecture specs (Orchestrator, PM Agent, Executor), (5) Project onboarding skill (SKILL.md). Mark all backfilled tasks as completed immediately. Until this is done, Planner shows 0% completion on work that is already shipped in code, causing every PM assessment to produce a false-zero baseline."
    reason: "Blocker — backfill task due tomorrow and not confirmed complete. Planner completion rate is artificially 0% because shipped Phase 1 work is invisible. Updating description to reinforce urgency and provide clear scope for execution."

  - id: "INS-004"
    type: update_task
    priority: high
    task_id: "9QIA4iwTTEKr4bObnx7TVpcAMOuj"
    field: "description"
    value: "Due 2026-04-22 (6 days). Set concrete target dates for both milestones in docs/milestones.md: (1) Phase 1: CLI + Agent System — proposed target 2026-05-30 based on remaining work (multi-agent system completion + end-to-end validation), (2) Phase 2: Teams Bot Integration — propose a date at least 8 weeks after Phase 1 target, pending Azure Bot Service research findings. Without milestone dates, PM agent health ratings will remain schedule-blind and cannot reach green."
    reason: "Blocker — no schedule baseline exists. Both milestones have TBD dates. This is a persistent gap from Run 1 and Run 2. Updating description with proposed dates to help owner make a quick decision."

  - id: "INS-005"
    type: update_task
    priority: high
    task_id: "4EtXneZ9W0awkcv0SGiTGJcADjpc"
    field: "description"
    value: "Due 2026-04-30 (14 days). Research and document: (1) Azure Bot Service — what is it, what does setup involve, what permissions are needed? (2) Teams bot registration in Azure AD — app registration requirements, manifest, bot channel, (3) Microsoft Bot Framework SDK vs Azure Bot Service — which to use? (4) How does the bot receive messages from Teams channels? (5) Estimated effort for Phase 2. Output: a short research note added to docs/dependencies.md updating the 'Azure Bot Service' row from 'Unknown' to a defined status. This unblocks all Phase 2 planning."
    reason: "Blocker — Phase 2 fully blocked on this research. Due in 14 days but at 0% progress. Updating description with concrete scope so it is immediately actionable."

  - id: "INS-006"
    type: flag_risk
    priority: high
    risk: "config.yaml bucket_ids have not been updated after Run 2 bucket restructure instructions — live Planner bucket structure is unknown and may diverge from config.yaml"
    impact: medium
    mitigation: "Owner to confirm current live bucket state in Planner (via planner buckets list --plan-id WWclzqKzu0y9Abfr3qx4yZcAFNzi) and update config.yaml to match. No new bucket create_task instructions should be issued until the live state is confirmed."
    reason: "Bucket structure gap — config.yaml shows phase-based buckets but Run 2 instructions attempted a Kanban restructure. The two are inconsistent and the live state is unverified."

  - id: "INS-007"
    type: flag_risk
    priority: high
    risk: "Unknown 7th task exists in Planner — created between Run 1 and Run 3 with no documentation in project files"
    impact: low
    mitigation: "Owner to identify the 7th task (via planner tasks list --plan-id WWclzqKzu0y9Abfr3qx4yZcAFNzi) and either: (a) add context to its description, (b) assign it to the correct bucket, or (c) delete it if erroneous."
    reason: "Snapshot baseline shows 7 tasks. Run 1 created 6. The 7th is unaccounted for in any project documentation."

  - id: "INS-008"
    type: update_milestone
    priority: medium
    milestone: "Phase 1: CLI + Agent System"
    field: status
    value: "on-track"
    reason: "Progress check — Phase 1 has ~70-80% code completion. No milestone date exists so no schedule slippage can be confirmed. Remaining work (full Orchestrator/Executor capability) is in progress. on-track is appropriate pending milestone date being set."

  - id: "INS-009"
    type: update_milestone
    priority: medium
    milestone: "Phase 2: Teams Bot Integration"
    field: status
    value: "at-risk"
    reason: "Blocker identification — Azure Bot Service research task at 0% progress with 14 days to due date. No Phase 2 planning is possible until research completes. at-risk status persists."

  - id: "INS-010"
    type: add_note
    priority: medium
    field: "issues-log.md"
    value: "2026-04-16 (Run 3) — Observation: config.yaml bucket_ids still reflect original phase-based structure (phase1, phase2, admin, qa) despite Run 2 instructions recommending a Kanban bucket restructure. It is unknown whether the Planner live bucket state matches config.yaml or the Run 2 instructions. PM Agent has raised ask_human (INS-001) to resolve this before further bucket instructions are issued. Until resolved, bucket routing for new task creation is unreliable."
    reason: "Bucket structure discrepancy identified in Run 3 gap analysis. Recording in issues-log.md for traceability."

  - id: "INS-011"
    type: add_note
    priority: low
    field: "decision-log.md"
    value: "2026-04-16 (Run 3) — PM Agent observation: Run 2 bucket restructure instructions (create 'In Progress', create 'Done', rename 'To do' to 'Backlog') appear not to have been reflected in config.yaml. Phase-based bucket structure in config.yaml (Phase 1, Phase 2, Admin, Q&A) remains consistent with decision-log entry from 2026-04-15. PM Agent is treating config.yaml as the source of truth pending owner confirmation. If the Kanban restructure is confirmed as the intended direction, config.yaml must be updated to reflect new bucket IDs before the next agent run."
    reason: "Structural ambiguity in bucket strategy — recording for traceability and to ensure the decision is made explicitly by the owner rather than inferred by the agent."
```

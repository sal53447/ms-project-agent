# PM Instructions — test agent
Generated: 2026-04-15T10:00:00Z
Methodology: Kanban
Health: amber

## Assessment Summary

Run 2 finds the plan in a structurally improved but operationally stalled state: all 6 tasks from Run 1 were successfully created, but every task sits at 0% progress, no task has a due date visible in Planner, and all 6 are piled into the single "To do" bucket — making the Kanban board unreadable and providing no signal about what is active versus queued. The most urgent intervention this cycle is to restructure the board into a meaningful flow (Backlog → In Progress → Done, plus Q&A), move tasks to their correct columns, and assign due dates so the PM agent can produce schedule-based health ratings next run. The backfill of completed Phase 1 work and the Azure Bot Service research task remain open execution items.

## Methodology Rationale

Kanban is selected because this is a solo continuous-delivery project with no fixed sprint cadence, work flows from discovery through delivery continuously, and a dedicated Q&A bucket serves as the human-agent communication channel.

---

## Findings

### Progress

- 6 tasks exist in Planner (all created by Run 1 Executors) — this is improvement over the zero-task baseline from Run 1.
- All 6 tasks are at 0% completion with no due dates recorded in Planner, despite INS-001 and INS-002 having due dates specified in the instructions. Due dates were likely not applied during execution — see Blockers.
- Both milestones still have TBD target dates; no schedule baseline exists. Schedule health cannot be calculated.
- Phase 1 completed work (CLI, auth, async services, agent specs) remains invisible in Planner — the backfill task (INS-003 / task QZRCpwlHlka41HJM7_TG4ZcAMgzE) was created but has not been acted on.
- The Azure Bot Service research task (INS-001 / task 4EtXneZ9W0awkcv0SGiTGJcADjpc) exists but has 0% progress; Phase 2 remains fully blocked.
- Estimated Planner completion rate: 0% (0 of 6 tasks done). Actual Phase 1 code completion: ~70% (CLI, auth, services done; Orchestrator and Executor agents remaining).

### Risks

- R1 (Open): Learning curve for deploying sub-agents into Teams — still no progress on research.
- R2 (Open): Azure Bot Service requirements unknown — research task created but not started.
- R3 (Open): No milestone target dates — persists from Run 1; "Set milestone target dates" task exists but has 0% progress.
- R4 (Open): Phase 1 completed work not reflected in Planner — backfill task exists but has not been executed.
- R5 (Open): All 6 tasks in a single "To do" bucket — no workflow visibility, no WIP tracking, no separation of backlog from active work. This will cause every future PM assessment to have degraded signal quality. Impact: medium.
- NEW R6: Due dates from Run 1 INS-001 (2026-04-30) and INS-002 (2026-04-22) do not appear to have been applied in Planner (execution log notes Executor agents ran as Orchestrator fallback). If dates were not actually set, the two most time-sensitive tasks have no deadline signal. Impact: medium.

### Blockers

- Bucket structure: all tasks in "To do" — no way to distinguish queued, active, or completed work without expanding each task. This blocks meaningful Kanban flow and PM assessment accuracy.
- No due dates on any tasks in Planner — blocks schedule health assessment in future runs.
- "Create Planner tasks for completed Phase 1 work (backfill)" task exists but is unstarted — until Phase 1 completed items are marked done, Planner reports 0% on all work including finished deliverables.
- "Set milestone target dates" task exists but is unstarted — no schedule baseline is possible until this is resolved.

### Gaps

- Bucket structure gap: current buckets are "To do" and "Q&A". A Kanban-appropriate set should be: Backlog, In Progress, Done, Q&A. Without In Progress and Done buckets, there is no workflow state tracking.
- config.yaml `milestone_bucket` and `risk_bucket` fields are empty — cannot be populated until the correct bucket names exist in Planner.
- config.yaml document paths (`requirements`, `decisions_log`, `stakeholders`) are still empty — this task exists (INS-011 / fYbOxO-TJ0y0m2wMpXoxCJcAAvmO) but has not been acted on.
- Due dates on tasks 4EtXneZ9W0awkcv0SGiTGJcADjpc and 9QIA4iwTTEKr4bObnx7TVpcAMOuj need verification and application; they may not have been set during Run 1 execution.

### Bucket Structure Review

Current state: 2 buckets ("To do", "Q&A"). All workflow tasks land in "To do" with no way to show progress state in the Planner board view.

Recommended Kanban bucket structure for this project:

| Bucket Name | Purpose | Maps to config.yaml key |
|---|---|---|
| Backlog | Planned but not yet started work | (new — update config.yaml) |
| In Progress | Actively being worked on (WIP limit: 2 for solo dev) | (new — replaces "To do" role) |
| Done | Completed tasks — kept visible for PM assessment accuracy | (new) |
| Q&A | Human-agent communication tasks | qa (existing) |

The existing "To do" bucket should be renamed to "Backlog" (retains its ID, Planner supports rename). Tasks currently in "To do" should be triaged: the Azure Bot Service research task and "Set milestone target dates" task are the most active and should move to "In Progress"; the others remain in "Backlog". "In Progress" and "Done" are new buckets to create.

After bucket restructure, config.yaml should be updated:
- `bucket_ids.todo` → rename key to `backlog`, keep same ID (Aj0eGMEpMk6roT87HPkK_pcADpEX)
- `bucket_ids.in_progress` → new bucket ID (to be created)
- `bucket_ids.done` → new bucket ID (to be created)
- `bucket_ids.qa` → unchanged (yWh9JA8ZvE6lhPdRwEYEHJcAI5WJ)
- `agent.milestone_bucket` → "Backlog" (milestones are planned but not active)
- `agent.risk_bucket` → "Backlog" (risk research tasks start in backlog)

---

## Instructions

```yaml
instructions:
  - id: "INS-001"
    type: create_bucket
    priority: high
    plan_id: "WWclzqKzu0y9Abfr3qx4yZcAFNzi"
    name: "In Progress"
    reason: "Bucket structure gap — no active-work column exists. All tasks collapse into a single backlog bucket, making Kanban flow untrackable. This is the highest-priority structural fix this cycle."

  - id: "INS-002"
    type: create_bucket
    priority: high
    plan_id: "WWclzqKzu0y9Abfr3qx4yZcAFNzi"
    name: "Done"
    reason: "Bucket structure gap — no completion column exists. Without a Done bucket, the PM agent cannot calculate accurate completion rates from Planner state, and backfill tasks cannot be placed correctly."

  - id: "INS-003"
    type: update_task
    priority: high
    task_id: "Aj0eGMEpMk6roT87HPkK_pcADpEX"
    field: "title"
    value: "Backlog"
    reason: "Bucket structure review — the existing 'To do' bucket should be renamed to 'Backlog' to reflect its correct Kanban role (queued, unstarted work). Renaming retains the existing bucket ID and all task assignments."

  - id: "INS-004"
    type: update_task
    priority: high
    task_id: "4EtXneZ9W0awkcv0SGiTGJcADjpc"
    field: "due_date"
    value: "2026-04-30"
    reason: "Risk R6 — due date from Run 1 INS-001 may not have been applied. This task is the Phase 2 research blocker; deadline enforcement is critical. Re-asserting the due date."

  - id: "INS-005"
    type: update_task
    priority: high
    task_id: "9QIA4iwTTEKr4bObnx7TVpcAMOuj"
    field: "due_date"
    value: "2026-04-22"
    reason: "Risk R6 — due date from Run 1 INS-002 may not have been applied. Setting milestone target dates is the prerequisite for all future schedule-based health assessments."

  - id: "INS-006"
    type: update_task
    priority: high
    task_id: "QZRCpwlHlka41HJM7_TG4ZcAMgzE"
    field: "due_date"
    value: "2026-04-17"
    reason: "Blocker — backfill task has no due date and 0% progress. Planner shows 0% project completion because completed Phase 1 work is invisible. This task must be executed within 2 days to give future PM assessments an accurate baseline."

  - id: "INS-007"
    type: update_task
    priority: high
    task_id: "cwiLNJYF7k2ONLJ4rInxS5cABq2K"
    field: "due_date"
    value: "2026-05-15"
    reason: "Gap — 'Complete multi-agent system' has no due date. This is the primary remaining Phase 1 deliverable. A provisional date enables schedule health to be tracked."

  - id: "INS-008"
    type: update_task
    priority: high
    task_id: "uVg9CWOJ-0mwNGJEZkViWJcAEoSa"
    field: "due_date"
    value: "2026-05-22"
    reason: "Gap — 'Validate project onboarding workflow end-to-end' has no due date. Required for Phase 1 milestone completion; date set after multi-agent system task."

  - id: "INS-009"
    type: update_task
    priority: high
    task_id: "fYbOxO-TJ0y0m2wMpXoxCJcAAvmO"
    field: "due_date"
    value: "2026-04-22"
    reason: "Gap — 'Update config.yaml' has no due date. config.yaml must be populated before the bucket restructure is complete, so it can be done in the same session as INS-001/INS-002."

  - id: "INS-010"
    type: flag_risk
    priority: high
    risk: "All 6 tasks concentrated in a single 'To do' bucket — Kanban board provides zero workflow signal"
    impact: medium
    mitigation: "Create 'In Progress' and 'Done' buckets (INS-001, INS-002). Rename 'To do' to 'Backlog' (INS-003). Move active tasks to 'In Progress'. Update config.yaml bucket mappings after restructure."
    reason: "Bucket structure review — single-bucket collapse identified as R5 during risk scan. Formally recording in risk register so pattern is visible in future runs."

  - id: "INS-011"
    type: flag_risk
    priority: high
    risk: "Due dates from Run 1 instructions may not have been applied to Planner tasks — execution log notes Executor agents fell back to Orchestrator direct execution"
    impact: medium
    mitigation: "Re-assert due dates via update_task instructions (INS-004 through INS-009). Verify in Planner after this run that due dates are visible on all tasks."
    reason: "Risk R6 identified in risk scan — execution log notes Executor agents had permission restrictions and ran as Orchestrator fallback. Due dates may have been silently dropped."

  - id: "INS-012"
    type: add_note
    priority: medium
    field: "decision-log.md"
    value: |
      2026-04-15 (Run 2) — PM Agent recommended bucket restructure: rename "To do" to "Backlog", add "In Progress" and "Done" buckets to support Kanban flow. Rationale: all 6 tasks piled into a single bucket provides no workflow visibility and degrades PM assessment signal quality. Config.yaml bucket_ids should be updated after new buckets are created in Planner.
    reason: "Bucket structure review — recording the structural decision for future reference so the rationale is traceable."

  - id: "INS-013"
    type: update_milestone
    priority: medium
    milestone: "Phase 1: CLI + Agent System"
    field: status
    value: "on-track"
    reason: "Progress check — Phase 1 has meaningful completed work in code (~70%) and active tasks in Planner. No deadline has been missed (no date set). On-track is the correct status while work is progressing."

  - id: "INS-014"
    type: update_milestone
    priority: medium
    milestone: "Phase 2: Teams Bot Integration"
    field: status
    value: "at-risk"
    reason: "Blocker identification — Phase 2 research task still at 0% progress. Azure Bot Service dependency remains Unknown. at-risk status persists from Run 1."

  - id: "INS-015"
    type: add_note
    priority: low
    field: "issues-log.md"
    value: |
      2026-04-15 (Run 2) — Observation: Executor agents in Run 1 fell back to Orchestrator direct execution due to permission restrictions (no Bash/Write/Edit access). Due dates specified in INS-001 and INS-002 may not have been applied to Planner tasks. PM Agent has re-asserted these dates in Run 2 instructions INS-004 and INS-005. Recommend verifying Executor agent permissions before Run 3 to confirm CLI command access is working.
    reason: "Execution gap — Run 1 execution log explicitly states 'Executor agents failed due to permission restrictions'. Recording so the owner can diagnose Executor agent setup before the next run."
```

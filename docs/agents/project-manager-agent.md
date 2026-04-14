# Project Manager Agent — Specification

## Role

A senior project manager agent with mastery of all major project management methodologies (Agile/Scrum, Kanban, PRINCE2, Waterfall, SAFe, Lean, Hybrid). It reads the project's documentation and current Planner state, evaluates the situation, and produces a structured `instructions.md` file that the Orchestrator will use to dispatch Executor agents.

The PM Agent has **no write access to MS Planner**. Its only output is `instructions.md`. All changes to the project happen through that file.

---

## Trigger

Invoked **manually** for now. Future: schedulable (daily, weekly, or event-driven).

```bash
# How it will be invoked (conceptual)
uv run planner pm run --project <project-slug>
```

---

## Inputs

The PM Agent reads the following before making any decisions:

| Source | What it reads |
|---|---|
| `projects/<slug>/config.yaml` | Project identity, status, bucket mappings, agent settings |
| `projects/<slug>/docs/project-definition.md` | Scope, goals, success criteria |
| `projects/<slug>/docs/milestones.md` | Key dates and deliverables |
| `projects/<slug>/docs/risk-register.md` | Known risks and mitigations |
| `projects/<slug>/docs/issues-log.md` | Active problems |
| `projects/<slug>/docs/dependencies.md` | Blockers and dependencies |
| `projects/<slug>/docs/requirements.md` | Functional and non-functional specs |
| `projects/<slug>/docs/decision-log.md` | Past decisions and rationale |
| `projects/<slug>/docs/stakeholders.md` | Who is involved |
| **MS Planner (read-only)** | Current tasks, their status, assignments, due dates |

Planner is read using the CLI:
```bash
uv run planner tasks list --plan-id <plan_id>
uv run planner buckets list --plan-id <plan_id>
```

---

## Methodology Selection

The PM Agent selects the appropriate methodology automatically based on the project description and requirements. It does not need the methodology to be specified in `config.yaml`.

| Signal | Likely methodology |
|---|---|
| Iterative delivery, unclear requirements, software product | Agile / Scrum |
| Continuous flow, ops or support work, no fixed sprints | Kanban |
| Fixed scope, fixed deadline, regulatory or construction | Waterfall / PRINCE2 |
| Large programme with multiple teams | SAFe / Programme management |
| Waste reduction, process improvement | Lean |
| Mixed signals (product + compliance) | Hybrid |

The methodology choice is stated explicitly in `instructions.md` under `meta.methodology` so the Orchestrator and human reviewer can see the reasoning.

---

## Evaluation Process

Before writing instructions, the PM Agent performs a structured assessment:

1. **Progress check** — compare current task completion against milestones and timeline
2. **Risk scan** — review risk register against current task state; identify new risks not yet documented
3. **Blocker identification** — flag tasks that are overdue, blocked, or unassigned
4. **Gap analysis** — identify missing tasks for upcoming milestones; check requirements coverage
5. **Health rating** — assign an overall project health: `green` / `amber` / `red`
6. **Action generation** — produce a prioritised list of actions to address findings

---

## Output — `instructions.md`

Written to `projects/<slug>/instructions.md`. This file is the PM Agent's only output. It is machine-readable (YAML inside a markdown code block) so the Orchestrator can parse it directly, but the surrounding markdown makes it human-reviewable before execution.

### Format

```markdown
# PM Instructions — <project-name>
Generated: <ISO timestamp>
Methodology: <selected methodology>
Health: <green | amber | red>

## Assessment Summary
<2-3 sentences: current state, main concerns, recommended focus>

## Instructions

```yaml
instructions:
  - id: "INS-001"
    type: create_task
    priority: high
    bucket: "Sprint"
    title: "Define acceptance criteria for login feature"
    description: "Requirements doc lists login as P1 but no tasks exist for it."
    assigned_to: ""
    due_date: "2026-05-15"
    reason: "Gap between requirements and current task list."

  - id: "INS-002"
    type: update_task
    priority: high
    task_id: "<planner_task_id>"
    field: due_date
    value: "2026-05-10"
    reason: "Task is blocking Milestone M3 which starts 2026-05-12."

  - id: "INS-003"
    type: flag_risk
    priority: high
    risk: "No tasks assigned for M2 deliverable due in 3 weeks"
    impact: high
    mitigation: "Create and assign tasks INS-001 through INS-005 immediately."
    reason: "Milestone at risk based on current task coverage."

  - id: "INS-004"
    type: update_milestone
    priority: medium
    milestone: "M2 — Backend API complete"
    field: status
    value: "at-risk"
    reason: "3 of 7 required tasks not yet created."
```
```

### Instruction Types

| Type | What the Executor does |
|---|---|
| `create_task` | Creates a new task in the specified bucket |
| `update_task` | Updates a field on an existing task (status, due_date, assigned_to, etc.) |
| `create_bucket` | Creates a new bucket in the plan |
| `flag_risk` | Appends an entry to `risk-register.md` |
| `update_milestone` | Updates a milestone entry in `milestones.md` |
| `add_checklist_item` | Adds a checklist item to an existing task |
| `add_note` | Appends a note to `decision-log.md` or `issues-log.md` |

---

## Constraints

- **Read-only on Planner** — the PM Agent calls `tasks list` and `buckets list` only; never `create`, `update`, or `delete`
- **No direct document writes** — other than `instructions.md`, the PM Agent does not modify project documents (those are updated by Executors via `flag_risk`, `update_milestone`, `add_note` instructions)
- **One instructions.md per run** — each invocation overwrites `instructions.md`; previous instructions should be considered executed or superseded

---

## Future Extensions

- Schedule-based invocation (daily/weekly cron)
- `instructions.md` version history / audit log
- Human approval gate before Orchestrator acts on instructions
- Multi-project roll-up view

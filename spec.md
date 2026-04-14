# MS Project Agent — Skill Specification

## Overview

This document defines the specification for building a **project onboarding workflow skill** for the MS Project Agent. The goal is to onboard any MS Planner project into this codebase so that an agent can manage and summarize it efficiently, minimizing API calls.

---

## Onboarding Workflow

When onboarding a new project:

1. Collect project identity from the user (plan ID, group ID, name, etc.)
2. Create a `config.yaml` for the project under a designated folder (e.g., `projects/<project-name>/config.yaml`)
3. Scaffold the required project documents (see below) — created with user input
4. Register the project in a central index so agents can discover it
5. Validate the connection by making a lightweight API call

---

## Project Documents to Create at Onboarding

Each project should have the following documents created alongside the task list:

| Document | Purpose |
|---|---|
| **Project Definition** | Scope, goals, what is in/out |
| **Milestones** | Key dates and deliverables |
| **Risk Register** | Risks with probability, impact, mitigation |
| **Issues Log** | Active problems (distinct from risks) |
| **Requirements** | Functional and non-functional specs |
| **Work Breakdown Structure (WBS)** | Hierarchical decomposition of deliverables |
| **Assumptions & Constraints** | Known boundaries and preconditions |
| **Dependencies** | Task-to-task and project-to-project relationships |
| **Stakeholder Register** | Who is involved and their role |
| **RACI Matrix** | Responsible, Accountable, Consulted, Informed |
| **Budget / Cost Tracking** | Resource and financial overview |
| **Decision Log** | Key decisions and their rationale |
| **Change Requests** | Formal scope or schedule changes |
| **Status Reports** | Generated summaries from the above |
| **Lessons Learned** | Post-project or mid-project retrospective notes |
| **Meeting Notes / Action Items** | Ongoing communication record |

> **Priority tier for agent summaries:** Tasks → Milestones → Risks/Issues → Dependencies → Status Summary → Decision Log → Resource Assignments

---

## `config.yaml` Schema

Each project has a `config.yaml` that enables fast connection and agent context without extra API calls.

```yaml
project:
  name: "Project Alpha"
  plan_id: "abc123..."          # MS Planner plan ID (required)
  group_id: "xyz456..."         # M365 group ID (required)
  bucket_ids:                   # optional: named shortcuts to key buckets
    backlog: "bucket_id_1"
    sprint: "bucket_id_2"

meta:
  description: "Short summary of what this project is"
  owner: "name or email"
  start_date: "YYYY-MM-DD"
  end_date: "YYYY-MM-DD"
  status: "active"              # active | on-hold | closed
  tags: []

agent:
  summary_schedule: "weekly"    # how often to pull updates
  milestone_bucket: ""          # bucket ID tracking milestones
  risk_bucket: ""               # bucket ID tracking risks
  priority_labels:              # labels that trigger alerts
    - "High"
    - "Critical"

documents:
  requirements: ""              # link to requirements doc
  decisions_log: ""             # link to decisions log
  stakeholders: ""              # link to stakeholder register
```

### Minimum Required Fields

- `project.plan_id` — needed for all Planner API calls
- `project.group_id` — needed for group-level Graph API calls

Everything else is context that helps the agent answer questions without round-trips to the API.

---

## Skill Intent

This spec is the input to the **skill-creator** skill. The skill to be created should:

- Guide the user through onboarding a new MS Planner project
- Interactively collect values for `config.yaml`
- Scaffold the project document list (as stubs or prompts)
- Validate the connection using the existing `GraphClient`
- Register the project for agent discovery

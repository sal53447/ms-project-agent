---
name: ms-project-onboarding
description: Onboard a new MS Planner project into the ms-project-agent codebase. Use this skill whenever the user wants to add, register, connect, or set up a new project — even if they phrase it as "I want to track a new project", "add a project", "connect to a plan", or "set up a Planner project". Guides the user through collecting plan_id and group_id, writing a config.yaml, scaffolding project documents, and validating the connection.
---

# MS Planner Project Onboarding

This skill walks through onboarding a new MS Planner project so that the agent can manage and summarize it efficiently, with minimal API calls per session.

## What onboarding does

1. Collect the project's identity from the user
2. Validate the connection and pull what exists from Planner (tasks, buckets)
3. Interview the user to gather project context that Planner doesn't store
4. Create `projects/<project-slug>/config.yaml` with connection and context data
5. Create populated project documents from the interview answers
6. Register the project in `projects/index.yaml`
7. Create the **Q&A bucket** in the Planner plan (human-agent communication channel)

> **Why interview?** MS Planner only stores tasks. It has no project definition, milestones doc, risk register, or stakeholder list. That context only exists in people's heads or scattered documents — the interview captures it so the agent can answer questions and generate summaries without needing extra API calls later.

---

## Step 1 — Collect project identity

Ask the user for the following. The first two are required; the rest can be filled in later but collecting them now saves round-trips.

| Field | Required | Description |
|---|---|---|
| `plan_id` | Yes | MS Planner plan ID (find with `planner plans list --group-id <id>`) |
| `group_id` | Yes | M365 group / team ID (find with `planner groups list`) |
| `name` | Yes | Human-readable project name |
| `description` | Recommended | One-sentence summary of what the project is |
| `owner` | Recommended | Name or email of the project owner |
| `start_date` / `end_date` | Optional | ISO dates (YYYY-MM-DD) |
| `tags` | Optional | Comma-separated labels |

If the user doesn't provide `plan_id` or `group_id`, look them up using the CLI tools — don't ask the user to run commands themselves.

**Finding group_id by name:**
```bash
uv run planner groups list
```
Parse the output and match the group whose name is closest to what the user described. Show the match and confirm with the user before proceeding.

**Finding plan_id by name:**
```bash
uv run planner plans list --group-id <group_id>
```
Parse the output and match the plan whose title is closest to the project name the user provided. Show the match and confirm before proceeding.

If multiple close matches exist, list them and ask the user to pick one.

**Finding bucket IDs (optional but recommended):**

Once `plan_id` is known, list the plan's buckets and ask the user which ones serve as milestone, risk, backlog, sprint, etc.:
```bash
uv run planner buckets list --plan-id <plan_id>
```
Show the bucket names and IDs, then ask: "Which of these is your milestones bucket? Which tracks risks?" Map the answers to `project.bucket_ids` and `agent.milestone_bucket` / `agent.risk_bucket` in the config. Any bucket the user doesn't assign a role to can be left blank and filled in later.

---

## Step 2 — Create config.yaml

Create the file at `projects/<project-slug>/config.yaml` where `<project-slug>` is the project name lowercased and hyphenated (e.g., "Project Alpha" → `project-alpha`).

Use this template, filling in what the user provided and leaving the rest as empty strings or empty lists:

```yaml
project:
  name: "<name>"
  plan_id: "<plan_id>"          # required
  group_id: "<group_id>"        # required
  bucket_ids: {}                # fill in later: name -> bucket_id

meta:
  description: "<description>"
  owner: "<owner>"
  start_date: "<start_date>"
  end_date: "<end_date>"
  status: "active"              # active | on-hold | closed
  tags: []

agent:
  summary_schedule: "weekly"    # how often to pull updates
  milestone_bucket: ""          # bucket ID tracking milestones
  risk_bucket: ""               # bucket ID tracking risks
  priority_labels:
    - "High"
    - "Critical"

documents:
  requirements: ""
  decisions_log: ""
  stakeholders: ""
```

---

## Step 3 — Interview the user

MS Planner only stores tasks — it has no project definition, no milestones list, no risk register. Before creating any documents, interview the user to gather this context. 

**Always start here:** Ask the user to describe the project in their own words — what it is, what it's trying to achieve, and what done looks like. This single answer often contains enough to seed most of the documents. Listen carefully and note what's present and what's missing.

Then probe for gaps. For each area below, if the user's description didn't cover it, ask a focused follow-up question. Don't ask all of these at once — ask only what's still missing after their initial description, and batch related questions together to avoid overwhelming them.

| Area | What to ask if missing |
|---|---|
| **Scope** | What's in scope? What's explicitly out of scope? |
| **Goals / success criteria** | How will you know this project succeeded? |
| **Milestones** | What are the key dates or checkpoints? |
| **Risks** | What could go wrong? What are you most worried about? |
| **Stakeholders** | Who is involved? Who is the decision-maker? Who needs to be kept informed? |
| **Dependencies** | Does this depend on other projects or teams? Is anything waiting on this? |
| **Assumptions** | What are you assuming to be true that could change? |
| **Budget / resources** | Is there a budget or team size constraint worth capturing? |
| **Open issues** | Are there any known problems already in flight? |

Once you have enough to write meaningful content for each document, proceed. If a topic truly has no information (e.g. no budget discussion yet), create the file as a stub with headers only and a note that it needs to be filled in.

---

## Step 4 — Create project documents

Create files in `projects/<project-slug>/docs/` using the information gathered in the interview. These should be **populated with real content**, not empty templates. Use what the user told you.

| File | Populated from |
|---|---|
| `project-definition.md` | Project description, goals, scope in/out |
| `milestones.md` | Key dates and deliverables the user mentioned |
| `risk-register.md` | Risks named in the interview, with probability/impact/mitigation columns |
| `issues-log.md` | Any active problems the user mentioned |
| `requirements.md` | Functional and non-functional specs (stub if not discussed) |
| `wbs.md` | Work breakdown based on task buckets + user description |
| `assumptions-constraints.md` | Assumptions and constraints from the interview |
| `dependencies.md` | Dependencies on other projects/teams |
| `stakeholders.md` | Names and roles the user provided |
| `raci.md` | RACI matrix based on stakeholders (stub if not enough info) |
| `budget.md` | Budget/resource constraints if mentioned (stub if not) |
| `decision-log.md` | Any decisions already made that the user described |
| `change-requests.md` | Empty stub — populated over time |
| `lessons-learned.md` | Empty stub — populated over time |
| `meeting-notes.md` | Empty stub — populated over time |

Each file must have a `# Title` heading. Populated sections should have real content. Stub sections should have headers and a `> To be filled in.` note so gaps are visible.

**Priority for agent summaries:** Tasks → Milestones → Risks/Issues → Dependencies → Status Summary → Decision Log → Resource Assignments. When generating summaries, read these files in this order.

---

## Step 5 — Register in index

Append (or create) `projects/index.yaml` with an entry for this project:

```yaml
projects:
  - slug: "<project-slug>"
    name: "<name>"
    plan_id: "<plan_id>"
    group_id: "<group_id>"
    status: "active"
    config: "projects/<project-slug>/config.yaml"
```

If the file already exists, read it first and append — don't overwrite existing entries.

---

## Step 6 — Validate the connection

Run a lightweight API call to confirm the credentials and IDs are correct:

```bash
uv run planner tasks list --plan-id <plan_id>
```

If it succeeds, confirm to the user: "Connected — found N tasks in `<plan name>`."

If it fails:
- **404**: plan_id or group_id is wrong — ask the user to double-check
- **403**: app registration lacks permissions — point them to `docs/azure-setup.md`
- **401**: token issue — check that `.env` has valid `TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`

---

## Step 7 — Create the Q&A bucket

The Q&A bucket is the communication channel between humans and the agent system. It must exist before the Orchestrator can run.

Create it if it doesn't already exist:
```bash
uv run planner buckets list --plan-id <plan_id>
# If "Q&A" not present:
uv run planner buckets create --plan-id <plan_id> --name "Q&A"
```

If the bucket already exists (the plan was previously used), note its ID and store it in `config.yaml` under `project.bucket_ids.qa`.

The Q&A bucket works as follows:
- Humans create tasks in it to send requests or answer questions from the agent
- The agent creates tasks in it when it needs information from a human
- A task's **status** controls whether it is acted on:
  - `not_started` → documentation / waiting for human decision
  - `in_progress` → human has approved — the Orchestrator will act on it
  - `completed` → handled and closed

---

## Done

When all steps complete, summarise what was created:

```
✓ config.yaml        projects/<slug>/config.yaml
✓ 15 docs            projects/<slug>/docs/  (populated from interview)
✓ index entry        projects/index.yaml
✓ Q&A bucket         created in Planner (bucket ID saved to config.yaml)
✓ connection         validated (N tasks found)
```

Ask if the user wants to fill in any of the documents now or come back later.

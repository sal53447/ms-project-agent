---
name: ms-project-orchestrator
description: Run the full project management cycle for an MS Planner-backed project. Use this skill whenever the user wants to manage, check on, run a cycle for, or execute instructions on an existing project — even if they phrase it as "run the orchestrator", "manage project X", "check on project X", "execute the PM instructions", "run a PM cycle", "what needs to happen on project X", or "kick off the agents for project X". This is the main operational skill — it coordinates the PM Agent, Executor agents, and Q&A communication loop. Do NOT use for onboarding new projects (use ms-project-onboarding instead).
---

# MS Project Orchestrator

This skill runs the full project management cycle for an onboarded MS Planner project. It coordinates three roles:

- **You (the Orchestrator)** — load config, read Q&A, invoke agents, log results
- **PM Agent** (`pm-planner-agent`) — reads all docs + Planner state, produces `instructions.md`
- **Executor Agents** (`executor-agent`) — each executes one instruction from `instructions.md`

The Orchestrator does not make project decisions itself. It coordinates: reads state, hands context to the PM Agent, acts on the resulting instructions by spawning Executor agents, and manages the Q&A communication loop with humans.

---

## Before You Start

You need the **project slug**. If the user doesn't give one, check `projects/index.yaml` for the list of registered projects and ask which one.

---

## Run Sequence

Follow these steps in order. Do not skip steps.

### Step 1 — Load project config

Read `projects/<slug>/config.yaml`. Extract:
- `project.plan_id`
- `project.group_id`
- `project.bucket_ids` (including `bucket_ids.qa` if present)

If config.yaml doesn't exist, stop and tell the user to onboard the project first (using the `ms-project-onboarding` skill).

### Step 2 — Snapshot diff (detect human changes since last run)

Run a diff against the existing snapshot to detect what changed in Planner since the last Orchestrator run:

```bash
uv run planner snapshot diff --plan-id <plan_id> --project-dir projects/<slug>
```

Capture the JSON output. There are two possible outcomes:

**No prior snapshot** (`"status": "initial_baseline"` in output): This is the first run. The current Planner state will become the baseline. Note this in your context — the PM Agent will see the full task list but no delta.

**Delta output**: A JSON object with `completed`, `progressed`, `added`, `removed`, and `changed` arrays. Pass this to the PM Agent in Step 5 so it can react to human activity.

Store the delta output (or the initial-baseline note) as `snapshot_delta` — you will use it in Step 5.

### Step 3 — Ensure Q&A bucket exists

```bash
uv run planner buckets list --plan-id <plan_id>
```

Check if a bucket named "Q&A" exists. If not, create it:
```bash
uv run planner buckets create --plan-id <plan_id> --name "Q&A"
```

If you had to create it or if `bucket_ids.qa` is missing from config.yaml, save the bucket ID back to config.yaml under `project.bucket_ids.qa`.

### Step 4 — Read Q&A bucket

List all tasks in the plan and filter to the Q&A bucket:
```bash
uv run planner tasks list --plan-id <plan_id>
```

Filter results to only tasks whose bucket ID matches `bucket_ids.qa`.

### Step 5 — Classify Q&A items

Separate Q&A tasks by status:

| Task status | Classification | What you do |
|---|---|---|
| `not_started` | Documentation / pending | Pass to PM Agent as **context only** — not an active request |
| `in_progress` | **Active request** | Pass to PM Agent as a **request to fulfil** |
| `completed` | Already handled | Skip entirely |

**Critical rule:** You never promote a task to `in_progress` — only a human does that. A task at `not_started` is waiting for the human to decide; you treat it as background context.

Build two lists:
- `qa_context`: all `not_started` items (background knowledge)
- `qa_requests`: all `in_progress` items (things to act on)

### Step 6 — Run the PM Agent

Invoke the **`pm-planner-agent`** using the Agent tool with `subagent_type: "pm-planner-agent"`.

The PM Agent needs the full context package in its prompt:
- The project slug
- Path to config.yaml
- The plan_id
- The `qa_context` list (Q&A not_started tasks — for background)
- The `qa_requests` list (Q&A in_progress tasks — for action)
- The `snapshot_delta` from Step 2 (JSON — human activity since last run, or "initial_baseline")
- Any specific concerns the user raised

The PM Agent will:
1. Read all project docs under `projects/<slug>/docs/`
2. Read the current Planner state via CLI
3. Perform a structured assessment (progress, risks, blockers, gaps, health)
4. Write `projects/<slug>/instructions.md` with a YAML block of instructions

Wait for the PM Agent to complete before proceeding.

### Step 7 — Parse instructions.md

Read `projects/<slug>/instructions.md` and parse the YAML `instructions` block.

Split instructions into two groups:
- **`ask_human`** instructions → handle in Step 8
- **Action instructions** (`create_task`, `update_task`, `create_bucket`, `flag_risk`, `update_milestone`, `add_checklist_item`, `add_note`) → handle in Step 9

### Step 8 — Handle ask_human instructions

For each `ask_human` instruction, create a task in the Q&A bucket:

```bash
uv run planner tasks create \
  --plan-id <plan_id> \
  --bucket-id <qa_bucket_id> \
  --title "[Q] <question>"
```

The task starts as `not_started`. The human answers by editing the description and setting status to `in_progress`. On the next Orchestrator run, that answer becomes an active Q&A request.

### Step 9 — Spawn Executor agents

For each action instruction (not `ask_human`), spawn one **`executor-agent`** using the Agent tool with `subagent_type: "executor-agent"`.

**All Executors run in parallel** — spawn them all in the same message using multiple Agent tool calls.

Each Executor's prompt must include:
- The single instruction YAML block (copy it verbatim)
- The project slug
- The path to config.yaml: `projects/<slug>/config.yaml`
- The instruction ID (e.g., `INS-001`)

Example prompt for an Executor:

```
Execute this instruction for the "test-agent" project.

Project config: projects/test-agent/config.yaml

Instruction:
  id: "INS-001"
  type: create_task
  priority: high
  bucket: "Phase 1"
  title: "Research Azure Bot Service requirements"
  description: "Investigate what Azure services and permissions are needed for a Teams bot."
  assigned_to: ""
  due_date: "2026-05-01"
  reason: "Phase 2 blocker — dependencies unknown."

Read config.yaml for plan_id and bucket_ids, execute the instruction, and report the result as a YAML block with instruction_id, status (done/failed/skipped), and detail.
```

Wait for all Executors to complete.

### Step 10 — Write execution log

After all Executors finish, collect their results and append to `projects/<slug>/execution-log.md`.

Format:

```markdown
## Run — <ISO timestamp>

Triggered by: manual
Instructions processed: <N>

| Instruction | Type | Status | Detail |
|---|---|---|---|
| INS-001 | create_task | done | Task created: task-id-xyz |
| INS-002 | update_task | done | Due date updated |
| INS-003 | flag_risk | done | Risk appended to risk-register.md |
| INS-005 | ask_human | skipped | Q&A task created instead |
```

If the file doesn't exist yet, create it with a `# Execution Log` heading.

### Step 11 — Take new snapshot

Archive the current snapshot and capture a fresh one reflecting the post-execution state:

```bash
uv run planner snapshot take --plan-id <plan_id> --project-dir projects/<slug>
```

This archives the pre-run snapshot to `snapshot-archive/` and writes the new current state to `planner-snapshot.json`. The next Orchestrator run will diff against this snapshot.

### Step 12 — Close completed Q&A tasks

For each `in_progress` Q&A task that was fully addressed by the PM Agent's instructions and successfully executed:

```bash
uv run planner tasks update <task_id> --progress 100
```

A Q&A task is considered addressed when:
- It was an answer to a previous `ask_human` question and the PM Agent incorporated it
- It was a request and at least one Executor instruction directly corresponds to it

If unclear whether a request was fully addressed, leave it as `in_progress` for the next run.

### Step 13 — Report to the user

Summarise what happened:
- PM Agent health rating and key findings
- How many instructions were generated
- How many succeeded / failed / were ask_human
- Any Q&A tasks created for the human
- Any Q&A tasks closed
- Summary of human changes detected in the snapshot delta (if any)

---

## Constraints — Never Violate These

1. **The Orchestrator never makes project management decisions** — that is the PM Agent's job
2. **The Orchestrator never promotes Q&A tasks to `in_progress`** — only humans do that
3. **One Executor per instruction** — never batch multiple instructions into one Executor
4. **If `instructions.md` is missing or malformed after the PM Agent runs, stop and report the error** — do not attempt to infer instructions
5. **Always use the `pm-planner-agent` for assessment** — do not assess project health yourself
6. **Always use `executor-agent` for execution** — do not execute instructions yourself

---

## Q&A Lifecycle Reference

```
Human creates Q&A task (not_started)
  → Orchestrator reads it as documentation context
  
Human sets status to in_progress
  → Orchestrator passes it to PM Agent as an active request
  → PM Agent generates instructions to fulfil it
  → Executors carry out instructions
  → Orchestrator marks Q&A task as completed

PM Agent needs info → ask_human instruction
  → Orchestrator creates Q&A task (not_started) with question
  → Human answers in description, sets to in_progress
  → Next run: Orchestrator passes answer to PM Agent
```

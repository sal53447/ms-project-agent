# Orchestrator Agent — Specification

## Role

The main agent operates through **two distinct skills**, each representing a different mode of operation:

| Skill | When used | What it does |
|---|---|---|
| `ms-project-onboarding` | First time, for a new project | Guides the agent through creating config.yaml, project documents, Q&A bucket, and registering the project |
| `ms-project-orchestrator` | All subsequent runs | Puts the agent in the Orchestrator role: checks Q&A, runs the PM Agent, spawns Executors, manages the project lifecycle |

This document specifies **`ms-project-orchestrator`** — the ongoing management skill. For onboarding, see `skills/ms-project-onboarding/SKILL.md`.

The Orchestrator does not make project decisions itself. It coordinates: reads state, hands context to the PM Agent, acts on the resulting instructions by spawning Executor agents, and manages the Q&A communication loop with humans.

---

## Trigger

Invoked manually for now:
```bash
uv run planner orchestrate --project <project-slug>
```

Future: schedulable via cron (daily, weekly, or event-driven).

---

## Run Sequence

Each run follows this sequence in order:

```
1. Load project config
2. Check & ensure Q&A bucket exists
3. Read Q&A bucket — collect human messages
4. Separate Q&A items into: active requests vs. documentation
5. Run PM Agent with full context (docs + Planner state + Q&A context)
6. Parse instructions.md
7. Handle ask_human instructions → create Q&A tasks
8. Spawn Executor agents for all action instructions (in parallel)
9. Wait for Executors to complete
10. Write execution-log.md
11. Mark completed Q&A tasks as done
```

---

## Step 1 — Load project config

Read `projects/<slug>/config.yaml`. Extract:
- `project.plan_id`
- `project.group_id`
- `project.bucket_ids` (including `bucket_ids.qa`)

---

## Step 2 — Ensure Q&A bucket exists

```bash
uv run planner buckets list --plan-id <plan_id>
```

If a bucket named `Q&A` is not found, create it:
```bash
uv run planner buckets create --plan-id <plan_id> --name "Q&A"
```

Save the bucket ID to `config.yaml` under `project.bucket_ids.qa` if not already stored.

---

## Step 3 — Read Q&A bucket

```bash
uv run planner tasks list --plan-id <plan_id>
# Filter results to bucket_ids.qa
```

Read every task in the Q&A bucket. Each task has:
- **Title** — the subject of the message (request or question)
- **Description** — the full content
- **Status** — controls whether it is acted on

---

## Step 4 — Classify Q&A items

| Task status | Classification | What the Orchestrator does |
|---|---|---|
| `not_started` | Documentation / pending | Passes to PM Agent as context only — not as an active request |
| `in_progress` | **Active request** | Passes to PM Agent as a request to fulfil |
| `completed` | Handled | Skips — already processed |

**Active requests** are human-approved actions or answers. The human sets a task to `in_progress` when they want the system to act on it. The Orchestrator never promotes a task to `in_progress` on its own — only a human does that.

The PM Agent receives two separate lists:
- `qa_context`: all not_started items (background knowledge)
- `qa_requests`: all in_progress items (things to act on)

---

## Step 5 — Run PM Agent

Invoke the PM Agent with the full context package:

```
Input to PM Agent:
- projects/<slug>/docs/  (all project documents)
- Current Planner task list (read via CLI)
- qa_context: list of Q&A not_started tasks
- qa_requests: list of Q&A in_progress tasks
```

The PM Agent reads everything, evaluates the project situation, and writes `projects/<slug>/instructions.md`.

---

## Step 6 — Parse instructions.md

Read and parse the YAML block from `projects/<slug>/instructions.md`.

Split instructions into two groups:
- **`ask_human`** instructions → handle in Step 7
- **Action instructions** (`create_task`, `update_task`, etc.) → handle in Step 8

---

## Step 7 — Handle ask_human instructions

When the PM Agent needs information from a human, it generates an `ask_human` instruction:

```yaml
- id: "INS-005"
  type: ask_human
  priority: high
  question: "Which team member is responsible for the backend API milestone?"
  context: "M3 is due in 2 weeks and no task owner is assigned."
```

For each `ask_human` instruction, the Orchestrator creates a task in the Q&A bucket:

```bash
uv run planner tasks create \
  --plan-id <plan_id> \
  --bucket-id <qa_bucket_id> \
  --title "[Q] <question>" \
  --description "Context: <context>\n\nPlease answer in this task's description and set status to In Progress when ready."
```

The task starts as `not_started`. The human answers by editing the description and setting status to `in_progress`. On the next Orchestrator run, that answer becomes an active Q&A request and is passed to the PM Agent.

---

## Step 8 — Spawn Executor agents

For each action instruction (not `ask_human`), spawn one Executor agent. All Executors run **in parallel**.

Each Executor receives:
- The single instruction YAML block
- Path to `config.yaml`
- The instruction ID

The Orchestrator waits for all Executors to complete before proceeding.

---

## Step 9 — Write execution log

After all Executors finish, collect their results and append to `projects/<slug>/execution-log.md`:

```yaml
run:
  timestamp: "<ISO>"
  triggered_by: "manual"
  instructions_processed: 5
  results:
    - instruction_id: "INS-001"
      status: done
      detail: "Task created: task-id-xyz"
    - instruction_id: "INS-002"
      status: failed
      detail: "tasks update: 404 task not found"
    - instruction_id: "INS-005"
      status: skipped
      detail: "ask_human — Q&A task created instead"
```

---

## Step 10 — Close completed Q&A tasks

For each `in_progress` Q&A task that was fully addressed by the PM Agent's instructions, update its status to `completed`:

```bash
uv run planner tasks update --task-id <id> --status completed
```

A Q&A task is considered addressed when:
- It was an answer to a previous `ask_human` question and the PM Agent incorporated it
- It was a request and at least one Executor instruction directly corresponds to it

If unclear whether a request was fully addressed, leave it as `in_progress` for the next run.

---

## Q&A Lifecycle Summary

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

---

## Constraints

- The Orchestrator never makes project management decisions — that is the PM Agent's job
- The Orchestrator never promotes Q&A tasks to `in_progress` — only humans do that
- The Orchestrator spawns one Executor per instruction — never batches instructions into one Executor
- If `instructions.md` is missing or malformed, the Orchestrator stops and logs an error — it does not attempt to infer instructions

---

## Future Extensions

- Schedule-based invocation (cron)
- Human approval gate: hold Executors until a human reviews `instructions.md`
- Multi-project orchestration (loop over `projects/index.yaml`)
- Slack / Teams notification when Q&A tasks are created by the agent

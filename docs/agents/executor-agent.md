# Executor Agent — Specification

## Role

A small, fast, single-purpose agent assigned to carry out **one instruction** from `instructions.md`. It knows only the CLI tools needed to create and update tasks in MS Planner — nothing more. It does not read project documents, does not make decisions, and does not write `instructions.md`.

Designed to run on a cheap, fast model (e.g. **claude-haiku-4-5**) because its job is mechanical: parse one instruction, run one or a few CLI commands, report done.

Many Executors can run **in parallel**, each handling a different instruction simultaneously.

---

## Trigger

Spawned by the **Orchestrator**. Each Executor receives:

1. A single instruction block (one item from the `instructions` list in `instructions.md`)
2. The path to `projects/<slug>/config.yaml` (for connection details)
3. The instruction ID (e.g. `INS-001`) for reporting

The Orchestrator never sends more than one instruction per Executor.

---

## Inputs

| Input | Source |
|---|---|
| Single instruction (YAML block) | Parsed from `instructions.md` by the Orchestrator |
| `plan_id` | From `config.yaml` → `project.plan_id` |
| `bucket_ids` map | From `config.yaml` → `project.bucket_ids` |
| Instruction ID | Passed by the Orchestrator |

The Executor reads `config.yaml` itself to extract connection values. It reads nothing else.

---

## CLI Knowledge

The Executor knows only the following commands:

```bash
# Tasks
uv run planner tasks list --plan-id <plan_id>
uv run planner tasks create --plan-id <plan_id> --title <title> --bucket-id <id>
uv run planner tasks update --task-id <id> --<field> <value>

# Buckets
uv run planner buckets list --plan-id <plan_id>
uv run planner buckets create --plan-id <plan_id> --name <name>

# Checklist items
uv run planner tasks checklist add --task-id <id> --title <title>
```

It does not use `delete`, `groups`, `plans`, or any other commands.

---

## Execution Logic

For each instruction type, the Executor follows a fixed pattern:

### `create_task`
1. Look up `bucket_ids` in `config.yaml` to resolve bucket name → bucket ID
2. If bucket not in `bucket_ids`, run `buckets list` to find it by name
3. Run `tasks create` with title, bucket-id, and optionally due_date and assigned_to
4. If checklist items are specified, run `tasks checklist add` for each

### `update_task`
1. Use the `task_id` from the instruction directly
2. Run `tasks update --task-id <id> --<field> <value>`
3. If `task_id` is not provided, run `tasks list`, match by title, then update

### `create_bucket`
1. Run `buckets create --plan-id <plan_id> --name <name>`

### `flag_risk`
1. Append a new row to `projects/<slug>/docs/risk-register.md`
2. Format: `| <risk> | <impact> | <mitigation> | open |`

### `update_milestone`
1. Read `projects/<slug>/docs/milestones.md`
2. Find the milestone by name
3. Update the specified field (status, date, etc.)
4. Write the file back

### `add_checklist_item`
1. Run `tasks checklist add --task-id <id> --title <title>`

### `add_note`
1. Append a timestamped entry to the specified doc (`decision-log.md` or `issues-log.md`)

---

## Output

After completing its instruction, the Executor writes a result to a shared results file:

```yaml
- instruction_id: "INS-001"
  status: "done"            # done | failed | skipped
  detail: "Task created: <planner_task_id>"
  timestamp: "<ISO>"
```

Results are appended to `projects/<slug>/execution-log.md` so the Orchestrator and human can see what was done.

If a CLI command fails, the Executor sets `status: failed` and records the error in `detail`. It does not retry or attempt workarounds — it reports and stops.

---

## Constraints

- **One instruction per Executor** — the Orchestrator spawns a separate Executor per instruction
- **No decision-making** — if the instruction is ambiguous or the CLI call fails, the Executor reports failure; it does not invent alternatives
- **No access to PM logic** — the Executor does not read project documents (except the specific doc files for `flag_risk`, `update_milestone`, `add_note` instructions)
- **No delete commands** — Executors cannot delete tasks, buckets, or any Planner resource
- **Model**: claude-haiku-4-5 (fast and cheap; no extended thinking needed)

---

## Example

Given this instruction from the Orchestrator:

```yaml
- id: "INS-001"
  type: create_task
  priority: high
  bucket: "Sprint"
  title: "Define acceptance criteria for login feature"
  description: "Requirements doc lists login as P1 but no tasks exist for it."
  assigned_to: ""
  due_date: "2026-05-15"
  reason: "Gap between requirements and current task list."
```

The Executor:
1. Reads `config.yaml` → finds `bucket_ids.sprint: "bucket_id_2"`
2. Runs: `uv run planner tasks create --plan-id plan-abc123 --title "Define acceptance criteria for login feature" --bucket-id bucket_id_2`
3. Appends to `execution-log.md`:
```yaml
- instruction_id: "INS-001"
  status: "done"
  detail: "Task created: task-id-xyz"
  timestamp: "2026-04-14T21:15:00Z"
```

# MS Planner Agent — Design Spec

## Overview

A Python application that connects to Microsoft Planner via the Microsoft Graph API using app-only (client credentials) authentication. Provides both a CLI for manual management and a foundation for future automated workflows.

## Authentication

- **Flow:** OAuth 2.0 client credentials (app-only, no signed-in user)
- **Library:** `msal` (`ConfidentialClientApplication`)
- **Scope:** `https://graph.microsoft.com/.default`
- **Permissions required:** `Tasks.ReadWrite.All`, `Group.Read.All`, `User.Read.All` (application)
- **Token caching:** In-memory via MSAL (handles refresh automatically)
- **Config:** `TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET` from `.env` or environment variables

## Project Structure

```
ms-project-agent/
├── pyproject.toml
├── .env.example              # template for credentials
├── src/
│   └── ms_planner/
│       ├── __init__.py
│       ├── auth.py            # MSAL client credentials auth
│       ├── client.py          # core GraphClient (httpx + auth + etag handling)
│       ├── models/            # Pydantic models
│       │   ├── __init__.py
│       │   ├── plan.py
│       │   ├── task.py
│       │   ├── bucket.py
│       │   └── assignment.py
│       ├── services/          # business logic per resource
│       │   ├── __init__.py
│       │   ├── plans.py
│       │   ├── tasks.py
│       │   └── buckets.py
│       └── cli/               # Typer CLI commands
│           ├── __init__.py
│           ├── main.py
│           ├── plans.py
│           ├── tasks.py
│           └── buckets.py
├── tests/
│   └── ...
└── docs/
    ├── azure-setup.md         # App registration guide
    └── superpowers/specs/     # Design specs
```

## Tech Stack

- **Package manager:** `uv` with `pyproject.toml`
- **HTTP client:** `httpx` (async)
- **Auth:** `msal`
- **Data models:** `pydantic`
- **CLI:** `typer`
- **Output formatting:** `rich`
- **Config:** `python-dotenv`

## Core Components

### Auth (`auth.py`)

- `get_token() -> str` — acquires/refreshes an access token via client credentials flow
- Uses `msal.ConfidentialClientApplication`
- Token cached in memory; MSAL handles expiry/refresh

### GraphClient (`client.py`)

Async class wrapping `httpx.AsyncClient`.

- Base URL: `https://graph.microsoft.com/v1.0`
- Automatically injects `Authorization: Bearer {token}` header
- ETag management: stores ETags from GET responses, sends `If-Match` on PATCH/DELETE
- Retry logic for 409 (conflict) and 429 (throttling) with backoff
- Methods: `get()`, `post()`, `patch()`, `delete()` — return parsed JSON
- Raises typed exceptions for common Graph errors

### Services (`services/`)

Each service is an async class that takes a `GraphClient` instance.

**PlanService:**
- `list(group_id)` — list plans for a group
- `get(plan_id)` — get a single plan
- `create(group_id, title)` — create a plan in a group
- `update(plan_id, ...)` — update plan properties
- `delete(plan_id)` — delete a plan

**TaskService:**
- `list(plan_id)` — list tasks in a plan
- `get(task_id)` — get a single task
- `get_details(task_id)` — get task details (description, checklist, attachments)
- `create(plan_id, title, assignments, ...)` — create a task
- `update(task_id, ...)` — update task properties
- `update_details(task_id, ...)` — update checklist, attachments, description
- `delete(task_id)` — delete a task
- `list_my_tasks(user_id)` — list tasks assigned to a user

**BucketService:**
- `list(plan_id)` — list buckets in a plan
- `create(plan_id, name)` — create a bucket
- `update(bucket_id, ...)` — update bucket properties
- `delete(bucket_id)` — delete a bucket

### Pydantic Models (`models/`)

Data classes for API request/response mapping:

- `Plan` — id, title, owner (group ID), created datetime, container
- `Task` — id, plan_id, bucket_id, title, assignments, progress, priority, start/due dates, order hint
- `TaskDetails` — description, checklist items, attachments (references)
- `Bucket` — id, plan_id, name, order hint
- `Assignment` — user_id, order hint

## CLI Design

Entry point: `planner` (installed via `pyproject.toml` script entry).

```
planner plans list --group-id <id>
planner plans get <plan-id>
planner plans create --group-id <id> --title "Q3 Sprint"
planner plans delete <plan-id>

planner buckets list --plan-id <id>
planner buckets create --plan-id <id> --name "To Do"
planner buckets delete <bucket-id>

planner tasks list --plan-id <id>
planner tasks get <task-id>
planner tasks create --plan-id <id> --title "Fix bug" --bucket-id <id> --assign <user-id>
planner tasks update <task-id> --progress completed --priority 3
planner tasks delete <task-id>
planner tasks details <task-id>

planner tasks checklist add <task-id> --item "Review PR"
planner tasks checklist remove <task-id> --item-id <id>

planner tasks attach <task-id> --url "https://..." --alias "Design doc"
```

**Output:** Clean tables via `rich` by default. `--json` flag for raw JSON output.

**Config:** Reads from `.env` or environment variables. Optional `--env-file` flag.

## Error Handling

### Custom Exceptions

- `PlannerNotFoundError` — 404
- `PlannerForbiddenError` — 403
- `PlannerConflictError` — 409/412 (after retry exhausted)
- `PlannerThrottledError` — 429

### ETag Concurrency

1. Every GET stores `@odata.etag` from the response
2. PATCH/DELETE automatically attaches the stored ETag via `If-Match`
3. On 409/412, re-fetch the resource, get new ETag, retry once

### Throttling

On 429 responses, read `Retry-After` header and wait. Max 3 retries.

### CLI Error Display

Services raise exceptions; CLI catches and displays user-friendly messages via `rich`. No raw tracebacks.

## Future Extensibility

The architecture is designed to support automated workflows later:

- **Services are async** — callable from CLI (via `asyncio.run`) or from a long-running service (FastAPI, scheduler, event loop)
- **No CLI coupling** — all logic lives in services. Any future trigger (webhook, cron, message queue) imports the same services
- **Config is environment-based** — works the same locally or deployed as a container

No service framework scaffolding is included now — just the clean separation that makes it trivial to add later.

## Graph API Endpoints Reference

| Operation | Method | Endpoint |
|---|---|---|
| List plans for group | GET | `/groups/{group-id}/planner/plans` |
| Get plan | GET | `/planner/plans/{plan-id}` |
| Create plan | POST | `/planner/plans` |
| Update plan | PATCH | `/planner/plans/{plan-id}` |
| Delete plan | DELETE | `/planner/plans/{plan-id}` |
| List tasks in plan | GET | `/planner/plans/{plan-id}/tasks` |
| Get task | GET | `/planner/tasks/{task-id}` |
| Get task details | GET | `/planner/tasks/{task-id}/details` |
| Create task | POST | `/planner/tasks` |
| Update task | PATCH | `/planner/tasks/{task-id}` |
| Update task details | PATCH | `/planner/tasks/{task-id}/details` |
| Delete task | DELETE | `/planner/tasks/{task-id}` |
| List user tasks | GET | `/users/{user-id}/planner/tasks` |
| List buckets in plan | GET | `/planner/plans/{plan-id}/buckets` |
| Create bucket | POST | `/planner/buckets` |
| Update bucket | PATCH | `/planner/buckets/{bucket-id}` |
| Delete bucket | DELETE | `/planner/buckets/{bucket-id}` |

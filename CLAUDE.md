# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MS Planner Agent — a Python CLI + library for managing Microsoft Planner via the Microsoft Graph API using app-only (client credentials) authentication. Also includes a multi-agent project management system that reads Planner state, assesses project health, and dispatches actions.

## Common Commands

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest -v

# Run a single test file
uv run pytest tests/test_services/test_tasks.py -v

# Run a single test by name
uv run pytest -k "test_list_tasks" -v

# Run CLI
uv run planner --help
uv run planner groups list
uv run planner plans list --group-id <id>
uv run planner tasks list --plan-id <id>
uv run planner buckets list --plan-id <id>
```

## Microsoft Planner Hierarchy

M365 Group (SharePoint site / email group / Teams team) → Plan → Bucket → Task → Checklist items, attachments. To find a plan, first identify its parent Group via `planner groups list`. The tenant has 274+ groups; pagination is required.

## Architecture

- **Layered design:** `auth.py` → `GraphClient` (`client.py`) → services (`services/`) → CLI (`cli/`)
- Services are **async** — CLI bridges with `asyncio.run_until_complete()`
- GraphClient handles **ETag concurrency** (If-Match headers on PATCH/DELETE) and **retry** (429 throttling with Retry-After, 409 conflicts)
- CLI commands are thin wrappers that call services and format output with rich tables or `--json`
- Custom exceptions in `exceptions.py` map to HTTP status codes: `PlannerNotFoundError` (404), `PlannerForbiddenError` (403), `PlannerConflictError` (409/412), `PlannerThrottledError` (429)

## Multi-Agent System

Three agent roles coordinate project management (specs in `docs/agents/`):

| Agent | Role | Model | Writes to |
|---|---|---|---|
| **Orchestrator** | Coordinates runs: loads config, reads Q&A bucket, invokes PM Agent, spawns Executors | — | `execution-log.md` |
| **PM Agent** | Senior PM that reads all project docs + Planner state, assesses health, selects methodology | sonnet | `instructions.md` (YAML) |
| **Executor** | Single-purpose: executes one instruction via CLI commands | haiku | Planner tasks + project docs |

Flow: Orchestrator → PM Agent produces `instructions.md` → Orchestrator parses → spawns parallel Executors → each runs one instruction.

The PM Agent definition lives at `.claude/agents/pm-planner-agent.md`. Project onboarding skill at `skills/ms-project-onboarding/SKILL.md`.

## Project Management Structure

Each managed project lives under `projects/<slug>/` with:
- `config.yaml` — plan_id, group_id, bucket mappings, agent settings (minimum: plan_id + group_id)
- `docs/` — project-definition, milestones, risk-register, issues-log, requirements, wbs, dependencies, stakeholders, raci, budget, decision-log, change-requests, lessons-learned, meeting-notes
- `instructions.md` — PM Agent output consumed by Orchestrator
- `execution-log.md` — results of Executor runs

Projects are registered in `projects/index.yaml`.

**Q&A bucket** in Planner serves as human-agent communication: task status controls flow (`not_started` = context, `in_progress` = act on it, `completed` = handled).

## Testing Patterns

- **TDD** — tests written before implementation
- Services tested with `AsyncMock(spec=GraphClient)` via `mock_client` fixture in `tests/conftest.py`
- GraphClient tested with `respx` (httpx mock transport)
- CLI tested with `typer.testing.CliRunner`, mocking `_get_*_service()` factories
- pytest-asyncio with `asyncio_mode = "auto"` — no need for `@pytest.mark.asyncio`

## Key Conventions

- All service methods are async
- Snake_case in Python, camelCase mapped via Pydantic aliases for Graph API
- CLI entry point: `ms_planner.cli.main:run` (wraps typer app with error handling)
- Graph API pagination: always follow `@odata.nextLink` — the tenant has more entities than a single page returns

## Configuration

Requires `.env` file (or env vars): `TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`. See `docs/azure-setup.md` for Azure app registration setup (needs `Tasks.ReadWrite.All`, `Group.Read.All`, `User.Read.All` application permissions with admin consent).

# CLAUDE.md

## Project Overview

MS Planner Agent — a Python CLI + library for managing Microsoft Planner via the Microsoft Graph API using app-only (client credentials) authentication.

## Tech Stack

- **Python 3.11+** with `uv` package manager
- **httpx** (async HTTP client), **msal** (auth), **pydantic** (models), **typer** + **rich** (CLI)
- **pytest** + **pytest-asyncio** + **respx** (testing)

## Project Structure

```
src/ms_planner/
├── auth.py          # MSAL client credentials token acquisition
├── client.py        # Async GraphClient (ETag, retry, error mapping)
├── config.py        # Settings from env vars / .env (pydantic-settings)
├── exceptions.py    # PlannerError hierarchy (404, 403, 409, 429)
├── models/          # Pydantic models (Plan, Task, Bucket, etc.)
├── services/        # Async CRUD services (PlanService, TaskService, BucketService)
└── cli/             # Typer CLI commands (plans, buckets, tasks)
```

## Common Commands

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest -v

# Run CLI
uv run planner --help
uv run planner plans list --group-id <id>
uv run planner tasks list --plan-id <id>
```

## Architecture

- **Layered design:** auth → GraphClient → services → CLI
- Services are **async** — CLI bridges with `asyncio.run_until_complete()`
- GraphClient handles **ETag concurrency** (If-Match headers) and **retry** (429 throttling, 409 conflicts)
- CLI commands are thin wrappers that call services and format output with rich tables or `--json`

## Testing Patterns

- **TDD** — tests written before implementation
- Services tested with `AsyncMock(spec=GraphClient)` via `mock_client` fixture in `conftest.py`
- GraphClient tested with `respx` (httpx mock)
- CLI tested with `typer.testing.CliRunner`, mocking `_get_*_service()` factories

## Configuration

Requires `.env` file (or env vars): `TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`

See `docs/azure-setup.md` for Azure app registration instructions.

## Key Conventions

- All service methods are async
- Snake_case in Python, camelCase mapped via Pydantic aliases for Graph API
- Custom exceptions map to HTTP status codes (403, 404, 409/412, 429)
- CLI entry point is `ms_planner.cli.main:run` (wraps typer app with error handling)

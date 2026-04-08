# MS Planner Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI + library for managing Microsoft Planner via the Graph API using app-only authentication.

**Architecture:** A layered design with auth → HTTP client → services → CLI. Auth uses MSAL client credentials. An async `GraphClient` wraps `httpx` with ETag/retry handling. Services provide typed CRUD methods per resource. Typer CLI calls services and renders output with `rich`.

**Tech Stack:** Python 3.11+, `uv`, `httpx`, `msal`, `pydantic`, `typer`, `rich`, `python-dotenv`, `pytest`, `pytest-asyncio`, `respx`

---

## File Map

| File | Responsibility |
|---|---|
| `pyproject.toml` | Project metadata, dependencies, script entry point |
| `.gitignore` | Ignore `.env`, `__pycache__`, `.venv`, etc. |
| `.env.example` | Template for credentials |
| `src/ms_planner/__init__.py` | Package root |
| `src/ms_planner/config.py` | Load settings from env vars / `.env` |
| `src/ms_planner/exceptions.py` | Custom exception classes |
| `src/ms_planner/auth.py` | MSAL token acquisition |
| `src/ms_planner/client.py` | Async GraphClient with ETag + retry |
| `src/ms_planner/models/__init__.py` | Re-export all models |
| `src/ms_planner/models/plan.py` | Plan pydantic model |
| `src/ms_planner/models/bucket.py` | Bucket pydantic model |
| `src/ms_planner/models/task.py` | Task + TaskDetails pydantic models |
| `src/ms_planner/models/assignment.py` | Assignment pydantic model |
| `src/ms_planner/services/__init__.py` | Re-export all services |
| `src/ms_planner/services/plans.py` | PlanService CRUD |
| `src/ms_planner/services/buckets.py` | BucketService CRUD |
| `src/ms_planner/services/tasks.py` | TaskService CRUD + details |
| `src/ms_planner/cli/__init__.py` | Empty |
| `src/ms_planner/cli/main.py` | Typer app entry, sub-command registration |
| `src/ms_planner/cli/plans.py` | CLI plan commands |
| `src/ms_planner/cli/buckets.py` | CLI bucket commands |
| `src/ms_planner/cli/tasks.py` | CLI task commands |
| `tests/conftest.py` | Shared fixtures (mock GraphClient, respx mocks) |
| `tests/test_config.py` | Config loading tests |
| `tests/test_auth.py` | Auth token tests |
| `tests/test_client.py` | GraphClient tests (ETag, retry, errors) |
| `tests/test_models.py` | Model parsing tests |
| `tests/test_services/test_plans.py` | PlanService tests |
| `tests/test_services/test_buckets.py` | BucketService tests |
| `tests/test_services/test_tasks.py` | TaskService tests |
| `tests/test_cli/test_plans.py` | CLI plan command tests |
| `tests/test_cli/test_buckets.py` | CLI bucket command tests |
| `tests/test_cli/test_tasks.py` | CLI task command tests |

---

### Task 1: Project scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `src/ms_planner/__init__.py`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "ms-planner-agent"
version = "0.1.0"
description = "Microsoft Planner management via Graph API"
requires-python = ">=3.11"
dependencies = [
    "httpx>=0.27",
    "msal>=1.28",
    "pydantic>=2.7",
    "typer>=0.12",
    "rich>=13.7",
    "python-dotenv>=1.0",
]

[project.scripts]
planner = "ms_planner.cli.main:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/ms_planner"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[dependency-groups]
dev = [
    "pytest>=8.2",
    "pytest-asyncio>=0.23",
    "respx>=0.21",
]
```

- [ ] **Step 2: Create `.gitignore`**

```
.env
.venv/
__pycache__/
*.pyc
dist/
*.egg-info/
.pytest_cache/
```

- [ ] **Step 3: Create `.env.example`**

```
TENANT_ID=your-tenant-id
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
```

- [ ] **Step 4: Create `src/ms_planner/__init__.py`**

```python
"""MS Planner Agent — Microsoft Planner management via Graph API."""
```

- [ ] **Step 5: Initialize uv and install dependencies**

Run: `cd /home/pouyan/projects/ms-project-agent && uv sync`
Expected: Dependencies installed, `.venv` created, lock file generated.

- [ ] **Step 6: Verify Python runs**

Run: `uv run python -c "import ms_planner; print('OK')"`
Expected: `OK`

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml .gitignore .env.example src/ms_planner/__init__.py uv.lock
git commit -m "feat: project scaffolding with uv and dependencies"
```

---

### Task 2: Config and exceptions

**Files:**
- Create: `src/ms_planner/config.py`
- Create: `src/ms_planner/exceptions.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write the failing test for config**

```python
# tests/test_config.py
import os
from ms_planner.config import Settings


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("TENANT_ID", "t-123")
    monkeypatch.setenv("CLIENT_ID", "c-456")
    monkeypatch.setenv("CLIENT_SECRET", "s-789")

    settings = Settings()
    assert settings.tenant_id == "t-123"
    assert settings.client_id == "c-456"
    assert settings.client_secret == "s-789"


def test_settings_missing_env_raises(monkeypatch):
    monkeypatch.delenv("TENANT_ID", raising=False)
    monkeypatch.delenv("CLIENT_ID", raising=False)
    monkeypatch.delenv("CLIENT_SECRET", raising=False)

    import pytest
    with pytest.raises(Exception):
        Settings()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'ms_planner.config'`

- [ ] **Step 3: Implement config**

```python
# src/ms_planner/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    tenant_id: str
    client_id: str
    client_secret: str
    graph_base_url: str = "https://graph.microsoft.com/v1.0"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
```

Note: This requires `pydantic-settings`. Add it to `pyproject.toml` dependencies:
```toml
"pydantic-settings>=2.3",
```
Then run: `uv sync`

- [ ] **Step 4: Implement exceptions**

```python
# src/ms_planner/exceptions.py
class PlannerError(Exception):
    """Base exception for Planner API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


class PlannerNotFoundError(PlannerError):
    """Resource not found (404)."""


class PlannerForbiddenError(PlannerError):
    """Access denied (403)."""


class PlannerConflictError(PlannerError):
    """ETag conflict after retry exhausted (409/412)."""


class PlannerThrottledError(PlannerError):
    """Rate limited after retries exhausted (429)."""
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_config.py -v`
Expected: 2 passed

- [ ] **Step 6: Commit**

```bash
git add src/ms_planner/config.py src/ms_planner/exceptions.py tests/test_config.py pyproject.toml uv.lock
git commit -m "feat: add config loading and custom exceptions"
```

---

### Task 3: Auth module

**Files:**
- Create: `src/ms_planner/auth.py`
- Create: `tests/test_auth.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_auth.py
from unittest.mock import MagicMock, patch
from ms_planner.auth import get_token
from ms_planner.config import Settings


def _make_settings() -> Settings:
    return Settings(
        tenant_id="t-123",
        client_id="c-456",
        client_secret="s-789",
    )


@patch("ms_planner.auth.msal.ConfidentialClientApplication")
def test_get_token_from_cache(mock_cca_cls):
    mock_app = MagicMock()
    mock_app.acquire_token_silent.return_value = {"access_token": "cached-token"}
    mock_cca_cls.return_value = mock_app

    token = get_token(_make_settings())
    assert token == "cached-token"
    mock_app.acquire_token_silent.assert_called_once()
    mock_app.acquire_token_for_client.assert_not_called()


@patch("ms_planner.auth.msal.ConfidentialClientApplication")
def test_get_token_acquires_new(mock_cca_cls):
    mock_app = MagicMock()
    mock_app.acquire_token_silent.return_value = None
    mock_app.acquire_token_for_client.return_value = {"access_token": "new-token"}
    mock_cca_cls.return_value = mock_app

    token = get_token(_make_settings())
    assert token == "new-token"


@patch("ms_planner.auth.msal.ConfidentialClientApplication")
def test_get_token_raises_on_error(mock_cca_cls):
    mock_app = MagicMock()
    mock_app.acquire_token_silent.return_value = None
    mock_app.acquire_token_for_client.return_value = {
        "error": "invalid_client",
        "error_description": "Bad credentials",
    }
    mock_cca_cls.return_value = mock_app

    import pytest
    with pytest.raises(RuntimeError, match="Bad credentials"):
        get_token(_make_settings())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_auth.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'ms_planner.auth'`

- [ ] **Step 3: Implement auth**

```python
# src/ms_planner/auth.py
import msal
from ms_planner.config import Settings

_SCOPE = ["https://graph.microsoft.com/.default"]

_app_cache: dict[str, msal.ConfidentialClientApplication] = {}


def _get_app(settings: Settings) -> msal.ConfidentialClientApplication:
    key = f"{settings.tenant_id}:{settings.client_id}"
    if key not in _app_cache:
        _app_cache[key] = msal.ConfidentialClientApplication(
            client_id=settings.client_id,
            client_credential=settings.client_secret,
            authority=f"https://login.microsoftonline.com/{settings.tenant_id}",
        )
    return _app_cache[key]


def get_token(settings: Settings) -> str:
    app = _get_app(settings)
    result = app.acquire_token_silent(_SCOPE, account=None)
    if not result:
        result = app.acquire_token_for_client(scopes=_SCOPE)
    if "access_token" in result:
        return result["access_token"]
    raise RuntimeError(
        result.get("error_description", result.get("error", "Unknown auth error"))
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_auth.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add src/ms_planner/auth.py tests/test_auth.py
git commit -m "feat: add MSAL client credentials auth"
```

---

### Task 4: GraphClient with ETag and retry

**Files:**
- Create: `src/ms_planner/client.py`
- Create: `tests/test_client.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_client.py
import pytest
import httpx
import respx
from ms_planner.client import GraphClient
from ms_planner.exceptions import (
    PlannerNotFoundError,
    PlannerForbiddenError,
    PlannerThrottledError,
)


@pytest.fixture
def client():
    return GraphClient(token_factory=lambda: "test-token")


@respx.mock
@pytest.mark.asyncio
async def test_get_returns_json(client):
    respx.get("https://graph.microsoft.com/v1.0/planner/plans/p1").mock(
        return_value=httpx.Response(
            200,
            json={"id": "p1", "title": "Test"},
            headers={"ETag": '"etag-1"'},
        )
    )
    data = await client.get("/planner/plans/p1")
    assert data["id"] == "p1"


@respx.mock
@pytest.mark.asyncio
async def test_get_stores_etag(client):
    respx.get("https://graph.microsoft.com/v1.0/planner/plans/p1").mock(
        return_value=httpx.Response(
            200,
            json={"id": "p1", "@odata.etag": '"etag-abc"'},
            headers={"ETag": '"etag-abc"'},
        )
    )
    await client.get("/planner/plans/p1")
    assert client.get_etag("/planner/plans/p1") == '"etag-abc"'


@respx.mock
@pytest.mark.asyncio
async def test_patch_sends_if_match(client):
    client.set_etag("/planner/plans/p1", '"etag-abc"')
    route = respx.patch("https://graph.microsoft.com/v1.0/planner/plans/p1").mock(
        return_value=httpx.Response(204)
    )
    await client.patch("/planner/plans/p1", json={"title": "Updated"})
    assert route.calls[0].request.headers["If-Match"] == '"etag-abc"'


@respx.mock
@pytest.mark.asyncio
async def test_get_raises_not_found(client):
    respx.get("https://graph.microsoft.com/v1.0/planner/plans/bad").mock(
        return_value=httpx.Response(404, json={"error": {"message": "Not found"}})
    )
    with pytest.raises(PlannerNotFoundError):
        await client.get("/planner/plans/bad")


@respx.mock
@pytest.mark.asyncio
async def test_get_raises_forbidden(client):
    respx.get("https://graph.microsoft.com/v1.0/planner/plans/p1").mock(
        return_value=httpx.Response(403, json={"error": {"message": "Forbidden"}})
    )
    with pytest.raises(PlannerForbiddenError):
        await client.get("/planner/plans/p1")


@respx.mock
@pytest.mark.asyncio
async def test_throttle_retries(client):
    route = respx.get("https://graph.microsoft.com/v1.0/planner/plans/p1")
    route.side_effect = [
        httpx.Response(429, headers={"Retry-After": "0"}),
        httpx.Response(200, json={"id": "p1"}),
    ]
    data = await client.get("/planner/plans/p1")
    assert data["id"] == "p1"
    assert route.call_count == 2


@respx.mock
@pytest.mark.asyncio
async def test_throttle_exhausted_raises(client):
    respx.get("https://graph.microsoft.com/v1.0/planner/plans/p1").mock(
        return_value=httpx.Response(429, headers={"Retry-After": "0"})
    )
    with pytest.raises(PlannerThrottledError):
        await client.get("/planner/plans/p1")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_client.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'ms_planner.client'`

- [ ] **Step 3: Implement GraphClient**

```python
# src/ms_planner/client.py
import asyncio
from collections.abc import Callable
from typing import Any

import httpx

from ms_planner.exceptions import (
    PlannerConflictError,
    PlannerForbiddenError,
    PlannerNotFoundError,
    PlannerThrottledError,
)

_BASE_URL = "https://graph.microsoft.com/v1.0"
_MAX_RETRIES = 3


class GraphClient:
    def __init__(self, token_factory: Callable[[], str]):
        self._token_factory = token_factory
        self._etags: dict[str, str] = {}
        self._http = httpx.AsyncClient(base_url=_BASE_URL, timeout=30.0)

    def get_etag(self, path: str) -> str | None:
        return self._etags.get(path)

    def set_etag(self, path: str, etag: str) -> None:
        self._etags[path] = etag

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token_factory()}"}

    def _store_etag(self, path: str, data: dict[str, Any]) -> None:
        etag = data.get("@odata.etag")
        if etag:
            self._etags[path] = etag

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        headers = self._auth_headers()

        if method in ("PATCH", "DELETE"):
            etag = self._etags.get(path)
            if etag:
                headers["If-Match"] = etag

        for attempt in range(_MAX_RETRIES):
            response = await self._http.request(
                method, path, json=json, headers=headers
            )

            if response.status_code == 429:
                if attempt < _MAX_RETRIES - 1:
                    retry_after = int(response.headers.get("Retry-After", "1"))
                    await asyncio.sleep(retry_after)
                    continue
                raise PlannerThrottledError(
                    "Rate limited after max retries", status_code=429
                )

            if response.status_code in (409, 412):
                if attempt < _MAX_RETRIES - 1:
                    await asyncio.sleep(0.5)
                    continue
                raise PlannerConflictError(
                    "ETag conflict after max retries",
                    status_code=response.status_code,
                )

            break

        if response.status_code == 403:
            msg = self._extract_error(response)
            raise PlannerForbiddenError(msg, status_code=403)

        if response.status_code == 404:
            msg = self._extract_error(response)
            raise PlannerNotFoundError(msg, status_code=404)

        if response.status_code >= 400:
            msg = self._extract_error(response)
            raise PlannerError(msg, status_code=response.status_code)

        if response.status_code == 204:
            return None

        data = response.json()
        if method == "GET":
            self._store_etag(path, data)
        return data

    @staticmethod
    def _extract_error(response: httpx.Response) -> str:
        try:
            body = response.json()
            return body.get("error", {}).get("message", response.text)
        except Exception:
            return response.text

    async def get(self, path: str) -> dict[str, Any]:
        result = await self._request("GET", path)
        return result  # type: ignore[return-value]

    async def post(self, path: str, json: dict[str, Any]) -> dict[str, Any]:
        result = await self._request("POST", path, json=json)
        return result  # type: ignore[return-value]

    async def patch(
        self, path: str, json: dict[str, Any]
    ) -> dict[str, Any] | None:
        return await self._request("PATCH", path, json=json)

    async def delete(self, path: str) -> None:
        await self._request("DELETE", path)

    async def close(self) -> None:
        await self._http.aclose()
```

Note: Fix the import in the `>= 400` catch — add `PlannerError` to the import from `exceptions.py`:

```python
from ms_planner.exceptions import (
    PlannerConflictError,
    PlannerError,
    PlannerForbiddenError,
    PlannerNotFoundError,
    PlannerThrottledError,
)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_client.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add src/ms_planner/client.py tests/test_client.py
git commit -m "feat: add async GraphClient with ETag and retry logic"
```

---

### Task 5: Pydantic models

**Files:**
- Create: `src/ms_planner/models/__init__.py`
- Create: `src/ms_planner/models/plan.py`
- Create: `src/ms_planner/models/bucket.py`
- Create: `src/ms_planner/models/task.py`
- Create: `src/ms_planner/models/assignment.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_models.py
from datetime import datetime
from ms_planner.models import Plan, Bucket, Task, TaskDetails, Assignment


def test_plan_from_api_response():
    data = {
        "id": "p1",
        "title": "Sprint 1",
        "owner": "group-abc",
        "createdDateTime": "2026-01-15T10:30:00Z",
        "container": {"containerId": "group-abc", "type": "group"},
        "@odata.etag": '"W/\"etag1\""',
    }
    plan = Plan.model_validate(data)
    assert plan.id == "p1"
    assert plan.title == "Sprint 1"
    assert plan.owner == "group-abc"
    assert isinstance(plan.created_date_time, datetime)


def test_bucket_from_api_response():
    data = {
        "id": "b1",
        "planId": "p1",
        "name": "To Do",
        "orderHint": "8585 ...",
    }
    bucket = Bucket.model_validate(data)
    assert bucket.id == "b1"
    assert bucket.plan_id == "p1"
    assert bucket.name == "To Do"


def test_task_from_api_response():
    data = {
        "id": "t1",
        "planId": "p1",
        "bucketId": "b1",
        "title": "Fix bug",
        "assignments": {
            "user-1": {"@odata.type": "#microsoft.graph.plannerAssignment", "orderHint": "8585"},
        },
        "percentComplete": 50,
        "priority": 3,
        "startDateTime": "2026-02-01T00:00:00Z",
        "dueDateTime": "2026-02-10T00:00:00Z",
        "orderHint": "8585",
    }
    task = Task.model_validate(data)
    assert task.id == "t1"
    assert task.percent_complete == 50
    assert task.priority == 3
    assert len(task.assignments) == 1
    assert "user-1" in task.assignments


def test_task_details_from_api_response():
    data = {
        "id": "t1",
        "description": "Detailed description here",
        "checklist": {
            "item-1": {"title": "Review PR", "isChecked": False},
            "item-2": {"title": "Run tests", "isChecked": True},
        },
        "references": {
            "https%3A//example.com": {"alias": "Design doc", "type": "Other"},
        },
    }
    details = TaskDetails.model_validate(data)
    assert details.description == "Detailed description here"
    assert len(details.checklist) == 2
    assert len(details.references) == 1


def test_assignment_model():
    a = Assignment(order_hint="8585")
    assert a.order_hint == "8585"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement models**

```python
# src/ms_planner/models/assignment.py
from pydantic import BaseModel, ConfigDict


class Assignment(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    order_hint: str | None = None
```

```python
# src/ms_planner/models/plan.py
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class PlanContainer(BaseModel):
    container_id: str = Field(alias="containerId")
    type: str


class Plan(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    owner: str | None = None
    created_date_time: datetime | None = Field(None, alias="createdDateTime")
    container: PlanContainer | None = None
    etag: str | None = Field(None, alias="@odata.etag")
```

```python
# src/ms_planner/models/bucket.py
from pydantic import BaseModel, ConfigDict, Field


class Bucket(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    plan_id: str = Field(alias="planId")
    name: str
    order_hint: str | None = Field(None, alias="orderHint")
    etag: str | None = Field(None, alias="@odata.etag")
```

```python
# src/ms_planner/models/task.py
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ChecklistItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str
    is_checked: bool = Field(False, alias="isChecked")


class Reference(BaseModel):
    alias: str | None = None
    type: str | None = None


class Task(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    plan_id: str | None = Field(None, alias="planId")
    bucket_id: str | None = Field(None, alias="bucketId")
    title: str
    assignments: dict[str, Any] = Field(default_factory=dict)
    percent_complete: int = Field(0, alias="percentComplete")
    priority: int = Field(5)
    start_date_time: datetime | None = Field(None, alias="startDateTime")
    due_date_time: datetime | None = Field(None, alias="dueDateTime")
    order_hint: str | None = Field(None, alias="orderHint")
    etag: str | None = Field(None, alias="@odata.etag")


class TaskDetails(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    description: str = ""
    checklist: dict[str, ChecklistItem] = Field(default_factory=dict)
    references: dict[str, Reference] = Field(default_factory=dict)
    etag: str | None = Field(None, alias="@odata.etag")
```

```python
# src/ms_planner/models/__init__.py
from ms_planner.models.assignment import Assignment
from ms_planner.models.bucket import Bucket
from ms_planner.models.plan import Plan, PlanContainer
from ms_planner.models.task import ChecklistItem, Reference, Task, TaskDetails

__all__ = [
    "Assignment",
    "Bucket",
    "ChecklistItem",
    "Plan",
    "PlanContainer",
    "Reference",
    "Task",
    "TaskDetails",
]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_models.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/ms_planner/models/ tests/test_models.py
git commit -m "feat: add pydantic models for plans, tasks, buckets"
```

---

### Task 6: PlanService

**Files:**
- Create: `src/ms_planner/services/__init__.py`
- Create: `src/ms_planner/services/plans.py`
- Create: `tests/test_services/__init__.py`
- Create: `tests/test_services/test_plans.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Create shared test fixtures**

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock
from ms_planner.client import GraphClient


@pytest.fixture
def mock_client():
    client = AsyncMock(spec=GraphClient)
    client.get_etag = lambda path: None
    client.set_etag = lambda path, etag: None
    return client
```

```python
# tests/test_services/__init__.py
```

- [ ] **Step 2: Write the failing tests**

```python
# tests/test_services/test_plans.py
import pytest
from unittest.mock import AsyncMock
from ms_planner.services.plans import PlanService
from ms_planner.models import Plan


@pytest.fixture
def service(mock_client):
    return PlanService(mock_client)


@pytest.mark.asyncio
async def test_list_plans(service, mock_client):
    mock_client.get.return_value = {
        "value": [
            {"id": "p1", "title": "Sprint 1", "owner": "g1"},
            {"id": "p2", "title": "Sprint 2", "owner": "g1"},
        ]
    }
    plans = await service.list("g1")
    assert len(plans) == 2
    assert all(isinstance(p, Plan) for p in plans)
    mock_client.get.assert_called_once_with("/groups/g1/planner/plans")


@pytest.mark.asyncio
async def test_get_plan(service, mock_client):
    mock_client.get.return_value = {"id": "p1", "title": "Sprint 1", "owner": "g1"}
    plan = await service.get("p1")
    assert isinstance(plan, Plan)
    assert plan.title == "Sprint 1"
    mock_client.get.assert_called_once_with("/planner/plans/p1")


@pytest.mark.asyncio
async def test_create_plan(service, mock_client):
    mock_client.post.return_value = {"id": "p-new", "title": "New Plan", "owner": "g1"}
    plan = await service.create(group_id="g1", title="New Plan")
    assert plan.id == "p-new"
    mock_client.post.assert_called_once_with(
        "/planner/plans",
        {
            "container": {"url": "https://graph.microsoft.com/v1.0/groups/g1", "type": "group"},
            "title": "New Plan",
        },
    )


@pytest.mark.asyncio
async def test_update_plan(service, mock_client):
    mock_client.patch.return_value = None
    await service.update("p1", title="Updated")
    mock_client.patch.assert_called_once_with(
        "/planner/plans/p1", {"title": "Updated"}
    )


@pytest.mark.asyncio
async def test_delete_plan(service, mock_client):
    await service.delete("p1")
    mock_client.delete.assert_called_once_with("/planner/plans/p1")
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest tests/test_services/test_plans.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 4: Implement PlanService**

```python
# src/ms_planner/services/plans.py
from ms_planner.client import GraphClient
from ms_planner.models import Plan


class PlanService:
    def __init__(self, client: GraphClient):
        self._client = client

    async def list(self, group_id: str) -> list[Plan]:
        data = await self._client.get(f"/groups/{group_id}/planner/plans")
        return [Plan.model_validate(item) for item in data["value"]]

    async def get(self, plan_id: str) -> Plan:
        data = await self._client.get(f"/planner/plans/{plan_id}")
        return Plan.model_validate(data)

    async def create(self, group_id: str, title: str) -> Plan:
        body = {
            "container": {
                "url": f"https://graph.microsoft.com/v1.0/groups/{group_id}",
                "type": "group",
            },
            "title": title,
        }
        data = await self._client.post("/planner/plans", body)
        return Plan.model_validate(data)

    async def update(self, plan_id: str, **kwargs: str) -> None:
        await self._client.patch(f"/planner/plans/{plan_id}", dict(kwargs))

    async def delete(self, plan_id: str) -> None:
        await self._client.delete(f"/planner/plans/{plan_id}")
```

```python
# src/ms_planner/services/__init__.py
from ms_planner.services.plans import PlanService
from ms_planner.services.buckets import BucketService
from ms_planner.services.tasks import TaskService

__all__ = ["PlanService", "BucketService", "TaskService"]
```

Note: The `__init__.py` will fail to import until Tasks 7 and 8 are done. Create it with just PlanService for now:

```python
# src/ms_planner/services/__init__.py
from ms_planner.services.plans import PlanService

__all__ = ["PlanService"]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_services/test_plans.py -v`
Expected: 5 passed

- [ ] **Step 6: Commit**

```bash
git add src/ms_planner/services/__init__.py src/ms_planner/services/plans.py tests/conftest.py tests/test_services/ 
git commit -m "feat: add PlanService with full CRUD"
```

---

### Task 7: BucketService

**Files:**
- Create: `src/ms_planner/services/buckets.py`
- Create: `tests/test_services/test_buckets.py`
- Modify: `src/ms_planner/services/__init__.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_services/test_buckets.py
import pytest
from ms_planner.services.buckets import BucketService
from ms_planner.models import Bucket


@pytest.fixture
def service(mock_client):
    return BucketService(mock_client)


@pytest.mark.asyncio
async def test_list_buckets(service, mock_client):
    mock_client.get.return_value = {
        "value": [
            {"id": "b1", "planId": "p1", "name": "To Do", "orderHint": "8585"},
        ]
    }
    buckets = await service.list("p1")
    assert len(buckets) == 1
    assert buckets[0].name == "To Do"
    mock_client.get.assert_called_once_with("/planner/plans/p1/buckets")


@pytest.mark.asyncio
async def test_create_bucket(service, mock_client):
    mock_client.post.return_value = {"id": "b-new", "planId": "p1", "name": "Done"}
    bucket = await service.create(plan_id="p1", name="Done")
    assert bucket.name == "Done"
    mock_client.post.assert_called_once_with(
        "/planner/buckets",
        {"planId": "p1", "name": "Done"},
    )


@pytest.mark.asyncio
async def test_update_bucket(service, mock_client):
    mock_client.patch.return_value = None
    await service.update("b1", name="In Progress")
    mock_client.patch.assert_called_once_with(
        "/planner/buckets/b1", {"name": "In Progress"}
    )


@pytest.mark.asyncio
async def test_delete_bucket(service, mock_client):
    await service.delete("b1")
    mock_client.delete.assert_called_once_with("/planner/buckets/b1")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_services/test_buckets.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement BucketService**

```python
# src/ms_planner/services/buckets.py
from ms_planner.client import GraphClient
from ms_planner.models import Bucket


class BucketService:
    def __init__(self, client: GraphClient):
        self._client = client

    async def list(self, plan_id: str) -> list[Bucket]:
        data = await self._client.get(f"/planner/plans/{plan_id}/buckets")
        return [Bucket.model_validate(item) for item in data["value"]]

    async def create(self, plan_id: str, name: str) -> Bucket:
        body = {"planId": plan_id, "name": name}
        data = await self._client.post("/planner/buckets", body)
        return Bucket.model_validate(data)

    async def update(self, bucket_id: str, **kwargs: str) -> None:
        await self._client.patch(f"/planner/buckets/{bucket_id}", dict(kwargs))

    async def delete(self, bucket_id: str) -> None:
        await self._client.delete(f"/planner/buckets/{bucket_id}")
```

Update `src/ms_planner/services/__init__.py`:

```python
from ms_planner.services.buckets import BucketService
from ms_planner.services.plans import PlanService

__all__ = ["BucketService", "PlanService"]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_services/test_buckets.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add src/ms_planner/services/buckets.py src/ms_planner/services/__init__.py tests/test_services/test_buckets.py
git commit -m "feat: add BucketService with full CRUD"
```

---

### Task 8: TaskService

**Files:**
- Create: `src/ms_planner/services/tasks.py`
- Create: `tests/test_services/test_tasks.py`
- Modify: `src/ms_planner/services/__init__.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_services/test_tasks.py
import pytest
from ms_planner.services.tasks import TaskService
from ms_planner.models import Task, TaskDetails


@pytest.fixture
def service(mock_client):
    return TaskService(mock_client)


@pytest.mark.asyncio
async def test_list_tasks(service, mock_client):
    mock_client.get.return_value = {
        "value": [
            {"id": "t1", "planId": "p1", "title": "Task 1"},
            {"id": "t2", "planId": "p1", "title": "Task 2"},
        ]
    }
    tasks = await service.list("p1")
    assert len(tasks) == 2
    assert all(isinstance(t, Task) for t in tasks)
    mock_client.get.assert_called_once_with("/planner/plans/p1/tasks")


@pytest.mark.asyncio
async def test_get_task(service, mock_client):
    mock_client.get.return_value = {"id": "t1", "planId": "p1", "title": "Task 1"}
    task = await service.get("t1")
    assert task.title == "Task 1"
    mock_client.get.assert_called_once_with("/planner/tasks/t1")


@pytest.mark.asyncio
async def test_get_details(service, mock_client):
    mock_client.get.return_value = {
        "id": "t1",
        "description": "Do the thing",
        "checklist": {},
        "references": {},
    }
    details = await service.get_details("t1")
    assert isinstance(details, TaskDetails)
    assert details.description == "Do the thing"
    mock_client.get.assert_called_once_with("/planner/tasks/t1/details")


@pytest.mark.asyncio
async def test_create_task(service, mock_client):
    mock_client.post.return_value = {"id": "t-new", "planId": "p1", "title": "New Task"}
    task = await service.create(plan_id="p1", title="New Task")
    assert task.id == "t-new"
    mock_client.post.assert_called_once_with(
        "/planner/tasks",
        {"planId": "p1", "title": "New Task"},
    )


@pytest.mark.asyncio
async def test_create_task_with_assignments(service, mock_client):
    mock_client.post.return_value = {
        "id": "t-new",
        "planId": "p1",
        "title": "Assigned Task",
        "assignments": {"user-1": {"@odata.type": "#microsoft.graph.plannerAssignment", "orderHint": " !"}},
    }
    task = await service.create(
        plan_id="p1",
        title="Assigned Task",
        assignments=["user-1"],
    )
    assert task.id == "t-new"
    mock_client.post.assert_called_once_with(
        "/planner/tasks",
        {
            "planId": "p1",
            "title": "Assigned Task",
            "assignments": {
                "user-1": {"@odata.type": "#microsoft.graph.plannerAssignment", "orderHint": " !"},
            },
        },
    )


@pytest.mark.asyncio
async def test_create_task_with_bucket(service, mock_client):
    mock_client.post.return_value = {
        "id": "t-new",
        "planId": "p1",
        "bucketId": "b1",
        "title": "Bucketed",
    }
    task = await service.create(plan_id="p1", title="Bucketed", bucket_id="b1")
    mock_client.post.assert_called_once_with(
        "/planner/tasks",
        {"planId": "p1", "title": "Bucketed", "bucketId": "b1"},
    )


@pytest.mark.asyncio
async def test_update_task(service, mock_client):
    mock_client.patch.return_value = None
    await service.update("t1", percent_complete=100)
    mock_client.patch.assert_called_once_with(
        "/planner/tasks/t1", {"percentComplete": 100}
    )


@pytest.mark.asyncio
async def test_update_details(service, mock_client):
    mock_client.patch.return_value = None
    await service.update_details("t1", description="Updated desc")
    mock_client.patch.assert_called_once_with(
        "/planner/tasks/t1/details", {"description": "Updated desc"}
    )


@pytest.mark.asyncio
async def test_delete_task(service, mock_client):
    await service.delete("t1")
    mock_client.delete.assert_called_once_with("/planner/tasks/t1")


@pytest.mark.asyncio
async def test_list_user_tasks(service, mock_client):
    mock_client.get.return_value = {
        "value": [{"id": "t1", "planId": "p1", "title": "My Task"}]
    }
    tasks = await service.list_user_tasks("user-1")
    assert len(tasks) == 1
    mock_client.get.assert_called_once_with("/users/user-1/planner/tasks")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_services/test_tasks.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement TaskService**

```python
# src/ms_planner/services/tasks.py
from typing import Any
from ms_planner.client import GraphClient
from ms_planner.models import Task, TaskDetails


class TaskService:
    def __init__(self, client: GraphClient):
        self._client = client

    async def list(self, plan_id: str) -> list[Task]:
        data = await self._client.get(f"/planner/plans/{plan_id}/tasks")
        return [Task.model_validate(item) for item in data["value"]]

    async def get(self, task_id: str) -> Task:
        data = await self._client.get(f"/planner/tasks/{task_id}")
        return Task.model_validate(data)

    async def get_details(self, task_id: str) -> TaskDetails:
        data = await self._client.get(f"/planner/tasks/{task_id}/details")
        return TaskDetails.model_validate(data)

    async def create(
        self,
        plan_id: str,
        title: str,
        *,
        bucket_id: str | None = None,
        assignments: list[str] | None = None,
    ) -> Task:
        body: dict[str, Any] = {"planId": plan_id, "title": title}
        if bucket_id:
            body["bucketId"] = bucket_id
        if assignments:
            body["assignments"] = {
                user_id: {
                    "@odata.type": "#microsoft.graph.plannerAssignment",
                    "orderHint": " !",
                }
                for user_id in assignments
            }
        data = await self._client.post("/planner/tasks", body)
        return Task.model_validate(data)

    async def update(self, task_id: str, **kwargs: Any) -> None:
        # Convert snake_case to camelCase for Graph API
        body = {}
        key_map = {
            "percent_complete": "percentComplete",
            "start_date_time": "startDateTime",
            "due_date_time": "dueDateTime",
            "bucket_id": "bucketId",
            "order_hint": "orderHint",
        }
        for k, v in kwargs.items():
            api_key = key_map.get(k, k)
            body[api_key] = v
        await self._client.patch(f"/planner/tasks/{task_id}", body)

    async def update_details(self, task_id: str, **kwargs: Any) -> None:
        await self._client.patch(f"/planner/tasks/{task_id}/details", dict(kwargs))

    async def delete(self, task_id: str) -> None:
        await self._client.delete(f"/planner/tasks/{task_id}")

    async def list_user_tasks(self, user_id: str) -> list[Task]:
        data = await self._client.get(f"/users/{user_id}/planner/tasks")
        return [Task.model_validate(item) for item in data["value"]]
```

Update `src/ms_planner/services/__init__.py`:

```python
from ms_planner.services.buckets import BucketService
from ms_planner.services.plans import PlanService
from ms_planner.services.tasks import TaskService

__all__ = ["BucketService", "PlanService", "TaskService"]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_services/test_tasks.py -v`
Expected: 10 passed

- [ ] **Step 5: Commit**

```bash
git add src/ms_planner/services/tasks.py src/ms_planner/services/__init__.py tests/test_services/test_tasks.py
git commit -m "feat: add TaskService with CRUD, details, and user tasks"
```

---

### Task 9: CLI — main app and plans commands

**Files:**
- Create: `src/ms_planner/cli/__init__.py`
- Create: `src/ms_planner/cli/main.py`
- Create: `src/ms_planner/cli/plans.py`
- Create: `tests/test_cli/__init__.py`
- Create: `tests/test_cli/test_plans.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_cli/__init__.py
```

```python
# tests/test_cli/test_plans.py
import pytest
from unittest.mock import AsyncMock, patch
from typer.testing import CliRunner
from ms_planner.cli.main import app
from ms_planner.models import Plan

runner = CliRunner()


@patch("ms_planner.cli.plans._get_plan_service")
def test_plans_list(mock_get_svc):
    mock_svc = AsyncMock()
    mock_svc.list.return_value = [
        Plan(id="p1", title="Sprint 1", owner="g1"),
        Plan(id="p2", title="Sprint 2", owner="g1"),
    ]
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["plans", "list", "--group-id", "g1"])
    assert result.exit_code == 0
    assert "Sprint 1" in result.output
    assert "Sprint 2" in result.output


@patch("ms_planner.cli.plans._get_plan_service")
def test_plans_get(mock_get_svc):
    mock_svc = AsyncMock()
    mock_svc.get.return_value = Plan(id="p1", title="Sprint 1", owner="g1")
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["plans", "get", "p1"])
    assert result.exit_code == 0
    assert "Sprint 1" in result.output


@patch("ms_planner.cli.plans._get_plan_service")
def test_plans_create(mock_get_svc):
    mock_svc = AsyncMock()
    mock_svc.create.return_value = Plan(id="p-new", title="New Plan", owner="g1")
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["plans", "create", "--group-id", "g1", "--title", "New Plan"])
    assert result.exit_code == 0
    assert "p-new" in result.output


@patch("ms_planner.cli.plans._get_plan_service")
def test_plans_list_json(mock_get_svc):
    mock_svc = AsyncMock()
    mock_svc.list.return_value = [
        Plan(id="p1", title="Sprint 1", owner="g1"),
    ]
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["plans", "list", "--group-id", "g1", "--json"])
    assert result.exit_code == 0
    assert '"id"' in result.output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_cli/test_plans.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement CLI main and plans**

```python
# src/ms_planner/cli/__init__.py
```

```python
# src/ms_planner/cli/main.py
import typer
from ms_planner.cli.plans import plans_app
from ms_planner.cli.buckets import buckets_app
from ms_planner.cli.tasks import tasks_app

app = typer.Typer(name="planner", help="Microsoft Planner CLI")
app.add_typer(plans_app, name="plans")
app.add_typer(buckets_app, name="buckets")
app.add_typer(tasks_app, name="tasks")

if __name__ == "__main__":
    app()
```

Note: This will import buckets and tasks CLI modules that don't exist yet. Create stubs:

```python
# src/ms_planner/cli/buckets.py (stub — replaced in Task 10)
import typer

buckets_app = typer.Typer(help="Manage buckets")
```

```python
# src/ms_planner/cli/tasks.py (stub — replaced in Task 11)
import typer

tasks_app = typer.Typer(help="Manage tasks")
```

Now the full plans CLI:

```python
# src/ms_planner/cli/plans.py
import asyncio
import json as json_lib
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ms_planner.auth import get_token
from ms_planner.client import GraphClient
from ms_planner.config import Settings
from ms_planner.services.plans import PlanService

plans_app = typer.Typer(help="Manage plans")
console = Console()


def _get_plan_service() -> PlanService:
    settings = Settings()
    client = GraphClient(token_factory=lambda: get_token(settings))
    return PlanService(client)


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@plans_app.command("list")
def list_plans(
    group_id: Annotated[str, typer.Option("--group-id", help="M365 Group ID")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """List all plans in a group."""
    service = _get_plan_service()
    plans = _run(service.list(group_id))

    if json:
        console.print(json_lib.dumps([p.model_dump() for p in plans], indent=2, default=str))
        return

    table = Table(title="Plans")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Owner")
    for p in plans:
        table.add_row(p.id, p.title, p.owner or "")
    console.print(table)


@plans_app.command("get")
def get_plan(
    plan_id: Annotated[str, typer.Argument(help="Plan ID")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Get a specific plan."""
    service = _get_plan_service()
    plan = _run(service.get(plan_id))

    if json:
        console.print(json_lib.dumps(plan.model_dump(), indent=2, default=str))
        return

    table = Table(title="Plan")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("ID", plan.id)
    table.add_row("Title", plan.title)
    table.add_row("Owner", plan.owner or "")
    table.add_row("Created", str(plan.created_date_time) if plan.created_date_time else "")
    console.print(table)


@plans_app.command("create")
def create_plan(
    group_id: Annotated[str, typer.Option("--group-id", help="M365 Group ID")],
    title: Annotated[str, typer.Option("--title", help="Plan title")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Create a new plan in a group."""
    service = _get_plan_service()
    plan = _run(service.create(group_id, title))

    if json:
        console.print(json_lib.dumps(plan.model_dump(), indent=2, default=str))
        return

    console.print(f"[green]Created plan:[/green] {plan.id} — {plan.title}")


@plans_app.command("delete")
def delete_plan(
    plan_id: Annotated[str, typer.Argument(help="Plan ID")],
):
    """Delete a plan."""
    service = _get_plan_service()
    _run(service.delete(plan_id))
    console.print(f"[red]Deleted plan:[/red] {plan_id}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_cli/test_plans.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add src/ms_planner/cli/ tests/test_cli/
git commit -m "feat: add CLI framework and plan commands"
```

---

### Task 10: CLI — bucket commands

**Files:**
- Modify: `src/ms_planner/cli/buckets.py`
- Create: `tests/test_cli/test_buckets.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_cli/test_buckets.py
import pytest
from unittest.mock import AsyncMock, patch
from typer.testing import CliRunner
from ms_planner.cli.main import app
from ms_planner.models import Bucket

runner = CliRunner()


@patch("ms_planner.cli.buckets._get_bucket_service")
def test_buckets_list(mock_get_svc):
    mock_svc = AsyncMock()
    mock_svc.list.return_value = [
        Bucket(id="b1", plan_id="p1", name="To Do"),
        Bucket(id="b2", plan_id="p1", name="Done"),
    ]
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["buckets", "list", "--plan-id", "p1"])
    assert result.exit_code == 0
    assert "To Do" in result.output
    assert "Done" in result.output


@patch("ms_planner.cli.buckets._get_bucket_service")
def test_buckets_create(mock_get_svc):
    mock_svc = AsyncMock()
    mock_svc.create.return_value = Bucket(id="b-new", plan_id="p1", name="In Progress")
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["buckets", "create", "--plan-id", "p1", "--name", "In Progress"])
    assert result.exit_code == 0
    assert "b-new" in result.output


@patch("ms_planner.cli.buckets._get_bucket_service")
def test_buckets_delete(mock_get_svc):
    mock_svc = AsyncMock()
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["buckets", "delete", "b1"])
    assert result.exit_code == 0
    assert "b1" in result.output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_cli/test_buckets.py -v`
Expected: FAIL — `_get_bucket_service` not found

- [ ] **Step 3: Implement bucket CLI**

```python
# src/ms_planner/cli/buckets.py
import asyncio
import json as json_lib
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ms_planner.auth import get_token
from ms_planner.client import GraphClient
from ms_planner.config import Settings
from ms_planner.services.buckets import BucketService

buckets_app = typer.Typer(help="Manage buckets")
console = Console()


def _get_bucket_service() -> BucketService:
    settings = Settings()
    client = GraphClient(token_factory=lambda: get_token(settings))
    return BucketService(client)


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@buckets_app.command("list")
def list_buckets(
    plan_id: Annotated[str, typer.Option("--plan-id", help="Plan ID")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """List all buckets in a plan."""
    service = _get_bucket_service()
    buckets = _run(service.list(plan_id))

    if json:
        console.print(json_lib.dumps([b.model_dump() for b in buckets], indent=2, default=str))
        return

    table = Table(title="Buckets")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Plan ID")
    for b in buckets:
        table.add_row(b.id, b.name, b.plan_id)
    console.print(table)


@buckets_app.command("create")
def create_bucket(
    plan_id: Annotated[str, typer.Option("--plan-id", help="Plan ID")],
    name: Annotated[str, typer.Option("--name", help="Bucket name")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Create a new bucket in a plan."""
    service = _get_bucket_service()
    bucket = _run(service.create(plan_id, name))

    if json:
        console.print(json_lib.dumps(bucket.model_dump(), indent=2, default=str))
        return

    console.print(f"[green]Created bucket:[/green] {bucket.id} — {bucket.name}")


@buckets_app.command("delete")
def delete_bucket(
    bucket_id: Annotated[str, typer.Argument(help="Bucket ID")],
):
    """Delete a bucket."""
    service = _get_bucket_service()
    _run(service.delete(bucket_id))
    console.print(f"[red]Deleted bucket:[/red] {bucket_id}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_cli/test_buckets.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add src/ms_planner/cli/buckets.py tests/test_cli/test_buckets.py
git commit -m "feat: add CLI bucket commands"
```

---

### Task 11: CLI — task commands

**Files:**
- Modify: `src/ms_planner/cli/tasks.py`
- Create: `tests/test_cli/test_tasks.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_cli/test_tasks.py
import pytest
from unittest.mock import AsyncMock, patch
from typer.testing import CliRunner
from ms_planner.cli.main import app
from ms_planner.models import Task, TaskDetails, ChecklistItem

runner = CliRunner()


@patch("ms_planner.cli.tasks._get_task_service")
def test_tasks_list(mock_get_svc):
    mock_svc = AsyncMock()
    mock_svc.list.return_value = [
        Task(id="t1", title="Fix bug", plan_id="p1"),
        Task(id="t2", title="Add feature", plan_id="p1"),
    ]
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["tasks", "list", "--plan-id", "p1"])
    assert result.exit_code == 0
    assert "Fix bug" in result.output


@patch("ms_planner.cli.tasks._get_task_service")
def test_tasks_get(mock_get_svc):
    mock_svc = AsyncMock()
    mock_svc.get.return_value = Task(id="t1", title="Fix bug", plan_id="p1", percent_complete=50)
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["tasks", "get", "t1"])
    assert result.exit_code == 0
    assert "Fix bug" in result.output


@patch("ms_planner.cli.tasks._get_task_service")
def test_tasks_create(mock_get_svc):
    mock_svc = AsyncMock()
    mock_svc.create.return_value = Task(id="t-new", title="New Task", plan_id="p1")
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["tasks", "create", "--plan-id", "p1", "--title", "New Task"])
    assert result.exit_code == 0
    assert "t-new" in result.output


@patch("ms_planner.cli.tasks._get_task_service")
def test_tasks_details(mock_get_svc):
    mock_svc = AsyncMock()
    mock_svc.get_details.return_value = TaskDetails(
        id="t1",
        description="Detailed desc",
        checklist={"c1": ChecklistItem(title="Review", is_checked=False)},
        references={},
    )
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["tasks", "details", "t1"])
    assert result.exit_code == 0
    assert "Detailed desc" in result.output


@patch("ms_planner.cli.tasks._get_task_service")
def test_tasks_delete(mock_get_svc):
    mock_svc = AsyncMock()
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["tasks", "delete", "t1"])
    assert result.exit_code == 0
    assert "t1" in result.output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_cli/test_tasks.py -v`
Expected: FAIL — `_get_task_service` not found

- [ ] **Step 3: Implement task CLI**

```python
# src/ms_planner/cli/tasks.py
import asyncio
import json as json_lib
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ms_planner.auth import get_token
from ms_planner.client import GraphClient
from ms_planner.config import Settings
from ms_planner.services.tasks import TaskService

tasks_app = typer.Typer(help="Manage tasks")
console = Console()


def _get_task_service() -> TaskService:
    settings = Settings()
    client = GraphClient(token_factory=lambda: get_token(settings))
    return TaskService(client)


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@tasks_app.command("list")
def list_tasks(
    plan_id: Annotated[str, typer.Option("--plan-id", help="Plan ID")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """List all tasks in a plan."""
    service = _get_task_service()
    tasks = _run(service.list(plan_id))

    if json:
        console.print(json_lib.dumps([t.model_dump() for t in tasks], indent=2, default=str))
        return

    table = Table(title="Tasks")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Progress")
    table.add_column("Priority")
    table.add_column("Due Date")
    for t in tasks:
        progress = f"{t.percent_complete}%"
        due = str(t.due_date_time.date()) if t.due_date_time else ""
        table.add_row(t.id, t.title, progress, str(t.priority), due)
    console.print(table)


@tasks_app.command("get")
def get_task(
    task_id: Annotated[str, typer.Argument(help="Task ID")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Get a specific task."""
    service = _get_task_service()
    task = _run(service.get(task_id))

    if json:
        console.print(json_lib.dumps(task.model_dump(), indent=2, default=str))
        return

    table = Table(title="Task")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("ID", task.id)
    table.add_row("Title", task.title)
    table.add_row("Plan ID", task.plan_id or "")
    table.add_row("Bucket ID", task.bucket_id or "")
    table.add_row("Progress", f"{task.percent_complete}%")
    table.add_row("Priority", str(task.priority))
    table.add_row("Start", str(task.start_date_time) if task.start_date_time else "")
    table.add_row("Due", str(task.due_date_time) if task.due_date_time else "")
    table.add_row("Assignees", ", ".join(task.assignments.keys()) if task.assignments else "")
    console.print(table)


@tasks_app.command("create")
def create_task(
    plan_id: Annotated[str, typer.Option("--plan-id", help="Plan ID")],
    title: Annotated[str, typer.Option("--title", help="Task title")],
    bucket_id: Annotated[str | None, typer.Option("--bucket-id", help="Bucket ID")] = None,
    assign: Annotated[list[str] | None, typer.Option("--assign", help="User IDs to assign")] = None,
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Create a new task."""
    service = _get_task_service()
    task = _run(service.create(plan_id=plan_id, title=title, bucket_id=bucket_id, assignments=assign))

    if json:
        console.print(json_lib.dumps(task.model_dump(), indent=2, default=str))
        return

    console.print(f"[green]Created task:[/green] {task.id} — {task.title}")


@tasks_app.command("update")
def update_task(
    task_id: Annotated[str, typer.Argument(help="Task ID")],
    progress: Annotated[int | None, typer.Option("--progress", help="Percent complete (0, 50, 100)")] = None,
    priority: Annotated[int | None, typer.Option("--priority", help="Priority (0-10, lower=higher)")] = None,
    title: Annotated[str | None, typer.Option("--title", help="New title")] = None,
):
    """Update a task."""
    service = _get_task_service()
    kwargs = {}
    if progress is not None:
        kwargs["percent_complete"] = progress
    if priority is not None:
        kwargs["priority"] = priority
    if title is not None:
        kwargs["title"] = title
    if not kwargs:
        console.print("[yellow]No updates specified[/yellow]")
        return
    _run(service.update(task_id, **kwargs))
    console.print(f"[green]Updated task:[/green] {task_id}")


@tasks_app.command("delete")
def delete_task(
    task_id: Annotated[str, typer.Argument(help="Task ID")],
):
    """Delete a task."""
    service = _get_task_service()
    _run(service.delete(task_id))
    console.print(f"[red]Deleted task:[/red] {task_id}")


@tasks_app.command("details")
def task_details(
    task_id: Annotated[str, typer.Argument(help="Task ID")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Get task details (description, checklist, attachments)."""
    service = _get_task_service()
    details = _run(service.get_details(task_id))

    if json:
        console.print(json_lib.dumps(details.model_dump(), indent=2, default=str))
        return

    console.print(f"[bold]Description:[/bold] {details.description}")
    if details.checklist:
        console.print("\n[bold]Checklist:[/bold]")
        for item_id, item in details.checklist.items():
            check = "[x]" if item.is_checked else "[ ]"
            console.print(f"  {check} {item.title}  ({item_id})")
    if details.references:
        console.print("\n[bold]Attachments:[/bold]")
        for url, ref in details.references.items():
            console.print(f"  {ref.alias or 'Untitled'}: {url}")


@tasks_app.command("checklist-add")
def checklist_add(
    task_id: Annotated[str, typer.Argument(help="Task ID")],
    item: Annotated[str, typer.Option("--item", help="Checklist item text")],
):
    """Add a checklist item to a task."""
    import uuid

    service = _get_task_service()
    item_id = str(uuid.uuid4())
    _run(
        service.update_details(
            task_id,
            checklist={item_id: {"@odata.type": "microsoft.graph.plannerChecklistItem", "title": item}},
        )
    )
    console.print(f"[green]Added checklist item:[/green] {item}")


@tasks_app.command("checklist-remove")
def checklist_remove(
    task_id: Annotated[str, typer.Argument(help="Task ID")],
    item_id: Annotated[str, typer.Option("--item-id", help="Checklist item ID")],
):
    """Remove a checklist item from a task."""
    service = _get_task_service()
    _run(service.update_details(task_id, checklist={item_id: None}))
    console.print(f"[red]Removed checklist item:[/red] {item_id}")


@tasks_app.command("attach")
def attach(
    task_id: Annotated[str, typer.Argument(help="Task ID")],
    url: Annotated[str, typer.Option("--url", help="URL to attach")],
    alias: Annotated[str, typer.Option("--alias", help="Display name")] = "",
):
    """Attach a URL reference to a task."""
    import urllib.parse

    service = _get_task_service()
    encoded_url = urllib.parse.quote(url, safe="")
    _run(
        service.update_details(
            task_id,
            references={
                encoded_url: {
                    "@odata.type": "microsoft.graph.plannerExternalReference",
                    "alias": alias,
                    "type": "Other",
                }
            },
        )
    )
    console.print(f"[green]Attached:[/green] {alias or url}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_cli/test_tasks.py -v`
Expected: 5 passed

- [ ] **Step 5: Run all tests**

Run: `uv run pytest -v`
Expected: All tests pass (total ~30+)

- [ ] **Step 6: Commit**

```bash
git add src/ms_planner/cli/tasks.py tests/test_cli/test_tasks.py
git commit -m "feat: add CLI task commands with checklist and attachments"
```

---

### Task 12: CLI error handling and final polish

**Files:**
- Modify: `src/ms_planner/cli/main.py`

- [ ] **Step 1: Add error handling wrapper to main CLI**

Update `src/ms_planner/cli/main.py`:

```python
# src/ms_planner/cli/main.py
import typer
from rich.console import Console

from ms_planner.cli.plans import plans_app
from ms_planner.cli.buckets import buckets_app
from ms_planner.cli.tasks import tasks_app
from ms_planner.exceptions import (
    PlannerConflictError,
    PlannerForbiddenError,
    PlannerNotFoundError,
    PlannerThrottledError,
)

app = typer.Typer(
    name="planner",
    help="Microsoft Planner CLI — manage plans, tasks, and buckets via Graph API",
)
app.add_typer(plans_app, name="plans")
app.add_typer(buckets_app, name="buckets")
app.add_typer(tasks_app, name="tasks")

console = Console(stderr=True)


@app.callback()
def main():
    """Microsoft Planner CLI."""


def run():
    try:
        app()
    except PlannerNotFoundError as e:
        console.print(f"[red]Not found:[/red] {e}")
        raise typer.Exit(1)
    except PlannerForbiddenError as e:
        console.print(f"[red]Access denied:[/red] {e}")
        console.print("[dim]Check that admin consent was granted for the app permissions.[/dim]")
        raise typer.Exit(1)
    except PlannerConflictError as e:
        console.print(f"[red]Conflict:[/red] {e}")
        console.print("[dim]The resource was modified by another user. Try again.[/dim]")
        raise typer.Exit(1)
    except PlannerThrottledError as e:
        console.print(f"[red]Rate limited:[/red] {e}")
        console.print("[dim]Too many requests. Wait a moment and try again.[/dim]")
        raise typer.Exit(1)
    except RuntimeError as e:
        console.print(f"[red]Auth error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    run()
```

Update the script entry in `pyproject.toml`:

```toml
[project.scripts]
planner = "ms_planner.cli.main:run"
```

- [ ] **Step 2: Run all tests**

Run: `uv run pytest -v`
Expected: All tests pass

- [ ] **Step 3: Verify CLI help works**

Run: `uv run planner --help`
Expected: Shows help with plans, buckets, tasks subcommands

Run: `uv run planner plans --help`
Expected: Shows plan commands (list, get, create, delete)

- [ ] **Step 4: Commit**

```bash
git add src/ms_planner/cli/main.py pyproject.toml
git commit -m "feat: add CLI error handling and finalize entry point"
```

---

### Task 13: Full test suite run and final commit

- [ ] **Step 1: Run full test suite**

Run: `uv run pytest -v --tb=short`
Expected: All tests pass. No warnings about unclosed resources.

- [ ] **Step 2: Verify the CLI installs and runs**

Run: `uv run planner --help`
Run: `uv run planner plans --help`
Run: `uv run planner tasks --help`
Run: `uv run planner buckets --help`
Expected: All show correct help text.

- [ ] **Step 3: Final commit (if any remaining changes)**

```bash
git status
# If clean, nothing to commit. If files remain:
git add -A
git commit -m "chore: final cleanup"
```

- [ ] **Step 4: Push to remote**

```bash
git push origin main
```

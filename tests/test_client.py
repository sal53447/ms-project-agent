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

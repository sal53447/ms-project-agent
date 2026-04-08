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

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
    mock_client.get.return_value = {"id": "b1", "planId": "p1", "name": "Phase 1"}
    mock_client.patch.return_value = None
    await service.update("b1", name="Phase 1 — Done")
    mock_client.patch.assert_called_once_with(
        "/planner/buckets/b1", {"name": "Phase 1 — Done"}
    )


@pytest.mark.asyncio
async def test_delete_bucket(service, mock_client):
    mock_client.get.return_value = {"id": "b1", "planId": "p1", "name": "Phase 1"}
    await service.delete("b1")
    mock_client.delete.assert_called_once_with("/planner/buckets/b1")

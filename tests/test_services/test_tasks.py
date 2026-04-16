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
    mock_client.get.return_value = {"id": "t1", "planId": "p1", "title": "Task 1"}
    mock_client.patch.return_value = None
    await service.update("t1", percent_complete=100)
    mock_client.patch.assert_called_once_with(
        "/planner/tasks/t1", {"percentComplete": 100}
    )


@pytest.mark.asyncio
async def test_update_task_with_assignments(service, mock_client):
    mock_client.get.return_value = {"id": "t1", "planId": "p1", "title": "Task 1"}
    mock_client.patch.return_value = None
    assignments = {
        "user-1": {"@odata.type": "#microsoft.graph.plannerAssignment", "orderHint": " !"}
    }
    await service.update("t1", assignments=assignments)
    mock_client.patch.assert_called_once_with(
        "/planner/tasks/t1", {"assignments": assignments}
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

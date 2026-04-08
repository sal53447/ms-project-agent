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

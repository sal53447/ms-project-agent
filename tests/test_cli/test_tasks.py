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

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


@patch("ms_planner.cli.tasks._get_task_service")
def test_tasks_update_description(mock_get_svc):
    mock_svc = AsyncMock()
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["tasks", "update", "t1", "--description", "New description"])
    assert result.exit_code == 0
    mock_svc.update_details.assert_called_once_with("t1", description="New description")
    mock_svc.update.assert_not_called()


@patch("ms_planner.cli.tasks._get_task_service")
def test_tasks_update_assign(mock_get_svc):
    mock_svc = AsyncMock()
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["tasks", "update", "t1", "--assign", "user-id-1"])
    assert result.exit_code == 0
    mock_svc.update.assert_called_once_with(
        "t1",
        assignments={
            "user-id-1": {
                "@odata.type": "#microsoft.graph.plannerAssignment",
                "orderHint": " !",
            }
        },
    )


@patch("ms_planner.cli.tasks._get_task_service")
def test_tasks_update_assign_multiple(mock_get_svc):
    mock_svc = AsyncMock()
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["tasks", "update", "t1", "--assign", "uid-1", "--assign", "uid-2"])
    assert result.exit_code == 0
    call_kwargs = mock_svc.update.call_args[1]
    assert "uid-1" in call_kwargs["assignments"]
    assert "uid-2" in call_kwargs["assignments"]


@patch("ms_planner.cli.tasks._get_task_service")
def test_tasks_update_description_and_progress(mock_get_svc):
    """Description update and field update can be combined in one call."""
    mock_svc = AsyncMock()
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["tasks", "update", "t1", "--description", "Done", "--progress", "100"])
    assert result.exit_code == 0
    mock_svc.update_details.assert_called_once_with("t1", description="Done")
    mock_svc.update.assert_called_once_with("t1", percent_complete=100)

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

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

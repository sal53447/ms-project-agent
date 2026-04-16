import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from typer.testing import CliRunner

from ms_planner.cli.main import app
from ms_planner.models import TaskSnapshot, TaskStatus, SnapshotFile, SnapshotDiff

runner = CliRunner()


def _make_snapshot_file(tasks=None):
    return SnapshotFile(
        taken_at="2026-04-15T10:00:00Z",
        plan_id="p1",
        tasks=tasks or [],
    )


def _make_task_snapshot(**kwargs):
    defaults = dict(
        task_id="t1",
        title="Build CLI",
        bucket_id="b1",
        bucket_name="Phase 1",
        status=TaskStatus.not_started,
        start_date=None,
        due_date=None,
        assigned_to=[],
    )
    defaults.update(kwargs)
    return TaskSnapshot(**defaults)


@patch("ms_planner.cli.snapshot._get_snapshot_service")
def test_snapshot_take_first_run(mock_get_svc, tmp_path):
    """First run: no existing snapshot → writes initial snapshot, no archive."""
    mock_svc = MagicMock()
    mock_svc.fetch = AsyncMock(return_value=[_make_task_snapshot()])
    mock_svc.load.return_value = None  # no existing snapshot
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["snapshot", "take", "--plan-id", "p1", "--project-dir", str(tmp_path)])
    assert result.exit_code == 0
    mock_svc.fetch.assert_called_once_with("p1")
    mock_svc.archive.assert_not_called()
    mock_svc.save.assert_called_once()


@patch("ms_planner.cli.snapshot._get_snapshot_service")
def test_snapshot_take_archives_existing(mock_get_svc, tmp_path):
    """Subsequent run: existing snapshot is archived before new one is written."""
    existing = _make_snapshot_file([_make_task_snapshot()])
    mock_svc = MagicMock()
    mock_svc.fetch = AsyncMock(return_value=[_make_task_snapshot()])
    mock_svc.load.return_value = existing
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["snapshot", "take", "--plan-id", "p1", "--project-dir", str(tmp_path)])
    assert result.exit_code == 0
    mock_svc.archive.assert_called_once_with(tmp_path)
    mock_svc.save.assert_called_once()


@patch("ms_planner.cli.snapshot._get_snapshot_service")
def test_snapshot_diff_no_existing_snapshot(mock_get_svc, tmp_path):
    """diff with no existing snapshot outputs a baseline message."""
    mock_svc = MagicMock()
    mock_svc.fetch = AsyncMock(return_value=[_make_task_snapshot()])
    mock_svc.load.return_value = None
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["snapshot", "diff", "--plan-id", "p1", "--project-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "baseline" in result.output.lower() or "initial" in result.output.lower()


@patch("ms_planner.cli.snapshot._get_snapshot_service")
def test_snapshot_diff_with_existing_outputs_json(mock_get_svc, tmp_path):
    """diff with existing snapshot outputs the delta as JSON."""
    existing = _make_snapshot_file([_make_task_snapshot()])
    new_tasks = [_make_task_snapshot(status=TaskStatus.completed)]
    diff = SnapshotDiff(
        since="2026-04-15T10:00:00Z",
        as_of="2026-04-16T10:00:00Z",
        completed=new_tasks,
        progressed=[],
        added=[],
        removed=[],
        changed=[],
    )
    mock_svc = MagicMock()
    mock_svc.fetch = AsyncMock(return_value=new_tasks)
    mock_svc.load.return_value = existing
    mock_svc.diff.return_value = diff
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["snapshot", "diff", "--plan-id", "p1", "--project-dir", str(tmp_path)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["completed"][0]["task_id"] == "t1"
    assert data["since"] == "2026-04-15T10:00:00Z"


@patch("ms_planner.cli.snapshot._get_snapshot_service")
def test_snapshot_diff_no_changes_message(mock_get_svc, tmp_path):
    """diff with no changes outputs a no-changes indicator."""
    existing = _make_snapshot_file([_make_task_snapshot()])
    new_tasks = [_make_task_snapshot()]
    diff = SnapshotDiff(
        since="2026-04-15T10:00:00Z",
        as_of="2026-04-16T10:00:00Z",
        completed=[],
        progressed=[],
        added=[],
        removed=[],
        changed=[],
    )
    mock_svc = MagicMock()
    mock_svc.fetch = AsyncMock(return_value=new_tasks)
    mock_svc.load.return_value = existing
    mock_svc.diff.return_value = diff
    mock_get_svc.return_value = mock_svc

    result = runner.invoke(app, ["snapshot", "diff", "--plan-id", "p1", "--project-dir", str(tmp_path)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["completed"] == []
    assert data["added"] == []

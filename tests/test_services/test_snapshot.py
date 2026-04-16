import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from ms_planner.models import Task, Bucket, TaskSnapshot, TaskStatus, SnapshotFile, SnapshotDiff
from ms_planner.services.snapshot import SnapshotService


@pytest.fixture
def service(mock_client):
    return SnapshotService(mock_client)


@pytest.fixture
def task_data():
    return [
        {
            "id": "t1",
            "planId": "p1",
            "bucketId": "b1",
            "title": "Build CLI",
            "percentComplete": 0,
            "assignments": {},
        },
        {
            "id": "t2",
            "planId": "p1",
            "bucketId": "b2",
            "title": "Write tests",
            "percentComplete": 50,
            "assignments": {"user-1": {}},
            "startDateTime": "2026-04-01T00:00:00Z",
            "dueDateTime": "2026-04-30T00:00:00Z",
        },
        {
            "id": "t3",
            "planId": "p1",
            "bucketId": "b1",
            "title": "Deploy",
            "percentComplete": 100,
            "assignments": {},
        },
    ]


@pytest.fixture
def bucket_data():
    return [
        {"id": "b1", "planId": "p1", "name": "Phase 1"},
        {"id": "b2", "planId": "p1", "name": "Phase 2"},
    ]


# --- fetch ---

@pytest.mark.asyncio
async def test_fetch_returns_snapshots(service, mock_client, task_data, bucket_data):
    mock_client.get.side_effect = [
        {"value": task_data},
        {"value": bucket_data},
    ]
    snapshots = await service.fetch("p1")
    assert len(snapshots) == 3
    assert all(isinstance(s, TaskSnapshot) for s in snapshots)


@pytest.mark.asyncio
async def test_fetch_maps_bucket_name(service, mock_client, task_data, bucket_data):
    mock_client.get.side_effect = [
        {"value": task_data},
        {"value": bucket_data},
    ]
    snapshots = await service.fetch("p1")
    by_id = {s.task_id: s for s in snapshots}
    assert by_id["t1"].bucket_name == "Phase 1"
    assert by_id["t2"].bucket_name == "Phase 2"


@pytest.mark.asyncio
async def test_fetch_derives_status(service, mock_client, task_data, bucket_data):
    mock_client.get.side_effect = [
        {"value": task_data},
        {"value": bucket_data},
    ]
    snapshots = await service.fetch("p1")
    by_id = {s.task_id: s for s in snapshots}
    assert by_id["t1"].status == TaskStatus.not_started
    assert by_id["t2"].status == TaskStatus.in_progress
    assert by_id["t3"].status == TaskStatus.completed


@pytest.mark.asyncio
async def test_fetch_extracts_dates(service, mock_client, task_data, bucket_data):
    mock_client.get.side_effect = [
        {"value": task_data},
        {"value": bucket_data},
    ]
    snapshots = await service.fetch("p1")
    t2 = next(s for s in snapshots if s.task_id == "t2")
    assert t2.start_date == "2026-04-01"
    assert t2.due_date == "2026-04-30"


@pytest.mark.asyncio
async def test_fetch_extracts_assigned_to(service, mock_client, task_data, bucket_data):
    mock_client.get.side_effect = [
        {"value": task_data},
        {"value": bucket_data},
    ]
    snapshots = await service.fetch("p1")
    t2 = next(s for s in snapshots if s.task_id == "t2")
    assert t2.assigned_to == ["user-1"]


# --- load / save / archive ---

def test_load_returns_none_when_no_snapshot(service, tmp_path):
    result = service.load(tmp_path)
    assert result is None


def test_save_and_load_roundtrip(service, tmp_path):
    tasks = [
        TaskSnapshot(
            task_id="t1",
            title="Build CLI",
            bucket_id="b1",
            bucket_name="Phase 1",
            status=TaskStatus.not_started,
            start_date=None,
            due_date="2026-05-01",
            assigned_to=[],
        )
    ]
    service.save(tmp_path, "p1", tasks)
    loaded = service.load(tmp_path)
    assert loaded is not None
    assert loaded.plan_id == "p1"
    assert len(loaded.tasks) == 1
    assert loaded.tasks[0].task_id == "t1"
    assert loaded.tasks[0].due_date == "2026-05-01"


def test_archive_moves_snapshot(service, tmp_path):
    tasks = [
        TaskSnapshot(
            task_id="t1",
            title="T",
            bucket_id="b1",
            bucket_name="Phase 1",
            status=TaskStatus.not_started,
            start_date=None,
            due_date=None,
            assigned_to=[],
        )
    ]
    service.save(tmp_path, "p1", tasks)
    service.archive(tmp_path)
    archive_dir = tmp_path / "snapshot-archive"
    assert archive_dir.exists()
    archived = list(archive_dir.glob("planner-snapshot-*.json"))
    assert len(archived) == 1


def test_archive_no_op_when_no_snapshot(service, tmp_path):
    # Should not raise
    service.archive(tmp_path)
    assert not (tmp_path / "snapshot-archive").exists()


def test_save_overwrites_after_archive(service, tmp_path):
    tasks_v1 = [
        TaskSnapshot(
            task_id="t1", title="Old", bucket_id="b1", bucket_name="P1",
            status=TaskStatus.not_started, start_date=None, due_date=None, assigned_to=[]
        )
    ]
    tasks_v2 = [
        TaskSnapshot(
            task_id="t1", title="Updated", bucket_id="b1", bucket_name="P1",
            status=TaskStatus.completed, start_date=None, due_date=None, assigned_to=[]
        )
    ]
    service.save(tmp_path, "p1", tasks_v1)
    service.archive(tmp_path)
    service.save(tmp_path, "p1", tasks_v2)
    current = service.load(tmp_path)
    assert current.tasks[0].title == "Updated"
    assert len(list((tmp_path / "snapshot-archive").glob("*.json"))) == 1


# --- diff ---

@pytest.fixture
def old_snapshot():
    return SnapshotFile(
        taken_at="2026-04-15T10:00:00Z",
        plan_id="p1",
        tasks=[
            TaskSnapshot(
                task_id="t1", title="Build CLI", bucket_id="b1", bucket_name="Phase 1",
                status=TaskStatus.not_started, start_date=None, due_date="2026-05-01",
                assigned_to=[]
            ),
            TaskSnapshot(
                task_id="t2", title="Write tests", bucket_id="b1", bucket_name="Phase 1",
                status=TaskStatus.in_progress, start_date=None, due_date=None,
                assigned_to=["user-1"]
            ),
            TaskSnapshot(
                task_id="t3", title="Old task", bucket_id="b1", bucket_name="Phase 1",
                status=TaskStatus.not_started, start_date=None, due_date=None,
                assigned_to=[]
            ),
        ]
    )


def test_diff_detects_completed(service, old_snapshot):
    new_tasks = [
        TaskSnapshot(
            task_id="t1", title="Build CLI", bucket_id="b1", bucket_name="Phase 1",
            status=TaskStatus.completed, start_date=None, due_date="2026-05-01",
            assigned_to=[]
        ),
        TaskSnapshot(
            task_id="t2", title="Write tests", bucket_id="b1", bucket_name="Phase 1",
            status=TaskStatus.in_progress, start_date=None, due_date=None,
            assigned_to=["user-1"]
        ),
        TaskSnapshot(
            task_id="t3", title="Old task", bucket_id="b1", bucket_name="Phase 1",
            status=TaskStatus.not_started, start_date=None, due_date=None,
            assigned_to=[]
        ),
    ]
    diff = service.diff(old_snapshot, new_tasks, as_of="2026-04-16T10:00:00Z")
    assert len(diff.completed) == 1
    assert diff.completed[0].task_id == "t1"
    assert diff.progressed == []


def test_diff_detects_progressed(service, old_snapshot):
    new_tasks = [
        TaskSnapshot(
            task_id="t1", title="Build CLI", bucket_id="b1", bucket_name="Phase 1",
            status=TaskStatus.not_started, start_date=None, due_date="2026-05-01",
            assigned_to=[]
        ),
        TaskSnapshot(
            task_id="t2", title="Write tests", bucket_id="b1", bucket_name="Phase 1",
            status=TaskStatus.in_progress, start_date=None, due_date=None,
            assigned_to=["user-1"]
        ),
        # t1 stays not_started, t2 already in_progress so no change
        # Let's use t3 to go in_progress
        TaskSnapshot(
            task_id="t3", title="Old task", bucket_id="b1", bucket_name="Phase 1",
            status=TaskStatus.in_progress, start_date=None, due_date=None,
            assigned_to=[]
        ),
    ]
    diff = service.diff(old_snapshot, new_tasks, as_of="2026-04-16T10:00:00Z")
    assert len(diff.progressed) == 1
    assert diff.progressed[0].task_id == "t3"
    assert diff.completed == []


def test_diff_detects_added(service, old_snapshot):
    new_tasks = [
        TaskSnapshot(
            task_id="t1", title="Build CLI", bucket_id="b1", bucket_name="Phase 1",
            status=TaskStatus.not_started, start_date=None, due_date="2026-05-01",
            assigned_to=[]
        ),
        TaskSnapshot(
            task_id="t2", title="Write tests", bucket_id="b1", bucket_name="Phase 1",
            status=TaskStatus.in_progress, start_date=None, due_date=None,
            assigned_to=["user-1"]
        ),
        TaskSnapshot(
            task_id="t3", title="Old task", bucket_id="b1", bucket_name="Phase 1",
            status=TaskStatus.not_started, start_date=None, due_date=None,
            assigned_to=[]
        ),
        TaskSnapshot(
            task_id="t4", title="New human task", bucket_id="b2", bucket_name="Phase 2",
            status=TaskStatus.not_started, start_date=None, due_date=None,
            assigned_to=[]
        ),
    ]
    diff = service.diff(old_snapshot, new_tasks, as_of="2026-04-16T10:00:00Z")
    assert len(diff.added) == 1
    assert diff.added[0].task_id == "t4"


def test_diff_detects_removed(service, old_snapshot):
    new_tasks = [
        TaskSnapshot(
            task_id="t1", title="Build CLI", bucket_id="b1", bucket_name="Phase 1",
            status=TaskStatus.not_started, start_date=None, due_date="2026-05-01",
            assigned_to=[]
        ),
        TaskSnapshot(
            task_id="t2", title="Write tests", bucket_id="b1", bucket_name="Phase 1",
            status=TaskStatus.in_progress, start_date=None, due_date=None,
            assigned_to=["user-1"]
        ),
        # t3 removed
    ]
    diff = service.diff(old_snapshot, new_tasks, as_of="2026-04-16T10:00:00Z")
    assert "t3" in diff.removed


def test_diff_detects_field_changes(service, old_snapshot):
    new_tasks = [
        TaskSnapshot(
            task_id="t1", title="Build CLI", bucket_id="b1", bucket_name="Phase 1",
            status=TaskStatus.not_started, start_date=None, due_date="2026-06-01",  # changed
            assigned_to=[]
        ),
        TaskSnapshot(
            task_id="t2", title="Write tests", bucket_id="b2", bucket_name="Phase 2",  # bucket changed
            status=TaskStatus.in_progress, start_date=None, due_date=None,
            assigned_to=["user-1"]
        ),
        TaskSnapshot(
            task_id="t3", title="Old task", bucket_id="b1", bucket_name="Phase 1",
            status=TaskStatus.not_started, start_date=None, due_date=None,
            assigned_to=[]
        ),
    ]
    diff = service.diff(old_snapshot, new_tasks, as_of="2026-04-16T10:00:00Z")
    changed_ids = {c.task_id for c in diff.changed}
    assert "t1" in changed_ids
    assert "t2" in changed_ids
    t1_change = next(c for c in diff.changed if c.task_id == "t1")
    assert "due_date" in t1_change.fields
    assert t1_change.fields["due_date"]["from"] == "2026-05-01"
    assert t1_change.fields["due_date"]["to"] == "2026-06-01"


def test_diff_empty_when_no_changes(service, old_snapshot):
    new_tasks = list(old_snapshot.tasks)
    diff = service.diff(old_snapshot, new_tasks, as_of="2026-04-16T10:00:00Z")
    assert not diff.has_changes


def test_diff_since_and_as_of(service, old_snapshot):
    diff = service.diff(old_snapshot, list(old_snapshot.tasks), as_of="2026-04-16T10:00:00Z")
    assert diff.since == "2026-04-15T10:00:00Z"
    assert diff.as_of == "2026-04-16T10:00:00Z"

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from ms_planner.client import GraphClient
from ms_planner.models.snapshot import (
    SnapshotDiff,
    SnapshotFile,
    TaskChange,
    TaskSnapshot,
    TaskStatus,
    status_from_percent,
)
from ms_planner.services.buckets import BucketService
from ms_planner.services.tasks import TaskService

_TRACKED_FIELDS = ("due_date", "start_date", "bucket_id", "bucket_name", "assigned_to", "title")


class SnapshotService:
    def __init__(self, client: GraphClient):
        self._task_svc = TaskService(client)
        self._bucket_svc = BucketService(client)

    async def fetch(self, plan_id: str) -> list[TaskSnapshot]:
        tasks, buckets = (
            await self._task_svc.list(plan_id),
            await self._bucket_svc.list(plan_id),
        )
        bucket_names = {b.id: b.name for b in buckets}
        return [_to_snapshot(t, bucket_names) for t in tasks]

    def load(self, project_dir: Path) -> SnapshotFile | None:
        path = project_dir / "planner-snapshot.json"
        if not path.exists():
            return None
        return SnapshotFile.model_validate_json(path.read_text())

    def save(self, project_dir: Path, plan_id: str, tasks: list[TaskSnapshot]) -> None:
        snapshot = SnapshotFile(
            taken_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            plan_id=plan_id,
            tasks=tasks,
        )
        path = project_dir / "planner-snapshot.json"
        path.write_text(snapshot.model_dump_json(indent=2))

    def archive(self, project_dir: Path) -> None:
        path = project_dir / "planner-snapshot.json"
        if not path.exists():
            return
        archive_dir = project_dir / "snapshot-archive"
        archive_dir.mkdir(exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        shutil.copy2(path, archive_dir / f"planner-snapshot-{ts}.json")

    def diff(
        self,
        old: SnapshotFile,
        new_tasks: list[TaskSnapshot],
        as_of: str,
    ) -> SnapshotDiff:
        old_by_id = {t.task_id: t for t in old.tasks}
        new_by_id = {t.task_id: t for t in new_tasks}

        completed: list[TaskSnapshot] = []
        progressed: list[TaskSnapshot] = []
        added: list[TaskSnapshot] = []
        removed: list[str] = []
        changed: list[TaskChange] = []

        for task_id, new in new_by_id.items():
            if task_id not in old_by_id:
                added.append(new)
                continue
            old_task = old_by_id[task_id]
            # Status changes
            if old_task.status != TaskStatus.completed and new.status == TaskStatus.completed:
                completed.append(new)
            elif old_task.status == TaskStatus.not_started and new.status == TaskStatus.in_progress:
                progressed.append(new)
            # Field changes (only for non-status transitions already captured above)
            field_diff: dict = {}
            for field in _TRACKED_FIELDS:
                old_val = getattr(old_task, field)
                new_val = getattr(new, field)
                if old_val != new_val:
                    field_diff[field] = {"from": old_val, "to": new_val}
            if field_diff:
                changed.append(TaskChange(task_id=task_id, title=new.title, fields=field_diff))

        for task_id in old_by_id:
            if task_id not in new_by_id:
                removed.append(task_id)

        return SnapshotDiff(
            since=old.taken_at,
            as_of=as_of,
            completed=completed,
            progressed=progressed,
            added=added,
            removed=removed,
            changed=changed,
        )


def _to_snapshot(task, bucket_names: dict[str, str]) -> TaskSnapshot:
    return TaskSnapshot(
        task_id=task.id,
        title=task.title,
        bucket_id=task.bucket_id,
        bucket_name=bucket_names.get(task.bucket_id) if task.bucket_id else None,
        status=status_from_percent(task.percent_complete),
        start_date=task.start_date_time.date().isoformat() if task.start_date_time else None,
        due_date=task.due_date_time.date().isoformat() if task.due_date_time else None,
        assigned_to=list(task.assignments.keys()),
    )

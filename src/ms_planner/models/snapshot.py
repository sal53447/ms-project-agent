from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel


class TaskStatus(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"


def status_from_percent(percent_complete: int) -> TaskStatus:
    if percent_complete == 0:
        return TaskStatus.not_started
    if percent_complete == 100:
        return TaskStatus.completed
    return TaskStatus.in_progress


class TaskSnapshot(BaseModel):
    task_id: str
    title: str
    bucket_id: str | None
    bucket_name: str | None
    status: TaskStatus
    start_date: str | None  # YYYY-MM-DD
    due_date: str | None    # YYYY-MM-DD
    assigned_to: list[str]  # user IDs


class TaskChange(BaseModel):
    task_id: str
    title: str
    fields: dict[str, dict[str, Any]]  # {"due_date": {"from": "...", "to": "..."}}


class SnapshotFile(BaseModel):
    taken_at: str   # ISO-8601 timestamp
    plan_id: str
    tasks: list[TaskSnapshot]


class SnapshotDiff(BaseModel):
    since: str                  # taken_at of old snapshot
    as_of: str                  # taken_at of new snapshot
    completed: list[TaskSnapshot]
    progressed: list[TaskSnapshot]
    added: list[TaskSnapshot]
    removed: list[str]          # task_ids of tasks deleted from Planner
    changed: list[TaskChange]

    @property
    def has_changes(self) -> bool:
        return bool(
            self.completed
            or self.progressed
            or self.added
            or self.removed
            or self.changed
        )

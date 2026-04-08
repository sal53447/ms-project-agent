from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ChecklistItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str
    is_checked: bool = Field(False, alias="isChecked")


class Reference(BaseModel):
    alias: str | None = None
    type: str | None = None


class Task(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    plan_id: str | None = Field(None, alias="planId")
    bucket_id: str | None = Field(None, alias="bucketId")
    title: str
    assignments: dict[str, Any] = Field(default_factory=dict)
    percent_complete: int = Field(0, alias="percentComplete")
    priority: int = Field(5)
    start_date_time: datetime | None = Field(None, alias="startDateTime")
    due_date_time: datetime | None = Field(None, alias="dueDateTime")
    order_hint: str | None = Field(None, alias="orderHint")
    etag: str | None = Field(None, alias="@odata.etag")


class TaskDetails(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    description: str = ""
    checklist: dict[str, ChecklistItem] = Field(default_factory=dict)
    references: dict[str, Reference] = Field(default_factory=dict)
    etag: str | None = Field(None, alias="@odata.etag")

from __future__ import annotations

from typing import Any
from ms_planner.client import GraphClient
from ms_planner.models import Task, TaskDetails


class TaskService:
    def __init__(self, client: GraphClient):
        self._client = client

    async def list(self, plan_id: str) -> list[Task]:
        data = await self._client.get(f"/planner/plans/{plan_id}/tasks")
        return [Task.model_validate(item) for item in data["value"]]

    async def get(self, task_id: str) -> Task:
        data = await self._client.get(f"/planner/tasks/{task_id}")
        return Task.model_validate(data)

    async def get_details(self, task_id: str) -> TaskDetails:
        data = await self._client.get(f"/planner/tasks/{task_id}/details")
        return TaskDetails.model_validate(data)

    async def create(
        self,
        plan_id: str,
        title: str,
        *,
        bucket_id: str | None = None,
        assignments: list[str] | None = None,
    ) -> Task:
        body: dict[str, Any] = {"planId": plan_id, "title": title}
        if bucket_id:
            body["bucketId"] = bucket_id
        if assignments:
            body["assignments"] = {
                user_id: {
                    "@odata.type": "#microsoft.graph.plannerAssignment",
                    "orderHint": " !",
                }
                for user_id in assignments
            }
        data = await self._client.post("/planner/tasks", body)
        return Task.model_validate(data)

    async def update(self, task_id: str, **kwargs: Any) -> None:
        # Fetch task first to get the current ETag (required for PATCH)
        await self.get(task_id)
        body = {}
        key_map = {
            "percent_complete": "percentComplete",
            "start_date_time": "startDateTime",
            "due_date_time": "dueDateTime",
            "bucket_id": "bucketId",
            "order_hint": "orderHint",
        }
        for k, v in kwargs.items():
            api_key = key_map.get(k, k)
            body[api_key] = v
        await self._client.patch(f"/planner/tasks/{task_id}", body)

    async def update_details(self, task_id: str, **kwargs: Any) -> None:
        # Fetch details first to populate ETag cache (required for PATCH)
        await self._client.get(f"/planner/tasks/{task_id}/details")
        await self._client.patch(f"/planner/tasks/{task_id}/details", dict(kwargs))

    async def delete(self, task_id: str) -> None:
        await self._client.delete(f"/planner/tasks/{task_id}")

    async def list_user_tasks(self, user_id: str) -> list[Task]:
        data = await self._client.get(f"/users/{user_id}/planner/tasks")
        return [Task.model_validate(item) for item in data["value"]]

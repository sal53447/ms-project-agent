from ms_planner.client import GraphClient
from ms_planner.models import Plan


class PlanService:
    def __init__(self, client: GraphClient):
        self._client = client

    async def list(self, group_id: str) -> list[Plan]:
        data = await self._client.get(f"/groups/{group_id}/planner/plans")
        return [Plan.model_validate(item) for item in data["value"]]

    async def get(self, plan_id: str) -> Plan:
        data = await self._client.get(f"/planner/plans/{plan_id}")
        return Plan.model_validate(data)

    async def create(self, group_id: str, title: str) -> Plan:
        body = {
            "container": {
                "url": f"https://graph.microsoft.com/v1.0/groups/{group_id}",
                "type": "group",
            },
            "title": title,
        }
        data = await self._client.post("/planner/plans", body)
        return Plan.model_validate(data)

    async def update(self, plan_id: str, **kwargs: str) -> None:
        await self._client.patch(f"/planner/plans/{plan_id}", dict(kwargs))

    async def delete(self, plan_id: str) -> None:
        await self._client.delete(f"/planner/plans/{plan_id}")

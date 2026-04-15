from ms_planner.client import GraphClient
from ms_planner.models import Bucket


class BucketService:
    def __init__(self, client: GraphClient):
        self._client = client

    async def list(self, plan_id: str) -> list[Bucket]:
        data = await self._client.get(f"/planner/plans/{plan_id}/buckets")
        return [Bucket.model_validate(item) for item in data["value"]]

    async def create(self, plan_id: str, name: str) -> Bucket:
        body = {"planId": plan_id, "name": name}
        data = await self._client.post("/planner/buckets", body)
        return Bucket.model_validate(data)

    async def get(self, bucket_id: str) -> Bucket:
        data = await self._client.get(f"/planner/buckets/{bucket_id}")
        return Bucket.model_validate(data)

    async def update(self, bucket_id: str, **kwargs: str) -> None:
        # Fetch bucket first to get the current ETag (required for PATCH)
        await self.get(bucket_id)
        await self._client.patch(f"/planner/buckets/{bucket_id}", dict(kwargs))

    async def delete(self, bucket_id: str) -> None:
        # Fetch bucket first to get the current ETag (required for DELETE)
        await self.get(bucket_id)
        await self._client.delete(f"/planner/buckets/{bucket_id}")

from ms_planner.client import GraphClient
from ms_planner.models.user import User


class UserService:
    def __init__(self, client: GraphClient):
        self._client = client

    async def get(self, user_id_or_email: str) -> User:
        """Fetch a user by ID or email (userPrincipalName)."""
        data = await self._client.get(f"/users/{user_id_or_email}")
        return User.model_validate(data)

    async def resolve_to_id(self, id_or_email: str) -> str:
        """Return a user ID. If the input looks like an email, resolve it via
        the Graph API. Otherwise return it unchanged (assumed to be a GUID)."""
        if "@" in id_or_email:
            user = await self.get(id_or_email)
            return user.id
        return id_or_email

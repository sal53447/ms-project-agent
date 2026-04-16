from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    display_name: str | None = Field(None, alias="displayName")
    mail: str | None = None
    user_principal_name: str | None = Field(None, alias="userPrincipalName")

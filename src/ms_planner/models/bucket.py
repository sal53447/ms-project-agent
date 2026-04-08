from pydantic import BaseModel, ConfigDict, Field


class Bucket(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    plan_id: str = Field(alias="planId")
    name: str
    order_hint: str | None = Field(None, alias="orderHint")
    etag: str | None = Field(None, alias="@odata.etag")

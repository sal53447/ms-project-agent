from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class PlanContainer(BaseModel):
    container_id: str = Field(alias="containerId")
    type: str


class Plan(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    owner: str | None = None
    created_date_time: datetime | None = Field(None, alias="createdDateTime")
    container: PlanContainer | None = None
    etag: str | None = Field(None, alias="@odata.etag")

from pydantic import BaseModel, ConfigDict


class Assignment(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    order_hint: str | None = None

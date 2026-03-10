import datetime

from pydantic import BaseModel, ConfigDict


class LinkSchemaIn(BaseModel):
    url: str
    project_id: int

class LinkSchemaOut(BaseModel):
    id: int
    url: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LinkSchemaIn(BaseModel):
    url: str
    project_id: int


class LinkSchemaUpdate(BaseModel):
    url: Optional[str] = None


class LinkSchemaFilter(BaseModel):
    url: Optional[str] = None
    project_id: Optional[int] = None
    user_id: Optional[int] = None


class LinkSchemaOut(BaseModel):
    id: int
    url: str
    project_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

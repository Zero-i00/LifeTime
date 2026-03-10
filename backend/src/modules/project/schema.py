import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from modules.link.schema import LinkSchemaOut


class ProjectSchemaIn(BaseModel):
    name: str


class ProjectSchemaUpdate(BaseModel):
    name: Optional[str] = None

class ProjectSchemaOut(ProjectSchemaIn):
    id: int

    created_at: datetime.datetime
    updated_at: datetime.datetime

    links: List['LinkSchemaOut'] = []

    model_config = ConfigDict(from_attributes=True)

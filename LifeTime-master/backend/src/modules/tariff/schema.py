import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TariffSchemaIn(BaseModel):
    title: str
    description: Optional[str] = None

    price: Decimal
    old_price: Optional[Decimal] = None

    link_limit: int
    project_limit: int


class TariffSchemaOut(TariffSchemaIn):
    id: int
    is_initial: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


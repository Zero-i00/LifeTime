import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class TariffSchemaIn(BaseModel):
    title: str
    description: str

    price: Decimal
    old_price: Decimal

    link_limit: int
    project_limit: int


class TariffSchemaOut(TariffSchemaIn):
    id: int
    is_initial: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


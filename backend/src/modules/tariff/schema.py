from decimal import Decimal
from pydantic import BaseModel

class TariffSchemaIn(BaseModel):
    title: str
    description: str

    price: Decimal
    old_price: Decimal

    link_limit: int
    project_limit: int


class TariffSchemaOut(BaseModel):
    id: int

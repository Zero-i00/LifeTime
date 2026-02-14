import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from modules.tariff.schema import TariffSchemaOut


class UserSchemaIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserSchemaUpdate(UserSchemaIn):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class UserSchemaOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    tariff: TariffSchemaOut
    last_login_at: datetime.datetime

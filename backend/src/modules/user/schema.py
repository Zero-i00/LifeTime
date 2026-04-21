import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from modules.tariff.schema import TariffSchemaOut

class UserSchemaIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    tariff_id: int
    last_login_at: datetime.datetime

class UserSchemaUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    tariff_id: Optional[int] = None
    last_login_at: Optional[datetime.datetime] = None

class UserSchemaOut(BaseModel):
    id: int
    full_name: str
    email: str
    tariff: TariffSchemaOut
    last_login_at: datetime.datetime
    role: str

    model_config = ConfigDict(from_attributes=True)
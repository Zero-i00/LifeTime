from enum import Enum

from pydantic import BaseModel, EmailStr

from database.models.user import UserRole
from modules.user.schema import UserSchemaOut


class TokenEnum(Enum):
    ACCESS_TOKEN = 'access_token'
    REFRESH_TOKEN = 'refresh_token'


class TokenType(Enum):
    BEARER = "Bearer"


class AccessTokenPayload(BaseModel):
    sub: str
    email: str
    user_id: int
    role: UserRole
    token_type: TokenEnum = TokenEnum.ACCESS_TOKEN.value


class RefreshTokenPayload(BaseModel):
    sub: str
    user_id: int
    token_type: TokenEnum = TokenEnum.REFRESH_TOKEN.value


class LoginSchemaIn(BaseModel):
    email: EmailStr
    password: str


class RegisterSchemaIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class AuthSchemaOut(BaseModel):
    access_token: str
    user: UserSchemaOut
    token_type: TokenType = TokenType.BEARER

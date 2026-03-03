from enum import Enum

from pydantic import BaseModel, EmailStr

from modules.user.schema import UserSchemaOut


class TokenEnum(Enum):
    ACCESS_TOKEN = 'access_token'
    REFRESH_TOKEN = 'refresh_token'


class TokenType(Enum):
    BEARER = "Bearer"


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

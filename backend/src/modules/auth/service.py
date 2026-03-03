import datetime
from datetime import timedelta

import jwt
from fastapi import (
    status,
    Request,
    Response,
    HTTPException, Depends
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings, IS_DEBUG
from database.models.user import UserModel
from modules.auth.schema import LoginSchemaIn, TokenEnum, RegisterSchemaIn
from modules.auth.strategies.token import token_strategy
from modules.tariff.service import tariff_service
from modules.user.schema import UserSchemaIn
from modules.user.service import user_service
from utils.normalize import normalize_email

http_bearer = HTTPBearer()

class AuthService:
    def __init__(self) -> None:
        self.invalid_token_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid jwt token",
        )

        self.invalid_login_or_password_exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password",
        )


    async def register(self, session: AsyncSession, data: RegisterSchemaIn) -> UserModel:
        is_exist_query = select(UserModel).where(UserModel.email == normalize_email(str(data.email)))
        is_exist_result = await session.execute(is_exist_query)
        if is_exist_result.scalars().first():
            raise user_service.already_exists_exception

        tariff = await tariff_service.get_initial_tariff(session)

        payload = UserSchemaIn(
            email=data.email,
            password=data.password,
            full_name=data.full_name,
            tariff_id=tariff.id,
            last_login_at=datetime.datetime.now(),
        )

        user = await user_service.create(session, payload)
        return user

    async def login(self, session: AsyncSession, data: LoginSchemaIn) -> UserModel:
        email = normalize_email(str(data.email))

        user = await user_service.get_by_email(session, email)

        if not user_service.validate_password(data.password, user.password):
            raise self.invalid_login_or_password_exception

        return user

    async def logout(self, session: AsyncSession) -> None:
        # TODO jwt refresh token black list
        pass


    async def refresh(self, session: AsyncSession, request: Request) -> UserModel:
        payload = self.get_refresh_payload(request)

        user_id = payload.get('user_id', None)
        if user_id is None:
            raise self.invalid_token_exception

        user = await user_service.retrieve(session, user_id)
        return user

    def get_access_token_payload(self, credentials: HTTPAuthorizationCredentials = Depends(http_bearer)) -> dict:
        access_token = credentials.credentials

        try:
            return token_strategy.decode_jwt(
                token=access_token
            )
        except jwt.InvalidTokenError as e:
            raise self.invalid_token_exception

    def get_refresh_payload(self, reqeust: Request) -> dict:
        token = reqeust.cookies.get(TokenEnum.REFRESH_TOKEN.value, None)
        if token is None:
            raise self.invalid_token_exception

        payload = token_strategy.decode_jwt(token)
        if payload is None:
            raise self.invalid_token_exception

        return payload


    @staticmethod
    def create_access_token(user: UserModel) -> str:
        payload = {
            'sub': user.email,
            'user_id': user.id,
            'email': user.email,
            'type': TokenEnum.ACCESS_TOKEN.value
        }

        return token_strategy.encode_jwt(payload)

    @staticmethod
    def create_refresh_token(user: UserModel) -> str:
        payload = {
            'sub': user.email,
            'user_id': user.id,
            'type': TokenEnum.REFRESH_TOKEN.value
        }

        return token_strategy.encode_jwt(
            payload=payload,
            expire_timedelta=timedelta(days=settings.auth.refresh_token_expire_days)
        )

    @staticmethod
    def set_refresh_token_to_cookie(response: Response, refresh_token: str):
        response.set_cookie(
            key=TokenEnum.REFRESH_TOKEN.value,
            value=refresh_token,
            httponly=True,
            secure=True,
            domain=settings.app.host,
            samesite='none' if IS_DEBUG else 'strict',
            expires=int(timedelta(days=settings.auth.refresh_token_expire_days).total_seconds())
        )


auth_service = AuthService()

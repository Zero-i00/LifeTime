import bcrypt
from fastapi import (
    status,
    HTTPException
)

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user import UserModel
from modules.user.schema import UserSchemaOut, UserSchemaIn, UserSchemaUpdate
from utils.normalize import normalize_email


class UserService:
    def __init__(self) -> None:
        self.not_found_exception = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

        self.already_exists_exception = HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )


    async def list(self, session: AsyncSession) -> Sequence[UserModel]:
        query = select(UserModel)
        result = await session.execute(query)

        return result.scalars().all()

    async def retrieve(self, session: AsyncSession, user_id: int) -> type[UserModel]:
        user = await session.get(UserModel, user_id)
        if user is None:
            raise self.not_found_exception

        return user

    async def get_by_email(self, session: AsyncSession, email: str) -> type[UserModel]:
        query = select(UserModel).where(UserModel.email == email)
        result = await session.execute(query)

        user = result.scalars().one_or_none()
        if user is None:
            raise self.not_found_exception

        return user


    async def create(self, session: AsyncSession, obj: UserSchemaIn) -> UserModel:
        user = self.to_model(obj)
        user.password = self.hash_password(obj.password)

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user

    async def update(self, session: AsyncSession, user_id: int, obj: UserSchemaUpdate) -> type[UserModel]:
        user = await self.retrieve(session, user_id)

        if obj.email:
            user.email = normalize_email(str(obj.email))

        if obj.full_name:
            user.full_name = obj.full_name

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user

    async def destroy(self, session: AsyncSession, user_id: int) -> bool:
        user = await self.retrieve(session, user_id)
        await session.delete(user)
        return True


    @staticmethod
    def hash_password(password: str) -> bytes:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt)

    @staticmethod
    def validate_password(password: str, hashed_password: bytes) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password)

    @staticmethod
    def to_schema(obj: UserModel) -> UserSchemaOut:
        return UserSchemaOut.model_validate(obj)

    @staticmethod
    def to_model(obj: UserSchemaIn) -> UserModel:
        return UserModel(
            email=normalize_email(str(obj.email)),
            full_name=obj.full_name,
        )


user_service = UserService()

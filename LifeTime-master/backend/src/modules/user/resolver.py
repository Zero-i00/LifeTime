from fastapi import APIRouter
from fastapi.params import Depends

from database.session import AsyncSessionDep
from modules.auth.service import auth_service
from modules.user.schema import UserSchemaOut, UserSchemaUpdate
from modules.auth.schema import AccessTokenPayload
from modules.user.service import user_service


class UserResolver:
    router = APIRouter(
        prefix="/user",
        tags=["User"]
    )

    @staticmethod
    @router.get('/profile')
    async def profile(
        session: AsyncSessionDep,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload)
    ) -> UserSchemaOut:
        user = await user_service.retrieve(session, credentials.user_id)
        return user_service.to_schema(user)

    @staticmethod
    @router.patch('/profile')
    async def update_profile(
        session: AsyncSessionDep,
        user_update: UserSchemaUpdate,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload)
    ) -> UserSchemaOut:
        """
        Обновление профиля текущего пользователя.
        Все поля опциональны - обновляются только переданные.
        """
        updated_user = await user_service.update(
            session, 
            credentials.user_id, 
            user_update
        )
        return user_service.to_schema(updated_user)


user_resolver = UserResolver()
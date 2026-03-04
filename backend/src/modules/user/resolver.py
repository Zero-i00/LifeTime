from fastapi import APIRouter
from fastapi.params import Depends

from database.session import AsyncSessionDep
from modules.auth.service import auth_service
from modules.user.schema import UserSchemaOut
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



user_resolver = UserResolver()

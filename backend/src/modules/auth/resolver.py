from fastapi import (
    status,
    Request,
    Response,
    APIRouter,
)
from database.session import AsyncSessionDep
from modules.auth.schema import AuthSchemaOut, LoginSchemaIn, RegisterSchemaIn
from modules.auth.service import auth_service
from modules.user.service import user_service


class AuthResolver:
    router = APIRouter(
        prefix="/auth",
        tags=["Auth"],
    )

    @staticmethod
    @router.post("/register", status_code=status.HTTP_200_OK)
    async def register(
        response: Response,
        session: AsyncSessionDep,
        data: RegisterSchemaIn
    ) -> AuthSchemaOut:
        user = await auth_service.register(session, data)

        access_token = auth_service.create_access_token(user)

        refresh_token = auth_service.create_refresh_token(user)
        auth_service.set_refresh_token_to_cookie(response, refresh_token)

        return AuthSchemaOut(
            access_token=access_token,
            user=user_service.to_schema(user),
        )

    @staticmethod
    @router.post("/login", status_code=status.HTTP_200_OK)
    async def login(
        response: Response,
        session: AsyncSessionDep,
        data: LoginSchemaIn
    ) -> AuthSchemaOut:
        user = await auth_service.login(session, data)

        access_token = auth_service.create_access_token(user)

        refresh_token = auth_service.create_refresh_token(user)
        auth_service.set_refresh_token_to_cookie(response, refresh_token)

        return AuthSchemaOut(
            access_token=access_token,
            user=user_service.to_schema(user),
        )

    @staticmethod
    @router.post("/logout", status_code=status.HTTP_200_OK)
    async def logout(
        session: AsyncSessionDep,
    ) -> None:
        await auth_service.logout(session)



    @staticmethod
    @router.post("/refresh_token", status_code=status.HTTP_200_OK)
    async def refresh_token(
        request: Request,
        response: Response,
        session: AsyncSessionDep,
    ) -> AuthSchemaOut:
        user = await auth_service.refresh(session, request)

        access_token = auth_service.create_access_token(user)

        refresh_token = auth_service.create_refresh_token(user)
        auth_service.set_refresh_token_to_cookie(response, refresh_token)

        return AuthSchemaOut(
            access_token=access_token,
            user=user_service.to_schema(user),
        )


auth_resolver = AuthResolver()

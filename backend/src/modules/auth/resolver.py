from fastapi import (
    status,
    Request,
    Response,
    APIRouter,
)
from database.session import AsyncSessionDep
from modules.auth.schema import AuthSchemaOut, AuthSchemaIn
from modules.auth.service import auth_service


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
        data: AuthSchemaIn
    ) -> AuthSchemaOut:
        user = await auth_service.register(session, data)

        access_token = auth_service.create_access_token(session)

        refresh_token = auth_service.create_refresh_token(session)
        auth_service.set_refresh_token_to_cookie(response, refresh_token)

        return AuthSchemaOut(
            user=user,
            access_token=access_token,
        )

    @staticmethod
    @router.post("/login", status_code=status.HTTP_200_OK)
    async def login(
        response: Response,
        session: AsyncSessionDep,
        data: AuthSchemaIn
    ) -> AuthSchemaOut:
        user = await auth_service.login(session, data)

        access_token = auth_service.create_access_token(session)

        refresh_token = auth_service.create_refresh_token(session)
        auth_service.set_refresh_token_to_cookie(response, refresh_token)

        return AuthSchemaOut(
            user=user,
            access_token=access_token,
        )

    @staticmethod
    @router.post("/logout", status_code=status.HTTP_200_OK)
    async def logout(
        session: AsyncSessionDep,
    ) -> None:
        await auth_service.logout(session)



    @staticmethod
    @router.post("/refresh", status_code=status.HTTP_200_OK)
    async def refresh(
        request: Request,
        response: Response,
        session: AsyncSessionDep,
    ) -> AuthSchemaOut:
        user = await auth_service.refresh(session, request)

        access_token = auth_service.create_access_token(session)

        refresh_token = auth_service.create_refresh_token(session)
        auth_service.set_refresh_token_to_cookie(response, refresh_token)

        return AuthSchemaOut(
            user=user,
            access_token=access_token,
        )


auth_resolver = AuthResolver()

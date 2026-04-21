from typing import List, Optional

from fastapi import APIRouter, status, Depends, Query

from database.models.user import UserRole
from database.session import AsyncSessionDep
from modules.auth.schema import AccessTokenPayload
from modules.auth.service import auth_service
from modules.link.schema import LinkSchemaOut, LinkSchemaIn, LinkSchemaUpdate, LinkSchemaFilter
from modules.link.service import link_service


class LinkResolver:
    router = APIRouter(
        prefix="/link",
        tags=["Link"],
    )

    @staticmethod
    @router.get("/", status_code=status.HTTP_200_OK)
    async def list(
        session: AsyncSessionDep,
        url: Optional[str] = Query(None),
        project_id: Optional[int] = Query(None),
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> List[LinkSchemaOut]:
        is_admin = credentials.role == UserRole.ADMIN.value
        filters = LinkSchemaFilter(
            url=url,
            project_id=project_id,
            user_id=None if is_admin else credentials.user_id,
        )
        links = await link_service.list(session, filters)
        return [link_service.to_schema(link) for link in links]

    @staticmethod
    @router.get("/{link_id}", status_code=status.HTTP_200_OK)
    async def retrieve(
        session: AsyncSessionDep,
        link_id: int,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> LinkSchemaOut:
        is_admin = credentials.role == UserRole.ADMIN.value
        filters = LinkSchemaFilter(user_id=None if is_admin else credentials.user_id)
        return await link_service.retrieve_with_schema(session, link_id, filters)

    @staticmethod
    @router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(
        session: AsyncSessionDep,
        obj: LinkSchemaIn,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> LinkSchemaOut:
        link = await link_service.create(session, credentials.user_id, obj)
        return link_service.to_schema(link)

    @staticmethod
    @router.patch("/{link_id}", status_code=status.HTTP_200_OK)
    async def update(
        session: AsyncSessionDep,
        link_id: int,
        obj: LinkSchemaUpdate,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> LinkSchemaOut:
        link = await link_service.update(session, link_id, credentials.user_id, obj)
        return link_service.to_schema(link)

    @staticmethod
    @router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete(
        session: AsyncSessionDep,
        link_id: int,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> None:
        await link_service.delete(session, link_id, credentials.user_id)

    @staticmethod
    @router.post("/{link_id}/schema/accept", status_code=status.HTTP_204_NO_CONTENT)
    async def accept_schema(
        session: AsyncSessionDep,
        link_id: int,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> None:
        """Принимает изменения схемы: текущий different становится новым baseline."""
        await link_service.accept_schema(session, link_id, credentials.user_id)

    @staticmethod
    @router.get("/{link_id}/schema/{version}", status_code=status.HTTP_200_OK)
    async def get_schema_version(
        session: AsyncSessionDep,
        link_id: int,
        version: str,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> dict:
        """Получает конкретную версию schema.json из бакета link-schemas."""
        return await link_service.get_schema_version(
            session, link_id, credentials.user_id, version
        )


link_resolver = LinkResolver()

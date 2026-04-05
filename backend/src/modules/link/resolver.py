import json
from typing import List, Optional

from fastapi import APIRouter, status, Depends, Query, HTTPException

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
        filters = LinkSchemaFilter(url=url, project_id=project_id, user_id=None if is_admin else credentials.user_id)

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

        link = await link_service.retrieve(session, link_id, filters)
        return link_service.to_schema(link)

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
    @router.get("/{link_id}/schema", status_code=status.HTTP_200_OK)
    async def get_link_schema(
        session: AsyncSessionDep,
        link_id: int,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> dict:
        """
        Получает schema.json для указанной ссылки из S3
        """
        schema = await link_service.get_link_schema(session, link_id, credentials.user_id)
        
        if schema is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schema not found"
            )
        
        return schema

    @staticmethod
    @router.get("/{link_id}/schema/{version}", status_code=status.HTTP_200_OK)
    async def get_link_schema_version(
        session: AsyncSessionDep,
        link_id: int,
        version: str,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> dict:
        """
        Получает конкретную версию schema.json для указанной ссылки из S3
        """
        # Проверяем существование ссылки и права доступа
        link = await session.get(LinkModel, link_id)
        if link is None or link.project.user_id != credentials.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Link not found"
            )
        

        key = f"{credentials.user_id}/{link_id}/schemas/schema_{version}.json"
        

        existing = await link_service.s3_client.get_object(link_service.schema_bucket, key)
        
        if existing:
            try:
                return json.loads(existing)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Invalid JSON format in schema file"
                )
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema version {version} not found"
        )


link_resolver = LinkResolver()
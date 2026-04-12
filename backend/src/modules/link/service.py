import json
from typing import Optional, Sequence

from fastapi import status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import LinkModel, ProjectModel
from modules.link.schema import LinkSchemaOut, LinkSchemaIn, LinkSchemaUpdate, LinkSchemaFilter
from lib.s3 import s3_client
from modules.link.strategies.check import check_strategy

class LinkService:
    def __init__(self):
        self.not_found_exception = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
        self.s3_client = s3_client
        self.schema_bucket = "link-schemas"  

    async def list(self, session: AsyncSession, filters: LinkSchemaFilter) -> Sequence[LinkModel]:
        query = select(LinkModel)

        if filters.url is not None:
            query = query.where(LinkModel.url.ilike(f"%{filters.url}%"))
        if filters.project_id is not None:
            query = query.where(LinkModel.project_id == filters.project_id)
        if filters.user_id is not None:
            query = query.join(LinkModel.project).where(ProjectModel.user_id == filters.user_id)

        result = await session.execute(query)
        return result.scalars().all()

    async def retrieve(self, session: AsyncSession, link_id: int, filters: LinkSchemaFilter) -> LinkModel:
        link = await session.get(LinkModel, link_id)
        if link is None:
            raise self.not_found_exception
        if filters.user_id is not None and link.project.user_id != filters.user_id:
            raise self.not_found_exception
        return link

    async def create(self, session: AsyncSession, user_id: int, obj: LinkSchemaIn) -> LinkModel:
        project = await session.get(ProjectModel, obj.project_id)
        if project is None or project.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        link = LinkModel(url=obj.url, project_id=obj.project_id)
        session.add(link)
        await session.commit()
        await session.refresh(link)

        return link

    async def update(self, session: AsyncSession, link_id: int, user_id: int, obj: LinkSchemaUpdate) -> LinkModel:
        link = await session.get(LinkModel, link_id)
        if link is None or link.project.user_id != user_id:
            raise self.not_found_exception

        if obj.url is not None:
            link.url = obj.url

        await session.commit()
        await session.refresh(link)

        return link

    async def delete(self, session: AsyncSession, link_id: int, user_id: int) -> None:
        link = await session.get(LinkModel, link_id)
        if link is None or link.project.user_id != user_id:
            raise self.not_found_exception

        await session.delete(link)
        await session.commit()

    async def get_link_schema(self, session: AsyncSession, link_id: int, user_id: int) -> Optional[dict]:
        """
        Получает schema.json из S3 хранилища по link_id
        
        Args:
            session: сессия БД
            link_id: ID ссылки
            user_id: ID пользователя для проверки прав
            
        Returns:
            dict: содержимое schema.json или None если файл не найден
        """
     
        link = await session.get(LinkModel, link_id)
        if link is None or link.project.user_id != user_id:
            raise self.not_found_exception
        

        # TODO: replaced in Task 5 with SchemaStrategy.get_snapshot
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schema not available yet")

    @staticmethod
    def to_schema(obj: LinkModel) -> LinkSchemaOut:
        return LinkSchemaOut(
            id=obj.id,
            url=obj.url,
            project_id=obj.project_id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


link_service = LinkService()
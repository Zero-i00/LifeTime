from typing import Sequence

from fastapi import (
    status,
    HTTPException,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import ProjectModel
from modules.link.service import link_service
from modules.project.schema import ProjectSchemaOut, ProjectSchemaIn, ProjectSchemaUpdate


class ProjectService:
    def __init__(self):
        self.not_found_exception = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    async def list(self, session: AsyncSession) -> Sequence[ProjectModel]:
        query = select(ProjectModel)
        result = await session.execute(query)

        return result.scalars().all()

    async def retrieve(self, session: AsyncSession, project_id: int) -> type[ProjectModel]:
        project = await session.get(ProjectModel, project_id)
        if project is None:
            raise self.not_found_exception

        return project

    async def create(self, session: AsyncSession, user_id: int, obj: ProjectSchemaIn) -> ProjectModel:
        project = self.to_model(obj)
        project.user_id = user_id

        session.add(project)
        await session.commit()
        await session.refresh(project)

        return project

    async def update(self, session: AsyncSession, user_id: int, obj: ProjectSchemaUpdate) -> ProjectModel:
        ...

    @staticmethod
    def to_schema(obj: ProjectModel) -> ProjectSchemaOut:
        return ProjectSchemaOut(
            id=obj.id,
            name=obj.name,
            links=[
                link_service.to_schema(link)
                for link in obj.links
            ],
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    @staticmethod
    def to_model(obj: ProjectSchemaIn) -> ProjectModel:
        return ProjectModel(
            name=obj.name,
        )


project_service = ProjectService()

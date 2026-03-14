from typing import Sequence

from fastapi import status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import ProjectModel
from modules.link.service import link_service
from modules.project.schema import ProjectSchemaOut, ProjectSchemaIn, ProjectSchemaUpdate, ProjectSchemaFilter


class ProjectService:
    def __init__(self):
        self.not_found_exception = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    async def list(self, session: AsyncSession, filters: ProjectSchemaFilter) -> Sequence[ProjectModel]:
        query = select(ProjectModel)

        if filters.name is not None:
            query = query.where(ProjectModel.name.ilike(f"%{filters.name}%"))
        if filters.user_id is not None:
            query = query.where(ProjectModel.user_id == filters.user_id)

        result = await session.execute(query)
        return result.scalars().all()

    async def retrieve(self, session: AsyncSession, project_id: int, filters: ProjectSchemaFilter) -> ProjectModel:
        project = await session.get(ProjectModel, project_id)
        if project is None:
            raise self.not_found_exception

        if filters.user_id is not None and project.user_id != filters.user_id:
            raise self.not_found_exception

        return project

    async def create(self, session: AsyncSession, user_id: int, obj: ProjectSchemaIn) -> ProjectModel:
        project = self.to_model(obj)
        project.user_id = user_id

        session.add(project)
        await session.commit()
        await session.refresh(project)

        return project

    async def update(self, session: AsyncSession, project_id: int, user_id: int, obj: ProjectSchemaUpdate) -> ProjectModel:
        project = await session.get(ProjectModel, project_id)
        if project is None or project.user_id != user_id:
            raise self.not_found_exception

        if obj.name is not None:
            project.name = obj.name

        await session.commit()
        await session.refresh(project)

        return project

    async def delete(self, session: AsyncSession, project_id: int, user_id: int) -> None:
        project = await session.get(ProjectModel, project_id)
        if project is None or project.user_id != user_id:
            raise self.not_found_exception

        await session.delete(project)
        await session.commit()

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

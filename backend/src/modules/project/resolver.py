from typing import List, Optional

from fastapi import APIRouter, status, Depends, Query

from database.models.user import UserRole
from database.session import AsyncSessionDep
from modules.auth.schema import AccessTokenPayload
from modules.auth.service import auth_service
from modules.project.schema import ProjectSchemaOut, ProjectSchemaIn, ProjectSchemaUpdate, ProjectSchemaFilter
from modules.project.service import project_service


class ProjectResolver:
    router = APIRouter(
        prefix="/project",
        tags=["Project"],
    )

    @staticmethod
    @router.get("/", status_code=status.HTTP_200_OK)
    async def list(
        session: AsyncSessionDep,
        name: Optional[str] = Query(None),
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> List[ProjectSchemaOut]:
        is_admin = credentials.role == UserRole.ADMIN.value
        filters = ProjectSchemaFilter(name=name, user_id=None if is_admin else credentials.user_id)

        projects = await project_service.list(session, filters)
        return [project_service.to_schema(p) for p in projects]

    @staticmethod
    @router.get("/{project_id}", status_code=status.HTTP_200_OK)
    async def retrieve(
        session: AsyncSessionDep,
        project_id: int,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> ProjectSchemaOut:
        is_admin = credentials.role == UserRole.ADMIN.value
        filters = ProjectSchemaFilter(user_id=None if is_admin else credentials.user_id)

        project = await project_service.retrieve(session, project_id, filters)
        return project_service.to_schema(project)

    @staticmethod
    @router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(
        session: AsyncSessionDep,
        obj: ProjectSchemaIn,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> ProjectSchemaOut:
        project = await project_service.create(session, credentials.user_id, obj)
        return project_service.to_schema(project)

    @staticmethod
    @router.patch("/{project_id}", status_code=status.HTTP_200_OK)
    async def update(
        session: AsyncSessionDep,
        project_id: int,
        obj: ProjectSchemaUpdate,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> ProjectSchemaOut:
        project = await project_service.update(session, project_id, credentials.user_id, obj)
        return project_service.to_schema(project)

    @staticmethod
    @router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete(
        session: AsyncSessionDep,
        project_id: int,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> None:
        await project_service.delete(session, project_id, credentials.user_id)


project_resolver = ProjectResolver()

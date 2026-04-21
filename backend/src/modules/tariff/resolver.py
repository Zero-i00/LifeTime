from typing import List

from fastapi import APIRouter, status
from fastapi.params import Depends

from database.models.user import UserRole
from database.session import AsyncSessionDep
from modules.auth.guards.role_required import role_required
from modules.auth.schema import AccessTokenPayload
from modules.tariff.schema import TariffSchemaOut,TariffSchemaIn
from modules.tariff.service import tariff_service


class TariffResolver:
    router = APIRouter(
        prefix="/tariff",
        tags=["Tariff"],
    )

    @staticmethod
    @router.get("/", status_code=status.HTTP_200_OK)
    async def list(
        session: AsyncSessionDep
    ) -> List[TariffSchemaOut]:
        data = await tariff_service.list(session)

        return [tariff_service.to_schema(tariff) for tariff in data]

    @staticmethod
    @router.get("/{tariff_id}", status_code=status.HTTP_200_OK)
    async def retrieve(
            session: AsyncSessionDep,
            tariff_id: int
    ) -> TariffSchemaOut:
        data = await tariff_service.retrieve(session, tariff_id)
        return tariff_service.to_schema(data)

    @staticmethod
    @router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(
            session: AsyncSessionDep,
            obj: TariffSchemaIn,
            _: AccessTokenPayload = Depends(role_required([UserRole.ADMIN]))
    ) -> TariffSchemaOut:
        data = await tariff_service.create(session, obj)
        return tariff_service.to_schema(data)


tariff_resolver = TariffResolver()

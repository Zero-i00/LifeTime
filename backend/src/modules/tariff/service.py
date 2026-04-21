from typing import Sequence

from fastapi import (
    status,
    HTTPException,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import TariffModel
from modules.tariff.schema import TariffSchemaOut, TariffSchemaIn


class TariffService:
    def __init__(self) -> None:
        self.not_found_exception = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tariff not found"
        )

    async def list(self, session: AsyncSession) -> Sequence[TariffModel]:
        query = select(TariffModel)
        result = await session.execute(query)

        return result.scalars().all()

    async def retrieve(self, session: AsyncSession, tariff_id: int) -> type[TariffModel]:
        tariff = await session.get(TariffModel, tariff_id)
        if not tariff:
            raise self.not_found_exception

        return tariff

    async def get_initial_tariff(self, session: AsyncSession) -> type[TariffModel]:
        query = select(TariffModel).where(TariffModel.is_initial == True)
        result = await session.execute(query)

        tariff = result.scalars().first()
        if not tariff:
            raise self.not_found_exception

        return tariff

    async def create(self, session: AsyncSession, obj: TariffSchemaIn) -> TariffModel:
        tariff = self.to_model(obj)

        session.add(tariff)
        await session.commit()
        await session.refresh(tariff)

        return tariff

    @staticmethod
    def to_schema(obj: type[TariffModel]) -> TariffSchemaOut:
        return TariffSchemaOut.model_validate(obj)

    @staticmethod
    def to_model(obj: TariffSchemaIn) -> TariffModel:
        return TariffModel(
            title=obj.title,
            description=obj.description,
            price=obj.price,
            old_price=obj.old_price,
            link_limit=obj.link_limit,
            project_limit=obj.project_limit,
            is_initial=True
        )

tariff_service = TariffService()

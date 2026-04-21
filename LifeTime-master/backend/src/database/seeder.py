from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import TariffModel
from database.session import session_factory


async def seed_initial_tariff(session: AsyncSession) -> None:
    query = select(TariffModel).where(TariffModel.is_initial == True)
    result = await session.execute(query)
    tariff = result.scalars().first()

    if tariff:
        return

    initial_tariff = TariffModel(
        title="Старт",
        description="Базовый тариф, в котором есть всё для комфортного старта",
        price=Decimal("0.00"),
        old_price=Decimal("0.00"),
        link_limit=5,
        project_limit=1,
        is_initial=True,
    )

    session.add(initial_tariff)
    await session.commit()


async def run_seeders() -> None:
    async with session_factory() as session:
        await seed_initial_tariff(session)

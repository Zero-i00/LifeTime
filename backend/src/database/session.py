from fastapi import Depends
from typing import Annotated
from config import settings, IS_DEBUG
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

engine = create_async_engine(
    url=settings.db.dsn.encoded_string(),
    echo=IS_DEBUG
)

session_factory = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with session_factory() as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_session)]

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import SocialMediaModal


class SocialMediaService:
    
    async def list(self, session: AsyncSession) -> list[SocialMediaModal]:
        query = select(SocialMediaModal)
        result = await session.execute(query)

        return result.scalars().all()


social_media_service = SocialMediaService()

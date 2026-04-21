from typing import List

from fastapi import APIRouter, status

from database.session import AsyncSessionDep
from modules.contact.schema import SocialMediaSchemaOut
from modules.contact.service import social_media_service



class SocialMediaResolver:
    router = APIRouter(
        prefix='/contact',
        tags=['Contact']
    )

    @staticmethod
    @router.get('/', status_code=status.HTTP_200_OK)
    async def list(
        session: AsyncSessionDep
    ) -> List[SocialMediaSchemaOut]:
        contacts = await social_media_service.list(session)
        return contacts
    

contact_resolver = SocialMediaResolver()

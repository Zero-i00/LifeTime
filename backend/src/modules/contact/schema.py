from pydantic import BaseModel
from database.models.contact import SocialMedia


class SocialMediaSchemaOut(BaseModel):
    id: int
    type: SocialMedia
    title: str
    url: str
    is_active: bool


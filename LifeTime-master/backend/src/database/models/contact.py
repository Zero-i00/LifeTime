import enum
from sqlalchemy import Enum
from database.orm import Base, max_char_field
from sqlalchemy.orm import Mapped, mapped_column, relationship



class SocialMedia(enum.Enum):
    OK = 'OK'
    MAX = ' MAX'
    EMAIL = 'EMAIL'
    TELEGRAM = 'TELEGRAM'


class SocialMediaModal(Base):
    __tablename__ = 'social_media'

    media_type: Mapped[SocialMedia] = mapped_column(Enum(SocialMedia))
    
    title: Mapped[max_char_field]
    url: Mapped[str]

    is_active: Mapped[bool] = mapped_column(default=True)
    


import datetime
from typing import Annotated
from config import constants
from sqlalchemy import String, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


max_char_field = Annotated[str, constants.model.max_char_field]
max_text_field = Annotated[str, constants.model.max_text_field]

class Base(DeclarativeBase):

    type_annotation_map = {
        max_char_field: String(constants.model.max_char_field),
        max_text_field: String(constants.model.max_text_field),
    }

    id: Mapped[int] = mapped_column(primary_key=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )

    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow,
    )
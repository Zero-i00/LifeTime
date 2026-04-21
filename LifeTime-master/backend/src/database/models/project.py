from typing import TYPE_CHECKING, List

from database.orm import Base, max_char_field
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from database.models.user import UserModel
    from database.models.link import LinkModel

class ProjectModel(Base):
    __tablename__ = "projects"

    name: Mapped[max_char_field]

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    user: Mapped["UserModel"] = relationship(back_populates="projects")

    links: Mapped[List["LinkModel"]] = relationship(back_populates="project", lazy='selectin')

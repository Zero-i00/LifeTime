from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey

from database.orm import Base, max_text_field
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from database.models.project import ProjectModel

class LinkModel(Base):
    __tablename__ = "links"

    url: Mapped[max_text_field] = mapped_column(unique=True)

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    project: Mapped["ProjectModel"] = relationship(back_populates='links')


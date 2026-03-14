import datetime
import enum
from typing import Optional, TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Enum
from database.orm import Base, max_char_field
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    from database.models.tariff import TariffModel
    from database.models.project import ProjectModel

class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class UserModel(Base):

    __tablename__ = "users"
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[bytes]

    full_name: Mapped[max_char_field]

    last_login_at: Mapped[Optional[datetime.datetime]]

    tariff_id: Mapped[int] = mapped_column(ForeignKey("tariffs.id"))
    tariff: Mapped["TariffModel"] = relationship(back_populates="users", lazy='selectin')

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)

    projects: Mapped[List["ProjectModel"]] = relationship(back_populates="user", lazy='selectin')
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

from database.orm import Base, max_char_field
from sqlalchemy import CheckConstraint, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from database.models.user import UserModel


class TariffModel(Base):
    __tablename__ = "tariffs"
    __table_args__ = (
        CheckConstraint('link_limit >= 0', name='ck_link_limit_positive'),
        CheckConstraint('project_limit >= 0', name='ck_project_limit_positive'),
    )

    title: Mapped[max_char_field]
    description: Mapped[Optional[max_char_field]]

    link_limit: Mapped[int] = mapped_column(default=0)
    project_limit: Mapped[int] = mapped_column(default=0)

    is_initial: Mapped[bool] = mapped_column(default=False)

    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    old_price: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))

    users: Mapped[List["UserModel"]] = relationship(back_populates='tariff')

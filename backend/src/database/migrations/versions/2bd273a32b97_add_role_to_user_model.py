"""add role to user model

Revision ID: 2bd273a32b97
Revises: 9306b3f88e7b
Create Date: 2026-03-14 04:19:38.438072

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2bd273a32b97'
down_revision: Union[str, Sequence[str], None] = '9306b3f88e7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    userrole = sa.Enum('ADMIN', 'USER', name='userrole')
    userrole.create(op.get_bind())
    op.add_column('users', sa.Column('role', userrole, nullable=False, server_default='USER'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')
    sa.Enum(name='userrole').drop(op.get_bind())

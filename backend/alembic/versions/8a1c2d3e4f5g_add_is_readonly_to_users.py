"""add_is_readonly_to_users

Revision ID: 8a1c2d3e4f5g
Revises: 3b1850a696a3
Create Date: 2025-12-13 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a1c2d3e4f5g'
down_revision: Union[str, None] = '3b1850a696a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_readonly', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('users', 'is_readonly')

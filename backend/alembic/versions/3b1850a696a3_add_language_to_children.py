"""add_language_to_children

Revision ID: 3b1850a696a3
Revises: 36bec497c5b4
Create Date: 2025-12-13 13:50:35.306538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b1850a696a3'
down_revision: Union[str, None] = '36bec497c5b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('children', sa.Column('language', sa.String(10), nullable=True))


def downgrade() -> None:
    op.drop_column('children', 'language')

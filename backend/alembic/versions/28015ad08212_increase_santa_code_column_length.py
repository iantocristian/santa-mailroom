"""increase santa_code column length

Revision ID: 28015ad08212
Revises: d019a8ee92a7
Create Date: 2025-12-09 19:26:42.725274

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28015ad08212'
down_revision: Union[str, None] = 'd019a8ee92a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Increase column length to support word-based codes like "MistletoePenguin"
    op.alter_column('families', 'santa_code',
               existing_type=sa.VARCHAR(length=8),
               type_=sa.String(length=30),
               existing_nullable=False)


def downgrade() -> None:
    op.alter_column('families', 'santa_code',
               existing_type=sa.String(length=30),
               type_=sa.VARCHAR(length=8),
               existing_nullable=False)


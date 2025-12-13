"""Add i18n fields to notifications

Revision ID: 17163de390f8
Revises: 8a1c2d3e4f5g
Create Date: 2025-12-13 22:08:07.377435

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17163de390f8'
down_revision: Union[str, None] = '8a1c2d3e4f5g'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add i18n columns to notifications table
    op.add_column('notifications', sa.Column('title_key', sa.String(length=100), nullable=True))
    op.add_column('notifications', sa.Column('title_params', sa.Text(), nullable=True))
    op.add_column('notifications', sa.Column('message_key', sa.String(length=100), nullable=True))
    op.add_column('notifications', sa.Column('message_params', sa.Text(), nullable=True))
    op.alter_column('notifications', 'title',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)


def downgrade() -> None:
    op.alter_column('notifications', 'title',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)
    op.drop_column('notifications', 'message_params')
    op.drop_column('notifications', 'message_key')
    op.drop_column('notifications', 'title_params')
    op.drop_column('notifications', 'title_key')

"""add santa_code to families

Revision ID: d019a8ee92a7
Revises: 46688856f616
Create Date: 2025-12-09 19:10:33.652852

"""
from typing import Sequence, Union
import secrets
import string

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision: str = 'd019a8ee92a7'
down_revision: Union[str, None] = '46688856f616'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def generate_code() -> str:
    """Generate a unique 8-character alphanumeric code."""
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '').replace('L', '')
    return ''.join(secrets.choice(chars) for _ in range(8))


def upgrade() -> None:
    # Add column as nullable first
    op.add_column('families', sa.Column('santa_code', sa.String(length=8), nullable=True))
    
    # Generate codes for existing families
    bind = op.get_bind()
    session = Session(bind=bind)
    
    # Get all families without codes
    result = session.execute(sa.text("SELECT id FROM families WHERE santa_code IS NULL"))
    family_ids = [row[0] for row in result]
    
    # Generate unique codes
    used_codes = set()
    for family_id in family_ids:
        code = generate_code()
        while code in used_codes:
            code = generate_code()
        used_codes.add(code)
        session.execute(
            sa.text("UPDATE families SET santa_code = :code WHERE id = :id"),
            {"code": code, "id": family_id}
        )
    session.commit()
    
    # Now make column non-nullable and add unique index
    op.alter_column('families', 'santa_code', nullable=False)
    op.create_index(op.f('ix_families_santa_code'), 'families', ['santa_code'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_families_santa_code'), table_name='families')
    op.drop_column('families', 'santa_code')


"""add invite_codes table

Revision ID: 36bec497c5b4
Revises: 28015ad08212
Create Date: 2025-12-09 19:34:47.213057

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '36bec497c5b4'
down_revision: Union[str, None] = '28015ad08212'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if invite_codes table already exists
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()
    
    if 'invite_codes' not in existing_tables:
        # Create invite_codes table first (referenced by users)
        op.create_table('invite_codes',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('code', sa.String(length=20), nullable=False),
            sa.Column('note', sa.String(length=200), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('used_by_id', sa.Integer(), nullable=True),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.ForeignKeyConstraint(['used_by_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_invite_codes_code'), 'invite_codes', ['code'], unique=True)
        op.create_index(op.f('ix_invite_codes_id'), 'invite_codes', ['id'], unique=False)
    
    # Check if users.invite_code_id column exists
    columns = [c['name'] for c in inspector.get_columns('users')]
    
    if 'invite_code_id' not in columns:
        op.add_column('users', sa.Column('invite_code_id', sa.Integer(), nullable=True))
        op.create_foreign_key('fk_users_invite_code', 'users', 'invite_codes', ['invite_code_id'], ['id'])
    
    # Drop old invite_token column if exists
    if 'invite_token' in columns:
        # Check for index first
        indexes = [i['name'] for i in inspector.get_indexes('users')]
        if 'ix_users_invite_token' in indexes:
            op.drop_index(op.f('ix_users_invite_token'), table_name='users')
        op.drop_column('users', 'invite_token')


def downgrade() -> None:
    # Restore invite_token column
    op.add_column('users', sa.Column('invite_token', sa.VARCHAR(length=512), nullable=True))
    op.create_index(op.f('ix_users_invite_token'), 'users', ['invite_token'], unique=True)
    
    # Remove invite_code_id
    op.drop_constraint('fk_users_invite_code', 'users', type_='foreignkey')
    op.drop_column('users', 'invite_code_id')
    
    # Drop invite_codes table
    op.drop_index(op.f('ix_invite_codes_id'), table_name='invite_codes')
    op.drop_index(op.f('ix_invite_codes_code'), table_name='invite_codes')
    op.drop_table('invite_codes')

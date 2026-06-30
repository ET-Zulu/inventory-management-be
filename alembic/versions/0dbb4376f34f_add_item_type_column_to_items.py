"""add item_type column to items

Revision ID: 0dbb4376f34f
Revises: a49e366cd8c4
Create Date: 2026-06-30 13:26:50.236986

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0dbb4376f34f'
down_revision: Union[str, Sequence[str], None] = 'a49e366cd8c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        'warehouses',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    op.create_table(
        'notifications',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('message', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('item_id', sa.Uuid(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['items.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_notifications_item_id'),
        'notifications',
        ['item_id'],
        unique=False
    )

    op.drop_column('bulk_imports', 'file_link')

    op.drop_constraint(
        op.f('invite_tokens_token_hash_key'),
        'invite_tokens',
        type_='unique'
    )

    # ✅ FIXED COLUMN NAME + SQLALCHEMY ONLY
    op.add_column(
        'items',
        sa.Column(
            'item_type',
            sa.Enum('SALLABLE', 'NON_SALLABLE', name='itemtype'),
            nullable=False
        )
    )

    op.add_column(
        'items',
        sa.Column('warehouse_id', sa.Uuid(), nullable=False)
    )

    op.create_foreign_key(
        None,
        'items',
        'warehouses',
        ['warehouse_id'],
        ['id']
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(None, 'items', type_='foreignkey')
    op.drop_column('items', 'warehouse_id')
    op.drop_column('items', 'item_type')

    op.create_unique_constraint(
        op.f('invite_tokens_token_hash_key'),
        'invite_tokens',
        ['token_hash'],
        postgresql_nulls_not_distinct=False
    )

    op.add_column(
        'bulk_imports',
        sa.Column('file_link', sa.VARCHAR(), autoincrement=False, nullable=True)
    )

    op.drop_index(
        op.f('ix_notifications_item_id'),
        table_name='notifications'
    )
    op.drop_table('notifications')
    op.drop_table('warehouses')
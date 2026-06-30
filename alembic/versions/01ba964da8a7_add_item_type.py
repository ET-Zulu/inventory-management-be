"""add item_type

Revision ID: 01ba964da8a7
Revises: a49e366cd8c4
Create Date: 2026-06-30 11:51:05.055441
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel  # IMPORTANT: required for AutoString


# revision identifiers, used by Alembic.
revision: str = '01ba964da8a7'
down_revision: Union[str, Sequence[str], None] = 'a49e366cd8c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Define enum explicitly (important for Postgres)
itemtype_enum = sa.Enum(
    'SALLABLE',
    'NON_SALLABLE',
    name='itemtype'
)


def upgrade() -> None:
    """Upgrade schema."""

    # Create enum type first (Postgres requirement)
    itemtype_enum.create(op.get_bind(), checkfirst=True)

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('message', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('severity', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
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

    op.drop_constraint(
        op.f('invite_tokens_token_hash_key'),
        'invite_tokens',
        type_='unique'
    )

    # Add new column safely (IMPORTANT: server_default avoids crash on existing rows)
    op.add_column(
        'items',
        sa.Column(
            'item_type',
            itemtype_enum,
            nullable=False,
            server_default='SALLABLE'
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column('items', 'item_type')

    op.create_unique_constraint(
        op.f('invite_tokens_token_hash_key'),
        'invite_tokens',
        ['token_hash'],
        postgresql_nulls_not_distinct=False
    )

    op.drop_index(
        op.f('ix_notifications_item_id'),
        table_name='notifications'
    )

    op.drop_table('notifications')

    # Drop enum type (important cleanup)
    itemtype_enum.drop(op.get_bind(), checkfirst=True)

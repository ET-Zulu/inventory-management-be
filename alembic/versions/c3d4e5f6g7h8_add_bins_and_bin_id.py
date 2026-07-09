"""add bins table and bin_id to items

Revision ID: c3d4e5f6g7h8
Revises: a49323ca03eb_merge_refreshtoken_and_warehouses
Create Date: 2026-07-09

Strategy for existing data:
  1. Create bins table.
  2. For every existing warehouse create a system bin "General Storage".
  3. Add bins_id to items (nullable first), then populate using the warehouse's system bin.
  4. Enforce NOT NULL + FK on items.bin_id.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c3d4e5f6g7h8"
down_revision: Union[str, Sequence[str], None] = "270c17509549"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bins",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("warehouse_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
    )

    # Create a system "General Storage" bin for each existing warehouse.
    op.execute(
        sa.text(
            """
            INSERT INTO bins (id, warehouse_id, name, is_system, created_at)
            SELECT gen_random_uuid(), id, 'General Storage', true, NOW()
            FROM warehouses
            WHERE is_active = true
            """
        )
    )

    # Add bin_id to items.
    op.add_column(
        "items",
        sa.Column("bin_id", sa.Uuid(), nullable=True),
    )

    # Populate items.bin_id by joining to the warehouse's system bin.
    op.execute(
        sa.text(
            """
            UPDATE items
            SET bin_id = (
                SELECT b.id
                FROM bins b
                WHERE b.warehouse_id = items.warehouse_id
                  AND b.name = 'General Storage'
                  AND b.is_system = true
                LIMIT 1
            )
            WHERE items.bin_id IS NULL
            """
        )
    )

    op.alter_column("items", "bin_id", nullable=False)

    op.create_foreign_key(
        "fk_items_bin_id",
        "items",
        "bins",
        ["bin_id"],
        ["id"],
    )

    # Keep legacy location column until full code refactor removes it.


def downgrade() -> None:
    op.drop_constraint("fk_items_bin_id", "items", type_="foreignkey")
    op.drop_column("items", "bin_id")
    op.drop_table("bins")


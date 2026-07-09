"""drop item warehouse_id after bin normalization

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-07-09

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6g7h8i9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6g7h8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    missing_bins = bind.execute(
        sa.text("SELECT COUNT(*) FROM items WHERE bin_id IS NULL")
    ).scalar_one()
    if missing_bins:
        raise RuntimeError("Cannot drop items.warehouse_id until every item has a bin_id.")

    mismatched_bins = bind.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM items i
            JOIN bins b ON b.id = i.bin_id
            WHERE i.warehouse_id IS NOT NULL
              AND b.warehouse_id <> i.warehouse_id
            """
        )
    ).scalar_one()
    if mismatched_bins:
        raise RuntimeError(
            "Cannot drop items.warehouse_id while item bins point to different warehouses."
        )

    op.drop_constraint("fk_items_warehouse_id", "items", type_="foreignkey")
    op.drop_column("items", "warehouse_id")


def downgrade() -> None:
    op.add_column("items", sa.Column("warehouse_id", sa.Uuid(), nullable=True))
    op.execute(
        sa.text(
            """
            UPDATE items
            SET warehouse_id = bins.warehouse_id
            FROM bins
            WHERE items.bin_id = bins.id
            """
        )
    )
    op.alter_column("items", "warehouse_id", nullable=False)
    op.create_foreign_key(
        "fk_items_warehouse_id",
        "items",
        "warehouses",
        ["warehouse_id"],
        ["id"],
    )

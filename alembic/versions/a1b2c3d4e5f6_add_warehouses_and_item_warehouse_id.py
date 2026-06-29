"""add warehouses table and item warehouse_id

Revision ID: a1b2c3d4e5f6
Revises: 670dc68645d6
Create Date: 2026-06-29 00:00:00.000000

Strategy for existing data:
  1. Create the warehouses table.
  2. Insert a seed "Main Warehouse" record.
  3. Add warehouse_id to items as nullable.
  4. Assign all existing items to "Main Warehouse".
  5. Enforce NOT NULL + FK constraint on warehouse_id.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "670dc68645d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Fixed UUID for the seed warehouse so it is stable across environments.
MAIN_WAREHOUSE_ID = "00000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # 1. Create warehouses table                                           #
    # ------------------------------------------------------------------ #
    op.create_table(
        "warehouses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # ------------------------------------------------------------------ #
    # 2. Seed "Main Warehouse"                                             #
    # ------------------------------------------------------------------ #
    op.execute(
        sa.text(
            """
            INSERT INTO warehouses (id, name, location, capacity, description, is_active, created_at)
            VALUES (:id, :name, :location, :capacity, :description, :is_active, NOW())
            """
        ).bindparams(
            id=MAIN_WAREHOUSE_ID,
            name="Main Warehouse",
            location=None,
            capacity=0,
            description="Default warehouse – auto-created during migration",
            is_active=True,
        )
    )

    # ------------------------------------------------------------------ #
    # 3. Add warehouse_id to items as nullable (no FK yet)                 #
    # ------------------------------------------------------------------ #
    op.add_column(
        "items",
        sa.Column("warehouse_id", sa.Uuid(), nullable=True),
    )

    # ------------------------------------------------------------------ #
    # 4. Assign all existing items to Main Warehouse                       #
    # ------------------------------------------------------------------ #
    op.execute(
        sa.text(
            "UPDATE items SET warehouse_id = :wid WHERE warehouse_id IS NULL"
        ).bindparams(wid=MAIN_WAREHOUSE_ID)
    )

    # ------------------------------------------------------------------ #
    # 5. Enforce NOT NULL + FK on warehouse_id                             #
    # ------------------------------------------------------------------ #
    op.alter_column("items", "warehouse_id", nullable=False)
    op.create_foreign_key(
        "fk_items_warehouse_id",
        "items",
        "warehouses",
        ["warehouse_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_items_warehouse_id", "items", type_="foreignkey")
    op.drop_column("items", "warehouse_id")
    op.drop_table("warehouses")

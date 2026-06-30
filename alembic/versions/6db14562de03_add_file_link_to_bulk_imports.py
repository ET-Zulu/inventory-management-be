"""add file link to bulk imports

Revision ID: 6db14562de03
Revises: 36ef52126684
Create Date: 2026-06-26 20:37:26.561721

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6db14562de03'
down_revision: Union[str, Sequence[str], None] = '36ef52126684'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "bulk_imports",
        sa.Column("file_link", sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("bulk_imports", "file_link")

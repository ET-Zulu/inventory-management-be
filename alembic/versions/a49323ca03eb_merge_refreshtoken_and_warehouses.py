"""Merge RefreshToken and Warehouses

Revision ID: a49323ca03eb
Revises: 429b74f7f6f2, a1b2c3d4e5f6
Create Date: 2026-06-30 10:21:14.034202

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a49323ca03eb'
down_revision: Union[str, Sequence[str], None] = ('429b74f7f6f2', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

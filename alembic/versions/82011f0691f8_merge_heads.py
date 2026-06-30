"""merge heads

Revision ID: 82011f0691f8
Revises: 01ba964da8a7, 36ef52126684
Create Date: 2026-06-30 16:36:24.304832

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82011f0691f8'
down_revision: Union[str, Sequence[str], None] = ('01ba964da8a7', '36ef52126684')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

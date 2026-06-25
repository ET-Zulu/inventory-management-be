"""merge auth + alerts heads

Revision ID: 36ef52126684
Revises: 429b74f7f6f2, 59eb99cc2cd8
Create Date: 2026-06-25 14:37:41.193432

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36ef52126684'
down_revision: Union[str, Sequence[str], None] = ('429b74f7f6f2', '59eb99cc2cd8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

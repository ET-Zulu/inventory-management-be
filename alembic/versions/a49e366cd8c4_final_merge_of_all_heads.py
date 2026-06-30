"""Final merge of all heads

Revision ID: a49e366cd8c4
Revises: 59eb99cc2cd8, a49323ca03eb
Create Date: 2026-06-30 10:23:47.863193

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a49e366cd8c4'
down_revision: Union[str, Sequence[str], None] = ('59eb99cc2cd8', 'a49323ca03eb')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

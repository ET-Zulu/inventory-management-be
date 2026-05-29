"""merge branched heads

Revision ID: 670dc68645d6
Revises: 3ae30b8c0b7b, 4f52309c8aef, 9c3b2d4e1f8a
Create Date: 2026-05-29 19:01:07.592490

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '670dc68645d6'
down_revision: Union[str, Sequence[str], None] = ('3ae30b8c0b7b', '4f52309c8aef', '9c3b2d4e1f8a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

"""invite token lookup indexes

Revision ID: 9c3b2d4e1f8a
Revises: fe4afd6b286c
Create Date: 2026-05-26 00:00:00.000000

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "9c3b2d4e1f8a"
down_revision = "fe4afd6b286c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_invite_tokens_email",
        "invite_tokens",
        ["email"],
        unique=False,
    )
    op.create_index(
        "ix_invite_tokens_role",
        "invite_tokens",
        ["role"],
        unique=False,
    )
    op.create_index(
        "ix_invite_tokens_invited_by",
        "invite_tokens",
        ["invited_by"],
        unique=False,
    )
    op.create_index(
        "ix_invite_tokens_expires_at",
        "invite_tokens",
        ["expires_at"],
        unique=False,
    )
    op.create_index(
        "ix_invite_tokens_used_at",
        "invite_tokens",
        ["used_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_invite_tokens_used_at", table_name="invite_tokens")
    op.drop_index("ix_invite_tokens_expires_at", table_name="invite_tokens")
    op.drop_index("ix_invite_tokens_invited_by", table_name="invite_tokens")
    op.drop_index("ix_invite_tokens_role", table_name="invite_tokens")
    op.drop_index("ix_invite_tokens_email", table_name="invite_tokens")

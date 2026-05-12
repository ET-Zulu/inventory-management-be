from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship

from app.model.enums import UserRole


class InviteToken(SQLModel, table=True):
    __tablename__ = "invite_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    email: str
    role: UserRole

    token_hash: str = Field(unique=True)

    invited_by: Optional[UUID] = Field(
        default=None,
        foreign_key="users.id"
    )

    expires_at: datetime
    used_at: Optional[datetime] = None

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    inviter: Optional["User"] = Relationship(
        back_populates="invites_sent"
    )

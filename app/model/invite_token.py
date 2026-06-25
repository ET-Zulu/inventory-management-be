from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship

from app.model.enums import UserRole

if TYPE_CHECKING:
    from app.model.user import User


class InviteToken(SQLModel, table=True):
    __tablename__ = "invite_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    email: str = Field(index=True)
    role: UserRole = Field(index=True)

    token_hash: str = Field(unique=True, index=True)

    invited_by: Optional[UUID] = Field(default=None, foreign_key="users.id", index=True)

    expires_at: datetime = Field(index=True)
    used_at: Optional[datetime] = Field(default=None, index=True)

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    inviter: Optional["User"] = Relationship(
        back_populates="invites_sent"
    )

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.model.user import User


class PasswordResetToken(SQLModel, table=True):
    __tablename__ = "password_reset_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # SHA-256 hash of the raw token sent to the user
    token_hash: str = Field(unique=True, index=True)

    user_id: UUID = Field(foreign_key="users.id", index=True)

    expires_at: datetime
    used_at: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="password_reset_tokens")

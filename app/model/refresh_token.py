from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.model.user import User


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    token: str = Field(unique=True, index=True)
    user_id: UUID = Field(foreign_key="users.id")
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="refresh_tokens")

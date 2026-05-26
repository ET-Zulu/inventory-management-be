from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship

from app.model.enums import UserRole


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    name: str
    email: str = Field(unique=True, index=True)

    password_hash: str
    role: UserRole = Field(index=True)

    is_active: bool = True

    created_at: datetime = Field(default_factory=datetime.utcnow)
    transactions: List["Transaction"] = Relationship(
        back_populates="user"
    )

    invites_sent: List["InviteToken"] = Relationship(
        back_populates="inviter"
    )

    bulk_imports: List["BulkImport"] = Relationship(
        back_populates="uploader"
    )

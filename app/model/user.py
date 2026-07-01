from datetime import datetime
from typing import List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship

from app.model.enums import UserRole

if TYPE_CHECKING:
    from app.model.bulk_import import BulkImport
    from app.model.invite_token import InviteToken
    from app.model.transaction import Transaction
    from app.model.refresh_token import RefreshToken
    from app.model.password_reset_token import PasswordResetToken


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    name: str
    email: str = Field(unique=True, index=True)

    password_hash: str
    role: UserRole = Field(index=True)

    is_active: bool = True

    profile_picture: str | None = Field(default=None)
    last_login: datetime | None = Field(default=None)

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

    refresh_tokens: List["RefreshToken"] = Relationship(
        back_populates="user"
    )

    password_reset_tokens: List["PasswordResetToken"] = Relationship(
        back_populates="user"
    )

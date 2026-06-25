from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship

from app.model.item import Item


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True
    )

    title: str
    message: str

    type: str
    severity: str

    item_id: UUID | None = Field(
        default=None,
        foreign_key="items.id",
        index=True
    )

    is_read: bool = Field(default=False)

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    item: "Item" = Relationship(
        back_populates="notifications"
    )
from datetime import datetime
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.model.item import Item
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    name: str = Field(unique=True)

    is_active: bool = True

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )
    deleted_at: datetime | None = None
    
    items: List["Item"] = Relationship(
        back_populates="category"
    )

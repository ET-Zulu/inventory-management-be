from datetime import datetime
from typing import List, TYPE_CHECKING
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from app.model.item import Item

from sqlmodel import SQLModel, Field, Relationship


class Warehouse(SQLModel, table=True):
    __tablename__ = "warehouses"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    name: str = Field(unique=True)

    location: str | None = Field(default=None)

    capacity: int = Field(default=0, ge=0)

    description: str | None = Field(default=None)

    is_active: bool = True

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )
    deleted_at: datetime | None = None

    items: List["Item"] = Relationship(
        back_populates="warehouse"
    )

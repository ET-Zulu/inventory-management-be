from datetime import datetime
from typing import List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.model.item import Item
    from app.model.warehouse import Warehouse


class Bin(SQLModel, table=True):
    __tablename__ = "bins"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    warehouse_id: UUID = Field(foreign_key="warehouses.id")

    # If true, this bin is system-managed and cannot be deleted.


    name: str

    is_system: bool = Field(default=False)


    created_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    items: List["Item"] = Relationship(back_populates="bin")
    warehouse: "Warehouse" = Relationship(back_populates="bins")




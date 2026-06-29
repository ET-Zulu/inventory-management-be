from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from app.model.transaction import Transaction
    from app.model.vendor import Vendor
    from app.model.category import Category
    from app.model.warehouse import Warehouse
    from app.model.notification import Notification

from sqlmodel import SQLModel, Field, Relationship


class Item(SQLModel, table=True):
    __tablename__ = "items"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    sku: str = Field(unique=True, index=True)

    name: str
    description: Optional[str] = None

    quantity_on_hand: int = Field(default=0)
    minimum_stock_level: int = Field(default=0)

    cost_price: float
    selling_price: float

    location: str = Field(default="")

    category_id: Optional[UUID] = Field(
        default=None,
        foreign_key="categories.id"
    )

    vendor_id: UUID = Field(
        foreign_key="vendors.id"
    )

    warehouse_id: UUID = Field(
        foreign_key="warehouses.id"
    )

    is_active: bool = True

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    deleted_at: datetime | None = None

    category: Optional["Category"] = Relationship(
        back_populates="items"
    )

    vendor: "Vendor" = Relationship(
        back_populates="items"
    )

    warehouse: "Warehouse" = Relationship(
        back_populates="items"
    )

    transactions: List["Transaction"] = Relationship(
        back_populates="item"
    )

    notifications: List["Notification"] = Relationship(
        back_populates="item"
    )

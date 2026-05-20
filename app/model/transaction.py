from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship

from app.model.enums import TransactionType


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    item_id: UUID = Field(foreign_key="items.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)

    transaction_type: TransactionType
    quantity_change: int
    before_quantity: int
    after_quantity: int

    reference_number: str = Field(index=True, nullable=False)

    notes: Optional[str] = Field(default=None, nullable=True)

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True
    )

    item: "Item" = Relationship(
        back_populates="transactions"
    )

    user: "User" = Relationship(
        back_populates="transactions"
    )
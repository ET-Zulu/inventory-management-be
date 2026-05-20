from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from app.model.enums import TransactionType


class TransactionCreateRequest(BaseModel):
    
    item_id: UUID = Field(..., description="The UUID of the stock item")
    user_id: UUID = Field(..., description="The UUID of the operator performing this action")
    transaction_type: TransactionType = Field(..., description="Must be 'INBOUND' or 'OUTBOUND'")
    quantity_change: int = Field(..., description="Must be a positive integer greater than zero")
    reference_number: str = Field(..., description="Reference code, e.g., INV-1002")
    notes: Optional[str] = Field(default=None, description="Optional description of the transaction")

    @field_validator("quantity_change")
    @classmethod
    def validate_positive_quantity(cls, value: int) -> int:
        """Enforces that input quantities are always positive integers."""
        if value <= 0:
            raise ValueError("Quantity change must be greater than zero.")
        return value


class TransactionCreateDataResponse(BaseModel):
    
    id: UUID
    user_id: UUID
    item_id: UUID
    transaction_type: TransactionType
    quantity_change: int
    reference_number: str
    notes: Optional[str] = None
    before_quantity: int
    after_quantity: int
    created_at: datetime


class TransactionListItemResponse(BaseModel):
    
    id: UUID
    item: str = Field(..., description="Name of the item")
    sku: str = Field(..., description="Unique SKU code of the item")
    transaction_type: TransactionType
    quantity_change: int
    operator_name: str = Field(..., description="Name of the operator pulled from user record")
    reference_number: str
    notes: Optional[str] = None
    before_quantity: int
    after_quantity: int
    created_at: datetime


class TransactionListDashboardResponse(BaseModel):
    
    total_movement: int
    inbound_24h: int
    outbound_24h: int
    anomalies: int
    data: list[TransactionListItemResponse]
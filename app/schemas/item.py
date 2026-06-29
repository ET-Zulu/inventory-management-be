"""Item schemas."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    """Schema for creating an item."""
    sku: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    initial_stock: int = Field(default=0, ge=0)
    minimum_stock_level: int = Field(default=0, ge=0)
    cost_price: float = Field(..., ge=0)
    selling_price: float = Field(..., ge=0)
    category_id: Optional[UUID] = None
    vendor_id: UUID
    warehouse_id: UUID
    bin_location: Optional[str] = None


class ItemUpdate(BaseModel):
    """Schema for updating an item. SKU is immutable."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    minimum_stock_level: Optional[int] = Field(default=None, ge=0)
    cost_price: Optional[float] = Field(default=None, ge=0)
    selling_price: Optional[float] = Field(default=None, ge=0)
    category_id: Optional[UUID] = None
    vendor_id: Optional[UUID] = None
    warehouse_id: Optional[UUID] = None
    bin_location: Optional[str] = None


class ItemResponse(BaseModel):
    """Schema for item response with derived status."""
    id: UUID
    sku: str
    name: str
    description: Optional[str] = None
    quantity_on_hand: int
    minimum_stock_level: int
    cost_price: float
    selling_price: float
    category_id: Optional[UUID] = None
    vendor_id: UUID
    warehouse_id: UUID
    bin_location: Optional[str] = None
    is_active: bool
    created_at: datetime
    status: str

    class Config:
        from_attributes = True


class ItemSummary(BaseModel):
    """Summary stats for item list responses."""
    active_skus: int
    below_threshold: int


class ItemListResponse(BaseModel):
    """Schema for paginated item list with summary."""
    summary: ItemSummary
    data: List[ItemResponse]
    page: int
    limit: int
    total: int


class StorageCapacityResponse(BaseModel):
    """Schema for storage capacity info."""
    total_quantity: int
    total_capacity: int
    used_percent: float
    free_percent: float

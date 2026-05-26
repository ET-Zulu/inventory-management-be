"""Category schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    """Schema for creating a category."""
    name: str = Field(..., min_length=1, max_length=255)


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)


class CategoryResponse(BaseModel):
    """Schema for category response."""
    id: UUID
    name: str
    created_at: datetime
    vendor_total: int = 0

    class Config:
        from_attributes = True

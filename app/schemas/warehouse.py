"""Warehouse schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class WarehouseCreate(BaseModel):
    """Schema for creating a warehouse."""

    name: str = Field(..., min_length=1, max_length=255)
    location: Optional[str] = None
    capacity: int = Field(..., ge=0)
    description: Optional[str] = None


class WarehouseUpdate(BaseModel):
    """Schema for updating a warehouse. All fields are optional."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    location: Optional[str] = None
    capacity: Optional[int] = Field(default=None, ge=0)
    description: Optional[str] = None


class WarehouseResponse(BaseModel):
    """Schema for warehouse response."""

    id: UUID
    name: str
    location: Optional[str] = None
    capacity: int
    description: Optional[str] = None
    created_at: datetime
    used_capacity: int
    available_capacity: int

    class Config:
        from_attributes = True

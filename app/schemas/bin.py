"""Bin schemas."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BinCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class BinUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)


class BinResponse(BaseModel):
    id: UUID
    warehouse_id: UUID
    name: str
    is_system: bool
    created_at: datetime
    items_count: int = 0

    class Config:
        from_attributes = True


class BinListResponse(BaseModel):
    data: List[BinResponse]
    page: int
    limit: int
    total: int

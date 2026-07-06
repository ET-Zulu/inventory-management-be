"""Category totals schemas."""

from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


class CategoryItemsCount(BaseModel):
    category_id: UUID
    category_name: str
    total_items: int


class CategoryItemsCountListResponse(BaseModel):
    data: List[CategoryItemsCount]


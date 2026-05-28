from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ReplenishmentItem(BaseModel):
    item_name: str
    sku: str
    current_stock: int
    threshold: int
    qty_needed: int
    estimated_cost: float


class ReplenishmentResponse(BaseModel):
    total_reorder_value: float
    out_of_stock: int
    pending_order: int
    critical_low_stock: int
    items_grouped_by_vendor: Dict[str, List[ReplenishmentItem]]
from pydantic import BaseModel


class LowStockAlert(BaseModel):
    item_name: str
    stock: int
    threshold: int
    severity: str
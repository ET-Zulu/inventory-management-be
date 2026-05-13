from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class VendorCreate(BaseModel):
    name: str
    contact_person: Optional[str] = None
    contact_info: Optional[str] = None
    location: Optional[str] = None
    lead_time: Optional[int] = 0


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_info: Optional[str] = None
    location: Optional[str] = None
    lead_time: Optional[int] = None
    is_active: Optional[bool] = None


class VendorRead(BaseModel):
    id: UUID
    name: str
    contact_person: str
    contact_info: str
    location: str
    lead_time: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ContactPersonSchema(BaseModel):
    first_name: str
    last_name: Optional[str] = None


class ContactInfoSchema(BaseModel):
    primary_phone: str
    secondary_phone: Optional[str] = None
    email: Optional[str] = None


class LocationSchema(BaseModel):
    city: str
    country: str


class VendorCreate(BaseModel):
    name: str
    contact_person: ContactPersonSchema
    contact_info: ContactInfoSchema
    location: LocationSchema
    lead_time: int = 0


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[ContactPersonSchema] = None
    contact_info: Optional[ContactInfoSchema] = None
    location: Optional[LocationSchema] = None
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
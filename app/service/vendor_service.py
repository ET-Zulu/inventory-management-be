from typing import Optional
from sqlmodel import Session, select
from uuid import UUID

from app.model.vendor import Vendor
from app.model.item import Item

from app.repository.vendor_repository import (
    create_vendor,
    get_vendor_by_id,
    get_all_vendors,
    update_vendor,
    delete_vendor
)

from app.schemas.vendor import VendorCreate, VendorUpdate

def build_vendor_fields(data: VendorCreate):
    full_name = data.contact_person.first_name
    if data.contact_person.last_name:
        full_name += f" {data.contact_person.last_name}"

    contact_parts = [data.contact_info.primary_phone]

    if data.contact_info.secondary_phone:
        contact_parts.append(data.contact_info.secondary_phone)

    if data.contact_info.email:
        contact_parts.append(data.contact_info.email.strip().lower())

    contact = " | ".join(contact_parts)
    location = f"{data.location.city}, {data.location.country}"

    return full_name, contact, location

def create_vendor_service(session: Session, data: VendorCreate):

    full_name, contact, location = build_vendor_fields(data)

    vendor = Vendor(
        name=data.name,
        contact_person=full_name,
        contact_info=contact,
        location=location,
        lead_time=data.lead_time
    )

    return create_vendor(session, vendor)

def get_vendor_service(session: Session, vendor_id: UUID):

    vendor = get_vendor_by_id(session, vendor_id)

    if not vendor:
        raise ValueError("VENDOR_NOT_FOUND")

    return vendor

def list_vendors_service(
    session: Session,
    page: int,
    limit: int,
    search: str | None = None
):

    skip = (page - 1) * limit

    vendors, _total = get_all_vendors(
        session=session,
        skip=skip,
        limit=limit,
        search=search
    )

    return vendors, _total

def update_vendor_service(session: Session, vendor_id: UUID, data: VendorUpdate):

    vendor = get_vendor_by_id(session, vendor_id)

    if not vendor:
        raise ValueError("VENDOR_NOT_FOUND")

    if data.name is not None:
        vendor.name = data.name

    if data.contact_person is not None:
        full_name = data.contact_person.first_name
        if data.contact_person.last_name:
            full_name += f" {data.contact_person.last_name}"
        vendor.contact_person = full_name

    if data.contact_info is not None:
        contact_parts = [data.contact_info.primary_phone]

        if data.contact_info.secondary_phone:
            contact_parts.append(data.contact_info.secondary_phone)

        if data.contact_info.email:
            contact_parts.append(data.contact_info.email.strip().lower())

        vendor.contact_info = " | ".join(contact_parts)

    if data.location is not None:
        vendor.location = f"{data.location.city}, {data.location.country}"

    if data.lead_time is not None:
        vendor.lead_time = data.lead_time

    if data.is_active is not None:
        vendor.is_active = data.is_active

    return update_vendor(session, vendor)


def get_vendor_summary(session: Session, vendor_id: UUID) -> Optional[dict]:
    vendor = get_vendor_by_id(session, vendor_id)
    if not vendor:
        return None

    items = session.exec(
        select(Item).where(Item.vendor_id == vendor_id, Item.is_active == True)  # noqa: E712
    ).all()

    return {
        "vendor_id": str(vendor.id),
        "vendor_name": vendor.name,
        "total_items": len(items),
        "total_inventory_quantity": sum(item.quantity_on_hand for item in items),
        "low_stock_items": [item.id for item in items if item.quantity_on_hand <= item.minimum_stock_level],
        "items": [item.id for item in items],
    }


def delete_vendor_service(session: Session, vendor_id: UUID):

    vendor = get_vendor_by_id(session, vendor_id)

    if not vendor:
        raise ValueError("VENDOR_NOT_FOUND")

    item_exists = session.exec(
        select(Item.id).where(Item.vendor_id == vendor_id, Item.is_active == True)  # noqa: E712
    ).first()

    if item_exists:
        raise ValueError(
            "Cannot delete vendor because it is referenced by existing items."
        )

    return delete_vendor(session, vendor)
from sqlmodel import Session, select
from uuid import UUID

from app.repository.vendor_repository import (
    create_vendor,
    get_vendor_by_id,
    get_all_vendors,
    update_vendor,
    delete_vendor
)

from app.model.item import Item
from app.schemas.vendor import VendorCreate, VendorUpdate

 
def create_vendor_service(session: Session, data: VendorCreate):

 
    return create_vendor(session, data)
 
def get_vendor_service(session: Session, vendor_id: UUID):

    vendor = get_vendor_by_id(session, vendor_id)

    if not vendor:
        raise ValueError("VENDOR_NOT_FOUND")

    return vendor

 
def list_vendors_service(session: Session):

    return get_all_vendors(session)
 
def update_vendor_service(session: Session, vendor_id: UUID, data: VendorUpdate):

    vendor = get_vendor_by_id(session, vendor_id)

    if not vendor:
        raise ValueError("VENDOR_NOT_FOUND")

    return update_vendor(session, vendor, data)

 
def delete_vendor_service(session: Session, vendor_id: UUID):
    vendor = get_vendor_by_id(session, vendor_id)

    if not vendor:
        raise ValueError("VENDOR_NOT_FOUND")

    item_exists = session.exec(
        select(Item.id).where(Item.vendor_id == vendor_id)
    ).first()

    if item_exists:
        raise ValueError("VENDOR_HAS_ITEMS")

    return delete_vendor(session, vendor)
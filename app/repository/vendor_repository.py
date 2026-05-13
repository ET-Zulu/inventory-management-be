from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID

from app.model.vendor import Vendor
from app.schemas.vendor import VendorCreate, VendorUpdate

def create_vendor(session: Session, data: VendorCreate) -> Vendor:

    # normalize email/contact
    contact = (data.contact_info or "").strip().lower()

    # check ONLY active vendors
    existing = session.exec(
        select(Vendor).where(
            Vendor.contact_info == contact,
            Vendor.is_active == True
        )
    ).first()

    if existing:
        raise Exception("VENDOR_CONTACT_EXISTS")

    vendor = Vendor(
        name=data.name,
        contact_person=data.contact_person,
        contact_info=contact,
        location=data.location,
        lead_time=data.lead_time
    )

    session.add(vendor)
    session.commit()
    session.refresh(vendor)
    return vendor

def get_vendor_by_id(session: Session, vendor_id: UUID) -> Optional[Vendor]:
    return session.exec(
        select(Vendor).where(
            Vendor.id == vendor_id,
            Vendor.is_active == True
        )
    ).first()

def get_all_vendors(session: Session) -> List[Vendor]:
    return session.exec(select(Vendor)).all()

def update_vendor(
    session: Session,
    vendor: Vendor,
    data: VendorUpdate
) -> Vendor:

    if data.name is not None:
        vendor.name = data.name

    if data.contact_person is not None:
        vendor.contact_person = data.contact_person

    if data.contact_info is not None:
        vendor.contact_info = data.contact_info

    if data.location is not None:
        vendor.location = data.location

    if data.lead_time is not None:
        vendor.lead_time = data.lead_time

    if data.is_active is not None:
        vendor.is_active = data.is_active

    session.add(vendor)
    session.commit()
    session.refresh(vendor)
    return vendor

def delete_vendor(session: Session, vendor: Vendor) -> Vendor:
    vendor.is_active = False
    session.add(vendor)
    session.commit()
    session.refresh(vendor)
    return vendor
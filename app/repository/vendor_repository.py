from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID

from app.model.vendor import Vendor


def create_vendor(session: Session, vendor: Vendor) -> Vendor:
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
    return session.exec(
        select(Vendor).where(Vendor.is_active == True)
    ).all()


def update_vendor(session: Session, vendor: Vendor) -> Vendor:
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
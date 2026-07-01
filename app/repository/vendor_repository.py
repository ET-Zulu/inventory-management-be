from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from sqlalchemy import or_, func

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


def get_all_vendors(
    session: Session,
    skip: int = 0,
    limit: int = 20,
    search: str | None = None
):

    query = select(Vendor).where(
        Vendor.is_active == True
    )

    if search:
        search = f"%{search.lower()}%"

        query = query.where(
            or_(
                func.lower(Vendor.name).like(search),
                func.lower(Vendor.contact_person).like(search),
                func.lower(Vendor.location).like(search)
            )
        )

    query = query.offset(skip).limit(limit)

    total_query = select(func.count()).select_from(Vendor).where(
        Vendor.is_active == True
    )

    return session.exec(query).all(), session.exec(total_query).one()


def update_vendor(session: Session, vendor: Vendor) -> Vendor:
    session.add(vendor)
    session.commit()
    session.refresh(vendor)
    return vendor


def delete_vendor(session: Session, vendor: Vendor) -> Vendor:
    vendor.is_active = False
    vendor.deleted_at = func.now()
    session.add(vendor)
    session.commit()
    session.refresh(vendor)
    return vendor
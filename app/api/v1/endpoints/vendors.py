from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from uuid import UUID

from app.core.database import get_session
from app.dependencies.auth import get_admin, get_current_active_user

from app.schemas.vendor import VendorCreate, VendorUpdate, VendorRead
from app.schemas.common import success_response, error_response, ErrorCode

from app.service.vendor_service import (
    create_vendor_service,
    get_vendor_service,
    list_vendors_service,
    update_vendor_service,
    delete_vendor_service
)

from app.model.item import Item
from sqlmodel import select

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.post("/", dependencies=[Depends(get_admin)])
def create_vendor(
    data: VendorCreate,
    session: Session = Depends(get_session)
):
    try:
        vendor = create_vendor_service(session, data)

        return success_response(
            message="Vendor created successfully",
            data=vendor
        )

    except Exception as e:
        return error_response(ErrorCode.BAD_REQUEST, str(e))


@router.get("/", dependencies=[Depends(get_current_active_user)])
def get_vendors(
    page: int = 1,
    limit: int = 20,
    search: str | None = Query(default=None),
    session: Session = Depends(get_session)
):

    vendors = list_vendors_service(
        session=session,
        page=page,
        limit=limit,
        search=search
    )

    data = [
        VendorRead(
            id=v.id,
            name=v.name,
            contact_person=v.contact_person,
            contact_info=v.contact_info,
            location=v.location,
            lead_time=v.lead_time,
            is_active=v.is_active,
            created_at=v.created_at,
        ).model_dump() | {"items_count": len(v.items)}
        for v in vendors
    ]

    return success_response(
        message="Vendors fetched successfully",
        data=data
    )

@router.get("/{vendor_id}", dependencies=[Depends(get_current_active_user)])
def get_vendor(
    vendor_id: UUID,
    session: Session = Depends(get_session)
):

    try:
        vendor = get_vendor_service(session, vendor_id)

        if not vendor:
            return error_response(
                ErrorCode.NOT_FOUND,
                "Vendor not found"
            )

        items_count = session.exec(
            select(Item).where(Item.vendor_id == vendor_id)
        ).all()

        data = VendorRead.model_validate(vendor).model_dump()
        data["items_count"] = len(items_count)

        return success_response(
            message="Vendor fetched successfully",
            data=data
        )

    except Exception as e:
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))


@router.patch("/{vendor_id}", dependencies=[Depends(get_admin)])
def update_vendor(
    vendor_id: UUID,
    data: VendorUpdate,
    session: Session = Depends(get_session)
):
    try:
        vendor = update_vendor_service(session, vendor_id, data)

        return success_response(
            message="Vendor updated successfully",
            data=vendor
        )

    except Exception as e:
        return error_response(ErrorCode.BAD_REQUEST, str(e))


@router.delete("/{vendor_id}", dependencies=[Depends(get_admin)])
def delete_vendor(
    vendor_id: UUID,
    session: Session = Depends(get_session)
):
    try:
        vendor = delete_vendor_service(session, vendor_id)

        return success_response(
            message="Vendor deleted successfully",
            data=vendor
        )

    except Exception as e:
        return error_response(ErrorCode.BAD_REQUEST, str(e))
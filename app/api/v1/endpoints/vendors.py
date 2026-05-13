from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID

from app.core.database import get_session
from app.schemas.vendor import VendorCreate, VendorUpdate, VendorRead
from app.service.vendor_service import (
    create_vendor_service,
    get_vendor_service,
    list_vendors_service,
    update_vendor_service,
    delete_vendor_service
)

router = APIRouter(prefix="/vendors", tags=["Vendors"])

@router.post("/", response_model=VendorRead)
def create_vendor(
    data: VendorCreate,
    session: Session = Depends(get_session)
):
    try:
        return create_vendor_service(session, data)
    except Exception as e:
        raise handle_error(e)

@router.get("/", response_model=list[VendorRead])
def get_vendors(session: Session = Depends(get_session)):
    vendors = list_vendors_service(session)
    return [v for v in vendors if v.is_active]


@router.get("/{vendor_id}", response_model=VendorRead)
def get_vendor(
    vendor_id: UUID,
    session: Session = Depends(get_session)
):
    try:
        return get_vendor_service(session, vendor_id)
    except Exception as e:
        raise handle_error(e)

@router.patch("/{vendor_id}", response_model=VendorRead)
def update_vendor(
    vendor_id: UUID,
    data: VendorUpdate,
    session: Session = Depends(get_session)
):
    try:
        return update_vendor_service(session, vendor_id, data)
    except Exception as e:
        raise handle_error(e)

@router.delete("/{vendor_id}", response_model=VendorRead)
def delete_vendor(
    vendor_id: UUID,
    session: Session = Depends(get_session)
):
    try:
        return delete_vendor_service(session, vendor_id)
    except Exception as e:
        raise handle_error(e)

def handle_error(e: Exception):
    msg = str(e)

    if msg == "VENDOR_CONTACT_EXISTS":
        raise HTTPException(status_code=409, detail=msg)

    if msg == "VENDOR_HAS_ITEMS":
        raise HTTPException(status_code=409, detail=msg)

    if msg == "VENDOR_NOT_FOUND":
        raise HTTPException(status_code=404, detail=msg)

    raise HTTPException(status_code=400, detail=msg)
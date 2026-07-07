from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from uuid import UUID

from app.core.database import get_session
from app.dependencies.auth import get_admin, get_current_active_user

from app.schemas.item import ItemResponse
from app.schemas.vendor import VendorCreate, VendorUpdate, VendorRead
from app.schemas.common import success_response, error_response, resource_in_use_error_response, ErrorCode

from app.service import item_service
from app.service.vendor_service import (
    create_vendor_service,
    get_vendor_service,
    list_vendors_service,
    update_vendor_service,
    delete_vendor_service,
    get_vendor_summary,
)

from app.model.item import Item
from sqlmodel import select

router = APIRouter(prefix="/vendors", tags=["Vendors"])


def _item_to_response(item) -> dict:
    status = item_service.derive_status(item)
    return ItemResponse(
        id=item.id,
        sku=item.sku,
        name=item.name,
        description=item.description,
        quantity_on_hand=item.quantity_on_hand,
        minimum_stock_level=item.minimum_stock_level,
        cost_price=item.cost_price,
        selling_price=item.selling_price,
        category_id=item.category_id,
        vendor_id=item.vendor_id,
        warehouse_id=item.warehouse_id,
        bin_location=item.location or None,
        is_active=item.is_active,
        created_at=item.created_at,
        status=status,
    ).model_dump()


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

    vendors , _total = list_vendors_service(
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
        data=data,
        total=_total
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


@router.get("/{vendor_id}/summary", dependencies=[Depends(get_current_active_user)])
def vendor_summary(vendor_id: UUID, session: Session = Depends(get_session)):
    summary = get_vendor_summary(session, vendor_id)
    if not summary:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Vendor not found"),
        )
    return success_response(message="Vendor summary retrieved successfully", data=summary)


@router.get("/{vendor_id}/items", dependencies=[Depends(get_current_active_user)])
def vendor_items(
    vendor_id: UUID,
    session: Session = Depends(get_session),
    page: int = 1,
    limit: int = 20,
    search: str | None = Query(default=None),
    low_stock: bool = Query(default=False),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
):
    result = item_service.get_all_items(
        session,
        page=page,
        limit=limit,
        vendor_id=vendor_id,
        search=search,
        low_stock=low_stock,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    items = [item_service.derive_status(item) for item in result["data"]]
    return success_response(
        message="Vendor items retrieved successfully",
        data={
            "summary": result["summary"],
            "data": [_item_to_response(item) for item in result["data"]],
            "page": result["page"],
            "limit": result["limit"],
            "total": result["total"],
        },
    )


@router.get("/{vendor_id}/low-stock-items", dependencies=[Depends(get_current_active_user)])
def vendor_low_stock_items(
    vendor_id: UUID,
    session: Session = Depends(get_session),
    page: int = 1,
    limit: int = 20,
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
):
    result = item_service.get_all_items(
        session,
        page=page,
        limit=limit,
        vendor_id=vendor_id,
        low_stock=True,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return success_response(
        message="Vendor low-stock items retrieved successfully",
        data={
            "summary": result["summary"],
            "data": [_item_to_response(item) for item in result["data"]],
            "page": result["page"],
            "limit": result["limit"],
            "total": result["total"],
        },
    )


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

    except ValueError as e:
        if str(e) == "VENDOR_NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail=error_response(ErrorCode.NOT_FOUND, "Vendor not found"),
            ) from e

        raise HTTPException(
            status_code=409,
            detail=resource_in_use_error_response(str(e)),
        ) from e

    except Exception as e:
        return error_response(ErrorCode.BAD_REQUEST, str(e))
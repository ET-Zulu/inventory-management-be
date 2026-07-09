from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.core.database import get_session
from app.core.database import SessionType
from app.dependencies.auth import get_admin, get_current_active_user, get_operator
from app.schemas.common import success_response, error_response, ErrorCode
from app.schemas.item import (
    ItemCreate,
    ItemUpdate,
    ItemResponse,
    ItemListResponse,
    ItemSummary,
    StorageCapacityResponse,
)
from app.service import item_service

router = APIRouter(prefix="/items", tags=["Items"])


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


# /storage/capacity must be defined before /{item_id} so FastAPI
# doesn't try to parse "storage" as a UUID
@router.get("/storage/capacity", dependencies=[Depends(get_current_active_user)])
def get_storage_capacity(session: SessionType):
    capacity = item_service.get_storage_capacity(session)
    return success_response(
        message="Storage capacity retrieved successfully",
        data=StorageCapacityResponse(**capacity).model_dump(),
    )


@router.post("", status_code=201, dependencies=[Depends(get_operator)])
def create_item(payload: ItemCreate, session: SessionType):
    try:
        item = item_service.create_item(session, payload)
        return success_response(
            message="Item created successfully",
            data=_item_to_response(item),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=error_response(ErrorCode.CONFLICT, str(e)),
        )


@router.get("", dependencies=[Depends(get_current_active_user)])
def get_items(
    session: SessionType,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    category: Optional[UUID] = Query(default=None),
    vendor: Optional[UUID] = Query(default=None),
    warehouse: Optional[UUID] = Query(default=None),
    search: Optional[str] = Query(default=None),
    low_stock: bool = Query(default=False),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
):
    result = item_service.get_all_items(
        session,
        page=page,
        limit=limit,
        category_id=category,
        vendor_id=vendor,
        warehouse_id=warehouse,
        search=search,
        low_stock=low_stock,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    items_data = [_item_to_response(item) for item in result["data"]]

    response_data = ItemListResponse(
        summary=ItemSummary(**result["summary"]),
        data=[ItemResponse(**d) for d in items_data],
        page=result["page"],
        limit=result["limit"],
        total=result["total"],
    ).model_dump()

    return success_response(
        message="Items retrieved successfully",
        data=response_data,
    )


@router.get("/check-sku")
def check_sku(
    sku: str,
    session: Session = Depends(get_session),
):
    return item_service.check_sku_availability(session, sku)

@router.get("/{item_id}", dependencies=[Depends(get_current_active_user)])
def get_item(item_id: UUID, session: SessionType):
    item = item_service.get_item_by_id(session, item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Item not found"),
        )
    return success_response(
        message="Item retrieved successfully",
        data=_item_to_response(item),
    )


@router.patch("/{item_id}", dependencies=[Depends(get_operator)])
def update_item(item_id: UUID, payload: ItemUpdate, session: SessionType):
    item = item_service.update_item(session, item_id, payload)
    if not item:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Item not found"),
        )
    return success_response(
        message="Item updated successfully",
        data=_item_to_response(item),
    )


@router.delete("/{item_id}", dependencies=[Depends(get_admin)])
def delete_item(item_id: UUID, session: SessionType):
    item, action = item_service.delete_item(session, item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Item not found"),
        )

    if action == "soft_deleted":
        message = "Item deactivated (has transaction history)"
    else:
        message = "Item permanently deleted"

    return success_response(message=message)


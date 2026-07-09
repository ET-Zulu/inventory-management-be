from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.database import get_session
from app.core.database import SessionType
from app.dependencies.auth import get_admin, get_current_active_user
from app.schemas.common import success_response, error_response, resource_in_use_error_response, ErrorCode
from app.schemas.item import ItemResponse
from app.schemas.warehouse import (
    WarehouseCreate,
    WarehouseListResponse,
    WarehouseUpdate,
)


from app.service import item_service, warehouse_service

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


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


@router.post("", status_code=201, dependencies=[Depends(get_admin)])
def create_warehouse(payload: WarehouseCreate, session: SessionType):
    warehouse = warehouse_service.create_warehouse(session, payload)
    response = warehouse_service.get_warehouse_by_id(session, warehouse.id)
    if response is None:
        raise ValueError("Failed to retrieve the created warehouse")
    try:
       
        return success_response(
            message="Warehouse created successfully",
            data=response.model_dump(), #type ignore
        )
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=error_response(ErrorCode.CONFLICT, str(e)),
        )


@router.get("", dependencies=[Depends(get_current_active_user)])
def get_warehouses(
    session: SessionType,
    page: int = Query(default=1, ge=1),
    #limit: int = Query(default=20, ge=1, le=100),
    limit: int = Query(250, max_value=500)
):
    result = warehouse_service.get_all_warehouses(session, page=page, limit=limit)
    response_data = WarehouseListResponse(**result).model_dump()
    return success_response(
        message="Warehouses retrieved successfully",
        data=response_data,
    )


@router.get("/check-warehouse-name" , dependencies=[Depends(get_current_active_user)])
def check_warehouse_name(
    name: str,
    session: SessionType
):
    return warehouse_service.check_warehouse_name_availability(session, name)


@router.get("/{warehouse_id}", dependencies=[Depends(get_current_active_user)])
def get_warehouse(warehouse_id: UUID, session: SessionType):
    warehouse = warehouse_service.get_warehouse_by_id(session, warehouse_id)
    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Warehouse not found"),
        )
    return success_response(
        message="Warehouse retrieved successfully",
        data=warehouse.model_dump(),
    )


@router.get("/{warehouse_id}/summary", dependencies=[Depends(get_current_active_user)])
def warehouse_summary(warehouse_id: UUID, session: SessionType):
    summary = warehouse_service.get_warehouse_summary(session, warehouse_id)
    if not summary:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Warehouse not found"),
        )
    return success_response(message="Warehouse summary retrieved successfully", data=summary)


@router.get("/{warehouse_id}/items", dependencies=[Depends(get_current_active_user)])
def warehouse_items(
    warehouse_id: UUID,
    session: SessionType,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    low_stock: bool = Query(default=False),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
):
    result = item_service.get_all_items(
        session,
        page=page,
        limit=limit,
        warehouse_id=warehouse_id,
        search=search,
        low_stock=low_stock,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return success_response(
        message="Warehouse items retrieved successfully",
        data={
            "summary": result["summary"],
            "data": [_item_to_response(item) for item in result["data"]],
            "page": result["page"],
            "limit": result["limit"],
            "total": result["total"],
        },
    )


@router.get("/{warehouse_id}/low-stock-items", dependencies=[Depends(get_current_active_user)])
def warehouse_low_stock_items(
    warehouse_id: UUID,
    session: SessionType,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
):
    result = item_service.get_all_items(
        session,
        page=page,
        limit=limit,
        warehouse_id=warehouse_id,
        low_stock=True,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return success_response(
        message="Warehouse low-stock items retrieved successfully",
        data={
            "summary": result["summary"],
            "data": [_item_to_response(item) for item in result["data"]],
            "page": result["page"],
            "limit": result["limit"],
            "total": result["total"],
        },
    )


@router.patch("/{warehouse_id}", dependencies=[Depends(get_admin)])
def update_warehouse(warehouse_id: UUID, payload: WarehouseUpdate, session: SessionType):
    warehouse = warehouse_service.update_warehouse(session, warehouse_id, payload)
    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Warehouse not found"),
        )
    return success_response(
        message="Warehouse updated successfully",
        data=warehouse.model_dump(),
    )


@router.delete("/{warehouse_id}", dependencies=[Depends(get_admin)])
def delete_warehouse(warehouse_id: UUID, session: SessionType):
    try:
        warehouse = warehouse_service.delete_warehouse(session, warehouse_id)
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=resource_in_use_error_response(str(e)),
        ) from e

    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Warehouse not found"),
        )
    return success_response(message="Warehouse deleted successfully")







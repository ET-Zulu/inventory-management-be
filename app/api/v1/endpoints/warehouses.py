from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.database import get_session
from app.core.database import SessionType
from app.dependencies.auth import get_admin, get_current_active_user
from app.schemas.common import success_response, error_response, ErrorCode
from app.schemas.warehouse import WarehouseCreate, WarehouseListResponse, WarehouseUpdate
from app.service import warehouse_service

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.post("", status_code=201, dependencies=[Depends(get_admin)])
def create_warehouse(payload: WarehouseCreate, session: SessionType):
    try:
        warehouse = warehouse_service.create_warehouse(session, payload)
        response = warehouse_service.get_warehouse_by_id(session, warehouse.id)
        return success_response(
            message="Warehouse created successfully",
            data=response.model_dump(),
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
    limit: int = Query(default=20, ge=1, le=100),
):
    result = warehouse_service.get_all_warehouses(session, page=page, limit=limit)
    response_data = WarehouseListResponse(**result).model_dump()
    return success_response(
        message="Warehouses retrieved successfully",
        data=response_data,
    )


@router.get("/check-warehouse-name")
def check_warehouse_name(
    name: str,
    session: SessionType = Depends(get_session),
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
    warehouse = warehouse_service.delete_warehouse(session, warehouse_id)
    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Warehouse not found"),
        )
    return success_response(message="Warehouse deleted successfully")

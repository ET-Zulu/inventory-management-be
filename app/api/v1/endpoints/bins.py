from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.database import SessionType
from app.dependencies.auth import get_admin, get_current_active_user, get_operator
from app.schemas.bin import BinCreate, BinListResponse, BinUpdate
from app.schemas.common import ErrorCode, error_response, resource_in_use_error_response, success_response
from app.service import bin_service

router = APIRouter(prefix="/warehouses/{warehouse_id}/bins", tags=["Bins"])


@router.post("", status_code=201, dependencies=[Depends(get_operator)])
def create_bin(warehouse_id: UUID, payload: BinCreate, session: SessionType):
    try:
        bin_ = bin_service.create_bin(session, warehouse_id, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=error_response(ErrorCode.CONFLICT, str(e)),
        ) from e

    if not bin_:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Warehouse not found"),
        )
    return success_response(message="Bin created successfully", data=bin_.model_dump())


@router.get("", dependencies=[Depends(get_current_active_user)])
def get_bins(
    warehouse_id: UUID,
    session: SessionType,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    result = bin_service.get_bins(session, warehouse_id, page=page, limit=limit)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Warehouse not found"),
        )
    return success_response(
        message="Bins retrieved successfully",
        data=BinListResponse(**result).model_dump(),
    )


@router.get("/{bin_id}", dependencies=[Depends(get_current_active_user)])
def get_bin(warehouse_id: UUID, bin_id: UUID, session: SessionType):
    bin_ = bin_service.get_bin(session, warehouse_id, bin_id)
    if not bin_:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Bin not found"),
        )
    return success_response(message="Bin retrieved successfully", data=bin_.model_dump())


@router.patch("/{bin_id}", dependencies=[Depends(get_operator)])
def update_bin(warehouse_id: UUID, bin_id: UUID, payload: BinUpdate, session: SessionType):
    try:
        bin_ = bin_service.update_bin(session, warehouse_id, bin_id, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=error_response(ErrorCode.CONFLICT, str(e)),
        ) from e

    if not bin_:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Bin not found"),
        )
    return success_response(message="Bin updated successfully", data=bin_.model_dump())


@router.delete("/{bin_id}", dependencies=[Depends(get_admin)])
def delete_bin(warehouse_id: UUID, bin_id: UUID, session: SessionType):
    try:
        bin_ = bin_service.delete_bin(session, warehouse_id, bin_id)
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=resource_in_use_error_response(str(e)),
        ) from e

    if not bin_:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Bin not found"),
        )
    return success_response(message="Bin deleted successfully")

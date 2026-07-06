from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.database import SessionType
from app.dependencies.auth import get_current_active_user
from app.schemas.common import success_response, error_response, ErrorCode
from app.service import category_total_service

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/total-items", dependencies=[Depends(get_current_active_user)])
def total_items_across_categories(session: SessionType):
    try:
        data = category_total_service.get_total_items_across_categories(session)
        return success_response(
            message="Total items across all categories retrieved successfully",
            data=data,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=error_response(ErrorCode.CONFLICT, str(e)),
        )


@router.get("/{category_id}/total-items", dependencies=[Depends(get_current_active_user)])
def total_items_for_category(category_id: UUID, session: SessionType):
    try:
        data = category_total_service.get_total_items_for_category(session, category_id)
        return success_response(
            message="Total items for category retrieved successfully",
            data=data,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, str(e)),
        )


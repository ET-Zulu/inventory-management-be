from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.database import SessionType
from app.dependencies.auth import get_admin, get_current_active_user
from app.schemas.common import success_response, error_response, resource_in_use_error_response, ErrorCode
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.service import category_service

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("", status_code=201, dependencies=[Depends(get_admin)])
def create_category(payload: CategoryCreate, session: SessionType):
    try:
        category = category_service.create_category(session, payload)
        response = category_service.get_category_by_id(session, category.id)
        return success_response(
            message="Category created successfully",
            data=response.model_dump(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=error_response(ErrorCode.CONFLICT, str(e)),
        )


@router.get("", dependencies=[Depends(get_current_active_user)])
def get_categories(session: SessionType , page: int = 1, limit: int = 10):
    categories, _total = category_service.get_all_categories(session, page=page, limit=limit)
    return success_response(
        message="Categories retrieved successfully",
        data=[cat.model_dump() for cat in categories],
        total=_total
    ) 


@router.get("/{category_id}", dependencies=[Depends(get_current_active_user)])
def get_category(category_id: UUID, session: SessionType):
    category = category_service.get_category_by_id(session, category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Category not found"),
        )
    return success_response(
        message="Category retrieved successfully",
        data=category.model_dump(),
    )


@router.get("/{category_id}/summary", dependencies=[Depends(get_current_active_user)])
def category_summary(category_id: UUID, session: SessionType):
    summary = category_service.get_category_summary(session, category_id)
    if not summary:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Category not found"),
        )
    return success_response(message="Category summary retrieved successfully", data=summary)


@router.patch("/{category_id}", dependencies=[Depends(get_admin)])
def update_category(category_id: UUID, payload: CategoryUpdate, session: SessionType):
    category = category_service.update_category(session, category_id, payload)
    if not category:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Category not found"),
        )
    return success_response(
        message="Category updated successfully",
        data=category.model_dump(),
    )


@router.delete("/{category_id}", dependencies=[Depends(get_admin)])
def delete_category(category_id: UUID, session: SessionType):
    try:
        category = category_service.delete_category(session, category_id)
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=resource_in_use_error_response(str(e)),
        ) from e

    if not category:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Category not found"),
        )
    return success_response(message="Category deleted successfully")
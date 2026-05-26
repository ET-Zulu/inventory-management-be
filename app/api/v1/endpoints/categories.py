from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.core.database import SessionType
from app.schemas.common import success_response, error_response, ErrorCode
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.service import category_service

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("", status_code=201)
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


@router.get("")
def get_categories(session: SessionType):
    categories = category_service.get_all_categories(session)
    return success_response(
        message="Categories retrieved successfully",
        data=[cat.model_dump() for cat in categories],
    )


@router.get("/{category_id}")
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


@router.patch("/{category_id}")
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


@router.delete("/{category_id}")
def delete_category(category_id: UUID, session: SessionType):
    category = category_service.delete_category(session, category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail=error_response(ErrorCode.NOT_FOUND, "Category not found"),
        )
    return success_response(message="Category deleted successfully")
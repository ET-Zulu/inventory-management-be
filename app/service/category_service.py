from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session

from app.model.category import Category
from app.schemas.category import CategoryResponse
from app.repository import category_repository


def _to_response(session: Session, category: Category) -> CategoryResponse:
    vendor_total = category_repository.count_vendors_for_category(session, category.id)
    return CategoryResponse(
        id=category.id,
        name=category.name,
        created_at=category.created_at,
        vendor_total=vendor_total,
    )


def create_category(session: Session, payload) -> Category:
    existing = category_repository.get_category_by_name(session, payload.name)
    if existing:
        raise ValueError(f"Category '{payload.name}' already exists")

    category = Category(name=payload.name)
    return category_repository.save_category(session, category)


def get_all_categories(session: Session) -> List[CategoryResponse]:
    categories = category_repository.get_all_active_categories(session)
    return [_to_response(session, cat) for cat in categories]


def get_category_by_id(session: Session, category_id: UUID) -> Optional[CategoryResponse]:
    category = category_repository.get_category_by_id(session, category_id)
    if not category:
        return None
    return _to_response(session, category)


def update_category(session: Session, category_id: UUID, payload) -> Optional[CategoryResponse]:
    category = category_repository.get_category_by_id(session, category_id)
    if not category:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)

    saved = category_repository.save_category(session, category)
    return _to_response(session, saved)


def delete_category(session: Session, category_id: UUID) -> Optional[Category]:
    category = category_repository.get_category_by_id(session, category_id)
    if not category:
        return None

    category.is_active = False
    category.deleted_at = datetime.utcnow()
    return category_repository.save_category(session, category)
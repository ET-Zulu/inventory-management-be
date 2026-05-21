from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select, func

from app.model.category import Category
from app.model.item import Item
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse


def create_category(session: Session, payload: CategoryCreate) -> Category:
    existing = session.exec(
        select(Category).where(Category.name == payload.name)
    ).first()
    if existing:
        raise ValueError(f"Category '{payload.name}' already exists")

    category = Category(name=payload.name)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def get_all_categories(session: Session) -> List[CategoryResponse]:
    categories = session.exec(
        select(Category).where(Category.is_active == True)  # noqa: E712
    ).all()

    results = []
    for cat in categories:
        vendor_total = _count_vendors_for_category(session, cat.id)
        results.append(
            CategoryResponse(
                id=cat.id,
                name=cat.name,
                created_at=cat.created_at,
                vendor_total=vendor_total,
            )
        )
    return results


def get_category_by_id(session: Session, category_id: UUID) -> Optional[Category]:
    return session.exec(
        select(Category).where(
            Category.id == category_id,
            Category.is_active == True,  # noqa: E712
        )
    ).first()


def update_category(
    session: Session, category_id: UUID, payload: CategoryUpdate
) -> Optional[Category]:
    category = get_category_by_id(session, category_id)
    if not category:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)

    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def delete_category(session: Session, category_id: UUID) -> Optional[Category]:
    category = get_category_by_id(session, category_id)
    if not category:
        return None

    category.is_active = False
    category.deleted_at = datetime.utcnow()
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def _count_vendors_for_category(session: Session, category_id: UUID) -> int:
    # Count distinct vendors that supply at least one item in this category
    result = session.exec(
        select(func.count(func.distinct(Item.vendor_id))).where(
            Item.category_id == category_id,
            Item.is_active == True,  # noqa: E712
        )
    ).one()
    return result or 0
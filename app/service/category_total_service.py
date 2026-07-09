from typing import Dict
from uuid import UUID

from sqlmodel import Session

from app.model.category import Category
from app.repository import category_repository_totals


def get_total_items_across_categories(session: Session) -> Dict:
    total_items = category_repository_totals.count_total_items_across_categories(session)
    return {"total_items": int(total_items or 0)}


def get_total_items_for_category(session: Session, category_id: UUID) -> Dict:
    category = session.get(Category, category_id)
    if not category or not category.is_active:
        raise ValueError("Category not found")

    total_items = category_repository_totals.count_total_items_for_category(session, category_id)
    return {
        "category_id": category_id,
        "total_items": int(total_items or 0),
    }


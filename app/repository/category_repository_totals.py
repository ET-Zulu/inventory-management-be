from typing import List, Tuple
from uuid import UUID

from sqlalchemy import func
from sqlmodel import Session, select

from app.model.category import Category
from app.model.item import Item


def count_total_items_across_categories(session: Session) -> int:
    result = session.exec(
        select(func.coalesce(func.sum(Item.quantity_on_hand), 0))
        .join(Category, Item.category_id == Category.id)  # type: ignore
        .where(
            Category.is_active == True,  # noqa: E712
            Item.is_active == True,  # noqa: E712
        )
    ).one()

    return int(result or 0)


def count_total_items_for_category(session: Session, category_id: UUID) -> int:
    result = session.exec(
        select(func.coalesce(func.sum(Item.quantity_on_hand), 0))
        .join(Category, Item.category_id == Category.id)  # type: ignore
        .where(
            Category.id == category_id,
            Category.is_active == True,  # noqa: E712
            Item.is_active == True,  # noqa: E712
        )
    ).one()

    return int(result or 0)


from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select, func
from app.model.category import Category
from app.model.item import Item


def get_category_by_name(session: Session, name: str) -> Optional[Category]:
    return session.exec(
        select(Category).where(Category.name == name)
    ).first()


def get_all_active_categories(session: Session ,page: int,limit: int,) -> List[Category]:
    
    offset = (page - 1) * limit
    data =session.exec(
        select(Category).where(Category.is_active == True).offset(offset).limit(limit)  # noqa: E712
    ).all()

    total = session.exec(
        select(func.count()).select_from(Category).where(Category.is_active == True) 
     )
    
    return data , total.one()





def get_category_by_id(session: Session, category_id: UUID) -> Optional[Category]:
    return session.exec(
        select(Category).where(
            Category.id == category_id,
            Category.is_active == True,  # noqa: E712
        )
    ).first()


def save_category(session: Session, category: Category) -> Category:
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def count_vendors_for_category(session: Session, category_id: UUID) -> int:
    # Distinct vendors that have at least one active item in this category
    result = session.exec(
        select(func.count(func.distinct(Item.vendor_id))).where(
            Item.category_id == category_id,
            Item.is_active == True,  # noqa: E712
        )
    ).one()
    return result or 0

from typing import List, Optional, Tuple
from uuid import UUID
from sqlmodel import Session, select, func, or_, col
from app.model.item import Item
from app.model.transaction import Transaction


def get_item_by_sku(session: Session, sku: str) -> Optional[Item]:
    # Case-insensitive — "kbd-001" and "KBD-001" are the same SKU
    sku_upper = sku.strip().upper()
    return session.exec(
        select(Item).where(func.upper(Item.sku) == sku_upper)
    ).first()


def get_item_by_id(session: Session, item_id: UUID) -> Optional[Item]:
    return session.exec(
        select(Item).where(
            Item.id == item_id,
            Item.is_active == True,  # noqa: E712
        )
    ).first()


def get_filtered_items(
    session: Session,
    page: int = 1,
    limit: int = 20,
    category_id: Optional[UUID] = None,
    vendor_id: Optional[UUID] = None,
    search: Optional[str] = None,
    low_stock: bool = False,
) -> Tuple[List[Item], int]:
    query = select(Item).where(Item.is_active == True)  # noqa: E712

    if category_id:
        query = query.where(Item.category_id == category_id)
    if vendor_id:
        query = query.where(Item.vendor_id == vendor_id)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                col(Item.name).ilike(pattern),
                col(Item.sku).ilike(pattern),
            )
        )
    if low_stock:
        query = query.where(Item.quantity_on_hand <= Item.minimum_stock_level)

    total = session.exec(select(func.count()).select_from(query.subquery())).one()
    offset = (page - 1) * limit
    items = session.exec(query.offset(offset).limit(limit)).all()
    return items, (total or 0)


def count_active_skus(session: Session) -> int:
    result = session.exec(
        select(func.count()).where(Item.is_active == True)  # noqa: E712
    ).one()
    return result or 0


def count_below_threshold(session: Session) -> int:
    result = session.exec(
        select(func.count()).where(
            Item.is_active == True,  # noqa: E712
            Item.quantity_on_hand <= Item.minimum_stock_level,
        )
    ).one()
    return result or 0


def save_item(session: Session, item: Item) -> Item:
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def has_transactions(session: Session, item_id: UUID) -> bool:
    return session.exec(
        select(Transaction).where(Transaction.item_id == item_id)
    ).first() is not None


def delete_item_hard(session: Session, item: Item) -> None:
    session.delete(item)
    session.commit()


def get_total_quantity(session: Session) -> int:
    return session.exec(
        select(func.coalesce(func.sum(Item.quantity_on_hand), 0)).where(
            Item.is_active == True  # noqa: E712
        )
    ).one() or 0


def get_total_minimum_stock_level(session: Session) -> int:
    return session.exec(
        select(func.coalesce(func.sum(Item.minimum_stock_level), 0)).where(
            Item.is_active == True  # noqa: E712
        )
    ).one() or 0

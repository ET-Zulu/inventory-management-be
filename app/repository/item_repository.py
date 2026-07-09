from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.model.bin import Bin
from app.model.item import Item
from app.model.transaction import Transaction


def get_item_by_sku(session: Session, sku: str) -> Optional[Item]:
    return session.exec(
        select(Item).where(
            func.lower(Item.sku) == sku.strip().lower()
        )
    ).first()


def get_item_by_id(session: Session, item_id: UUID) -> Optional[Item]:
    return session.exec(
        select(Item).where(Item.id == item_id)
    ).first()


def save_item(session: Session, item: Item) -> Item:
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def get_filtered_items(
    session: Session,
    page: int,
    limit: int,
    category_id: Optional[UUID] = None,
    vendor_id: Optional[UUID] = None,
    warehouse_id: Optional[UUID] = None,
    bin_id: Optional[UUID] = None,
    search: Optional[str] = None,
    low_stock: bool = False,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> Tuple[List[Item], int]:
    query = select(Item).where(Item.is_active == True)  # noqa: E712
    count_query = select(func.count()).select_from(Item).where(
        Item.is_active == True
    )  # noqa: E712

    joined_bin = False
    if warehouse_id is not None:
        query = query.join(Bin, Item.bin_id == Bin.id).where(Bin.warehouse_id == warehouse_id)
        count_query = count_query.join(Bin, Item.bin_id == Bin.id).where(Bin.warehouse_id == warehouse_id)
        joined_bin = True

    if bin_id is not None:
        query = query.where(Item.bin_id == bin_id)
        count_query = count_query.where(Item.bin_id == bin_id)

    if category_id is not None:
        query = query.where(Item.category_id == category_id)
        count_query = count_query.where(Item.category_id == category_id)

    if vendor_id is not None:
        query = query.where(Item.vendor_id == vendor_id)
        count_query = count_query.where(Item.vendor_id == vendor_id)

    if search:
        search_term = f"%{search.strip().lower()}%"
        search_filter = or_(
            func.lower(Item.name).like(search_term),
            func.lower(Item.sku).like(search_term),
            func.lower(Item.description).like(search_term),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    if low_stock:
        low_stock_filter = Item.quantity_on_hand <= Item.minimum_stock_level
        query = query.where(low_stock_filter)
        count_query = count_query.where(low_stock_filter)

    sort_column = {
        "name": Item.name,
        "sku": Item.sku,
        "quantity_on_hand": Item.quantity_on_hand,
        "created_at": Item.created_at,
    }.get(sort_by, Item.created_at)

    sort_attr = sort_column.asc() if sort_order.lower() == "asc" else sort_column.desc()
    query = query.order_by(sort_attr)

    total = session.exec(count_query).one()

    offset = (page - 1) * limit
    items = session.exec(query.offset(offset).limit(limit)).all()
    return items, total or 0


def count_active_skus(session: Session) -> int:
    result = session.exec(
        select(func.count()).select_from(Item).where(Item.is_active == True)  # noqa: E712
    ).one()
    return result or 0


def count_below_threshold(session: Session) -> int:
    result = session.exec(
        select(func.count()).select_from(Item).where(
            Item.is_active == True,  # noqa: E712
            Item.quantity_on_hand <= Item.minimum_stock_level,
        )
    ).one()
    return result or 0


def has_transactions(session: Session, item_id: UUID) -> bool:
    result = session.exec(
        select(func.count()).select_from(Transaction).where(
            Transaction.item_id == item_id
        )
    ).one()
    return (result or 0) > 0


def delete_item_hard(session: Session, item: Item) -> None:
    session.delete(item)
    session.commit()


def get_total_quantity(session: Session) -> int:
    result = session.exec(
        select(func.coalesce(func.sum(Item.quantity_on_hand), 0)).where(
            Item.is_active == True  # noqa: E712
        )
    ).one()
    return int(result or 0)


def get_total_minimum_stock_level(session: Session) -> int:
    result = session.exec(
        select(func.coalesce(func.sum(Item.minimum_stock_level), 0)).where(
            Item.is_active == True  # noqa: E712
        )
    ).one()
    return int(result or 0)

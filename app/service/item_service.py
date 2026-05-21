from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlmodel import Session, select, func, or_, col

from app.model.item import Item
from app.model.transaction import Transaction


def derive_status(item: Item) -> str:
    if item.quantity_on_hand == 0:
        return "out of stock"
    if item.quantity_on_hand <= item.minimum_stock_level:
        return "low stock"
    return "in stock"


def create_item(session: Session, payload) -> Item:
    # SKU check is case-insensitive — "kbd-001" and "KBD-001" are the same
    sku_upper = payload.sku.strip().upper()

    existing = session.exec(
        select(Item).where(func.upper(Item.sku) == sku_upper)
    ).first()
    if existing:
        raise ValueError(f"SKU '{payload.sku}' already exists")

    item = Item(
        sku=payload.sku.strip(),
        name=payload.name,
        description=payload.description,
        quantity_on_hand=payload.initial_stock,
        minimum_stock_level=payload.minimum_stock_level,
        cost_price=payload.cost_price,
        selling_price=payload.selling_price,
        category_id=payload.category_id,
        vendor_id=payload.vendor_id,
        location=payload.bin_location or "",
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def get_all_items(
    session: Session,
    *,
    page: int = 1,
    limit: int = 20,
    category_id: Optional[UUID] = None,
    vendor_id: Optional[UUID] = None,
    search: Optional[str] = None,
    low_stock: bool = False,
) -> Dict:
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

    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    offset = (page - 1) * limit
    items = session.exec(query.offset(offset).limit(limit)).all()

    # Summary stats are always across all active items, not just the current filter
    active_skus = session.exec(
        select(func.count()).where(Item.is_active == True)  # noqa: E712
    ).one()

    below_threshold = session.exec(
        select(func.count()).where(
            Item.is_active == True,  # noqa: E712
            Item.quantity_on_hand <= Item.minimum_stock_level,
        )
    ).one()

    return {
        "summary": {
            "active_skus": active_skus or 0,
            "below_threshold": below_threshold or 0,
        },
        "data": items,
        "page": page,
        "limit": limit,
        "total": total or 0,
    }


def get_item_by_id(session: Session, item_id: UUID) -> Optional[Item]:
    return session.exec(
        select(Item).where(
            Item.id == item_id,
            Item.is_active == True,  # noqa: E712
        )
    ).first()


def update_item(session: Session, item_id: UUID, payload) -> Optional[Item]:
    item = get_item_by_id(session, item_id)
    if not item:
        return None

    update_data = payload.model_dump(exclude_unset=True)

    # SKU is immutable, drop it silently if someone passes it
    update_data.pop("sku", None)

    # Schema uses bin_location but the model field is location
    if "bin_location" in update_data:
        update_data["location"] = update_data.pop("bin_location") or ""

    for key, value in update_data.items():
        setattr(item, key, value)

    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_item(session: Session, item_id: UUID) -> Tuple[Optional[Item], str]:
    item = get_item_by_id(session, item_id)
    if not item:
        return None, "not_found"

    # Can't hard delete if transactions reference this item
    has_transactions = session.exec(
        select(Transaction).where(Transaction.item_id == item_id)
    ).first()

    if has_transactions:
        item.is_active = False
        item.deleted_at = datetime.utcnow()
        session.add(item)
        session.commit()
        session.refresh(item)
        return item, "soft_deleted"
    else:
        session.delete(item)
        session.commit()
        return item, "hard_deleted"


def get_storage_capacity(session: Session) -> Dict:
    total_quantity = session.exec(
        select(func.coalesce(func.sum(Item.quantity_on_hand), 0)).where(
            Item.is_active == True  # noqa: E712
        )
    ).one()

    # Using sum of minimum_stock_levels as a capacity baseline per item slot
    total_capacity = session.exec(
        select(func.coalesce(func.sum(Item.minimum_stock_level), 0)).where(
            Item.is_active == True  # noqa: E712
        )
    ).one()

    if total_capacity == 0:
        used_percent = 0.0
        free_percent = 100.0
    else:
        used_percent = round((total_quantity / total_capacity) * 100, 2)
        free_percent = round(100.0 - used_percent, 2)

    return {
        "total_quantity": total_quantity,
        "total_capacity": total_capacity,
        "used_percent": used_percent,
        "free_percent": free_percent,
    }
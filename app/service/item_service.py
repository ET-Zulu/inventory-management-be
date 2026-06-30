from datetime import datetime
from typing import Dict, Optional, Tuple
from uuid import UUID

from sqlmodel import Session

from app.model.item import Item
from app.repository import item_repository


def derive_status(item: Item) -> str:
    if item.quantity_on_hand == 0:
        return "out of stock"
    if item.quantity_on_hand <= item.minimum_stock_level:
        return "low stock"
    return "in stock"


def create_item(session: Session, payload) -> Item:
    existing = item_repository.get_item_by_sku(session, payload.sku)
    if existing:
        if existing.is_active:
            raise ValueError(f"SKU '{payload.sku}' already exists")
        # Reactivate soft-deleted item with the new creation payload
        existing.is_active = True
        existing.deleted_at = None
        existing.name = payload.name
        existing.description = payload.description
        existing.quantity_on_hand = payload.initial_stock
        existing.minimum_stock_level = payload.minimum_stock_level
        existing.cost_price = payload.cost_price
        existing.selling_price = payload.selling_price
        existing.category_id = payload.category_id
        existing.vendor_id = payload.vendor_id
        existing.warehouse_id = payload.warehouse_id
        existing.location = payload.bin_location or ""
        return item_repository.save_item(session, existing)

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
        warehouse_id=payload.warehouse_id,
        location=payload.bin_location or "",
        Itemtypes=payload.Itemtypes
    )
    return item_repository.save_item(session, item)


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
    items, total = item_repository.get_filtered_items(
        session, page, limit, category_id, vendor_id, search, low_stock
    )

    active_skus = item_repository.count_active_skus(session)
    below_threshold = item_repository.count_below_threshold(session)

    return {
        "summary": {
            "active_skus": active_skus,
            "below_threshold": below_threshold,
        },
        "data": items,
        "page": page,
        "limit": limit,
        "total": total,
    }


def get_item_by_id(session: Session, item_id: UUID) -> Optional[Item]:
    return item_repository.get_item_by_id(session, item_id)


def update_item(session: Session, item_id: UUID, payload) -> Optional[Item]:
    item = item_repository.get_item_by_id(session, item_id)
    if not item:
        return None

    update_data = payload.model_dump(exclude_unset=True)

    update_data.pop("sku", None)

    if "bin_location" in update_data:
        update_data["location"] = update_data.pop("bin_location") or ""

    for key, value in update_data.items():
        setattr(item, key, value)

    return item_repository.save_item(session, item)


def delete_item(session: Session, item_id: UUID) -> Tuple[Optional[Item], str]:
    item = item_repository.get_item_by_id(session, item_id)
    if not item:
        return None, "not_found"

    has_tx = item_repository.has_transactions(session, item_id)

    if has_tx:
        item.is_active = False
        item.deleted_at = datetime.utcnow()
        saved_item = item_repository.save_item(session, item)
        return saved_item, "soft_deleted"
    else:
        item_repository.delete_item_hard(session, item)
        return item, "hard_deleted"


def get_storage_capacity(session: Session) -> Dict:
    total_quantity = item_repository.get_total_quantity(session)
    # Business decision: we treat the sum of minimum_stock_level as total capacity
    total_capacity = item_repository.get_total_minimum_stock_level(session)

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

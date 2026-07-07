from datetime import datetime
from typing import Dict, Optional, Tuple
from uuid import UUID
import re

from sqlmodel import Session

from app.model.category import Category
from app.model.item import Item
from app.model.enums import Itemtype
from app.model.vendor import Vendor
from app.model.warehouse import Warehouse
from app.repository import item_repository, warehouse_repository


def derive_status(item: Item) -> str:
    if item.quantity_on_hand == 0:
        return "out of stock"
    if item.quantity_on_hand <= item.minimum_stock_level:
        return "low stock"
    return "in stock"


def _parse_item_type(value: Optional[str]) -> Itemtype:
    if not value:
        return Itemtype.SALLABLE

    normalized = value.strip().upper()
    try:
        return Itemtype(normalized)
    except ValueError:
        return Itemtype.SALLABLE


def _validate_item_references(session: Session, payload) -> None:
    if payload.vendor_id is None:
        raise ValueError("vendor_id is required")

    if payload.warehouse_id is None:
        raise ValueError("warehouse_id is required")

    vendor = session.get(Vendor, payload.vendor_id)
    if not vendor or not vendor.is_active:
        raise ValueError(f"vendor '{payload.vendor_id}' not found or inactive")

    warehouse = session.get(Warehouse, payload.warehouse_id)
    if not warehouse or not warehouse.is_active:
        raise ValueError(f"warehouse '{payload.warehouse_id}' not found or inactive")

    if payload.category_id is not None:
        category = session.get(Category, payload.category_id)
        if not category or not category.is_active:
            raise ValueError(f"category '{payload.category_id}' not found or inactive")


def create_item(session: Session, payload) -> Item:
    sku = payload.sku.strip().upper()

    if not re.fullmatch(r"SKU-\d{3,}", sku):
        raise ValueError("SKU must follow the format SKU-001")

    _validate_item_references(session, payload)

    existing = item_repository.get_item_by_sku(session, sku)

    if existing:
        if existing.is_active:
            raise ValueError(f"SKU '{sku}' already exists")

        existing.is_active = True
        existing.deleted_at = None
        existing.sku = sku
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
        existing.item_type = _parse_item_type(getattr(payload, "Itemtypes", None))

        return item_repository.save_item(session, existing)

    item = Item(
        sku=sku,
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
        item_type=_parse_item_type(getattr(payload, "Itemtypes", None)),
    )

    return item_repository.save_item(session, item)


def get_all_items(
    session: Session,
    *,
    page: int = 1,
    limit: int = 20,
    category_id: Optional[UUID] = None,
    vendor_id: Optional[UUID] = None,
    warehouse_id: Optional[UUID] = None,
    search: Optional[str] = None,
    low_stock: bool = False,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> Dict:
    items, total = item_repository.get_filtered_items(
        session,
        page,
        limit,
        category_id=category_id,
        vendor_id=vendor_id,
        warehouse_id=warehouse_id,
        search=search,
        low_stock=low_stock,
        sort_by=sort_by,
        sort_order=sort_order,
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

    if "vendor_id" in update_data and update_data["vendor_id"] is not None:
        vendor = session.get(Vendor, update_data["vendor_id"])
        if not vendor or not vendor.is_active:
            raise ValueError(f"vendor '{update_data['vendor_id']}' not found or inactive")

    if "warehouse_id" in update_data and update_data["warehouse_id"] is not None:
        warehouse = session.get(Warehouse, update_data["warehouse_id"])
        if not warehouse or not warehouse.is_active:
            raise ValueError(f"warehouse '{update_data['warehouse_id']}' not found or inactive")

    if "category_id" in update_data and update_data["category_id"] is not None:
        category = session.get(Category, update_data["category_id"])
        if not category or not category.is_active:
            raise ValueError(f"category '{update_data['category_id']}' not found or inactive")

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

def check_sku_availability(session: Session, sku: str) -> Dict:
    sku = sku.strip().upper()

    # Only allow SKU-001, SKU-002, etc.
    if not re.fullmatch(r"SKU-\d{3,}", sku):
        return {
            "sku": sku,
            "available": False,
            "message": "SKU must follow the format SKU-001"
        }

    existing = item_repository.get_item_by_sku(session, sku)

    if existing and existing.is_active:
        return {
            "sku": sku,
            "available": False,
            "message": f"{sku} is already in use"
        }

    return {
        "sku": sku,
        "available": True,
        "message": f"{sku} is available"
    }
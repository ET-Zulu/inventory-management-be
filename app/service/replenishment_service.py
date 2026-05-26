from sqlmodel import Session, select
from collections import defaultdict

from app.model.item import Item
from app.model.vendor import Vendor
from app.model.category import Category

def get_replenishment_service(session: Session, search: str = None, category: str = None):

    query = (
        select(Item, Vendor)
        .join(Vendor, Item.vendor_id == Vendor.id)
        .distinct(Item.id)   
    )

    if category:
        query = query.join(Category, Item.category_id == Category.id).where(
            Category.name.ilike(f"%{category}%")
        )

    results = session.exec(query).all()

    grouped = defaultdict(list)

    total_reorder_value = 0
    out_of_stock = 0
    pending_order = 0
    critical_low_stock = 0

    for item, vendor in results:

        if search:
            if search.lower() not in item.name.lower() and search.lower() not in item.sku.lower():
                continue

        current_stock = item.quantity_on_hand
        threshold = item.minimum_stock_level

        qty_needed = max(threshold - current_stock, 0)
        estimated_cost = qty_needed * item.cost_price

        if current_stock == 0:
            out_of_stock += 1
        elif current_stock < threshold * 0.5:
            critical_low_stock += 1
        elif current_stock < threshold:
            pending_order += 1

        total_reorder_value += estimated_cost

        grouped[vendor.name].append({
            "item_name": item.name,
            "sku": item.sku,
            "current_stock": current_stock,
            "threshold": threshold,
            "qty_needed": qty_needed,
            "estimated_cost": estimated_cost
        })

    return {
        "total_reorder_value": total_reorder_value,
        "out_of_stock": out_of_stock,
        "pending_order": pending_order,
        "critical_low_stock": critical_low_stock,
        "items_grouped_by_vendor": dict(grouped)
    }
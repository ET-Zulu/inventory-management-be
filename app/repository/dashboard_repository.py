from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from sqlalchemy import cast, extract, func, or_, String, case
from sqlmodel import Session, select, col, desc

from app.model.item import Item
from app.model.vendor import Vendor
from app.model.transaction import Transaction
from app.model.enums import TransactionType


def get_dashboard_summary_metrics(session: Session) -> dict[str, Any]:
    total_items = session.exec(
        select(func.count()).select_from(Item).where(col(Item.is_active) == True)
    ).first() or 0

    low_stock = session.exec(
        select(func.count()).select_from(Item).where(
            col(Item.is_active) == True,
            col(Item.quantity_on_hand) <= 10
        )
    ).first() or 0

    inventory_value = session.exec(
        select(func.sum(col(Item.quantity_on_hand) * col(Item.cost_price)))
    ).first() or 0

    active_vendors = session.exec(
        select(func.count()).select_from(Vendor).where(col(Vendor.is_active) == True)
    ).first() or 0

    return {
        "total_items": int(total_items),
        "low_stock": int(low_stock),
        "inventory_value": float(inventory_value),
        "active_vendors": int(active_vendors),
    }


def fetch_monthly_stock_movements(session: Session) -> list[dict[str, Any]]:
    month_expr = extract("month", col(Transaction.created_at))
    
    statement = (
        select(
            month_expr,
            func.sum(case({Transaction.transaction_type == TransactionType.INBOUND: func.coalesce(Transaction.quantity_change, 0)}, else_=0)),
            func.sum(case({Transaction.transaction_type == TransactionType.OUTBOUND: func.coalesce(Transaction.quantity_change, 0)}, else_=0)),
        )
        .group_by(month_expr)
        .order_by(month_expr.asc())
    )
    
    results = session.exec(statement).all()
    
    month_map = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
    }

    return [
        {
            "month": month_map.get(int(row[0]), "Unknown"),
            "stock_in": int(row[1] or 0),
            "stock_out": int(row[2] or 0)
        }
        for row in results
    ]


def fetch_recent_dashboard_transactions(session: Session, limit: int = 5) -> list[Transaction]:
    statement = (
        select(Transaction)
        .join(Item)
        .order_by(desc(Transaction.created_at))
        .limit(limit)
    )
    return session.exec(statement).all()  # type: ignore


def execute_dashboard_global_search(session: Session, query: str) -> dict[str, list[dict]]:
    search_text = f"%{query}%"

    items = session.exec(
        select(Item).where(
            or_(
                col(Item.name).ilike(search_text),
                col(Item.sku).ilike(search_text)
            )
        ).limit(10)
    ).all()

    vendors = session.exec(
        select(Vendor).where(
            or_(
                col(Vendor.name).ilike(search_text),
                col(Vendor.contact_info).ilike(search_text)  
                )
        ).limit(10)
    ).all()

    return {
        "inventory": [{"id": str(i.id), "name": i.name, "sku": i.sku, "qty": i.quantity_on_hand} for i in items],
        "vendors": [{"id": str(v.id), "name": v.name, "email": v.contact_info} for v in vendors]
    }
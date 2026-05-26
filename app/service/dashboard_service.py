from sqlmodel import Session
from typing import Optional
from ...app.repository import dashboard_repository as repo

def get_dashboard_overview(db: Session) -> dict:
    
    metrics = repo.get_dashboard_summary_metrics(db)
    chart = repo.fetch_monthly_stock_movements(db)
    recent_txs = repo.fetch_recent_dashboard_transactions(db, limit=5)

    formatted_txs = [
        {
            "id": str(tx.id),
            "item": tx.item.name,
            "sku": tx.item.sku,
            "transaction_type": tx.transaction_type,
            "quantity_change": tx.quantity_change,
            "created_at": tx.created_at.isoformat(),
        }
        for tx in recent_txs
    ]

    return {
        "total_items": metrics["total_items"],
        "low_stock": metrics["low_stock"],
        "inventory_value": metrics["inventory_value"],
        "active_vendors": metrics["active_vendors"],
        "stock_movement_chart": chart,
        "recent_transactions": formatted_txs,
    }

def search_dashboard_entities(db: Session, query: Optional[str]) -> dict:
    if not query or not query.strip():
        return {"inventory": [], "vendors": []}
        
    return repo.execute_dashboard_global_search(db, query.strip())
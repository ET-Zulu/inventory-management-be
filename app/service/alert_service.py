from sqlmodel import Session, select
from app.model.item import Item


def calculate_severity(stock: int, threshold: int) -> str:
    if stock == 0:
        return "critical"
    elif stock < threshold * 0.5:
        return "high"
    elif stock < threshold:
        return "warning"
    return "safe"


def get_alerts_service(session: Session):

    items = session.exec(select(Item)).all()

    alerts = []

    for item in items:

        if item.quantity_on_hand < item.minimum_stock_level:

            alerts.append({
                "item_name": item.name,
                "stock": item.quantity_on_hand,
                "threshold": item.minimum_stock_level,
                "severity": calculate_severity(
                    item.quantity_on_hand,
                    item.minimum_stock_level
                )
            })

    # sort by severity priority
    severity_order = {"critical": 0, "high": 1, "warning": 2}

    alerts.sort(key=lambda x: severity_order.get(x["severity"], 3))

    return alerts
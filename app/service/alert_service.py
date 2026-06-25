from sqlmodel import Session, select
from app.model.item import Item
from app.model.notification import Notification


from app.utilts.websocket_helper import manager


def calculate_severity(stock: int, threshold: int) -> str:
    if stock == 0:
        return "critical"
    elif stock < threshold * 0.5:
        return "high"
    elif stock < threshold:
        return "warning"
    return "safe"


async def get_alerts_service(session: Session):


    # remove N+1 query by fetching all items at once and calculating alerts in memory
    items = session.exec(
        select(Item).where(
            Item.quantity_on_hand < Item.minimum_stock_level
        )
    ).all()

    

    alerts = []

    for item in items:
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


async def create_notification(
    session: Session,
    *,
    title: str,
    message: str,
    notification_type: str,
    severity: str,
    item_id=None
):

    existing = session.exec(
        select(Notification).where(
            Notification.type == notification_type,
            Notification.item_id == item_id,
            Notification.is_read == False
        )
    ).first()

    if existing:
        return existing

    notification = Notification(
        title=title,
        message=message,
        type=notification_type,
        severity=severity,
        item_id=item_id
    )

    session.add(notification)
    session.commit()
    session.refresh(notification)

    await manager.broadcast({
        "event": "NEW_NOTIFICATION",
        "notification": {
            "id": str(notification.id),
            "title": notification.title,
            "message": notification.message,
            "type": notification.type,
            "severity": notification.severity,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat()
        }
    })

    return notification


def get_notifications_service(
    session: Session,
    page: int = 1,
    page_size: int = 20
):

    statement = (
        select(Notification)
        .order_by(Notification.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    return session.exec(statement).all()

def get_unread_count_service(
    session: Session
):
    notifications = session.exec(
        select(Notification)
        .where(Notification.is_read == False)
    ).all()

    return len(notifications)


def mark_notification_read_service(
    notification_id,
    session: Session
):

    notification = session.get(
        Notification,
        notification_id
    )

    if not notification:
        return None

    notification.is_read = True

    session.add(notification)
    session.commit()

    return notification

def mark_all_read_service(
    session: Session
):

    notifications = session.exec(
        select(Notification)
        .where(Notification.is_read == False)
    ).all()

    for notification in notifications:
        notification.is_read = True

    session.commit()

    return True
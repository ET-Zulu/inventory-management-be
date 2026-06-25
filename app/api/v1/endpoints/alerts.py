from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.dependencies.auth import get_current_active_user
from app.service.alert_service import get_alerts_service, get_notifications_service, get_unread_count_service, mark_all_read_service, mark_notification_read_service

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.utilts.websocket_helper import manager


router = APIRouter(tags=["alerts"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.get("/alerts", dependencies=[Depends(get_current_active_user)])
def get_alerts(session: Session = Depends(get_session)):
    return get_alerts_service(session)

@router.get("/alerts/notifications", dependencies=[Depends(get_current_active_user)])
def get_notifications(session: Session = Depends(get_session)):
    return get_notifications_service(session)
#  get unread notifications
@router.get("/alerts/notifications/unread_count", dependencies=[Depends(get_current_active_user)])
def get_unread_count(session: Session = Depends(get_session)):
    return get_unread_count_service(session)

# mark notification as read
@router.post("/alerts/notifications/{notification_id}/mark_read", dependencies=[Depends(get_current_active_user)])  
def mark_notification_read(notification_id: str, session: Session = Depends(get_session)):
    return mark_notification_read_service(notification_id, session)

# mark all notifications as read
@router.post("/alerts/notifications/mark_all_read", dependencies=[Depends(get_current_active_user
)])
def mark_all_notifications_read(session: Session = Depends(get_session)):
    return mark_all_read_service(session)


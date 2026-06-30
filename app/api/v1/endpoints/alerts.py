from fastapi import APIRouter, Depends
from fastapi.params import Query
from sqlmodel import Session

from app.core.database import get_session
from app.dependencies.auth import get_current_active_user
from app.service.alert_service import get_alerts_service, get_notifications_service, get_unread_count_service, mark_all_read_service, mark_notification_read_service

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.utilts.websocket_helper import manager


router = APIRouter(tags=["alerts"])

from fastapi import WebSocket, WebSocketDisconnect, Query, status
from jose import jwt, JWTError
from app.core.config import settings


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(None)
):
    # 1. Reject if no token
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 2. Validate JWT
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        user_id: str = payload.get("sub")
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 3. Accept ONLY after auth passes
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.get("/alerts", dependencies=[Depends(get_current_active_user)])
async def get_alerts(session: Session = Depends(get_session)):
    return await get_alerts_service(session)

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


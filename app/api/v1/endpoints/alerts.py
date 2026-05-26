from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.service.alert_service import get_alerts_service

router = APIRouter(tags=["alerts"])


@router.get("/alerts")
def get_alerts(session: Session = Depends(get_session)):
    return get_alerts_service(session)
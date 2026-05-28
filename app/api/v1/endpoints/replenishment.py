from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_session
from app.service.replenishment_service import get_replenishment_service
from app.service.alert_service import get_alerts_service

router = APIRouter(tags=["replenishment"])


@router.get("/replenishment")
def get_replenishment(
    search: str | None = Query(None),
    category: str | None = Query(None),
    session: Session = Depends(get_session)
):
    return get_replenishment_service(session, search, category)


@router.get("/alerts")
def get_alerts(session: Session = Depends(get_session)):
    return get_alerts_service(session)
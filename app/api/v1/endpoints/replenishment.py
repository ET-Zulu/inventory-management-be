from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_session
from app.dependencies.auth import get_current_active_user
from app.service.replenishment_service import get_replenishment_service
from app.service.alert_service import get_alerts_service

router = APIRouter(tags=["replenishment"])


@router.get("/replenishment", dependencies=[Depends(get_current_active_user)])
def get_replenishment(
    search: str | None = Query(None),
    category: str | None = Query(None),
    session: Session = Depends(get_session)
):
    return get_replenishment_service(session, search, category)


@router.get("/alerts", dependencies=[Depends(get_current_active_user)])
async def get_alerts(session: Session = Depends(get_session)):
    return await get_alerts_service(session)
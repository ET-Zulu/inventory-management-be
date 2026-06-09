from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_session
from app.dependencies.auth import get_current_active_user
from app.schemas import SuccessResponse, success_response
from app.service.dashboard_service import get_dashboard_overview, search_dashboard_entities

router = APIRouter()

@router.get("", response_model=SuccessResponse, dependencies=[Depends(get_current_active_user)])
def dashboard_overview(db: Session = Depends(get_session)):
    data = get_dashboard_overview(db)
    return success_response(message="Dashboard data retrieved successfully", data=data)


@router.get("/search", response_model=SuccessResponse, dependencies=[Depends(get_current_active_user)])
def dashboard_search(
    q: Optional[str] = Query(default=None, description="Search globally by item, sku, or vendor info"),
    db: Session = Depends(get_session)
):
    search_results = search_dashboard_entities(db, q)
    return success_response(message="Search completed successfully", data=search_results)
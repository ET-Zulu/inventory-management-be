from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_session
from app.dependencies.auth import get_admin
from app.model.enums import UserRole
from app.model.user import User
from app.schemas.user import UserListResponse
from app.service.auth_service import list_users

router = APIRouter()


@router.get("", response_model=UserListResponse, dependencies=[Depends(get_admin)])
def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: UserRole | None = Query(default=None),
    db: Session = Depends(get_session),
) -> UserListResponse:
    return list_users(db, page=page, limit=limit, role=role)

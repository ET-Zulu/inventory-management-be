from datetime import timedelta
from typing import Any
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.core import security
from app.core.config import settings
from app.core.database import get_session
from app.dependencies.auth import get_admin, get_current_user
from app.model.enums import UserRole
from app.model.user import User
from app.schemas.auth import (
    AdminSetupRequest,
    InviteCreateRequest,
    InviteCreateResponse,
    LoginRequest,
    SetupPasswordRequest,
    SetupPasswordResponse,
)
from app.schemas.token import Token
from app.service.auth_service import create_invite, setup_password

router = APIRouter()


def _build_access_token_response(user: User) -> Token:
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login", response_model=Token)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_session),
) -> Any:
    user = db.exec(select(User).where(User.email == payload.email)).first()
    if user is None or not security.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return _build_access_token_response(user)


@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    user = db.exec(select(User).where(User.email == form_data.username)).first()
    if user is None or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return _build_access_token_response(user)


@router.post("/login/test-token", response_model=dict)
def test_token(current_user: User = Depends(get_current_user)) -> Any:
    return {"id": current_user.id, "email": current_user.email, "role": current_user.role}


@router.post("/invite", response_model=InviteCreateResponse)
def create_admin_invite(
    invite_in: InviteCreateRequest,
    db: Session = Depends(get_session),
    admin_user: User = Depends(get_admin),
) -> Any:
    invite, raw_token = create_invite(db, admin_user, invite_in)
    return {
        "invite_token": raw_token,
        "expires_at": invite.expires_at,
    }


@router.post("/setup-password", response_model=SetupPasswordResponse)
def setup_account_password(
    payload: SetupPasswordRequest,
    db: Session = Depends(get_session),
) -> Any:
    user = setup_password(db, payload)
    return user


# create admin account:
@router.post("/create-admin", response_model=SetupPasswordResponse)
def create_admin_account(
    payload: AdminSetupRequest,
    db: Session = Depends(get_session),
) -> Any:
    existing_admin = db.exec(
        select(User).where(User.role == UserRole.ADMIN)
    ).first()
    if existing_admin:
        raise HTTPException(
            status_code=400,
            detail="Admin account already exists. Please use the invite flow to create additional admin accounts.",
        )

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=security.get_password_hash(payload.password),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
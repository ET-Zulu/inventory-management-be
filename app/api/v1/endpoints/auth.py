from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.core import security
from app.core.config import settings
from app.core.database import get_session
from app.dependencies.auth import get_admin, get_current_active_user, get_current_user
from app.model.enums import UserRole
from app.model.refresh_token import RefreshToken
from app.model.user import User
from app.schemas.auth import (
    AdminSetupRequest,
    ChangePasswordRequest,
    EditProfileRequest,
    ForgotPasswordRequest,
    InviteCreateRequest,
    InviteCreateResponse,
    LoginRequest,
    MeResponse,
    ResetPasswordRequest,
    SetupPasswordRequest,
    SetupPasswordResponse,
)
from app.schemas.common import success_response
from app.schemas.token import Token, RefreshTokenRequest, LogoutRequest
from app.service import auth_service
from app.service.auth_service import create_invite, setup_password
import secrets

router = APIRouter()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _stamp_last_login(db: Session, user: User) -> None:
    """Update last_login timestamp and commit."""
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)


def _build_access_token_response(db: Session, user: User) -> Token:
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_str = secrets.token_urlsafe(32)
    refresh_token = RefreshToken(
        token=refresh_token_str,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(refresh_token)
    db.commit()

    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
    }


# ---------------------------------------------------------------------------
# Existing authentication endpoints
# ---------------------------------------------------------------------------

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
    _stamp_last_login(db, user)
    return _build_access_token_response(db, user)


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
    _stamp_last_login(db, user)
    return _build_access_token_response(db, user)


@router.post("/login/test-token", response_model=dict)
def test_token(current_user: User = Depends(get_current_user)) -> Any:
    return {"id": current_user.id, "email": current_user.email, "role": current_user.role}


@router.post("/refresh-token", response_model=Token)
def refresh_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_session),
) -> Any:
    token_record = db.exec(
        select(RefreshToken).where(RefreshToken.token == payload.refresh_token)
    ).first()

    if not token_record:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if token_record.expires_at < datetime.utcnow():
        db.delete(token_record)
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = token_record.user
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive or deleted")

    # Rotate — delete old token before issuing a new one
    db.delete(token_record)
    db.commit()

    return _build_access_token_response(db, user)


@router.post("/logout")
def logout(
    payload: LogoutRequest,
    db: Session = Depends(get_session),
) -> Any:
    token_record = db.exec(
        select(RefreshToken).where(RefreshToken.token == payload.refresh_token)
    ).first()

    if token_record:
        db.delete(token_record)
        db.commit()

    return success_response("Logged out successfully")


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


# ---------------------------------------------------------------------------
# New: current user profile
# ---------------------------------------------------------------------------

@router.get("/me", response_model=MeResponse)
def get_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Return the currently authenticated user's profile."""
    return auth_service.get_me(current_user)


@router.patch("/me", response_model=MeResponse)
def edit_profile(
    payload: EditProfileRequest,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update editable profile fields (name, profile_picture)."""
    return auth_service.edit_profile(db, current_user, payload)


# ---------------------------------------------------------------------------
# New: change password
# ---------------------------------------------------------------------------

@router.patch("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Change the current user's password after verifying the existing one."""
    auth_service.change_password(db, current_user, payload)
    return success_response("Password changed successfully")


# ---------------------------------------------------------------------------
# New: forgot / reset password
# ---------------------------------------------------------------------------

@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_session),
) -> Any:
    """
    Initiate the password reset flow.
    Always returns the same response regardless of whether the email exists.
    """
    auth_service.forgot_password(db, payload)
    return success_response(
        "If an account with that email exists, a password reset link has been sent."
    )


@router.post("/reset-password")
def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_session),
) -> Any:
    """Reset password using a valid, unexpired reset token."""
    auth_service.reset_password(db, payload)
    return success_response("Password has been reset successfully. You can now log in.")

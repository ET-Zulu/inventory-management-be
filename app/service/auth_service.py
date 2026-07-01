from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlmodel import Session, select

from app.core import security
from app.model.enums import UserRole
from app.model.invite_token import InviteToken
from app.model.password_reset_token import PasswordResetToken
from app.model.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    EditProfileRequest,
    ForgotPasswordRequest,
    InviteCreateRequest,
    MeResponse,
    ResetPasswordRequest,
    SetupPasswordRequest,
)
from app.schemas.user import UserListItem, UserListResponse
from app.service.email_service import send_invitation_email, send_password_reset_email


INVITE_TTL_HOURS = 24
RESET_TOKEN_TTL_HOURS = 1


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _generate_invite_token() -> str:
    return secrets.token_urlsafe(32)


# ---------------------------------------------------------------------------
# Existing: invite + setup password
# ---------------------------------------------------------------------------

def create_invite(
    db: Session,
    invited_by: User,
    invite_in: InviteCreateRequest,
) -> tuple[InviteToken, str]:
    if invite_in.role not in {
        UserRole.ADMIN,
        UserRole.OPERATOR,
        UserRole.VIEWER,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite role must be admin, operator, or viewer.",
        )

    now = datetime.utcnow()
    existing_active_invite = db.exec(
        select(InviteToken).where(
            InviteToken.email == invite_in.email,
            InviteToken.used_at.is_(None),
            InviteToken.expires_at > now,
        )
    ).first()
    if existing_active_invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An active invite already exists for this email.",
        )

    existing_user = db.exec(
        select(User).where(User.email == invite_in.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    raw_token = _generate_invite_token()
    invite = InviteToken(
        email=invite_in.email,
        role=invite_in.role,
        token_hash=_hash_token(raw_token),
        invited_by=invited_by.id,
        expires_at=now + timedelta(hours=INVITE_TTL_HOURS),
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)

    send_invitation_email(email=invite_in.email, role=invite_in.role, raw_token=raw_token)

    return invite, raw_token


def setup_password(db: Session, payload: SetupPasswordRequest) -> User:
    now = datetime.utcnow()
    token_hash = _hash_token(payload.token)
    invite = db.exec(
        select(InviteToken).where(InviteToken.token_hash == token_hash)
    ).first()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid invite token.",
        )

    if invite.used_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite token has already been used.",
        )

    if invite.expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite token has expired.",
        )

    if invite.email.lower() != payload.email.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite email does not match.",
        )

    existing_user = db.exec(
        select(User).where(User.email == payload.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=security.get_password_hash(payload.password),
        role=invite.role,
        is_active=True,
    )
    invite.used_at = now

    db.add(user)
    db.add(invite)
    db.commit()
    db.refresh(user)
    return user


def list_users(
    db: Session,
    page: int,
    limit: int,
    role: UserRole | None = None,
) -> UserListResponse:
    filters = []
    if role is not None:
        filters.append(User.role == role)

    total_users = db.exec(
        select(func.count()).select_from(User).where(*filters)
    ).one()

    active_now = db.exec(
        select(func.count()).select_from(User).where(
            *filters,
            User.is_active.is_(True),
        )
    ).one()

    now = datetime.utcnow()
    pending_filters = [
        InviteToken.used_at.is_(None),
        InviteToken.expires_at > now,
    ]
    if role is not None:
        pending_filters.append(InviteToken.role == role)

    pending_invites = db.exec(
        select(func.count()).select_from(InviteToken).where(*pending_filters)
    ).one()

    offset = (page - 1) * limit
    users = db.exec(
        select(User)
        .where(*filters)
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return UserListResponse(
        total_users=total_users,
        active_now=active_now,
        pending_invites=pending_invites,
        data=[UserListItem.model_validate(user) for user in users],
    )


# ---------------------------------------------------------------------------
# New: current user / profile
# ---------------------------------------------------------------------------

def get_me(user: User) -> MeResponse:
    return MeResponse.model_validate(user)


def edit_profile(db: Session, user: User, payload: EditProfileRequest) -> MeResponse:
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return MeResponse.model_validate(user)


# ---------------------------------------------------------------------------
# New: change password
# ---------------------------------------------------------------------------

def change_password(db: Session, user: User, payload: ChangePasswordRequest) -> None:
    if not security.verify_password(payload.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )
    user.password_hash = security.get_password_hash(payload.new_password)
    db.add(user)
    db.commit()


# ---------------------------------------------------------------------------
# New: forgot password
# ---------------------------------------------------------------------------

def forgot_password(db: Session, payload: ForgotPasswordRequest) -> None:
    """
    Always returns without revealing whether the email exists.
    Generates a reset token and emails it only when the account is found.
    """
    now = datetime.utcnow()
    user = db.exec(select(User).where(User.email == payload.email)).first()

    if not user or not user.is_active:
        # Silent return — do not reveal whether the address exists
        return

    raw_token = secrets.token_urlsafe(32)
    reset_token = PasswordResetToken(
        token_hash=_hash_token(raw_token),
        user_id=user.id,
        expires_at=now + timedelta(hours=RESET_TOKEN_TTL_HOURS),
    )
    db.add(reset_token)
    db.commit()

    send_password_reset_email(email=user.email, raw_token=raw_token)


# ---------------------------------------------------------------------------
# New: reset password
# ---------------------------------------------------------------------------

def reset_password(db: Session, payload: ResetPasswordRequest) -> None:
    now = datetime.utcnow()
    token_hash = _hash_token(payload.reset_token)

    record = db.exec(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash
        )
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token.",
        )

    if record.used_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has already been used.",
        )

    if record.expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired.",
        )

    user = record.user
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token.",
        )

    user.password_hash = security.get_password_hash(payload.new_password)
    record.used_at = now

    db.add(user)
    db.add(record)
    db.commit()

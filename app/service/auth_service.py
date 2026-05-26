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
from app.model.user import User
from app.schemas.auth import InviteCreateRequest, SetupPasswordRequest
from app.schemas.user import UserListItem, UserListResponse


INVITE_TTL_HOURS = 24


def _hash_invite_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _generate_invite_token() -> str:
    return secrets.token_urlsafe(32)


def create_invite(
    db: Session,
    invited_by: User,
    invite_in: InviteCreateRequest,
) -> tuple[InviteToken, str]:
    if invite_in.role not in {UserRole.ADMIN, UserRole.OPERATOR}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite role must be admin or operator.",
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
        token_hash=_hash_invite_token(raw_token),
        invited_by=invited_by.id,
        expires_at=now + timedelta(hours=INVITE_TTL_HOURS),
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite, raw_token


def setup_password(db: Session, payload: SetupPasswordRequest) -> User:
    now = datetime.utcnow()
    token_hash = _hash_invite_token(payload.token)
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

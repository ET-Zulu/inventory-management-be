from __future__ import annotations

from typing import List
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.model.enums import UserRole


class UserRead(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True


class UserListItem(UserRead):
    pass


class UserListResponse(BaseModel):
    total_users: int
    active_now: int
    pending_invites: int
    data: List[UserListItem]

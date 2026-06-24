from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from app.model.enums import UserRole

class UserLoginResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: UserRole

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserLoginResponse

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

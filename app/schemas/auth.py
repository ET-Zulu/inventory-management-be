from datetime import datetime
import re
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.model.enums import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class InviteCreateRequest(BaseModel):
    email: EmailStr
    role: UserRole = Field(default=UserRole.OPERATOR)


class InviteCreateResponse(BaseModel):
    invite_token: str
    expires_at: datetime


class SetupPasswordRequest(BaseModel):
    token: str
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(
        min_length=8,
        description="Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character.",
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not re.fullmatch(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$",
            value,
        ):
            raise ValueError(
                "Password must include at least one uppercase letter, one lowercase letter, one number, and one special character."
            )
        return value

class AdminSetupRequest(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(
        min_length=8,
        description="Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character.",
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not re.fullmatch(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$",
            value,
        ):
            raise ValueError(
                "Password must include at least one uppercase letter, one lowercase letter, one number, and one special character."
            )
        return value

  


class SetupPasswordResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

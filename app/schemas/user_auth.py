import uuid
from datetime import datetime
from pydantic import BaseModel
from app.model.enums import UserRole

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: UserRole = UserRole.VIEWER

class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

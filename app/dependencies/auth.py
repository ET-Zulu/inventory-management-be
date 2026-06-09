from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.model.enums import UserRole
from app.model.user import User
from app.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_prefix}/auth/login/access-token"
)


def get_current_user(
    db: Session = Depends(get_session), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    if not token_data.sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    user = db.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def _require_roles(current_user: User, allowed_roles: set[UserRole]) -> User:
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user


def require_roles(*allowed_roles: UserRole):
    def role_dependency(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        return _require_roles(current_user, set(allowed_roles))

    return role_dependency


def get_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    return _require_roles(current_user, {UserRole.ADMIN})


def get_operator(
    current_user: User = Depends(get_current_active_user),
) -> User:
    return _require_roles(current_user, {UserRole.ADMIN, UserRole.OPERATOR})

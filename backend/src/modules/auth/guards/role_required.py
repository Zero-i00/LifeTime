from fastapi import (
    status,
    Depends,
    HTTPException
)

from database.models.user import UserRole
from modules.auth.service import auth_service
from modules.auth.schema import AccessTokenPayload


def role_required(required_roles: list[UserRole]):
    def check(user: AccessTokenPayload = Depends(auth_service.get_access_token_payload)):
        if user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )
        return user
    return check

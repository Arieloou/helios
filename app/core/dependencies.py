# core/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from datetime import datetime

from app.core.clients import RedisClient, redis_db
from app.core.security import decode_access_token

from app.core.schemas import CurrentUser, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciales inválidas",
    headers={"WWW-Authenticate": "Bearer"},
)

revoked_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token revocado",
    headers={"WWW-Authenticate": "Bearer"},
)

session_invalidated_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Sesión invalidada, inicia sesión nuevamente",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_redis_client() -> RedisClient:
    return redis_db

async def get_current_user(token: str = Depends(oauth2_scheme), redis_client: RedisClient = Depends(get_redis_client)) -> CurrentUser:
    try:
        # Get token payload from header
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        issued_at: datetime = payload.get("iat")

        # Validates that the redis client (db) has not revoked the token
        if await redis_client.is_token_blocked(token):
            raise revoked_exception

        # Validates that the token is still valid
        if await redis_client.is_issued_before_invalidation(user_id, issued_at):
            raise session_invalidated_exception

        if user_id is None:
            raise credentials_exception
            
        # Return the current user
        return CurrentUser(
            id=user_id,
            username=payload.get("username", ""),
            email=payload.get("email", ""),
            role=payload.get("role", ""),
        )
    except ValueError:
        raise credentials_exception

def require_role(*allowed_roles: UserRole):
    def role_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción"
            )
        return current_user

    return role_checker
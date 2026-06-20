# features/auth/exception_handlers.py

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.features.auth.exceptions import (
    AuthError,
    ExpiredRefreshTokenError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    RefreshTokenReuseDetectedError,
    UserAlreadyExistsError,
    UserNotFoundError,
    NoActiveUserError,
)

_ERROR_STATUS_MAP = {
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    InvalidRefreshTokenError: status.HTTP_401_UNAUTHORIZED,
    ExpiredRefreshTokenError: status.HTTP_401_UNAUTHORIZED,
    RefreshTokenReuseDetectedError: status.HTTP_401_UNAUTHORIZED,
    UserAlreadyExistsError: status.HTTP_409_CONFLICT,
    UserNotFoundError: status.HTTP_404_NOT_FOUND,
    NoActiveUserError: status.HTTP_423_LOCKED,
}

async def auth_error_handler(request: Request, exc: AuthError) -> JSONResponse:
    status_code = _ERROR_STATUS_MAP.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return JSONResponse(status_code=status_code, content={"detail": str(exc) or exc.__class__.__name__})
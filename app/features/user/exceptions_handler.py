# features/user/exception_handlers.py

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.features.user.exceptions import (
    AuthError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

_ERROR_STATUS_MAP = {
    AuthError: status.HTTP_400_BAD_REQUEST,
    UserAlreadyExistsError: status.HTTP_409_CONFLICT,
    UserNotFoundError: status.HTTP_404_NOT_FOUND,
}

async def user_error_handler(request: Request, exc: AuthError) -> JSONResponse:
    status_code = _ERROR_STATUS_MAP.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return JSONResponse(status_code=status_code, content={"detail": str(exc) or exc.__class__.__name__})
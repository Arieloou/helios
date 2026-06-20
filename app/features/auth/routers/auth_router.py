# features/auth/routers/auth_router.py

from datetime import datetime
from helios.app.features.auth.services.auth_service import AuthService
from flask import request
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status

# Dependency of core feature
from app.core.dependencies import get_current_user

# Dependencies of user feature
from app.features.user.services.user_service import UserService

# Dependency of auth feature
from ..services import SessionTokenService
from ..dependencies import get_auth_service, get_session_token_service
from ..schemas import LoginRequest, AuthMessageResponse
from ..exceptions import *

router = APIRouter()

ACCESS_TOKEN_MAX_AGE = 15 * 60  # 15 minutos en segundos
REFRESH_TOKEN_MAX_AGE = 7 * 24 * 60 * 60  # 7 días en segundos

def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Centraliza las flags de cookies para no repetirlas en cada endpoint."""
    response.set_cookie(
        "access_token", access_token,
        httponly=True, secure=True, samesite="lax", max_age=ACCESS_TOKEN_MAX_AGE,
    )
    response.set_cookie(
        "refresh_token", refresh_token,
        httponly=True, secure=True, samesite="strict", max_age=REFRESH_TOKEN_MAX_AGE,
    )

def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


@router.post("/login", response_model=AuthMessageResponse)
async def login(
    credentials: LoginRequest, 
    response: Response, 
    auth_service: AuthService
):
    access_token, refresh_token = await auth_service.authenticate(credentials.email, credentials.password)

    _set_auth_cookies(response, access_token, refresh_token)

    return AuthMessageResponse(message="login exitoso")

@router.post("/logout", response_model=AuthMessageResponse)
async def logout(
    response: Response,
    current_user = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    access_token = request.cookies.get("access_token")
    raw_refresh_token = request.cookies.get("refresh_token")
    
    await auth_service.logout(access_token, raw_refresh_token, current_user.id)

    _clear_auth_cookies(response)
    
    return AuthMessageResponse(message="logout exitoso")

@router.post("/refresh", response_model=AuthMessageResponse)
async def refresh(
    request: Request, 
    response: Response, 
    current_user = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    raw_token = request.cookies.get("refresh_token")
    if not raw_token:
        raise InvalidRefreshTokenError("No refresh token provided")

    access_token, refresh_token = await auth_service.rotate_access_and_refresh_tokens(raw_token, current_user.id)

    _set_auth_cookies(response, access_token, refresh_token)

    return AuthMessageResponse(message="token renovado")
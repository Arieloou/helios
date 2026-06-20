# features/auth/dependencies.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db 

from .repositories import RefreshTokenRepository
from .services import SessionTokenService, AuthService

def get_session_token_service(db: AsyncSession = Depends(get_db)) -> SessionTokenService:
    """
    FastAPI inyectará 'db' automáticamente.
    Nosotros la usamos para crear el Repositorio, y luego el Servicio.
    """
    repository = RefreshTokenRepository(db)
    return SessionTokenService(session=db, refresh_token_repository=repository)

def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """
    FastAPI inyectará 'db' automáticamente.
    Nosotros la usamos para crear el Repositorio, y luego el Servicio.
    """
    repository = RefreshTokenRepository(db)
    return AuthService(refresh_token_repository=repository)
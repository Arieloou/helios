# features/auth/dependencies.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db 

from .repositories import UserRepository, RefreshTokenRepository
from .services import UserService, SessionTokenService

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """
    FastAPI inyectará 'db' automáticamente.
    Nosotros la usamos para crear el Repositorio, y luego el Servicio.
    """
    repository = UserRepository(db)
    return UserService(user_repository=repository)
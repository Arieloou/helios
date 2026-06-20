# features/auth/services/session_token_service.py

from app.core.security import ALGORITHM
from sqlalchemy.ext.asyncio import AsyncSession

from jose import jwt
from datetime import datetime, timedelta
import secrets

from app.core.config import settings
from app.core.security import hash_token

from ..models import RefreshToken
from ..repositories import RefreshTokenRepository
from ..exceptions import (
    InvalidRefreshTokenError,
    ExpiredRefreshTokenError,
    RefreshTokenReuseDetectedError
)

REFRESH_TOKEN_EXPIRE_DAYS = 7
ACCESS_TOKEN_EXPIRE_MINUTES = 15
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

class SessionTokenService:

    # Dependency Injection, only in this case we use AsyncSession because 
    # the service is the one that commits all the operations    
    def __init__(self, session: AsyncSession, refresh_token_repository: RefreshTokenRepository):
        self.session = session
        self.refresh_token_repository = refresh_token_repository

    def create_access_token(self, user_id: str) -> str:
        """
        Creates a new access token for a specific user.
        """
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "type": "access",
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    async def create_refresh_token(self, user_id: str) -> str:
        raw_token = secrets.token_urlsafe(64)  # no necesita ser JWT, puede ser un valor random
        
        db_token = RefreshToken(
            user_id=user_id,
            token_hash=hash_token(raw_token),
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )

        await self.refresh_token_repository.save(db_token)
        await self.session.commit()

        return raw_token  # este es el que se envía al cliente, el hash queda en BD

    async def rotate_refresh_token(self, old_token: str) -> str:
        old_token_hash = hash_token(old_token)
        refresh_token_db = await self.refresh_token_repository.get_by_token_hash(old_token_hash)

        if refresh_token_db is None:
            raise InvalidRefreshTokenError()
        
        # If the token was revoked, revoke all tokens of the user and raise error
        if refresh_token_db.revoked:
            await self.revoke_all_by_user_id(refresh_token_db.user_id)
            raise RefreshTokenReuseDetectedError()
        
        if refresh_token_db.expires_at < datetime.utcnow():
            raise ExpiredRefreshTokenError()

        # Revoke only the old token
        await self.revoke_refresh_token_by_hash(old_token_hash)

        # Creates a new refresh token
        new_raw_token = await self.create_refresh_token(refresh_token_db.user_id)

        await self.session.commit()

        # Return the user id and the new refresh token,
        # so the auth_service can create a new access token
        return new_raw_token

    # Obtiene el token desde la cabecera (raw_token) y lo revoca
    # Lo usa el endpoint /logout para cerrar sesión
    async def revoke_refresh_token_by_hash(self, token_hash: str) -> None:
        await self.refresh_token_repository.revoke_one_by_token_hash(token_hash)
        await self.session.commit()

    # Revoca todos los tokens de un usuario
    # Lo usa el endpoint /logout cuando se detecta reutilización
    async def revoke_all_by_user_id(self, user_id: str) -> int:
        count = await self.refresh_token_repository.revoke_all_by_user_id(user_id)
        await self.session.commit()
        return count
# features/auth/services/auth_service.py

from time import time
from app.core.security import verify_password, decode_access_token
from app.core.decorators.audit_decorator import audit

from app.core.clients import RedisClient

from app.features.user.exceptions import UserNotFoundError
from app.features.user.services import UserService

from ..services import SessionTokenService

class AuthService:
    def __init__(self, user_service: UserService, session_token_service: SessionTokenService, redis_client: RedisClient):
        self.user_service = user_service
        self.session_token_service = session_token_service
        self.redis_client = redis_client

    def _get_token_ttl_seconds (self, access_token: str) -> int:
        payload = decode_access_token(access_token)
        exp = payload["exp"]
        remaining = exp - int(time.time())
        return max(remaining, 0)

    async def rotate_access_and_refresh_tokens(self, old_token: str, current_user_id: str) -> tuple[str, str]:
        """
        Rotates the refresh token by creating a new one.
        """
        new_refresh_token = await self.session_token_service.rotate_refresh_token(old_token)
        new_access_token = self.session_token_service.create_access_token(current_user_id)
        return new_access_token, new_refresh_token

    @audit("authenticate")
    async def authenticate(self, email: str, password: str):
        """
        Authenticates a user by checking their credentials.
        """
        user = await self.user_service.get_user_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise UserNotFoundError("Usuario o contraseña incorrectos")
        return user
    
    @audit("logout")
    async def logout(self, current_access_token: str, current_refresh_token: str, user_id: str) -> None:
        """
        Revokes all active refresh tokens for a specific user.
        """
        await self.session_token_service.revoke_refresh_token_by_hash(current_refresh_token)
        await self.redis_client.add_to_blocklist(user_id, self._get_token_ttl_seconds(current_access_token))
        return 

    @audit("revoke_all_user_sessions")
    async def revoke_all_user_sessions(self, user_id: str) -> None:
        """
        Revokes all active refresh tokens for a specific user.
        """
        await self.session_token_service.revoke_all_for_user(user_id)
        await self.redis_client.invalidate_tokens_for_user(user_id)
        return
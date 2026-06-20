# features/auth/repositories/refresh_token_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional, List

from datetime import datetime

from ..models import RefreshToken

class RefreshTokenRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def revoke_one_by_token_hash(self, token_hash: str) -> int:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash, RefreshToken.revoked == False)
            .values(revoked=True, expires_at=datetime.utcnow())
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    async def revoke_all_by_user_id(self, user_id: str) -> int:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked == False)
            .values(revoked=True, expires_at=datetime.utcnow())
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    async def save(self, refresh_token: RefreshToken) -> RefreshToken:
        self.session.add(refresh_token)
        await self.session.flush() # asigna el ID sin cerrar la transacción
        return refresh_token

    async def get_by_token_hash(self, token_hash: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_user_id(self, user_id: str) -> List[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_active_refresh_tokens(self) -> List[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.expires_at > datetime.utcnow())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_expired(self) -> int:
        stmt = delete(RefreshToken).where(RefreshToken.expires_at < datetime.utcnow())
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount
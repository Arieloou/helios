# features/user/repositories/user_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from app.features.auth.models import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_name(self, name: str) -> Optional[User]:
        stmt = select(User).where(User.name == name)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_user_by_id(self, id: str) -> Optional[User]:
        stmt = select(User).where(User.id == id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all_users(self) -> List[User]:
        stmt = select(User)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_users(self) -> List[User]:
        stmt = select(User).where(User.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_inactive_users(self) -> List[User]:
        stmt = select(User).where(User.is_active == False)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def save(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> User:
        await self.session.delete(user)
        await self.session.commit()
        return user

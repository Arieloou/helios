from datetime import datetime, timezone
from ..repositories import UserRepository
from ..schemas import UserRole, UserCreate
from ..models import User


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, user: UserCreate, current_user_id: str):
        if await self.repository.get_by_name(user.username):
            raise ValueError("El usuario ya existe")
                
        user = User(
            name=user.name,
            email=user.email,
            password_hash=user.password,
            role=user.role,
        )
        return await self.repository.save(user)


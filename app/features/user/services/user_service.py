# features/user/services/user_service.py

from ..repositories import UserRepository
from ..schemas import UserCreate, UserUpdate
from ..models import User
from ..exceptions import EmailAlreadyExistsError, UserAlreadyExistsError, UserNotFoundError

from app.core.decorators.audit_decorator import audit
from app.core.security import hash_password

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    @audit("create_user")
    async def create_user(self, user: UserCreate):
        
        if await self.user_repository.get_by_email(user.email):
            raise EmailAlreadyExistsError()
                
        if await self.user_repository.get_by_name(user.username):
            raise UserAlreadyExistsError()

        user = User(
            name=user.name,
            email=user.email,
            password_hash=hash_password(user.password),
            role=user.role,
        )

        return await self.user_repository.save(user)
    
    # It only update decriptive data, like name, email, password and role
    @audit("update_user")
    async def update_user(self, user: UserUpdate):
        db_user = await self.user_repository.get_by_id(user.id)
        if not db_user:
            raise UserNotFoundError()

        update_data = user.model_dump(exclude_unset=True)

        if "email" in update_data:
            if await self.user_repository.get_by_email(update_data["email"]):
                raise EmailAlreadyExistsError()
        
        if "username" in update_data:
            if await self.user_repository.get_by_name(update_data["username"]):
                raise UserAlreadyExistsError()

        if "password" in update_data:
            update_data["password_hash"] = hash_password(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)

        return await self.user_repository.save(db_user)

    # It only update the status of the user
    @audit("inactive_user")
    async def inactive_user(self, user_id: str):
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        user.is_active = False

        return await self.user_repository.save(user)
    
    async def get_all_users(self):
        return await self.user_repository.get_all()
    
    async def get_user_by_id(self, user_id: str):
        return await self.user_repository.get_by_id(user_id)
    
    async def get_user_by_email(self, email: str):
        return await self.user_repository.get_by_email(email)
    
    async def get_user_by_name(self, name: str):
        return await self.user_repository.get_by_name(name)
    
    async def get_all_active_users(self):
        return await self.user_repository.get_active()
    
    async def get_all_inactive_users(self):
        return await self.user_repository.get_inactive()

from datetime import datetime
from typing import Dict, List, Optional
import uuid


class UserRole:
    ADMIN = "admin"
    AGENT = "agent"


class User:
    _instances: Dict[str, "User"] = {}

    def __init__(
        self,
        id: Optional[str] = None,
        username: str = "",
        email: Optional[str] = None,
        password_hash: str = "",
        role: str = UserRole.AGENT,
        is_active: bool = True,
        failed_attempts: int = 0,
        locked_until: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active
        self.failed_attempts = failed_attempts
        self.locked_until = locked_until
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at
        self._instances[self.id] = self

    def to_dict(self, include_sensitive: bool = False) -> Dict:
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "failed_attempts": self.failed_attempts,
            "locked_until": self.locked_until.isoformat() if self.locked_until else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        return data

    def is_locked(self) -> bool:
        if self.locked_until and self.locked_until > datetime.now():
            return True
        return False

    def increment_failed_attempts(self) -> None:
        self.failed_attempts += 1
        if self.failed_attempts >= 5:
            from datetime import timedelta
            self.locked_until = datetime.now() + timedelta(minutes=15)
        self.updated_at = datetime.now()

    def reset_failed_attempts(self) -> None:
        self.failed_attempts = 0
        self.locked_until = None
        self.updated_at = datetime.now()

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now()

    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.now()

    @classmethod
    def get_by_id(cls, id: str) -> Optional["User"]:
        return cls._instances.get(id)

    @classmethod
    def get_by_username(cls, username: str) -> Optional["User"]:
        for user in cls._instances.values():
            if user.username == username:
                return user
        return None

    @classmethod
    def get_by_email(cls, email: str) -> Optional["User"]:
        for user in cls._instances.values():
            if user.email == email:
                return user
        return None

    @classmethod
    def get_all(cls) -> List["User"]:
        return list(cls._instances.values())

    @classmethod
    def get_active_users(cls) -> List["User"]:
        return [u for u in cls._instances.values() if u.is_active]

    @classmethod
    def create(
        cls,
        username: str,
        password_hash: str,
        email: Optional[str] = None,
        role: str = UserRole.AGENT,
    ) -> "User":
        if cls.get_by_username(username):
            raise ValueError(f"Ya existe un usuario con el nombre '{username}'")

        if email and cls.get_by_email(email):
            raise ValueError(f"Ya existe un usuario con el email '{email}'")

        return cls(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
        )

    @classmethod
    def create_admin_user(cls, username: str, password_hash: str, email: Optional[str] = None) -> "User":
        return cls.create(username, password_hash, email, UserRole.ADMIN)

    def delete(self) -> None:
        if self.id in self._instances:
            del self._instances[self.id]
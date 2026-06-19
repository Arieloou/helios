"""
User model for authentication and authorization.
Stores user credentials with encrypted sensitive fields (username, email, password_hash).
Uses username_hash (SHA-256) for deterministic lookups since AES-GCM is non-deterministic.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

from .base import db, TimestampMixin


class UserRole:
    """Constants for user roles."""
    ADMIN = "admin"
    AGENT = "agent"


class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    # Encrypted fields: middleware will auto-encrypt/decrypt these
    __encrypted_fields__ = ["username", "email", "password_hash"]

    # Hash fields: maps source field -> hash column for deterministic lookups
    __hash_fields__ = {"username": "username_hash"}

    # Columns
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.Text, nullable=False)
    username_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.Text, nullable=True)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), default=UserRole.AGENT, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    failed_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)

    # Max failed login attempts and lockout duration
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15

    _instances: Dict[str, "User"] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id:
            self._instances[self.id] = self

    def to_dict(self, include_sensitive: bool = False) -> Dict:
        """Convert user to dictionary. Excludes password by default."""
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
        if include_sensitive:
            data["password_hash"] = self.password_hash
        return data

    def is_locked(self) -> bool:
        """Check if account is locked due to failed attempts."""
        if self.locked_until and self.locked_until > datetime.now():
            return True
        # Auto-unlock if lockout period has passed
        if self.locked_until and self.locked_until <= datetime.now():
            self.locked_until = None
            self.failed_attempts = 0
        return False

    def increment_failed_attempts(self) -> None:
        """Increment failed attempts counter, lock account after 5 failures."""
        self.failed_attempts += 1
        if self.failed_attempts >= self.MAX_FAILED_ATTEMPTS:
            self.locked_until = datetime.now() + timedelta(minutes=self.LOCKOUT_MINUTES)
        self.updated_at = datetime.now()
        db.session.commit()

    def reset_failed_attempts(self) -> None:
        """Reset failed attempts and unlock the account."""
        self.failed_attempts = 0
        self.locked_until = None
        self.updated_at = datetime.now()
        db.session.commit()

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
        self.updated_at = datetime.now()
        db.session.commit()

    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
        self.updated_at = datetime.now()
        db.session.commit()

    @classmethod
    def get_by_id(cls, user_id: str) -> Optional["User"]:
        """Find user by primary key."""
        return cls.query.get(user_id)

    @classmethod
    def get_by_username_hash(cls, username: str) -> Optional["User"]:
        """Find user by username using deterministic hash lookup."""
        from app.services.encryption_middleware import compute_lookup_hash
        hashed = compute_lookup_hash(username)
        return cls.query.filter_by(username_hash=hashed).first()

    @classmethod
    def get_by_username(cls, username: str) -> Optional["User"]:
        """Find user by username (alias for hash-based lookup)."""
        return cls.get_by_username_hash(username)

    @classmethod
    def get_by_email(cls, email: str) -> Optional["User"]:
        """Find user by email. Loads all users and filters in-memory after decryption."""
        users = cls.query.all()
        for user in users:
            if user.email and user.email == email:
                return user
        return None

    @classmethod
    def get_all(cls) -> List["User"]:
        """Get all users."""
        return cls.query.all()

    @classmethod
    def get_active_users(cls) -> List["User"]:
        """Get all active users."""
        return cls.query.filter_by(is_active=True).all()

    @classmethod
    def create(
        cls,
        username: str,
        password_hash: str,
        email: Optional[str] = None,
        role: str = UserRole.AGENT,
    ) -> "User":
        """Create a new user. Checks for duplicate username."""
        if cls.get_by_username(username):
            raise ValueError(f"Ya existe un usuario con el nombre '{username}'")

        if email and cls.get_by_email(email):
            raise ValueError(f"Ya existe un usuario con el email '{email}'")

        # Compute username_hash for lookup before encryption middleware runs
        from app.services.encryption_middleware import compute_lookup_hash
        user = cls(
            username=username,
            username_hash=compute_lookup_hash(username),
            email=email,
            password_hash=password_hash,
            role=role,
        )
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def create_admin_user(
        cls, username: str, password_hash: str, email: Optional[str] = None
    ) -> "User":
        """Shortcut to create an admin user."""
        return cls.create(username, password_hash, email, UserRole.ADMIN)

    def delete(self) -> None:
        """Delete the user from the database."""
        if self.id in self._instances:
            del self._instances[self.id]
        db.session.delete(self)
        db.session.commit()
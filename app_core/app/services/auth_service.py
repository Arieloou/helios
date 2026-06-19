"""
Authentication Service.
Handles user authentication, registration, and account management.
Password flow: plaintext -> SHA-256 hash -> stored (encryption middleware handles DB encryption).
"""

from datetime import datetime
from typing import Dict, List, Optional
import hashlib

from app.models.user import User, UserRole


class AuthService:
    """Service layer for authentication and user management operations."""

    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a password using SHA-256 before storage."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @classmethod
    def verify_password(cls, password: str, stored_hash: str) -> bool:
        """Compare input password hash against stored hash."""
        return cls.hash_password(password) == stored_hash

    @classmethod
    def authenticate(cls, username: str, password: str) -> Dict:
        """
        Authenticate a user by username and password.
        Returns dict with success status, user data, and error messages.
        Handles account locking after 5 failed attempts.
        """
        # Lookup user by deterministic username hash
        user = User.get_by_username(username)
        if not user:
            return {"success": False, "error": "Usuario o contraseña incorrectos"}

        # Check if account is deactivated
        if not user.is_active:
            return {"success": False, "error": "Usuario desactivado. Contacte al administrador."}

        # Check if account is locked
        if user.is_locked():
            return {
                "success": False,
                "error": f"Usuario bloqueado. Intente en {cls.LOCKOUT_MINUTES} minutos.",
            }

        # Verify password (middleware already decrypted password_hash from DB)
        if cls.verify_password(password, user.password_hash):
            # Successful login: reset failed attempts
            user.reset_failed_attempts()
            return {
                "success": True,
                "user": user.to_dict(),
                "role": user.role,
            }
        else:
            # Failed login: increment counter
            user.increment_failed_attempts()
            remaining = cls.MAX_FAILED_ATTEMPTS - user.failed_attempts
            if remaining > 0:
                return {
                    "success": False,
                    "error": f"Usuario o contraseña incorrectos. Intentos restantes: {remaining}",
                }
            else:
                return {
                    "success": False,
                    "error": f"Usuario bloqueado por demasiados intentos fallidos. "
                             f"Intente en {cls.LOCKOUT_MINUTES} minutos.",
                }

    @classmethod
    def create_user(
        cls,
        username: str,
        password: str,
        email: Optional[str] = None,
        role: str = UserRole.AGENT,
    ) -> Dict:
        """Create a new user with hashed password."""
        password_hash = cls.hash_password(password)
        try:
            user = User.create(username, password_hash, email, role)
            return {"success": True, "user": user.to_dict()}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    @classmethod
    def update_user(
        cls,
        user_id: str,
        username: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
    ) -> Dict:
        """Update user profile fields (not password)."""
        user = User.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Usuario no encontrado"}

        if username and username != user.username:
            if User.get_by_username(username):
                return {"success": False, "error": "Ya existe un usuario con ese nombre"}
            user.username = username
            # Recompute username_hash for the new username
            from app.services.encryption_middleware import compute_lookup_hash
            user.username_hash = compute_lookup_hash(username)

        if email and email != user.email:
            if User.get_by_email(email):
                return {"success": False, "error": "Ya existe un usuario con ese email"}
            user.email = email

        if role:
            if role not in [UserRole.ADMIN, UserRole.AGENT]:
                return {"success": False, "error": "Rol inválido"}
            user.role = role

        user.updated_at = datetime.now()
        from app.models.base import db
        db.session.commit()
        return {"success": True, "user": user.to_dict()}

    @classmethod
    def change_password(cls, user_id: str, old_password: str, new_password: str) -> Dict:
        """Change a user's password after verifying the old one."""
        user = User.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Usuario no encontrado"}

        if not cls.verify_password(old_password, user.password_hash):
            return {"success": False, "error": "Contraseña actual incorrecta"}

        user.password_hash = cls.hash_password(new_password)
        user.updated_at = datetime.now()
        from app.models.base import db
        db.session.commit()
        return {"success": True, "message": "Contraseña actualizada exitosamente"}

    @classmethod
    def deactivate_user(cls, user_id: str) -> Dict:
        """Deactivate a user account."""
        user = User.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Usuario no encontrado"}
        user.deactivate()
        return {"success": True, "message": "Usuario desactivado"}

    @classmethod
    def activate_user(cls, user_id: str) -> Dict:
        """Activate a user account."""
        user = User.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Usuario no encontrado"}
        user.activate()
        return {"success": True, "message": "Usuario activado"}

    @classmethod
    def delete_user(cls, user_id: str) -> Dict:
        """Delete a user account."""
        user = User.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Usuario no encontrado"}
        user.delete()
        return {"success": True, "message": "Usuario eliminado"}

    @classmethod
    def list_users(cls) -> List[Dict]:
        """List all users (without sensitive data)."""
        return [u.to_dict() for u in User.get_all()]

    @classmethod
    def get_user(cls, user_id: str) -> Optional[Dict]:
        """Get a single user by ID."""
        user = User.get_by_id(user_id)
        return user.to_dict() if user else None

    @classmethod
    def is_admin(cls, role: str) -> bool:
        """Check if role is admin."""
        return role == UserRole.ADMIN

    @classmethod
    def is_agent(cls, role: str) -> bool:
        """Check if role is agent."""
        return role == UserRole.AGENT

    @classmethod
    def has_permission(cls, user_role: str, required_role: str) -> bool:
        """Check if user role meets the required role level."""
        role_hierarchy = {
            UserRole.ADMIN: 2,
            UserRole.AGENT: 1,
        }
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
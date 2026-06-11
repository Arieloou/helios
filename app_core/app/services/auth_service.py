from datetime import datetime
from typing import Dict, List, Optional
import hashlib

from app.models.user import User, UserRole


class AuthService:
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15

    @classmethod
    def hash_password(cls, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    @classmethod
    def verify_password(cls, password: str, password_hash: str) -> bool:
        return cls.hash_password(password) == password_hash

    @classmethod
    def authenticate(cls, username: str, password: str) -> Dict:
        user = User.get_by_username(username)
        if not user:
            return {"success": False, "error": "Usuario o contraseña incorrectos"}

        if not user.is_active:
            return {"success": False, "error": "Usuario desactivado. Contacte al administrador."}

        if user.is_locked():
            return {"success": False, "error": f"Usuario bloqueado. Intente en {cls.LOCKOUT_MINUTES} minutos."}

        if cls.verify_password(password, user.password_hash):
            user.reset_failed_attempts()
            return {
                "success": True,
                "user": user.to_dict(),
                "role": user.role,
            }
        else:
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
                    "error": f"Usuario bloqueado por demasiados intentos fallidos. Intente en {cls.LOCKOUT_MINUTES} minutos.",
                }

    @classmethod
    def create_user(
        cls,
        username: str,
        password: str,
        email: Optional[str] = None,
        role: str = UserRole.AGENT,
    ) -> Dict:
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
        user = User.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Usuario no encontrado"}

        if username and username != user.username:
            if User.get_by_username(username):
                return {"success": False, "error": "Ya existe un usuario con ese nombre"}
            user.username = username

        if email and email != user.email:
            if User.get_by_email(email):
                return {"success": False, "error": "Ya existe un usuario con ese email"}
            user.email = email

        if role:
            if role not in [UserRole.ADMIN, UserRole.AGENT]:
                return {"success": False, "error": "Rol inválido"}
            user.role = role

        user.updated_at = datetime.now()
        return {"success": True, "user": user.to_dict()}

    @classmethod
    def change_password(cls, user_id: str, old_password: str, new_password: str) -> Dict:
        user = User.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Usuario no encontrado"}

        if not cls.verify_password(old_password, user.password_hash):
            return {"success": False, "error": "Contraseña actual incorrecta"}

        user.password_hash = cls.hash_password(new_password)
        user.updated_at = datetime.now()
        return {"success": True, "message": "Contraseña actualizada exitosamente"}

    @classmethod
    def deactivate_user(cls, user_id: str) -> Dict:
        user = User.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Usuario no encontrado"}

        user.deactivate()
        return {"success": True, "message": "Usuario desactivado"}

    @classmethod
    def activate_user(cls, user_id: str) -> Dict:
        user = User.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Usuario no encontrado"}

        user.activate()
        return {"success": True, "message": "Usuario activado"}

    @classmethod
    def delete_user(cls, user_id: str) -> Dict:
        user = User.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Usuario no encontrado"}

        user.delete()
        return {"success": True, "message": "Usuario eliminado"}

    @classmethod
    def list_users(cls) -> List[Dict]:
        return [u.to_dict() for u in User.get_all()]

    @classmethod
    def get_user(cls, user_id: str) -> Optional[Dict]:
        user = User.get_by_id(user_id)
        return user.to_dict() if user else None

    @classmethod
    def is_admin(cls, role: str) -> bool:
        return role == UserRole.ADMIN

    @classmethod
    def is_agent(cls, role: str) -> bool:
        return role == UserRole.AGENT

    @classmethod
    def has_permission(cls, user_role: str, required_role: str) -> bool:
        role_hierarchy = {
            UserRole.ADMIN: 2,
            UserRole.AGENT: 1,
        }
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
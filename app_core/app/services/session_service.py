"""
Session Service (Single Responsibility Principle).
Centralizes all session-related user resolution logic.
Controllers depend on this service via flask.g instead of
parsing session dicts or calling the ORM directly.
"""

from typing import Optional

from flask import g, session

from app.models.user import User


class SessionService:
    """Resolves the authenticated user from the session into flask.g."""

    # Key used in flask.g to store the resolved user
    CURRENT_USER_KEY = "current_user"

    @classmethod
    def load_current_user(cls) -> None:
        """
        Before-request hook: resolve user_id from session cookie
        into a live User ORM instance stored in flask.g.
        The encryption middleware auto-decrypts fields on load,
        so g.current_user.username is always plaintext.
        """
        setattr(g, cls.CURRENT_USER_KEY, None)

        session_data = session.get("user")
        if not session_data:
            return

        user_id = session_data.get("user_id")
        if not user_id:
            return

        # Fetch from DB — triggers the 'load' event which decrypts fields
        user = User.get_by_id(user_id)
        if user and user.is_active:
            setattr(g, cls.CURRENT_USER_KEY, user)
        else:
            # User was deactivated or deleted — invalidate session
            session.clear()

    @classmethod
    def get_current_user(cls) -> Optional[User]:
        """Return the resolved user from flask.g (set by before_request)."""
        return getattr(g, cls.CURRENT_USER_KEY, None)

    @classmethod
    def get_username(cls) -> str:
        """Return decrypted username or a safe fallback."""
        user = cls.get_current_user()
        return user.username if user else "[desconocido]"

    @classmethod
    def get_role(cls) -> Optional[str]:
        """Return the role of the current user."""
        user = cls.get_current_user()
        return user.role if user else None

    @classmethod
    def is_authenticated(cls) -> bool:
        """Check if a valid user is loaded."""
        return cls.get_current_user() is not None

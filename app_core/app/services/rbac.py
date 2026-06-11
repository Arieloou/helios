from functools import wraps
from flask import session, flash, redirect, url_for, abort
from app.services.auth_service import AuthService
from app.models.user import UserRole


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            flash("Debe iniciar sesión para acceder a esta página.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = session.get("user")
            if not user:
                flash("Debe iniciar sesión para acceder a esta página.", "error")
                return redirect(url_for("auth.login"))

            user_role = user.get("role")
            if user_role not in allowed_roles:
                flash("No tiene permisos para acceder a esta página.", "error")
                return redirect(url_for("auth.dashboard"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get("user")
        if not user:
            flash("Debe iniciar sesión para acceder a esta página.", "error")
            return redirect(url_for("auth.login"))

        if user.get("role") != UserRole.ADMIN:
            flash("Esta acción requiere permisos de administrador.", "error")
            return redirect(url_for("auth.dashboard"))

        return f(*args, **kwargs)
    return decorated_function


def check_permission(resource_owner_id: str = None) -> bool:
    user = session.get("user")
    if not user:
        return False

    if user.get("role") == UserRole.ADMIN:
        return True

    if resource_owner_id and user.get("user_id") == resource_owner_id:
        return True

    return False
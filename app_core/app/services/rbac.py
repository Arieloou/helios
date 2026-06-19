from functools import wraps
from flask import flash, redirect, url_for, abort
from app.services.session_service import SessionService
from app.models.user import UserRole


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not SessionService.is_authenticated():
            flash("Debe iniciar sesión para acceder a esta página.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not SessionService.is_authenticated():
                flash("Debe iniciar sesión para acceder a esta página.", "error")
                return redirect(url_for("auth.login"))

            user_role = SessionService.get_role()
            if user_role not in allowed_roles:
                flash("No tiene permisos para acceder a esta página.", "error")
                return redirect(url_for("auth.dashboard"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not SessionService.is_authenticated():
            flash("Debe iniciar sesión para acceder a esta página.", "error")
            return redirect(url_for("auth.login"))

        if SessionService.get_role() != UserRole.ADMIN:
            flash("Esta acción requiere permisos de administrador.", "error")
            return redirect(url_for("auth.dashboard"))

        return f(*args, **kwargs)
    return decorated_function


def check_permission(resource_owner_id: str = None) -> bool:
    user = SessionService.get_current_user()
    if not user:
        return False

    if user.role == UserRole.ADMIN:
        return True

    if resource_owner_id and user.id == resource_owner_id:
        return True

    return False
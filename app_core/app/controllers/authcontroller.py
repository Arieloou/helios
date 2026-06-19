"""
Authentication Controller.
Handles login, logout, and session management.
Uses AuthService for credential validation and SessionService for user resolution.
"""

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash,
)

from app.services.auth_service import AuthService
from app.services.session_service import SessionService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle login form display and submission."""
    # Redirect if already logged in
    if SessionService.is_authenticated():
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Validate required fields
        if not username or not password:
            flash("Usuario y contraseña son requeridos.", "error")
            return render_template("auth/login.html")

        try:
            # Authenticate via service layer
            result = AuthService.authenticate(username, password)

            if result["success"]:
                # Store only the user_id and role in the session cookie
                # The username is NOT stored — it will be resolved fresh
                # from the DB on each request by SessionService
                session["user"] = {
                    "user_id": result["user"]["id"],
                    "role": result["role"],
                }
                flash("Inicio de sesión exitoso.", "success")
                return redirect(url_for("auth.dashboard"))
            else:
                flash(result["error"], "error")
                return render_template("auth/login.html")

        except ConnectionError as e:
            flash(f"Servicio de cifrado no disponible: {e}", "error")
            return render_template("auth/login.html")
        except Exception as e:
            flash(f"Error inesperado: {e}", "error")
            return render_template("auth/login.html")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    """Clear session and redirect to login."""
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/dashboard")
def dashboard():
    """Display the main dashboard after login."""
    # SessionService resolves user from DB via before_request hook
    user = SessionService.get_current_user()
    if not user:
        return redirect(url_for("auth.login"))

    return render_template(
        "dashboard.html",
        username=user.username,
        role=user.role,
    )

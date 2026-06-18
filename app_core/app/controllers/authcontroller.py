"""
Authentication Controller.
Handles login, logout, and session management.
Uses AuthService for credential validation and session for state.
"""

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash,
)

from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle login form display and submission."""
    # Redirect if already logged in
    if session.get("user"):
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
                # Store user data in session
                session["user"] = {
                    "user_id": result["user"]["id"],
                    "username": result["user"]["username"],
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
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    return render_template(
        "dashboard.html",
        username=user.get("username", "[desconocido]"),
        role=user.get("role"),
    )

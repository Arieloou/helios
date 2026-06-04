"""
Controlador de autenticación.
Gestiona login, logout y control de acceso por roles.
Utiliza el cliente gRPC para cifrar datos sensibles.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if not username or not password:
            flash("Usuario y contraseña son requeridos.", "error")
            return render_template("auth/login.html")

        try:
            encryption = current_app.extensions["encryption"]
            encrypted_username = encryption.encrypt(username)
            encrypted_password = encryption.encrypt(password)

            session["user"] = {
                "username_encrypted": encrypted_username,
                "password_encrypted": encrypted_password,
                "role": "Agent",
            }

            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for("auth.dashboard"))

        except ConnectionError as e:
            flash(f"Servicio de cifrado no disponible: {e}", "error")
            return render_template("auth/login.html")
        except Exception as e:
            flash(f"Error inesperado: {e}", "error")
            return render_template("auth/login.html")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    try:
        encryption = current_app.extensions["encryption"]
        decrypted_username = encryption.decrypt(user["username_encrypted"])
    except Exception:
        decrypted_username = "[cifrado]"

    return render_template("dashboard.html", username=decrypted_username, role=user.get("role"))

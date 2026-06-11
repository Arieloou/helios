from flask import Blueprint, flash, redirect, render_template, request, url_for, session

from app.services.auth_service import AuthService
from app.services.rbac import admin_required
from app.models.user import UserRole


user_bp = Blueprint("user", __name__, url_prefix="/users")


def _get_current_user():
    user = session.get("user")
    return user


@user_bp.route("/")
@admin_required
def index():
    users = AuthService.list_users()
    current_user = _get_current_user()
    return render_template(
        "users/index.html",
        users=users,
        current_user=current_user,
    )


@user_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create():
    current_user = _get_current_user()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", UserRole.AGENT)

        if not username or not password:
            flash("Usuario y contraseña son requeridos.", "error")
            return render_template("users/create.html", current_user=current_user)

        result = AuthService.create_user(
            username=username,
            password=password,
            email=email if email else None,
            role=role,
        )

        if result["success"]:
            flash(f"Usuario '{username}' creado exitosamente.", "success")
            return redirect(url_for("user.index"))
        else:
            flash(result["error"], "error")

    return render_template("users/create.html", current_user=current_user)


@user_bp.route("/<user_id>/edit", methods=["GET", "POST"])
@admin_required
def edit(user_id: str):
    current_user = _get_current_user()
    user = AuthService.get_user(user_id)

    if not user:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("user.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        role = request.form.get("role", "").strip()

        result = AuthService.update_user(
            user_id=user_id,
            username=username if username else None,
            email=email if email else None,
            role=role if role else None,
        )

        if result["success"]:
            flash("Usuario actualizado exitosamente.", "success")
            return redirect(url_for("user.index"))
        else:
            flash(result["error"], "error")

    return render_template(
        "users/edit.html",
        user=user,
        current_user=current_user,
    )


@user_bp.route("/<user_id>/deactivate")
@admin_required
def deactivate(user_id: str):
    current_user_data = session.get("user", {})
    if current_user_data.get("user_id") == user_id:
        flash("No puede desactivarse a sí mismo.", "error")
        return redirect(url_for("user.index"))

    result = AuthService.deactivate_user(user_id)
    if result["success"]:
        flash(result["message"], "success")
    else:
        flash(result["error"], "error")

    return redirect(url_for("user.index"))


@user_bp.route("/<user_id>/activate")
@admin_required
def activate(user_id: str):
    result = AuthService.activate_user(user_id)
    if result["success"]:
        flash(result["message"], "success")
    else:
        flash(result["error"], "error")

    return redirect(url_for("user.index"))


@user_bp.route("/<user_id>/delete")
@admin_required
def delete(user_id: str):
    current_user_data = session.get("user", {})
    if current_user_data.get("user_id") == user_id:
        flash("No puede eliminarse a sí mismo.", "error")
        return redirect(url_for("user.index"))

    result = AuthService.delete_user(user_id)
    if result["success"]:
        flash(result["message"], "success")
    else:
        flash(result["error"], "error")

    return redirect(url_for("user.index"))


@user_bp.route("/<user_id>/change-password", methods=["GET", "POST"])
def change_password(user_id: str):
    current_user_data = session.get("user", {})
    if not current_user_data:
        flash("Debe iniciar sesión.", "error")
        return redirect(url_for("auth.login"))

    if current_user_data.get("role") != UserRole.ADMIN and current_user_data.get("user_id") != user_id:
        flash("No tiene permisos para cambiar esta contraseña.", "error")
        return redirect(url_for("auth.dashboard"))

    user = AuthService.get_user(user_id)
    if not user:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("user.index"))

    if request.method == "POST":
        old_password = request.form.get("old_password", "").strip()
        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not old_password or not new_password:
            flash("Todas las contraseñas son requeridas.", "error")
            return render_template("users/change_password.html", user=user)

        if new_password != confirm_password:
            flash("Las contraseñas no coinciden.", "error")
            return render_template("users/change_password.html", user=user)

        if len(new_password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "error")
            return render_template("users/change_password.html", user=user)

        result = AuthService.change_password(user_id, old_password, new_password)
        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("auth.dashboard"))
        else:
            flash(result["error"], "error")

    return render_template("users/change_password.html", user=user)
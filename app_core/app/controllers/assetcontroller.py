"""
Controlador de activos de información.
Gestiona el CRUD de activos, utilizando el servicio de cifrado
para proteger datos sensibles de los activos.
"""

from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash

asset_bp = Blueprint("assets", __name__, url_prefix="/assets")

_assets_store: list[dict] = []


@asset_bp.route("/")
def index():
    decrypted_assets = []
    encryption = current_app.extensions["encryption"]

    for asset in _assets_store:
        try:
            name = encryption.decrypt(asset["name_encrypted"])
            description = encryption.decrypt(asset["description_encrypted"])
        except Exception:
            name = "[error descifrado]"
            description = "[error descifrado]"

        decrypted_assets.append({
            "id": asset["id"],
            "name": name,
            "description": description,
            "type": asset["type"],
        })

    return render_template("assets/index.html", assets=decrypted_assets)


@asset_bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        name = request.form.get("name", "")
        description = request.form.get("description", "")
        asset_type = request.form.get("type", "")

        if not name or not description:
            flash("Nombre y descripción son requeridos.", "error")
            return render_template("assets/create.html")

        try:
            encryption = current_app.extensions["encryption"]
            encrypted_name = encryption.encrypt(name)
            encrypted_description = encryption.encrypt(description)

            asset = {
                "id": len(_assets_store) + 1,
                "name_encrypted": encrypted_name,
                "description_encrypted": encrypted_description,
                "type": asset_type,
            }
            _assets_store.append(asset)

            flash("Activo creado exitosamente.", "success")
            return redirect(url_for("assets.index"))

        except ConnectionError as e:
            flash(f"Servicio de cifrado no disponible: {e}", "error")
            return render_template("assets/create.html")

    return render_template("assets/create.html")

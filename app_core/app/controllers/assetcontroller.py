from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask import session

from app.services.asset_service import AssetService
from app.services.assessment_service import AssessmentService
from app.services.import_service import ImportService
from app.services.rbac import login_required

asset_bp = Blueprint("assets", __name__, url_prefix="/assets")


def _get_active_assessment_id() -> str:
    active = AssessmentService.get_active()
    return active["id"] if active else None


@asset_bp.route("/")
def index():
    active_assessment = AssessmentService.get_active()
    assets = AssetService.list_all()

    if active_assessment:
        assets = [a for a in assets if a.get("assessment_id") == active_assessment["id"]]

    return render_template(
        "assets/index.html",
        assets=assets,
        active_assessment=active_assessment,
    )


@asset_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    active_assessment = AssessmentService.get_active()
    if not active_assessment:
        flash("Debe crear una evaluación antes de gestionar activos.", "warning")
        return redirect(url_for("assessments.create"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        asset_type = request.form.get("asset_type", "").strip()
        description = request.form.get("description", "").strip()
        confidentiality = int(request.form.get("confidentiality", 1))
        integrity = int(request.form.get("integrity", 1))
        availability = int(request.form.get("availability", 1))

        if not name:
            flash("El nombre del activo es requerido.", "error")
            return render_template("assets/create.html", active_assessment=active_assessment)

        if not asset_type:
            flash("El tipo de activo es requerido.", "error")
            return render_template("assets/create.html", active_assessment=active_assessment)

        assessment_id = _get_active_assessment_id()

        try:
            AssetService.create(
                name=name,
                asset_type=asset_type,
                description=description,
                confidentiality=confidentiality,
                integrity=integrity,
                availability=availability,
                assessment_id=assessment_id,
            )
            flash(f"Activo '{name}' creado exitosamente.", "success")
            return redirect(url_for("assets.index"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("assets/create.html", active_assessment=active_assessment)
        except Exception as e:
            flash(f"Error al crear el activo: {e}", "error")
            return render_template("assets/create.html", active_assessment=active_assessment)

    return render_template("assets/create.html", active_assessment=active_assessment)


@asset_bp.route("/<asset_id>/edit", methods=["GET", "POST"])
def edit(asset_id: str):
    asset = AssetService.get_by_id(asset_id)
    if not asset:
        flash("Activo no encontrado.", "error")
        return redirect(url_for("assets.index"))

    active_assessment = AssessmentService.get_active()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        asset_type = request.form.get("asset_type", "").strip()
        description = request.form.get("description", "").strip()
        confidentiality = int(request.form.get("confidentiality", 1))
        integrity = int(request.form.get("integrity", 1))
        availability = int(request.form.get("availability", 1))

        if not name:
            flash("El nombre del activo es requerido.", "error")
            return render_template("assets/edit.html", asset=asset, active_assessment=active_assessment)

        try:
            AssetService.update(
                asset_id=asset_id,
                name=name,
                asset_type=asset_type,
                description=description,
                confidentiality=confidentiality,
                integrity=integrity,
                availability=availability,
            )
            flash(f"Activo '{name}' actualizado exitosamente.", "success")
            return redirect(url_for("assets.index"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("assets/edit.html", asset=asset, active_assessment=active_assessment)
        except Exception as e:
            flash(f"Error al actualizar el activo: {e}", "error")
            return render_template("assets/edit.html", asset=asset, active_assessment=active_assessment)

    return render_template("assets/edit.html", asset=asset, active_assessment=active_assessment)


@asset_bp.route("/<asset_id>/delete")
def delete(asset_id: str):
    try:
        AssetService.delete(asset_id)
        flash("Activo eliminado exitosamente.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error al eliminar el activo: {e}", "error")

    return redirect(url_for("assets.index"))


@asset_bp.route("/import", methods=["GET", "POST"])
@login_required
def import_assets():
    active_assessment = AssessmentService.get_active()
    if not active_assessment:
        flash("Debe crear una evaluación antes de gestionar activos.", "warning")
        return redirect(url_for("assessments.create"))

    if request.method == "POST":
        if "file" not in request.files:
            flash("No se ha seleccionado ningún archivo.", "error")
            return render_template("assets/import.html", active_assessment=active_assessment)

        file = request.files["file"]
        if file.filename == "":
            flash("No se ha seleccionado ningún archivo.", "error")
            return render_template("assets/import.html", active_assessment=active_assessment)

        if not file.filename.endswith(".csv"):
            flash("El archivo debe ser de tipo CSV.", "error")
            return render_template("assets/import.html", active_assessment=active_assessment)

        try:
            csv_content = file.read().decode("utf-8")
            assessment_id = _get_active_assessment_id()
            result = ImportService.import_csv(csv_content, assessment_id)

            if result.errors and not result.imported:
                flash(f"Error al importar: {result.errors[0]['error']}", "error")
            elif result.imported:
                flash(f"Importados {result.imported_count} activos. {result.errors_count} errores.", "success")
            else:
                flash("No se importaron activos.", "info")

            return render_template(
                "assets/import.html",
                active_assessment=active_assessment,
                result=result.to_dict() if result.imported or result.errors else None,
            )
        except Exception as e:
            flash(f"Error al procesar el archivo: {e}", "error")
            return render_template("assets/import.html", active_assessment=active_assessment)

    return render_template("assets/import.html", active_assessment=active_assessment)


@asset_bp.route("/template")
def download_template():
    template = ImportService.get_csv_template()
    from flask import Response
    return Response(
        template,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=activos_template.csv"},
    )
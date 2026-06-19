from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services.assessment_service import AssessmentService
from app.services.session_service import SessionService
from app.services.asset_service import AssetService
from app.services.rbac import login_required, admin_required
from app.models.risk_models import AssetThreatMapping

assessment_bp = Blueprint("assessment", __name__, url_prefix="/assessments")


@assessment_bp.route("/")
@login_required
def index():
    assessments = AssessmentService.list_all()
    active_assessment = AssessmentService.get_active()
    return render_template(
        "assessments/index.html",
        assessments=assessments,
        active_assessment=active_assessment,
    )


@assessment_bp.route("/<assessment_id>")
@login_required
def detail(assessment_id: str):
    assessment = AssessmentService.get_by_id(assessment_id)
    if not assessment:
        flash("Evaluación no encontrada.", "error")
        return redirect(url_for("assessment.index"))

    assets = AssetService.list_by_assessment(assessment_id)
    risks = AssetThreatMapping.get_by_assessment(assessment_id)

    return render_template(
        "assessments/detail.html",
        assessment=assessment,
        assets=assets,
        risks=risks,
    )


@assessment_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        period = request.form.get("period", "").strip()

        if not name:
            flash("El nombre de la evaluación es requerido.", "error")
            return render_template("assessments/create.html")

        if not period:
            flash("El período de la evaluación es requerido.", "error")
            return render_template("assessments/create.html")

        try:
            current_user = SessionService.get_username()
            AssessmentService.create(
                name=name,
                description=description,
                period=period,
                created_by=current_user,
            )
            flash(f"Evaluación '{name}' creada exitosamente.", "success")
            return redirect(url_for("assessment.index"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("assessments/create.html")
        except Exception as e:
            flash(f"Error al crear la evaluación: {e}", "error")
            return render_template("assessments/create.html")

    return render_template("assessments/create.html")


@assessment_bp.route("/<assessment_id>/edit", methods=["GET", "POST"])
def edit(assessment_id: str):
    assessment = AssessmentService.get_by_id(assessment_id)
    if not assessment:
        flash("Evaluación no encontrada.", "error")
        return redirect(url_for("assessment.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        period = request.form.get("period", "").strip()

        if not name:
            flash("El nombre de la evaluación es requerido.", "error")
            return render_template("assessments/edit.html", assessment=assessment)

        if not period:
            flash("El período de la evaluación es requerido.", "error")
            return render_template("assessments/edit.html", assessment=assessment)

        try:
            AssessmentService.update(
                assessment_id=assessment_id,
                name=name,
                description=description,
                period=period,
            )
            flash(f"Evaluación '{name}' actualizada exitosamente.", "success")
            return redirect(url_for("assessment.index"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("assessments/edit.html", assessment=assessment)
        except Exception as e:
            flash(f"Error al actualizar la evaluación: {e}", "error")
            return render_template("assessments/edit.html", assessment=assessment)

    return render_template("assessments/edit.html", assessment=assessment)


@assessment_bp.route("/<assessment_id>/delete")
@admin_required
def delete(assessment_id: str):
    try:
        AssessmentService.delete(assessment_id)
        flash("Evaluación eliminada exitosamente.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error al eliminar la evaluación: {e}", "error")

    return redirect(url_for("assessment.index"))


@assessment_bp.route("/<assessment_id>/archive")
def archive(assessment_id: str):
    try:
        AssessmentService.archive(assessment_id)
        flash("Evaluación archivada exitosamente.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error al archivar la evaluación: {e}", "error")

    return redirect(url_for("assessment.index"))


@assessment_bp.route("/<assessment_id>/close")
def close(assessment_id: str):
    try:
        AssessmentService.close(assessment_id)
        flash("Evaluación cerrada exitosamente.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error al cerrar la evaluación: {e}", "error")

    return redirect(url_for("assessment.index"))


@assessment_bp.route("/<assessment_id>/reopen")
def reopen(assessment_id: str):
    try:
        AssessmentService.reopen(assessment_id)
        flash("Evaluación reopenueada exitosamente.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error al reopenear la evaluación: {e}", "error")

    return redirect(url_for("assessment.index"))


@assessment_bp.route("/select")
def select():
    active_assessments = AssessmentService.list_active()
    current_active = AssessmentService.get_active()
    return render_template(
        "assessments/select.html",
        assessments=active_assessments,
        current_active=current_active,
    )


@assessment_bp.route("/<assessment_id>/set-active")
def set_active(assessment_id: str):
    try:
        AssessmentService.set_active(assessment_id)
        flash("Evaluación activada exitosamente.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error al activar la evaluación: {e}", "error")

    return redirect(url_for("assessment.index"))


@assessment_bp.route("/clear-active")
def clear_active():
    AssessmentService.clear_active()
    flash("Evaluación activa removida.", "info")
    return redirect(url_for("assessment.index"))
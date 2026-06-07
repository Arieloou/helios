from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services.magerit_service import MageritService
from app.services.assessment_service import AssessmentService
from app.services.asset_service import AssetService
from app.data.catalogs import (
    initialize_catalogs,
    get_threats,
    get_threat_categories,
    get_vulnerabilities,
    get_vulnerability_categories,
)

risk_bp = Blueprint("risk", __name__, url_prefix="/risk")

initialize_catalogs()


@risk_bp.route("/")
def index():
    active_assessment = AssessmentService.get_active()
    mappings = MageritService.list_mappings(active_assessment["id"] if active_assessment else None)
    summary = MageritService.get_risk_summary(active_assessment["id"] if active_assessment else None)
    return render_template(
        "risk/mappings.html",
        mappings=mappings,
        summary=summary,
        active_assessment=active_assessment,
    )


@risk_bp.route("/create", methods=["GET", "POST"])
def create():
    active_assessment = AssessmentService.get_active()
    assets = AssetService.list_all()
    
    if active_assessment:
        assets = [a for a in assets if a.get("assessment_id") == active_assessment["id"]]

    threats = get_threats()
    threat_categories = get_threat_categories()
    vulnerabilities = get_vulnerabilities()
    vuln_categories = get_vulnerability_categories()

    if request.method == "POST":
        asset_id = request.form.get("asset_id", "").strip()
        threat_id = request.form.get("threat_id", "").strip()
        vulnerability_id = request.form.get("vulnerability_id", "").strip()
        probability = int(request.form.get("probability", 1))
        degradation = float(request.form.get("degradation", 0.5))

        if not asset_id or not threat_id or not vulnerability_id:
            flash("Todos los campos son requeridos.", "error")
            return render_template(
                "risk/create_mapping.html",
                assets=assets,
                threats=threats,
                vulnerabilities=vulnerabilities,
                active_assessment=active_assessment,
            )

        try:
            MageritService.create_mapping(
                asset_id=asset_id,
                threat_id=threat_id,
                vulnerability_id=vulnerability_id,
                probability=probability,
                degradation=degradation,
                assessment_id=active_assessment["id"] if active_assessment else None,
            )
            flash("Mapeo creado exitosamente.", "success")
            return redirect(url_for("risk.index"))
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error al crear el mapeo: {e}", "error")

    return render_template(
        "risk/create_mapping.html",
        assets=assets,
        threats=threats,
        vulnerabilities=vulnerabilities,
        active_assessment=active_assessment,
    )


@risk_bp.route("/<mapping_id>/edit", methods=["GET", "POST"])
def edit(mapping_id: str):
    mapping = MageritService.get_mapping(mapping_id)
    if not mapping:
        flash("Mapeo no encontrado.", "error")
        return redirect(url_for("risk.index"))

    active_assessment = AssessmentService.get_active()

    if request.method == "POST":
        probability = int(request.form.get("probability", 1))
        degradation = float(request.form.get("degradation", 0.5))

        try:
            MageritService.update_mapping(
                mapping_id=mapping_id,
                probability=probability,
                degradation=degradation,
            )
            flash("Mapeo actualizado exitosamente.", "success")
            return redirect(url_for("risk.index"))
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error al actualizar el mapeo: {e}", "error")

    return render_template(
        "risk/edit_mapping.html",
        mapping=mapping,
        active_assessment=active_assessment,
    )


@risk_bp.route("/<mapping_id>/delete")
def delete(mapping_id: str):
    try:
        MageritService.delete_mapping(mapping_id)
        flash("Mapeo eliminado exitosamente.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error al eliminar el mapeo: {e}", "error")

    return redirect(url_for("risk.index"))


@risk_bp.route("/matrix")
def matrix():
    active_assessment = AssessmentService.get_active()
    mappings = MageritService.list_mappings(active_assessment["id"] if active_assessment else None)
    return render_template(
        "risk/matrix.html",
        mappings=mappings,
        active_assessment=active_assessment,
    )


@risk_bp.route("/recalculate")
def recalculate():
    active_assessment = AssessmentService.get_active()
    try:
        count = MageritService.recalculate_all(active_assessment["id"] if active_assessment else None)
        flash(f"Se recalcularon {count} mapeos.", "success")
    except Exception as e:
        flash(f"Error al recalcular: {e}", "error")
    return redirect(url_for("risk.index"))
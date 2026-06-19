from flask import Blueprint, flash, redirect, render_template, request, url_for, Response

from app.services.dashboard_service import DashboardService
from app.services.export_service import ExportService
from app.services.assessment_service import AssessmentService
from app.services.session_service import SessionService


dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
def index():
    active_assessment = AssessmentService.get_active()
    summary = DashboardService.get_executive_summary(
        active_assessment["id"] if active_assessment else None
    )
    return render_template(
        "dashboard/overview.html",
        summary=summary,
        active_assessment=active_assessment,
    )


@dashboard_bp.route("/overview")
def overview():
    active_assessment = AssessmentService.get_active()
    summary = DashboardService.get_executive_summary(
        active_assessment["id"] if active_assessment else None
    )
    return render_template(
        "dashboard/overview.html",
        summary=summary,
        active_assessment=active_assessment,
    )


@dashboard_bp.route("/matrix")
def matrix():
    active_assessment = AssessmentService.get_active()
    matrix_data = DashboardService.get_risk_matrix_data(
        active_assessment["id"] if active_assessment else None
    )
    return render_template(
        "dashboard/matrix.html",
        matrix_data=matrix_data,
        active_assessment=active_assessment,
    )


@dashboard_bp.route("/risk-journey")
def risk_journey():
    active_assessment = AssessmentService.get_active()
    journeys = DashboardService.get_risk_journey_data(
        active_assessment["id"] if active_assessment else None
    )
    return render_template(
        "dashboard/risk_journey.html",
        journeys=journeys,
        active_assessment=active_assessment,
    )


@dashboard_bp.route("/export")
def export_page():
    active_assessment = AssessmentService.get_active()
    export_options = ExportService.get_export_options()
    return render_template(
        "dashboard/export.html",
        export_options=export_options,
        active_assessment=active_assessment,
    )


@dashboard_bp.route("/export/<format_type>")
def export_data(format_type: str):
    active_assessment = AssessmentService.get_active()
    assessment_id = active_assessment["id"] if active_assessment else None

    try:
        if format_type == "json":
            content = ExportService.export_to_json(assessment_id)
            mimetype = "application/json"
            filename = "helios_dashboard.json"
        elif format_type == "csv":
            content = ExportService.export_to_csv(assessment_id)
            mimetype = "text/csv"
            filename = "helios_riesgos.csv"
        elif format_type == "journey_csv":
            content = ExportService.export_risk_journey_csv(assessment_id)
            mimetype = "text/csv"
            filename = "helios_viaje_riesgo.csv"
        elif format_type == "powerbi":
            content = ExportService.export_powerbi_format(assessment_id)
            mimetype = "application/json"
            filename = "helios_powerbi.json"
        else:
            flash(f"Formato de exportación no válido: {format_type}", "error")
            return redirect(url_for("dashboard.export_page"))

        return Response(
            content,
            mimetype=mimetype,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as e:
        flash(f"Error al exportar: {e}", "error")
        return redirect(url_for("dashboard.export_page"))


@dashboard_bp.route("/api/data")
def api_data():
    active_assessment = AssessmentService.get_active()
    data = DashboardService.get_dashboard_data(
        active_assessment["id"] if active_assessment else None
    )
    from flask import jsonify
    return jsonify(data)
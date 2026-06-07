from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services.iso27002_service import ISO27002Service
from app.services.assessment_service import AssessmentService
from app.data.iso_controls import initialize_iso_catalogs

iso_bp = Blueprint("iso", __name__, url_prefix="/iso")

initialize_iso_catalogs()


@iso_bp.route("/")
def index():
    active_assessment = AssessmentService.get_active()
    questionnaire = ISO27002Service.get_questionnaire_for_assessment(
        active_assessment["id"] if active_assessment else None
    )
    return render_template(
        "iso/questionnaire.html",
        questionnaire=questionnaire,
        active_assessment=active_assessment,
    )


@iso_bp.route("/control/<control_id>", methods=["GET", "POST"])
def control_questionnaire(control_id: str):
    active_assessment = AssessmentService.get_active()
    if not active_assessment:
        flash("No hay evaluación activa.", "error")
        return redirect(url_for("iso.index"))
    
    assessment_id = active_assessment["id"]
    
    control = ISO27002Service.get_controls()
    control_data = next((c for c in control if c["control_id"] == control_id), None)
    
    if not control_data:
        flash("Control no encontrado.", "error")
        return redirect(url_for("iso.index"))
    
    questions = ISO27002Service.get_questions(control_id)
    
    from app.models.iso_models import ControlResponse
    responses = ControlResponse.get_by_control(assessment_id, control_id)
    response_map = {r.question_id: r for r in responses}
    
    maturity = ISO27002Service.get_maturity_by_control(assessment_id, control_id)
    
    if request.method == "POST":
        for question in questions:
            question_id = question["id"]
            response_value = request.form.get(f"q_{question_id}")
            
            if response_value:
                try:
                    response = int(response_value)
                    ISO27002Service.save_response(
                        assessment_id=assessment_id,
                        control_id=control_id,
                        question_id=question_id,
                        response=response,
                    )
                except ValueError as e:
                    flash(str(e), "error")
        
        flash("Respuestas guardadas.", "success")
        return redirect(url_for("iso.control_questionnaire", control_id=control_id))
    
    return render_template(
        "iso/response_form.html",
        control=control_data,
        questions=questions,
        response_map=response_map,
        maturity=maturity,
        active_assessment=active_assessment,
    )


@iso_bp.route("/maturity")
def maturity_report():
    active_assessment = AssessmentService.get_active()
    if not active_assessment:
        flash("No hay evaluación activa.", "error")
        return redirect(url_for("iso.index"))
    
    report = ISO27002Service.get_maturity_report(active_assessment["id"])
    domain_maturity = ISO27002Service.get_maturity_by_domain(active_assessment["id"])
    
    return render_template(
        "iso/maturity_report.html",
        report=report,
        domain_maturity=domain_maturity,
        active_assessment=active_assessment,
    )


@iso_bp.route("/save-response", methods=["POST"])
def save_response():
    active_assessment = AssessmentService.get_active()
    if not active_assessment:
        return {"error": "No hay evaluación activa"}, 400
    
    control_id = request.form.get("control_id")
    question_id = request.form.get("question_id")
    response = int(request.form.get("response"))
    
    try:
        result = ISO27002Service.save_response(
            assessment_id=active_assessment["id"],
            control_id=control_id,
            question_id=question_id,
            response=response,
        )
        return {"success": True, "maturity": result["maturity"], "maturity_display": result["maturity_display"]}
    except ValueError as e:
        return {"error": str(e)}, 400
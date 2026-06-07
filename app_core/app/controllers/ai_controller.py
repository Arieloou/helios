from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask import jsonify

from app.services.ai_analysis_service import AIAnalysisService
from app.services.asset_service import AssetService
from app.services.assessment_service import AssessmentService

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")


@ai_bp.route("/status")
def status():
    available = AIAnalysisService.is_available()
    models = AIAnalysisService.get_models() if available else []
    return jsonify({
        "available": available,
        "models": models,
    })


@ai_bp.route("/analyze/<asset_id>", methods=["GET", "POST"])
def analyze(asset_id: str):
    asset = AssetService.get_by_id(asset_id)
    if not asset:
        flash("Activo no encontrado.", "error")
        return redirect(url_for("assets.index"))

    active_assessment = AssessmentService.get_active()

    if request.method == "POST":
        result = AIAnalysisService.analyze_asset_safe(asset_id)

        if result.get("success"):
            return render_template(
                "ai/analysis_result.html",
                asset=asset,
                analysis=result,
                active_assessment=active_assessment,
            )
        else:
            flash(result.get("error", "Error al analizar"), "error")
            return render_template(
                "ai/analysis_result.html",
                asset=asset,
                analysis=result,
                active_assessment=active_assessment,
            )

    result = AIAnalysisService.analyze_asset_safe(asset_id)

    return render_template(
        "ai/analysis_result.html",
        asset=asset,
        analysis=result,
        active_assessment=active_assessment,
    )


@ai_bp.route("/check")
def check():
    available = AIAnalysisService.is_available()
    return jsonify({
        "available": available,
    })
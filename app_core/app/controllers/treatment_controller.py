from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask import session

from app.services.treatment_service import TreatmentService
from app.services.assessment_service import AssessmentService
from app.services.risk_classifier import RiskClassifier


treatment_bp = Blueprint("treatment", __name__, url_prefix="/treatment")


def _get_current_user():
    user = session.get("user")
    if user:
        try:
            encryption = None
            from flask import current_app
            encryption = current_app.extensions.get("encryption")
            if encryption:
                return encryption.decrypt(user.get("username_encrypted", ""))
            return "[cifrado]"
        except Exception:
            return "[cifrado]"
    return None


@treatment_bp.route("/risks")
def risks():
    active_assessment = AssessmentService.get_active()
    unacceptable_risks = TreatmentService.list_unacceptable_risks(
        active_assessment["id"] if active_assessment else None
    )
    return render_template(
        "treatment/risks.html",
        risks=unacceptable_risks,
        active_assessment=active_assessment,
        RiskClassifier=RiskClassifier,
    )


@treatment_bp.route("/plans")
def plans():
    active_assessment = AssessmentService.get_active()
    plans = TreatmentService.list_plans(
        active_assessment["id"] if active_assessment else None
    )
    return render_template(
        "treatment/plans.html",
        plans=plans,
        active_assessment=active_assessment,
        RiskClassifier=RiskClassifier,
    )


@treatment_bp.route("/plan/<plan_id>")
def plan_detail(plan_id: str):
    active_assessment = AssessmentService.get_active()
    plan = TreatmentService.get_plan_with_tasks(plan_id)
    if not plan:
        flash("Plan no encontrado.", "error")
        return redirect(url_for("treatment.plans"))
    return render_template(
        "treatment/plan_detail.html",
        plan=plan,
        active_assessment=active_assessment,
        RiskClassifier=RiskClassifier,
    )


@treatment_bp.route("/plan/<mapping_id>/create", methods=["GET", "POST"])
def create_plan(mapping_id: str):
    active_assessment = AssessmentService.get_active()
    mapping = TreatmentService.get_mapping_details(mapping_id)

    if not mapping:
        flash("Mapeo no encontrado.", "error")
        return redirect(url_for("treatment.risks"))

    if request.method == "POST":
        strategy = request.form.get("strategy", "mitigate").strip()

        try:
            plan = TreatmentService.create_plan(
                mapping_id=mapping_id,
                strategy=strategy,
                assessment_id=active_assessment["id"] if active_assessment else None,
            )
            flash("Plan de tratamiento creado exitosamente.", "success")
            return redirect(url_for("treatment.plan_detail", plan_id=plan["id"]))
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error al crear el plan: {e}", "error")

    return render_template(
        "treatment/create_plan.html",
        mapping=mapping,
        active_assessment=active_assessment,
    )


@treatment_bp.route("/plan/<plan_id>/edit", methods=["GET", "POST"])
def edit_plan(plan_id: str):
    active_assessment = AssessmentService.get_active()
    plan = TreatmentService.get_plan_with_tasks(plan_id)

    if not plan:
        flash("Plan no encontrado.", "error")
        return redirect(url_for("treatment.plans"))

    if request.method == "POST":
        strategy = request.form.get("strategy", "").strip()
        status = request.form.get("status", "").strip()

        try:
            if strategy:
                TreatmentService.update_plan(plan_id, strategy=strategy)
            if status:
                TreatmentService.update_plan(plan_id, status=status)
            flash("Plan actualizado exitosamente.", "success")
            return redirect(url_for("treatment.plan_detail", plan_id=plan_id))
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error al actualizar el plan: {e}", "error")

    return render_template(
        "treatment/edit_plan.html",
        plan=plan,
        active_assessment=active_assessment,
    )


@treatment_bp.route("/plan/<plan_id>/delete")
def delete_plan(plan_id: str):
    try:
        TreatmentService.delete_plan(plan_id)
        flash("Plan de tratamiento eliminado.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error al eliminar el plan: {e}", "error")

    return redirect(url_for("treatment.plans"))


@treatment_bp.route("/plan/<plan_id>/task/create", methods=["GET", "POST"])
def create_task(plan_id: str):
    active_assessment = AssessmentService.get_active()
    plan = TreatmentService.get_plan_with_tasks(plan_id)

    if not plan:
        flash("Plan no encontrado.", "error")
        return redirect(url_for("treatment.plans"))

    if request.method == "POST":
        description = request.form.get("description", "").strip()
        responsible = request.form.get("responsible", "").strip()
        due_date = request.form.get("due_date", "").strip()

        if not description:
            flash("La descripción es requerida.", "error")
            return render_template(
                "treatment/create_task.html",
                plan=plan,
                active_assessment=active_assessment,
            )

        try:
            task = TreatmentService.create_task(
                plan_id=plan_id,
                description=description,
                responsible=responsible if responsible else None,
                due_date=due_date if due_date else None,
            )
            flash("Tarea creada exitosamente.", "success")
            return redirect(url_for("treatment.plan_detail", plan_id=plan_id))
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error al crear la tarea: {e}", "error")

    return render_template(
        "treatment/create_task.html",
        plan=plan,
        active_assessment=active_assessment,
    )


@treatment_bp.route("/task/<task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id: str):
    active_assessment = AssessmentService.get_active()
    task = TreatmentService.list_tasks()
    task_data = next((t for t in task if t["id"] == task_id), None)

    if not task_data:
        flash("Tarea no encontrada.", "error")
        return redirect(url_for("treatment.plans"))

    if request.method == "POST":
        description = request.form.get("description", "").strip()
        responsible = request.form.get("responsible", "").strip()
        due_date = request.form.get("due_date", "").strip()
        status = request.form.get("status", "").strip()
        progress = request.form.get("progress_percentage", "").strip()

        try:
            kwargs = {}
            if description:
                kwargs["description"] = description
            if responsible is not None:
                kwargs["responsible"] = responsible
            if due_date:
                kwargs["due_date"] = due_date
            if status:
                kwargs["status"] = status
            if progress:
                kwargs["progress_percentage"] = int(progress)

            TreatmentService.update_task(task_id, **kwargs)
            flash("Tarea actualizada exitosamente.", "success")
            return redirect(url_for("treatment.plan_detail", plan_id=task_data["plan_id"]))
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error al actualizar la tarea: {e}", "error")

    return render_template(
        "treatment/edit_task.html",
        task=task_data,
        active_assessment=active_assessment,
    )


@treatment_bp.route("/task/<task_id>/delete")
def delete_task(task_id: str):
    task = TreatmentService.list_tasks()
    task_data = next((t for t in task if t["id"] == task_id), None)

    try:
        TreatmentService.delete_task(task_id)
        flash("Tarea eliminada.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error al eliminar la tarea: {e}", "error")

    if task_data:
        return redirect(url_for("treatment.plan_detail", plan_id=task_data["plan_id"]))
    return redirect(url_for("treatment.plans"))
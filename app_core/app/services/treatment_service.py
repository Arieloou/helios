from typing import Dict, List, Optional
from datetime import datetime

from app.models.treatment_models import TreatmentPlan, TreatmentTask
from app.models.risk_models import AssetThreatMapping
from app.services.risk_classifier import RiskClassifier
from app.services.assessment_service import AssessmentService


class TreatmentService:
    UNACCEPTABLE_RR_THRESHOLD = 12

    @classmethod
    def list_unacceptable_risks(cls, assessment_id: Optional[str] = None) -> List[Dict]:
        if assessment_id:
            mappings = AssetThreatMapping.get_by_assessment(assessment_id)
        else:
            mappings = AssetThreatMapping.get_all()

        result = []
        for mapping in mappings:
            if mapping.residual_risk and RiskClassifier.is_unacceptable(mapping.residual_risk):
                data = mapping.to_dict()
                existing_plan = TreatmentPlan.get_by_mapping(mapping.id)
                data["has_treatment_plan"] = existing_plan is not None
                data["plan_id"] = existing_plan.id if existing_plan else None

                from app.models.asset import Asset
                asset = Asset.get_by_id(mapping.asset_id)
                if asset:
                    data["asset_name"] = asset.name

                result.append(data)

        return result

    @classmethod
    def get_mapping_details(cls, mapping_id: str) -> Optional[Dict]:
        mapping = AssetThreatMapping.get_by_id(mapping_id)
        if not mapping:
            return None

        data = mapping.to_dict()

        from app.models.asset import Asset
        asset = Asset.get_by_id(mapping.asset_id)
        if asset:
            data["asset_name"] = asset.name
            data["asset_type"] = asset.asset_type

        plan = TreatmentPlan.get_by_mapping(mapping_id)
        if plan:
            data["existing_plan"] = plan.to_dict()

        return data

    @classmethod
    def create_plan(
        cls,
        mapping_id: str,
        strategy: str,
        assessment_id: Optional[str] = None,
    ) -> Dict:
        mapping = AssetThreatMapping.get_by_id(mapping_id)
        if not mapping:
            raise ValueError(f"Mapeo no encontrado: {mapping_id}")

        if not assessment_id:
            active = AssessmentService.get_active()
            if active:
                assessment_id = active["id"]

        existing = TreatmentPlan.get_by_mapping(mapping_id)
        if existing:
            raise ValueError("Ya existe un plan de tratamiento para este mapeo")

        valid_strategies = ["mitigate", "accept", "transfer"]
        if strategy not in valid_strategies:
            raise ValueError(f"Estrategia inválida. Debe ser: {', '.join(valid_strategies)}")

        plan = TreatmentPlan(
            assessment_id=assessment_id,
            mapping_id=mapping_id,
            strategy=strategy,
            status="pending",
        )

        return plan.to_dict()

    @classmethod
    def update_plan(
        cls,
        plan_id: str,
        strategy: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict:
        plan = TreatmentPlan.get_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan no encontrado: {plan_id}")

        if strategy:
            valid_strategies = ["mitigate", "accept", "transfer"]
            if strategy not in valid_strategies:
                raise ValueError(f"Estrategia inválida: {strategy}")
            plan.strategy = strategy

        if status:
            valid_statuses = ["pending", "approved", "in_progress", "completed"]
            if status not in valid_statuses:
                raise ValueError(f"Estado inválido: {status}")
            plan.status = status
            plan.updated_at = datetime.now()

        return plan.to_dict()

    @classmethod
    def delete_plan(cls, plan_id: str) -> None:
        plan = TreatmentPlan.get_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan no encontrado: {plan_id}")

        tasks = TreatmentTask.get_by_plan(plan_id)
        for task in tasks:
            task.delete()

        plan.delete()

    @classmethod
    def list_plans(cls, assessment_id: Optional[str] = None) -> List[Dict]:
        if assessment_id:
            plans = [p for p in TreatmentPlan.get_all() if p.assessment_id == assessment_id]
        else:
            plans = TreatmentPlan.get_all()

        result = []
        for plan in plans:
            data = plan.to_dict()
            mapping = AssetThreatMapping.get_by_id(plan.mapping_id)
            if mapping:
                data["residual_risk"] = mapping.residual_risk
                data["risk_zone"] = RiskClassifier.get_risk_zone(mapping.residual_risk or 0)

                from app.models.asset import Asset
                asset = Asset.get_by_id(mapping.asset_id)
                if asset:
                    data["asset_name"] = asset.name

            tasks = TreatmentTask.get_by_plan(plan.id)
            data["task_count"] = len(tasks)
            data["completed_tasks"] = len([t for t in tasks if t.status == "completed"])

            result.append(data)

        return result

    @classmethod
    def create_task(
        cls,
        plan_id: str,
        description: str,
        responsible: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> Dict:
        plan = TreatmentPlan.get_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan no encontrado: {plan_id}")

        if not description:
            raise ValueError("La descripción de la tarea es requerida")

        due_date_dt = None
        if due_date:
            try:
                due_date_dt = datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD")

        task = TreatmentTask(
            plan_id=plan_id,
            description=description,
            responsible=responsible,
            due_date=due_date_dt,
            status="pending",
            progress_percentage=0,
        )

        return task.to_dict()

    @classmethod
    def update_task(
        cls,
        task_id: str,
        description: Optional[str] = None,
        responsible: Optional[str] = None,
        due_date: Optional[str] = None,
        status: Optional[str] = None,
        progress_percentage: Optional[int] = None,
    ) -> Dict:
        task = TreatmentTask.get_by_id(task_id)
        if not task:
            raise ValueError(f"Tarea no encontrada: {task_id}")

        if description:
            task.description = description
        if responsible is not None:
            task.responsible = responsible
        if due_date:
            try:
                task.due_date = datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD")
        if status:
            valid_statuses = ["pending", "in_progress", "completed"]
            if status not in valid_statuses:
                raise ValueError(f"Estado inválido: {status}")
            task.status = status
        if progress_percentage is not None:
            task.progress_percentage = max(0, min(100, progress_percentage))

        task.updated_at = datetime.now()
        return task.to_dict()

    @classmethod
    def delete_task(cls, task_id: str) -> None:
        task = TreatmentTask.get_by_id(task_id)
        if not task:
            raise ValueError(f"Tarea no encontrada: {task_id}")
        task.delete()

    @classmethod
    def list_tasks(cls, plan_id: Optional[str] = None) -> List[Dict]:
        if plan_id:
            tasks = TreatmentTask.get_by_plan(plan_id)
        else:
            tasks = TreatmentTask.get_all()

        result = []
        for task in tasks:
            data = task.to_dict()
            plan = TreatmentPlan.get_by_id(task.plan_id)
            if plan:
                data["plan_strategy"] = plan.strategy
                data["plan_status"] = plan.status
            result.append(data)

        return result

    @classmethod
    def get_plan_with_tasks(cls, plan_id: str) -> Optional[Dict]:
        plan = TreatmentPlan.get_by_id(plan_id)
        if not plan:
            return None

        data = plan.to_dict()
        tasks = TreatmentTask.get_by_plan(plan_id)
        data["tasks"] = [t.to_dict() for t in tasks]

        if tasks:
            total_progress = sum(t.progress_percentage for t in tasks) / len(tasks)
            data["overall_progress"] = round(total_progress, 1)
        else:
            data["overall_progress"] = 0

        mapping = AssetThreatMapping.get_by_id(plan.mapping_id)
        if mapping:
            data["residual_risk"] = mapping.residual_risk
            data["risk_inherent"] = mapping.risk_inherent

            from app.models.asset import Asset
            asset = Asset.get_by_id(mapping.asset_id)
            if asset:
                data["asset_name"] = asset.name

        return data
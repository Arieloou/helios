from typing import Dict, List, Optional

from app.models.assesment import Assessment, AssessmentStatus


class AssessmentService:
    _active_assessment_id: Optional[str] = None

    @classmethod
    def list_all(cls) -> List[Dict]:
        assessments = Assessment.get_all()
        return [a.to_dict() for a in assessments]

    @classmethod
    def list_active(cls) -> List[Dict]:
        assessments = Assessment.get_active()
        return [a.to_dict() for a in assessments]

    @classmethod
    def get_by_id(cls, assessment_id: str) -> Optional[Dict]:
        assessment = Assessment.get_by_id(assessment_id)
        return assessment.to_dict() if assessment else None

    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        period: str,
        created_by: Optional[str] = None,
    ) -> Dict:
        assessment = Assessment.create(
            name=name,
            description=description,
            period=period,
            created_by=created_by,
        )
        return assessment.to_dict()

    @classmethod
    def update(
        cls,
        assessment_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        period: Optional[str] = None,
    ) -> Dict:
        assessment = Assessment.get_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Evaluación no encontrada: {assessment_id}")

        assessment.update(name=name, description=description, period=period)
        return assessment.to_dict()

    @classmethod
    def delete(cls, assessment_id: str) -> None:
        assessment = Assessment.get_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Evaluación no encontrada: {assessment_id}")

        if assessment.status == AssessmentStatus.CLOSED:
            raise ValueError("No se puede eliminar una evaluación cerrada")

        assessment.delete()

    @classmethod
    def archive(cls, assessment_id: str) -> Dict:
        assessment = Assessment.get_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Evaluación no encontrada: {assessment_id}")

        assessment.archive()
        if cls._active_assessment_id == assessment_id:
            cls._active_assessment_id = None
        return assessment.to_dict()

    @classmethod
    def close(cls, assessment_id: str) -> Dict:
        assessment = Assessment.get_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Evaluación no encontrada: {assessment_id}")

        if assessment.status == AssessmentStatus.CLOSED:
            raise ValueError("La evaluación ya está cerrada")

        assessment.close()
        if cls._active_assessment_id == assessment_id:
            cls._active_assessment_id = None
        return assessment.to_dict()

    @classmethod
    def reopen(cls, assessment_id: str) -> Dict:
        assessment = Assessment.get_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Evaluación no encontrada: {assessment_id}")

        if assessment.status != AssessmentStatus.CLOSED:
            raise ValueError("Solo se pueden reopenear evaluaciones cerradas")

        assessment.reopen()
        return assessment.to_dict()

    @classmethod
    def set_active(cls, assessment_id: str) -> Dict:
        assessment = Assessment.get_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Evaluación no encontrada: {assessment_id}")

        if assessment.status != AssessmentStatus.ACTIVE:
            raise ValueError("Solo se pueden activar evaluaciones activas")

        cls._active_assessment_id = assessment_id
        return assessment.to_dict()

    @classmethod
    def get_active(cls) -> Optional[Dict]:
        if not cls._active_assessment_id:
            return None
        assessment = Assessment.get_by_id(cls._active_assessment_id)
        return assessment.to_dict() if assessment else None

    @classmethod
    def clear_active(cls) -> None:
        cls._active_assessment_id = None

    @classmethod
    def is_active(cls, assessment_id: str) -> bool:
        return cls._active_assessment_id == assessment_id

    @classmethod
    def get_active_assessment_id(cls) -> Optional[str]:
        return cls._active_assessment_id
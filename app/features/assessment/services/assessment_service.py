# features/assessment/services/assessment_service.py

# Import shared types, schemas, and dependencies
from datetime import datetime, timezone

# Import feature-specific types, schemas, and models
from ..repositories import AssessmentRepository
from ..schemas import AssessmentStatus, AssessmentCreate
from ..models import Assessment

from app.core.decorators.audit_decorator import audit

class AssessmentService:
    def __init__(self, repository: AssessmentRepository):
        self.repository = repository

    @audit("create_assessment")
    async def create_assessment(self, assessment: AssessmentCreate, current_user_id: str):
        if await self.repository.get_by_name(assessment.name):
            raise ValueError("La evaluación ya existe")
                
        assessment = Assessment(
            name=assessment.name,
            description=assessment.description,
            period=assessment.period,
            status=AssessmentStatus.ACTIVE.value,
            created_by=current_user_id
        )
        return await self.repository.save(assessment)

    # Update assessment
    @audit("update_assessment")
    

    @audit("close_assessment")  
    async def close_assessment(self, assessment_id: str):
        assessment = await self.repository.get_by_id(assessment_id)
        
        if not assessment:
            raise ValueError(f"No se encontró la evaluación con id {assessment_id}")

        assessment.status = AssessmentStatus.CLOSED.value
        assessment.closed_at = datetime.now(timezone.utc)
        
        return await self.repository.save(assessment)

    @audit("archive_assessment")
    async def archive_assessment(self, assessment_id: str):
        assessment = await self.repository.get_by_id(assessment_id)

        if not assessment:
            raise ValueError("Evaluación no encontrada")

        assessment.status = AssessmentStatus.ARCHIVED.value
        assessment.archived_at = datetime.now(timezone.utc) 
        
        return await self.repository.save(assessment)

    @audit("reopen_assessment")
    async def reopen_assessment(self, assessment_id: str):
        assessment = await self.repository.get_by_id(assessment_id)

        if not assessment:
            raise ValueError("Evaluación no encontrada")

        assessment.status = AssessmentStatus.ACTIVE.value
        assessment.closed_at = None
        assessment.archived_at = None
        
        return await self.repository.save(assessment)
    
    # It includes all assessment types (active, closed, archived)
    async def get_all_assessments(self):
        return await self.repository.get_all()

    async def get_all_closed_assessments(self):
        return await self.repository.get_closed()

    async def get_all_archived_assessments(self):
        return await self.repository.get_archived()

    async def get_all_active_assessments(self):
        return await self.repository.get_active()
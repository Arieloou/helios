from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db 

from .repositories import AssessmentRepository
from .services import AssessmentService

def get_assessment_service(db: AsyncSession = Depends(get_db)) -> AssessmentService:
    """
    FastAPI inyectará 'db' automáticamente.
    Nosotros la usamos para crear el Repositorio, y luego el Servicio.
    """
    repository = AssessmentRepository(db)
    return AssessmentService(repository)